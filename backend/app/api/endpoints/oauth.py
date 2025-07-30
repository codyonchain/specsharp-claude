from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth, OAuthError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from jose import jwt
from datetime import datetime, timedelta
import secrets
import httpx

from app.core.config import settings
from app.models.auth import User
from app.db.database import get_db
from app.db.models import User as DBUser
from app.api.endpoints.auth import create_access_token, get_current_user_with_cookie

router = APIRouter()

# Initialize OAuth
oauth = OAuth()

# Configure Google OAuth
try:
    oauth.register(
        name='google',
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    logger.info(f"Google OAuth configured with client_id: {settings.google_client_id[:10]}...")
except Exception as e:
    logger.error(f"Failed to configure Google OAuth: {str(e)}")



def get_or_create_oauth_user(db: Session, email: str, full_name: str, oauth_id: str, profile_picture: str = None) -> DBUser:
    """Get existing OAuth user or create new one"""
    # First check if user exists with this OAuth ID
    user = db.query(DBUser).filter(
        DBUser.oauth_provider == 'google',
        DBUser.oauth_id == oauth_id
    ).first()
    
    if user:
        # Update user info in case it changed
        user.email = email
        user.full_name = full_name
        if profile_picture:
            user.profile_picture = profile_picture
        db.commit()
        return user
    
    # Check if user exists with this email (migrating from password auth)
    user = db.query(DBUser).filter(DBUser.email == email).first()
    
    if user:
        # Migrate existing user to OAuth
        user.oauth_provider = 'google'
        user.oauth_id = oauth_id
        if profile_picture:
            user.profile_picture = profile_picture
        db.commit()
        return user
    
    # Create new user with a random unusable password for OAuth users
    import uuid
    dummy_password = f"oauth_user_{uuid.uuid4().hex}"
    
    user = DBUser(
        email=email,
        full_name=full_name,
        oauth_provider='google',
        oauth_id=oauth_id,
        profile_picture=profile_picture,
        is_active=True,
        hashed_password=dummy_password  # OAuth users don't use passwords
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/login/google")
async def oauth_login(request: Request):
    """Initiate Google OAuth login flow"""
    try:
        logger.info("Starting Google OAuth login flow")
        client = oauth.create_client('google')
        
        # Use different redirect URI based on environment
        if settings.environment == "development":
            # Check if request is from 127.0.0.1 or localhost
            host = request.headers.get("host", "localhost:8001")
            if "127.0.0.1" in host:
                redirect_uri = "http://127.0.0.1:8001/api/v1/oauth/callback/google"
            else:
                redirect_uri = "http://localhost:8001/api/v1/oauth/callback/google"
        else:
            redirect_uri = "https://api.specsharp.ai/api/v1/oauth/callback/google"
        
        logger.info(f"OAuth redirect URI: {redirect_uri}")
        
        # Let authlib handle state generation internally
        return await client.authorize_redirect(request, redirect_uri)
    except Exception as e:
        logger.error(f"OAuth login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OAuth initialization failed: {str(e)}")


@router.get("/callback/google")
async def oauth_callback(request: Request, response: Response, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    
    # Log the callback for debugging
    state = request.query_params.get('state')
    logger.info(f"OAuth callback - received state: {state[:10] if state else 'None'}...")
    logger.info(f"OAuth callback - session data: {dict(request.session)}")
    
    try:
        client = oauth.create_client('google')
        # Authlib automatically uses the redirect_uri from the session
        token = await client.authorize_access_token(request)
        
        # Get user info from Google
        logger.info(f"Token data keys: {list(token.keys())}")
        user_info = token.get('userinfo')
        
        if not user_info:
            # Fetch user info if not in token
            logger.info("Userinfo not in token, fetching from Google API")
            async with httpx.AsyncClient() as http_client:
                resp = await http_client.get(
                    'https://www.googleapis.com/oauth2/v1/userinfo',
                    headers={'Authorization': f'Bearer {token["access_token"]}'}
                )
                user_info = resp.json()
                logger.info(f"Fetched user info: {user_info}")
        else:
            logger.info(f"User info from token: {user_info}")
        
        email = user_info.get('email')
        full_name = user_info.get('name', email)
        oauth_id = user_info.get('sub')  # Google uses 'sub' for user ID
        profile_picture = user_info.get('picture')
        
        logger.info(f"Extracted - email: {email}, name: {full_name}, id: {oauth_id}")
        
        if not email or not oauth_id:
            logger.error(f"Missing required user info - email: {email}, oauth_id: {oauth_id}")
            raise HTTPException(status_code=400, detail="Failed to get user information from OAuth provider")
        
        # Get or create user
        user = get_or_create_oauth_user(
            db=db,
            email=email,
            full_name=full_name,
            oauth_id=oauth_id,
            profile_picture=profile_picture
        )
        
        # Create JWT token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # For development, pass token in URL since cookies don't work cross-origin
        # In production with same domain, use httpOnly cookies
        redirect_url = f"{settings.frontend_url}/dashboard?token={access_token}"
        response = RedirectResponse(url=redirect_url)
        
        # Also set cookie for backend API calls
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Set to False for localhost development
            samesite="lax",
            max_age=access_token_expires.total_seconds()
        )
        
        # Set CSRF token
        from app.core.csrf import generate_csrf_token
        csrf_token = generate_csrf_token()
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=False,
            secure=True,
            samesite="lax",
            max_age=access_token_expires.total_seconds()
        )
        
        return response
        
    except OAuthError as e:
        logger.error(f"OAuth error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.get("/user/info")
async def get_user_info(current_user: DBUser = Depends(get_current_user_with_cookie), db: Session = Depends(get_db)):
    """Get current user information including OAuth details"""
    # current_user is already a User object from the dependency
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "profile_picture": user.profile_picture,
        "oauth_provider": user.oauth_provider,
        "is_active": user.is_active,
        "created_at": user.created_at
    }


@router.post("/logout")
async def oauth_logout(request: Request, response: Response):
    """Clear OAuth session and cookies"""
    # Clear all session data
    request.session.clear()
    
    # Clear the access token cookie
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="csrf_token")
    
    return {"message": "Logged out successfully"}


@router.get("/clear-session")
async def clear_oauth_session(request: Request, response: Response):
    """Clear all OAuth session data - use this to fix stuck sessions"""
    # Clear ALL session data
    request.session.clear()
    
    # Also clear any cookies
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="csrf_token")
    response.delete_cookie(key="session")
    
    # Return a redirect to login
    return RedirectResponse(url=settings.frontend_url + "/login?session_cleared=true")