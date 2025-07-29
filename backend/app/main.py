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

from app.core.config import settings
from app.api.endpoints import auth, oauth, scope, cost, floor_plan, trade_package, comparison, markup, excel_export, pdf_export, subscription, team, share, demo
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

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(oauth.router, prefix="/api/v1/oauth", tags=["oauth"])
app.include_router(scope.router, prefix="/api/v1/scope", tags=["scope"])
app.include_router(cost.router, prefix="/api/v1/cost", tags=["cost"])
app.include_router(floor_plan.router, prefix="/api/v1/floor-plan", tags=["floor-plan"])
app.include_router(trade_package.router, prefix="/api/v1/trade-package", tags=["trade-package"])
app.include_router(comparison.router, prefix="/api/v1/comparison", tags=["comparison"])
app.include_router(markup.router, prefix="/api/v1/markup", tags=["markup"])
app.include_router(excel_export.router, prefix="/api/v1/excel", tags=["excel"])
app.include_router(pdf_export.router, prefix="/api/v1/pdf", tags=["pdf"])
app.include_router(subscription.router, prefix="/api/v1/subscription", tags=["subscription"])
app.include_router(team.router, prefix="/api/v1/team", tags=["team"])
app.include_router(share.router, prefix="/api/v1", tags=["share"])
app.include_router(demo.router, prefix="/api/v1/demo", tags=["demo"])


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs"
    }