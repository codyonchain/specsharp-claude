from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, get_auth_context
from app.core.rate_limiter import limiter
from app.core.run_limits import get_run_limit_snapshot
from app.db.database import get_db


router = APIRouter(prefix="/auth", tags=["v2-auth"])


@router.get("/me")
@limiter.limit("120/minute")
async def get_auth_me(
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    run_limits = get_run_limit_snapshot(db, org_id=auth.org_id, email=auth.email)
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
