
"""
Runs Terraform formatting validation using:
terraform fmt -check -recursive
"""

from __future__ import annotations

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

from utils.helpers import terraform_fmt_check


class FormattingValidator:
    """
    Validates Terraform formatting using terraform fmt.
    """

    validator_name = "FormattingValidator"

    def validate(
        self,
        terraform_file: Path,
        analysis,
    ) -> ValidationResult:

        start_time = time.perf_counter()

        recommendations: list[Recommendation] = []

        working_directory = terraform_file.parent

        fmt_result = terraform_fmt_check(
            working_directory=working_directory
        )

        execution_time = (
            time.perf_counter() - start_time
        ) * 1000

        # terraform fmt exit codes:
        # 0 -> Already formatted
        # 3 -> Formatting required

        if fmt_result.returncode == 0:
            return ValidationResult(
                validator=self.validator_name,
                status=STATUS_SUCCESS,
                issues_found=0,
                execution_time_ms=round(
                    execution_time,
                    2,
                ),
                recommendations=[],
            )

        affected_files = [
            line.strip()
            for line in fmt_result.stdout.splitlines()
            if line.strip()
        ]

        if not affected_files:
            affected_files = [
                terraform_file.name
            ]

        recommendations.append(
            Recommendation(
                category=RecommendationCategory.FORMATTING,
                severity=Severity.LOW,
                title="Terraform Formatting Required",
                message=(
                    "The Terraform file is not formatted according to"
                    "terraform fmt standards" 
                ),
                line_number=None,
                resource=", ".join(
                    affected_files
                ),
                original_value=None,
                suggested_value="Run terraform fmt",
                auto_fixable=True,
                validator=self.validator_name,
            )
        )

        return ValidationResult(
            validator=self.validator_name,
            status=STATUS_WARNING,
            issues_found=len(
                recommendations
            ),
            execution_time_ms=round(
                execution_time,
                2,
            ),
            recommendations=recommendations,
        )