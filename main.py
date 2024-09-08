from fastapi import FastAPI
from routers import rowsController  # Ensure this imports your router module
from db.database import Base, engine  # Ensure Base and engine are initialized in database.py

# Initialize FastAPI app
app = FastAPI()
# Create database tables based on models
Base.metadata.create_all(bind=engine)

# Register the logs router
app.include_router(rowsController.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}