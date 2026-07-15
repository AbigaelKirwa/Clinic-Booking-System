from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.doctor import DoctorAvailabilityResponse, DoctorCreate, DoctorResponse
from app.services.doctor_service import (
    DuplicateEntryError,
    create_doctor as create_doctor_service,
    list_doctor as list_doctor_service,
    list_doctor_available_slots as list_doctor_available_slots_service,
    list_doctors as list_doctors_service,
)

router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"],
)


@router.post("/", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(doctor_data: DoctorCreate, db: Session = Depends(get_db)):
    try:
        return create_doctor_service(db, doctor_data)
    except DuplicateEntryError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get("/", response_model=list[DoctorResponse], status_code=status.HTTP_200_OK)
def list_doctors(db: Session = Depends(get_db)):
    return list_doctors_service(db)


@router.get("/{doctor_id}", response_model=DoctorResponse, status_code=status.HTTP_200_OK)
def list_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = list_doctor_service(db, doctor_id)
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {doctor_id} not found",
        )
    return doctor


@router.get(
    "/{doctor_id}/availability",
    response_model=DoctorAvailabilityResponse,
    status_code=status.HTTP_200_OK,
)
def list_doctor_available_slots(
    doctor_id: int,
    date: date,
    db: Session = Depends(get_db),
):
    availability = list_doctor_available_slots_service(db, doctor_id, date)
    if availability is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {doctor_id} not found",
        )
    return availability
