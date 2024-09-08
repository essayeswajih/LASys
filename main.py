from fastapi import FastAPI
from routers import rowsController  
from db.database import Base, engine  

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(rowsController.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}