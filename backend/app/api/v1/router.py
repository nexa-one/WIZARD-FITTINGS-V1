from fastapi import APIRouter
from app.api.v1.endpoints import auth, orders, fittings, users

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(fittings.router, prefix="/fittings", tags=["Fittings"])
