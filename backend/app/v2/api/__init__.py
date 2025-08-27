"""V2 API module"""

from fastapi import APIRouter
from .scope import router as scope_router
from .comparison import router as comparison_router

# Create main v2 router
router = APIRouter()

# Include sub-routers
router.include_router(scope_router)
router.include_router(comparison_router)

__all__ = ['router']