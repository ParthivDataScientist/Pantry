import os

class Settings:
    PROJECT_NAME = os.getenv("PROJECT_NAME", "Insta-Pantry")
    PROJECT_VERSION = os.getenv("PROJECT_VERSION", "1.0.0")

    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
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
            self.DATABASE_URL = os.getenv("DATABASE_URL")

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
        
        # Check if the key is ASN.1 encoded (starts with headers) or just raw
        # Attempt to decode to bytes to check length
        try:
            import base64
            # Add padding if needed
            pad = len(self.VAPID_PUBLIC_KEY) % 4
            if pad > 0:
                self.VAPID_PUBLIC_KEY += "=" * (4 - pad)
                
            key_bytes = base64.b64decode(self.VAPID_PUBLIC_KEY)
            
            # P-256 key is 65 bytes (0x04 + 32X + 32Y)
            # ASN.1 SubjectPublicKeyInfo for P-256 is usually 91 bytes
            if len(key_bytes) > 65:
                # Find the 0x04 65-byte sequence
                # It is usually at the end. 
                # Header usually ends with 0x03 0x42 0x00
                if b'\x03\x42\x00\x04' in key_bytes:
                    idx = key_bytes.find(b'\x03\x42\x00')
                    raw_key = key_bytes[idx+3:]
                    # Re-encode to URL-safe base64 for frontend
                    self.VAPID_PUBLIC_KEY = base64.urlsafe_b64encode(raw_key).decode().strip("=")
        except Exception:
            pass # Keep original if fails

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

