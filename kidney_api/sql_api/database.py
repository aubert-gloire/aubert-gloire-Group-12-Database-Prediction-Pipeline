from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings
import os
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        # Get the directory where this file (database.py) is located
        env_file = os.path.join(os.path.dirname(__file__), ".env")

settings = Settings()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()