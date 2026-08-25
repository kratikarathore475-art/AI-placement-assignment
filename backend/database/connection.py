import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # project root (AI-Placement-Assistant/)
os.makedirs(BASE_DIR / "data", exist_ok=True)

# Force the SQLite path to always resolve relative to project root,
# no matter which folder you run the script from.
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///./"):
    db_path = BASE_DIR / db_url.replace("sqlite:///./", "")
    db_url = f"sqlite:///{db_path}"

connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}

engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from models import user, question, interview
    Base.metadata.create_all(bind=engine)