from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import date

import crud
import models
import schemas
from database import get_db
from routers.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=schemas.Abwesenheit, status_code=status.HTTP_201_CREATED)
def create_abwesenheit_api(
    abwesenheit_in: schemas.AbwesenheitCreate,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    # Set benutzer_id to current user if not provided
    if not abwesenheit_in.benutzer_id:
        abwesenheit_in.benutzer_id = current_user.id
    elif current_user.id != abwesenheit_in.benutzer_id and current_user.rolle.name.lower() not in ["administrator", "manager"]:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create absence for another user")
    
    if not crud.get_abwesenheit_typ(db, abwesenheit_in.abwesenheit_typ_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AbwesenheitTyp mit ID {abwesenheit_in.abwesenheit_typ_id} nicht gefunden")
    
    return crud.create_abwesenheit(db=db, abwesenheit=abwesenheit_in, beantragt_von_benutzer_id=current_user.id)

@router.get("/", response_model=List[schemas.Abwesenheit])
def read_abwesenheiten_api(
    skip: int = 0, limit: int = 100,
    benutzer_id: int | None = None,
    abwesenheit_typ_id: int | None = None,
    status_filter: str | None = None,
    start_datum: date | None = None,
    end_datum: date | None = None,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    if current_user.rolle.name.lower() not in ["administrator", "manager"]:
        if benutzer_id is not None and benutzer_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view absences for this user")
        benutzer_id_to_filter = benutzer_id if benutzer_id is not None else current_user.id
        return crud.get_abwesenheiten(db, skip=skip, limit=limit, benutzer_id=benutzer_id_to_filter, abwesenheit_typ_id=abwesenheit_typ_id, status=status_filter, start_datum=start_datum, end_datum=end_datum)
    
    return crud.get_abwesenheiten(db, skip=skip, limit=limit, benutzer_id=benutzer_id, abwesenheit_typ_id=abwesenheit_typ_id, status=status_filter, start_datum=start_datum, end_datum=end_datum)

@router.get("/{abwesenheit_id}", response_model=schemas.Abwesenheit)
def read_abwesenheit_api(
    abwesenheit_id: int,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    db_ab = crud.get_abwesenheit(db, abwesenheit_id)
    if not db_ab:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Abwesenheit nicht gefunden")
    if current_user.id != db_ab.benutzer_id and current_user.rolle.name.lower() not in ["administrator", "manager"]:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this absence")
    return db_ab

@router.put("/{abwesenheit_id}", response_model=schemas.Abwesenheit)
def update_abwesenheit_api(
    abwesenheit_id: int,
    abwesenheit_update: schemas.AbwesenheitUpdate,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    db_ab = crud.get_abwesenheit(db, abwesenheit_id)
    if not db_ab:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Abwesenheit nicht gefunden")

    is_owner = current_user.id == db_ab.benutzer_id
    is_manager_or_admin = current_user.rolle.name.lower() in ["administrator", "manager"]
    genehmiger_id_to_pass = None

    if not is_owner and not is_manager_or_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this absence")

    if is_owner and not is_manager_or_admin:
        if db_ab.status != 'beantragt':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Absence can only be updated by owner if status is 'beantragt'")
        if abwesenheit_update.status is not None and abwesenheit_update.status != db_ab.status:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner cannot change absence status.")
        if abwesenheit_update.kommentar_genehmiger is not None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner cannot set approver comment.")
        if abwesenheit_update.genehmigt_von_benutzer_id is not None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner cannot set approver.")
            
    if is_manager_or_admin:
        if abwesenheit_update.status in ['genehmigt', 'abgelehnt'] and abwesenheit_update.status != db_ab.status:
            genehmiger_id_to_pass = current_user.id

    if abwesenheit_update.abwesenheit_typ_id and abwesenheit_update.abwesenheit_typ_id != db_ab.abwesenheit_typ_id and not crud.get_abwesenheit_typ(db, abwesenheit_update.abwesenheit_typ_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AbwesenheitTyp mit ID {abwesenheit_update.abwesenheit_typ_id} nicht gefunden")

    updated_ab = crud.update_abwesenheit(db, abwesenheit_id=abwesenheit_id, abwesenheit_update=abwesenheit_update, genehmiger_id=genehmiger_id_to_pass)
    if not updated_ab:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Update failed")
    return updated_ab

@router.delete("/{abwesenheit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_abwesenheit_api(
    abwesenheit_id: int,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    db_ab = crud.get_abwesenheit(db, abwesenheit_id)
    if not db_ab:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Abwesenheit nicht gefunden")
    
    is_owner = current_user.id == db_ab.benutzer_id
    is_admin = current_user.rolle.name.lower() == "administrator"

    if not is_owner and not is_admin:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this absence")
    
    if is_owner and not is_admin and db_ab.status != 'beantragt': # Corrected: allow deletion of 'abgelehnt' by owner too
        if db_ab.status != 'abgelehnt':
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Absence can only be deleted by owner if status is 'beantragt' or 'abgelehnt'")

    crud.delete_abwesenheit(db, abwesenheit_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
