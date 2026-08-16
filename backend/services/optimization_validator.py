"""
Performs rule-based optimization validation for terraform files
checks:
oversized EC2 instance types, expensive EBS volume types, excessively large EBS volumes,
missing S3 lifecycle config, missing S3 versioning, missing auto scaling config,
high IOPS config, missing deletion protection
"""

from __future__ import annotations

import re
import time
from pathlib import Path

from config.settings import (
    STATUS_SUCCESS,
    STATUS_WARNING,
)

from models.recommendation import (
    Recommendation,
    RecommendationCategory,
    Severity,
)

from models.validation_result import ValidationResult

from utils.helpers import (
    get_line_number,
    read_file,
)


class OptimizationValidator:
    #Performs rule-based optimization analysis.

    validator_name = "OptimizationValidator"

    LARGE_INSTANCE_PREFIXES = (
        "m5.4xlarge",
        "m5.8xlarge",
        "m5.12xlarge",
        "m5.16xlarge",
        "m5.24xlarge",
        "c5.4xlarge",
        "c5.9xlarge",
        "c5.12xlarge",
        "c5.18xlarge",
        "c5.24xlarge",
        "r5.4xlarge",
        "r5.8xlarge",
        "r5.12xlarge",
        "r5.16xlarge",
        "r5.24xlarge",
    )

    def validate(
        self,
        terraform_file: Path,
        analysis,
    ) -> ValidationResult:

        start = time.perf_counter()

        content = read_file(terraform_file)

        recommendations: list[Recommendation] = []

        # large EC2 instance
        if "aws_instance" in analysis["resources"]:
            for match in re.finditer(
                r'instance_type\s*=\s*"([^"]+)"',
                content,
            ):

                instance = match.group(1)

                if instance.startswith(
                    self.LARGE_INSTANCE_PREFIXES
                ):

                    recommendations.append(
                        Recommendation(
                            category=RecommendationCategory.OPTIMIZATION,
                            severity=Severity.MEDIUM,
                            title="Large EC2 Instance",
                            message=(
                                "Review whether the selected EC2 instance "
                                "size is required."
                            ),
                            line_number=get_line_number(
                                content,
                                match.group(0),
                            ),
                            resource=None,
                            original_value=match.group(0),
                            suggested_value='instance_type = "t3.medium"',
                            auto_fixable=True,
                            validator=self.validator_name,
                        )
                    )

        # expensive EBS volume
        if "aws_ebs_volume" in analysis["resources"]:
            for match in re.finditer(
                r'type\s*=\s*"(io1|io2)"',
                content,
            ):

                recommendations.append(
                    Recommendation(
                        category=RecommendationCategory.OPTIMIZATION,
                        severity=Severity.MEDIUM,
                        title="High-Cost EBS Volume",
                        message=(
                            "Consider gp3 unless high IOPS are required."
                        ),
                        line_number=get_line_number(
                            content,
                            match.group(0),
                        ),
                        resource=None,
                        original_value=match.group(0),
                        suggested_value='type = "gp3"',
                        auto_fixable=True,
                        validator=self.validator_name,
                    )
                )

        # large EBS size
        if "aws_ebs_size" in analysis["resources"]:
            for match in re.finditer(
                r'volume_size\s*=\s*(\d+)',
                content,
            ):

                size = int(match.group(1))

                if size > 500:

                    recommendations.append(
                        Recommendation(
                            category=RecommendationCategory.OPTIMIZATION,
                            severity=Severity.LOW,
                            title="Large EBS Volume",
                            message=(
                                "Verify that such a large EBS volume is "
                                "necessary."
                            ),
                            line_number=get_line_number(
                                content,
                                match.group(0),
                            ),
                            resource=None,
                            original_value=match.group(0),
                            suggested_value= "volume_size = 500",
                            auto_fixable=True,
                            validator=self.validator_name,
                        )
                    )

        # missing S3 lifecycle
        if "aws_s3_bucket" in analysis["resources"]:
            bucket_blocks = re.finditer(
                r'resource\s+"aws_s3_bucket"\s+"[^"]+"\s*\{(.*?)\}',
                content,
                re.DOTALL,
            )

            for block in bucket_blocks:

                bucket = block.group(1)

                if "lifecycle_rule" not in bucket:

                    recommendations.append(
                        Recommendation(
                            category=RecommendationCategory.OPTIMIZATION,
                            severity=Severity.LOW,
                            title="Missing S3 Lifecycle Rule",
                            message="Consider adding lifecycle rules.",
                            line_number=None,
                            resource=None,
                            original_value=None,
                            suggested_value="""
                        lifecycle_rule {
                        enabled = true

                        expiration {
                            days = 90
                        }
                        }
                        """,
                            auto_fixable=True,
                            validator=self.validator_name,
                        )
                    )

                if "versioning" not in bucket:

                    recommendations.append(
                        Recommendation(
                            category=RecommendationCategory.OPTIMIZATION,
                            severity=Severity.LOW,
                            title="S3 Versioning Disabled",
                            message="Enable S3 versioning.",
                            line_number=None,
                            resource=None,
                            original_value=None,
                            suggested_value="""
                        versioning {
                        enabled = true
                        }
                        """,
                            auto_fixable=True,
                            validator=self.validator_name,
                        )
                    )

        # high provisioned IOPS
        if "aws_ebs_volume" in analysis["resources"]:
            for match in re.finditer(
                r'iops\s*=\s*(\d+)',
                content,
            ):

                iops = int(match.group(1))

                if iops > 10000:

                    recommendations.append(
                        Recommendation(
                            category=RecommendationCategory.OPTIMIZATION,
                            severity=Severity.MEDIUM,
                            title="High Provisioned IOPS",
                            message=(
                                "Review whether such high IOPS are required."
                            ),
                            line_number=get_line_number(
                                content,
                                match.group(0),
                            ),
                            resource=None,
                            original_value=str(iops),
                            suggested_value="iops = 3000",
                            auto_fixable=True,
                            validator=self.validator_name,
                        )
                    )

        # missing auto scaling
        if "aws_autoscaling_group" in analysis["resources"]:
            ec2_count = len(
                re.findall(
                    r'resource\s+"aws_instance"',
                    content,
                )
            )

            asg_count = len(
                re.findall(
                    r'resource\s+"aws_autoscaling_group"',
                    content,
                )
            )

            if ec2_count >= 2 and asg_count == 0:

                recommendations.append(
                    Recommendation(
                        category=RecommendationCategory.OPTIMIZATION,
                        severity=Severity.MEDIUM,
                        title="Auto Scaling Not Configured",
                        message="Multiple EC2 instances detected without an Auto Scaling Group.",
                        line_number=None,
                        resource=None,
                        original_value=None,
                        suggested_value="""
                    resource "aws_autoscaling_group" "example" {

                    }
                    """,
                        auto_fixable=False,
                        validator=self.validator_name,
                    )
                )

        # deletion protection
        if "aws_db_instance" in analysis["resources"]:
            for match in re.finditer(
                r'resource\s+"aws_db_instance"\s+"[^"]+"\s*\{(.*?)\}',
                content,
                re.DOTALL,
            ):

                block = match.group(1)

                if "deletion_protection" not in block:

                    recommendations.append(
                        Recommendation(
                            category=RecommendationCategory.OPTIMIZATION,
                            severity=Severity.LOW,
                            title="Deletion Protection Not Enabled",
                            message="Enable deletion protection for production databases.",
                            line_number=None,
                            resource=None,
                            original_value=None,
                            suggested_value="deletion_protection = true",
                            auto_fixable=True,
                            validator=self.validator_name,
                        )
                    )

        execution_time = (
            time.perf_counter() - start
        ) * 1000

        return ValidationResult(
            validator=self.validator_name,
            status=(
                STATUS_SUCCESS
                if not recommendations
                else STATUS_WARNING
            ),
            issues_found=len(recommendations),
            execution_time_ms=round(
                execution_time,
                2,
            ),
            recommendations=recommendations,
        )