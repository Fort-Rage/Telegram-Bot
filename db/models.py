import enum

from typing import Optional
from sqlalchemy import ForeignKey, Integer, String, Enum, Boolean, DateTime, func, BigInteger, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    surname: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    books: Mapped[list["Book"]] = relationship(back_populates="owner")
    wish_list: Mapped[list["WishList"]] = relationship(back_populates="user")
    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class Category(str, enum.Enum):
    PROGRAMMING = "Programming"
    DATA_SCIENCE = "Data Science"
    MACHINE_LEARNING = "Machine Learning"
    ARTIFICIAL_INTELLIGENCE = "Artificial Intelligence"
    CYBERSECURITY = "Cybersecurity"
    SOFTWARE_ENGINEERING = "Software Engineering"
    DATABASES = "Databases"
    WEB_DEVELOPMENT = "Web Development"
    DEVOPS = "DevOps"
    ALGORITHMS = "Algorithms"


class Book(Base):
    __tablename__ = "books"

    book_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    author: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.location_id", ondelete="CASCADE"), nullable=False)
    created: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    qr_code: Mapped[LargeBinary] = mapped_column(LargeBinary, nullable=True)

    owner: Mapped["User"] = relationship(back_populates="books")
    location: Mapped["Location"] = relationship(back_populates="books")
    orders: Mapped[list["Order"]] = relationship(back_populates="book")
    book_categories: Mapped[list["BookCategory"]] = relationship(back_populates="book")


class BookCategory(Base):
    __tablename__ = "books_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.book_id", ondelete="CASCADE"), nullable=False)
    category: Mapped[Category] = mapped_column(
        Enum(Category, native_enum=False),
        nullable=False
    )

    book: Mapped["Book"] = relationship(back_populates="book_categories")


class WishList(Base):
    __tablename__ = 'wishlists'

    wish_list_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False)
    book_title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="wish_list")


class OrderStatus(str, enum.Enum):
    RESERVED = "Reserved"
    RETURNED = "Returned"
    IN_PROCESS = "In process"
    CANCELLED = "Cancelled"


class Order(Base):
    __tablename__ = 'orders'

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.book_id", ondelete="CASCADE"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False),
        nullable=False,
        default=OrderStatus.RESERVED
    )
    taken_from_id: Mapped[int] = mapped_column(ForeignKey("locations.location_id", ondelete="SET NULL"), nullable=True)
    returned_to_id: Mapped[int] = mapped_column(ForeignKey("locations.location_id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="orders")
    book: Mapped["Book"] = relationship(back_populates="orders")
    taken_from: Mapped["Location"] = relationship(
        foreign_keys=[taken_from_id], back_populates="orders_taken"
    )
    returned_to: Mapped["Location"] = relationship(
        foreign_keys=[returned_to_id], back_populates="orders_returned"
    )


class City(str, enum.Enum):
    Almaty = 'Almaty'
    Berlin = 'Berlin'
    Bishkek = 'Bishkek'
    Bratislava = 'Bratislava'
    Gdansk = 'Gdansk'
    Krakow = 'Krakow'
    Lodz = 'Lodz'
    London = 'London'
    Mexico_city = 'Mexico city'
    New_York = 'New York'
    San_Francisco = 'San Francisco'
    Sofia = 'Sofia'
    Tashkent = 'Tashkent'
    Tbilisi = 'Tbilisi'
    Vienna = 'Vienna'
    Vilnius = 'Vilnius'
    Warsaw = 'Warsaw'
    Wroclaw = 'Wroclaw'


class Location(Base):
    __tablename__ = 'locations'

    location_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city: Mapped[City] = mapped_column(
        Enum(City, native_enum=False),
        nullable=False
    )
    room: Mapped[str] = mapped_column(String, nullable=False)
    qr_code: Mapped[LargeBinary] = mapped_column(LargeBinary, nullable=True)

    books: Mapped[list["Book"]] = relationship(back_populates="location")
    orders_taken: Mapped[list["Order"]] = relationship(
        foreign_keys=[Order.taken_from_id], back_populates="taken_from"
    )
    orders_returned: Mapped[list["Order"]] = relationship(
        foreign_keys=[Order.returned_to_id], back_populates="returned_to"
    )
