from datetime import date, datetime, time, timedelta

from app.models.doctor import Doctor
from app.schemas.doctor import TimeSlot

SLOT_DURATION = timedelta(minutes=30)


def generate_doctor_slots(doctor: Doctor, target_date: date) -> list[TimeSlot]:
    """Generate all valid 30-minute slots from the doctor's working hours."""
    slots: list[TimeSlot] = []
    cursor = datetime.combine(target_date, doctor.start_time)
    end = datetime.combine(target_date, doctor.end_time)

    while cursor + SLOT_DURATION <= end:
        slots.append(
            TimeSlot(
                start_time=cursor.time(),
                end_time=(cursor + SLOT_DURATION).time(),
            )
        )
        cursor += SLOT_DURATION

    return slots


def is_valid_doctor_slot(
    doctor: Doctor,
    target_date: date,
    start_time: time,
    end_time: time,
) -> bool:
    requested = TimeSlot(start_time=start_time, end_time=end_time)
    return requested in generate_doctor_slots(doctor, target_date)
