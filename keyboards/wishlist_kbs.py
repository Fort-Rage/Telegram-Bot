from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from uuid6 import UUID

add_wishlist_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add a book", callback_data="add-wishlist")],
        [InlineKeyboardButton(text="❌ Close Menu", callback_data="close_menu")]
    ]
)

wishlist_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add a book", callback_data="add-wishlist"),
         InlineKeyboardButton(text="🗑 Delete a book", callback_data="wishlist-rm")],
        [InlineKeyboardButton(text="✏️ Update a book", callback_data="wishlist-upd"),
         InlineKeyboardButton(text="ℹ️ Show details", callback_data="wishlist-detail")],
        [InlineKeyboardButton(text="❌ Close Menu", callback_data="close_menu")]
    ]
)

admin_wishlist_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Delete a wishlist", callback_data="wishlist-rm"),
         InlineKeyboardButton(text="ℹ️ Show details", callback_data="wishlist-detail")],
        [InlineKeyboardButton(text="❌ Close Menu", callback_data="close_menu")]
    ]
)

upd_wishlist_item_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📖 Book title", callback_data=f"upd-wish-book-title")],
        [InlineKeyboardButton(text="👤 Author", callback_data=f"upd-wish-author")],
        [InlineKeyboardButton(text="📝 Comment", callback_data=f"upd-wish-comment")],
        [InlineKeyboardButton(text="⬅️ Go back", callback_data="wishlist-upd")]
    ]
)

back_to_detail_wishlist_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Go back", callback_data="wishlist-detail")]
    ]
)

back_to_wishlist_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back_to_wishlist")]
    ]
)


async def action_wishlist_kb(wishlists: list, action: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for wish in wishlists:
        builder.add(InlineKeyboardButton(
            text=f"{wish.book_title} - {wish.author}",
            callback_data=f"wishlist_{action}_{wish.id}"
        ))
    builder.add(InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back_to_wishlist"))

    return builder.adjust(1).as_markup()


async def rm_confirm_kb(wish_id: UUID) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Confirm", callback_data=f"wish_confirm_{wish_id}"),
                InlineKeyboardButton(text="❌ Cancel", callback_data=f"wish_cancel_{wish_id}"),
            ]
        ]
    )
    return markup


async def back_to_wishlist_upd_kb(wish_id: UUID) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Go back", callback_data=f"wishlist_upd_{wish_id}")]
        ]
    )
    return markup
