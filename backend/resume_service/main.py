from fastapi import FastAPI
from routes import router
from database import initialize_database

app = FastAPI(title="Resume Service API")

@app.on_event("startup")
async def startup_event():
    initialize_database()

@app.on_event("shutdown")
async def shutdown_event():
    close_database_connection()

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
# or 
# uvicorn main:app --reload