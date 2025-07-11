import enum
import uuid6

from typing import Optional
from sqlalchemy import ForeignKey, String, Enum, Boolean, DateTime, func, LargeBinary, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class TelegramUsers(Base):
    __tablename__ = 'tg_users'

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    telegram_id: Mapped[str] = mapped_column(String, unique=True)
    username: Mapped[str] = mapped_column(String)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    app_user: Mapped["AppUsers"] = relationship(back_populates="tg_user")


class AppUsers(Base):
    __tablename__ = 'app_users'

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    tg_user_id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tg_users.id"),
        nullable=False
    )
    employee_id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id"),
        nullable=False
    )
    role_id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id"),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    last_seen_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    tg_user: Mapped["TelegramUsers"] = relationship(back_populates="app_user")
    employee: Mapped["Employees"] = relationship(back_populates="app_user")
    role: Mapped["Roles"] = relationship(back_populates="app_users")

    books: Mapped[list["Book"]] = relationship(back_populates="owner")
    wish_list: Mapped[list["WishList"]] = relationship(back_populates="user")
    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class Employees(Base):
    __tablename__ = 'employees'

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    app_user: Mapped["AppUsers"] = relationship(back_populates="employee")


class Roles(Base):
    __tablename__ = 'roles'

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    permissions: Mapped[list["Permissions"]] = relationship(
        secondary="role_permissions",
        back_populates="roles"
    )
    app_users: Mapped[list["AppUsers"]] = relationship(back_populates="role")


class RolePermission(Base):
    __tablename__ = 'role_permissions'

    role_id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True
    )
    permission_id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True
    )


class Permissions(Base):
    __tablename__ = 'permissions'

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    roles: Mapped[list["Roles"]] = relationship(
        secondary="role_permissions",
        back_populates="permissions"
    )


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

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    author: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False
    )
    location_id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("locations.id", ondelete="CASCADE"),
        nullable=False
    )
    created: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    qr_code: Mapped[LargeBinary] = mapped_column(LargeBinary, nullable=True)

    owner: Mapped["AppUsers"] = relationship(back_populates="books")
    location: Mapped["Location"] = relationship(back_populates="books")
    orders: Mapped[list["Order"]] = relationship(back_populates="book")
    book_categories: Mapped[list["BookCategory"]] = relationship(back_populates="book")


class BookCategory(Base):
    __tablename__ = "books_categories"

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    book_id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False
    )
    category: Mapped[Category] = mapped_column(
        Enum(Category, native_enum=False),
        nullable=False
    )

    book: Mapped["Book"] = relationship(back_populates="book_categories")


class WishList(Base):
    __tablename__ = 'wishlists'

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    app_user_id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False
    )
    book_title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["AppUsers"] = relationship(back_populates="wish_list")


class OrderStatus(str, enum.Enum):
    RESERVED = "Reserved"
    RETURNED = "Returned"
    IN_PROCESS = "In process"
    CANCELLED = "Cancelled"


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    app_user_id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False
    )
    book_id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False),
        nullable=False,
        default=OrderStatus.RESERVED
    )

    taken_from_id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True
    )
    returned_to_id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["AppUsers"] = relationship(back_populates="orders")
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

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
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
