"""Route initialization for the API."""

from app.api.routes.common import router as common_router
from app.api.routes.processing import router as processing_router

__all__ = ["common_router", "processing_router"]