from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    onboarding_complete = Column(Boolean, default=False)
    current_year = Column(String(20), nullable=True)
    interest_field = Column(String(60), nullable=True)
    target_role = Column(String(120), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")
    progress_entries = relationship("ProgressEntry", back_populates="user", cascade="all, delete-orphan")