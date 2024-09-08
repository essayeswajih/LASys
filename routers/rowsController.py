from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import rowEntity  # Assuming this contains your Row model
from db.database import get_db
from schemas.rowDTO import RowDTO

router = APIRouter()

# GET: Fetch all rows
@router.get("/rows", response_model=List[RowDTO])
def read_rows(db: Session = Depends(get_db)):
    rows = db.query(rowEntity.Row).all()
    return rows

# GET: Find rows by log_id
@router.get("/rows/log/{log_id}", response_model=List[RowDTO])
def find_rows_by_log_id(log_id: int, db: Session = Depends(get_db)):
    rows = db.query(rowEntity.Row).filter(rowEntity.Row.log_id == log_id).all()
    
    if not rows:
        raise HTTPException(status_code=404, detail="No rows found for the specified log ID")
    
    return rows

# POST: Create a new row
@router.post("/rows", response_model=RowDTO)
async def create_row(row: RowDTO, db: Session = Depends(get_db)):
    db_row = rowEntity.Row(
        ip=row.ip,
        url=row.url,
        dateTime=datetime.fromisoformat(row.dateTime),  # Correcting the dateTime conversion
        method=row.method,
        status=row.status,
        referer=row.referer,
        user_agent=row.user_agent,
        log_id=row.log_id  # Make sure log_id exists in the RowDTO schema
    )

    db.add(db_row)
    db.commit()
    db.refresh(db_row)

    return db_row

# DELETE: Delete a row by ID
@router.delete("/rows/{row_id}", response_model=RowDTO)
def delete_row(row_id: int, db: Session = Depends(get_db)):

    db_row = db.query(rowEntity.Row).filter(rowEntity.Row.id == row_id).first()
    
    if db_row is None:
        raise HTTPException(status_code=404, detail="Row not found")
    
    db.delete(db_row)
    db.commit()
    
    return db_row