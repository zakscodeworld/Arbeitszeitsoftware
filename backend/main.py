from typing import List
from fastapi import FastAPI, Depends, Form, HTTPException, Request, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exception_handlers import HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
import os

# Load environment variables from .env file if present
from dotenv import load_dotenv
load_dotenv()

# Set up email configuration with known working values
email_config = {
    'SMTP_SERVER': 'smtp.strato.de',
    'SMTP_PORT': '465',
    'SMTP_USERNAME': 'webmaster@zaksprojects.de',
    'SMTP_PASSWORD': 'Zaka123123!!',
    'SENDER_EMAIL': 'webmaster@zaksprojects.de',    'SENDER_NAME': 'BBQ GmbH Zeiterfassung',
    'APP_URL': 'https://zeiterfassung.zaksprojects.de',  # Default URL
    'DISABLE_EMAIL_SENDING': 'False',
    'ENVIRONMENT': 'production',
    'EMAIL_LOG_LEVEL': 'DEBUG'
}

# Update environment with email configuration
os.environ.update(email_config)

from database import engine, get_db, Base
import models
import crud
import schemas
from routers.auth import router as auth_router, get_current_active_user
from routers import users as users_router
from routers import projects as projects_router
from routers import tasks as tasks_router
from routers import roles as roles_router
from routers import time_entries as time_entries_router
from routers import absences as absences_router
from routers import absence_types as absence_types_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Zeiterfassungstool API")

# Static files and templates - Ensure templates is defined before use in routes
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates") # Definition of templates

# Include new routers
app.include_router(auth_router) # Handles /auth/token, /auth/register
app.include_router(users_router.router, prefix="/api/v1/users", tags=["Users"]) 
# Add a legacy route for users to support existing frontend code
app.include_router(users_router.router, prefix="/users", tags=["Users Legacy"])
app.include_router(projects_router.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(tasks_router.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(roles_router.router, prefix="/api/v1/roles", tags=["Roles"])
app.include_router(time_entries_router.router, prefix="/api/v1/time-entries", tags=["Time Entries"])
# Add an alias route for time_entries to support legacy code
app.include_router(time_entries_router.router, prefix="/api/v1/time_entries", tags=["Time Entries"])
app.include_router(absences_router.router, prefix="/api/v1/absences", tags=["Absences"])
app.include_router(absence_types_router.router, prefix="/api/v1/absence-types", tags=["Absence Types"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    # Apply database migrations
    try:
        import os
        from apply_migration import apply_migration
        print("Starting to apply database migrations...")
        if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")):
            os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations"), exist_ok=True)
        apply_migration()
        print("Database migrations applied successfully!")
    except Exception as e:
        print(f"Error applying database migrations: {str(e)}")
        import traceback
        traceback.print_exc()
      # Initialize database connection
    try:
        print("Application startup: Database tables (based on new models.py) should be created if they didn't exist.")
        print("Attempting to create initial data (roles, absence types, admin user)...")
        db = next(get_db())
        crud.create_initial_data(db)
        db.close()
        print("Initial data creation process completed.")
    except Exception as e:
        print(f"Error during initial data creation: {e}")
        import traceback
        traceback.print_exc()
        if db is not None:
            db.close()

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/login")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request, 
    db: Session = Depends(get_db),
):
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
        }
    )

# ---------- HTML‐Seiten (Login, Register, Passwort, Hilfe, specific dashboards) ----------
# These remain as direct HTML serving routes. 
# Their POST counterparts for form submission are being phased out or modified to guide towards API usage.

@app.get("/arbeitszeiten/dashboard", response_class=HTMLResponse)
def az_dashboard(request: Request, db: Session = Depends(get_db)):
    # This page will need to fetch data via JS from the new API endpoints
    # For now, it might show stale or no data if crud.get_arbeitszeiten is removed/changed
    # az_list = crud.get_arbeitszeiten(db) # This was for the old direct DB access
    return templates.TemplateResponse(
        "arbeitszeiten.html",
        {"request": request, "arbeitszeiten": [], "error": None} # Pass empty list for now
    )

@app.post("/arbeitszeiten/dashboard", response_class=HTMLResponse)
def az_add(
    request: Request,
    benutzer_id: int    = Form(...),
    datum: date         = Form(...),
    startzeit: str      = Form(...),
    endzeit: str        = Form(None),
    kommentar: str      = Form(None),
    db: Session         = Depends(get_db),
):
    # This form submission should be replaced by a JS call to POST /api/v1/time-entries/
    # try:
    #     az_in = schemas.ArbeitszeitCreate(...) # Old schema
    #     crud.create_arbeitszeit(db, az_in) # Old direct DB access
    #     return RedirectResponse(url="/arbeitszeiten/dashboard", status_code=302)
    # except Exception as e:
    #     return templates.TemplateResponse(
    #         "arbeitszeiten.html",
    #         {"request": request, "arbeitszeiten": [], "error": str(e)}
    #     )
    return templates.TemplateResponse(
        "arbeitszeiten.html",
        {"request": request, "arbeitszeiten": [], "error": "Submitting time entries via this form is deprecated. Please use the API."}
    )

@app.get("/urlaube/dashboard", response_class=HTMLResponse)
def urlaub_dashboard(request: Request, db: Session = Depends(get_db)):
    # This page will need to fetch data via JS from the new API endpoints
    # urlaube = crud.get_urlaube(db) # Old direct DB access
    return templates.TemplateResponse(
        "urlaub.html",
        {"request": request, "urlaube": []} # Pass empty list for now
    )

@app.get("/urlaube/genehmigen", response_class=HTMLResponse)
def urlaub_genehmigen_dashboard(request: Request, db: Session = Depends(get_db)):
    # Diese Seite dient zur Verwaltung der Urlaubsanträge durch Administratoren und Manager
    return templates.TemplateResponse(
        "urlaub_genehmigen.html",
        {"request": request}
    )

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("Login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    nutzername: str = Form(...),
    passwort: str    = Form(...),
    db: Session      = Depends(get_db),
):
    return templates.TemplateResponse(
        "Login.html",
        {"request": request, "error": "Login via this form is deprecated. Please use API endpoint /auth/token."}
    )

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request, db: Session = Depends(get_db)):
    rollen = crud.get_rollen(db) # Changed from crud.get_rollen_list(db)
    return templates.TemplateResponse("register.html", {
        "request": request, "rollen": rollen, "error": None
    })

