from math import ceil
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from uuid6 import UUID

from db.database import async_session_factory
from db.queries.app_user_crud import AppUserObj

book_confirmation_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Confirm", callback_data="book_confirm_remove"),
            InlineKeyboardButton(text="Cancel", callback_data="book_cancel_remove"),
        ]
    ]
)

books_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add a book", callback_data="add_book"),
         InlineKeyboardButton(text="ℹ️ Show details", callback_data="book_detail")],
        [InlineKeyboardButton(text="✏️ Update a book", callback_data="update_book"),
         InlineKeyboardButton(text="🗑 Remove a book", callback_data="remove_book")],
        [InlineKeyboardButton(text="🔳 Show QR", callback_data="qrcode_book"),
         InlineKeyboardButton(text="❌ Close Menu", callback_data="close_menu")]
    ]
)

no_books_kb_admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add a book", callback_data="add_book")],
        [InlineKeyboardButton(text="❌ Close Menu", callback_data="close_menu")]
    ]
)

no_books_kb_user = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Close Menu", callback_data="close_menu")
        ]
    ]
)

user_book_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="ℹ️ Show details", callback_data="book_detail"),
            InlineKeyboardButton(text="❌ Close Menu", callback_data="close_menu"),
        ]
    ]
)


def category_kb(result: list) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=category)] for category in result] +
                 [[KeyboardButton(text="✅ Done")]],
        resize_keyboard=True
    )
    return keyboard


def book_list_kb(books: list, action: str, page: int = 1, per_page: int = 5) -> InlineKeyboardMarkup:
    total_pages = ceil(len(books) / per_page)
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, len(books))
    books_page = books[start_idx:end_idx]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f'{index + 1}: {book.title}', callback_data=f"{action}_select_{book.id}"
            )] for index, book in enumerate(books_page)
        ]
    )

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅ Previous", callback_data=f"{action}_page_{page - 1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡", callback_data=f"{action}_page_{page + 1}"))

    if nav_buttons:
        keyboard.inline_keyboard.append(nav_buttons)

    back_button = InlineKeyboardButton(text="⬅️ Go back", callback_data="back_button")
    keyboard.inline_keyboard.append([back_button])

    return keyboard


def book_update_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Title", callback_data="update_title"),
                InlineKeyboardButton(text="Author", callback_data="update_author")
            ],
            [
                InlineKeyboardButton(text="Description", callback_data="update_description"),
                InlineKeyboardButton(text="Owner", callback_data="update_owner")
            ],
            [
                InlineKeyboardButton(text="Location", callback_data="update_book_location"),
                InlineKeyboardButton(text="Categories", callback_data="update_categories")
            ],
            [
                InlineKeyboardButton(text='Save changes', callback_data="save_changes"),
            ],
            [
                InlineKeyboardButton(text='Cancel changes', callback_data="book_cancel_update")
            ]
        ]
    )
    return keyboard


def order_cancel_kb(book_id: UUID, is_admin: False) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Order", callback_data=f"order-book_{book_id}"),
                InlineKeyboardButton(text="⬅️ Go back", callback_data="book_view_back"),
            ]
        ]
    )
    if is_admin:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text='QR', callback_data=f"qr_book_{book_id}"),
        ])

    return keyboard


async def owners_kb(result: list, action: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    async with async_session_factory() as session:
        for user in result:
            fullname = await AppUserObj().get_employee_fullname(session=session, app_user_id=user.id)
            builder.button(
                text=fullname,
                callback_data=f"select_owner_{action}:{user.id}"
            )

    return builder.adjust(2).as_markup()


def create_book_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Confirm", callback_data="create_book_confirm")],
            [InlineKeyboardButton(text="Cancel", callback_data="create_book_cancel")],
        ]
    )


def back_to_books_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Books menu", callback_data="back_to_list"),
                InlineKeyboardButton(text="❌ Close", callback_data="close_menu"),
            ]
        ]
    )


def create_loc_or_exit() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Create location", callback_data="add_location")],
            [InlineKeyboardButton(text="❌ Close Menu", callback_data="close_menu")],
        ]
    )


def show_books_kb(books: list) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    for book in books:
        keyboard.add(InlineKeyboardButton(
            text=f"{book.author}: {book.title}",
            callback_data=f"qr_book_{book.id}"
        ))

    keyboard.adjust(2)

    keyboard.row(InlineKeyboardButton(
        text="⬅️ Back to Menu",
        callback_data="back_to_list"
    ))

    return keyboard.as_markup()
