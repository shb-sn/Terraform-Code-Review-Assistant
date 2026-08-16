"""
Analyzes a terraform file and extracts metadata required by the validation engine
this module does not perform any configuration
it only discover providers, resources, variables, outputs, modules, locals, data sources
"""

from __future__ import annotations
import re
from pathlib import Path

from utils.helpers import read_file

class TerraformAnalyzer:
    #extract metadata from terraform config
    def analyze(
            self,
            terraform_file: Path
    ) -> dict:
        """
        analyze a terraform file
        return dict metadata extracted from the file
        """

        content=read_file(terraform_file)

        providers= sorted(
            set(
                re.findall(
                    r'provider\s+"([^"]+)"',
                    content,
                    re.IGNORECASE
                )
            )
        )

        resources= sorted(
            set(
                re.findall(
                    r'resource\s+"([^"]+)"\s+"[^"]+"',
                    content,
                    re.IGNORECASE
                )
            )
        )

        variables= sorted(
            set(
                re.findall(
                    r'variable\s+"([^"]+)"',
                    content,
                    re.IGNORECASE
                )
            )
        )

        outputs= sorted(
            set(
                re.findall(
                    r'output\s+"([^"]+)"',
                    content,
                    re.IGNORECASE
                )
            )
        )

        modules= sorted(
            set(
                re.findall(
                    r'module\s+"([^"]+)"',
                    content,
                    re.IGNORECASE
                )
            )
        )

        data_sources= sorted(
            set(
                re.findall(
                    r'data\s+"([^"]+)"\s+"[^"]+"',
                    content,
                    re.IGNORECASE
                )
            )
        )

        locals_present= bool(
            re.search(
                r'locals\s*\{',
                content,
                re.IGNORECASE
            )
        )

        return {
        "providers": providers,
        "resources": resources,
        "variables": variables,
        "outputs": outputs,
        "modules": modules,
        "data_sources": data_sources,
        "locals": locals_present,
    
        "has_provider": len(providers) > 0,
        "has_resources": len(resources) > 0,
        "has_variables": len(variables) > 0,
        "has_outputs": len(outputs) > 0,
        "has_modules": len(modules) > 0,
    
        "has_ec2": "aws_instance" in resources,
        "has_s3": "aws_s3_bucket" in resources,
        "has_rds": "aws_db_instance" in resources,
        "has_vpc": "aws_vpc" in resources,
        "has_security_group": "aws_security_group" in resources,
        "has_lambda": "aws_lambda_function" in resources,
        "has_iam": any(r.startswith("aws_iam") for r in resources),
    }