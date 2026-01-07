from backend.app.db.session import SessionLocal
from backend.app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.username == "test_pantry").first()
if user:
    user.role = "pantry"
    db.commit()
    print("User role updated to pantry")
else:
    print("User not found")
db.close()
