"""
Download endpoint.

Workflow

1. Retrieve workspace.
2. Verify reviewed Terraform file exists.
3. Return download metadata.
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
)

from fastapi.responses import FileResponse

from models.api_models import (
    DownloadResponse,
)

from services.workspace_manager import (
    WorkspaceManager,
)

router = APIRouter(
    prefix="/download",
    tags=["Download"],
)

workspace_manager = WorkspaceManager()


@router.get(
    "/{review_id}",
    response_model=DownloadResponse,
)
def download(
    review_id: str,
) -> DownloadResponse:

    try:

        workspace = workspace_manager.get_workspace(
            review_id
        )

        reviewed_file = workspace[
            "reviewed_file"
        ]

        if not reviewed_file.exists():
            raise HTTPException(
                status_code=404,
                detail="Reviewed Terraform file not found.",
            )

        return DownloadResponse(
            review_id=review_id,
            filename=reviewed_file.name,
            download_url=f"/download/file/{review_id}",
        )

    except HTTPException:
        raise

    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=str(exception),
        ) from exception

@router.get("/file/{review_id}")
def download_file(review_id: str):
 
    workspace = workspace_manager.get_workspace(review_id)
 
    reviewed_file = workspace["reviewed_file"]
 
    if not reviewed_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Reviewed file not found."
        )
 
    return FileResponse(
        path=reviewed_file,
        filename=reviewed_file.name,
        media_type="text/plain",
    )