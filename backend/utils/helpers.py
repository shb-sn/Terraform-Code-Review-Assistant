"""
Reusable utility  functions for the application
It only contains generic helper functions
"""

from __future__ import annotations
import logging
from re import sub
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Optional
from fastapi import HTTPException, UploadFile
from config.settings import(
    MAX_FILE_SIZE,
    TERRAFORM_EXECUTABLE,
    ALLOWED_EXTENSIONS,
    SECRET_VISIBLE_CHARS
)

logger= logging.getLogger(__name__)


#uuid
def generate_review_id() -> str:
    #generate a unique review ID
    return str(uuid.uuid4())


#file validation
def is_valid_terraform_file(upload_file:UploadFile) -> bool:
    """validate uploaded terraform file"""
    if upload_file.filename is None:
        return False
    
    extension=Path(upload_file.filename).suffix.lower()
    return extension in ALLOWED_EXTENSIONS

def validate_file_size(file_path:Path) -> None:
    """validate uploaded file size"""
    size=file_path.stat().st_size

    if size>MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {MAX_FILE_SIZE} bytes."
        )
    

#file operations
def save_uploaded_file(
        upload_file:UploadFile,
        destination:Path,
) -> Path:
    """save uploaded file"""
    destination.mkdir(parents=True, exist_ok=True)
    assert upload_file.filename is not None
    file_path= destination / upload_file.filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

        validate_file_size(file_path)

        logger.info("Saved files: %s", file_path)

        return file_path
    
    except Exception as e:
        logger.exception("Failed saving uploaded file.")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    

def read_file(file_path: Path) -> str:
    """read a UTF-8 text file"""
    try:
        return file_path.read_text(encoding="utf-8")

    except Exception as e:
        logger.exception("Unable to read file.")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


def write_file(
    file_path: Path,
    content: str,
) -> None:
    """write a UTF-8 text file"""
    try:
        file_path.write_text(content, encoding="utf-8")
        logger.info("Written file: %s", file_path)

    except Exception as e:
        logger.exception("Unable to write file.")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
        
def delete_file(file_path:Path) -> None:
    """delete a file if it exists"""
    try:
        if file_path.exists():
            file_path.unlink()

    except Exception as e:
        logger.exception("Unable to delete file.")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
def delete_directory(directory:Path) -> None:
    """delete directory recursively"""
    try:
        if directory.exists():
            shutil.rmtree(directory)

    except Exception as e:
        logger.exception("Unableto delete directory.")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
#terraform helpers
def run_terraform_commands(
        commands: list[str],
        working_directory:Path,
) -> subprocess.CompletedProcess:
    """execute a terraform command"""
    try:
        result=subprocess.run(
            commands,
            cwd=working_directory,
            capture_output=True,
            text=True,
            check=False
        )
        return result
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"{TERRAFORM_EXECUTABLE} executable not found."
        ) from e
    
def terraform_init(working_directory: Path) -> subprocess.CompletedProcess:
    """run terraform init"""
    if (working_directory / ".terraform").exists():
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="Already initialized",
            stderr="",
        )
    return run_terraform_commands(
        [
            TERRAFORM_EXECUTABLE,
            "init",
            "-backend=false",
            "-input=false",
            "-no-color",
        ], 
        working_directory,
    )

def terraform_validate(working_directory: Path) -> subprocess.CompletedProcess:
    """run terraform validate"""
    return run_terraform_commands(
        [
            TERRAFORM_EXECUTABLE,
            "validate",
            "-no-color",
        ],
        working_directory,
    )

def terraform_fmt_check(working_directory: Path) -> subprocess.CompletedProcess:
    """run terraform fmt-check"""
    return run_terraform_commands(
        [
            TERRAFORM_EXECUTABLE,
            "fmt",
            "-check",
            "-recursive",
        ],
        working_directory,
    )

#security helpers
def mask_secret(secret:Optional[str]) -> str:
    """mask a secret before returning it
    admin1234 becomes *****1234"""
    if not secret:
        return ""
    
    visible= SECRET_VISIBLE_CHARS

    if len(secret) <= visible:
        return "*" * len(secret)
    
    return "*" * (len(secret)-visible) + secret[-visible:]

#miscalleneous
def get_line_number(
        file_content:str,
        search_text:str,
) -> Optional[int]:
    """
    find the first line number containing the search text
    """
    for index, line in enumerate(file_content.splitlines(), start=1):
        if search_text in line:
            return index
        
    return None