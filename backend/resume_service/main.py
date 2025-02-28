from fastapi import FastAPI
from routes import router
from database import initialize_database
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_database()
    yield

app = FastAPI(title="Resume Service API", lifespan=lifespan)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
# or 
# uvicorn main:app --reload