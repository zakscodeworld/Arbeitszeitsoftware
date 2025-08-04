from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import get_db
from routers.auth import get_current_active_user, admin_required

router = APIRouter()

@router.post("/", response_model=schemas.AbwesenheitTyp, status_code=status.HTTP_201_CREATED)
def create_absence_type_api(
    absence_type_in: schemas.AbwesenheitTypCreate,
    db: Session = Depends(get_db),
    current_admin: models.Benutzer = Depends(admin_required)
):
    return crud.create_abwesenheit_typ(db=db, abwesenheit_typ=absence_type_in)

@router.get("/", response_model=List[schemas.AbwesenheitTyp])
def read_absence_types_api(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user) # Allow all users to read absence types
):
    return crud.get_abwesenheit_typen(db, skip=skip, limit=limit)

@router.get("/{absence_type_id}", response_model=schemas.AbwesenheitTyp)
def read_absence_type_api(
    absence_type_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Benutzer = Depends(admin_required)
):
    db_type = crud.get_abwesenheit_typ(db, abwesenheit_typ_id=absence_type_id)
    if not db_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AbwesenheitTyp nicht gefunden")
    return db_type

@router.put("/{absence_type_id}", response_model=schemas.AbwesenheitTyp)
def update_absence_type_api(
    absence_type_id: int,
    absence_type_update: schemas.AbwesenheitTypUpdate,
    db: Session = Depends(get_db),
    current_admin: models.Benutzer = Depends(admin_required)
):
    updated_type = crud.update_abwesenheit_typ(db, abwesenheit_typ_id=absence_type_id, abwesenheit_typ_update=absence_type_update)
    if not updated_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AbwesenheitTyp nicht gefunden oder Update fehlgeschlagen")
    return updated_type

@router.delete("/{absence_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_absence_type_api(
    absence_type_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Benutzer = Depends(admin_required)
):
    # Optional: Add check if type is in use by any Abwesenheit using a CRUD function
    # e.g., if crud.is_abwesenheit_typ_in_use(db, absence_type_id):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="AbwesenheitTyp wird noch verwendet.")
    success = crud.delete_abwesenheit_typ(db, abwesenheit_typ_id=absence_type_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AbwesenheitTyp nicht gefunden oder konnte nicht gelöscht werden")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
