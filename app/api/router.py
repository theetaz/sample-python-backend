from fastapi.routing import APIRouter
from app.api.user.route import router as user_router
from app.api.auth.route import router as auth_router
from app.api.complaint.route import router as complaint_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(
    complaint_router, prefix="/complaint", tags=["complaint"])
