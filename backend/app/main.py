
import sys
import os
# Add the project root (switched to absolute path resolution) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from backend.app.api.endpoints import router
from backend.app.core.config import settings
from backend.app.db.init_db import init_db
from backend.app.db.session import SessionLocal

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# Define base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend/static")), name="static")

# Templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "frontend/templates"))

# Include API router
app.include_router(router, prefix="/api")

# Serve HTML pages
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/order", response_class=HTMLResponse)
async def read_order(request: Request):
    return templates.TemplateResponse("order.html", {"request": request})

@app.get("/pantry", response_class=HTMLResponse)
async def read_pantry(request: Request):
    return templates.TemplateResponse("pantry.html", {"request": request})

from fastapi.responses import FileResponse
@app.get("/sw.js")
async def service_worker():
    return FileResponse(os.path.join(BASE_DIR, "sw.js"), media_type="application/javascript")

@app.on_event("startup")
def on_startup():
    # Initialize DB
    db = SessionLocal()
    init_db(db)
    db.close()

if __name__ == "__main__":
    import uvicorn
    # Run the app
    # Trigger reload
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
