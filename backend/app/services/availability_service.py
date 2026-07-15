from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.availability import Availability
from app.schemas.availability import AvailabilityCreate

class DuplicateEntryError(Exception):
    """Raised when a unique doctor id exists"""

def create_availability(db:Session, availability_data:AvailabilityCreate) -> Availability:
    availability = Availability(**availability_data.model_dump())

    db.add(availability)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateEntryError("The doctor already has their availability set")

    db.refresh(availability)
    return availability