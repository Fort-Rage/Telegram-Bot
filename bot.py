import os
import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from handlers import registration_handler, wishlist_handlers, order_handlers, location_handlers
from handlers.book_handlers import book_router

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(location_handlers.router)
dp.include_router(registration_handler.router)
dp.include_router(wishlist_handlers.router)
dp.include_router(book_router)
dp.include_router(order_handlers.router)


async def main():
    print('Bot is running...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print('Exit')
    finally:
        loop.close()
