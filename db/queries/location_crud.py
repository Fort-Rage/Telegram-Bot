import logging
import os

from io import BytesIO
from aiogram.types import BufferedInputFile
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from uuid6 import UUID

from QR.create_qr import make_qr
from db.database import async_session_factory
from db.models import Location, City
from interface import CRUD
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class LocationObj(CRUD):
    async def create(self, session: async_session_factory, city: str, room: str) -> bool:
        try:
            try:
                city_enum = City(city)
            except ValueError:
                logger.error(f"Error while creating location: invalid city value — {city}")
                return False

            new_location = Location(city=city_enum, room=room)
            session.add(new_location)
            await session.flush()

            bot = os.getenv('BOT_NAME')

            qr_data = f"https://t.me/{bot}?start=location_{new_location.id}"
            qr_code_bytes = make_qr(qr_data)
            new_location.qr_code = qr_code_bytes

            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error while creating location (city={city}, room={room}): {e}")
            return False

    async def read(self, session: async_session_factory) -> list[Location]:
        try:
            result = await session.execute(select(Location))
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error while retrieving locations: {e}")
            return []

    async def update(self, session: async_session_factory, location_id: UUID, city: str, room: str) -> bool:
        try:
            location = await session.get(Location, location_id)
            if not location:
                return False

            location.city = city
            location.room = room
            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error while updating location (id={location_id}, city={city}, room={room}): {e}")
            return False

    async def remove(self, session: async_session_factory, location_id: UUID) -> bool:
        try:
            location = await session.get(Location, location_id)
            if location:
                await session.delete(location)
                await session.commit()
                return True
            else:
                return False
        except Exception as e:
            await session.rollback()
            logger.error(f"Error while removing location (id={location_id}): {e}")
            return False

    async def get_obj(self, session: async_session_factory, location_id: UUID) -> Location | None:
        try:
            location = await session.get(Location, location_id)
            if not location:
                return None
            return location
        except SQLAlchemyError as e:
            logger.error(f"Error while retrieving location (id={location_id}): {e}")
            return None

    @staticmethod
    async def get_location_id(session: async_session_factory, city: str, room: str) -> UUID | None:
        try:
            result = await session.execute(
                select(Location).where(Location.city == city, Location.room == room)
            )
            location = result.scalar_one_or_none()
            return location.id if location else None
        except SQLAlchemyError as e:
            logger.error(f"Error while retrieving location ID (city={city}, room={room}): {e}")
            return None

    @staticmethod
    async def get_cities():
        return [ct for ct in City]

    @staticmethod
    async def get_location_qr_code(session: async_session_factory, location_id: UUID) -> BufferedInputFile | None:
        try:
            location = await session.get(Location, location_id)
            if not location or not location.qr_code:
                return None

            qr_image = BytesIO(location.qr_code)
            input_file = BufferedInputFile(
                file=qr_image.getvalue(),
                filename="qr.png"
            )
            return input_file
        except SQLAlchemyError as e:
            logger.error(f"Error while retrieving QR code for location (id={location_id}): {e}")
            return None
