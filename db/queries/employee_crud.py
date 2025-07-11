import logging

from sqlalchemy import select
from db.database import async_session_factory
from db.models import Employees
from interface import CRUD

logger = logging.getLogger(__name__)


class EmployeeObj(CRUD):
    async def create(self):
        pass

    async def read(self):
        pass

    async def update(self):
        pass

    async def remove(self):
        pass

    async def get_obj(self):
        pass

    @staticmethod
    async def get_obj_by_email(session: async_session_factory, email: str) -> Employees | None:
        try:
            query = select(Employees).where(Employees.email == email)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error while retrieving employee by email {email}: {e}")
            return None
