from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.fitting import FittingCreate, FittingUpdate, FittingResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.fitting_service import create_fitting, get_fitting, update_fitting, list_fittings

router = APIRouter()


@router.post("/", response_model=FittingResponse, status_code=status.HTTP_201_CREATED)
async def create_fitting_endpoint(
    data: FittingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    fitting = await create_fitting(db, data, current_user)
    return _serialize_fitting(fitting)


@router.get("/", response_model=PaginatedResponse)
async def list_fittings_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    fitting_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await list_fittings(db, current_user.tenant_id, page, page_size, fitting_type)
    return PaginatedResponse(
        items=[_serialize_fitting(f) for f in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/{fitting_id}", response_model=FittingResponse)
async def get_fitting_endpoint(
    fitting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    fitting = await get_fitting(db, fitting_id, current_user.tenant_id)
    return _serialize_fitting(fitting)


@router.patch("/{fitting_id}", response_model=FittingResponse)
async def update_fitting_endpoint(
    fitting_id: str,
    data: FittingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    fitting = await update_fitting(db, fitting_id, data, current_user)
    return _serialize_fitting(fitting)


def _serialize_fitting(fitting) -> dict:
    return {
        "id": str(fitting.id),
        "name": fitting.name,
        "fitting_type": fitting.fitting_type,
        "material": fitting.material,
        "connection_type": fitting.connection_type,
        "dimensions": fitting.dimensions or {},
        "geometry_data": fitting.geometry_data or {},
        "engineering_data": fitting.engineering_data or {},
        "gauge": fitting.gauge,
        "description": fitting.description,
        "is_validated": fitting.is_validated,
        "is_template": fitting.is_template,
        "tenant_id": str(fitting.tenant_id),
        "created_by": str(fitting.created_by),
        "created_at": fitting.created_at.isoformat() if fitting.created_at else "",
        "updated_at": fitting.updated_at.isoformat() if fitting.updated_at else "",
    }
