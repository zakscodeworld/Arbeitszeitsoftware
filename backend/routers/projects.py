from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import Response # Add Response import

import crud
import models
import schemas
from database import get_db
from .auth import admin_required, get_current_active_user # Import dependencies

router = APIRouter(
    tags=["projects"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Projekt, status_code=status.HTTP_201_CREATED)
def create_project_api(
    project_in: schemas.ProjektCreate, 
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user) # Or admin_required if only admins can create
):
    """
    Create a new project.
    Accessible by authenticated users (or admins/managers depending on policy).
    """
    # Add authorization logic if needed, e.g., only managers/admins can create projects.
    # For now, any authenticated user can create a project.
    return crud.create_projekt(db=db, projekt=project_in)

@router.get("/", response_model=List[schemas.Projekt])
def read_projects_api(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user) # All authenticated users can see projects
):
    """
    Retrieve a list of projects.
    """
    projects = crud.get_projekte(db, skip=skip, limit=limit)
    return projects

@router.get("/{project_id}", response_model=schemas.Projekt)
def read_project_api(
    project_id: int, 
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    """
    Retrieve a specific project by ID.
    """
    db_project = crud.get_projekt(db, projekt_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projekt nicht gefunden")
    return db_project

@router.put("/{project_id}", response_model=schemas.Projekt)
def update_project_api(
    project_id: int, 
    project_update: schemas.ProjektUpdate, 
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user) # Changed from admin_required
):
    """
    Update a project. Any authenticated user can update projects.
    """
    db_project = crud.update_projekt(db, projekt_id=project_id, projekt_update=project_update)
    if db_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projekt nicht gefunden")
    return db_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_api(
    project_id: int, 
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user) # Jeder authentifizierte Benutzer kann Projekte löschen
):
    """
    Delete a project. Authenticated access required.
    """
    # Before deleting a project, consider if related entities (tasks, time entries) should also be handled (e.g., deleted or disassociated)
    # This might require cascading deletes in the DB or explicit deletion logic here.
    # For now, we assume the CRUD operation handles direct deletion or the DB handles cascades.
    
    db_project = crud.get_projekt(db, projekt_id=project_id) # Check if project exists
    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projekt nicht gefunden")

    success = crud.delete_projekt(db, projekt_id=project_id)
    if not success:
        # This condition might be hard to reach if get_projekt already confirmed existence
        # and delete_projekt raises an error for other reasons or if the DB constraint prevents deletion.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Projekt konnte nicht gelöscht werden (evtl. بسبب Abhängigkeiten)")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
