"""
SQLAlchemy declarative base and model registry.

Import all models here so that ``Base.metadata.create_all()`` can discover
every table, including those defined in models that are not imported elsewhere.
"""

from backend.app.db.session import Base  # noqa: F401 — re-exported for convenience

# Registering all models with the shared metadata
from backend.app.models.user import User  # noqa: F401
from backend.app.models.product import Product  # noqa: F401
from backend.app.models.order import Order  # noqa: F401
from backend.app.models.push_subscription import PushSubscription  # noqa: F401
