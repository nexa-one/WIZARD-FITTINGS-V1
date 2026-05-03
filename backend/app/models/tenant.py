import uuid
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.models.base_model import UUIDMixin, TimestampMixin


class Tenant(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255))
    contact_phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(Text)
    logo_url: Mapped[str | None] = mapped_column(String(500))

    users: Mapped[list["User"]] = relationship("User", back_populates="tenant", lazy="select")
    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="tenant", lazy="select")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="tenant", lazy="select")
    fittings: Mapped[list["Fitting"]] = relationship("Fitting", back_populates="tenant", lazy="select")

    def __repr__(self) -> str:
        return f"<Tenant id={self.id} name={self.name}>"
