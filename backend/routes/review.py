"""
Review endpoint.

Workflow

1. Retrieve workspace.
2. Get uploaded Terraform file.
3. Run Validation Engine.
4. Generate recommendations.
5. Return complete review response.
"""

from _future_ import annotations
import traceback

from fastapi import APIRouter, HTTPException

from models.api_models import (
    ReviewRequest,
    ReviewResponse,
)
from models.validation_result import (
    ValidationResult,
)
from services.validation_engine import (
    ValidationEngine,
)
from services.service_container import(
    workspace_manager,
    recommendation_engine
)

router = APIRouter(
    prefix="/review",
    tags=["Review"],
)


validation_engine = ValidationEngine()

@router.post(
    "",
    response_model=ReviewResponse,
)
def review(
    request: ReviewRequest,
) -> ReviewResponse:

    try:

        workspace = workspace_manager.get_workspace(
            request.review_id
        )

        terraform_file = workspace[
            "terraform_file"
        ]

        validation_results = validation_engine.run(
            terraform_file
        )

        recommendations = (
            recommendation_engine.generate(
                request.review_id,
                validation_results,
            )
        )

        reports = {
            result.validator: result
            for result in validation_results
        }

        def get_report(
            validator: str,
        ) -> ValidationResult:

            return reports.get(
                validator,
                ValidationResult(
                    validator=validator,
                    status="Success",
                    issues_found=0,
                    execution_time_ms=0,
                    recommendations=[],
                ),
            )

        overall_status = "Success"

        for result in validation_results:

            if result.status == "Failed":
                overall_status = "Failed"
                break

            if (
                result.status == "Warning"
                and overall_status != "Failed"
            ):
                overall_status = "Warning"

        return ReviewResponse(
            review_id=request.review_id,
            syntax_report=get_report(
                "SyntaxValidator",
            ),
            formatting_report=get_report(
                "FormattingValidator",
            ),
            security_report=get_report(
                "SecurityValidator",
            ),
            configuration_report=get_report(
                "ConfigurationValidator",
            ),
            best_practice_report=get_report(
                "BestPracticeValidator",
            ),
            optimization_report=get_report(
                "OptimizationValidator",
            ),
            recommendations=recommendations,
            overall_status=overall_status,
        )

    except HTTPException:
        raise

    except Exception as exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(exception),
        ) from exception