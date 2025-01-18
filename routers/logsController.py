import subprocess
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from tools.parser import parse_apache_log
from models.rowEntity import Row
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
# POST: Upload a new Log File
@router.post("/logs/upload")
async def upload_log(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded.")

        # Read the file contents
        contents = await file.read()

        # Process the Apache log file
        row_dtos = parse_apache_log(contents.decode())
        
        # Convert Pydantic Row to SQLAlchemy Row objects
        rows = [Row(**row_dto.model_dump()) for row_dto in row_dtos]
        
        # Create and save the Log object
        log = Log(
            file_name=file.filename,
            file_type="apache",
            rows=rows  # Associating ORM rows with the log
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        # Convert log to LogDTO for response
        log_dto = LogDTO.model_validate(log)
        return {"message": "Log uploaded successfully", "log": log_dto.model_dump()}
    except HTTPException as he:
        raise he  # Re-raise HTTPExceptions as-is
    except Exception as e:
        logger.error(f"Error occurred while uploading log: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while uploading the log: {e}")
    
# GET: get a rows by log id
@router.get("/logs/{log_id}/rows", response_model=list[RowDTO])
def find_rows_by_log_id(log_id: int, db: Session = Depends(get_db)):
    log = db.query(Log).filter(Log.id == log_id).first()
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    rows = log.rows
    return rows

# GET: get top status by log id
@router.get("/logs/{log_id}/topstatus", response_model=list[dict[int, int]])
def find_top_rows_by_log_id(log_id: int, db: Session = Depends(get_db)):
    log = db.query(Log).filter(Log.id == log_id).first()
    
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    
    # Query to get the top 5 most frequent status codes with their counts
    statuscodes = db.query(Row.status, func.count(Row.status).label('status_count')) \
        .filter(Row.log_id == log_id) \
        .group_by(Row.status) \
        .order_by(func.count(Row.status).desc()) \
        .limit(5) \
        .all()
    
    # Format the result as a list of dictionaries {status_code: count}
    top_status_codes = [{status[0]: status[1]} for status in statuscodes]
    
    return top_status_codes

# GET: get top rows that have top status by log id
@router.get("/logs/{log_id}/rows/topstatus", response_model=list[RowDTO])
def find_top_rows_by_log_id(log_id: int, db: Session = Depends(get_db)):
    log = db.query(Log).filter(Log.id == log_id).first()
    
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    
    # Query to get the top 5 most frequent status codes
    statuscodes = db.query(Row.status).filter(Row.log_id == log_id) \
        .group_by(Row.status) \
        .order_by(func.count(Row.status).desc()) \
        .limit(5) \
        .all()
    
    # Extract the status codes from the result
    top_status_codes = [status[0] for status in statuscodes]
    
    # Retrieve rows with those status codes and sort them
    top_rows = [row for row in log.rows if row.status in top_status_codes]
    
    return top_rows

# GET: get top status by log id
@router.get("/logs/{log_id}/toppaths", response_model=list[dict[str, int]])
def find_top_paths_by_log_id(log_id: int, db: Session = Depends(get_db)):
    log = db.query(Log).filter(Log.id == log_id).first()
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    
    # Query to get the top 5 most frequent paths with their counts
    paths = db.query(Row.url, func.count(Row.url).label('path_count')) \
        .filter(Row.log_id == log_id) \
        .group_by(Row.url) \
        .order_by(func.count(Row.url).desc()) \
        .limit(5) \
        .all()
    
    # Format the result as a list of dictionaries
    top_paths = [{path[0]: path[1]} for path in paths]
    
    return top_paths


# GET: get top HTTP methods by log id
@router.get("/logs/{log_id}/topmethods", response_model=list[dict[str, int]])
def find_top_methods_by_log_id(log_id: int, db: Session = Depends(get_db)):
    log = db.query(Log).filter(Log.id == log_id).first()
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    
    # Query to get the top 5 most frequent HTTP methods with their counts
    methods = db.query(Row.method, func.count(Row.method).label('method_count')) \
        .filter(Row.log_id == log_id) \
        .group_by(Row.method) \
        .order_by(func.count(Row.method).desc()) \
        .limit(5) \
        .all()
    
    # Format the results as a list of dictionaries
    top_methods = [{method[0]: method[1]} for method in methods]
    
    return top_methods
# GET: get top IP's methods by log id
@router.get("/logs/{log_id}/topips", response_model=list[dict[str, int]])
def find_top_ips_by_log_id(log_id: int, db: Session = Depends(get_db)):
    log = db.query(Log).filter(Log.id == log_id).first()
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    
    # Query to get the top 5 most frequent IP addresses with their counts
    ips = db.query(Row.ip, func.count(Row.ip).label('ip_count')) \
        .filter(Row.log_id == log_id) \
        .group_by(Row.ip) \
        .order_by(func.count(Row.ip).desc()) \
        .limit(5) \
        .all()
    
    # Format the results as a list of dictionaries
    top_ips = [{ip[0]: ip[1]} for ip in ips]
    
    return top_ips

# GET: get top protocols methods by log id
@router.get("/logs/{log_id}/topprotocols", response_model=list[dict[str, int]])
def find_top_protocols_by_log_id(log_id: int, db: Session = Depends(get_db)):
    log = db.query(Log).filter(Log.id == log_id).first()
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    
    # Query to get the top 5 most frequent protocols with their counts
    protocols = db.query(Row.protocol, func.count(Row.protocol).label('protocol_count')) \
        .filter(Row.log_id == log_id) \
        .group_by(Row.protocol) \
        .order_by(func.count(Row.protocol).desc()) \
        .limit(5) \
        .all()
    
    # Format the results as a list of dictionaries
    top_protocols = [{protocol[0]: protocol[1]} for protocol in protocols]
    
    return top_protocols

# GET: get top users methods by log id
@router.get("/logs/{log_id}/topusers", response_model=list[dict[str, int]])
def find_top_users_by_log_id(log_id: int, db: Session = Depends(get_db)):
    log = db.query(Log).filter(Log.id == log_id).first()
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    
    # Query to get the top 5 most frequent users with their counts
    users = db.query(Row.user, func.count(Row.user).label('user_count')) \
        .filter(Row.log_id == log_id) \
        .group_by(Row.user) \
        .order_by(func.count(Row.user).desc()) \
        .limit(5) \
        .all()
    
    # Format the results as a list of dictionaries
    top_users = [{user[0]: user[1]} for user in users]
    
    return top_users
# GET: get top user agents methods by log id
@router.get("/logs/{log_id}/topuseragents", response_model=list[dict[str, int]])
def find_top_user_agents_by_log_id(log_id: int, db: Session = Depends(get_db)):
    log = db.query(Log).filter(Log.id == log_id).first()
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    
    # Query to get the top 5 most frequent user agents with their counts
    user_agents = db.query(Row.user_agent, func.count(Row.user_agent).label('user_agent_count')) \
        .filter(Row.log_id == log_id) \
        .group_by(Row.user_agent) \
        .order_by(func.count(Row.user_agent).desc()) \
        .limit(5) \
        .all()
    
    # Format the results as a list of dictionaries
    top_user_agents = [{user_agent[0]: user_agent[1]} for user_agent in user_agents]
    
    return top_user_agents


class FilterRequest(BaseModel):
    file_name: str
    sed_command: str

# POST: get filtred rows by log name and sed command
@router.post("/logs/rows/filtred", response_model=str)
def find_filtred_rows_by_log_name_and_sed_command(
    request: FilterRequest,  # Use the request body model
    db: Session = Depends(get_db)
):
    file_name = request.file_name
    sed_command = request.sed_command

    # Fetch the log by file name
    log = db.query(Log).filter(Log.file_name == file_name).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    # Check if the log has rows
    if not log.rows:
        raise HTTPException(status_code=400, detail="No rows found for the log")

    # Convert rows to a formatted string suitable for sed processing
    try:
        rows_data = "\n".join(
            f"{row.ip} {row.remote_logname} {row.user} {row.timestamp} "
            f"{row.method} {row.url} {row.protocol} {row.status} "
            f"{row.response_size if row.response_size else '0'} {row.referer if row.referer else '-'} {row.user_agent}"
            for row in log.rows
        )
    except AttributeError as e:
        raise HTTPException(status_code=500, detail=f"Error formatting rows: {e} , {(log.rows[0])}")

    try:
        # Use subprocess to apply the sed command on rows_data
        process = subprocess.run(
            ["sed", sed_command],
            input=rows_data,
            text=True,
            capture_output=True,
            check=True,
        )
        filtered_output = process.stdout

        return filtered_output

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error applying sed command: {e.stderr or str(e)}"
        )
    
# GET: get recent rows by log id
@router.get("/logs/{log_id}/recentrows", response_model=list[RowDTO])
def find_top_rows_by_log_id(log_id: int, db: Session = Depends(get_db)):
    log = db.query(Log).filter(Log.id == log_id).first()
    
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    
    # Query to get the recent 10 rows ordered by row id
    rows = db.query(Row).filter(Row.log_id == log_id) \
        .order_by(Row.id.desc()) \
        .limit(10) \
        .all()
    
    # Return rows directly
    return rows