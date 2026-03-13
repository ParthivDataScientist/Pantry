"""ORM model for the ``users`` table."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "pantry" | "employee"

    # SQLAlchemy resolves relationship targets by class name within the same Base
    push_subscriptions = relationship(
        "PushSubscription",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
