"""
Database initialisation.

Creates all tables and, if the database is empty, seeds default users and
products so the application works immediately after a fresh deployment.
"""

import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.db.session import engine
import backend.app.db.base  # noqa: F401 — ensures all models are registered
from backend.app.models.user import User
from backend.app.models.product import Product
from backend.app.core.security import get_password_hash

logger = logging.getLogger(__name__)

# ── Seed data ─────────────────────────────────────────────────────────────────

_DEFAULT_USERS: list[dict] = [
    {"username": "pantry_admin", "password": "admin123", "role": "pantry"},
    {"username": "alice",        "password": "password",  "role": "employee"},
    {"username": "bob",          "password": "password",  "role": "employee"},
    {"username": "charlie",      "password": "password",  "role": "employee"},
]

_DEFAULT_PRODUCTS: list[dict] = [
    {"name": "Water bottle",        "name_hindi": "पानी की बोतल",     "price": 0.0, "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&h=400&fit=crop"},
    {"name": "Glass of water",      "name_hindi": "पानी का गिलास",    "price": 0.0, "image_url": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400&h=400&fit=crop"},
    {"name": "Tea",                 "name_hindi": "चाय",               "price": 0.0, "image_url": "https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?w=400&h=400&fit=crop"},
    {"name": "Black tea",           "name_hindi": "काली चाय",          "price": 0.0, "image_url": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=400&h=400&fit=crop"},
    {"name": "Coffee",              "name_hindi": "कॉफ़ी",             "price": 0.0, "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&h=400&fit=crop"},
    {"name": "Coffee without Sugar","name_hindi": "बिना चीनी की कॉफ़ी","price": 0.0, "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400&h=400&fit=crop"},
    {"name": "Cold drink",          "name_hindi": "कोल्ड ड्रिंक",     "price": 0.0, "image_url": "https://images.unsplash.com/photo-1581006852262-e4307cf6283a?w=400&h=400&fit=crop"},
    {"name": "Small plate",         "name_hindi": "छोटी प्लेट",        "price": 0.0, "image_url": "https://images.unsplash.com/photo-1610701596061-2ecf227e85b2?w=400&h=400&fit=crop"},
    {"name": "Big plate",           "name_hindi": "बड़ी प्लेट",         "price": 0.0, "image_url": "https://images.unsplash.com/photo-1686580091125-a64b744bba4c?w=400&h=400&fit=crop"},
    {"name": "Small bowl",          "name_hindi": "छोटी कटोरी",        "price": 0.0, "image_url": "https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=400&h=400&fit=crop"},
    {"name": "Spoon",               "name_hindi": "चम्मच",             "price": 0.0, "image_url": "https://images.unsplash.com/photo-1619367300933-376d8c5cd5f9?w=400&h=400&fit=crop"},
    {"name": "Fork",                "name_hindi": "कांटा",             "price": 0.0, "image_url": "https://images.unsplash.com/photo-1569702824812-351205c9cde5?w=400&h=400&fit=crop"},
    {"name": "Salt",                "name_hindi": "नमक",               "price": 0.0, "image_url": "https://images.unsplash.com/photo-1634612831148-03a8550e1d52?w=400&h=400&fit=crop"},
    {"name": "Sugar",               "name_hindi": "चीनी",              "price": 0.0, "image_url": "https://images.unsplash.com/photo-1610219171189-286769cc9b20?w=400&h=400&fit=crop"},
    {"name": "Lunch",               "name_hindi": "दोपहर का भोजन",    "price": 0.0, "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=400&fit=crop"},
    {"name": "Vada pav",            "name_hindi": "वड़ा पाव",           "price": 0.0, "image_url": "https://images.unsplash.com/photo-1750767396969-f37060ebe07d?w=400&h=400&fit=crop"},
    {"name": "Samosa",              "name_hindi": "समोसा",             "price": 0.0, "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&h=400&fit=crop"},
    {"name": "Breakfast",           "name_hindi": "नाश्ता",            "price": 0.0, "image_url": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=400&h=400&fit=crop"},
    {"name": "Other",               "name_hindi": "अन्य",              "price": 0.0, "image_url": "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=400&h=400&fit=crop"},
]


# ── Migration helpers ─────────────────────────────────────────────────────────

def _apply_migrations(db: Session) -> None:
    """
    Apply lightweight schema migrations that cannot be handled by
    ``create_all`` (e.g. adding columns to existing tables).
    """
    # Add `name_hindi` column if an older database is missing it
    try:
        db.execute(text("SELECT name_hindi FROM products LIMIT 1"))
    except Exception:
        db.rollback()
        try:
            logger.info("Migrating database: adding 'name_hindi' column to products…")
            db.execute(text("ALTER TABLE products ADD COLUMN name_hindi VARCHAR"))
            db.commit()
            logger.info("Migration applied successfully.")
        except Exception as exc:
            logger.error("Migration failed: %s", exc)
            db.rollback()


# ── Seeding helpers ───────────────────────────────────────────────────────────

def _seed_users(db: Session) -> None:
    """Create default users if they do not already exist."""
    for user_data in _DEFAULT_USERS:
        exists = db.query(User).filter(User.username == user_data["username"]).first()
        if not exists:
            db.add(User(
                username=user_data["username"],
                password_hash=get_password_hash(user_data["password"]),
                role=user_data["role"],
            ))


def _seed_products(db: Session) -> None:
    """
    Create products from the seed list, or update existing ones so that
    image URLs and Hindi names stay current across deployments.
    """
    for prod_data in _DEFAULT_PRODUCTS:
        product = db.query(Product).filter(Product.name == prod_data["name"]).first()
        if product:
            product.name_hindi = prod_data["name_hindi"]
            product.image_url = prod_data["image_url"]
        else:
            db.add(Product(**prod_data))


# ── Public API ────────────────────────────────────────────────────────────────

def init_db(db: Session) -> None:
    """
    Initialise the database:
    1. Create all tables.
    2. Apply any pending schema migrations.
    3. Seed default users and products.
    """
    # Import Base here to avoid circular imports at module load time
    from backend.app.db.base import Base  # noqa: F401
    Base.metadata.create_all(bind=engine)

    _apply_migrations(db)
    _seed_users(db)
    _seed_products(db)

    db.commit()


if __name__ == "__main__":
    from backend.app.db.session import SessionLocal

    db = SessionLocal()
    try:
        init_db(db)
        print("Database initialised successfully.")
    finally:
        db.close()