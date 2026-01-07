from backend.app.db.session import SessionLocal
from backend.app.models.user import User
from backend.app.models.push_subscription import PushSubscription
from backend.app.core.security import get_password_hash

db = SessionLocal()

# Check for pantry user
pantry_user = db.query(User).filter(User.role == "pantry").first()
if not pantry_user:
    print("Creating pantry user...")
    pantry_user = User(username="pantry_manager", password_hash=get_password_hash("password123"), role="pantry")
    db.add(pantry_user)
    db.commit()
    print("Created pantry_manager / password123")
else:
    print(f"Found pantry user: {pantry_user.username}")

# Check for employee user
employee_user = db.query(User).filter(User.role == "employee").first()
if not employee_user:
    print("Creating employee user...")
    employee_user = User(username="employee_1", password_hash=get_password_hash("password123"), role="employee")
    db.add(employee_user)
    db.commit()
    print("Created employee_1 / password123")
else:
    print(f"Found employee user: {employee_user.username}")

db.close()
