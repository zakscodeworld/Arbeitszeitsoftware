from sqlalchemy.orm import Session, joinedload
import sqlalchemy.orm
from passlib.context import CryptContext
from datetime import date, datetime, timedelta
from decimal import Decimal

import models
import schemas

# Password Hashing Context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# ---------- Rolle CRUD ----------
def get_rolle(db: Session, rolle_id: int) -> models.Rolle | None:
    return db.query(models.Rolle).filter(models.Rolle.id == rolle_id).first()

def get_rolle_by_name(db: Session, name: str) -> models.Rolle | None:
    return db.query(models.Rolle).filter(models.Rolle.name == name).first()

def get_rollen(db: Session, skip: int = 0, limit: int = 100) -> list[models.Rolle]:
    return db.query(models.Rolle).offset(skip).limit(limit).all()

def create_rolle(db: Session, rolle: schemas.RolleCreate) -> models.Rolle:
    db_rolle = models.Rolle(name=rolle.name, beschreibung=rolle.beschreibung)
    db.add(db_rolle)
    db.commit()
    db.refresh(db_rolle)
    return db_rolle

def update_rolle(db: Session, rolle_id: int, rolle_update: schemas.RolleBase) -> models.Rolle | None:
    db_rolle = get_rolle(db, rolle_id)
    if db_rolle:
        db_rolle.name = rolle_update.name
        db_rolle.beschreibung = rolle_update.beschreibung
        db.commit()
        db.refresh(db_rolle)
    return db_rolle

def delete_rolle(db: Session, rolle_id: int) -> models.Rolle | None:
    db_rolle = get_rolle(db, rolle_id)
    if db_rolle:
        db.delete(db_rolle)
        db.commit()
    return db_rolle

# ---------- Benutzer CRUD ----------
def get_benutzer(db: Session, benutzer_id: int) -> models.Benutzer | None:
    return db.query(models.Benutzer).filter(models.Benutzer.id == benutzer_id).first()

def get_benutzer_by_username(db: Session, username: str) -> models.Benutzer | None:
    return db.query(models.Benutzer).filter(models.Benutzer.username == username).first()

def get_benutzer_by_email(db: Session, email: str) -> models.Benutzer | None:
    return db.query(models.Benutzer).filter(models.Benutzer.email == email).first()

def get_benutzer_list(db: Session, skip: int = 0, limit: int = 100) -> list[models.Benutzer]:
    return db.query(models.Benutzer).offset(skip).limit(limit).all()

def create_benutzer(db: Session, benutzer: schemas.BenutzerCreate, send_welcome_email: bool = True) -> models.Benutzer:
    hashed_password = get_password_hash(benutzer.passwort)
    db_benutzer = models.Benutzer(
        username=benutzer.username,
        email=benutzer.email,
        passwort_hash=hashed_password,
        vorname=benutzer.vorname,
        nachname=benutzer.nachname,
        rolle_id=benutzer.rolle_id,
        ist_aktiv=benutzer.ist_aktiv
    )
    db.add(db_benutzer)
    db.commit()
    db.refresh(db_benutzer)
    
    # Send welcome email with account information
    if send_welcome_email and db_benutzer.email:
        try:
            from email_utils import send_account_created_notification
            user_name = f"{db_benutzer.vorname} {db_benutzer.nachname}"
            # We don't send the actual password in the email for security reasons,
            # but we can notify that an account was created
            send_account_created_notification(
                db_benutzer.email,
                user_name,
                db_benutzer.username
            )
        except Exception as e:
            print(f"Failed to send account creation notification: {str(e)}")
            # Continue even if email notification fails
    
    return db_benutzer

