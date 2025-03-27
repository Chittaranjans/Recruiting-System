from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.api import jobs, candidates, interviews, notifications, kanban, auth
from app.core.database import Base
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
from fastapi.middleware.cors import CORSMiddleware

# Initialize database
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])
app.include_router(candidates.router, prefix="/api/v1", tags=["candidates"])
app.include_router(interviews.router, prefix="/api/v1", tags=["interviews"])
app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])
app.include_router(kanban.router, prefix="/api/v1", tags=["kanban"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.on_event("startup")
def check_database_connection():
    print("Starting server...")
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Database connected successfully!")
    except OperationalError as e:
        print(f"Database connection failed: {e}")

@app.get("/health", tags=["health"])
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "Database connected"}
    except OperationalError:
        return {"status": "Database not connected"}
    
@app.get("/")
def read_root():
    return {"message": "Welcome to the Recruitment Tracking API"}
