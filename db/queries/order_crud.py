import logging

from typing import Optional
from sqlalchemy import select, case
from sqlalchemy.orm import joinedload

from db.database import async_session_factory
from db.models import Order, OrderStatus, Book
from db.queries.app_user_crud import AppUserObj
from interface import CRUD

logger = logging.getLogger(__name__)


class OrderObj(CRUD):
    async def create(self, session: async_session_factory, user_id: int, book_id: int, status=OrderStatus.RESERVED,
                     taken_from_id: Optional[int] = None, returned_to_id: Optional[int] = None):
        try:
            new_order = Order(
                telegram_id=user_id,
                book_id=book_id,
                status=status,
                taken_from_id=taken_from_id,
                returned_to_id=returned_to_id
            )
            session.add(new_order)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error when adding order: {e}")
            return False

    async def read(self, session: async_session_factory, user_id: int):
        try:
            status_order = case(
                (Order.status == OrderStatus.RESERVED, 0),
                (Order.status == OrderStatus.IN_PROCESS, 1),
                (Order.status == OrderStatus.RETURNED, 2),
                (Order.status == OrderStatus.CANCELLED, 2),
            )

            if await UserObj().is_admin(session=session, telegram_id=user_id):
                query = select(Order).options(
                    joinedload(Order.book),
                    joinedload(Order.taken_from),
                    joinedload(Order.returned_to),
                ).order_by(status_order)
            else:
                query = select(Order).where(Order.telegram_id == user_id).options(
                    joinedload(Order.book),
                    joinedload(Order.taken_from),
                    joinedload(Order.returned_to),
                ).order_by(status_order)

            result = await session.execute(query)
            orders = result.scalars().all()
            return orders
        except Exception as e:
            logger.error(f"Error when retrieving orders: {e}")
            return []

    async def update(self, session: async_session_factory):
        pass

    async def remove(self, session: async_session_factory, order_id: int):
        try:
            query = select(Order).where(Order.order_id == order_id)
            result = await session.execute(query)
            order = result.scalar_one_or_none()

            if order:
                await session.delete(order)
                await session.commit()
                return True
            return False
        except Exception as e:
            await session.rollback()
            logger.error(f"Error when removing order: {e}")
            return False

    async def get_obj(self, session: async_session_factory, order_id: int):
        try:
            query = select(Order).where(Order.order_id == order_id).options(
                    joinedload(Order.book),
                    joinedload(Order.taken_from),
                    joinedload(Order.returned_to),
                )
            result = await session.execute(query)
            order = result.scalar_one_or_none()
            return order
        except Exception as e:
            logger.error(f"Error when retrieving order: {e}")
            return None

    @staticmethod
    async def update_status(session: async_session_factory, order_id: int, new_status: str):
        try:
            query = select(Order).where(Order.order_id == order_id)
            result = await session.execute(query)
            order = result.scalar_one_or_none()

            if order:
                order.status = new_status
                await session.commit()
                return True
            return False
        except Exception as e:
            await session.rollback()
            logger.error(f"Error when updating status of order: {e}")
            return False

    @staticmethod
    async def update_status_and_location(
            session: async_session_factory,
            order_id: int,
            new_status: str,
            location_id: int
    ):
        try:
            query = select(Order).where(Order.order_id == order_id)
            result = await session.execute(query)
            order = result.scalar_one_or_none()

            if order:
                order.status = new_status
                order.returned_to_id = location_id

                query_book = select(Book).where(Book.book_id == order.book_id)
                result_book = await session.execute(query_book)
                book = result_book.scalar_one_or_none()

                if book:
                    book.location_id = location_id
                    await session.commit()
                    return True
            return False
        except Exception as e:
            await session.rollback()
            logger.error(f"Error when updating status and location of order: {e}")
            return False

    @staticmethod
    async def is_order_exist(user_id, book_id, session):
        try:
            order = await session.scalar(
                select(Order).where(
                    Order.telegram_id == user_id,
                    Order.book_id == book_id,
                    Order.status == OrderStatus.RESERVED
                )
            )
            if order:
                order.status = OrderStatus.IN_PROCESS
                await session.commit()
                return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error when checking if order {e}")
            return False

    @staticmethod
    async def is_book_taken(session, book_id):
        book_taken = await session.scalar(
            select(Order).where(
                Order.book_id == book_id,
                Order.status == OrderStatus.IN_PROCESS
            )
        )
        return True if book_taken else False
