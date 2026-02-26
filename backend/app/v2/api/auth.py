from fastapi import APIRouter, Depends

from app.core.auth import AuthContext, get_auth_context


router = APIRouter(prefix="/auth", tags=["v2-auth"])


@router.get("/me")
async def get_auth_me(auth: AuthContext = Depends(get_auth_context)):
    return {
        "success": True,
        "data": {
            "user_id": auth.user_id,
            "email": auth.email,
            "org_id": auth.org_id,
            "role": auth.role,
        },
    }
