from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime, time
from decimal import Decimal
from fastapi.security import OAuth2PasswordBearer # Added import

# Helper Pydantic Config
class OrmConfig:
    # Pydantic V2 uses model_config instead of Config
    # and from_attributes instead of orm_mode
    # However, to minimize changes for now, we'll keep orm_mode
    # but be aware of the V2 way:
    # model_config = {"from_attributes": True}
    orm_mode = True

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") # Defined oauth2_scheme

# ---------- Rolle Schemas ----------
class RolleBase(BaseModel):
    name: str
    beschreibung: Optional[str] = None

class RolleCreate(RolleBase):
    pass

class RolleUpdate(RolleBase): # Added RolleUpdate schema
    pass

class Rolle(RolleBase):
    id: int

    class Config(OrmConfig):
        pass

# ---------- Benutzer Schemas ----------
class BenutzerBase(BaseModel):
    username: str
    email: EmailStr
    vorname: str
    nachname: str
    ist_aktiv: Optional[bool] = True

class BenutzerCreate(BenutzerBase):
    passwort: str
    rolle_id: int

class BenutzerUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    vorname: Optional[str] = None
    nachname: Optional[str] = None
    ist_aktiv: Optional[bool] = None
    passwort: Optional[str] = None # For password change
    rolle_id: Optional[int] = None

class Benutzer(BenutzerBase):
    id: int
    rolle_id: int
    erstellt_am: datetime
    aktualisiert_am: datetime
    rolle: Rolle # Nested schema for relationship

    class Config(OrmConfig):
        pass

# ---------- Projekt Schemas ----------
class ProjektBase(BaseModel):
    name: str
    beschreibung: Optional[str] = None
    status: Optional[str] = 'aktiv'
    start_datum: Optional[date] = None
    end_datum: Optional[date] = None

class ProjektCreate(ProjektBase):
    pass

class ProjektUpdate(BaseModel):
    name: Optional[str] = None
    beschreibung: Optional[str] = None
    status: Optional[str] = None
    start_datum: Optional[date] = None
    end_datum: Optional[date] = None

class Projekt(ProjektBase):
    id: int
    erstellt_am: datetime
    aktualisiert_am: datetime
    # aufgaben: List['Aufgabe'] = [] # Avoid circular import for now, handle in specific response models if needed

    class Config(OrmConfig):
        pass

# ---------- Aufgabe Schemas ----------
class AufgabeBase(BaseModel):
    name: str
    beschreibung: Optional[str] = None
    geplante_stunden: Optional[Decimal] = None
    status: Optional[str] = 'offen'
    faelligkeits_datum: Optional[date] = None

class AufgabeCreate(AufgabeBase):
    projekt_id: int

class AufgabeUpdate(BaseModel):
    name: Optional[str] = None
    projekt_id: Optional[int] = None # Allow moving task to another project
    beschreibung: Optional[str] = None
    geplante_stunden: Optional[Decimal] = None
    status: Optional[str] = None
    faelligkeits_datum: Optional[date] = None

class Aufgabe(AufgabeBase):
    id: int
    projekt_id: int
    erstellt_am: datetime
    aktualisiert_am: datetime
    # projekt: Projekt # Avoid circular import for now

    class Config(OrmConfig):
        pass

# ---------- Zeiteintrag Schemas ----------
class ZeiteintragBase(BaseModel):
    datum: date
    startzeit: time  # Required field
    endzeit: time    # Required field
    stunden: Optional[Decimal] = None  # Automatically calculated
    beschreibung: Optional[str] = None
    ist_abrechenbar: bool = True  # Default to True but required

class ZeiteintragCreate(ZeiteintragBase):
    benutzer_id: Optional[int] = None  # Usually taken from current authenticated user
    aufgabe_id: int
    projekt_id: int # Denormalized, ensure consistency

class ZeiteintragUpdate(BaseModel):
    datum: Optional[date] = None
    startzeit: Optional[time] = None
    endzeit: Optional[time] = None
    stunden: Optional[Decimal] = None
    beschreibung: Optional[str] = None
    ist_abrechenbar: Optional[bool] = None
    aufgabe_id: Optional[int] = None # Allow changing task
    projekt_id: Optional[int] = None # Allow changing project (if task changes)

