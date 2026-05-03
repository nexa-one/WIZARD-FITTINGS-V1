import uuid
import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from app.models.fitting import Fitting
from app.models.user import User
from app.schemas.fitting import FittingCreate, FittingUpdate
from app.schemas.common import PaginatedResponse
from app.engines.geometry_engine import compute_fitting_geometry


async def create_fitting(db: AsyncSession, data: FittingCreate, current_user: User) -> Fitting:
    dims = data.dimensions.model_dump(exclude_none=True)
    geometry = compute_fitting_geometry(data.fitting_type.value, dims)

    fitting = Fitting(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        name=data.name,
        fitting_type=data.fitting_type,
        material=data.material,
        connection_type=data.connection_type,
        dimensions=dims,
        geometry_data=geometry,
        engineering_data={},
        gauge=data.gauge,
        description=data.description,
        is_template=data.is_template,
    )
    db.add(fitting)
    await db.flush()
    return fitting


async def get_fitting(db: AsyncSession, fitting_id: str, tenant_id: uuid.UUID) -> Fitting:
    result = await db.execute(
        select(Fitting).where(Fitting.id == uuid.UUID(fitting_id), Fitting.tenant_id == tenant_id)
    )
    fitting = result.scalar_one_or_none()
    if not fitting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fitting not found")
    return fitting


async def update_fitting(db: AsyncSession, fitting_id: str, data: FittingUpdate, current_user: User) -> Fitting:
    fitting = await get_fitting(db, fitting_id, current_user.tenant_id)
    update_data = data.model_dump(exclude_none=True)

    if "dimensions" in update_data:
        dims = update_data["dimensions"]
        if isinstance(dims, dict):
            fitting.dimensions = {**fitting.dimensions, **dims}
            fitting.geometry_data = compute_fitting_geometry(fitting.fitting_type.value, fitting.dimensions)
        del update_data["dimensions"]

    for field, value in update_data.items():
        setattr(fitting, field, value)

    await db.flush()
    return fitting


async def list_fittings(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
    fitting_type: str = None,
) -> PaginatedResponse:
    query = select(Fitting).where(Fitting.tenant_id == tenant_id)
    if fitting_type:
        query = query.where(Fitting.fitting_type == fitting_type)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    query = query.order_by(Fitting.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 0,
    )
