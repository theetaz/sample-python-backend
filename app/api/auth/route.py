from fastapi import APIRouter, Depends, Body, status, HTTPException
from fastapi.responses import Response
from sqlmodel.ext.asyncio.session import AsyncSession
from app.common.http_response_model import CommonResponse
from app.database import db_session
from app.api.auth.service import AuthService
from app.schemas import CreateUser, RefreshToken, LoginUser, SsoUserLoginRequest, PasswordResetRequest, PasswordResetRequestRequest
from app.auth.auth_handler import AuthHandler

router = APIRouter()


@router.post("/register", name="Register new user")
async def register_user(
        response: Response,
        create_user: CreateUser = Body(...),
        session: AsyncSession = Depends(db_session)):

    try:

        user_service = AuthService(session)
        user = await user_service.create_user(create_user)

        payload = CommonResponse(
            message="User has been created successfully",
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


# login a user
@router.post("/login", name="Login user")
async def login_user(
        response: Response,
        user_data: LoginUser = Body(...),
        session: AsyncSession = Depends(db_session)):

    try:

        user_service = AuthService(session)
        access_token = await user_service.authenticate_user(user_data.email, user_data.password.encode('utf-8'))

        payload = CommonResponse(
            message="User has been authorized in successfully",
            success=True,
            payload=access_token,
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


@router.post("/token/refresh", name="Refresh user token")
async def refresh_user_token(
        response: Response,
        refresh_token_data: RefreshToken = Body(...),
        session: AsyncSession = Depends(db_session)):
    try:
        user_service = AuthService(session)
        access_token = await user_service.get_access_token_using_refresh_token(refresh_token_data.refresh_token)

        payload = CommonResponse(
            message="Token has been refreshed successfully",
            success=True,
            payload=access_token,
            meta=None
        )
        response.status_code = status.HTTP_200_OK
        return payload

    except Exception as e:
        payload = CommonResponse(
            success=False,
            message=str(e),
            payload=None
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return payload


@router.get("/me", name="Get current user by token")
async def get_user_by_token(
        response: Response,
        email: str = Depends(AuthHandler()),
        session: AsyncSession = Depends(db_session)):
    try:
        user_service = AuthService(session)
        user = await user_service.get_user_by_email(email)

        payload = CommonResponse(
            message="User Fetched successfully",
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


# rest the password of a user
@router.post("/reset-password", name="Rest the password of a user")
async def reset_user_password(
        response: Response,
        reset_password: PasswordResetRequest = Body(...),
        session: AsyncSession = Depends(db_session)):

    try:

        user_service = AuthService(session)
        user = await user_service.rest_user_password(reset_password.new_password, reset_password.token)

        payload = CommonResponse(
            message="Password has been reset successfully",
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

# send reset password email


@router.post("/reset-password-email", name="Send reset password email")
async def trigger_rest_password_email(
        response: Response,
        password_rest: PasswordResetRequestRequest = Body(...),
        session: AsyncSession = Depends(db_session)):

    try:

        user_service = AuthService(session)
        user = await user_service.send_reset_password_email(password_rest.email)

        payload = CommonResponse(
            message="Password reset email has been sent successfully",
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
