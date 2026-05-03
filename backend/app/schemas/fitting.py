from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from app.models.fitting import FittingType, MaterialType, ConnectionType


class FittingDimensions(BaseModel):
    width_inlet: Optional[float] = None
    height_inlet: Optional[float] = None
    width_outlet: Optional[float] = None
    height_outlet: Optional[float] = None
    diameter_inlet: Optional[float] = None
    diameter_outlet: Optional[float] = None
    length: Optional[float] = None
    angle: Optional[float] = None
    radius: Optional[float] = None
    offset_x: Optional[float] = None
    offset_y: Optional[float] = None
    neck_width: Optional[float] = None
    neck_height: Optional[float] = None


class FittingCreate(BaseModel):
    name: str
    fitting_type: FittingType
    material: MaterialType = MaterialType.GALVANIZED
    connection_type: ConnectionType = ConnectionType.SLIP
    dimensions: FittingDimensions = FittingDimensions()
    gauge: Optional[str] = None
    description: Optional[str] = None
    is_template: bool = False


class FittingUpdate(BaseModel):
    name: Optional[str] = None
    material: Optional[MaterialType] = None
    connection_type: Optional[ConnectionType] = None
    dimensions: Optional[FittingDimensions] = None
    gauge: Optional[str] = None
    description: Optional[str] = None


class FittingResponse(BaseModel):
    id: str
    name: str
    fitting_type: FittingType
    material: MaterialType
    connection_type: ConnectionType
    dimensions: Dict[str, Any]
    geometry_data: Dict[str, Any]
    engineering_data: Dict[str, Any]
    gauge: Optional[str]
    description: Optional[str]
    is_validated: bool
    is_template: bool
    tenant_id: str
    created_by: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}
