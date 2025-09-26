from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, speaking, reading, writing, listening, users
from app.routes.admin import speaking as admin_speaking
from app.routes.admin import reading as admin_reading  
from app.routes.admin import writing as admin_writing
from app.routes.admin import listening as admin_listening
from app.routes.admin import dashboard as admin_dashboard
from app.database import create_tables

app = FastAPI(
    title="IELTS Practice API",
    description="Backend API for IELTS practice tests",
    version="1.0.0"
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    print("✅ Database tables created successfully!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication
app.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Admin routes - separated by skill
app.include_router(admin_speaking.router, prefix="/admin/speaking", tags=["admin-speaking"])
app.include_router(admin_reading.router, prefix="/admin/reading", tags=["admin-reading"])
app.include_router(admin_writing.router, prefix="/admin/writing", tags=["admin-writing"])
app.include_router(admin_listening.router, prefix="/admin/listening", tags=["admin-listening"])
app.include_router(admin_dashboard.router, prefix="/admin/dashboard", tags=["admin-dashboard"])

# User routes
app.include_router(users.router, prefix="/users", tags=["users"])

# Test routes
app.include_router(speaking.router, prefix="/speaking", tags=["speaking"])
app.include_router(reading.router, prefix="/reading", tags=["reading"])
app.include_router(writing.router, prefix="/writing", tags=["writing"])
app.include_router(listening.router, prefix="/listening", tags=["listening"])

@app.get("/")
async def root():
    return {"message": "IELTS Practice API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}