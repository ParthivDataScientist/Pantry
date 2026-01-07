import os

class Settings:
    PROJECT_NAME = os.getenv("PROJECT_NAME", "Insta-Pantry")
    PROJECT_VERSION = os.getenv("PROJECT_VERSION", "1.0.0")

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pantry.db")
    SECRET_KEY = os.getenv("SECRET_KEY",'')
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
            if "private_key.pem" in self.VAPID_PRIVATE_KEY:
                # In production, we should get the key content from Env, not a file path default
                # Unless the user explicitly mapped a file, but for Vercel it's usually the content.
                # Let's just warn or check length.
                pass 


    # VAPID Keys
    VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", os.path.join(os.getcwd(), "private_key.pem"))
    VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "BJG_hQ9UMeD-mTM25uoB_LOvV4_0l1cpzrZ_l1HXXHG53LC4c3ssWUU2L0_SFvWNVxZwdCO3_4UWyEp_BbJTO20")
    VAPID_CLAIMS_EMAIL = os.getenv("VAPID_CLAIMS_EMAIL", "mailto:admin@example.com")

settings = Settings()
