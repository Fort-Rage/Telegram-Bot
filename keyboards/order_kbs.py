from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.models import OrderStatus

no_order_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Close Menu", callback_data="close_menu")]
    ]
)

back_to_detail_order_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Go back", callback_data="order-detail")]
    ]
)

back_to_order_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back_to_order")]
    ]
)


async def get_order_kb(has_reserved_orders: bool) -> InlineKeyboardMarkup:
    if has_reserved_orders:
        buttons = [[
            InlineKeyboardButton(text="🚫 Cancel order", callback_data="order-cancel"),
            InlineKeyboardButton(text="ℹ️ Show details", callback_data="order-detail")
        ]]
    else:
        buttons = [[
            InlineKeyboardButton(text="ℹ️ Show details", callback_data="order-detail")
        ]]

    buttons.append([
        InlineKeyboardButton(text="❌ Close Menu", callback_data="close_menu")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def action_order_kb(action: str, orders: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if action == 'cancel':
        for order in orders:
            if order.status == OrderStatus.RESERVED:
                builder.add(InlineKeyboardButton(
                    text=f"{order.book.title}",
                    callback_data=f"order_{action}_{order.id}"
                ))
    elif action == 'detail':
        for order in orders:
            builder.add(InlineKeyboardButton(
                text=f"{order.book.title}",
                callback_data=f"order_{action}_{order.id}"
            ))

    builder.add(InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back_to_order"))
    return builder.adjust(1).as_markup()


async def return_order_kb(orders: list):
    builder = InlineKeyboardBuilder()

    for order in orders:
        if order.status == OrderStatus.IN_PROCESS:
            builder.add(InlineKeyboardButton(
                text=f"{order.book.title}",
                callback_data=f"order_return_{order.id}"
            ))

    builder.add(InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back_to_order"))
    return builder.adjust(1).as_markup()


async def confirm_return_kb(location_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Return a book", callback_data=f"return_book_{location_id}")]
    ])
