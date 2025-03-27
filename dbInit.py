# filepath: d:\Dev\Recruitment-Tracking\Backend\initialize_db.py
from app.core.database import Base, engine
from app.models.base import JobPosting, Candidate

# Drop all tables
print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)
print("Tables dropped successfully!")

# Create all tables
print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
