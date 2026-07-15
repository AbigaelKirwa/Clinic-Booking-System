from datetime import date, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorAvailabilityResponse, DoctorCreate, TimeSlot

SLOT_DURATION = timedelta(minutes=30)


class DuplicateEntryError(Exception):
    """Raised when a unique doctor field exists"""


def create_doctor(db: Session, doctor_data: DoctorCreate) -> Doctor:
    doctor = Doctor(**doctor_data.model_dump())

    db.add(doctor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateEntryError("A doctor with this email/phone number already exists")

    db.refresh(doctor)
    return doctor


def list_doctors(db: Session) -> list[Doctor]:
    return db.query(Doctor).order_by(Doctor.id).all()


def list_doctor(db: Session, doctor_id: int) -> Doctor | None:
    return db.get(Doctor, doctor_id)


def list_doctor_available_slots(
    db: Session,
    doctor_id: int,
    target_date: date,
) -> DoctorAvailabilityResponse | None:
    doctor = db.get(Doctor, doctor_id)
    if doctor is None:
        return None

    if not doctor.available:
        return DoctorAvailabilityResponse(
            doctor_id=doctor_id,
            date=target_date,
            slots=[],
        )

    booked_appointments = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == target_date,
            Appointment.status == AppointmentStatus.BOOKED,
        )
        .all()
    )
    booked_starts = {appointment.start_time for appointment in booked_appointments}

    slots: list[TimeSlot] = []
    cursor = datetime.combine(target_date, doctor.start_time)
    end = datetime.combine(target_date, doctor.end_time)

    while cursor + SLOT_DURATION <= end:
        slot_start = cursor.time()
        slot_end = (cursor + SLOT_DURATION).time()

        if slot_start not in booked_starts:
            slots.append(TimeSlot(start_time=slot_start, end_time=slot_end))

        cursor += SLOT_DURATION

    return DoctorAvailabilityResponse(
        doctor_id=doctor_id,
        date=target_date,
        slots=slots,
    )
