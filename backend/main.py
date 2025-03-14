from fastapi import FastAPI
from backend.api.routes import router
from backend.core.database import initialize_database
from contextlib import asynccontextmanager
from backend.api.auth import auth_router
from backend.core.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_database()
    yield

app = FastAPI(title="Job Search and Match Service API", lifespan=lifespan)
app.include_router(router)
app.include_router(auth_router)

logger.debug("Starting application")

# uvicorn main:app --reload
# uvicorn api:app --reload --log-level debug