def update_benutzer(db: Session, benutzer_id: int, benutzer_update: schemas.BenutzerUpdate) -> models.Benutzer | None:
    db_benutzer = get_benutzer(db, benutzer_id)
    if db_benutzer:
        update_data = benutzer_update.model_dump(exclude_unset=True)
        if "passwort" in update_data and update_data["passwort"]:
            hashed_password = get_password_hash(update_data["passwort"])
            db_benutzer.passwort_hash = hashed_password
            del update_data["passwort"] # Avoid trying to set it directly

        for key, value in update_data.items():
            setattr(db_benutzer, key, value)
        
        try:
            db.commit()
            db.refresh(db_benutzer)
            return db_benutzer
        except Exception as e:
            db.rollback()
            # Log error
            print(f"Error updating user: {str(e)}")
            # Check for unique constraint violations
            if "unique constraint" in str(e).lower() and "email" in str(e).lower():
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Die E-Mail-Adresse '{update_data.get('email')}' wird bereits von einem anderen Benutzer verwendet."
                )
            elif "unique constraint" in str(e).lower() and "username" in str(e).lower():
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Der Benutzername '{update_data.get('username')}' wird bereits von einem anderen Benutzer verwendet."
                )
            # Re-raise other errors
            raise
    return db_benutzer

def delete_benutzer(db: Session, benutzer_id: int) -> models.Benutzer | None:
    db_benutzer = get_benutzer(db, benutzer_id)
    if db_benutzer:
        db.delete(db_benutzer)
        db.commit()
    return db_benutzer

def get_benutzer_by_rolle_id(db: Session, rolle_id: int) -> list[models.Benutzer]:
    """
    Holt alle Benutzer mit einer bestimmten Rolle
    """
    return db.query(models.Benutzer).filter(models.Benutzer.rolle_id == rolle_id).all()

# ---------- Projekt CRUD ----------
def get_projekt(db: Session, projekt_id: int) -> models.Projekt | None:
    return db.query(models.Projekt).filter(models.Projekt.id == projekt_id).first()

def get_projekte(db: Session, skip: int = 0, limit: int = 100) -> list[models.Projekt]:
    return db.query(models.Projekt).offset(skip).limit(limit).all()

def get_projekt_by_name(db: Session, name: str) -> models.Projekt | None:
    return db.query(models.Projekt).filter(models.Projekt.name == name).first()

def create_projekt(db: Session, projekt: schemas.ProjektCreate) -> models.Projekt:
    db_projekt = models.Projekt(**projekt.model_dump())
    db.add(db_projekt)
    db.commit()
    db.refresh(db_projekt)
    return db_projekt

def update_projekt(db: Session, projekt_id: int, projekt_update: schemas.ProjektUpdate) -> models.Projekt | None:
    db_projekt = get_projekt(db, projekt_id)
    if db_projekt:
        update_data = projekt_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_projekt, key, value)
        db.commit()
        db.refresh(db_projekt)
    return db_projekt

def delete_projekt(db: Session, projekt_id: int) -> models.Projekt | None:
    db_projekt = get_projekt(db, projekt_id)
    if db_projekt:
        db.delete(db_projekt)
        db.commit()
    return db_projekt

# ---------- Aufgabe CRUD ----------
def get_aufgabe(db: Session, aufgabe_id: int) -> models.Aufgabe | None:
    return db.query(models.Aufgabe).filter(models.Aufgabe.id == aufgabe_id).first()

def get_aufgaben(db: Session, skip: int = 0, limit: int = 100) -> list[models.Aufgabe]:
    return db.query(models.Aufgabe).offset(skip).limit(limit).all()

def get_aufgaben_by_projekt(db: Session, projekt_id: int, skip: int = 0, limit: int = 100) -> list[models.Aufgabe]:
    return db.query(models.Aufgabe).filter(models.Aufgabe.projekt_id == projekt_id).offset(skip).limit(limit).all()

def create_aufgabe(db: Session, aufgabe: schemas.AufgabeCreate) -> models.Aufgabe:
    db_aufgabe = models.Aufgabe(**aufgabe.model_dump())
    db.add(db_aufgabe)
    db.commit()
    db.refresh(db_aufgabe)
    return db_aufgabe

def update_aufgabe(db: Session, aufgabe_id: int, aufgabe_update: schemas.AufgabeUpdate) -> models.Aufgabe | None:
    db_aufgabe = get_aufgabe(db, aufgabe_id)
    if db_aufgabe:
        update_data = aufgabe_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_aufgabe, key, value)
        db.commit()
        db.refresh(db_aufgabe)
    return db_aufgabe

