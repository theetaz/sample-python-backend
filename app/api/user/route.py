from fastapi import APIRouter, Depends, Body, status, HTTPException
from fastapi.responses import Response
from sqlmodel.ext.asyncio.session import AsyncSession
from app.common.http_response_model import CommonResponse
from app.database import db_session
from app.api.user.service import UserService
from app.schemas import UpdateUser, ChangePasswordRequest
from app.auth.auth_handler import AuthHandler


router = APIRouter()


@router.patch("/update", name="Update user details")
async def register_user(
        response: Response,
        update_user: UpdateUser = Body(...),
        email: str = Depends(AuthHandler()),
        session: AsyncSession = Depends(db_session)) -> CommonResponse:
    try:

        user_service = UserService(session)
        user = await user_service.update_user(email, update_user)

        payload = CommonResponse(
            message="User has been updated successfully",
            success=True,
            payload=user,
            meta=None
        )
        response.status_code = status.HTTP_200_OK
        return payload

    except HTTPException as http_err:
        payload = CommonResponse(
            success=False,
            message=str(http_err.detail),
            payload=None
        )
        response.status_code = http_err.status_code
        return payload

    except Exception as e:
        payload = CommonResponse(
            success=False,
            message=str(e),
            payload=None
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return payload


@router.delete("/delete", name="Delete user details")
async def register_user(
        response: Response,
        email: str = Depends(AuthHandler()),
        session: AsyncSession = Depends(db_session)) -> CommonResponse:
    try:

        user_service = UserService(session)
        user = await user_service.delete_user(email)

        payload = CommonResponse(
            message="User has been deleted successfully",
            success=True,
            payload=user,
            meta=None
        )
        response.status_code = status.HTTP_200_OK
        return payload

    except HTTPException as http_err:
        payload = CommonResponse(
            success=False,
            message=str(http_err.detail),
            payload=None
        )
        response.status_code = http_err.status_code
        return payload

    except Exception as e:
        payload = CommonResponse(
            success=False,
            message=str(e),
            payload=None
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return payload


@router.patch("/change-password", name="Change current logged in user password")
async def change_current_user_password(
        response: Response,
        email: str = Depends(AuthHandler()),
        change_password: ChangePasswordRequest = Body(...),
        session: AsyncSession = Depends(db_session)) -> CommonResponse:
    try:
        user_service = UserService(session)
        is_changed = await user_service.change_password(email, change_password.current_password, change_password.new_password)

        payload = CommonResponse(
            message="User password has changed successfully",
            success=True,
            payload=is_changed,
            meta=None
        )
        response.status_code = status.HTTP_200_OK
        return payload

    except HTTPException as http_err:
        payload = CommonResponse(
            success=False,
            message=str(http_err.detail),
            payload=None
        )
        response.status_code = http_err.status_code
        return payload

    except Exception as e:
        payload = CommonResponse(
            success=False,
            message=str(e),
            payload=None
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return payload
