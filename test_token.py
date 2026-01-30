
import sys
import os
from datetime import datetime, timedelta

# Add path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.app.core.security import create_access_token
from backend.app.core.config import settings
from jose import jwt

def test_expiry():
    settings.SECRET_KEY = settings.SECRET_KEY or "test_secret_key"
    print(f"Settings expiry minutes: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
    
    token = create_access_token(data={"sub": "test"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    exp = payload.get("exp")
    exp_dt = datetime.utcfromtimestamp(exp)
    now = datetime.utcnow()
    
    diff = exp_dt - now
    print(f"Token expires in: {diff}")
    
    if diff.total_seconds() > 100000: # 30 days is roughly 2.5 million seconds
        print("SUCCESS: Token expiration is long enough.")
    else:
        print("FAILURE: Token expiration is too short.")

if __name__ == "__main__":
    test_expiry()
