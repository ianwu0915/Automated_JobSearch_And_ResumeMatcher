from fastapi import FastAPI
from backend.api.routes import router
from backend.core.database import initialize_database
from contextlib import asynccontextmanager
from backend.api.auth import auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_database()
    yield

app = FastAPI(title="Job Search and Match Service API", lifespan=lifespan)
app.include_router(router)
app.include_router(auth_router)

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)

# or
# uvicorn main:app --reload