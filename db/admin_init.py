import asyncio
import os

from dotenv import load_dotenv
from database import async_session_factory
from models import TelegramUsers, Employees, Roles, AppUsers

load_dotenv()


async def create_admin(session_factory):
    async with session_factory() as session:
        try:
            tg_id = os.getenv('ADMIN_TG_ID')
            username = os.getenv('ADMIN_USERNAME')
            full_name = os.getenv('ADMIN_FULLNAME')
            email = os.getenv('ADMIN_EMAIL')
            role = os.getenv('ADMIN_ROLE')

            tg_user = TelegramUsers(telegram_id=str(tg_id), username=str(username))
            session.add(tg_user)
            await session.flush()

            employee = Employees(full_name=full_name, email=email)
            session.add(employee)
            await session.flush()

            role = Roles(name=role)
            session.add(role)
            await session.flush()

            app_user = AppUsers(
                tg_user_id=tg_user.id,
                employee_id=employee.id,
                role_id=role.id
            )
            session.add(app_user)

            await session.commit()
            print('Admin created')

        except Exception as e:
            await session.rollback()
            print(f"Error during admin creation: {e}")


if __name__ == '__main__':
    asyncio.run(create_admin(async_session_factory))
