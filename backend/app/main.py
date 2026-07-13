from fastapi import FastAPI
from pydantic import BaseModel
from app.api.routes.patients import router as patients_router

app = FastAPI(
    title="Clinic Booking App"
)

app.include_router(patients_router)

@app.get("/health")
def health_check():
    return {"status":"healthy"}