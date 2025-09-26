from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from .base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(200))
    profile_picture_url = Column(String(500))
    
    # Auth provider (only Google)
    google_id = Column(String(255), unique=True, nullable=True)
    
    # Simple preferences
    target_band_score = Column(String(10), nullable=True)  # "7.0", "6.5", etc
    
    # Account status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def __str__(self):
        return self.full_name or self.email
    
    @property
    def display_name(self):
        return self.full_name or self.email.split('@')[0]