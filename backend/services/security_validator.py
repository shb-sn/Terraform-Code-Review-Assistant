"""
Performs rule-based security validation on Terraform files.

Checks include:
- Hardcoded passwords
- Secrets
- API keys
- AWS credentials
- GitHub tokens
- JWT tokens
- Private keys
- Open CIDR blocks
- Public resources
- IAM wildcards
- Encryption disabled
- HTTP endpoints
- Public S3 buckets

This validator is completely rule-based and does not use AI or LLMs.
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

from utils.regex_patterns import (
    PASSWORD_PATTERN,
    SECRET_PATTERN,
    API_KEY_PATTERN,
    AWS_ACCESS_KEY_PATTERN,
    AWS_SECRET_ACCESS_KEY_PATTERN,
    BEARER_TOKEN_PATTERN,
    TOKEN_PATTERN,
    GITHUB_TOKEN_PATTERN,
    GOOGLE_API_KEY_PATTERN,
    AZURE_STORAGE_ACCOUNT_KEY_PATTERN,
    JWT_PATTERN,
    RSA_PRIVATE_KEY_PATTERN,
    SSH_PRIVATE_KEY_PATTERN,
    SENSITIVE_VARIABLE_PATTERN,
    OPEN_CIDR_PATTERN,
    PUBLIC_RESOURCE_PATTERN,
    IAM_WILDCARD_ACTION_PATTERN,
    IAM_WILDCARD_RESOURCE_PATTERN,
    ENCRYPTION_DISABLED_PATTERN,
    HTTP_URL_PATTERN,
    S3_PUBLIC_ACL_PATTERN,
    S3_PUBLIC_POLICY_PATTERN,
    S3_PUBLIC_ACCESS_BLOCK_PATTERN,
)


class SecurityValidator:

    validator_name = "SecurityValidator"

    def __init__(self) -> None:

        self.rules = [

            (
                PASSWORD_PATTERN,
                "Hardcoded Password",
                "Replace the hardcoded password with a Terraform variable.",
                Severity.HIGH,
                True,
            ),

            (
                SECRET_PATTERN,
                "Hardcoded Secret",
                "Store secrets securely using Terraform variables or a secret manager.",
                Severity.HIGH,
                True,
            ),

            (
                API_KEY_PATTERN,
                "Hardcoded API Key",
                "Avoid hardcoding API keys.",
                Severity.HIGH,
                True,
            ),

            (
                AWS_ACCESS_KEY_PATTERN,
                "AWS Access Key Exposed",
                "Remove AWS access keys from Terraform code.",
                Severity.HIGH,
                True,
            ),

            (
                AWS_SECRET_ACCESS_KEY_PATTERN,
                "AWS Secret Access Key Exposed",
                "Move AWS secret access keys to a secure location.",
                Severity.HIGH,
                True,
            ),

            (
                BEARER_TOKEN_PATTERN,
                "Bearer Token Exposed",
                "Store bearer tokens securely.",
                Severity.HIGH,
                True,
            ),

            (
                TOKEN_PATTERN,
                "Hardcoded Token",
                "Avoid storing authentication tokens directly.",
                Severity.HIGH,
                True,
            ),

            (
                GITHUB_TOKEN_PATTERN,
                "GitHub Token Exposed",
                "GitHub Personal Access Tokens should never be committed.",
                Severity.HIGH,
                True,
            ),

            (
                GOOGLE_API_KEY_PATTERN,
                "Google API Key Exposed",
                "Move API keys to secure variables.",
                Severity.HIGH,
                True,
            ),

            (
                AZURE_STORAGE_ACCOUNT_KEY_PATTERN,
                "Azure Storage Account Key Exposed",
                "Store Azure Storage credentials securely.",
                Severity.HIGH,
                True,
            ),

            (
                JWT_PATTERN,
                "JWT Token Exposed",
                "JWT tokens should never be stored inside Terraform.",
                Severity.HIGH,
                True,
            ),

            (
                RSA_PRIVATE_KEY_PATTERN,
                "Private Key Detected",
                "Private keys should never be committed.",
                Severity.HIGH,
                False,
            ),

            (
                SSH_PRIVATE_KEY_PATTERN,
                "SSH Private Key Detected",
                "SSH private keys should never be committed.",
                Severity.HIGH,
                False,
            ),

            (
                SENSITIVE_VARIABLE_PATTERN,
                "Sensitive Variable Found",
                "Sensitive Terraform variable detected.",
                Severity.MEDIUM,
                False,
            ),

            (
                OPEN_CIDR_PATTERN,
                "Open Security Group",
                "Restrict 0.0.0.0/0 wherever possible.",
                Severity.HIGH,
                True,
            ),

            (
                PUBLIC_RESOURCE_PATTERN,
                "Public Resource",
                "Avoid exposing resources publicly.",
                Severity.HIGH,
                True,
            ),

            (
                IAM_WILDCARD_ACTION_PATTERN,
                "IAM Wildcard Action",
                "Avoid Action=\"*\".",
                Severity.HIGH,
                True,
            ),

            (
                IAM_WILDCARD_RESOURCE_PATTERN,
                "IAM Wildcard Resource",
                "Avoid Resource=\"*\".",
                Severity.HIGH,
                True,
            ),

            (
                ENCRYPTION_DISABLED_PATTERN,
                "Encryption Disabled",
                "Enable encryption.",
                Severity.HIGH,
                True,
            ),

            (
                HTTP_URL_PATTERN,
                "Insecure HTTP URL",
                "Use HTTPS instead of HTTP.",
                Severity.MEDIUM,
                True,
            ),

            (
                S3_PUBLIC_ACL_PATTERN,
                "Public S3 ACL",
                "Avoid public bucket ACLs.",
                Severity.HIGH,
                True,
            ),

            (
                S3_PUBLIC_POLICY_PATTERN,
                "Public S3 Bucket Policy",
                "Avoid Principal=\"*\" in bucket policies.",
                Severity.HIGH,
                True,
            ),

            (
                S3_PUBLIC_ACCESS_BLOCK_PATTERN,
                "S3 Public Access Block Disabled",
                "Enable all S3 Public Access Block settings.",
                Severity.HIGH,
                True,
            ),
        ]

    def validate(
        self,
        terraform_file: Path,
        analysis,
    ) -> ValidationResult:

        start_time = time.perf_counter()

        content = read_file(
            terraform_file
        )

        recommendations: list[
            Recommendation
        ] = []

        for (
            pattern,
            title,
            message,
            severity,
            auto_fixable,
        ) in self.rules:

            matches = re.finditer(
                pattern,
                content,
                flags=re.MULTILINE,
            )

            for match in matches:

                matched_text = match.group().splitlines()[0]
                full_line=matched_text.strip()

                line_number = get_line_number(
                    content,
                    matched_text,
                )

                recommendations.append(
                    Recommendation(
                        category=RecommendationCategory.SECURITY,
                        severity=severity,
                        title=title,
                        message=message,
                        line_number=line_number,
                        resource=None,
                        original_value=matched_text,
                        suggested_value=self._get_suggested_value(
                            title
                        ),
                        auto_fixable=auto_fixable,
                        validator=self.validator_name,
                    )
                )

        unique_recommendations: list[
            Recommendation
        ] = []

        seen: set[
            tuple[str, int | None]
        ] = set()

        for recommendation in recommendations:

            key = (
                recommendation.title,
                recommendation.line_number,
            )

            if key not in seen:
                seen.add(key)
                unique_recommendations.append(
                    recommendation
                )

        recommendations = unique_recommendations

        execution_time = (
            time.perf_counter()
            - start_time
        ) * 1000

        status = (
            STATUS_SUCCESS
            if not recommendations
            else STATUS_WARNING
        )

        return ValidationResult(
            validator=self.validator_name,
            status=status,
            issues_found=len(
                recommendations
            ),
            execution_time_ms=round(
                execution_time,
                2,
            ),
            recommendations=recommendations,
        )
    
    def _get_suggested_value(
        self,
        title: str,
    ) -> str | None:

        suggestions = {

            "Hardcoded Password":
            "password = var.db_password",

            "Hardcoded Secret":
            "secret = var.secret",

            "Hardcoded API Key":
            "api_key = var.api_key",

            "AWS Access Key Exposed":
            "access_key = var.aws_access_key",

            "AWS Secret Access Key Exposed":
            "secret_key = var.aws_secret_access_key",

            "Bearer Token Exposed":
            "token = var.bearer_token",

            "Hardcoded Token":
            "token = var.access_token",

            "GitHub Token Exposed":
            "github_token = var.github_token",

            "Google API Key Exposed":
            "google_api_key = var.google_api_key",

            "Azure Storage Account Key Exposed":
            "azure_storage_account_key = var.azure_storage_account_key",

            "JWT Token Exposed":
            "jwt = var.jwt",

            "Private Key Detected":
            None,

            "SSH Private Key Detected":
            None,

            "Sensitive Variable Found":
            None,

            "Open Security Group":
            'cidr_blocks = ["10.0.0.0/24"]',

            "Public Resource":
            "public_accessible = false",

            "IAM Wildcard Action":
            'Action = ["ec2:Describe*"]',

            "IAM Wildcard Resource":
            'Resource = aws_instance.example.arn',

            "Encryption Disabled":
            "encryption = true",

            "Insecure HTTP URL":
            "https://",

            "Public S3 ACL":
            'acl = "private"',

            "Public S3 Bucket Policy":
            '"Principal": {"AWS":"123456789012"}',

            "S3 Public Access Block Disabled":
            """block_public_acls = true
            block_public_policy = true
            ignore_public_acls = true
            restrict_public_buckets = true""",

            "Encryption Disabled":
            "encrypted = true",
 
            "Metadata Service Not Secured":
            'http_tokens = "required"',
 
            "Public S3 ACL":
            'acl = "private"',
 
            "S3 Versioning Disabled":
            "enabled = true",
 
            "Public Database":
            "publicly_accessible = false",
 
            "Skip Final Snapshot Enabled":
            "skip_final_snapshot = false",
 
            "Open Security Group":
            'cidr_blocks = ["10.0.0.0/24"]',
        }

        return suggestions.get(title)