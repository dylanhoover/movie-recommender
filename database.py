from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Define your database URL
DATABASE_URL = "postgresql://username:password@localhost:5432/yourdatabase"

# Create a new SQLAlchemy engine instance
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for your models
Base = declarative_base()

# Dependency to get the database session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
