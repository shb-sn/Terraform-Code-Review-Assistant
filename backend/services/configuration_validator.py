"""
Performs rule-based configuration validation for terraform files
checks:
missing terraform block, missing required_version, missing provider block, 
missing provider version pinning, dupicate variable declarations, missing variable declarations,
hardcoded instance types
"""

from __future__ import annotations
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

class ConfigurationValidator:
    #performs terraform configuration validation
    validator_name= "ConfigurationValidator"

    def validate(
            self,
            terraform_file: Path,
            analysis,
    ) -> ValidationResult:
        start= time.perf_counter()
        content= read_file(terraform_file)
        recommendations: list[Recommendation]=[]

        #terraform block
        if not re.search(
            r'terraform\s*\{',
            content,
            re.IGNORECASE
        ):
            recommendations.append(
                Recommendation(
                    category=RecommendationCategory.CONFIGURATION,
                    severity= Severity.HIGH,
                    title="Missing Terraform Block",
                    message="Add a terraform block with required_version.",
                    suggested_value=(
                        'terraform {\n'
                        'required_version= ">=1.5.0'
                        '}'
                    ),
                    line_number=None,
                    resource=None,
                    auto_fixable= True,
                    validator= self.validator_name,
                )
            )

        #required version
        if not re.search(
            r'required_version\s*\{',
            content,
            re.IGNORECASE
        ):
            recommendations.append(
                Recommendation(
                    category=RecommendationCategory.CONFIGURATION,
                    severity= Severity.MEDIUM,
                    title="Missing Terraform Version Constraint",
                    message="Specify required_version inside the terraform block.",
                    suggested_value='required_version = ">= 1.5.0"',
                    line_number=None,
                    resource=None,
                    auto_fixable= True,
                    validator= self.validator_name,
                )
            )

        #provider block
        if analysis["providers"]:
            provider_blocks=re.finditer(
                r'provider\s+"[^"]+"\s*\{(.*?)\}',
                content,
                re.DOTALL,
            )

            recommendations.append(
                Recommendation(
                    category=RecommendationCategory.CONFIGURATION,
                    severity= Severity.HIGH,
                    title="Missing Provider Block",
                    message="Terraform provider block not found.",
                    suggested_value=(
                        'provider "aws" {\n'
                        'region = var.aws_region\n'
                        '}'
                    ),
                    line_number=None,
                    resource=None,
                    auto_fixable= True,
                    validator= self.validator_name,
                )
            )

        #provider version pinned
        if analysis["providers"]:
            provider_blocks= re.finditer(
                r'provider\s+"[^"]+"\s*\{(.*?)\}',
                content,
                re.DOTALL
            )

            for block in provider_blocks:
                provider_text=block.group(1)

                if "version" not in provider_text:
                    recommendations.append(
                    Recommendation(
                        category=RecommendationCategory.CONFIGURATION,
                        severity= Severity.MEDIUM,
                        title="Provider Version Not Pinned",
                        message=(
                            "Specify a provider version to ensure"
                            "consistent deployments."
                        ),
                        suggested_value='version - "~> 5.0"',
                        line_number=None,
                        resource=None,
                        auto_fixable= True,
                        validator= self.validator_name,
                    )
                )
                
        #variable declarations
        declared_variables=[]
        referenced_variables=[]
        if analysis["variables"]:
            declared_variables=re.findall(
                r'variable\s+"([^"]+)"',
                content
                )
            referenced_variables=re.findall(
                r'var\.([A-Za-z0-9_]+)',
                content
            )

        declared_set= set(declared_variables)
        referenced_set= set(referenced_variables)

        #missing variable declaration
        missing=referenced_set-declared_set

        for variable in sorted(missing):
            recommendations.append(
                Recommendation(
                    category=RecommendationCategory.CONFIGURATION,
                    severity= Severity.HIGH,
                    title="Undefined Varaible",
                    message=f"Variable {variable} is referenced but not declared.",
                    suggested_value=(
                        f'variable "{variable}" {{\n'
                        f'type = string\n'
                        f'}}'
                    ),
                    line_number=None,
                    resource=None,
                    auto_fixable= True,
                    validator= self.validator_name,
                )
            )
        
        #duplicate variable declaration
        duplicates={
            variable
            for variable in declared_variables
            if declared_variables.count(variable)>1
        }

        for variable in duplicates:
            recommendations.append(
                Recommendation(
                    category=RecommendationCategory.CONFIGURATION,
                    severity= Severity.MEDIUM,
                    title="Duplicate Variable Declaration",
                    message=f"Variable {variable} is declared multiple times.",
                    suggested_value= "Remove duplicate variable declaration.",
                    line_number=None,
                    resource=None,
                    auto_fixable= False,
                    validator= self.validator_name,
                )
            )

        #harcoded instance types
        if "aws_instance" in analysis["resources"]:
            for match in re.finditer(
                r'instance_type\s*=\s*"([^"]+)"',
                content
            ):
                recommendations.append(
                    Recommendation(
                        category=RecommendationCategory.CONFIGURATION,
                        severity= Severity.LOW,
                        title="Hardcoded Instance Type",
                        message=(
                            "Use a Terraform variable instead of a"
                            "hardcoded instance type."
                        ),
                        line_number=get_line_number(
                            content,
                            match.group(0)
                        ),
                        resource=None,
                        original_value=match.group(0),
                        suggested_value="instance_type = var.instance_type",
                        auto_fixable= True,
                        validator= self.validator_name,
                    )
                )

        execution_time= (
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
            execution_time_ms=round(execution_time,2),
            recommendations=recommendations,
        )