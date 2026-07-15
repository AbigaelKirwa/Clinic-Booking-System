from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.schemas.appointment import (
    AppointmentCancel,
    AppointmentCreate,
    AppointmentReschedule,
)
from app.services.slot_utils import is_valid_doctor_slot

MIN_LEAD_TIME = timedelta(hours=1)


class DuplicateEntryError(Exception):
    """Raised when an appointment for that doctor slot already exists."""


class AppointmentValidationError(Exception):
    """Raised when booking rules are not satisfied."""


class AppointmentNotFoundError(Exception):
    """Raised when an appointment does not exist."""


def _validate_slot(
    db: Session,
    doctor: Doctor,
    target_date: date,
    start_time: time,
    end_time: time,
    *,
    exclude_appointment_id: int | None = None,
) -> None:
    if not doctor.available:
        raise AppointmentValidationError("Doctor is not available for bookings")

    if not is_valid_doctor_slot(doctor, target_date, start_time, end_time):
        raise AppointmentValidationError(
            "Requested time is not a valid appointment slot for this doctor"
        )

    slot_start = datetime.combine(target_date, start_time)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    if slot_start <= now:
        raise AppointmentValidationError("Cannot book an appointment in the past")

    if slot_start < now + MIN_LEAD_TIME:
        raise AppointmentValidationError(
            "Appointments must be booked at least 1 hour in advance"
        )

    query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.date == target_date,
        Appointment.start_time == start_time,
        Appointment.status == AppointmentStatus.BOOKED,
    )
    if exclude_appointment_id is not None:
        query = query.filter(Appointment.id != exclude_appointment_id)

    if query.first():
        raise DuplicateEntryError("An appointment for this slot has already been booked")


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

    _validate_slot(
        db,
        doctor,
        appointment_data.date,
        appointment_data.start_time,
        appointment_data.end_time,
    )

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


def cancel_appointment(
    db: Session,
    appointment_id: int,
    cancel_data: AppointmentCancel,
) -> Appointment:
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise AppointmentNotFoundError(
            f"Appointment with id {appointment_id} not found"
        )

    if appointment.status == AppointmentStatus.CANCELLED:
        raise AppointmentValidationError("Appointment is already cancelled")

    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancellation_reason = cancel_data.reason

    db.commit()
    db.refresh(appointment)
    return appointment


def reschedule_appointment(
    db: Session,
    appointment_id: int,
    reschedule_data: AppointmentReschedule,
) -> Appointment:
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise AppointmentNotFoundError(
            f"Appointment with id {appointment_id} not found"
        )

    if appointment.status == AppointmentStatus.CANCELLED:
        raise AppointmentValidationError("Cancelled appointments cannot be rescheduled")

    doctor = db.get(Doctor, appointment.doctor_id)
    if doctor is None:
        raise AppointmentValidationError(
            f"Doctor with id {appointment.doctor_id} not found"
        )

    # Same validation as a fresh booking; ignore this appointment so the
    # old slot does not count as "taken" while we move it.
    _validate_slot(
        db,
        doctor,
        reschedule_data.date,
        reschedule_data.start_time,
        reschedule_data.end_time,
        exclude_appointment_id=appointment.id,
    )

    # Moving date/time frees the original slot and reserves the new one.
    appointment.date = reschedule_data.date
    appointment.start_time = reschedule_data.start_time
    appointment.end_time = reschedule_data.end_time

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateEntryError("An appointment for this slot has already been booked")

    db.refresh(appointment)
    return appointment


def list_appointments(db: Session) -> list[Appointment]:
    return (
        db.query(Appointment)
        .order_by(Appointment.date, Appointment.start_time)
        .all()
    )
