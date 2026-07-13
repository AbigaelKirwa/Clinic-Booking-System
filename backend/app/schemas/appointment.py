from pydantic import BaseModel, ConfigDict
from datetime import time, date

class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_id: int
    date: date
    start_time: time
    end_time: time

class AppointmentResponse(BaseModel):
    doctor_id: int
    patient_id: int
    date: date
    start_time: time
    end_time: time
    status: str

    model_config = ConfigDict(from_attributes=True)