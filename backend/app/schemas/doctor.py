from pydantic import BaseModel, ConfigDict
from datetime import time, date

class DoctorCreate(BaseModel):
    first_name: str
    middle_name: str | None = None
    last_name: str | None = None
    email: str
    phone: str
    specialty: str | None
    start_time: time
    end_time: time
    available: bool

class DoctorResponse(BaseModel):
    id: int
    first_name: str
    middle_name: str | None = None
    last_name: str | None = None
    email: str
    phone: str
    specialty: str | None
    start_time: time
    end_time: time
    available: bool

    model_config = ConfigDict(from_attributes=True)

class TimeSlot(BaseModel):
    start_time: time
    end_time: time

class DoctorAvailabilityResponse(BaseModel):
    doctor_id: int
    date: date
    slots: list[TimeSlot]