@app.post("/register", response_class=HTMLResponse)
def register_submit(
     request: Request,
     nutzername: str  = Form(...),
     vorname: str     = Form(...),
     nachname: str    = Form(...),
     email: str       = Form(...),
     passwort: str    = Form(...),
     rolle_id: int    = Form(...),
     db: Session      = Depends(get_db),
 ):
    rollen = crud.get_rollen(db)
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "rollen": rollen, "error": "Registration via this form is deprecated. Please use API endpoint /auth/register."}
    )

@app.get("/hilfe", response_class=HTMLResponse)
def hilfe_page(request: Request):
    return templates.TemplateResponse("hilfe.html", {"request": request})

@app.get("/passwort", response_class=HTMLResponse)
def passwort_form(request: Request):
    return templates.TemplateResponse("passwort.html", {"request": request, "message": None})

@app.post("/passwort", response_class=HTMLResponse)
def passwort_submit(
    request: Request,
    neues_passwort: str = Form(...),
    db: Session         = Depends(get_db),
):
    return templates.TemplateResponse(
        "passwort.html",
        {"request": request, "message": "Passwort ändern via Form ist veraltet. Bitte API nutzen."}
    )

# --- dependency: nur für Admins (used by /rollen/dashboard HTML page) ---
def admin_required(current_user: models.Benutzer = Depends(get_current_active_user)):
    if not current_user.rolle or current_user.rolle.name.lower() != "administrator":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Zugriff nur für Administratoren")
    return current_user

# ---------- Rollen‐Verwaltung (HTML Admin Page) ----------
# This HTML part for roles management can remain here for the admin UI.
# The POST handler now checks for existing role name before creation.
@app.get("/rollen/dashboard", response_class=HTMLResponse)
def rollen_dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
    current_admin: models.Benutzer = Depends(admin_required)
):
    rollen = crud.get_rollen(db)
    return templates.TemplateResponse(
        "rollen.html",
        {"request": request, "rollen": rollen, "error": None, "current_user": current_admin}
    )

