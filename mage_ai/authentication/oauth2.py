import secrets
from datetime import datetime, timedelta
from typing import Dict

import jwt

from mage_ai.orchestration.db.models.oauth import (
    Oauth2AccessToken,
    Oauth2Application,
    User,
)
from mage_ai.orchestration.db.models.jwt_blacklist import JWTBlacklist
from mage_ai.settings import JWT_SECRET, MAGE_ACCESS_TOKEN_EXPIRY_TIME

JWT_ALGORITHM = 'HS256'


def generate_access_token(
    user: User,
    application: Oauth2Application = None,
    refresh_token: str = None,
    token: str = None,
    duration: int = None,
) -> Oauth2AccessToken:
    if duration is None:
        duration = MAGE_ACCESS_TOKEN_EXPIRY_TIME

    if not token:
        token = secrets.token_urlsafe()

        token_count = Oauth2AccessToken.query.filter(Oauth2AccessToken.token == token).count()
        while token_count >= 1:
            token = secrets.token_urlsafe()
            token_count = Oauth2AccessToken.query.filter(Oauth2AccessToken.token == token).count()

    attributes_data = dict(
        expires=datetime.utcnow() + timedelta(seconds=duration),
        token=token,
        user_id=user.id if user else None,
    )

    if refresh_token:
        attributes_data['refresh_token'] = refresh_token

    if application:
        attributes_data['oauth2_application_id'] = application.id

    return Oauth2AccessToken.create(**attributes_data)


def get_access_token(token: str) -> Oauth2AccessToken:
    return Oauth2AccessToken.query.filter(Oauth2AccessToken.token == token).first()


def encode_token(token: str, expires: datetime) -> str:
    return jwt.encode({
        'expires': expires.timestamp(),
        'token': token,
    }, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(encoded_token: str) -> Dict:
    return jwt.decode(encoded_token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM], verify=True)


def is_token_valid(encoded_token: str) -> bool:
    """
    Check if a JWT token is valid and not blacklisted.
    
    Args:
        encoded_token: The JWT token to validate
        
    Returns:
        bool: True if token is valid and not blacklisted, False otherwise
    """
    try:
        # First decode and validate token structure
        decoded = decode_token(encoded_token)
        
        # Check if token has expired
        expires_timestamp = decoded.get('expires')
        if not expires_timestamp:
            return False
            
        expires_datetime = datetime.fromtimestamp(expires_timestamp)
        if expires_datetime <= datetime.utcnow():
            return False
        
        # Then check if token is blacklisted (gracefully handle missing table)
        try:
            if JWTBlacklist.is_token_blacklisted(encoded_token):
                return False
        except Exception:
            # If blacklist table doesn't exist or there's a DB error,
            # continue without blacklist check (for backwards compatibility)
            pass
            
        return True
        
    except jwt.InvalidTokenError:
        return False
    except Exception:
        return False


def blacklist_token(encoded_token: str, reason: str = 'logout') -> bool:
    """
    Add a JWT token to the blacklist.
    
    Args:
        encoded_token: The JWT token to blacklist
        reason: Reason for blacklisting (default: 'logout')
        
    Returns:
        bool: True if token was successfully blacklisted, False otherwise
    """
    try:
        # Decode token to get expiration
        decoded = decode_token(encoded_token)
        expires_timestamp = decoded.get('expires')
        
        if not expires_timestamp:
            return False
            
        expires_datetime = datetime.fromtimestamp(expires_timestamp)
        
        # Add to blacklist (gracefully handle missing table)
        try:
            JWTBlacklist.blacklist_token(
                token=encoded_token,
                expires_at=expires_datetime,
                reason=reason
            )
            return True
        except Exception:
            # If blacklist table doesn't exist, gracefully fail
            # but still return True to not break logout flow
            return True
        
    except jwt.InvalidTokenError:
        return False
    except Exception:
        return False
