
from sqlalchemy.orm import Session
from backend.app.db.session import engine, SessionLocal
from backend.app.db.base import Base # Import base to access metadata
from backend.app.models.user import User
from backend.app.models.product import Product
from backend.app.core.security import get_password_hash

def init_db(db: Session):
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Check if pantry user exists
    pantry_user = db.query(User).filter(User.username == "pantry_admin").first()
    if not pantry_user:
        pantry_user = User(
            username="pantry_admin",
            password_hash=get_password_hash("admin123"),
            role="pantry"
        )
        db.add(pantry_user)

    # Check if employee users exist
    employees = ["alice", "bob", "charlie"]
    for emp in employees:
        user = db.query(User).filter(User.username == emp).first()
        if not user:
            user = User(
                username=emp,
                password_hash=get_password_hash("password"),
                role="employee"
            )
            db.add(user)

    # Check if products exist
    products = [
        {"name": "Water bottle", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&h=400&fit=crop"},
        {"name": "Glass of water", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400&h=400&fit=crop"},
        {"name": "Tea", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?w=400&h=400&fit=crop"},
        {"name": "Coffee", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&h=400&fit=crop"},
        {"name": "Black tea", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=400&h=400&fit=crop"},
        {"name": "Coffee without Sugar", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400&h=400&fit=crop"},
        {"name": "Cold drink", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1581006852262-e4307cf6283a?w=400&h=400&fit=crop"},
        {"name": "Small plate", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1610701596061-2ecf227e85b2?w=400&h=400&fit=crop"},
        {"name": "Big plate", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1686580091125-a64b744bba4c?w=400&h=400&fit=crop"},
        {"name": "Small bowl", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=400&h=400&fit=crop"},
        {"name": "Spoon", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1619367300933-376d8c5cd5f9?w=400&h=400&fit=crop"},
        {"name": "Fork", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1569702824812-351205c9cde5?w=400&h=400&fit=crop"},
        {"name": "Salt", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1634612831148-03a8550e1d52?w=400&h=400&fit=crop"},
        {"name": "Sugar", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1610219171189-286769cc9b20?w=400&h=400&fit=crop"},
        {"name": "Lunch", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=400&fit=crop"},
        {"name": "Vada pav", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1750767396969-f37060ebe07d?w=400&h=400&fit=crop"},
        {"name": "Samosa", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&h=400&fit=crop"},
        {"name": "Breakfast", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=400&h=400&fit=crop"},
        {"name": "Other", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=400&h=400&fit=crop"},
    ]
    
    for prod_data in products:
        product = db.query(Product).filter(Product.name == prod_data["name"]).first()
        if not product:
            product = Product(**prod_data)
            db.add(product)

    db.commit()

if __name__ == "__main__":
    db = SessionLocal()
    init_db(db)
    print("Database initialized!")