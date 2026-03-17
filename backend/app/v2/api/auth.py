from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.auth import (
    AuthContext,
    build_testing_auth_context,
    get_auth_context,
    is_testing_auth_enabled,
)
from app.core.rate_limiter import limiter
from app.core.run_limits import get_effective_run_limit_snapshot
from app.db.database import get_db


router = APIRouter(prefix="/auth", tags=["v2-auth"])
TESTING_SESSION_TTL_SECONDS = 3600


@router.post("/testing/session")
@limiter.limit("60/minute")
async def create_testing_session(request: Request):
    if not is_testing_auth_enabled():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    auth = build_testing_auth_context()
    expires_at = int((datetime.utcnow() + timedelta(seconds=TESTING_SESSION_TTL_SECONDS)).timestamp())
    return {
        "success": True,
        "data": {
            "access_token": auth.access_token,
            "expires_at": expires_at,
            "expires_in": TESTING_SESSION_TTL_SECONDS,
            "user": {
                "id": auth.user_id,
                "email": auth.email,
            },
            "org_id": auth.org_id,
            "role": auth.role,
        },
    }


@router.get("/me")
@limiter.limit("120/minute")
async def get_auth_me(
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    run_limits = get_effective_run_limit_snapshot(db, org_id=auth.org_id, email=auth.email)
    return {
        "success": True,
        "data": {
            "user_id": auth.user_id,
            "email": auth.email,
            "org_id": auth.org_id,
            "role": auth.role,
            "run_limits": run_limits.to_dict(),
        },
    }
