"""
Application entry point.

Creates the FastAPI application, registers all routes,
configures CORS and exposes a health endpoint.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import (
    API_TITLE,
    API_VERSION,
    API_DESCRIPTION,
)

from models.api_models import (
    HealthResponse,
)

from routes.upload import router as upload_router
from routes.review import router as review_router
from routes.apply import router as apply_router
from routes.download import router as download_router


app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(upload_router)
app.include_router(review_router)
app.include_router(apply_router)
app.include_router(download_router)


@app.get(
    "/",
    tags=["Health"],
)
def root() -> dict[str, str]:

    return {
        "message": (
            "Terraform Code Review Assistant API"
        )
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
)
def health() -> HealthResponse:

    return HealthResponse(
        application=API_TITLE,
        version=API_VERSION,
        status="Healthy",
    )