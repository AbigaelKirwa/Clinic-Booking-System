from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.services.appointment_service import (
    AppointmentValidationError,
    DuplicateEntryError,
    create_appointment as create_appointment_service,
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
