
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
        {"name": "Water Bottle", "price": 0.0, "image_url": "https://placehold.co/200x200/e0f2fe/0ea5e9?text=Water"},
        {"name": "Sandwich", "price": 0.0, "image_url": "https://placehold.co/200x200/fef3c7/d97706?text=Sandwich"},
        {"name": "Chips", "price": 0.0, "image_url": "https://placehold.co/200x200/fee2e2/dc2626?text=Chips"},
        {"name": "Cola", "price": 0.0, "image_url": "https://placehold.co/200x200/3c3c3c/ffffff?text=Cola"},
        {"name": "Tea", "price": 0.0, "image_url": "https://placehold.co/200x200/3c3c3c/ffffff?text=Tea"},
        {"name": "Coffee", "price": 0.0, "image_url": "https://placehold.co/200x200/3c3c3c/ffffff?text=Coffee"},
        {"name": "Milk", "price": 0.0, "image_url": "https://placehold.co/200x200/3c3c3c/ffffff?text=Milk"}
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