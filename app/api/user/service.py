from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import db_session
from app.models import User
from app.schemas import UpdateUser
from app.config import settings
from app.auth.token_handler import JWTTokenHandler
from app.auth.auth_handler import AuthHandler

class UserService:
  def __init__(
        self, 
        # auth_handler: AuthHandler = AuthHandler(),
        session:AsyncSession = Depends(db_session),
         auth_handler:AuthHandler = AuthHandler()
        ) -> None:
    self.session = session
    self.auth_handler = auth_handler
    

  # get a user by email
  async def get_user_by_email(self, email: str) -> User:
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")
    user_record = await self.session.execute(select(User).where(User.email == email))
    user = user_record.scalar_one_or_none()
    return user

  # update user by user email
  async def update_user(self, email: str, update_data: UpdateUser) -> User:
    user = await self.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data_dict = update_data.dict(exclude_unset=True)
    if 'email' in update_data_dict:
        existing_user = await self.get_user_by_email(update_data_dict['email'])
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already in use")

    for field, value in update_data_dict.items():
        setattr(user, field, value)

    self.session.add(user)
    await self.session.commit()
    await self.session.refresh(user)

    # updated user values
    return user
  
  # delete user by user email
  async def delete_user(self, email: str) -> bool:
    user = await self.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await self.session.delete(user)
    await self.session.commit()
    return True
  
   # change user password
  async def change_password(self, email: str, current_password:str, new_password: str) -> bool:
    user = await self.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # check if current password is correct
    is_valid_password = self.auth_handler.verify_password(current_password.encode("utf-8"), user.hashed_password) 
    if not is_valid_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
 
    # hash new password
    hashed_password = self.auth_handler.hash_password(new_password)
    user.hashed_password = hashed_password.decode("utf-8")

    self.session.add(user)
    await self.session.commit()
    await self.session.refresh(user)
    return True
    