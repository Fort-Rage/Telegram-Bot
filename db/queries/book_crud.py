import logging
import os

from aiogram.types import BufferedInputFile
from sqlalchemy import select, delete, exists
from sqlalchemy.exc import SQLAlchemyError
from uuid6 import UUID

from QR.create_qr import make_qr
from db.database import async_session_factory
from db.models import Book, BookCategory, Category, Order, OrderStatus
from interface import CRUD
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class BookObj(CRUD):
    async def create(self, session: async_session_factory, title: str, author: str, description: str, owner_id: UUID,
                     categories: list, location_id: UUID) -> bool:
        try:
            book = Book(
                title=title,
                description=description,
                author=author,
                owner_id=owner_id,
                location_id=location_id,
            )

            for category in categories:
                book.book_categories.append(BookCategory(category=category))

            session.add(book)
            await session.flush()

            bot = os.getenv('BOT_NAME')

            qr_data = f"https://t.me/{bot}?start=book_{book.id}"
            qr_code_bytes = make_qr(qr_data)
            book.qr_code = qr_code_bytes

            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error while creating Book (title='{title}', author='{author}', "
                         f"owner_id={owner_id}, location_id='{location_id}'): {e}")
            return False

    async def read(self, session: async_session_factory, available_books: bool = True) -> list[Book]:
        try:
            if available_books:
                result = await session.execute(
                    select(Book).filter(
                        ~exists().where(
                            (Order.book_id == Book.id) &
                            (Order.status.in_([OrderStatus.RESERVED, OrderStatus.IN_PROCESS]))
                        )
                    )
                )
            else:
                result = await session.execute(select(Book))

            books = result.scalars().all()
            return books
        except SQLAlchemyError as e:
            logger.error(f"Error while retrieving books: {e}")
            return []

    async def update(self, session: async_session_factory, book_id: UUID, updates: dict) -> bool:
        try:
            book = await session.get(Book, book_id)

            if not book:
                return False

            for field, value in updates.items():
                if field == "owner_id":
                    setattr(book, field, value)
                elif field == "description":
                    setattr(book, field, value if value != '-' else None)
                elif field != "categories":
                    setattr(book, field, value)

            if "categories" in updates:
                selected_categories = updates["categories"].split(", ")
                selected_categories_enum = []

                for category in selected_categories:
                    try:
                        category_key = category.upper().replace(" ", "_")
                        selected_categories_enum.append(Category[category_key])
                    except KeyError:
                        logger.warning(f"Invalid category '{category}' provided for Book id={book_id}. Update aborted.")
                        return False

                result = await session.execute(
                    select(BookCategory).where(BookCategory.book_id == book_id)
                )
                current_categories = result.scalars().all()
                current_categories_enum = {bc.category for bc in current_categories}

                removing_categories = current_categories_enum - set(selected_categories_enum)
                new_categories = set(selected_categories_enum) - current_categories_enum

                if removing_categories:
                    await session.execute(
                        delete(BookCategory)
                        .where(BookCategory.book_id == book_id)
                        .where(BookCategory.category.in_(removing_categories))
                    )

                for category in new_categories:
                    session.add(BookCategory(book_id=book_id, category=category))

            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error while updating Book with id={book_id}: {e}")
            return False

    async def remove(self, session: async_session_factory, book_id: UUID) -> bool:
        try:
            delete_book = await session.execute(
                delete(Book)
                .where(Book.id == book_id)
                .returning(Book.id)
            )

            deleted_id = delete_book.scalar_one_or_none()

            if not deleted_id:
                return False

            await session.execute(
                delete(BookCategory)
                .where(BookCategory.book_id == book_id)
            )
            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error while removing Book with id={book_id}: {e}")
            return False

    async def get_obj(self, session: async_session_factory, book_id: UUID) -> Book | None:
        try:
            book = await session.get(Book, book_id)
            return book
        except SQLAlchemyError as e:
            logger.error(f"Error while retrieving Book with id={book_id}: {e}")
            return None

    @staticmethod
    async def get_book_categories(session: async_session_factory, book_id: UUID) -> list:
        try:
            result = await session.execute(
                select(BookCategory.category).where(BookCategory.book_id == book_id)
            )
            categories = result.scalars().all()
            return [Category(cat).value for cat in categories]
        except SQLAlchemyError as e:
            logger.error(f"Error while retrieving categories for Book with id={book_id}: {e}")
            return []

    @staticmethod
    async def get_categories():
        return [cat for cat in Category]

    @staticmethod
    async def get_book_qr_code(session: async_session_factory, book_id: UUID) -> BufferedInputFile | None:
        try:
            book = await session.get(Book, book_id)
            if not book or not book.qr_code:
                return None

            input_file = BufferedInputFile(
                file=book.qr_code,
                filename="qr.png"
            )
            return input_file
        except SQLAlchemyError as e:
            logger.error(f"Error while retrieving QR code for Book (id={book_id}): {e}")
            return None

    @staticmethod
    async def get_books_by_location(session: async_session_factory, location_id: UUID) -> list[Book]:
        try:
            result = await session.execute(
                select(Book).where(Book.location_id == location_id)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error when retrieving books by location (id={location_id}): {e}")
            return []
