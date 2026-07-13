from pydantic import BaseModel, ConfigDict
from datetime import time

class AvailabilityCreate(BaseModel):
    doctor_id: int
    start_time: time
    end_time: time
    available: bool

class AvailabilityResponse(BaseModel):
    doctor_id: int
    start_time: time
    end_time: time
    available: bool

    model_config = ConfigDict(from_attributes=True)