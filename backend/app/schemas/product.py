
from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    name_hindi: str = None
    price: float
    image_url: str

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True
