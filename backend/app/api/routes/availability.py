from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.availability import AvailabilityCreate, AvailabilityResponse
from app.services.availability_service  import (
    DuplicateEntryError,
    create_availability as create_availability_service
)

router = APIRouter(
    prefix="/availability",
    tags=["Availability"]
)

@router.post("/", response_model=AvailabilityResponse, status_code=status.HTTP_201_CREATED)
def create_availability(availability_data:AvailabilityCreate, db:Session = Depends(get_db)):
    try:
        return create_avaiability_service(db, availability_Data)
    except DuplicateEntryError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        ) from exc