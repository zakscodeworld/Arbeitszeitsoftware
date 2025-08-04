\
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import get_db
from .auth import admin_required, get_current_active_user

router = APIRouter(
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# Moved /me routes before /{user_id} routes to avoid path parameter conflicts

@router.get("/me", response_model=schemas.Benutzer)
def read_current_user_api(
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    """
    Get the current logged-in user.
    """
    return current_user

@router.put("/me", response_model=schemas.Benutzer)
def update_current_user_api(
    user_update: schemas.BenutzerUpdate,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    """
    Update the current logged-in user's details.
    """
    # Check for email uniqueness if email is being updated
    if user_update.email and user_update.email != current_user.email:
        existing_user = crud.get_benutzer_by_email(db, email=user_update.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Die E-Mail-Adresse '{user_update.email}' wird bereits von einem anderen Benutzer verwendet."
            )
    
    # Check for username uniqueness if username is being updated
    if user_update.username and user_update.username != current_user.username:
        existing_user = crud.get_benutzer_by_username(db, username=user_update.username)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Der Benutzername '{user_update.username}' wird bereits von einem anderen Benutzer verwendet."
            )
    
    return crud.update_benutzer(db, benutzer_id=current_user.id, benutzer_update=user_update)

@router.patch("/me", response_model=schemas.Benutzer)
def patch_current_user_api(
    user_update: schemas.BenutzerUpdate,
    db: Session = Depends(get_db),
    current_user: models.Benutzer = Depends(get_current_active_user)
):
    """
    Update the current logged-in user's details with partial data (PATCH).
    """
    # Check for email uniqueness if email is being updated
    if user_update.email and user_update.email != current_user.email:
        existing_user = crud.get_benutzer_by_email(db, email=user_update.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Die E-Mail-Adresse '{user_update.email}' wird bereits von einem anderen Benutzer verwendet."
            )
    
    # Check for username uniqueness if username is being updated
    if user_update.username and user_update.username != current_user.username:
        existing_user = crud.get_benutzer_by_username(db, username=user_update.username)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Der Benutzername '{user_update.username}' wird bereits von einem anderen Benutzer verwendet."
            )
    
    return crud.update_benutzer(db, benutzer_id=current_user.id, benutzer_update=user_update)

@router.post("/me/preferences", response_model=dict)
def update_user_preferences(
    preferences: dict,
    current_user: models.Benutzer = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user preferences.
    """
    # Store preferences in user's metadata or a dedicated preferences table
    # This is a simplified implementation that just returns the preferences
    return preferences

# Admin and specific user routes

@router.get("/", response_model=List[schemas.Benutzer])
def read_users_api(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_admin: models.Benutzer = Depends(admin_required)
):
    """
    Retrieve a list of users. Admin access required.
    """
    users = crud.get_benutzer_list(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=schemas.Benutzer)
def read_user_api(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_admin: models.Benutzer = Depends(admin_required)
):
    """
    Retrieve a specific user by ID. Admin access required.
    """
    db_user = crud.get_benutzer(db, benutzer_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benutzer nicht gefunden")
    return db_user

@router.put("/{user_id}", response_model=schemas.Benutzer)
def update_user_api(
    user_id: int, 
    user_update: schemas.BenutzerUpdate, 
    db: Session = Depends(get_db), 
    current_admin: models.Benutzer = Depends(admin_required)
):
    """
    Update a user's details. Admin access required.
    Password updates should be handled carefully; this schema might allow password changes.
    """
    # Check if user exists
    db_user = crud.get_benutzer(db, benutzer_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benutzer nicht gefunden")
    
    # Check for email uniqueness if email is being updated
    if user_update.email and user_update.email != db_user.email:
        existing_user = crud.get_benutzer_by_email(db, email=user_update.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Die E-Mail-Adresse '{user_update.email}' wird bereits von einem anderen Benutzer verwendet."
            )
    
    # Check for username uniqueness if username is being updated
    if user_update.username and user_update.username != db_user.username:
        existing_user = crud.get_benutzer_by_username(db, username=user_update.username)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Der Benutzername '{user_update.username}' wird bereits von einem anderen Benutzer verwendet."
            )
    
    # Update user
    db_user = crud.update_benutzer(db, benutzer_id=user_id, benutzer_update=user_update)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_api(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_admin: models.Benutzer = Depends(admin_required)
):
    """
    Delete a user. Admin access required.
    """
    success = crud.delete_benutzer(db, benutzer_id=user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benutzer nicht gefunden oder konnte nicht gelöscht werden")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{user_id}/password", response_model=dict)
def update_user_password(
    user_id: int,
    password_data: schemas.PasswordUpdate,
    current_user: models.Benutzer = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user password"""
    # Verify that the user is updating their own password or is an admin
    if current_user.id != user_id and current_user.rolle_id != 1:  # 1 = Admin
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sie können nur Ihr eigenes Passwort ändern"
        )
    
    # Verify current password
    if not crud.verify_password(password_data.current_password, current_user.passwort_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Das aktuelle Passwort ist nicht korrekt"
        )
    
    # Update password
    updated_user = crud.update_password(db, user_id, password_data.new_password)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benutzer nicht gefunden"
        )
    
    return {"message": "Passwort erfolgreich aktualisiert"}
