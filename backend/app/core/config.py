"""
Application configuration.

Settings are read from environment variables. A SQLite fallback is provided
for local development so the server can start without any .env setup.
"""

import os
import base64


def _normalize_vapid_public_key(key: str) -> str:
    """
    Strip PEM headers/footers and convert an ASN.1-encoded VAPID public key
    to the raw 65-byte uncompressed point, base64url-encoded (no padding).

    Raw keys (65 bytes) are returned unchanged.
    """
    # Remove PEM wrapper and whitespace
    if "-----BEGIN PUBLIC KEY-----" in key:
        key = (
            key.replace("-----BEGIN PUBLIC KEY-----", "")
               .replace("-----END PUBLIC KEY-----", "")
               .replace("\n", "")
               .replace("\r", "")
               .strip()
        )

    # Ensure correct base64 padding before decoding
    pad = len(key) % 4
    if pad:
        key += "=" * (4 - pad)

    try:
        key_bytes = base64.b64decode(key)

        # P-256 uncompressed public key is exactly 65 bytes (0x04 + 32 + 32).
        # ASN.1 SubjectPublicKeyInfo wrapping is typically 91 bytes.
        if len(key_bytes) > 65 and b"\x03\x42\x00\x04" in key_bytes:
            idx = key_bytes.find(b"\x03\x42\x00")
            raw_key = key_bytes[idx + 3:]
            key = base64.urlsafe_b64encode(raw_key).decode().rstrip("=")
    except Exception:
        pass  # Return key as-is if anything fails

    return key


class Settings:
    """Central application settings loaded from environment variables."""

    # ── Project metadata ──────────────────────────────────────────────────
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Insta-Pantry")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "1.0.0")

    # ── Auth ──────────────────────────────────────────────────────────────
    SECRET_KEY: str
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 43200))

    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str

    # ── VAPID (Web Push) ──────────────────────────────────────────────────
    VAPID_PRIVATE_KEY: str
    VAPID_PUBLIC_KEY: str
    VAPID_CLAIMS_EMAIL: str

    def __init__(self) -> None:
        # Database — fall back to local SQLite for development
        self.DATABASE_URL = os.getenv("DATABASE_URL") or self._local_sqlite_url()

        # Auth secret
        self.SECRET_KEY = os.getenv("SECRET_KEY", "")
        if not self.SECRET_KEY:
            raise RuntimeError("SECRET_KEY environment variable is required.")

        # VAPID keys
        vapid_private = os.getenv("VAPID_PRIVATE_KEY", "")
        if not vapid_private:
            raise RuntimeError("VAPID_PRIVATE_KEY environment variable is required.")
        self.VAPID_PRIVATE_KEY = vapid_private

        vapid_public = os.getenv("VAPID_PUBLIC_KEY", "")
        if not vapid_public:
            raise RuntimeError("VAPID_PUBLIC_KEY environment variable is required.")
        self.VAPID_PUBLIC_KEY = _normalize_vapid_public_key(vapid_public)

        self.VAPID_CLAIMS_EMAIL = os.getenv("VAPID_CLAIMS_EMAIL", "mailto:admin@example.com")

    @staticmethod
    def _local_sqlite_url() -> str:
        """Return an absolute SQLite URL pointing to the project root."""
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )
        db_path = os.path.join(project_root, "pantry.db")
        return f"sqlite:///{db_path}"


settings = Settings()
