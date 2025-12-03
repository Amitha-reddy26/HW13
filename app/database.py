from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.config import settings

# ---------------------------------------------------------
# Create engine from DATABASE_URL in config.py
# ---------------------------------------------------------
def get_engine(database_url: str = settings.DATABASE_URL):
    try:
        engine = create_engine(database_url, echo=True)
        return engine
    except SQLAlchemyError as e:
        print(f"Error creating engine: {e}")
        raise


# ---------------------------------------------------------
# Create session factory
# ---------------------------------------------------------
def get_sessionmaker(engine):
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )


# Global engine + session
engine = get_engine()
SessionLocal = get_sessionmaker(engine)

# Declarative base for models
Base = declarative_base()


# ---------------------------------------------------------
# Dependency for routes
# ---------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
