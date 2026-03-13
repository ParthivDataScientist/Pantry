"""
FastAPI application entry point.

Mounts static files, serves HTML templates, and registers the API router.
Database initialisation is performed inside the `lifespan` context so it runs
once on startup with proper cleanup on shutdown.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.app.api.endpoints import router
from backend.app.core.config import settings
from backend.app.db.init_db import init_db
from backend.app.db.session import SessionLocal

# ── Directory constants ───────────────────────────────────────────────────────
# Resolved relative to this file's location so the app works regardless of the
# working directory it is started from.
_HERE = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(_HERE, "..", ".."))

STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "frontend", "templates")
SW_PATH = os.path.join(BASE_DIR, "sw.js")


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise the database on startup, clean up on shutdown."""
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    yield
    # (Add any shutdown logic here if needed in the future)


# ── Application ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

app.include_router(router, prefix="/api")


# ── Page routes ───────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/order", response_class=HTMLResponse)
async def order_page(request: Request):
    return templates.TemplateResponse("order.html", {"request": request})


@app.get("/pantry", response_class=HTMLResponse)
async def pantry_page(request: Request):
    return templates.TemplateResponse("pantry.html", {"request": request})


@app.get("/sw.js")
async def service_worker():
    """Serve the service worker from the project root at the expected path."""
    return FileResponse(SW_PATH, media_type="application/javascript")


# ── Dev runner ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