def delete_aufgabe(db: Session, aufgabe_id: int) -> models.Aufgabe | None:
    db_aufgabe = get_aufgabe(db, aufgabe_id)
    if db_aufgabe:
        db.delete(db_aufgabe)
        db.commit()
    return db_aufgabe

# ---------- Zeiteintrag CRUD ----------
def get_zeiteintrag(db: Session, zeiteintrag_id: int) -> models.Zeiteintrag | None:
    return db.query(models.Zeiteintrag).filter(models.Zeiteintrag.id == zeiteintrag_id).options(
        sqlalchemy.orm.joinedload(models.Zeiteintrag.projekt),
        sqlalchemy.orm.joinedload(models.Zeiteintrag.aufgabe)
    ).first()

def get_zeiteintraege(db: Session, skip: int = 0, limit: int = 100, benutzer_id: int | None = None, projekt_id: int | None = None, aufgabe_id: int | None = None, start_datum: date | None = None, end_datum: date | None = None) -> list[models.Zeiteintrag]:
    # Use joinedload to eagerly load related objects
    query = db.query(models.Zeiteintrag).join(
        models.Projekt, models.Zeiteintrag.projekt_id == models.Projekt.id, isouter=True
    ).join(
        models.Aufgabe, models.Zeiteintrag.aufgabe_id == models.Aufgabe.id, isouter=True
    ).options(        sqlalchemy.orm.joinedload(models.Zeiteintrag.projekt),
        sqlalchemy.orm.joinedload(models.Zeiteintrag.aufgabe)
    )
    
    if benutzer_id is not None:
        query = query.filter(models.Zeiteintrag.benutzer_id == benutzer_id)
    if projekt_id is not None:
        query = query.filter(models.Zeiteintrag.projekt_id == projekt_id)
    if aufgabe_id is not None:
        query = query.filter(models.Zeiteintrag.aufgabe_id == aufgabe_id)
    if start_datum is not None:
        query = query.filter(models.Zeiteintrag.datum >= start_datum)
    if end_datum is not None:
        query = query.filter(models.Zeiteintrag.datum <= end_datum)
    result = query.offset(skip).limit(limit).all()
    return result

def get_zeiteintraege_by_benutzer(db: Session, benutzer_id: int, skip: int = 0, limit: int = 100) -> list[models.Zeiteintrag]:
    return db.query(models.Zeiteintrag).filter(models.Zeiteintrag.benutzer_id == benutzer_id).offset(skip).limit(limit).all()

def create_zeiteintrag(db: Session, zeiteintrag: schemas.ZeiteintragCreate, current_user_id: int = None) -> models.Zeiteintrag:
    try:
        # If benutzer_id is not set, use the current user's ID
        data_dict = zeiteintrag.model_dump()
        if current_user_id and not zeiteintrag.benutzer_id:
            data_dict['benutzer_id'] = current_user_id
        
        # Calculate hours from start and end time
        start = datetime.combine(data_dict['datum'], data_dict['startzeit'])
        end = datetime.combine(data_dict['datum'], data_dict['endzeit'])
        
        # Handle overnight shifts
        if end < start:
            end += timedelta(days=1)
        
        duration = end - start
        hours = duration.total_seconds() / 3600
        data_dict['stunden'] = Decimal(str(round(hours, 2)))

        # Create and save the time entry
        db_zeiteintrag = models.Zeiteintrag(**data_dict)
        db.add(db_zeiteintrag)
        db.commit()
        db.refresh(db_zeiteintrag)
        
        # Check if hours are less than or exceed 8 hours and send notification
        from email_utils import send_work_hours_notification
        
        # Get the user information for sending email
        benutzer = db.query(models.Benutzer).filter(models.Benutzer.id == db_zeiteintrag.benutzer_id).first()
        if benutzer and benutzer.email:
            # Format user name for the email
            user_name = f"{benutzer.vorname} {benutzer.nachname}"
            
            # Convert Decimal to float for comparison
            hours_float = float(data_dict['stunden'])
            
            if hours_float < 8.0:
                # Send notification for under 8 hours
                send_work_hours_notification(
                    benutzer.email, 
                    user_name, 
                    str(data_dict['datum']), 
                    hours_float, 
                    is_under=True
                )
            elif hours_float > 8.0:
                # Send notification for over 8 hours
                send_work_hours_notification(
                    benutzer.email, 
                    user_name, 
                    str(data_dict['datum']), 
                    hours_float, 
                    is_under=False
                )
        
        return db_zeiteintrag
    except Exception as e:
        db.rollback()
        print(f"Error creating time entry: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Fehler beim Erstellen des Zeiteintrags: {str(e)}")

