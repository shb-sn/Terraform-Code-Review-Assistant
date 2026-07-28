"""
Pydantic request and response models for the application.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from models.recommendation import Recommendation
from models.validation_result import ValidationResult

#upload models
class UploadResponse(BaseModel):
    #response returned after successfully uploading a .tf file
    model_config = ConfigDict(extra="forbid")

    review_id: str= Field(..., description="Unique review session ID.")
    filename: str= Field(..., description="Original uploaded filename.")
    message: str= Field(..., description="Upload status message.")

#review models
class ReviewRequest(BaseModel):
    #request model for initiating validation
    model_config = ConfigDict(extra="forbid")
    review_id: str= Field(..., description= "Unique review session ID.")

class ReviewResponse(BaseModel):
    #complete validation response returned to the frontend
    model_config = ConfigDict(extra="forbid")
    review_id: str
    syntax_report: ValidationResult
    formatting_report: ValidationResult
    security_report: ValidationResult
    configuration_report: ValidationResult
    best_practice_report: ValidationResult
    optimization_report: ValidationResult
    recommendations: List[Recommendation]
    overall_status: str

#apply recommendations models

class ApplyRequest(BaseModel):
    #request containing accepted and rejected recommendation IDs
    model_config = ConfigDict(extra="forbid")
    review_id:str
    accepted_recommendations: List[str] = Field(default_factory=list)
    rejected_recommendations: List[str] = Field(default_factory=list)

class ApplyResponse(BaseModel):
    #response after applying accepted recommendations
    model_config= ConfigDict(extra="forbid")
    review_id:str
    reviewed_filename:str
    accepted_recommendations: List[str]
    rejected_recommendations: List[str]
    message: str

#download models
class DownloadResponse(BaseModel):
    #metadata returned before downloading the reviewed file
    model_config=ConfigDict(extra="forbid")
    review_id:str
    filename:str
    download_url:str

#generic error model
class ErrorResponse(BaseModel):
    #generic API error response
    model_config=ConfigDict(extra="forbid")
    detail:str

#health check model
class HealthResponse(BaseModel):
    #API health check response
    model_config= ConfigDict(extra="forbid")
    application:str
    version:str
    status:str