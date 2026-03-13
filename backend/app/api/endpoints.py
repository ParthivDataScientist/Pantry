"""
API route handlers.

All endpoints are registered on ``router`` and mounted under ``/api``
in ``main.py``.
"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.api.deps import get_current_user
from backend.app.core.notifications import notify_pantry_managers
from backend.app.core.security import create_access_token, get_password_hash, verify_password
from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.models.order import Order as OrderModel
from backend.app.models.product import Product as ProductModel
from backend.app.models.push_subscription import PushSubscription
from backend.app.models.user import User
from backend.app.schemas.order import Order, OrderCreate
from backend.app.schemas.product import Product
from backend.app.schemas.push_subscription import PushSubscriptionCreate
from backend.app.schemas.user import Token, UserCreate, UserLogin

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Auth ──────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT access token."""
    user = db.query(User).filter(User.username == user_in.username).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    redirect_url = "/pantry" if user.role == "pantry" else "/order"

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "redirect_url": redirect_url,
        "role": user.role,
    }


@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new employee account and return a JWT access token."""
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered.",
        )

    new_user = User(
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        role="employee",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": new_user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "redirect_url": "/order",
        "role": new_user.role,
    }


# ── Products ──────────────────────────────────────────────────────────────────

@router.get("/products", response_model=List[Product])
def get_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all available products (requires authentication)."""
    return db.query(ProductModel).all()


# ── Orders ────────────────────────────────────────────────────────────────────

@router.post("/order", response_model=Order)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Place a new order. Only employees can place orders."""
    if current_user.role != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employees can place orders.",
        )

    # Enrich each ordered item with the latest image URL from the DB
    enriched_items = []
    for item in order_in.items:
        item_dict = item.dict()
        product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        if product and product.image_url:
            item_dict["image_url"] = product.image_url
        enriched_items.append(item_dict)

    db_order = OrderModel(
        employee_id=current_user.username,
        items=json.dumps(enriched_items),
        status="Pending",
        notes=order_in.notes or None,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    notify_pantry_managers(db, db_order)

    return db_order


@router.get("/pantry/orders", response_model=List[Order])
def get_pantry_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all pending orders. Only pantry staff can access this."""
    if current_user.role != "pantry":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only pantry staff can view orders.",
        )

    orders = db.query(OrderModel).filter(OrderModel.status == "Pending").all()

    # Re-enrich items with up-to-date product metadata (image, Hindi name)
    for order in orders:
        try:
            items = json.loads(order.items)
            enriched = []
            for item in items:
                product = db.query(ProductModel).filter(ProductModel.name == item["name"]).first()
                if product:
                    item["image_url"] = product.image_url
                    item["name_hindi"] = product.name_hindi
                enriched.append(item)
            order.items = json.dumps(enriched)
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("Could not enrich items for order %s: %s", order.id, exc)

    return orders


@router.patch("/order/{order_id}/done", status_code=status.HTTP_200_OK)
def mark_order_done(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an order as completed. Only pantry staff can do this."""
    if current_user.role != "pantry":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only pantry staff can mark orders as done.",
        )

    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order #{order_id} not found.",
        )

    order.status = "Completed"
    db.commit()
    return {"message": f"Order #{order_id} marked as completed."}


# ── Push Notifications ────────────────────────────────────────────────────────

@router.post("/subscribe", status_code=status.HTTP_200_OK)
def subscribe_to_push(
    subscription: PushSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a browser push subscription for the current user."""
    endpoint_str = str(subscription.endpoint)

    existing = db.query(PushSubscription).filter(
        PushSubscription.endpoint == endpoint_str
    ).first()
    if existing:
        return {"message": "Already subscribed."}

    new_sub = PushSubscription(
        user_id=current_user.id,
        endpoint=endpoint_str,
        p256dh=subscription.keys["p256dh"],
        auth=subscription.keys["auth"],
    )
    db.add(new_sub)
    db.commit()
    return {"message": "Subscribed successfully."}


@router.get("/vapid-public-key")
def get_vapid_public_key():
    """Return the VAPID public key for the browser push client."""
    return {"public_key": settings.VAPID_PUBLIC_KEY}
