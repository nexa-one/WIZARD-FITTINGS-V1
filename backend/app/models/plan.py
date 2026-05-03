import uuid
import enum
from sqlalchemy import String, Boolean, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.db.types import UUIDType, PortableEnum
from app.models.base_model import UUIDMixin, TimestampMixin


class PlanTier(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Plan(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "plans"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tier: Mapped[PlanTier] = mapped_column(PortableEnum(PlanTier), nullable=False)
    price_monthly: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    price_yearly: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    max_users: Mapped[int] = mapped_column(Integer, default=5)
    max_orders_per_month: Mapped[int] = mapped_column(Integer, default=100)
    max_storage_gb: Mapped[int] = mapped_column(Integer, default=5)
    features: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="plan")


class Subscription(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "subscriptions"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("tenants.id", ondelete="CASCADE"))
    plan_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("plans.id"))
    status: Mapped[SubscriptionStatus] = mapped_column(PortableEnum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    starts_at: Mapped[str | None] = mapped_column(String(50))
    ends_at: Mapped[str | None] = mapped_column(String(50))

    plan: Mapped["Plan"] = relationship("Plan", back_populates="subscriptions")
