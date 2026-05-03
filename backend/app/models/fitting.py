import uuid
import enum
from sqlalchemy import String, Boolean, ForeignKey, Numeric, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base
from app.models.base_model import UUIDMixin, TimestampMixin


class FittingType(str, enum.Enum):
    ELBOW = "elbow"
    TEE = "tee"
    REDUCER = "reducer"
    OFFSET = "offset"
    TRANSITION = "transition"
    CAP = "cap"
    DUCT = "duct"
    CUSTOM = "custom"


class MaterialType(str, enum.Enum):
    GALVANIZED = "galvanized"
    STAINLESS_304 = "stainless_304"
    STAINLESS_316 = "stainless_316"
    ALUMINUM = "aluminum"
    BLACK_IRON = "black_iron"
    PVC = "pvc"


class ConnectionType(str, enum.Enum):
    SLIP = "slip"
    DRIVE = "drive"
    FLANGED = "flanged"
    GROOVED = "grooved"
    WELDED = "welded"


class Fitting(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "fittings"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    fitting_type: Mapped[FittingType] = mapped_column(SAEnum(FittingType), nullable=False)
    material: Mapped[MaterialType] = mapped_column(SAEnum(MaterialType), default=MaterialType.GALVANIZED)
    connection_type: Mapped[ConnectionType] = mapped_column(SAEnum(ConnectionType), default=ConnectionType.SLIP)

    # Dimensions stored as structured JSON
    dimensions: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    # 3D geometry data (Three.js compatible)
    geometry_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    # Engineering validation results
    engineering_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    gauge: Mapped[str | None] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(Text)
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="fittings")
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="fitting")
    requests: Mapped[list["FittingRequest"]] = relationship("FittingRequest", back_populates="fitting")

    def __repr__(self) -> str:
        return f"<Fitting id={self.id} type={self.fitting_type} name={self.name}>"


class FittingRequest(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "fitting_requests"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    fitting_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("fittings.id"), nullable=True)
    requested_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    suggested_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    missing_fields: Mapped[list] = mapped_column(JSONB, default=list)
    validation_result: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(50), default="pending")

    fitting: Mapped["Fitting | None"] = relationship("Fitting", back_populates="requests")
