from datetime import datetime, time
from sqlalchemy import DateTime, String, func, Time, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Availability(Base):
    __tablename__ = "availability"

    id: Mapped[int] = mapped_column(
        primary_key=True, 
        index=True
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctor.id"),
        nullable=False,
        index=True,
        unique=True
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable = False
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable = False
    )

    available: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now(),
        nullable = False
    )