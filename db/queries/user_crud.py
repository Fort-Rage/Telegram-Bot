import logging

from sqlalchemy import select
from db.database import async_session_factory
from db.models import User
from interface import CRUD

logger = logging.getLogger(__name__)


class UserObj(CRUD):
    async def create(self, session: async_session_factory, telegram_id: int, name: str, surname: str):
        try:
            if await self.is_user_registered(session=session, telegram_id=telegram_id):
                return False
            new_user = User(telegram_id=telegram_id, name=name, surname=surname)
            session.add(new_user)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error when creating a user: {e}")
            return False

    async def read(self, session: async_session_factory):
        try:
            result = await session.execute(select(User))
            users = result.scalars().all()
            return users
        except Exception as e:
            logger.error(f"Error when retrieving users: {e}")
            return []

    async def update(self):
        pass

    async def remove(self):
        pass

    async def get_obj(self, session: async_session_factory, telegram_id: int):
        try:
            query = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(query)
            selected_user = result.scalars().one_or_none()
            return selected_user
        except Exception as e:
            logger.error(f"Error when retrieving user: {e}")
            return None

    @staticmethod
    async def is_user_registered(session: async_session_factory, telegram_id: int):
        try:
            query = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(query)
            selected_user = result.scalars().first()
            return selected_user is not None
        except Exception as e:
            logger.error(f"Error when checking user existence: {e}")
            return False

    @staticmethod
    async def get_user_id_by_name(session: async_session_factory, name: str, surname: str):
        try:
            result = await session.execute(select(User).where(User.name == name and User.surname == surname))
            user = result.scalars().first()

            if user:
                user_id = user.telegram_id
                return int(user_id)
            else:
                return None
        except Exception as e:
            logger.error(f"Error when retrieving user id: {e}")
            return None

    @staticmethod
    async def is_admin(session: async_session_factory, telegram_id: int):
        try:
            result = await session.get(User, telegram_id)
            return result.is_admin
        except Exception as e:
            logger.error(f"Error when checking admin status for user: {e}")
            return False
