from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
import logging
import sys
import os

from app.core.config import settings
from app.core.environment import EnvironmentChecker
# V1 endpoints removed - using V2 only
from app.v2.api.scope import router as v2_scope_router  # Real V2 API
# Cost DNA removed - Clean Engine V2 handles all costs
# from app.api.v1 import cost_dna
from app.db.database import engine, Base

logger = logging.getLogger(__name__)


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize Redis cache
    try:
        redis_url = getattr(settings, 'redis_url', 'redis://localhost:6379')
        redis = aioredis.from_url(redis_url, encoding="utf8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis), prefix="specsharp-cache:")
        logger.info("✅ Redis cache initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ Redis cache initialization failed: {e}. Continuing without cache.")
    
    yield
    
    # Cleanup
    try:
        await FastAPICache.clear()
    except:
        pass


# Disable API documentation in production for security
if settings.environment == "production":
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
        docs_url=None,  # Disable /docs
        redoc_url=None,  # Disable /redoc
        openapi_url=None  # Disable /openapi.json
    )
else:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan
    )

# Add rate limiter to app state
app.state.limiter = limiter

# Add rate limit exceeded handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add GZip compression middleware (compress responses > 1KB)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Log CORS configuration for debugging
logger.info(f"CORS Origins configured: {settings.cors_origins}")
logger.info(f"Environment: {settings.environment}")
logger.info(f"Frontend URL: {settings.frontend_url}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add session middleware for OAuth state management
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key or settings.secret_key
)

# V2 API - Real endpoints using unified_engine
app.include_router(v2_scope_router, tags=["v2-api"])
# Cost DNA removed - Clean Engine V2 handles all costs

@app.on_event("startup")
async def startup_event():
    """Run additional startup checks"""
    logger.info("FastAPI application ready")
    
    # Verify database connection
    try:
        from app.db.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("✅ Database connection verified")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        if EnvironmentChecker.get_environment() == "production":
            sys.exit(1)
    
    # Log CORS configuration based on environment
    env = EnvironmentChecker.get_environment()
    if env == "development":
        logger.info("CORS: Development origins enabled (localhost)")
    else:
        logger.info(f"CORS: Production origins enabled")
        if EnvironmentChecker.is_testing_mode():
            logger.error("🚨 WARNING: Testing mode active in production environment!")
    
    logger.info("🚀 SpecSharp Backend Ready")


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "SpecSharp API",
        "cors_origins": settings.cors_origins,
        "environment": settings.environment,
        "frontend_url": settings.frontend_url
    }