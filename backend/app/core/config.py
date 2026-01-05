import os

class Settings:
    PROJECT_NAME = os.getenv("PROJECT_NAME", "Insta-Pantry")
    PROJECT_VERSION = os.getenv("PROJECT_VERSION", "1.0.0")

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pantry.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    )

    def __init__(self):
        env = os.getenv("VERCEL_ENV") or os.getenv("ENV", "local")

        if env != "local":
            if not self.DATABASE_URL:
                raise RuntimeError("DATABASE_URL is required in production")
            if not self.SECRET_KEY:
                raise RuntimeError("SECRET_KEY is required in production")

            if not self.SECRET_KEY:
                raise RuntimeError("SECRET_KEY is required in production")

    # VAPID Keys for Push Notifications
    # GENERATE NEW KEYS FOR PRODUCTION!
    VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "Check-README-To-Generate")
    VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "Check-README-To-Generate")
    VAPID_CLAIMS_EMAIL = os.getenv("VAPID_CLAIMS_EMAIL", "mailto:admin@example.com")

settings = Settings()
