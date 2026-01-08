#!/usr/bin/env python3
"""Create a test user for scenario testing"""

from sqlalchemy.orm import Session
from passlib.context import CryptContext
import sys
sys.path.append('backend')

from app.db.database import SessionLocal
from app.db.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user():
    db = SessionLocal()
    
    # Check if user exists
    existing_user = db.query(User).filter(User.email == "test2@example.com").first()
    
    if existing_user:
        # Update password
        existing_user.hashed_password = pwd_context.hash("password123")
        db.commit()
        print("✓ Updated password for test2@example.com")
    else:
        # Create new user
        new_user = User(
            email="test2@example.com",
            username="test2",
            hashed_password=pwd_context.hash("password123"),
            is_active=True,
            is_verified=True
        )
        db.add(new_user)
        db.commit()
        print("✓ Created new user test2@example.com")
    
    db.close()
    print("User ready for testing with password: password123")

if __name__ == "__main__":
    create_test_user()