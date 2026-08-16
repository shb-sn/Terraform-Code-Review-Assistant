"""
Application configuration setting.
This module contains all configurable constants used throught the application.
"""

from pathlib import Path

#Project Directories

BASE_DIR: Path = Path(__file__).resolve().parent.parent
UPLOAD_DIR: Path = BASE_DIR / "uploads"
OUTPUT_DIR: Path = BASE_DIR / "output"

#Terraform configuration
TERRAFORM_EXECUTABLE: str = "terraform"

#File upload configuration
MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB

#Allowed terraform file extensions
ALLOWED_EXTENSIONS: set[str]= {
    ".tf",
    }

#Workspace configuration
WORKSPACE_PREFIX: str = "review_"  #prefix used when creating temporary workspace for review

#Output configuration
REVIEWED_FILENAME: str = "reviewed.tf"

#Logging
LOG_LEVEL: str = "INFO"

LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

#Security

#No of characters to display while masking secrets
SECRET_VISIBLE_CHARS: int = 4

#Recommendation serverity levels
SEVERITY_HIGH: str = "High"
SEVERITY_MEDIUM: str = "Medium"
SEVERITY_LOW: str = "Low"

#Validation status
STATUS_SUCCESS: str = "Success"
STATUS_WARNING: str = "Warning"
STATUS_FAILED: str = "Failed"

#Ensure required directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

#APIs
API_TITLE="Terraform Code Review Assistant"
API_VERSION="1.0.0"
API_DESCRIPTION=(
    "Backend API for reviewing Terraform code"
)