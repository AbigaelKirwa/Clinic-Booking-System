from pydantic import BaseModel, ConfigDict, Field
from datetime import time, date


class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_id: int
    date: date
    start_time: time
    end_time: time


class AppointmentCancel(BaseModel):
    reason: str = Field(min_length=1, max_length=255)


class AppointmentReschedule(BaseModel):
    date: date
    start_time: time
    end_time: time


class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    date: date
    start_time: time
    end_time: time
    status: str
    cancellation_reason: str | None = None

    model_config = ConfigDict(from_attributes=True)