class ProjektMinimal(BaseModel):
    id: int
    name: str

    class Config(OrmConfig):
        pass

class AufgabeMinimal(BaseModel):
    id: int
    name: str

    class Config(OrmConfig):
        pass

class Zeiteintrag(ZeiteintragBase):
    id: int
    benutzer_id: int
    aufgabe_id: int
    projekt_id: int
    erstellt_am: datetime
    aktualisiert_am: datetime
    projekt: Optional[ProjektMinimal] = None
    aufgabe: Optional[AufgabeMinimal] = None
    # benutzer: Benutzer # Avoid circular imports for now

    class Config(OrmConfig):
        pass

# ---------- AbwesenheitTyp Schemas ----------
class AbwesenheitTypBase(BaseModel):
    name: str
    beschreibung: Optional[str] = None

class AbwesenheitTypCreate(AbwesenheitTypBase):
    pass

class AbwesenheitTypUpdate(AbwesenheitTypBase): # Added AbwesenheitTypUpdate schema
    pass

class AbwesenheitTyp(AbwesenheitTypBase):
    id: int

    class Config(OrmConfig):
        pass

# ---------- Abwesenheit Schemas ----------
class AbwesenheitBase(BaseModel):
    start_datum: date
    end_datum: date
    grund: Optional[str] = None
    status: Optional[str] = 'beantragt' # Default status on creation

class AbwesenheitCreate(AbwesenheitBase):
    benutzer_id: int # Usually current authenticated user
    abwesenheit_typ_id: int

class AbwesenheitUpdate(BaseModel):
    start_datum: Optional[date] = None
    end_datum: Optional[date] = None
    grund: Optional[str] = None
    status: Optional[str] = None # For manager/admin to approve/reject
    abwesenheit_typ_id: Optional[int] = None # Allow changing type
    # genehmigt_von_benutzer_id: Optional[int] = None # Should be set by system on approval
    kommentar_genehmiger: Optional[str] = None # For manager/admin

class Abwesenheit(AbwesenheitBase):
    id: int
    benutzer_id: int
    abwesenheit_typ_id: int
    genehmigt_von_benutzer_id: Optional[int] = None
    kommentar_genehmiger: Optional[str] = None
    erstellt_am: datetime
    aktualisiert_am: datetime
    # benutzer: Benutzer # Avoid circular imports
    abwesenheit_typ: AbwesenheitTyp # Nested schema
    # genehmiger: Optional[Benutzer] = None

    class Config(OrmConfig):
        pass

# Schemas for JWT Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

# Password-Verify-Schema
class PasswordVerify(BaseModel):
    password: str

# Forward references for nested schemas with circular dependencies
# This is one way to handle them if you need deep nesting in responses.
# Another is to have specific response models.
# Projekt.update_forward_refs(Aufgabe=Aufgabe)
# Aufgabe.update_forward_refs(Projekt=Projekt)
# Benutzer.update_forward_refs(Zeiteintrag=Zeiteintrag, Abwesenheit=Abwesenheit, Rolle=Rolle)
# Zeiteintrag.update_forward_refs(Benutzer=Benutzer, Aufgabe=Aufgabe, Projekt=Projekt)
# Abwesenheit.update_forward_refs(Benutzer=Benutzer, AbwesenheitTyp=AbwesenheitTyp)

# For now, complex nested structures in responses are kept minimal to avoid circular import issues at startup.
# You can create more specific response models that include nested data as needed for particular endpoints.
# For example:
class BenutzerDetails(Benutzer):
    zeiteintraege: List[Zeiteintrag] = []
    abwesenheiten: List[Abwesenheit] = []

class ProjektDetails(Projekt):
    aufgaben: List[Aufgabe] = []

class AufgabeDetails(Aufgabe):
    projekt: Projekt
    zeiteintraege: List[Zeiteintrag] = []