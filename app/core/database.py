from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text

# Updated database URL
#SQLALCHEMY_DATABASE_URL = "postgresql://postgres.cjoxvljedeotlsxxheas:Chitta123456789123@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
#DATABASE_URL="postgresql://postgres.qgbhhpukkwwgmkhlbcdy:rQ#7kesqL9eXMiD@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
DATABASE_URL = "postgresql://postgres:postgrespassword@localhost:5430/recruitment_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Check database connection
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))  # Simple query to test connection
        print("Database connected successfully!")
except OperationalError as e:
    print(f"Database connection failed: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()