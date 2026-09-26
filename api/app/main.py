import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health, jobs
from app.storage import ensure_data_dirs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("quicklcoudy.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_data_dirs()
    logger.info("QUICKLCOUDY API started")
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="QUICKLCOUDY API",
        description="Image conversion API for QUICKLCOUDY",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(jobs.router, prefix="/api")
    return app


app = create_app()
