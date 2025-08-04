from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import date, datetime, time
from decimal import Decimal

import crud
import models
import schemas
from database import get_db
from routers.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=schemas.Zeiteintrag, status_code=status.HTTP_201_CREATED)
def create_zeiteintrag_api(
    zeiteintrag_in: schemas.ZeiteintragCreate,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    # Set benutzer_id to current user if not provided or not authorized
    if not zeiteintrag_in.benutzer_id:
        zeiteintrag_in.benutzer_id = current_user.id
    elif current_user.id != zeiteintrag_in.benutzer_id and current_user.rolle.name.lower() not in ["administrator", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create time entry for another user")
    
    if zeiteintrag_in.projekt_id and not crud.get_projekt(db, zeiteintrag_in.projekt_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Projekt mit ID {zeiteintrag_in.projekt_id} nicht gefunden")
    if zeiteintrag_in.aufgabe_id and not crud.get_aufgabe(db, zeiteintrag_in.aufgabe_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Aufgabe mit ID {zeiteintrag_in.aufgabe_id} nicht gefunden")
    
    return crud.create_zeiteintrag(db=db, zeiteintrag=zeiteintrag_in, current_user_id=current_user.id)

@router.get("/", response_model=List[schemas.Zeiteintrag])
def read_zeiteintraege_api(
    skip: int = 0, limit: int = 100,
    benutzer_id: int | None = None,
    projekt_id: int | None = None,
    aufgabe_id: int | None = None,
    start_datum: date | None = None,
    end_datum: date | None = None,
    is_billable: bool | None = None,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    if current_user.rolle.name.lower() not in ["administrator", "manager"]:
        if benutzer_id is not None and benutzer_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view time entries for this user")
        benutzer_id_to_filter = benutzer_id if benutzer_id is not None else current_user.id
        
        # Add the is_billable filter
        if is_billable is not None:
            return [entry for entry in crud.get_zeiteintraege(
                db, skip=skip, limit=limit, benutzer_id=benutzer_id_to_filter, 
                projekt_id=projekt_id, aufgabe_id=aufgabe_id, 
                start_datum=start_datum, end_datum=end_datum
            ) if entry.ist_abrechenbar == is_billable]
        
        return crud.get_zeiteintraege(
            db, skip=skip, limit=limit, benutzer_id=benutzer_id_to_filter, 
            projekt_id=projekt_id, aufgabe_id=aufgabe_id, 
            start_datum=start_datum, end_datum=end_datum
        )
    
    # For admin/manager users - apply is_billable filter if provided
    if is_billable is not None:
        return [entry for entry in crud.get_zeiteintraege(
            db, skip=skip, limit=limit, benutzer_id=benutzer_id, 
            projekt_id=projekt_id, aufgabe_id=aufgabe_id, 
            start_datum=start_datum, end_datum=end_datum
        ) if entry.ist_abrechenbar == is_billable]
    
    return crud.get_zeiteintraege(
        db, skip=skip, limit=limit, benutzer_id=benutzer_id, 
        projekt_id=projekt_id, aufgabe_id=aufgabe_id, 
        start_datum=start_datum, end_datum=end_datum
    )

@router.get("/{zeiteintrag_id}", response_model=schemas.Zeiteintrag)
def read_zeiteintrag_api(
    zeiteintrag_id: int,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    db_ze = crud.get_zeiteintrag(db, zeiteintrag_id)
    if not db_ze:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zeiteintrag nicht gefunden")
    if current_user.id != db_ze.benutzer_id and current_user.rolle.name.lower() not in ["administrator", "manager"]:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this time entry")
    return db_ze

@router.put("/{zeiteintrag_id}", response_model=schemas.Zeiteintrag)
def update_zeiteintrag_api(
    zeiteintrag_id: int,
    zeiteintrag_update: schemas.ZeiteintragUpdate,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    db_ze = crud.get_zeiteintrag(db, zeiteintrag_id)
    if not db_ze:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zeiteintrag nicht gefunden")
    if current_user.id != db_ze.benutzer_id and current_user.rolle.name.lower() not in ["administrator", "manager"]:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this time entry")
    if zeiteintrag_update.projekt_id and zeiteintrag_update.projekt_id != db_ze.projekt_id and not crud.get_projekt(db, zeiteintrag_update.projekt_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Projekt mit ID {zeiteintrag_update.projekt_id} nicht gefunden")
    if zeiteintrag_update.aufgabe_id and zeiteintrag_update.aufgabe_id != db_ze.aufgabe_id and not crud.get_aufgabe(db, zeiteintrag_update.aufgabe_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Aufgabe mit ID {zeiteintrag_update.aufgabe_id} nicht gefunden")
    updated_ze = crud.update_zeiteintrag(db, zeiteintrag_id, zeiteintrag_update)
    if not updated_ze:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Update failed")
    return updated_ze

@router.delete("/{zeiteintrag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zeiteintrag_api(
    zeiteintrag_id: int,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    db_ze = crud.get_zeiteintrag(db, zeiteintrag_id)
    if not db_ze:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zeiteintrag nicht gefunden")
    if current_user.id != db_ze.benutzer_id and current_user.rolle.name.lower() not in ["administrator", "manager"]:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this time entry")
    crud.delete_zeiteintrag(db, zeiteintrag_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/report", response_model=Dict[str, Any])
def get_time_entries_report(
    start_date: date,
    end_date: date,
    user_id: int | None = None,
    hourly_rate: float = 100.0,  # Default hourly rate for earnings calculation
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    """
    Generate a time entries report with summary statistics and detailed entries.
    Admin/Manager users can get reports for any user by specifying user_id,
    or for all users if user_id is not provided.
    Regular users can only get reports for themselves.
    """
    # Check permission for user_id
    if current_user.rolle.name.lower() not in ["administrator", "manager"]:
        if user_id is not None and user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view time entries for this user"
            )
        # Set user_id to current user's ID for regular users
        user_id = current_user.id
    
    # Get all time entries matching the criteria
    time_entries = crud.get_zeiteintraege(
        db, 
        skip=0, 
        limit=1000,  # Use a reasonable limit 
        benutzer_id=user_id,
        start_datum=start_date,
        end_datum=end_date
    )
    
    if not time_entries:
        return {
            "total_hours": 0.0,
            "total_work_days": 0,
            "total_earnings": 0.0,
            "distinct_users_count": 0,
            "entries": []
        }
    
    # Calculate summary statistics
    total_hours = sum(float(entry.stunden) for entry in time_entries if entry.stunden is not None)
    
    # Count unique days worked
    unique_days = set(entry.datum for entry in time_entries)
    total_work_days = len(unique_days)
    
    # Calculate total earnings based on hours and hourly rate
    total_earnings = total_hours * hourly_rate
    
    # Count distinct users if needed (only relevant for admin/manager report without user_id)
    distinct_users = set(entry.benutzer_id for entry in time_entries)
    distinct_users_count = len(distinct_users)
    
    # Format entries for response
    formatted_entries = []
    for entry in time_entries:
        username = f"{entry.benutzer.vorname} {entry.benutzer.nachname}" if entry.benutzer else "Unknown"
        formatted_entries.append({
            "id": entry.id,
            "date": entry.datum,
            "user_id": entry.benutzer_id,
            "user_name": username,
            "project_id": entry.projekt_id,
            "project_name": entry.projekt.name if entry.projekt else "Unknown",
            "task_id": entry.aufgabe_id,
            "task_name": entry.aufgabe.name if entry.aufgabe else "Unknown",
            "start_time": entry.startzeit.strftime("%H:%M") if entry.startzeit else None,
            "end_time": entry.endzeit.strftime("%H:%M") if entry.endzeit else None,
            "duration_decimal": float(entry.stunden) if entry.stunden is not None else None,
            "description": entry.beschreibung,
            "is_billable": entry.ist_abrechenbar,
            "earnings": float(entry.stunden) * hourly_rate if entry.stunden is not None else 0.0
        })
    
    return {
        "total_hours": total_hours,
        "total_work_days": total_work_days,
        "total_earnings": total_earnings,
        "distinct_users_count": distinct_users_count,
        "entries": formatted_entries
    }
