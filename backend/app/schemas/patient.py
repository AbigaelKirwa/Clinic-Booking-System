from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PatientCreate(BaseModel):
    first_name: str
    middle_name: str | None = None
    last_name: str
    phone: str
    email: str | None = None


class PatientResponse(BaseModel):
    id: int
    first_name: str
    middle_name: str | None = None
    last_name: str
    phone: str
    email: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
