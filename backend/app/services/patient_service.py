from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.schemas.patient import PatientCreate


class DuplicatePatientError(Exception):
    """Raised when a patient unique field already exists."""


def create_patient(db: Session, patient_data: PatientCreate) -> Patient:
    patient = Patient(**patient_data.model_dump())

    db.add(patient)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicatePatientError("A patient with this phone number already exists")

    db.refresh(patient)
    return patient


def list_patients(db: Session) -> list[Patient]:
    return db.query(Patient).order_by(Patient.id).all()

def list_patient(db:Session, patient_id: int) -> Patient:
    return db.get(Patient, patient_id)
