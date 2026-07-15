import enum
from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Index, String, Time, func, text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class AppointmentStatus(str, enum.Enum):
    BOOKED = "booked"
    CANCELLED = "cancelled"


class Appointment(Base):
    __tablename__ = "appointment"
    __table_args__ = (
        Index(
            "uq_doctor_date_start_booked",
            "doctor_id",
            "date",
            "start_time",
            unique=True,
            postgresql_where=text("status = 'booked'::appointment_status"),
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True, 
        index=True
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctor.id"),
        nullable=False,
        index=True,
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient.id"),
        nullable=False,
        index=True,
    )

    date: Mapped[date] = mapped_column(Date, nullable=False)

    start_time: Mapped[time] = mapped_column(Time, nullable=False)

    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    status: Mapped[AppointmentStatus] = mapped_column(
        SqlEnum(
            AppointmentStatus,
            name="appointment_status",
            values_callable=lambda statuses: [status.value for status in statuses],
        ),
        nullable=False,
    )

    cancellation_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
