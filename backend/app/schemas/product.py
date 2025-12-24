
from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    price: float
    image_url: str

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True
