from pydantic import BaseModel, ConfigDict

class PatientCreate(BaseModel):
    first_name: str
    middle_name: str | None = None
    last_name: str | None = None
    email: str
    phone: str
    specialty: str | None

class PatientResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)