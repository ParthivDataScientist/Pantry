
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class OrderItem(BaseModel):
    product_id: int
    quantity: int
    name: str
    price: float

class OrderCreate(BaseModel):
    employee: str
    items: List[OrderItem]
    total: float
    notes: str = ""

class Order(BaseModel):
    id: int
    employee_id: str
    items: str # We will parse this back
    status: str
    notes: str = None
    timestamp: datetime

    class Config:
        from_attributes = True
