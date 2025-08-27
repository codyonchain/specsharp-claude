from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext

from app.core.config import settings
from app.models.auth import User
from app.db.database import get_db
from app.db.models import User as DBUser
import os

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Check if we're in local development mode
IS_LOCAL_DEV = os.getenv("ENVIRONMENT", "development") in ["development", "local", "dev"]
if IS_LOCAL_DEV:
    print("🔓 AUTH BYPASS ENABLED: Running in LOCAL DEV mode - Authentication will be bypassed")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # LOCAL DEV BYPASS
    if IS_LOCAL_DEV:
        # Return or create a dev user for local testing
        dev_user = db.query(DBUser).filter(DBUser.email == "dev@localhost").first()
        if not dev_user:
            # Create a dev user if it doesn't exist
            dev_user = DBUser(
                email="dev@localhost",
                hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
                full_name="Dev User",
                is_active=True
            )
            db.add(dev_user)
            db.commit()
            db.refresh(dev_user)
        return dev_user
    
    # PRODUCTION AUTH FLOW
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # If no token from bearer auth
    if not token:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_with_cookie(request: Request, db: Session = Depends(get_db)):
    """Get current user with support for both Bearer token and httpOnly cookies"""
    
    # LOCAL DEV BYPASS
    if IS_LOCAL_DEV:
        # Return or create a dev user for local testing
        dev_user = db.query(DBUser).filter(DBUser.email == "dev@localhost").first()
        if not dev_user:
            # Create a dev user if it doesn't exist
            dev_user = DBUser(
                email="dev@localhost",
                hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
                full_name="Dev User",
                is_active=True
            )
            db.add(dev_user)
            db.commit()
            db.refresh(dev_user)
        return dev_user
    
    # PRODUCTION AUTH FLOW
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try Bearer token first
    auth_header = request.headers.get("Authorization")
    token = None
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    # Try cookie if no Bearer token
    if not token:
        token = request.cookies.get("access_token")
    
    # If no token from either source
    if not token:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint for username/password authentication"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response):
    """Clear the authentication cookies"""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="csrf_token")
    return {"message": "Successfully logged out"}