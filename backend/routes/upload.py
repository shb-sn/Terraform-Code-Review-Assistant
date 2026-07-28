"""
Upload endpoint.

Workflow

1. Validate uploaded Terraform file.
2. Create temporary workspace.
3. Save uploaded file.
4. Return review ID.
"""

from _future_ import annotations

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from models.api_models import (
    UploadResponse,
)

from services.workspace_manager import (
    WorkspaceManager,
)

from utils.helpers import (
    is_valid_terraform_file,
)

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)

workspace_manager = WorkspaceManager()


@router.post(
    "",
    response_model=UploadResponse,
)
def upload(
    terraform_file: UploadFile = File(...),
) -> UploadResponse:

    try:

        if not is_valid_terraform_file(
            terraform_file
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Only Terraform (.tf) files are allowed."
                ),
            )

        workspace = (
            workspace_manager.create_workspace()
        )

        workspace_manager.save_terraform_file(
            workspace,
            terraform_file,
        )

        return UploadResponse(
            review_id=workspace["review_id"],
            filename=str(terraform_file.filename),
            message=(
                "Terraform file uploaded successfully."
            ),
        )

    except HTTPException:
        raise

    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=str(exception),
        ) from exception