@app.post("/rollen/dashboard", response_class=HTMLResponse)
def rollen_add_form(
    request: Request,
    name: str = Form(...), 
    beschreibung: str = Form(None),
    db: Session = Depends(get_db),
    current_admin: models.Benutzer = Depends(admin_required)
):
    rollen = crud.get_rollen(db) # Get roles for template context in case of error
    db_role = crud.get_rolle_by_name(db, name=name)
    if db_role:
        return templates.TemplateResponse(
            "rollen.html",
            {"request": request, "rollen": rollen, "error": f"Rolle '{name}' existiert bereits.", "current_user": current_admin}
        )
    try:
        rolle_in = schemas.RolleCreate(name=name, beschreibung=beschreibung)
        crud.create_rolle(db=db, rolle=rolle_in)
        return RedirectResponse(url="/rollen/dashboard", status_code=status.HTTP_302_FOUND)
    except Exception as e: # Catch any other unexpected error during creation
        return templates.TemplateResponse(
            "rollen.html",
            {"request": request, "rollen": rollen, "error": str(e), "current_user": current_admin}
        )

# ---------- Direct HTML file routes ----------
# These routes serve HTML files directly at paths like /arbeitszeiten.html
@app.get("/arbeitszeiten.html", response_class=HTMLResponse)
def arbeitszeiten_html(request: Request):
    return templates.TemplateResponse("arbeitszeiten.html", {"request": request})

@app.get("/urlaub.html", response_class=HTMLResponse)
def urlaub_html(request: Request):
    return templates.TemplateResponse("urlaub.html", {"request": request})

@app.get("/rollen.html", response_class=HTMLResponse)
def rollen_html(request: Request):
    return templates.TemplateResponse("rollen.html", {"request": request})

@app.get("/admin_benutzer.html", response_class=HTMLResponse)
def admin_benutzer_html(request: Request):
    return templates.TemplateResponse("admin_benutzer.html", {"request": request})

@app.get("/info.html", response_class=HTMLResponse)
def info_html(request: Request):
    return templates.TemplateResponse("info.html", {"request": request})

@app.get("/hilfe.html", response_class=HTMLResponse)
def hilfe_html(request: Request):
    return templates.TemplateResponse("hilfe.html", {"request": request})

@app.get("/passwort.html", response_class=HTMLResponse)
def passwort_html(request: Request):
    return templates.TemplateResponse("passwort.html", {"request": request})

@app.get("/index.html", response_class=HTMLResponse)
def index_html(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/Login.html", response_class=HTMLResponse)
def login_html(request: Request):
    return templates.TemplateResponse("Login.html", {"request": request})

@app.get("/register.html", response_class=HTMLResponse)
def register_html(request: Request, db: Session = Depends(get_db)):
    rollen = crud.get_rollen(db)
    return templates.TemplateResponse("register.html", {"request": request, "rollen": rollen, "error": None})

@app.get("/datenschutz.html", response_class=HTMLResponse)
def datenschutz_html(request: Request):
    return templates.TemplateResponse("datenschutz.html", {"request": request})

@app.get("/impressum.html", response_class=HTMLResponse)
def impressum_html(request: Request):
    return templates.TemplateResponse("impressum.html", {"request": request})

@app.get("/health", tags=["health"], include_in_schema=False)
def health_check():
    """
    Health check endpoint for Docker and Kubernetes
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# 404 Error Page Route
@app.get("/404.html", response_class=HTMLResponse)
def error_404_html(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})

# Global 404 Exception Handler
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

# Catch-all route for any unmatched paths (must be last)
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(request: Request, full_path: str):
    # Only handle paths that look like they should be HTML pages
    if full_path.endswith('.html') or not '.' in full_path:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    # For other files (CSS, JS, images, etc.), return 404
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join("static", "images", "BBQGmbH.png")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return Response(status_code=204)  # No content response if favicon doesn't exist