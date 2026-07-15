from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.appointment import (
    AppointmentCancel,
    AppointmentCreate,
    AppointmentReschedule,
    AppointmentResponse,
)
from app.services.appointment_service import (
    AppointmentNotFoundError,
    AppointmentValidationError,
    DuplicateEntryError,
    cancel_appointment as cancel_appointment_service,
    create_appointment as create_appointment_service,
    list_appointments as list_appointments_service,
    reschedule_appointment as reschedule_appointment_service,
)

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment_data: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        return create_appointment_service(db, appointment_data)
    except AppointmentValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except DuplicateEntryError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get("/", response_model=list[AppointmentResponse], status_code=status.HTTP_200_OK)
def list_appointments(db: Session = Depends(get_db)):
    return list_appointments_service(db)


@router.patch(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
)
def cancel_appointment(
    appointment_id: int,
    cancel_data: AppointmentCancel,
    db: Session = Depends(get_db),
):
    try:
        return cancel_appointment_service(db, appointment_id, cancel_data)
    except AppointmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except AppointmentValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{appointment_id}/reschedule",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
)
def reschedule_appointment(
    appointment_id: int,
    reschedule_data: AppointmentReschedule,
    db: Session = Depends(get_db),
):
    try:
        return reschedule_appointment_service(db, appointment_id, reschedule_data)
    except AppointmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except AppointmentValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except DuplicateEntryError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
