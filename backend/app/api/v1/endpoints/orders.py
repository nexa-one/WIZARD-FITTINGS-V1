from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderSearchFilters
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.order_service import create_order, get_order, update_order, delete_order, search_orders
from app.models.order import OrderStatus, OrderType, UrgencyLevel
from typing import Optional, List

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_new_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = await create_order(db, data, current_user)
    return _serialize_order(order)


@router.get("/search", response_model=PaginatedResponse)
async def search_orders_endpoint(
    search: Optional[str] = Query(None),
    status: Optional[OrderStatus] = Query(None),
    order_type: Optional[OrderType] = Query(None),
    urgency: Optional[UrgencyLevel] = Query(None),
    job_id: Optional[str] = Query(None),
    created_by: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    filters = OrderSearchFilters(
        search=search, status=status, order_type=order_type,
        urgency=urgency, job_id=job_id, created_by=created_by,
        date_from=date_from, date_to=date_to, page=page, page_size=page_size,
    )
    result = await search_orders(db, filters, current_user.tenant_id)
    serialized_items = [_serialize_order(o) for o in result.items]
    return PaginatedResponse(
        items=serialized_items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_endpoint(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = await get_order(db, order_id, current_user.tenant_id)
    return _serialize_order(order)


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order_endpoint(
    order_id: str,
    data: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = await update_order(db, order_id, data, current_user)
    return _serialize_order(order)


@router.delete("/{order_id}", response_model=MessageResponse)
async def delete_order_endpoint(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await delete_order(db, order_id, current_user)
    return MessageResponse(message="Order deleted successfully")


def _serialize_order(order) -> dict:
    items = []
    for item in (order.items or []):
        items.append({
            "id": str(item.id),
            "order_id": str(item.order_id),
            "description": item.description,
            "quantity": item.quantity,
            "unit": item.unit,
            "notes": item.notes,
            "sort_order": item.sort_order,
            "specifications": item.specifications or {},
            "fitting_id": str(item.fitting_id) if item.fitting_id else None,
        })
    return {
        "id": str(order.id),
        "request_number": order.request_number,
        "requester_name": order.requester_name,
        "order_date": order.order_date,
        "urgency": order.urgency,
        "piece_quantity": order.piece_quantity,
        "status": order.status,
        "order_type": order.order_type,
        "notes": order.notes,
        "tags": order.tags or [],
        "tenant_id": str(order.tenant_id),
        "created_by": str(order.created_by),
        "job_id": str(order.job_id) if order.job_id else None,
        "job_area_id": str(order.job_area_id) if order.job_area_id else None,
        "items": items,
        "created_at": order.created_at.isoformat() if order.created_at else "",
        "updated_at": order.updated_at.isoformat() if order.updated_at else "",
    }
