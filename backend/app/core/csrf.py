"""
CSRF Protection for httpOnly cookie authentication
"""
import secrets
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse


def generate_csrf_token() -> str:
    """Generate a new CSRF token"""
    return secrets.token_urlsafe(32)


async def verify_csrf_token(request: Request) -> None:
    """Verify CSRF token for state-changing operations"""
    # Skip CSRF for GET, HEAD, OPTIONS requests
    if request.method in ["GET", "HEAD", "OPTIONS"]:
        return
    
    # Skip CSRF for auth endpoints (they don't have cookies yet)
    if request.url.path in ["/api/v1/auth/token", "/api/v1/auth/register", "/api/v1/demo/quick-signup"]:
        return
    
    # Get CSRF token from header
    csrf_header = request.headers.get("X-CSRF-Token")
    if not csrf_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing"
        )
    
    # Get CSRF token from cookie
    csrf_cookie = request.cookies.get("csrf_token")
    if not csrf_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF cookie missing"
        )
    
    # Verify tokens match
    if csrf_header != csrf_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch"
        )