import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from uuid6 import UUID

from db.database import async_session_factory
from db.models import Roles
from interface import CRUD

logger = logging.getLogger(__name__)


class RoleObj(CRUD):
    async def create(self):
        pass

    async def read(self):
        pass

    async def update(self):
        pass

    async def remove(self):
        pass

    async def get_obj(self, session: async_session_factory, role_id: UUID) -> Roles | None:
        try:
            if not role_id:
                return None

            role = await session.get(Roles, role_id)
            return role
        except SQLAlchemyError as e:
            logger.error(f"Error while retrieving role (id={role_id}): {e}")
            return None

    @staticmethod
    async def get_obj_by_name(session: async_session_factory, name: str) -> Roles | None:
        try:
            if not name:
                return None

            query = select(Roles).where(Roles.name == name)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error while retrieving role by name ({name}): {e}")
            return None
