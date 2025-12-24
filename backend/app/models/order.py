
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.app.db.session import Base
import json

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, index=True) # Storing username or ID
    items = Column(String) # JSON string of items
    status = Column(String, default="Pending") # Pending, Completed
    notes = Column(String, nullable=True) # User notes (e.g., "No sugar")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