def update_zeiteintrag(db: Session, zeiteintrag_id: int, zeiteintrag_update: schemas.ZeiteintragUpdate) -> models.Zeiteintrag | None:
    db_zeiteintrag = get_zeiteintrag(db, zeiteintrag_id)
    if db_zeiteintrag:
        update_data = zeiteintrag_update.model_dump(exclude_unset=True)
        
        # Save old values for comparison if startzeit or endzeit are changing
        recalculate_hours = False
        old_datum = db_zeiteintrag.datum
        old_startzeit = db_zeiteintrag.startzeit
        old_endzeit = db_zeiteintrag.endzeit
        
        for key, value in update_data.items():
            setattr(db_zeiteintrag, key, value)
            if key in ['startzeit', 'endzeit', 'datum']:
                recalculate_hours = True
                
        # Recalculate hours if either time or date has changed
        if recalculate_hours:
            # Use either updated or existing values
            datum = update_data.get('datum', old_datum)
            startzeit = update_data.get('startzeit', old_startzeit)
            endzeit = update_data.get('endzeit', old_endzeit)
            
            # Calculate hours from start and end time
            start = datetime.combine(datum, startzeit)
            end = datetime.combine(datum, endzeit)
            
            # Handle overnight shifts
            if end < start:
                end += timedelta(days=1)
            
            duration = end - start
            hours = duration.total_seconds() / 3600
            db_zeiteintrag.stunden = Decimal(str(round(hours, 2)))
            
        db.commit()
        db.refresh(db_zeiteintrag)
        
        # Send email notifications if hours are under/over 8 hours
        try:
            from email_utils import send_work_hours_notification
            
            # Get the user information for sending email
            benutzer = db.query(models.Benutzer).filter(models.Benutzer.id == db_zeiteintrag.benutzer_id).first()
            if benutzer and benutzer.email:
                # Format user name for the email
                user_name = f"{benutzer.vorname} {benutzer.nachname}"
                
                # Convert Decimal to float for comparison
                hours_float = float(db_zeiteintrag.stunden)
                
                if hours_float < 8.0:
                    # Send notification for under 8 hours
                    send_work_hours_notification(
                        benutzer.email, 
                        user_name, 
                        str(db_zeiteintrag.datum), 
                        hours_float, 
                        is_under=True
                    )
                elif hours_float > 8.0:
                    # Send notification for over 8 hours
                    send_work_hours_notification(
                        benutzer.email, 
                        user_name, 
                        str(db_zeiteintrag.datum), 
                        hours_float, 
                        is_under=False
                    )
        except Exception as e:
            print(f"Failed to send email notification: {str(e)}")
            # Continue even if email notification fails
    return db_zeiteintrag

def delete_zeiteintrag(db: Session, zeiteintrag_id: int) -> models.Zeiteintrag | None:
    db_zeiteintrag = get_zeiteintrag(db, zeiteintrag_id)
    if db_zeiteintrag:
        db.delete(db_zeiteintrag)
        db.commit()
    return db_zeiteintrag

# ---------- AbwesenheitTyp CRUD ----------
def get_abwesenheit_typ(db: Session, abwesenheit_typ_id: int) -> models.AbwesenheitTyp | None:
    return db.query(models.AbwesenheitTyp).filter(models.AbwesenheitTyp.id == abwesenheit_typ_id).first()

def get_abwesenheit_typ_by_name(db: Session, name: str) -> models.AbwesenheitTyp | None:
    return db.query(models.AbwesenheitTyp).filter(models.AbwesenheitTyp.name == name).first()

def get_abwesenheit_typen(db: Session, skip: int = 0, limit: int = 100) -> list[models.AbwesenheitTyp]:
    return db.query(models.AbwesenheitTyp).offset(skip).limit(limit).all()

