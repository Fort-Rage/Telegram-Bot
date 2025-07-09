import logging
from io import BytesIO

from aiogram.types import BufferedInputFile
from sqlalchemy import select, delete, exists
from sqlalchemy.exc import SQLAlchemyError
from QR.create_qr import make_qr
from db.models import Book, BookCategory, Category, Location, Order, OrderStatus
from interface import CRUD


class BookObj(CRUD):

    async def create(self, title, author, description, owner_id, categories, location_id, session):
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

            qr_data = f"https://t.me/ZhidaoCnBot?start=book_{book.book_id}"
            qr_code_bytes = make_qr(qr_data)
            book.qr_code = qr_code_bytes

            await session.commit()
            return book

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(e)
            return None

    async def read(self, session, available_books: bool = True):
        try:
            if available_books:
                result = await session.execute(
                    select(Book).filter(
                        ~exists().where(
                            (Order.book_id == Book.book_id) &
                            (Order.status.in_([OrderStatus.RESERVED, OrderStatus.IN_PROCESS]))
                        )
                    )
                )
            else:
                result = await session.execute(select(Book))

            books = result.scalars().all()
            return books

        except SQLAlchemyError as e:
            logging.error(f"=== Database error: {e}")
            return None

    async def update(self, book_id: int, updates: dict, session):
        try:
            book = await session.get(Book, book_id)

            for field, value in updates.items():
                if field != "categories":
                    setattr(book, field, value)

                if field == "owner_id":
                    setattr(book, field, int(value))

            if "categories" in updates:
                selected_categories = updates["categories"].split(", ")
                selected_categories_enum = []

                for category in selected_categories:
                    try:
                        category_key = category.upper().replace(" ", "_")
                        selected_categories_enum.append(Category[category_key])
                    except KeyError:
                        return None

                current_categories = await session.execute(
                    select(BookCategory).where(BookCategory.book_id == book_id)
                )
                current_categories = current_categories.scalars().all()
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
            return book

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"=== Database error: {e}")
            return None

    async def remove(self, book_id, session):
        try:
            delete_book = await session.execute(
                delete(Book)
                .where(Book.book_id == book_id)
                .returning(Book.book_id)
            )

            if delete_book.scalar_one_or_none():
                await session.execute(
                    delete(BookCategory)
                    .where(BookCategory.book_id == book_id)
                )
                await session.commit()
                return True

            return False

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"=== Database error: {e}")
            return False

    async def get_obj(self, book_id, session):
        try:
            book = await session.get(Book, book_id)
            return book
        except SQLAlchemyError as e:
            logging.error(f"=== Database error: {e}")
            return None

    @staticmethod
    async def get_book_categories(book_id, session):
        result = await session.execute(select(BookCategory.category).where(BookCategory.book_id == book_id))
        categories = result.scalars().all()
        return [Category(cat).value for cat in categories]

    @staticmethod
    async def get_categories():
        return [cat for cat in Category]

    @staticmethod
    async def get_book_location(loc_id: int, session):
        try:
            location = await session.get(Location, loc_id)
            return location
        except SQLAlchemyError as e:
            logging.error(f"{e}")

    @staticmethod
    async def get_book_qr(book_id, session):
        book = await session.get(Book, book_id)
        if book:
            qr_image = BytesIO(book.qr_code)
            input_file = BufferedInputFile(
                file=qr_image.getvalue(),
                filename="qr.png"
            )
            return input_file
        else:
            return None
