from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate

class DuplicateEntryError(Exception):
    """Raised when a unique doctor field exists"""

def create_doctor(db:Session, doctor_data:DoctorCreate) -> Doctor:
    doctor = Doctor(**doctor_data.model_dump())

    db.add(doctor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateEntryError("A doctor with this email/phone number already exists")

    db.refresh(doctor)
    return doctor

def list_doctors(db:Session) -> list[Doctor]:
    return db.query(Doctor).order_by(Doctor.id).all()

def list_doctor(db: Session, doctor_id: int) -> Doctor | None:
    return db.get(Doctor, doctor_id)

