from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from rotoger import Rotoger
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.user import User
from schemas.user import TokenResponse, UserLogin, UserResponse, UserSchema
from services.auth import create_access_token

router = APIRouter(prefix="/v1/user")
logger = Rotoger().get_logger()


@router.post("/", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def create_user(
    payload: UserSchema,
    request: Request,
    db_session: AsyncSession = Depends(get_db)
):
    await logger.ainfo(f"Creating user: {payload}")
    _user: User = User(
        **payload.model_dump(),
    )
    await _user.save(db_session)
    _user.access_token = await create_access_token(_user, request)
    return _user


@router.post("/token", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def get_token_for_user(
    user: Annotated[UserLogin, Form()],
    request: Request,
    db_session: AsyncSession = Depends(get_db),

):
    _user: User = await User.find(db_session, [User.email == user.email])
    if not _user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not _user.check_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is incorrect"
        )

    _token = await create_access_token(
        _user, request
    )
    return {"access_token": _token, "token_type": "bearer"}
