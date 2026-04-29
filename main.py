import logging
logging.basicConfig(level=logging.INFO)

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.routers import auth, dashboard, groups, assignments, school, users
from db.db_ext import init_db

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="LMS Exam Prep API", lifespan=lifespan)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # добавь свой фронтенд URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(groups.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(assignments.router, prefix="/api")
app.include_router(school.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Welcome to Exam Prep API", "docs": "/docs"}


if __name__ == "__main__":
    import os
    debug = os.getenv("DEBUG", "true").lower() == "true"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=debug)