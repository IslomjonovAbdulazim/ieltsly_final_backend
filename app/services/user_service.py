from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.user import User


class UserService:
    
    @staticmethod
    def create_google_user(db: Session, email: str, google_id: str, full_name: str = None, picture: str = None) -> User:
        """Create user from Google login"""
        user = User(
            email=email,
            full_name=full_name,
            profile_picture_url=picture,
            google_id=google_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def create_apple_user(db: Session, email: str, apple_id: str, full_name: str = None) -> User:
        """Create user from Apple login"""
        user = User(
            email=email,
            full_name=full_name,
            apple_id=apple_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
        return db.query(User).filter(User.google_id == google_id).first()
    
    @staticmethod
    def get_user_by_apple_id(db: Session, apple_id: str) -> Optional[User]:
        return db.query(User).filter(User.apple_id == apple_id).first()
    
    @staticmethod
    def update_last_login(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def update_profile(db: Session, user_id: int, full_name: str = None, target_score: str = None) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            if full_name:
                user.full_name = full_name
            if target_score:
                user.target_band_score = target_score
            db.commit()
            db.refresh(user)
        return user


class AuthService:
    
    @staticmethod
    def login_with_google(db: Session, email: str, google_id: str, full_name: str = None, picture: str = None) -> User:
        # Try to find existing user
        user = UserService.get_user_by_google_id(db, google_id)
        if not user:
            user = UserService.get_user_by_email(db, email)
            if user:
                # Link Google to existing account
                user.google_id = google_id
                if picture and not user.profile_picture_url:
                    user.profile_picture_url = picture
                db.commit()
            else:
                # Create new user
                user = UserService.create_google_user(db, email, google_id, full_name, picture)
        
        UserService.update_last_login(db, user.id)
        return user
    
    @staticmethod
    def login_with_apple(db: Session, email: str, apple_id: str, full_name: str = None) -> User:
        # Try to find existing user
        user = UserService.get_user_by_apple_id(db, apple_id)
        if not user:
            user = UserService.get_user_by_email(db, email)
            if user:
                # Link Apple to existing account
                user.apple_id = apple_id
                db.commit()
            else:
                # Create new user
                user = UserService.create_apple_user(db, email, apple_id, full_name)
        
        UserService.update_last_login(db, user.id)
        return user