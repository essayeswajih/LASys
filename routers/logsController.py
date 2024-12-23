import re
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, logger
from sqlalchemy.orm import Session
from typing import List
from models.logsEntity import Log
from db.database import get_db
from schemas.logDTO import LogDTO ,LogCreate
from schemas.rowDTO import RowDTO

import logging

logger = logging.getLogger(__name__)

# Instead of `fastapi.logger.error()`, use `logger.error()`



router = APIRouter()

# GET: get all logs
@router.get("/logs", response_model=List[LogDTO])
def find_all_logs(db: Session = Depends(get_db)):
    try:
        logs = db.query(Log).all()
        if not logs:
            raise HTTPException(status_code=404, detail="No logs found")
        
        # Serialize logs using dict(), assuming LogDTO fields match Log model
        return logs  # Or log.to_dict() if a custom method exists
    except Exception as e:
        print(e)
        logger.error(f"Error occurred while fetching logs: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching logs: {e}")
    
# GET: get a log by ID
@router.get("/logs/{log_id}",response_model=LogDTO)
def get_log_by_id(log_id:int,db:Session =Depends(get_db)):
    log = db.query(Log).filter(Log.id == log_id).first()
    if log is None:
        raise HTTPException(status_code=404,detail="Log not found")
    return log

# POST: Create a new log
@router.post("/logs", response_model=LogCreate)
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    try:
        db_log = Log(
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
    db_log = db.query(Log).filter(Log.id == log_id).first()
    
    if db_log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    
    db.delete(db_log)
    db.commit()
    
    return db_log

@router.post("/logs/upload")
async def upload_log(file: UploadFile = File(...)):
    try:
        # Read the file contents (it could be large, so handle carefully)
        contents = await file.read()
        
        # Process the Apache log file and extract log entries
        rows = parse_apache_log(contents.decode())
        
        # Create a new Log object
        log = Log(
            file_name=file.filename,
            file_type=file.content_type,
            rows=rows  # Assuming rows are instances of RowDTO or related ORM models
        )
        
        # Save the log object to the database
        # db.add(log)
        # db.commit()
        
        # Convert log to Pydantic LogDTO for response
        log_dto = LogDTO.model_validate(log)
        
        return {"message": "Log uploaded successfully", "log": log_dto.model_dump()}
    except Exception as e:
        logger.error(f"Error occurred while uploading log: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while uploading the log.")
    
def parse_apache_log(contents: str) -> List[RowDTO]:
    rows = []
    try:
        # Regular expression pattern for Apache log entry (common or combined log format)
        log_pattern = r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>.*?)\] "(?P<method>\S+) (?P<url>\S+) HTTP/\S+" (?P<status_code>\d+) (?P<response_size>\d+) "(?P<referrer>.*?)" "(?P<user_agent>.*?)"'
        
        # Process each line of the log file
        for line in contents.splitlines():
            match = re.match(log_pattern, line)
            if match:
                # Extract data from the log line using named groups
                log_data = match.groupdict()
                row = RowDTO(
                    ip=log_data['ip'],
                    timestamp=log_data['timestamp'],
                    method=log_data['method'],
                    url=log_data['url'],
                    status_code=log_data['status_code'],
                    response_size=log_data['response_size'],
                    referrer=log_data['referrer'],
                    user_agent=log_data['user_agent']
                )
                rows.append(row)
            else:
                logger.warning(f"Skipping invalid log line: {line}")
    except Exception as e:
        logger.error(f"Error occurred while parsing Apache log: {e}")
        raise HTTPException(status_code=400, detail="Error parsing the Apache log file.")
    
    return rows