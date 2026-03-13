"""Pydantic schemas for order-related API requests and responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class OrderItem(BaseModel):
    """A single item within an order."""

    product_id: int
    quantity: int
    name: str
    price: float = 0.0
    image_url: Optional[str] = None


class OrderCreate(BaseModel):
    """
    Payload for creating a new order.

    Note: ``employee`` is determined from the authenticated JWT token,
    not from this payload.
    """

    items: List[OrderItem]
    notes: Optional[str] = ""


class Order(BaseModel):
    """Full order representation returned by the API."""

    id: int
    employee_id: str
    items: str  # JSON-serialised list of OrderItem dicts
    status: str
    notes: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
