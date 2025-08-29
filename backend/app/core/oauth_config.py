import os
import logging
from typing import Optional
from app.core.environment import EnvironmentChecker

logger = logging.getLogger(__name__)

class OAuthConfig:
    """Manages OAuth configuration for different environments"""
    
    @staticmethod
    def is_oauth_enabled() -> bool:
        """Check if OAuth should be enabled"""
        # OAuth disabled if testing mode is on
        if EnvironmentChecker.is_testing_mode():
            logger.info("OAuth disabled - Testing mode active")
            return False
        
        # OAuth required in production
        if EnvironmentChecker.get_environment() == "production":
            logger.info("OAuth enabled - Production environment")
            return True
            
        # In development, OAuth is optional
        enabled = os.getenv("ENABLE_OAUTH", "false").lower() == "true"
        logger.info(f"OAuth {'enabled' if enabled else 'disabled'} - Development environment (ENABLE_OAUTH={os.getenv('ENABLE_OAUTH', 'false')})")
        return enabled
    
    @staticmethod
    def get_google_config() -> Optional[dict]:
        """Get Google OAuth configuration"""
        if not OAuthConfig.is_oauth_enabled():
            return None
            
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            logger.warning("OAuth enabled but Google credentials missing!")
            return None
            
        # Determine redirect URI based on environment
        if EnvironmentChecker.get_environment() == "development":
            redirect_uri = "http://localhost:8001/api/v1/oauth/callback/google"
        else:
            base_url = os.getenv("API_URL", "https://api.specsharp.ai")
            redirect_uri = f"{base_url}/api/v1/oauth/callback/google"
            
        return {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "scope": ["openid", "email", "profile"]
        }
    
    @staticmethod
    def log_oauth_status():
        """Log OAuth configuration status"""
        is_enabled = OAuthConfig.is_oauth_enabled()
        config = OAuthConfig.get_google_config()
        
        logger.info("=" * 50)
        logger.info("OAuth Configuration Status")
        logger.info("=" * 50)
        logger.info(f"OAuth Enabled: {is_enabled}")
        logger.info(f"Environment: {EnvironmentChecker.get_environment()}")
        logger.info(f"Testing Mode: {EnvironmentChecker.is_testing_mode()}")
        
        if is_enabled and config:
            logger.info(f"OAuth Provider: Google")
            logger.info(f"OAuth Redirect URI: {config['redirect_uri']}")
            logger.info("✅ OAuth configured correctly")
        elif is_enabled and not config:
            logger.error("❌ OAuth enabled but credentials missing!")
            logger.error("Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
        elif EnvironmentChecker.is_testing_mode():
            logger.info("ℹ️  Using auth bypass (testing mode)")
        else:
            logger.info("ℹ️  OAuth disabled")
        
        logger.info("=" * 50)