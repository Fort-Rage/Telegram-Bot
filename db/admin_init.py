import asyncio
import os

from dotenv import load_dotenv
from database import async_session_factory
from models import TelegramUsers

load_dotenv()


async def create_admin(session_factory):
    async with session_factory() as session:
        try:
            tg_id = os.getenv('ADMIN_TG_ID')
            user = TelegramUsers(telegram_id=str(tg_id), username='Vention')
            session.add(user)
            await session.commit()
            print('Admin created')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    asyncio.run(create_admin(async_session_factory))
