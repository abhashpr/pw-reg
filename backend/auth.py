"""Authentication and JWT token management."""

from datetime import datetime, timedelta
from typing import Optional
import jwt
from sqlalchemy.orm import Session
from models import User
from config import get_settings
import logging

logger = logging.getLogger("auth")


class AuthService:
    """Service for JWT token management."""
    
    @staticmethod
    def create_access_token(email: str, user_id: int) -> str:
        """
        Create JWT access token.
        
        Args:
            email: User email
            user_id: User ID
            
        Returns:
            JWT token string
        """
        settings = get_settings()
        
        to_encode = {
            "sub": email,
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes),
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        Verify JWT token and extract claims.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Token claims dict if valid, None otherwise
        """
        settings = get_settings()
        
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            return payload
        except (jwt.InvalidTokenError, jwt.DecodeError, jwt.ExpiredSignatureError) as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> Optional[User]:
        """
        Get current authenticated user from token.
        
        Args:
            db: Database session
            token: JWT token
            
        Returns:
            User object if token is valid, None otherwise
        """
        payload = AuthService.verify_token(token)
        
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user


def create_or_get_user(db: Session, email: str) -> User:
    """
    Create new user or return existing user.
    
    Args:
        db: Database session
        email: User email
        
    Returns:
        User object
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        user = User(email=email, is_verified=False)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"User created: {email}")
    
    return user

    
    @staticmethod
    def get_current_user(db: Session, token: str) -> Optional[User]:
        """
        Get current authenticated user from token.
        
        Args:
            db: Database session
            token: JWT token
            
        Returns:
            User object if token is valid, None otherwise
        """
        payload = AuthService.verify_token(token)
        
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user


def create_or_get_user(db: Session, email: str) -> User:
    """
    Create new user or return existing user.
    
    Args:
        db: Database session
        email: User email
        
    Returns:
        User object
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        user = User(email=email, is_verified=False)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"User created: {email}")
    
    return user
