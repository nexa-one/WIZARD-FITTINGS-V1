import uuid
import math
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderCreate, OrderUpdate, OrderSearchFilters
from app.schemas.common import PaginatedResponse


def _uuid_str(val) -> str:
    """Normalize a UUID value to string for dialect-portable comparison."""
    if val is None:
        return None
    return str(uuid.UUID(str(val)))


async def create_order(db: AsyncSession, data: OrderCreate, current_user: User) -> Order:
    order = Order(
        request_number=data.request_number,
        requester_name=data.requester_name,
        order_date=data.order_date,
        urgency=data.urgency,
        piece_quantity=data.piece_quantity,
        status=data.status,
        order_type=data.order_type,
        notes=data.notes,
        tags=data.tags,
        job_id=_uuid_str(data.job_id) if data.job_id else None,
        job_area_id=_uuid_str(data.job_area_id) if data.job_area_id else None,
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        audit_history=[{"action": "created", "user": str(current_user.id)}],
    )
    db.add(order)
    await db.flush()

    for item_data in data.items:
        item = OrderItem(
            order_id=order.id,
            fitting_id=_uuid_str(item_data.fitting_id) if item_data.fitting_id else None,
            description=item_data.description,
            quantity=item_data.quantity,
            unit=item_data.unit,
            notes=item_data.notes,
            sort_order=item_data.sort_order,
            specifications=item_data.specifications,
        )
        db.add(item)

    await db.flush()
    await db.refresh(order)
    return order


async def get_order(db: AsyncSession, order_id: str, tenant_id) -> Order:
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == _uuid_str(order_id), Order.tenant_id == str(tenant_id))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


async def update_order(db: AsyncSession, order_id: str, data: OrderUpdate, current_user: User) -> Order:
    order = await get_order(db, order_id, current_user.tenant_id)
    update_data = data.model_dump(exclude_none=True)

    for field, value in update_data.items():
        setattr(order, field, value)

    audit_entry = {"action": "updated", "user": str(current_user.id), "fields": list(update_data.keys())}
    order.audit_history = (order.audit_history or []) + [audit_entry]
    await db.flush()
    return order


async def delete_order(db: AsyncSession, order_id: str, current_user: User) -> None:
    order = await get_order(db, order_id, current_user.tenant_id)
    await db.delete(order)


async def search_orders(
    db: AsyncSession,
    filters: OrderSearchFilters,
    tenant_id,
) -> PaginatedResponse:
    query = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.tenant_id == str(tenant_id))
    )

    if filters.search:
        term = f"%{filters.search}%"
        query = query.where(
            or_(
                Order.request_number.ilike(term),
                Order.requester_name.ilike(term),
                Order.notes.ilike(term),
            )
        )
    if filters.status:
        query = query.where(Order.status == filters.status)
    if filters.order_type:
        query = query.where(Order.order_type == filters.order_type)
    if filters.urgency:
        query = query.where(Order.urgency == filters.urgency)
    if filters.job_id:
        query = query.where(Order.job_id == _uuid_str(filters.job_id))
    if filters.created_by:
        query = query.where(Order.created_by == _uuid_str(filters.created_by))
    if filters.date_from:
        query = query.where(Order.order_date >= filters.date_from)
    if filters.date_to:
        query = query.where(Order.order_date <= filters.date_to)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    offset = (filters.page - 1) * filters.page_size
    query = query.order_by(Order.created_at.desc()).offset(offset).limit(filters.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        pages=math.ceil(total / filters.page_size) if total > 0 else 0,
    )
