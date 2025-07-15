import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from db.database import async_session_factory
from db.models import TelegramUsers
from interface import CRUD

logger = logging.getLogger(__name__)


class TgUserObj(CRUD):
    async def create(self, session: async_session_factory, telegram_id: str, username: str) -> bool:
        try:
            new_tg_user = TelegramUsers(telegram_id=telegram_id, username=username)
            session.add(new_tg_user)
            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error while creating TgUser (telegram_id={telegram_id}, username={username}): {e}")
            return False

    async def read(self):
        pass

    async def update(self):
        pass

    async def remove(self):
        pass

    async def get_obj(self):
        pass

    @staticmethod
    async def get_obj_by_telegram_id(session: async_session_factory, telegram_id: str) -> TelegramUsers | None:
        try:
            query = select(TelegramUsers).where(TelegramUsers.telegram_id == telegram_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error while retrieving telegram user by telegram id ({telegram_id}): {e}")
            return None
