import os

class Settings:
    PROJECT_NAME = os.getenv("PROJECT_NAME", "Insta-Pantry")
    PROJECT_VERSION = os.getenv("PROJECT_VERSION", "1.0.0")

    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_b5nFf6GNiTvJ@ep-cool-smoke-advsyud7-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require")
    SECRET_KEY = os.getenv("SECRET_KEY",'parthiv283')
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    )

    def __init__(self):
        self.ENV = os.getenv("VERCEL_ENV") or os.getenv("ENV", "local")
        
        # Determine Database URL
        if self.ENV == "local":
            # Use SQLite for local development to avoid conflicts with Start fresh
            self.DATABASE_URL = "sqlite:///./pantry.db"
        else:
            # Use Production DB
            self.DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_b5nFf6GNiTvJ@ep-cool-smoke-advsyud7-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require")

        if self.ENV != "local":
            if not self.DATABASE_URL:
                raise RuntimeError("DATABASE_URL is required in production")
            if not self.SECRET_KEY:
                raise RuntimeError("SECRET_KEY is required in production")
            
            # VAPID key handling for production
            if "private_key.pem" in self.VAPID_PRIVATE_KEY:
                pass 


    # VAPID Keys
    VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", os.path.join(os.getcwd(), "private_key.pem"))
    VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "BC6WcAbTYUzXRgEPxN_rHTsCfYKk-BUk0yVao2czbAp39_K58ftCvpHq_0iPlXqvXegCZBVyYo-uf7xBE4JT1NE")
    VAPID_CLAIMS_EMAIL = os.getenv("VAPID_CLAIMS_EMAIL", "mailto:admin@example.com")

settings = Settings()