def create_abwesenheit_typ(db: Session, abwesenheit_typ: schemas.AbwesenheitTypCreate) -> models.AbwesenheitTyp:
    db_abwesenheit_typ = models.AbwesenheitTyp(**abwesenheit_typ.model_dump())
    db.add(db_abwesenheit_typ)
    db.commit()
    db.refresh(db_abwesenheit_typ)
    return db_abwesenheit_typ

def update_abwesenheit_typ(db: Session, abwesenheit_typ_id: int, abwesenheit_typ_update: schemas.AbwesenheitTypBase) -> models.AbwesenheitTyp | None:
    db_abwesenheit_typ = get_abwesenheit_typ(db, abwesenheit_typ_id)
    if db_abwesenheit_typ:
        update_data = abwesenheit_typ_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_abwesenheit_typ, key, value)
        db.commit()
        db.refresh(db_abwesenheit_typ)
    return db_abwesenheit_typ

def delete_abwesenheit_typ(db: Session, abwesenheit_typ_id: int) -> models.AbwesenheitTyp | None:
    db_abwesenheit_typ = get_abwesenheit_typ(db, abwesenheit_typ_id)
    if db_abwesenheit_typ:
        db.delete(db_abwesenheit_typ)
        db.commit()
    return db_abwesenheit_typ

# ---------- Abwesenheit CRUD ----------
def get_abwesenheit(db: Session, abwesenheit_id: int) -> models.Abwesenheit | None:
    return db.query(models.Abwesenheit).options(
        joinedload(models.Abwesenheit.abwesenheit_typ),
        joinedload(models.Abwesenheit.benutzer)
    ).filter(models.Abwesenheit.id == abwesenheit_id).first()

def get_abwesenheiten(db: Session, skip: int = 0, limit: int = 100, benutzer_id: int | None = None, abwesenheit_typ_id: int | None = None, status: str | None = None, start_datum: date | None = None, end_datum: date | None = None) -> list[models.Abwesenheit]:
    query = db.query(models.Abwesenheit).options(
        joinedload(models.Abwesenheit.abwesenheit_typ),
        joinedload(models.Abwesenheit.benutzer)
    )
    if benutzer_id is not None:
        query = query.filter(models.Abwesenheit.benutzer_id == benutzer_id)
    if abwesenheit_typ_id is not None:
        query = query.filter(models.Abwesenheit.abwesenheit_typ_id == abwesenheit_typ_id)
    if status is not None:
        query = query.filter(models.Abwesenheit.status == status)
    if start_datum is not None:
        query = query.filter(models.Abwesenheit.start_datum >= start_datum)
    if end_datum is not None:
        query = query.filter(models.Abwesenheit.end_datum <= end_datum)
    return query.offset(skip).limit(limit).all()

def get_abwesenheiten_by_benutzer(db: Session, benutzer_id: int, skip: int = 0, limit: int = 100) -> list[models.Abwesenheit]:
    return db.query(models.Abwesenheit).options(
        joinedload(models.Abwesenheit.abwesenheit_typ),
        joinedload(models.Abwesenheit.benutzer)
    ).filter(models.Abwesenheit.benutzer_id == benutzer_id).offset(skip).limit(limit).all()

