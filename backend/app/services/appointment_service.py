from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.schemas.appointment import AppointmentCreate
from app.services.slot_utils import is_valid_doctor_slot

MIN_LEAD_TIME = timedelta(hours=1)


class DuplicateEntryError(Exception):
    """Raised when an appointment for that doctor slot already exists."""


class AppointmentValidationError(Exception):
    """Raised when booking rules are not satisfied."""


def create_appointment(db: Session, appointment_data: AppointmentCreate) -> Appointment:
    doctor = db.get(Doctor, appointment_data.doctor_id)
    if doctor is None:
        raise AppointmentValidationError(
            f"Doctor with id {appointment_data.doctor_id} not found"
        )

    patient = db.get(Patient, appointment_data.patient_id)
    if patient is None:
        raise AppointmentValidationError(
            f"Patient with id {appointment_data.patient_id} not found"
        )

    if not doctor.available:
        raise AppointmentValidationError("Doctor is not available for bookings")

    if not is_valid_doctor_slot(
        doctor,
        appointment_data.date,
        appointment_data.start_time,
        appointment_data.end_time,
    ):
        raise AppointmentValidationError(
            "Requested time is not a valid appointment slot for this doctor"
        )

    slot_start = datetime.combine(appointment_data.date, appointment_data.start_time)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    if slot_start <= now:
        raise AppointmentValidationError("Cannot book an appointment in the past")

    if slot_start < now + MIN_LEAD_TIME:
        raise AppointmentValidationError(
            "Appointments must be booked at least 1 hour in advance"
        )

    existing = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == appointment_data.doctor_id,
            Appointment.date == appointment_data.date,
            Appointment.start_time == appointment_data.start_time,
            Appointment.status == AppointmentStatus.BOOKED,
        )
        .first()
    )
    if existing:
        raise DuplicateEntryError("An appointment for this slot has already been booked")

    appointment = Appointment(
        **appointment_data.model_dump(),
        status=AppointmentStatus.BOOKED,
    )

    db.add(appointment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateEntryError("An appointment for this slot has already been booked")

    db.refresh(appointment)
    return appointment
