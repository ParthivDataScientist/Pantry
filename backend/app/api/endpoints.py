
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
from pywebpush import webpush, WebPushException


from backend.app.db.session import get_db
from backend.app.core.security import verify_password, create_access_token
from backend.app.models.user import User
from backend.app.models.product import Product as ProductModel
from backend.app.models.order import Order as OrderModel
from backend.app.schemas.user import UserLogin, Token, UserCreate
from backend.app.schemas.product import Product
from backend.app.schemas.order import OrderCreate, Order
from backend.app.api.deps import get_current_user


router = APIRouter()


# Login Endpoint
@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_in.username).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    redirect_url = "/pantry" if user.role == "pantry" else "/order"
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "redirect_url": redirect_url,
        "role": user.role
    }


# Register Endpoint
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new user
    # Note: In a real app we might want to validate password strength etc.
    from backend.app.core.security import get_password_hash
    hashed_password = get_password_hash(user.password)
    
    new_user = User(username=user.username, password_hash=hashed_password, role="employee")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Auto-login behavior
    access_token = create_access_token(data={"sub": new_user.username})
    redirect_url = "/pantry" if new_user.role == "pantry" else "/order"
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "redirect_url": redirect_url,
        "role": new_user.role
    }


@router.get("/products", response_model=List[Product])
def get_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ProductModel).all()

@router.post("/order", response_model=Order)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verify employee matches current user or just use current user
    if current_user.role != "employee":
         raise HTTPException(status_code=403, detail="Only employees can place orders")

    item_str = json.dumps([item.dict() for item in order_in.items])
    
    db_order = OrderModel(
        employee_id=current_user.username,
        items=item_str,
        status="Pending",
        notes=order_in.notes
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Notify pantry managers
    notify_pantry_manager(db, db_order)
    
    return db_order

@router.get("/pantry/orders", response_model=List[Order])
def get_pantry_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "pantry":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return db.query(OrderModel).filter(OrderModel.status == "Pending").all()

@router.patch("/order/{order_id}/done")
def mark_order_done(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "pantry":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = "Completed"
    db.commit()
    return {"message": "Order completed"}


from pydantic import BaseModel, HttpUrl

class PushSubscriptionSchema(BaseModel):
    endpoint: HttpUrl
    keys: dict

@router.post("/subscribe")
def subscribe(subscription: PushSubscriptionSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Save subscription for the current user
    from backend.app.models.push_subscription import PushSubscription
    
    # Check if exists
    existing = db.query(PushSubscription).filter(PushSubscription.endpoint == str(subscription.endpoint)).first()
    if existing:
        return {"message": "Already subscribed"}
        
    new_sub = PushSubscription(
        user_id=current_user.id,
        endpoint=str(subscription.endpoint),
        p256dh=subscription.keys['p256dh'],
        auth=subscription.keys['auth']
    )
    db.add(new_sub)
    db.commit()
    return {"message": "Subscribed successfully"}

@router.get("/vapid-public-key")
def get_vapid_public_key():
    from backend.app.core.config import settings
    return {"public_key": settings.VAPID_PUBLIC_KEY}

def notify_pantry_manager(db: Session, order_details: OrderModel):
    from backend.app.core.config import settings
    from backend.app.models.push_subscription import PushSubscription
    
    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        print("pywebpush not installed. Skipping notification.")
        return

    # Get all pantry managers
    pantry_users = db.query(User).filter(User.role == "pantry").all()
    
    for user in pantry_users:
        for sub in user.push_subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {
                            "p256dh": sub.p256dh,
                            "auth": sub.auth
                        }
                    },
                    data=json.dumps({
                        "title": "New Order!",
                        "body": f"Order #{order_details.id} from {order_details.employee_id}",
                        "url": "/pantry"
                    }),
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": settings.VAPID_CLAIMS_EMAIL}
                )
            except WebPushException as ex:
                if ex.response and ex.response.status_code == 410:
                    # Subscription expired
                    db.delete(sub)
                    db.commit()
                print("Push failed", ex)
            except Exception as e:
                print(f"Error sending push: {e}")

