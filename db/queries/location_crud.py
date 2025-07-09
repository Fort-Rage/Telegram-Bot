import logging
from io import BytesIO

from aiogram.types import BufferedInputFile
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from QR.create_qr import make_qr
from interface import CRUD
from db.models import Location, City


class LocationObj(CRUD):

    async def read(self, session):
        try:
            result = await session.execute(select(Location))
            locations = result.scalars().all()
            return locations
        except SQLAlchemyError as e:
            logging.error(f"=== Database error: {e}")
            return None

    async def create(self, city: str, room: str, session):
        try:
            try:
                city_enum = City(city)
            except ValueError:
                logging.error(f"Invalid city value: {city}")
                return False

            new_location = Location(city=city_enum, room=room)
            session.add(new_location)
            await session.flush()

            qr_data = f"https://t.me/ZhidaoCnBot?start=location_{new_location.location_id}"
            qr_code_bytes = make_qr(qr_data)
            new_location.qr_code = qr_code_bytes

            await session.commit()
            return True

        except SQLAlchemyError as e:
            logging.error(f"=== Database error: {e}")
            await session.rollback()
            return None

    async def update(self, location_id, city, room, session):
        location = await session.get(Location, location_id)
        if location:
            try:
                location.city = city
                location.room = room
                await session.commit()
                return location
            except SQLAlchemyError as e:
                await session.rollback()
                logging.error(f"=== Database error: {e}")

        return None

    async def remove(self, location_id, session):
        try:
            location = await session.get(Location, location_id)
            if location:
                await session.delete(location)
                await session.commit()
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"=== Database error: {e}")
            await session.rollback()
            return None

    async def get_obj(self, location_id, session):
        try:
            location = await session.get(Location, location_id)
            return location.room if location else None

        except SQLAlchemyError as e:
            logging.error(f"=== Database error: {e}")

    @staticmethod
    async def get_location_id(city: str, room: str, session):
        try:
            result = await session.execute(
                select(Location).where(Location.city == city, Location.room == room)
            )
            location = result.scalars().one_or_none()
            return location.location_id if location else None
        except SQLAlchemyError as e:
            logging.error(f"=== Database error: {e}")

    @staticmethod
    async def get_cities():
        return [ct for ct in City]

    @staticmethod
    async def get_qr_code(location_id, session):
        book = await session.get(Location, location_id)
        if book:
            qr_image = BytesIO(book.qr_code)
            input_file = BufferedInputFile(
                file=qr_image.getvalue(),
                filename="qr.png"
            )
            return input_file
        else:
            return None
