from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.patient import PatientCreate, PatientResponse
from app.services.patient_service import (
    DuplicatePatientError,
    create_patient as create_patient_service,
    list_patients as list_patients_service,
    list_patient as list_patient_service
)

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient_data: PatientCreate, db: Session = Depends(get_db)):
    try:
        return create_patient_service(db, patient_data)
    except DuplicatePatientError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get("/", response_model=list[PatientResponse], status_code=status.HTTP_200_OK)
def list_patients(db: Session = Depends(get_db)):
    return list_patients_service(db)


@router.get("/{patient_id}", response_model=PatientResponse, status_code=status.HTTP_200_OK)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = list_patient_service(db, patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} not found",
        )
    return patient
