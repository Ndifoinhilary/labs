import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    # Uses email & password from BaseUserCreate
    pass


class UserUpdate(schemas.BaseUserUpdate):
    # Optional fields to update (email/password)
    pass
