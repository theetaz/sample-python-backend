from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import db_session
from app.models import User
from app.schemas import CreateUser, SsoUserLoginRequest
from app.config import settings
from app.auth.token_handler import JWTTokenHandler
from app.auth.auth_handler import AuthHandler


class AuthService:
    def __init__(
            self,
            session: AsyncSession = Depends(db_session),
            token_handler: JWTTokenHandler = JWTTokenHandler(),
            auth_handler: AuthHandler = AuthHandler()) -> None:
        self.session = session
        self.SECRET_KEY = settings.JWT_SECRET_KEY
        self.ALGORITHM = settings.JWT_ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.REFRESH_TOKEN_EXPIRE_MINUTES = settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES
        self.token_handler = token_handler
        self.auth_handler = auth_handler

    # get a user by email

    async def get_user_by_email(self, email: str) -> User:
        user_record = await self.session.execute(select(User).where(User.email == email))
        user = user_record.scalar_one_or_none()
        return user

    # create a new user

    async def create_user(self, new_user: CreateUser) -> User:
        user = await self.get_user_by_email(new_user.email)
        if user:
            raise HTTPException(
                status_code=400, detail="User with this email already exists")

        # hash password before saving into the db
        hashed_password = self.auth_handler.hash_password(new_user.password)

        user = User(
            name=new_user.name,
            email=new_user.email,
            hashed_password=hashed_password
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        # we need to send an email with activation link to the user // TODO
        return user

    async def authenticate_user(self, email: str, password: str) -> User:
        user = await self.get_user_by_email(email)

        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="User not found", headers={"WWW-Authenticate": "Bearer"})

        is_valid_password = self.auth_handler.verify_password(
            password, user.hashed_password)
        if not is_valid_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})

        access_token = self.token_handler.create_access_token(
            data={"sub": user.email})
        refresh_token = self.token_handler.create_refresh_token(
            data={"sub": user.email})
        return {
            "user": user,
            "access_token": access_token,
            "refresh_token":
            refresh_token,
            "token_type": "bearer"}

    async def get_access_token_using_refresh_token(self, refresh_token: str):

        email = await self.token_handler.validate_refresh_token(refresh_token)
        user = await self.get_user_by_email(email)

        if user is None:
            raise HTTPException(status_code=400, detail="User not found")

        access_token = self.token_handler.create_access_token(
            data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

    async def login_sso_user(self, sso_user: SsoUserLoginRequest):

        # check if user exists for given email and provider is null
        user = await self.get_user_by_email(sso_user.email)

        if user is None:
            # create a new user with random password
            password = self.auth_handler.generate_random_password()
            hashed_password = self.auth_handler.hash_password(str(password))

            user = User(
                name=sso_user.name,
                email=sso_user.email,
                hashed_password=hashed_password,
                profile_image=sso_user.image,
                provider=sso_user.provider,
                provider_id=sso_user.provider_id
            )

            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            access_token = self.token_handler.create_access_token(
                data={"sub": user.email})
            refresh_token = self.token_handler.create_refresh_token(
                data={"sub": user.email})
            return {
                "user": user,
                "access_token": access_token,
                "refresh_token":
                refresh_token,
                "token_type": "bearer"
            }

        else:

            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            access_token = self.token_handler.create_access_token(
                data={"sub": user.email})
            refresh_token = self.token_handler.create_refresh_token(
                data={"sub": user.email})
            return {
                "user": user,
                "access_token": access_token,
                "refresh_token":
                refresh_token,
                "token_type": "bearer"
            }

    async def send_reset_password_email(self, email: str):

        token = self.auth_handler.generate_token_for_rest_password_email(email)
        link = f"/auth/reset-password?token={token}"

        # TODO: add mail service to send actual mail
        return link

    async def rest_user_password(self, password: str, token: str):
        email = self.auth_handler.verify_reset_password_token(token)

        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")

        # get user by email
        user = await self.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=400, detail="User not found with provided email")

        # update user password
        hashed_password = self.auth_handler.hash_password(password)
        user.hashed_password = hashed_password.decode('utf-8')
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