def create_abwesenheit(db: Session, abwesenheit: schemas.AbwesenheitCreate, beantragt_von_benutzer_id: int = None) -> models.Abwesenheit:
    db_abwesenheit = models.Abwesenheit(**abwesenheit.model_dump())
    if beantragt_von_benutzer_id:
        db_abwesenheit.beantragt_von_benutzer_id = beantragt_von_benutzer_id
    db.add(db_abwesenheit)
    db.commit()
    db.refresh(db_abwesenheit)
    
    # Send email notification about new absence request
    try:
        from email_utils import send_absence_notification
        
        # Get user and absence type information
        benutzer = get_benutzer(db, db_abwesenheit.benutzer_id)
        abwesenheit_typ = get_abwesenheit_typ(db, db_abwesenheit.abwesenheit_typ_id)
        
        if benutzer and benutzer.email and abwesenheit_typ:
            # Format name
            user_name = f"{benutzer.vorname} {benutzer.nachname}"
            
            # Send email notification for the new request
            send_absence_notification(
                benutzer.email,
                user_name,
                abwesenheit_typ.name,
                db_abwesenheit.start_datum,
                db_abwesenheit.end_datum,
                db_abwesenheit.status
            )
            
            # If the requester is not the user (e.g., manager creating absence for employee),
            # send notification to the employee as well
            if beantragt_von_benutzer_id and beantragt_von_benutzer_id != db_abwesenheit.benutzer_id:
                manager = get_benutzer(db, beantragt_von_benutzer_id)
                if manager:
                    manager_name = f"{manager.vorname} {manager.nachname}"
                    comment = f"Erstellt von {manager_name}"
                    send_absence_notification(
                        benutzer.email,
                        user_name,
                        abwesenheit_typ.name,
                        db_abwesenheit.start_datum,
                        db_abwesenheit.end_datum,
                        db_abwesenheit.status,
                        manager_name,
                        comment
                    )
    except Exception as e:
        print(f"Failed to send absence creation notification: {str(e)}")
        # Continue even if email notification fails
        
    return db_abwesenheit

def update_abwesenheit(db: Session, abwesenheit_id: int, abwesenheit_update: schemas.AbwesenheitUpdate, genehmiger_id: int = None) -> models.Abwesenheit | None:
    db_abwesenheit = get_abwesenheit(db, abwesenheit_id)
    if db_abwesenheit:
        # Store old status for later comparison
        old_status = db_abwesenheit.status
        
        update_data = abwesenheit_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_abwesenheit, key, value)
        
        # Set genehmiger_id if provided and status is changing to 'genehmigt' or 'abgelehnt'
        if genehmiger_id and abwesenheit_update.status and abwesenheit_update.status in ['genehmigt', 'abgelehnt']:
            db_abwesenheit.genehmigt_von_benutzer_id = genehmiger_id
        
        db.commit()
        db.refresh(db_abwesenheit)
        
        # Check if status has changed and send notification
        new_status = db_abwesenheit.status
        if new_status != old_status and new_status in ['genehmigt', 'abgelehnt']:
            try:
                from email_utils import send_absence_notification
                
                # Get user and approver information
                benutzer = get_benutzer(db, db_abwesenheit.benutzer_id)
                approver = get_benutzer(db, db_abwesenheit.genehmigt_von_benutzer_id) if db_abwesenheit.genehmigt_von_benutzer_id else None
                abwesenheit_typ = get_abwesenheit_typ(db, db_abwesenheit.abwesenheit_typ_id)
                
                if benutzer and benutzer.email and abwesenheit_typ:
                    # Format names
                    user_name = f"{benutzer.vorname} {benutzer.nachname}"
                    approver_name = f"{approver.vorname} {approver.nachname}" if approver else None
                    
                    # Send email notification
                    send_absence_notification(
                        benutzer.email,
                        user_name,
                        abwesenheit_typ.name,
                        db_abwesenheit.start_datum,
                        db_abwesenheit.end_datum,
                        new_status,
                        approver_name,
                        db_abwesenheit.kommentar_genehmiger
                    )
            except Exception as e:
                print(f"Failed to send absence notification: {str(e)}")
                # Continue even if email notification fails
                
    return db_abwesenheit

def delete_abwesenheit(db: Session, abwesenheit_id: int) -> models.Abwesenheit | None:
    db_abwesenheit = get_abwesenheit(db, abwesenheit_id)
    if db_abwesenheit:
        db.delete(db_abwesenheit)
        db.commit()
    return db_abwesenheit

# ---------- Password Update ----------
def update_password(db: Session, benutzer_id: int, new_password: str):
    """Update user password"""
    db_benutzer = db.query(models.Benutzer).filter(models.Benutzer.id == benutzer_id).first()
    if db_benutzer:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        db_benutzer.passwort_hash = pwd_context.hash(new_password)
        db.commit()
        db.refresh(db_benutzer)
        
        # Send email notification for password change
        try:
            from email_utils import send_password_changed_notification
            if db_benutzer.email:
                user_name = f"{db_benutzer.vorname} {db_benutzer.nachname}"
                send_password_changed_notification(
                    db_benutzer.email,
                    user_name
                )
        except Exception as e:
            print(f"Failed to send password change notification: {str(e)}")
            # Continue even if email notification fails
            
        return db_benutzer
    return None

