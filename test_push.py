from backend.app.db.session import SessionLocal
from backend.app.models.push_subscription import PushSubscription
from backend.app.core.config import settings
from pywebpush import webpush, WebPushException
import json

db = SessionLocal()
subs = db.query(PushSubscription).all()
print(f"Found {len(subs)} subscriptions.")

for sub in subs:
    print(f"Sending to {sub.endpoint[:30]}...")
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
                "title": "Test Notification",
                "body": "This is a direct test from the backend.",
                "url": "/pantry"
            }),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_CLAIMS_EMAIL}
        )
        print("✅ Success!")
    except WebPushException as ex:
        print(f"❌ Failed: {ex}")
        if ex.response:
             print(f"Response: {ex.response.text}")

db.close()
