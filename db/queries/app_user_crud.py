import logging

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid6 import UUID

from db.database import async_session_factory
from db.models import AppUsers
from db.queries.role_crud import RoleObj
from db.queries.tg_user_crud import TgUserObj
from interface import CRUD

logger = logging.getLogger(__name__)


class AppUserObj(CRUD):
    async def create(self, session: async_session_factory, telegram_id: str, tg_user_id: UUID, employee_id: UUID,
                     role_id: UUID) -> bool:
        try:
            if await self.is_user_registered(session=session, telegram_id=telegram_id):
                return False
            new_user = AppUsers(tg_user_id=tg_user_id, employee_id=employee_id, role_id=role_id)
            session.add(new_user)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(
                f"Error while creating AppUser (tg_user_id={tg_user_id}, employee_id={employee_id}, "
                f"role_id={role_id}, telegram_id={telegram_id}): {e}"
            )
            return False

    async def read(self, session: async_session_factory) -> list[AppUsers]:
        try:
            result = await session.execute(select(AppUsers))
            users = result.scalars().all()
            return users
        except Exception as e:
            logger.error(f"Error while retrieving users: {e}")
            return []

    async def update(self):
        pass

    async def remove(self):
        pass

    async def get_obj(self, session: async_session_factory, app_user_id: UUID) -> AppUsers | None:
        try:
            query = select(AppUsers).where(AppUsers.id == app_user_id)
            result = await session.execute(query)
            app_user = result.scalar_one_or_none()
            return app_user
        except Exception as e:
            logger.error(f"Error while retrieving app user (id={app_user_id}): {e}")
            return None

    @staticmethod
    async def is_user_registered(session: async_session_factory, telegram_id: str) -> bool:
        try:
            tg_user = await TgUserObj().get_obj_by_telegram_id(session=session, telegram_id=telegram_id)
            if not tg_user:
                return False

            query = select(AppUsers).where(AppUsers.tg_user_id == tg_user.id)
            result = await session.execute(query)
            app_user = result.scalar_one_or_none()

            return app_user is not None
        except Exception as e:
            logger.error(f"Error while checking if user is registered (telegram_id={telegram_id}): {e}")
            return False

    # TODO: change function
    # @staticmethod
    # async def get_user_id_by_name(session: async_session_factory, name: str, surname: str):
    #     try:
    #         result = await session.execute(select(AppUsers).where(User.name == name and User.surname == surname))
    #         user = result.scalars().first()
    #
    #         if user:
    #             user_id = user.telegram_id
    #             return int(user_id)
    #         else:
    #             return None
    #     except Exception as e:
    #         logger.error(f"Error when retrieving user id: {e}")
    #         return None

    @staticmethod
    async def is_admin(session: async_session_factory, app_user_id: UUID) -> bool:
        try:
            app_user = await AppUserObj().get_obj(session=session, app_user_id=app_user_id)
            if not app_user:
                return False

            role = await RoleObj().get_obj(session=session, role_id=app_user.role_id)
            if not role:
                return False

            return role.name.lower() == 'admin'
        except Exception as e:
            logger.error(f"Error while checking admin status (app_user_id={app_user_id}): {e}")
            return False

    @staticmethod
    async def get_app_user_id(session: async_session_factory, telegram_id: str) -> UUID | None:
        try:
            tg_user = await TgUserObj().get_obj_by_telegram_id(session=session, telegram_id=telegram_id)
            if not tg_user:
                return None

            query = select(AppUsers).where(AppUsers.tg_user_id == tg_user.id)
            result = await session.execute(query)
            app_user = result.scalar_one_or_none()

            if not app_user:
                return None
            return app_user.id
        except Exception as e:
            logger.error(f"Error while getting AppUser id by telegram_id={telegram_id}: {e}")
            return None

    @staticmethod
    async def get_employee_fullname(session: async_session_factory, app_user_id: UUID) -> str | None:
        try:
            query = (
                select(AppUsers)
                .options(selectinload(AppUsers.employee))
                .where(AppUsers.id == app_user_id)
            )
            result = await session.execute(query)
            app_user = result.scalar_one_or_none()

            if not app_user:
                return None

            if not app_user.employee:
                return None

            return app_user.employee.full_name

        except Exception as e:
            logger.error(f"Error while getting employee fullname for AppUser id={app_user_id}: {e}")
            return None
