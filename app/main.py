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

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "build"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_pool()
    start_scheduler()
    yield
    await close_pool()


app = FastAPI(title="Stonklens", lifespan=lifespan)

app.include_router(screener.router)
app.include_router(company.router)
app.include_router(chart.router)
app.include_router(scores.router)

if (FRONTEND_DIR / "_app").exists():
    app.mount("/_app", StaticFiles(directory=str(FRONTEND_DIR / "_app")), name="app-assets")


@app.get("/{path:path}")
async def spa_fallback(request: Request, path: str = ""):
    file = FRONTEND_DIR / path
    if path and file.exists() and file.is_file():
        return FileResponse(str(file))
    return FileResponse(str(FRONTEND_DIR / "index.html"))
