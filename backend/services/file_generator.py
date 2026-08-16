"""
Generates the reviewed Terraform file.

Responsibilities

1. Read the original Terraform file.
2. Apply accepted auto-fixable recommendations.
3. Write the reviewed Terraform file.
4. Return the generated file path.
"""

from __future__ import annotations
import re

from pathlib import Path

from models.recommendation import (
    Recommendation,
)

from utils.helpers import (
    read_file,
    write_file,
)


class FileGenerator:
    """
    Applies accepted recommendations to a Terraform file.
    """

    reviewed_filename = "reviewed.tf"

    def generate(
        self,
        original_file: Path,
        accepted_recommendations: list[Recommendation],
        output_directory: Path,
    ) -> Path:

        content = read_file(
            original_file
        )

        content = self._apply_recommendations(
            content,
            accepted_recommendations,
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        reviewed_file = (
            output_directory
            / self.reviewed_filename
        )

        write_file(
            reviewed_file,
            content,
        )

        return reviewed_file
    
    def _apply_recommendations(
            self,
            content: str,
            recommendations: list[Recommendation],
            ) -> str:

        for recommendation in recommendations:

            title = recommendation.title
            suggested = recommendation.suggested_value
            original = recommendation.original_value

            if not recommendation.auto_fixable:
                continue
        
            # Normal replacement
            if original is not None and suggested is not None:

                if original in content:
                    content = content.replace(
                        original,
                        suggested,
                        1,
                    )

                continue

            # Missing Terraform Block
            if title == "Missing Terraform Block":

                if "terraform {" not in content:

                    terraform_block = (
                        'terraform {\n'
                        '  required_version = ">= 1.5.0"\n'
                        '}\n\n'
                    )

                    content = terraform_block + content

                continue

            # Missing Terraform Version
            if title == "Missing Terraform Version Constraint":

                if (
                    "terraform {" in content
                    and "required_version" not in content
                ):

                    content = content.replace(
                        "terraform {",
                        'terraform {\n  required_version = ">= 1.5.0"',
                        1,
                    )

                continue

            # Missing Provider Block
            if title == "Missing Provider Block":

                if 'provider "' not in content:

                    provider_block = (
                        '\nprovider "aws" {\n'
                        '  region = var.aws_region\n'
                        '}\n\n'
                    )

                    content += provider_block

                continue

            # Provider Version Not Pinned

            provider_match=re.search(
                r'provider\s+"aws"\s*{(.*?)}',
                content,
            )

            if(
                provider_match is not None
                and "version" not in provider_match.group(1)
            ):

                    content = content.replace(
                        'provider "aws" {',
                        'provider "aws" {\n'
                        '  version = "~> 5.0"',
                        1,
                    )
                    
                    continue

            # Undefined Variable
            if title == "Undefined Variable":

                if suggested is not None:
                    content += "\n\n" + suggested + "\n"

                continue

            # Missing Resource Tags
            if title == "Missing Resource Tags":

                if (
                    suggested is not None
                    and "tags = {" not in content
                ):

                    indented_tags = suggested.replace(
                        "\n",
                        "\n  ",
                    )

                    content = re.sub(
                        r'(resource\s+"[^"]+"\s+"[^"]+"\s*\{)',
                        r"\1\n  " + indented_tags,
                        content,
                        count=1,
                    )

                continue

        return content

    
    @staticmethod
    def _is_valid_recommendation(
        recommendation: Recommendation,
    ) -> bool:
        """
        Check whether a recommendation
        can be automatically applied.
        """

        return (
            recommendation.auto_fixable
        )