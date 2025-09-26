from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, speaking, reading, writing, listening, users

app = FastAPI(
    title="IELTS Practice API",
    description="Backend API for IELTS practice tests",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(users.router, prefix="/users", tags=["users"])
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