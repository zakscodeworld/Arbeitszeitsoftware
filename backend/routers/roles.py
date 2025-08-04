\
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import get_db
from .auth import admin_required, admin_or_manager_required # Import both dependencies from auth.py

router = APIRouter(
    tags=["roles"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Rolle, status_code=status.HTTP_201_CREATED)
def create_role_api(
    role_in: schemas.RolleCreate, 
    db: Session = Depends(get_db),
    current_admin: models.Benutzer = Depends(admin_required)
):
    """
    Create a new role. Admin access required.
    """
    # Check if role already exists by name
    db_role = crud.get_rolle_by_name(db, name=role_in.name)
    if db_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Rolle mit Namen '{role_in.name}' existiert bereits")
    return crud.create_rolle(db=db, rolle=role_in)

@router.get("/", response_model=List[schemas.Rolle])
def read_roles_api(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_admin: models.Benutzer = Depends(admin_or_manager_required) # Allow both admin and manager
):
    """
    Retrieve a list of roles. Admin or Manager access required.
    """
    roles = crud.get_rollen(db, skip=skip, limit=limit)
    return roles

@router.get("/{role_id}", response_model=schemas.Rolle)
def read_role_api(
    role_id: int, 
    db: Session = Depends(get_db),
    current_admin: models.Benutzer = Depends(admin_or_manager_required) # Allow both admin and manager
):
    """
    Retrieve a specific role by ID. Admin or Manager access required.
    """
    db_role = crud.get_rolle(db, rolle_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rolle nicht gefunden")
    return db_role

@router.put("/{role_id}", response_model=schemas.Rolle)
def update_role_api(
    role_id: int, 
    role_update: schemas.RolleUpdate, 
    db: Session = Depends(get_db),
    current_admin: models.Benutzer = Depends(admin_required)
):
    """
    Update a role's details. Admin access required.
    Be cautious if changing role names, especially for critical roles like 'Administrator'.
    """
    db_role = crud.update_rolle(db, rolle_id=role_id, rolle_update=role_update)
    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rolle nicht gefunden")
    return db_role

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role_api(
    role_id: int, 
    db: Session = Depends(get_db),
    current_admin: models.Benutzer = Depends(admin_required)
):
    """
    Delete a role. Admin access required.
    Consider implications: what happens to users with this role?
    Prevent deletion of essential roles (e.g., 'Administrator').
    """
    db_role = crud.get_rolle(db, rolle_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rolle nicht gefunden")
    
    # Prevent deletion of critical roles
    if db_role.name.lower() == "administrator":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Die Administrator-Rolle kann nicht gelöscht werden.")

    # Check if any user is currently assigned this role
    users_with_role = crud.get_benutzer_by_rolle_id(db, rolle_id=role_id)
    if users_with_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Rolle kann nicht gelöscht werden, da sie noch {len(users_with_role)} Benutzern zugewiesen ist.")

    success = crud.delete_rolle(db, rolle_id=role_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rolle nicht gefunden oder konnte nicht gelöscht werden")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
