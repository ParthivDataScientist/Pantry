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
        
        # 1. Database URL
        if self.ENV == "local":
            self.DATABASE_URL = "sqlite:///./pantry.db"
        else:
            self.DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_b5nFf6GNiTvJ@ep-cool-smoke-advsyud7-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require")

        # 2. VAPID Keys
        self.VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY") 
        if not self.VAPID_PRIVATE_KEY:
            # Fallback to local file only if ENV is local or key not provided
            self.VAPID_PRIVATE_KEY = os.path.join(os.getcwd(), "private_key.pem")
            
        self.VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "BJG_hQ9UMeD-mTM25uoB_LOvV4_0l1cpzrZ_l1HXXHG53LC4c3ssWUU2L0_SFvWNVxZwdCO3_4UWyEp_BbJTO20")
        
        # Sanitize PEM format if present (remove headers/footers/newlines)
        if "-----BEGIN PUBLIC KEY-----" in self.VAPID_PUBLIC_KEY:
            self.VAPID_PUBLIC_KEY = self.VAPID_PUBLIC_KEY.replace("-----BEGIN PUBLIC KEY-----", "")\
                                                         .replace("-----END PUBLIC KEY-----", "")\
                                                         .replace("\n", "")\
                                                         .replace("\r", "")\
                                                         .strip()

        self.VAPID_CLAIMS_EMAIL = os.getenv("VAPID_CLAIMS_EMAIL", "mailto:admin@example.com")

        # 3. Validation
        if self.ENV != "local":
            if not self.DATABASE_URL:
                raise RuntimeError("DATABASE_URL is required in production")
            if not self.SECRET_KEY:
                raise RuntimeError("SECRET_KEY is required in production")
            
            # Check if VAPID key is likely a file path but we are in production
            # (In prod, it should usually be the content, but if mapped as file that's okay too)
            if "private_key.pem" in self.VAPID_PRIVATE_KEY:
                # Log or warn if needed, but don't crash unless critical
                pass

settings = Settings()

