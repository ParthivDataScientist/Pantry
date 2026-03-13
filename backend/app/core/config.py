import os

class Settings:
    PROJECT_NAME = os.getenv("PROJECT_NAME", "Insta-Pantry")
    PROJECT_VERSION = os.getenv("PROJECT_VERSION", "1.0.0")

    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 43200)
    )

    def __init__(self):
        # 1. Database URL
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        if not self.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is required in production")

        # 2. VAPID Keys
        self.VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
        if not self.VAPID_PRIVATE_KEY:
            raise RuntimeError("VAPID_PRIVATE_KEY is required in production")
            
        self.VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
        if not self.VAPID_PUBLIC_KEY:
            raise RuntimeError("VAPID_PUBLIC_KEY is required in production")
        
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

        if not self.SECRET_KEY:
            raise RuntimeError("SECRET_KEY is required in production")

settings = Settings()

