import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.database import create_pool, close_pool
from app.services.updater import start_scheduler
from app.routers import screener, company, chart, scores

logging.basicConfig(level=logging.INFO)

# SvelteKit build output (production) or old static dir (fallback)
BUILD_DIR = Path(__file__).resolve().parent.parent / "frontend" / "build"
STATIC_DIR = Path(__file__).parent / "static"

# Use SvelteKit build if available, otherwise fall back to old static
FRONTEND_DIR = BUILD_DIR if BUILD_DIR.exists() else STATIC_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_pool()
    start_scheduler()
    yield
    await close_pool()


app = FastAPI(title="Nordic Stock Screener", lifespan=lifespan)

app.include_router(screener.router)
app.include_router(company.router)
app.include_router(chart.router)
app.include_router(scores.router)

# Mount SvelteKit's _app directory for immutable assets
if (FRONTEND_DIR / "_app").exists():
    app.mount("/_app", StaticFiles(directory=str(FRONTEND_DIR / "_app")), name="app-assets")

# Legacy static mount (for old frontend)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/{path:path}")
async def spa_fallback(request: Request, path: str = ""):
    # Serve actual files if they exist
    file = FRONTEND_DIR / path
    if path and file.exists() and file.is_file():
        return FileResponse(str(file))
    # Otherwise serve index.html (SPA fallback)
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return FileResponse(str(STATIC_DIR / "index.html"))
