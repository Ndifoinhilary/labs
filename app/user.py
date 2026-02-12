# app/user.py
import os
import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import UUIDIDMixin, BaseUserManager, FastAPIUsers
from fastapi_users.authentication import BearerTransport, JWTStrategy, AuthenticationBackend
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from app.db import User, get_user_db
from app.utils.email import send_email

SECRET = os.getenv("AUTH_SECRET", "change-me-in-env")

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        # Optionally auto-send verification email after register:
        token = await self.request_verify(user, request)
        # request_verify triggers on_after_request_verify below, where we actually send the email

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        # Send password reset email with token
        reset_link = f"{os.getenv('PUBLIC_APP_URL', 'http://localhost:8000')}/reset-password?token={token}"
        await send_email(
            to=user.email,
            subject="Reset your password",
            body=f"Use this link to reset your password: {reset_link}\nToken: {token}",
        )

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        # Send verification email with a token
        verify_link = f"{os.getenv('PUBLIC_APP_URL', 'http://localhost:8000')}/verify-email?token={token}"
        await send_email(
            to=user.email,
            subject="Verify your email",
            body=f"Click to verify: {verify_link}\nToken: {token}",
        )

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])
current_active_user = fastapi_users.current_user(active=True)