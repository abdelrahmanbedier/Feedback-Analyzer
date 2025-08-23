from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# The database URL tells SQLAlchemy where our database is located.
DATABASE_URL = "postgresql://user:password@db:5432/feedback_db"

# The engine is the main entry point for SQLAlchemy to communicate with the database.
engine = create_engine(DATABASE_URL)

# Each instance of SessionLocal will be a new database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# We will inherit from this Base class to create our database models.
Base = declarative_base()

# Dependency to get a DB session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()