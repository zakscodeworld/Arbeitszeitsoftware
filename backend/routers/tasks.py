from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import get_db
from .auth import get_current_active_user, admin_required

router = APIRouter(
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Aufgabe, status_code=status.HTTP_201_CREATED)
def create_task_api(
    task_in: schemas.AufgabeCreate,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    """
    Create a new task.
    Policy: Authenticated users can create tasks.
    Consider if task creation should be restricted (e.g., to project members or managers).
    """
    # Example: Link task to a project, ensure project exists
    # db_project = crud.get_projekt(db, projekt_id=task_in.projekt_id)
    # if not db_project:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Projekt mit ID {task_in.projekt_id} nicht gefunden")
    
    # Add authorization: e.g., if only project managers or assigned users can add tasks to a project.
    return crud.create_aufgabe(db=db, aufgabe=task_in)

@router.get("/", response_model=List[schemas.Aufgabe])
def read_tasks_api(
    skip: int = 0,
    limit: int = 100,
    projekt_id: int | None = None, # Optional filter by project
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    """
    Retrieve a list of tasks.
    Optionally filters by projekt_id.
    Policy: Authenticated users can see tasks.
    Consider restricting visibility based on project membership or user assignment.
    """
    if projekt_id:
        # Ensure project exists and user has access if necessary
        # db_project = crud.get_projekt(db, projekt_id=projekt_id)
        # if not db_project:
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Projekt mit ID {projekt_id} nicht gefunden")
        tasks = crud.get_aufgaben_by_projekt(db, projekt_id=projekt_id, skip=skip, limit=limit)
    else:
        tasks = crud.get_aufgaben(db, skip=skip, limit=limit)
    return tasks

@router.get("/{task_id}", response_model=schemas.Aufgabe)
def read_task_api(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    """
    Retrieve a specific task by ID.
    Policy: Authenticated users can see task details.
    Consider restricting visibility.
    """
    db_task = crud.get_aufgabe(db, aufgabe_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aufgabe nicht gefunden")
    # Add authorization: e.g., check if user is assigned to the task or is a project manager.
    return db_task

@router.put("/{task_id}", response_model=schemas.Aufgabe)
def update_task_api(
    task_id: int,
    task_update: schemas.AufgabeUpdate,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    """
    Update a task.
    Policy: Authenticated users who are assigned or are managers/admins.
    """
    db_task = crud.get_aufgabe(db, aufgabe_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aufgabe nicht gefunden")
    
    # Add authorization logic here:
    # Example: if current_user.id != db_task.zugewiesen_an_benutzer_id and not is_manager_or_admin(current_user):
    #    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this task")
        
    updated_task = crud.update_aufgabe(db, aufgabe_id=task_id, aufgabe_update=task_update)
    if updated_task is None: # Should not happen if db_task was found, but good practice
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aufgabe nach Update nicht gefunden")
    return updated_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_api(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    """
    Delete a task.
    Policy: Authenticated users can delete tasks.
    """
    db_task = crud.get_aufgabe(db, aufgabe_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aufgabe nicht gefunden")

    # Add specific authorization if needed before calling delete
    
    success = crud.delete_aufgabe(db, aufgabe_id=task_id)
    if not success:
        # This case might be redundant if get_aufgabe already confirmed existence
        # and delete_aufgabe itself doesn't return a boolean indicating success of deletion vs. not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aufgabe nicht gefunden oder konnte nicht gelöscht werden")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