# ---------- Initial Data Creation ----------
def create_initial_data(db: Session):
    # Create Roles
    rollen_namen = ["Administrator", "Manager", "Mitarbeiter"]
    for name in rollen_namen:
        if not get_rolle_by_name(db, name=name):
            create_rolle(db, rolle=schemas.RolleCreate(name=name, beschreibung=f"Rolle für {name}"))

    # Create AbwesenheitTypen
    abwesenheit_typen_namen = ["Urlaub", "Krankheit", "Sonderurlaub", "Fortbildung", "Homeoffice"]
    for name in abwesenheit_typen_namen:
        if not get_abwesenheit_typ_by_name(db, name=name):
            create_abwesenheit_typ(db, abwesenheit_typ=schemas.AbwesenheitTypCreate(name=name, beschreibung=f"Abwesenheitstyp: {name}"))

    # Create sample projects
    projekt_namen = [
        {"name": "Webentwicklung", "beschreibung": "Entwicklung von Webanwendungen"},
        {"name": "Mobile App", "beschreibung": "Entwicklung von mobilen Anwendungen"},
        {"name": "Datenanalyse", "beschreibung": "Analyse von Kundendaten"},
        {"name": "Marketing", "beschreibung": "Marketingkampagnen planen und umsetzen"},
        {"name": "Kundensupport", "beschreibung": "Betreuung von Kunden"}
    ]
    
    for projekt_data in projekt_namen:
        if not get_projekt_by_name(db, name=projekt_data["name"]):
            create_projekt(db, projekt=schemas.ProjektCreate(
                name=projekt_data["name"], 
                beschreibung=projekt_data["beschreibung"],
                status="aktiv"
            ))
    
    # Create sample tasks for projects
    sample_tasks = [
        {"name": "Frontend-Entwicklung", "beschreibung": "Entwicklung der Benutzeroberfläche"},
        {"name": "Backend-Entwicklung", "beschreibung": "Entwicklung der Serverlogik"},
        {"name": "Testen", "beschreibung": "Testen der Anwendung"},
        {"name": "Dokumentation", "beschreibung": "Erstellung der Dokumentation"},
        {"name": "Projektmanagement", "beschreibung": "Koordination des Projekts"}
    ]
    
    # Add tasks to each project
    projekte = get_projekte(db)
    for projekt in projekte:
        for task_data in sample_tasks:
            # Check if task already exists for this project
            existing_task = db.query(models.Aufgabe).filter(
                models.Aufgabe.projekt_id == projekt.id,
                models.Aufgabe.name == task_data["name"]
            ).first()
            
            if not existing_task:
                create_aufgabe(db, aufgabe=schemas.AufgabeCreate(
                    projekt_id=projekt.id,
                    name=task_data["name"],
                    beschreibung=task_data["beschreibung"],
                    geplante_stunden=40,
                    status="offen"
                ))

    # Create a default Admin User (if not exists)
    admin_username = "admin"
    if not get_benutzer_by_username(db, username=admin_username):
        admin_rolle = get_rolle_by_name(db, name="Administrator")
        if admin_rolle:
            admin_user = schemas.BenutzerCreate(
                username=admin_username,
                email="admin@example.com",
                passwort="adminpassword", # Store securely or prompt for it
                vorname="Admin",
                nachname="User",
                rolle_id=admin_rolle.id,
                ist_aktiv=True
            )
            create_benutzer(db, benutzer=admin_user)
            print(f"Default admin user '{admin_username}' created with password 'adminpassword'. Please change this password immediately.")
        else:
            print("Admin role not found. Could not create default admin user.")
    else:
        print(f"Admin user '{admin_username}' already exists.")

    # You can add more initial data here, e.g., a default project or task
    # default_projekt_name = "Internes Projekt"
    # if not db.query(models.Projekt).filter(models.Projekt.name == default_projekt_name).first():
    #     create_projekt(db, projekt=schemas.ProjektCreate(name=default_projekt_name, beschreibung="Standard internes Projekt"))
    #     print(f"Default project '{default_projekt_name}' created.")
