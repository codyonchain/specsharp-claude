import os
import sys
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class EnvironmentChecker:
    """Validates and logs environment configuration at startup"""
    
    @staticmethod
    def get_environment() -> str:
        """Get current environment (development/production)"""
        return os.getenv("ENVIRONMENT", "production")
    
    @staticmethod
    def is_testing_mode() -> bool:
        """Check if testing/auth bypass is enabled"""
        return os.getenv("TESTING", "false").lower() == "true"
    
    @staticmethod
    def check_required_vars() -> Dict[str, bool]:
        """Check which required environment variables are set"""
        env = EnvironmentChecker.get_environment()
        
        # Different requirements for different environments
        if env == "development":
            required = ["DATABASE_URL"]
            optional = ["TESTING", "SKIP_AUTH"]
        else:
            required = [
                "DATABASE_URL",
                "GOOGLE_CLIENT_ID", 
                "GOOGLE_CLIENT_SECRET",
                "JWT_SECRET"
            ]
            optional = ["SENTRY_DSN", "REDIS_URL"]
        
        results = {}
        
        # Check required (don't log values!)
        for var in required:
            results[var] = os.getenv(var) is not None
            
        # Check optional
        for var in optional:
            results[f"{var}_optional"] = os.getenv(var) is not None
            
        return results
    
    @staticmethod
    def log_startup_config():
        """Log configuration at startup (safely)"""
        env = EnvironmentChecker.get_environment()
        is_testing = EnvironmentChecker.is_testing_mode()
        checks = EnvironmentChecker.check_required_vars()
        
        # Log safe information only
        logger.info("=" * 50)
        logger.info("SpecSharp Backend Starting")
        logger.info("=" * 50)
        logger.info(f"Environment: {env}")
        logger.info(f"Testing Mode: {is_testing}")
        
        if env == "development" and is_testing:
            logger.warning("⚠️  AUTH BYPASS ENABLED - DEV MODE ONLY")
        
        # Log which vars are set (not their values!)
        missing = [k for k, v in checks.items() if not v and 'optional' not in k]
        if missing:
            logger.error(f"❌ Missing required variables: {missing}")
            if env == "production":
                logger.error("Cannot start in production with missing variables!")
                sys.exit(1)
        else:
            logger.info("✅ All required environment variables set")
        
        # Database connection type
        db_url = os.getenv("DATABASE_URL", "")
        if "postgresql" in db_url:
            logger.info("Database: PostgreSQL")
        elif "sqlite" in db_url:
            logger.info("Database: SQLite")
        else:
            logger.warning("Database: Unknown or not configured")
        
        # API URL (safe to log)
        api_url = os.getenv("API_URL", "not set")
        if "localhost" in api_url:
            logger.info("API URL: localhost (development)")
        elif api_url != "not set":
            logger.info(f"API URL: {api_url.split('//')[1].split('/')[0] if '//' in api_url else 'configured'}")
        
        logger.info("=" * 50)
        
        # Final safety check
        if env == "production" and is_testing:
            logger.error("🚨 CRITICAL: Testing mode enabled in production!")
            logger.error("🚨 This is a security risk! Shutting down.")
            sys.exit(1)

# Run checker when module is imported
EnvironmentChecker.log_startup_config()