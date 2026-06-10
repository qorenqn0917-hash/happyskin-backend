from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.user import User


class UserRepository:
    @staticmethod
    async def create(name: str, email: str, password_hash: str) -> User:
        user = User(name=name, email=email, password_hash=password_hash)
        async with AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user

    @staticmethod
    async def get_by_email(email: str) -> User | None:
        async with AsyncSessionLocal() as session:
            return await session.scalar(
                select(User).where(User.email == email)
            )

    @staticmethod
    async def get_by_id(user_id: str) -> User | None:
        async with AsyncSessionLocal() as session:
            return await session.scalar(
                select(User).where(User.id == user_id)
            )
