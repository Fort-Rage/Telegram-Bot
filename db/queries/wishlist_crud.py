import logging

from typing import Optional
from sqlalchemy import select
from db.database import async_session_factory
from db.models import WishList
from db.queries.app_user_crud import AppUserObj
from interface import CRUD

logger = logging.getLogger(__name__)


class WishlistObj(CRUD):
    async def create(self, session, user_id: int, book_title: str, author: str,
                     comment: Optional[str] = None):
        try:
            new_wishlist_item = WishList(user_id=user_id, book_title=book_title, author=author, comment=comment)
            session.add(new_wishlist_item)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error when adding to wishlist: {e}")
            return False

    async def read(self, session: async_session_factory, user_id: int):
        try:
            if await UserObj().is_admin(telegram_id=user_id, session=session):
                query = select(WishList)
            else:
                query = select(WishList).where(WishList.user_id == user_id)
            result = await session.execute(query)
            wishlist_items = result.scalars().all()
            return wishlist_items
        except Exception as e:
            logger.error(f"Error when retrieving wishlists: {e}")
            return []

    async def update(self, session: async_session_factory, field: str, wish_id: int, new_value: str):
        try:
            query = select(WishList).where(WishList.wish_list_id == wish_id)
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
            logger.error(f"Error when updating {field_name}: {e}")
            return False

    async def remove(self, session: async_session_factory, wish_id: int):
        try:
            query = select(WishList).where(WishList.wish_list_id == wish_id)
            result = await session.execute(query)
            wishlist_item = result.scalar_one_or_none()

            if wishlist_item:
                await session.delete(wishlist_item)
                await session.commit()
                return True
            return False
        except Exception as e:
            await session.rollback()
            logger.error(f"Error when removing from wishlist: {e}")
            return False

    async def get_obj(self, session: async_session_factory, wish_id: int):
        try:
            query = select(WishList).where(WishList.wish_list_id == wish_id)
            result = await session.execute(query)
            wishlist_item = result.scalar_one_or_none()
            return wishlist_item
        except Exception as e:
            logger.error(f"Error when retrieving wishlist item: {e}")
            return None
