from pydantic import BaseModel, ConfigDict

class DoctorCreate(BaseModel):
    first_name: str
    middle_name: str | None = None
    last_name: str | None = None
    email: str
    phone: str
    specialty: str | None

class DoctorResponse(BaseModel):
    id: int
    first_name: str
    middle_name: str | None = None
    last_name: str | None = None
    email: str
    phone: str
    specialty: str | None

    model_config = ConfigDict(from_attributes=True)