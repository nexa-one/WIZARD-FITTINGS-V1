import uuid
from sqlalchemy import String, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.db.types import UUIDType
from app.models.base_model import UUIDMixin, TimestampMixin


class Job(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "jobs"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_number: Mapped[str | None] = mapped_column(String(100), index=True)
    client_name: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="jobs")
    areas: Mapped[list["JobArea"]] = relationship("JobArea", back_populates="job", cascade="all, delete-orphan")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="job")

    def __repr__(self) -> str:
        return f"<Job id={self.id} name={self.name}>"


class JobArea(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "job_areas"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    floor_level: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    job: Mapped["Job"] = relationship("Job", back_populates="areas")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="job_area")
