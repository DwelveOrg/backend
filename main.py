import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routers import auth, dashboard, groups
from db.db_ext import init_db

import logging
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация БД при старте приложения."""
    await init_db()
    yield


app = FastAPI(
    title="LMS Exam Prep API",
    lifespan=lifespan
)

# Все роутеры под префиксом /api
app.include_router(auth.router, prefix="/api")
app.include_router(groups.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Welcome to Exam Prep API", "docs": "/docs"}


if __name__ == "__main__":
    import os
    debug = os.getenv("DEBUG", "true").lower() == "true"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=debug)