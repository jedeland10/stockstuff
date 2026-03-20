import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.database import create_pool, close_pool
from app.services.updater import start_scheduler
from app.routers import screener, company, chart

logging.basicConfig(level=logging.INFO)

STATIC_DIR = Path(__file__).parent / "static"


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

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def index():
    return FileResponse(str(STATIC_DIR / "index.html"))
