from pydantic import BaseModel, ConfigDict

class DoctorCreate(BaseModel):
    first_name: str
    middle_name: str | None = None
    last_name: str | None = None
    phone: str

class DoctorResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)