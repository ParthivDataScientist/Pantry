
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
        {"name": "Water bottle", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Water+Bottle"},
        {"name": "Glass of water", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Glass+of+water"},
        {"name": "Tea", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Tea"},
        {"name": "Coffee", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Coffee"},
        {"name": "Black tea", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Black+tea"},
        {"name": "Coffee without Sugar", "price": 0.0, "image_url": "https://placehold.co/200x200?text=No+Sugar+Coffee"},
        {"name": "Cold drink", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Cold+drink"},
        {"name": "Small plate", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Small+plate"},
        {"name": "Big plate", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Big+plate"},
        {"name": "Small bowl", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Small+bowl"},
        {"name": "Spoon", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Spoon"},
        {"name": "Fork", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Fork"},
        {"name": "Salt", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Salt"},
        {"name": "Sugar", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Sugar"},
        {"name": "Lunch", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Lunch"},
        {"name": "Vada pav", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Vada+pav"},
        {"name": "Samosa", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Samosa"},
        {"name": "Breakfast", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Breakfast"},
        {"name": "Other", "price": 0.0, "image_url": "https://placehold.co/200x200?text=Other"},
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