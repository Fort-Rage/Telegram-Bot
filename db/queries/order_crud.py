import logging

from typing import Optional
from sqlalchemy import select, case
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from uuid6 import UUID

from db.database import async_session_factory
from db.models import Order, OrderStatus, Book
from db.queries.app_user_crud import AppUserObj
from interface import CRUD

logger = logging.getLogger(__name__)


class OrderObj(CRUD):
    async def create(self, session: async_session_factory, app_user_id: UUID, book_id: UUID,
                     taken_from_id: UUID, returned_to_id: Optional[UUID] = None,
                     status: OrderStatus = OrderStatus.RESERVED) -> bool:
        try:
            new_order = Order(
                app_user_id=app_user_id,
                book_id=book_id,
                status=status,
                taken_from_id=taken_from_id,
                returned_to_id=returned_to_id
            )
            session.add(new_order)
            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error when creating order: {e}")
            return False

    async def read(self, session: async_session_factory, app_user_id: UUID) -> list[Order]:
        try:
            status_order = case(
                (Order.status == OrderStatus.RESERVED, 0),
                (Order.status == OrderStatus.IN_PROCESS, 1),
                (Order.status == OrderStatus.RETURNED, 2),
                (Order.status == OrderStatus.CANCELLED, 2),
            )

            options = (
                joinedload(Order.book),
                joinedload(Order.taken_from),
                joinedload(Order.returned_to),
            )

            is_admin = await AppUserObj().is_admin(session=session, app_user_id=app_user_id)
            query = select(Order).options(*options).order_by(status_order)
            if not is_admin:
                query = query.where(Order.app_user_id == app_user_id)

            result = await session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error when retrieving orders: {e}")
            return []

    async def update(self, session: async_session_factory):
        pass

    async def remove(self, session: async_session_factory, order_id: UUID) -> bool:
        try:
            order = await session.get(Order, order_id)
            if not order:
                return False

            await session.delete(order)
            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error when removing order (id={order_id}): {e}")
            return False

    async def get_obj(self, session: async_session_factory, order_id: UUID) -> Order | None:
        try:
            query = select(Order).where(Order.id == order_id).options(
                joinedload(Order.book),
                joinedload(Order.taken_from),
                joinedload(Order.returned_to),
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error when retrieving order (id={order_id}): {e}")
            return None

    @staticmethod
    async def update_status(session: async_session_factory, order_id: UUID, new_status: OrderStatus) -> bool:
        try:
            order = await session.get(Order, order_id)
            if not order:
                return False

            order.status = new_status
            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error when updating status of order (id={order_id}): {e}")
            return False

    @staticmethod
    async def update_status_and_location(session: async_session_factory, order_id: UUID, new_status: OrderStatus,
                                         location_id: UUID) -> bool:
        try:
            order = await session.get(Order, order_id)
            if not order:
                return False

            book = await session.get(Book, order.book_id)
            if not book:
                return False

            order.status = new_status
            order.returned_to_id = location_id
            book.location_id = location_id

            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(
                f"Error when updating status and location of order "
                f"(order_id={order_id}, status={new_status}, location_id={location_id}): {e}"
            )
            return False

    @staticmethod
    async def is_order_exist(session: async_session_factory, app_user_id: UUID, book_id: UUID) -> bool:
        try:
            order = await session.scalar(
                select(Order).where(
                    Order.app_user_id == app_user_id,
                    Order.book_id == book_id,
                    Order.status == OrderStatus.RESERVED
                )
            )
            if not order:
                return False

            order.status = OrderStatus.IN_PROCESS
            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(
                f"Error when checking if reserved order exists (app_user_id={app_user_id}, book_id={book_id}): {e}"
            )
            return False

    @staticmethod
    async def is_book_taken(session: async_session_factory, book_id: UUID) -> bool:
        try:
            order = await session.scalar(
                select(Order).where(
                    Order.book_id == book_id,
                    Order.status == OrderStatus.IN_PROCESS
                )
            )
            return bool(order)
        except SQLAlchemyError as e:
            logger.error(f"Error when checking if book is taken (id={book_id}: {e}")
            return False
