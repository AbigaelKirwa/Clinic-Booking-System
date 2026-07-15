from fastapi import FastAPI
from pydantic import BaseModel
from app.api.routes.patient import router as patient_router
from app.api.routes.doctor import router as doctor_router
from app.api.routes.appointment import router as appointment_router

app = FastAPI(
    title="Clinic Booking App"
)

app.include_router(patient_router)
app.include_router(doctor_router)
app.include_router(appointment_router)

@app.get("/health")
def health_check():
    return {"status":"healthy"}