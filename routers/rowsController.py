from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.rowEntity import Row   # Assuming this contains your Row model
from db.database import get_db
from schemas.rowDTO import RowDTO , RowCreate

router = APIRouter()

# GET: Fetch all rows
@router.get("/rows", response_model=List[RowDTO])
def read_rows(db: Session = Depends(get_db)):
    try:
        rows = db.query(Row).all()
        return rows
    except :
        raise HTTPException(status_code=404, detail="No rows found")  # Changed to

# GET: Find rows by log_id
@router.get("/rows/log/{log_id}", response_model=List[RowDTO])
def find_rows_by_log_id(log_id: int, db: Session = Depends(get_db)):

    rows = db.query(Row).filter(Row.log_id == log_id).all()
    if not rows:
        raise HTTPException(status_code=404, detail="No rows found for the specified log ID")
    return rows

# POST: Create a new row
@router.post("/rows", response_model=RowDTO)
async def create_row(row: RowCreate, db: Session = Depends(get_db)):
    try :
        db_row = Row(
            ip=row.ip,
            url=row.url,
            timestamp=row.timestamp,  # Correcting the dateTime conversion
            method=row.method,
            status=row.status,
            referer=row.referer,
            user_agent=row.user_agent,
            response_size=row.response_size,
            log_id=row.log_id  # Make sure log_id exists in the RowDTO schema
        )

        db.add(db_row)
        db.commit()
        db.refresh(db_row)

        return RowDTO(
            ip=db_row.ip,
            url=db_row.url,
            timestamp=db_row.timestamp,  # Ensure datetime is returned as ISO string
            method=db_row.method,
            status=db_row.status,
            response_size=db_row.response_size,
            referer=db_row.referer,
            user_agent=db_row.user_agent,
            log_id=db_row.log_id
        )
    except Exception as e:
        db.rollback()  # Ensure to rollback the transaction if an error occurs
        print(f"Error occurred: {e}")  # Log the exception for debugging
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating the log"
        )

# POST: Create All Rows
@router.post("/rows/all", response_model=List[RowDTO])
async def create_rows(rows: List[RowDTO], db: Session = Depends(get_db)):
    created_rows = []
    
    for row in rows:
        db_row = Row(
            ip=row.ip,
            url=row.url,
            timestamp=row.timestamp,
            method=row.method,
            status=row.status,
            response_size=row.response_size,
            referer=row.referer,
            user_agent=row.user_agent,
            log_id=row.log_id
        )
        db.add(db_row)
        created_rows.append(db_row)

    db.commit()

    # Refresh each row to ensure the latest state is reflected
    for row in created_rows:
        db.refresh(row)
    
    return created_rows
        
# DELETE: Delete a row by ID
@router.delete("/rows/{row_id}", response_model=RowDTO)
def delete_row(row_id: int, db: Session = Depends(get_db)):

    db_row = db.query(Row).filter(Row.id == row_id).first()
    
    if db_row is None:
        raise HTTPException(status_code=404, detail="Row not found")
    
    db.delete(db_row)
    db.commit()
    
    return db_row