# models.py
from sqlalchemy import (
    Column, Integer, String, Date, Time, ForeignKey, TIMESTAMP, Boolean, Text, Numeric, DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Rolle(Base):
    __tablename__ = "rollen"  # Plural convention
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g., "Administrator", "Mitarbeiter"
    beschreibung = Column(Text, nullable=True)

    # Relationship to Benutzer
    benutzer = relationship("Benutzer", back_populates="rolle")

    def __repr__(self):
        return f"<Rolle(name=\'{self.name}\')>"


class Benutzer(Base):
    __tablename__ = "benutzer"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    passwort_hash = Column(String(255), nullable=False)
    vorname = Column(String(100), nullable=False)
    nachname = Column(String(100), nullable=False)
    rolle_id = Column(Integer, ForeignKey("rollen.id"), nullable=False)
    ist_aktiv = Column(Boolean, default=True, nullable=False)
    # Using DateTime(timezone=True) for timezone awareness
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    aktualisiert_am = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    rolle = relationship("Rolle", back_populates="benutzer")
    zeiteintraege = relationship("Zeiteintrag", back_populates="benutzer", cascade="all, delete-orphan")
    abwesenheiten = relationship("Abwesenheit", foreign_keys="[Abwesenheit.benutzer_id]", back_populates="benutzer", cascade="all, delete-orphan")
    genehmigte_abwesenheiten = relationship("Abwesenheit", foreign_keys="[Abwesenheit.genehmigt_von_benutzer_id]", back_populates="genehmiger")

    def __repr__(self):
        return f"<Benutzer(username=\'{self.username}\')>"


class Projekt(Base):
    __tablename__ = "projekte"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    beschreibung = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default='aktiv')  # e.g., "aktiv", "archiviert", "abgeschlossen"
    start_datum = Column(Date, nullable=True)
    end_datum = Column(Date, nullable=True)
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    aktualisiert_am = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    aufgaben = relationship("Aufgabe", back_populates="projekt", cascade="all, delete-orphan")
    # Denormalized link for easier querying, if kept
    zeiteintraege = relationship("Zeiteintrag", back_populates="projekt")

    def __repr__(self):
        return f"<Projekt(name=\'{self.name}\')>"


class Aufgabe(Base):
    __tablename__ = "aufgaben"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    projekt_id = Column(Integer, ForeignKey("projekte.id"), nullable=False)
    name = Column(String(255), nullable=False)
    beschreibung = Column(Text, nullable=True)
    geplante_stunden = Column(Numeric(5, 2), nullable=True)  # e.g., 40.5 hours
    status = Column(String(50), nullable=False, default='offen')  # e.g., "offen", "in Arbeit", "erledigt"
    faelligkeits_datum = Column(Date, nullable=True)
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    aktualisiert_am = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    projekt = relationship("Projekt", back_populates="aufgaben")
    zeiteintraege = relationship("Zeiteintrag", back_populates="aufgabe", passive_deletes=True)

    def __repr__(self):
        return f"<Aufgabe(name='{self.name}')>"


class Zeiteintrag(Base):
    __tablename__ = "zeiteintraege"  # Formerly "Arbeitszeit"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    benutzer_id = Column(Integer, ForeignKey("benutzer.id", ondelete="CASCADE"), nullable=False)
    aufgabe_id = Column(Integer, ForeignKey("aufgaben.id", ondelete="CASCADE"), nullable=False)
    projekt_id = Column(Integer, ForeignKey("projekte.id", ondelete="CASCADE"), nullable=False)
    datum = Column(Date, nullable=False)
    startzeit = Column(Time(timezone=False), nullable=False)
    endzeit = Column(Time(timezone=False), nullable=False)
    stunden = Column(Numeric(5, 2), nullable=True)  # Automatically calculated from start/end
    beschreibung = Column(Text, nullable=True)
    ist_abrechenbar = Column(Boolean, default=True, nullable=False)
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    aktualisiert_am = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    benutzer = relationship("Benutzer", back_populates="zeiteintraege")
    aufgabe = relationship("Aufgabe", back_populates="zeiteintraege")
    projekt = relationship("Projekt", back_populates="zeiteintraege")

    def __repr__(self):
        return f"<Zeiteintrag(datum='{self.datum}', benutzer_id={self.benutzer_id}, stunden={self.stunden})>"


class AbwesenheitTyp(Base):
    __tablename__ = "abwesenheit_typen"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # e.g., "Urlaub", "Krankheit", "Sonderurlaub", "Fortbildung"
    name = Column(String(100), unique=True, nullable=False)
    beschreibung = Column(Text, nullable=True)

    # Relationship
    abwesenheiten = relationship("Abwesenheit", back_populates="abwesenheit_typ")

    def __repr__(self):
        return f"<AbwesenheitTyp(name=\'{self.name}\')>"


class Abwesenheit(Base):
    __tablename__ = "abwesenheiten"  # Replaces "Urlaub" and includes sick days etc.
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    benutzer_id = Column(Integer, ForeignKey("benutzer.id"), nullable=False)
    abwesenheit_typ_id = Column(Integer, ForeignKey("abwesenheit_typen.id"), nullable=False)
    start_datum = Column(Date, nullable=False)
    end_datum = Column(Date, nullable=False)
    grund = Column(Text, nullable=True)  # Optional reason from user
    status = Column(String(50), nullable=False, default='beantragt')  # e.g., "beantragt", "genehmigt", "abgelehnt"
    genehmigt_von_benutzer_id = Column(Integer, ForeignKey("benutzer.id"), nullable=True)
    kommentar_genehmiger = Column(Text, nullable=True)  # Optional comment from approver
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    aktualisiert_am = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    benutzer = relationship("Benutzer", foreign_keys=[benutzer_id], back_populates="abwesenheiten")
    abwesenheit_typ = relationship("AbwesenheitTyp", back_populates="abwesenheiten")
    genehmiger = relationship("Benutzer", foreign_keys=[genehmigt_von_benutzer_id], back_populates="genehmigte_abwesenheiten")

    def __repr__(self):
        return f"<Abwesenheit(start_datum=\'{self.start_datum}\', benutzer_id={self.benutzer_id}, typ_id={self.abwesenheit_typ_id})>"
