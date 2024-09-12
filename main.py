from fastapi import FastAPI
import uvicorn
from routers.rowsController import router as rowsRouter
from routers.logsController import router as logsRouter
from db.database import Base, engine  

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(rowsRouter, prefix="/api/v1")
app.include_router(logsRouter, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "API is working"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)