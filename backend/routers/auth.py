from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os

import crud
import schemas
import models
from database import get_db 

from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_in_env") 
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/auth", 
    tags=["authentication"] 
)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(schemas.oauth2_scheme), db: Session = Depends(get_db)) -> models.Benutzer:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_benutzer_by_username(db, username=username)
    if user is None:
        raise credentials_exception
        
    # Make sure role information is loaded
    if user.rolle is None:
        user.rolle = crud.get_rolle(db, rolle_id=user.rolle_id)
        if user.rolle is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                              detail="User role not found")
    return user

async def get_current_active_user(current_user: models.Benutzer = Depends(get_current_user)) -> models.Benutzer:
    if not current_user.ist_aktiv:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Dependency for admin-only routes
def admin_required(current_user: models.Benutzer = Depends(get_current_active_user)):
    is_admin = (current_user.rolle and current_user.rolle.name.lower() == "administrator") or \
               (current_user.rolle and current_user.rolle.id == 1)
    if not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator privileges required")
    return current_user

# Dependency for routes that require admin or manager privileges
def admin_or_manager_required(current_user: models.Benutzer = Depends(get_current_active_user)):
    is_admin = (current_user.rolle and current_user.rolle.name.lower() == "administrator") or \
               (current_user.rolle and current_user.rolle.id == 1)
    is_manager = (current_user.rolle and current_user.rolle.name.lower() == "manager") or \
                 (current_user.rolle and current_user.rolle.id == 2)
    
    if not (is_admin or is_manager):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator or Manager privileges required")
    return current_user

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_benutzer_by_username(db, username=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.passwort_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.Benutzer)
async def read_users_me(current_user: models.Benutzer = Depends(get_current_active_user)):
    return current_user

@router.post("/register", response_model=schemas.Benutzer)
def register_user(user_in: schemas.BenutzerCreate, db: Session = Depends(get_db)):
    db_user = crud.get_benutzer_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user_email = crud.get_benutzer_by_email(db, email=user_in.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    rolle = crud.get_rolle(db, rolle_id=user_in.rolle_id)
    if not rolle:
        raise HTTPException(status_code=400, detail=f"Rolle with id {user_in.rolle_id} not found.")

    return crud.create_benutzer(db=db, benutzer=user_in)

@router.post("/verify-password")
async def verify_current_password(
    password_data: schemas.PasswordVerify,
    current_user: models.Benutzer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify if the provided password matches the current user's password"""
    is_valid = crud.verify_password(password_data.password, current_user.passwort_hash)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    return {"valid": True}