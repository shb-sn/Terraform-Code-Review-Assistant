"""
Runs Terraform syntax validation using:

terraform init
terraform validate

Returns a ValidationResult object.
"""

from __future__ import annotations

import re
import time
from pathlib import Path

from config.settings import (
    STATUS_FAILED,
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
    terraform_init,
    terraform_validate,
)


class SyntaxValidator:
    """
    Performs Terraform syntax validation.
    """

    validator_name = "SyntaxValidator"

    def validate(
        self,
        terraform_file: Path,
        analysis,
    ) -> ValidationResult:

        start_time = time.perf_counter()

        recommendations: list[Recommendation] = []

        working_directory = terraform_file.parent

        # Run terraform init
        terraform_dir=working_directory / ".terraform"

        if not terraform_dir.exists():
            init_result=terraform_init(working_directory)

        # print("INIT STDOUT")
        # print(init_result.stdout)

        # print("INIT STDERR")
        # print(init_result.stderr)

        # print(f"terraform init took {time.perf_counter()-start_time:.2f}")

        if init_result.returncode != 0:

            recommendations.append(
                Recommendation(
                    category=RecommendationCategory.SYNTAX,
                    severity=Severity.HIGH,
                    title="Terraform Initialization Failed",
                    message=(
                        init_result.stderr.strip()
                        or init_result.stdout.strip()
                    ),
                    line_number=None,
                    resource=None,
                    original_value=None,
                    suggested_value=None,
                    auto_fixable=False,
                    validator=self.validator_name,
                )
            )

            execution_time = (
                time.perf_counter() - start_time
            ) * 1000

            return ValidationResult(
                validator=self.validator_name,
                status=STATUS_FAILED,
                issues_found=len(
                    recommendations
                ),
                execution_time_ms=round(
                    execution_time,
                    2,
                ),
                recommendations=recommendations,
            )

        # Run terraform validate
        validate_result = terraform_validate(
            working_directory
        )

        # print("VALIDATE STDOUT")
        # print(validate_result.stdout)

        # print("VALIDATE STDERR")
        # print(validate_result.stderr)

        # print(f"terraform validator took {time.perf_counter()-start_time:.2f}")

        if validate_result.returncode == 0:

            execution_time = (
                time.perf_counter() - start_time
            ) * 1000

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

        output = (
            validate_result.stderr
            if validate_result.stderr
            else validate_result.stdout
        )

        line_number = self._extract_line_number(
            output
        )

        recommendations.append(
            Recommendation(
                category=RecommendationCategory.SYNTAX,
                severity=Severity.HIGH,
                title="Terraform Validation Failed",
                message=output.strip(),
                line_number=line_number,
                resource=None,
                original_value=None,
                suggested_value=None,
                auto_fixable=False,
                validator=self.validator_name,
            )
        )

        execution_time = (
            time.perf_counter() - start_time
        ) * 1000

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

    @staticmethod
    def _extract_line_number(
        terraform_output: str,
    ) -> int | None:
        """
        Extract line number from terraform validate output.
        """

        match = re.search(
            r"line\s+(\d+)",
            terraform_output,
            re.IGNORECASE,
        )

        if match:
            return int(
                match.group(1)
            )

        return None