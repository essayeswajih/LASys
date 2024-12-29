from fastapi import FastAPI, Response
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

@app.get("/favicon.ico", response_class=Response)
async def favicon():
    return Response(status_code=204)  # No Content

if __name__ == "__main__":
    uvicorn.run(app, port=8000)