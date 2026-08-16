"""
Apply endpoint.

Workflow

1. Retrieve workspace.
2. Get cached recommendations.
3. Filter accepted recommendations.
4. Generate reviewed Terraform file.
5. Return ApplyResponse.
"""

from __future__ import annotations
import requests
from fastapi import (
    APIRouter,
    HTTPException,
)

from models.api_models import (
    ApplyRequest,
    ApplyResponse,
)
from services.service_container import(
    workspace_manager,
    recommendation_engine
)
from services.file_generator import (
    FileGenerator,
)

router = APIRouter(
    prefix="/apply",
    tags=["Apply"],
)

file_generator = FileGenerator()

@router.post(
    "",
    response_model=ApplyResponse,
)
def apply(
    request: ApplyRequest,
) -> ApplyResponse:

    try:

        workspace = workspace_manager.get_workspace(
            request.review_id
        )

        terraform_file = workspace[
            "terraform_file"
        ]

        recommendations = (
            recommendation_engine.get_cached_recommendations(
                request.review_id,
            )
        )

        accepted_recommendations = (
            recommendation_engine.get_recommendations(
                request.accepted_recommendations,
                recommendations,
            )
        )

        print("="*60)
        print("Total cached recommendations:", len(recommendations))
        print("Accepted IDs:", request.accepted_recommendations)
        print("Accepted recommendation objects:", len(accepted_recommendations))

        for r in accepted_recommendations:
            print(
                r.title,
                r.auto_fixable,
                repr(r.original_value),
                repr(r.suggested_value)
            )

        try:
            reviewed_file = file_generator.generate(
                original_file=terraform_file,
                accepted_recommendations=accepted_recommendations,
                output_directory=workspace["output_dir"],
            )

        except Exception:
            import traceback
            traceback.print_exc()
            raise

        recommendation_engine.clear_cached_recommendations(
            request.review_id
        )

        return ApplyResponse(
            review_id=request.review_id,
            reviewed_filename=reviewed_file.name,
            accepted_recommendations=(
                request.accepted_recommendations
            ),
            rejected_recommendations=(
                request.rejected_recommendations
            ),
            message=(
                "Recommendations applied successfully."
            ),
        )

    except HTTPException:
        raise

    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=str(exception),
        ) from exception