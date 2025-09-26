from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from app.models.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:WjZLYQUSYFbVsmOUUGzjDqLzvTjTZRhU@shortline.proxy.rlwy.net:51529/railway")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database"""
    try:
        # Import all models to ensure they're registered with SQLAlchemy
        from app.models import user, speaking, reading, writing, listening
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("📊 All database tables created/verified successfully")
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise e