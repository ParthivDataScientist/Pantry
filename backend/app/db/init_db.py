
from sqlalchemy.orm import Session
from backend.app.db.session import engine, SessionLocal
from backend.app.db.base import Base # Import base to access metadata
from backend.app.models.user import User
from backend.app.models.product import Product
from backend.app.models.push_subscription import PushSubscription
from backend.app.core.security import get_password_hash

def init_db(db: Session):
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Auto-migration: Check if name_hindi exists, if not add it
    # This is for production where we can't easily run manual migration scripts
    from sqlalchemy import text
    try:
        db.execute(text("SELECT name_hindi FROM products LIMIT 1"))
    except Exception:
        db.rollback()
        try:
            # Postgres syntax (works for SQLite too usually, but safe to try)
            # SQLite doesn't support IF NOT EXISTS in ADD COLUMN in all versions, 
            # but we are in the exception block so we know it doesn't exist.
            print("Migrating database: Adding name_hindi column...")
            db.execute(text("ALTER TABLE products ADD COLUMN name_hindi VARCHAR"))
            db.commit()
            print("Migration successful.")
        except Exception as e:
            print(f"Migration failed: {e}")
            db.rollback()

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
        {"name": "Water bottle", "name_hindi": "पानी की बोतल", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&h=400&fit=crop"},
        {"name": "Glass of water", "name_hindi": "पानी का गिलास", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400&h=400&fit=crop"},
        {"name": "Tea", "name_hindi": "चाय", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?w=400&h=400&fit=crop"},
        {"name": "Black tea", "name_hindi": "काली चाय", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=400&h=400&fit=crop"},
        {"name": "Coffee", "name_hindi": "कॉफ़ी", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&h=400&fit=crop"},
        {"name": "Coffee without Sugar", "name_hindi": "बिना चीनी की कॉफ़ी", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400&h=400&fit=crop"},
        {"name": "Cold drink", "name_hindi": "कोल्ड ड्रिंक", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1581006852262-e4307cf6283a?w=400&h=400&fit=crop"},
        {"name": "Small plate", "name_hindi": "छोटी प्लेट", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1610701596061-2ecf227e85b2?w=400&h=400&fit=crop"},
        {"name": "Big plate", "name_hindi": "बड़ी प्लेट", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1686580091125-a64b744bba4c?w=400&h=400&fit=crop"},
        {"name": "Small bowl", "name_hindi": "छोटी कटोरी", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=400&h=400&fit=crop"},
        {"name": "Spoon", "name_hindi": "चम्मच", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1619367300933-376d8c5cd5f9?w=400&h=400&fit=crop"},
        {"name": "Fork", "name_hindi": "कांटा", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1569702824812-351205c9cde5?w=400&h=400&fit=crop"},
        {"name": "Salt", "name_hindi": "नमक", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1634612831148-03a8550e1d52?w=400&h=400&fit=crop"},
        {"name": "Sugar", "name_hindi": "चीनी", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1610219171189-286769cc9b20?w=400&h=400&fit=crop"},
        {"name": "Lunch", "name_hindi": "दोपहर का भोजन", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=400&fit=crop"},
        {"name": "Vada pav", "name_hindi": "वड़ा पाव", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1750767396969-f37060ebe07d?w=400&h=400&fit=crop"},
        {"name": "Samosa", "name_hindi": "समोसा", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&h=400&fit=crop"},
        {"name": "Breakfast", "name_hindi": "नाश्ता", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=400&h=400&fit=crop"},
        {"name": "Other", "name_hindi": "अन्य", "price": 0.0, "image_url": "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=400&h=400&fit=crop"},
    ]
    
    for prod_data in products:
        product = db.query(Product).filter(Product.name == prod_data["name"]).first()
        if not product:
            product = Product(**prod_data)
            db.add(product)
        else:
            # Update existing if needed
            product.name_hindi = prod_data.get("name_hindi")
            product.image_url = prod_data.get("image_url")

    db.commit()

if __name__ == "__main__":
    db = SessionLocal()
    init_db(db)
    print("Database initialized!")