from fastapi import FastAPI, Request
from backend.api.routes import router
from backend.core.database import initialize_database
from contextlib import asynccontextmanager
from backend.api.auth import auth_router
from backend.core.logger import logger
from backend.core.middleware import log_middleware
from starlette.middleware.base import BaseHTTPMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_database()
    yield


app = FastAPI(title="Job Search and Match Service API", lifespan=lifespan)
app.include_router(router)
app.include_router(auth_router)
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

logger.debug("Starting application")

# uvicorn main:app --reload
# uvicorn api:app --reload --log-level debug