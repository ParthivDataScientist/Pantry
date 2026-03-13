import json
import logging
from sqlalchemy.orm import Session
from pywebpush import webpush, WebPushException
from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.models.order import Order

logger = logging.getLogger(__name__)

def send_push_notification(subscription_info: dict, data: dict):
    """
    Send a push notification to a single subscription.
    """
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(data),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_CLAIMS_EMAIL}
        )
        return True
    except WebPushException as ex:
        if ex.response and ex.response.status_code == 410:
            logger.info("Subscription expired or invalid: %s", ex)
            return False  # Signal to remove subscription
        logger.error("WebPush error: %s", ex)
    except Exception as e:
        logger.error("Unexpected error sending push: %s", e)
    return None

def notify_pantry_managers(db: Session, order: Order):
    """
    Notify all pantry managers about a new order.
    """
    pantry_users = db.query(User).filter(User.role == "pantry").all()
    
    notification_data = {
        "title": "New Order!",
        "body": f"Order #{order.id} from {order.employee_id}",
        "url": "/pantry"
    }

    for user in pantry_users:
        # Iterate over a copy of the list to allow modification during iteration if needed
        # (though we are modifying the DB, not the list itself)
        for sub in user.push_subscriptions:
            sub_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh,
                    "auth": sub.auth
                }
            }
            
            result = send_push_notification(sub_info, notification_data)
            
            if result is False:
                # Subscription is dead, remove it
                db.delete(sub)
    
    try:
        db.commit()
    except Exception as e:
        logger.error("Failed to commit subscription deletions: %s", e)
        db.rollback()
