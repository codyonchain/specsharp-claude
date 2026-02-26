from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
import logging
import sys

from app.core.config import settings
from app.core.environment import EnvironmentChecker
from app.core.rate_limiter import limiter
from app.v2.api.scope import router as v2_scope_router
from app.v2.api.auth import router as v2_auth_router
from app.db.database import engine, Base

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Initialize Redis cache (best-effort)
    try:
        redis_url = getattr(settings, "redis_url", "redis://localhost:6379")
        redis = aioredis.from_url(redis_url, encoding="utf8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis), prefix="specsharp-cache:")
        logger.info("✅ Redis cache initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ Redis cache initialization failed: {e}. Continuing without cache.")

    yield

    # Cleanup (best-effort)
    try:
        await FastAPICache.clear()
    except Exception:
        pass


# Disable API docs in production
if settings.environment == "production":
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
else:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)

if settings.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

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

# Session middleware used for OAuth flows if needed
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key or settings.secret_key
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Permissions-Policy",
        "geolocation=(), microphone=(), camera=(), payment=(), usb=(), accelerometer=()",
    )
    response.headers.setdefault("X-Frame-Options", "DENY")
    if settings.environment == "production":
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none';",
        )
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains; preload",
        )
    return response

# V2 API - unified_engine endpoints
app.include_router(v2_scope_router, prefix="/api/v2", tags=["v2-api"])
app.include_router(v2_auth_router, prefix="/api/v2", tags=["v2-auth"])


@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application ready")

    # Verify DB connection
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

    logger.info("🚀 SpecSharp Backend Ready")


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "SpecSharp API",
        "cors_origins": settings.cors_origins,
        "environment": settings.environment,
        "frontend_url": settings.frontend_url,
    }
