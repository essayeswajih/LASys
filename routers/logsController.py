from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import logsEntity
from db.database import get_db
from schemas.logDTO import LogDTO ,LogCreate

router = APIRouter()

# GET: get all logs
@router.get("/logs", response_model=List[LogDTO])  # Added leading "/"
def find_all_logs(db: Session = Depends(get_db)):
    try :
        logs = db.query(logsEntity.Log).all()
        return logs
    except :
        raise HTTPException(status_code=404, detail="No logs found")  # Changed to
    
# GET: get a log by ID
@router.get("/logs/{log_id}",response_model=LogDTO)
def get_log_by_id(log_id:int,db:Session =Depends(get_db)):
    log = db.query(logsEntity.Log).filter(logsEntity.Log.id == log_id).first()
    if log is None:
        raise HTTPException(status_code=404,detail="Log not found")
    return log

# POST: Create a new log
@router.post("/logs", response_model=LogCreate)
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    try:
        db_log = logsEntity.Log(
            log_of=log.log_of,
            file_name=log.file_name,
            file_type=log.file_type
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except Exception as e:
        db.rollback()  # Ensure to rollback the transaction if an error occurs
        print(f"Error occurred: {e}")  # Log the exception for debugging
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating the log"
        )

# DELETE: Delete a log by ID
@router.delete("/logs/{log_id}", response_model=LogDTO)
def delete_log(log_id: int, db: Session = Depends(get_db)):
    db_log = db.query(logsEntity.Log).filter(logsEntity.Log.id == log_id).first()
    
    if db_log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    
    db.delete(db_log)
    db.commit()
    
    return db_log
