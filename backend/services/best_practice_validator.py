
"""
Performs Terraform best practice validation
checks:
missing resource tags, naming convention violations, missing lifecycle blocks,
deprecated interpolation syntax, missing variable descriptions, missing output descriptions
"""

from _future_ import annotations
import re
import time
from pathlib import Path

from config.settings import(
    STATUS_SUCCESS,
    STATUS_WARNING
)
from models.recommendation import(
    Recommendation,
    RecommendationCategory,
    Severity
)
from models.validation_result import ValidationResult
from utils.helpers import(
    get_line_number,
    read_file
)

class BestPracticeValidator:
    #validates Terraform best practices.

    validator_name = "BestPracticeValidator"

    def validate(
        self,
        terraform_file: Path,
        analysis,
    ) -> ValidationResult:

        start = time.perf_counter()

        content = read_file(terraform_file)

        recommendations: list[Recommendation] = []


        # resource naming convention
        if analysis["resources"]:
            resource_pattern = re.finditer(
                r'resource\s+"([^"]+)"\s+"([^"]+)"',
                content,
            )

            for match in resource_pattern:

                resource_name = match.group(2)

                if not re.fullmatch(
                    r"[a-z0-9_]+",
                    resource_name,
                ):

                    recommendations.append(
                        Recommendation(
                            category=RecommendationCategory.BEST_PRACTICE,
                            severity=Severity.LOW,
                            title="Resource Naming Convention",
                            message=(
                                f'Resource "{resource_name}" should use '
                                "snake_case naming."
                            ),
                            line_number=get_line_number(
                                content,
                                match.group(0),
                            ),
                            resource=None,
                            original_value=resource_name,
                            suggested_value=resource_name.lower().replace("-", "_"),
                            auto_fixable=True,
                            validator=self.validator_name,
                        )
                    )

        # missing tags
        if analysis["resources"]:
            resource_blocks = re.finditer(
                r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{(.*?)\n\}',
                content,
                re.DOTALL,
            )

            missing_tags_reported=False

            for block in resource_blocks:

                resource_type=block.group(1)
                resource_name=block.group(2)
                block_text = block.group(3)

                if "tags" not in block_text and not missing_tags_reported:

                    recommendations.append(
                        Recommendation(
                            category=RecommendationCategory.BEST_PRACTICE,
                            severity=Severity.MEDIUM,
                            title="Missing Resource Tags",
                            message=(
                                f'Resource "{resource_type}.{resource_name}"'
                                'is missing standard tags'
                                '(Name, Environment, Owner, Project).'
                            ),
                            line_number=None,
                            resource=None,
                            original_value=None,
                            suggested_value="" \
                            "tags={" \
                            "Name=        var.name" \
                            "Environment= var.environment" \
                            "Owner=       var.owner" \
                            "Project=     var.project" \
                            "}",
                            auto_fixable=True,
                            validator=self.validator_name,
                        )
                    )

                    missing_tags_reported=True

        # missing lifecycle block
        if analysis["resources"]:
            resource_blocks = re.finditer(
                r'resource\s+"[^"]+"\s+"[^"]+"\s*\{(.*?)\n\}',
                content,
                re.DOTALL,
            )

            missing_lifecycle_reported=False

            for block in resource_blocks:

                block_text = block.group(1)

                if "lifecycle" not in block_text and not missing_lifecycle_reported:

                    recommendations.append(
                        Recommendation(
                            category=RecommendationCategory.BEST_PRACTICE,
                            severity=Severity.LOW,
                            title="Missing Lifecycle Block",
                            message=(
                                f'Resource "{resource_type}.{resource_name}"'
                                "does not define a lifecylce block."
                            ),
                            line_number=None,
                            resource=None,
                            original_value=None,
                            suggested_value="" \
                            "lifecycle {" \
                            "prevent_destroy = true}",
                            auto_fixable=True,
                            validator=self.validator_name,
                        )
                    )

                    missing_lifecycle_reported=True

        # deprecated interpolation syntax
        interpolation_matches = re.finditer(
            r'"\${[^"]+}"',
            content,
        )

        for match in interpolation_matches:

            recommendations.append(
                Recommendation(
                    category=RecommendationCategory.BEST_PRACTICE,
                    severity=Severity.MEDIUM,
                    title="Deprecated Interpolation Syntax",
                    message=(
                        "Avoid using deprecated interpolation-only syntax."
                    ),
                    line_number=get_line_number(
                        content,
                        match.group(0),
                    ),
                    resource=None,
                    original_value=match.group(0),
                    suggested_value=re.sub(
                        r'"\$\{([^"]+)\}"',
                        r"\1",
                        match.group(0)
                    ),
                    auto_fixable=True,
                    validator=self.validator_name,
                )
            )

        # variable description
        if analysis["variables"]:
            variable_blocks = re.finditer(
                r'variable\s+"[^"]+"\s*\{(.*?)\}',
                content,
                re.DOTALL,
            )

            for block in variable_blocks:

                variable_text = block.group(1)

                if "description" not in variable_text:

                    recommendations.append(
                        Recommendation(
                            category=RecommendationCategory.BEST_PRACTICE,
                            severity=Severity.LOW,
                            title="Variable Description Missing",
                            message=(
                                "Every variable should include a description."
                            ),
                            line_number=None,
                            resource=None,
                            original_value=None,
                            suggested_value='description = "Variable description"',
                            auto_fixable=False,
                            validator=self.validator_name,
                        )
                    )

        # output description
        if analysis["outputs"]:
            output_blocks = re.finditer(
                r'output\s+"[^"]+"\s*\{(.*?)\}',
                content,
                re.DOTALL,
            )

            for block in output_blocks:

                output_text = block.group(1)

                if "description" not in output_text:

                    recommendations.append(
                        Recommendation(
                            category=RecommendationCategory.BEST_PRACTICE,
                            severity=Severity.LOW,
                            title="Output Description Missing",
                            message=(
                                "Every output should include a description."
                            ),
                            line_number=None,
                            resource=None,
                            original_value=None,
                            suggested_value='description = "Output description"',
                            auto_fixable=False,
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