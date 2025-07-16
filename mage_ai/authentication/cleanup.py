import logging
from datetime import datetime, timedelta

from mage_ai.orchestration.db.models.jwt_blacklist import JWTBlacklist
from mage_ai.orchestration.db import safe_db_query

logger = logging.getLogger(__name__)


@safe_db_query
def cleanup_expired_jwt_tokens() -> int:
    """
    Clean up expired JWT tokens from the blacklist.
    
    This should be called periodically (e.g., daily) to prevent the blacklist
    table from growing indefinitely with expired tokens.
    
    Returns:
        int: Number of tokens removed from blacklist
    """
    try:
        count = JWTBlacklist.cleanup_expired_tokens()
        if count > 0:
            logger.info(f"Cleaned up {count} expired JWT tokens from blacklist")
        return count
    except Exception as e:
        logger.error(f"Error cleaning up expired JWT tokens: {e}")
        return 0


@safe_db_query
def cleanup_old_oauth_tokens() -> int:
    """
    Clean up OAuth2AccessToken records that are expired for more than 7 days.
    
    This helps keep the oauth2_access_token table from growing too large.
    
    Returns:
        int: Number of OAuth tokens removed
    """
    try:
        from mage_ai.orchestration.db.models.oauth import Oauth2AccessToken
        
        # Remove tokens expired for more than 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        expired_tokens = Oauth2AccessToken.query.filter(
            Oauth2AccessToken.expires < cutoff_date
        )
        
        count = expired_tokens.count()
        expired_tokens.delete()
        
        if count > 0:
            logger.info(f"Cleaned up {count} old OAuth tokens")
        return count
        
    except Exception as e:
        logger.error(f"Error cleaning up old OAuth tokens: {e}")
        return 0


def run_auth_cleanup() -> dict:
    """
    Run all authentication cleanup tasks.
    
    Returns:
        dict: Summary of cleanup results
    """
    results = {
        'jwt_tokens_cleaned': 0,
        'oauth_tokens_cleaned': 0,
        'errors': []
    }
    
    try:
        results['jwt_tokens_cleaned'] = cleanup_expired_jwt_tokens()
    except Exception as e:
        results['errors'].append(f"JWT cleanup error: {e}")
    
    try:
        results['oauth_tokens_cleaned'] = cleanup_old_oauth_tokens()
    except Exception as e:
        results['errors'].append(f"OAuth cleanup error: {e}")
    
    logger.info(f"Authentication cleanup completed: {results}")
    return results