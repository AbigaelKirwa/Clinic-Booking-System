from datetime import datetime
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Patient(Base):
    __tablename__ = "patient"

    id: Mapped[int] = mapped_column(
        primary_key=True, 
        index=True
    )

    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    middle_name: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    email: Mapped[str | None] = mapped_column(
        String(60),
        nullable=True
    )

    phone: Mapped[str] = mapped_column(
        String(13),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now(),
        nullable = False
    )