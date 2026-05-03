from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.models.order import OrderStatus, OrderType, UrgencyLevel


class OrderItemCreate(BaseModel):
    description: str
    quantity: int = 1
    unit: Optional[str] = None
    notes: Optional[str] = None
    sort_order: int = 0
    specifications: Dict[str, Any] = {}
    fitting_id: Optional[str] = None


class OrderItemResponse(OrderItemCreate):
    id: str
    order_id: str

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    request_number: str
    requester_name: str
    order_date: str
    urgency: UrgencyLevel = UrgencyLevel.NORMAL
    piece_quantity: int = 1
    status: OrderStatus = OrderStatus.DRAFT
    order_type: OrderType = OrderType.STANDARD
    notes: Optional[str] = None
    tags: List[str] = []
    job_id: Optional[str] = None
    job_area_id: Optional[str] = None
    items: List[OrderItemCreate] = []


class OrderUpdate(BaseModel):
    requester_name: Optional[str] = None
    order_date: Optional[str] = None
    urgency: Optional[UrgencyLevel] = None
    piece_quantity: Optional[int] = None
    status: Optional[OrderStatus] = None
    order_type: Optional[OrderType] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    job_id: Optional[str] = None
    job_area_id: Optional[str] = None


class OrderResponse(BaseModel):
    id: str
    request_number: str
    requester_name: str
    order_date: str
    urgency: UrgencyLevel
    piece_quantity: int
    status: OrderStatus
    order_type: OrderType
    notes: Optional[str]
    tags: List[str]
    tenant_id: str
    created_by: str
    job_id: Optional[str]
    job_area_id: Optional[str]
    items: List[OrderItemResponse] = []
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class OrderSearchFilters(BaseModel):
    search: Optional[str] = None
    status: Optional[OrderStatus] = None
    order_type: Optional[OrderType] = None
    urgency: Optional[UrgencyLevel] = None
    job_id: Optional[str] = None
    created_by: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    tags: Optional[List[str]] = None
    page: int = 1
    page_size: int = 20
