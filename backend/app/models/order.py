import uuid
import enum
from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, Enum as SAEnum, ARRAY, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base
from app.models.base_model import UUIDMixin, TimestampMixin


class OrderStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    IN_FABRICATION = "in_fabrication"
    QUALITY_CHECK = "quality_check"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderType(str, enum.Enum):
    STANDARD = "standard"
    CUSTOM = "custom"
    RUSH = "rush"
    REVISION = "revision"
    SAMPLE = "sample"


class UrgencyLevel(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Order(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "orders"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=True
    )
    job_area_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_areas.id"), nullable=True
    )

    request_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    requester_name: Mapped[str] = mapped_column(String(255), nullable=False)
    order_date: Mapped[str] = mapped_column(String(50), nullable=False)
    urgency: Mapped[UrgencyLevel] = mapped_column(SAEnum(UrgencyLevel), default=UrgencyLevel.NORMAL)
    piece_quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.DRAFT, nullable=False, index=True)
    order_type: Mapped[OrderType] = mapped_column(SAEnum(OrderType), default=OrderType.STANDARD, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    audit_history: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="orders")
    created_by_user: Mapped["User"] = relationship("User", back_populates="orders")
    job: Mapped["Job | None"] = relationship("Job", back_populates="orders")
    job_area: Mapped["JobArea | None"] = relationship("JobArea", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Order id={self.id} number={self.request_number} status={self.status}>"


class OrderItem(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "order_items"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fitting_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fittings.id"), nullable=True
    )
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    specifications: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    fitting: Mapped["Fitting | None"] = relationship("Fitting", back_populates="order_items")
