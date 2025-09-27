"""Main FastAPI application for medical report processing."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.api.routes.common import router as common_router
from app.api.routes.processing import router as processing_router
from app.api.simple_middleware import RateLimitMiddleware
from app.core.config import settings

FastAPI_description ="""
Endpoints to convert medical reports (typed or OCR-scanned) into structured, understandable output.
Rate limiting is applied to processing endpoints only.
Example of Text for text processing: endpoints/process-text
```
CBC: Hemglobin 10.2 g/dL (Low),
WBC 11200 /uL (Hgh)
```
"""

# Create main FastAPI application
app = FastAPI(
    title="Medical Report Processor",
    description="API for processing medical reports with OCR and structured output" + FastAPI_description,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting middleware for processing endpoints only
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
    target_paths=["/api/v1/process"]  # Only rate limit processing endpoints
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(processing_router)
# Include common routes (no rate limiting)
app.include_router(common_router)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": f"Internal server error: {str(exc)}",
            "data": None
        }
    )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Medical Report Processor API",
        "version": "1.0.0",
        "description": "Convert medical reports (typed or OCR-scanned) into structured, understandable output",
        "endpoints": {
            "common": {
                "health": "/api/v1/health",
                "supported_tests": "/api/v1/supported-tests"
            },
            "processing": {
                "process": "/api/v1/process",
                "process_text": "/api/v1/process-text", 
                "process_image": "/api/v1/process-image",
                "process_image_base64": "/api/v1/process-image-base64"
            }
        },
        "rate_limiting": {
            "enabled_for": "processing endpoints only",
            "requests_per_minute": settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
            "exempt_endpoints": ["/api/v1/health", "/api/v1/supported-tests"]
        },
        "docs": "/docs"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=4001,
        reload=True
    )