"""
Coordinates the complete validation workflow.
Responsibilities
1. Analyze Terraform file.
2. Decide which validators should execute.
3. Execute validators.
4. Aggregate validation reports.
5. Return all ValidationResult objects.
"""

from __future__ import annotations
from pathlib import Path

from models.validation_result import ValidationResult

from services.terraform_analyzer import TerraformAnalyzer
from services.syntax_validator import SyntaxValidator
from services.formatting_validator import FormattingValidator
from services.security_validator import SecurityValidator
from services.configuration_validator import ConfigurationValidator
from services.best_practice_validator import BestPracticeValidator
from services.optimization_validator import OptimizationValidator


class ValidationEngine:
    #Orchestrates execution of all validators
    def __init__(self) -> None:
        self.analyzer = TerraformAnalyzer()
        self.syntax_validator = SyntaxValidator()
        self.formatting_validator = FormattingValidator()
        self.security_validator = SecurityValidator()
        self.configuration_validator = ConfigurationValidator()
        self.best_practice_validator = BestPracticeValidator()
        self.optimization_validator = OptimizationValidator()

    def run(
        self,
        terraform_file: Path,
    ) -> list[ValidationResult]:
        #Execute applicable validators.

        analysis = self.analyzer.analyze(
            terraform_file
        )
        print(analysis)

        validation_results: list[
            ValidationResult
        ] = []

        # Always execute
        # please enable these two validators after installing terraform
        # validation_results.append(
        #     self.syntax_validator.validate(
        #         terraform_file,
        #         analysis
        #     )
        # )

        # validation_results.append(
        #     self.formatting_validator.validate(
        #         terraform_file,
        #         analysis
        #     )
        # )


        #analyzer-driven validators

        if self._should_run_security(
            analysis
        ):

            validation_results.append(
                self.security_validator.validate(
                    terraform_file, analysis
                )
            )

        if self._should_run_configuration(
            analysis
        ):

            validation_results.append(
                self.configuration_validator.validate(
                    terraform_file, analysis
                )
            )

        if self._should_run_best_practice(
            analysis
        ):

            validation_results.append(
                self.best_practice_validator.validate(
                    terraform_file, analysis
                )
            )

        if self._should_run_optimization(
            analysis
        ):

            validation_results.append(
                self.optimization_validator.validate(
                    terraform_file, analysis
                )
            )

        return validation_results

    # Decision Helpers
    @staticmethod
    def _should_run_security(
        analysis: dict,
    ) -> bool:

        security_resources = {
            "aws_security_group",
            "aws_instance",
            "aws_s3_bucket",
            "aws_db_instance",
            "aws_iam_role",
            "aws_iam_policy",
            "aws_iam_user",
            "aws_iam_group",
            "aws_kms_key",
            "aws_ebs_volume",
        }

        return bool(
            set(
                analysis["resources"]
            )
            &
            security_resources
        )

    @staticmethod
    def _should_run_configuration(
        analysis: dict,
    ) -> bool:

        return any(
            [
                analysis["providers"],
                analysis["resources"],
                analysis["variables"],
                analysis["modules"],
                analysis["outputs"],
                analysis["data_sources"],
            ]
        )
    
    @staticmethod
    def _should_run_best_practice(
        analysis: dict,
    ) -> bool:

        return any(
            [
                analysis["resources"],
                analysis["variables"],
                analysis["outputs"],
                analysis["modules"],
            ]
        )

    @staticmethod
    def _should_run_optimization(
        analysis: dict,
    ) -> bool:

        optimization_resources = {
            "aws_instance",
            "aws_ebs_volume",
            "aws_db_instance",
            "aws_s3_bucket",
            "aws_autoscaling_group",
        }

        return bool(
            set(analysis["resources"])
            & optimization_resources
        )