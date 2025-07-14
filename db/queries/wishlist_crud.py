import logging

from typing import Optional
from sqlalchemy import select
from uuid6 import UUID

from db.database import async_session_factory
from db.models import WishList
from db.queries.app_user_crud import AppUserObj
from interface import CRUD

logger = logging.getLogger(__name__)


class WishlistObj(CRUD):
    async def create(self, session, app_user_id: UUID, book_title: str, author: str,
                     comment: Optional[str] = None) -> bool:
        try:
            new_wishlist_item = WishList(app_user_id=app_user_id, book_title=book_title, author=author, comment=comment)
            session.add(new_wishlist_item)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(
                f"Error while creating WishList item (app_user_id={app_user_id}, book_title='{book_title}', "
                f"author='{author}', comment='{comment}'): {e}"
            )
            return False

    async def read(self, session: async_session_factory, app_user_id: UUID) -> list[WishList]:
        try:
            if await AppUserObj().is_admin(session=session, app_user_id=app_user_id):
                query = select(WishList)
            else:
                query = select(WishList).where(WishList.app_user_id == app_user_id)
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error while retrieving WishList items: {e}")
            return []

    async def update(self, session: async_session_factory, field: str, wish_id: UUID, new_value: str) -> bool:
        try:
            query = select(WishList).where(WishList.id == wish_id)
            result = await session.execute(query)
            wishlist_item = result.scalar_one_or_none()

            if wishlist_item:
                setattr(wishlist_item, field, new_value)
                await session.commit()
                return True
            return False
        except Exception as e:
            await session.rollback()
            field_name = field.replace('_', ' ')
            logger.error(
                f"Error while updating field '{field_name}' of WishList item (id={wish_id}) "
                f"to new value '{new_value}': {e}"
            )
            return False

    async def remove(self, session: async_session_factory, wish_id: UUID) -> bool:
        try:
            query = select(WishList).where(WishList.id == wish_id)
            result = await session.execute(query)
            wishlist_item = result.scalar_one_or_none()

            if wishlist_item:
                await session.delete(wishlist_item)
                await session.commit()
                return True
            return False
        except Exception as e:
            await session.rollback()
            logger.error(f"Error while removing WishList item with id={wish_id}: {e}")
            return False

    async def get_obj(self, session: async_session_factory, wish_id: UUID) -> WishList | None:
        try:
            query = select(WishList).where(WishList.id == wish_id)
            result = await session.execute(query)
            wishlist_item = result.scalar_one_or_none()
            return wishlist_item
        except Exception as e:
            logger.error(f"Error while retrieving WishList item (id={wish_id}): {e}")
            return None
