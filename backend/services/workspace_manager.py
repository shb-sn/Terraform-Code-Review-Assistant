"""
Manages review workspaces for terraform file processing.
This module contains workspace-related business logic. 
Responsibilities:
Generate review workspaces
Store uploaded terraform files
return workspace paths
cleanup workspaces after processing
"""

from pathlib import Path
from fastapi import HTTPException, UploadFile
from config.settings import (
    OUTPUT_DIR,
    REVIEWED_FILENAME,
    UPLOAD_DIR,
    WORKSPACE_PREFIX,
)
from utils.helpers import(
    delete_directory,
    save_uploaded_file,
    generate_review_id,
)

class WorkspaceManager:
    #handles creation and lifecycle of temporary review workspaces
    def create_workspace(self) -> dict:
        #create new review workspace and returns dict workspace metadata
        review_id=generate_review_id()

        upload_dir= UPLOAD_DIR/f"{WORKSPACE_PREFIX}{review_id}"
        output_dir= OUTPUT_DIR/f"{WORKSPACE_PREFIX}{review_id}"

        upload_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        return{
            "review_id": review_id,
            "upload_dir": upload_dir,
            "output_dir": output_dir,
            "reviewed_file": output_dir/REVIEWED_FILENAME,
        }
    
    def save_terraform_file(
            self,
            workspace:dict,
            upload_file:UploadFile,
    ) -> Path:
        """save uploaded terraform file into workspace
        returns saved file path
        """
        return save_uploaded_file(
            upload_file=upload_file,
            destination=workspace["upload_dir"],
        )
    
    def get_workspace(self, review_id:str) -> dict:
        #retrieve an existing workspace
        upload_dir=UPLOAD_DIR/f"{WORKSPACE_PREFIX}{review_id}"
        output_dir= OUTPUT_DIR/f"{WORKSPACE_PREFIX}{review_id}"

        if not upload_dir.exists():
            raise HTTPException(
                status_code=404,
                detail="Workspace not found."
            )
        
        terraform_files=list(upload_dir.glob("*.tf"))

        if not terraform_files:
            raise HTTPException(
                status_code=404,
                detail="Terraform file not found."
            )
        
        return{
            "review_id": review_id,
            "upload_dir": upload_dir,
            "output_dir": output_dir,
            "terraform_file": terraform_files[0],
            "reviewed_file": output_dir/REVIEWED_FILENAME,
        }
    
    def cleanup_workspace(self, review_id:str) -> None:
        #delete output workspace directories
        output_dir= OUTPUT_DIR/f"{WORKSPACE_PREFIX}{review_id}"
        delete_directory(output_dir)