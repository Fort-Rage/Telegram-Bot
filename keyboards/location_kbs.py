from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


add_location_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add a location", callback_data="add_location")],
        [InlineKeyboardButton(text="❌ Close Menu", callback_data="close_menu")]
    ]
)

location_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add a location", callback_data="add_location"),
         InlineKeyboardButton(text="🔳 Show QR code", callback_data="qrcode_location")],
        [InlineKeyboardButton(text="✏️ Update a location", callback_data="update_location"),
         InlineKeyboardButton(text="🗑 Delete a location", callback_data="remove_location")],
        [InlineKeyboardButton(text="❌ Close Menu", callback_data="close_menu")]
    ]
)


def back_to_loc_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back_to_loc_menu")],
        ]
    )


def locations_kb(result):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text=f'{location.city.value}: {location.room}') for location in result[i:i + 2]]
            for i in range(0, len(result), 2)
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


def show_locations_kb(locations: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for location in locations:
        builder.add(InlineKeyboardButton(
            text=f"{location.city.value}: {location.room}",
            callback_data=f"show_qrcode_{location.location_id}"
        ))

    builder.add(InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back_to_loc_menu"))
    return builder.adjust(2).as_markup()


def location_confirm():
    confirmation_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Confirm", callback_data="loc_confirm"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="loc_cancel"),
            ]
        ]
    )

    return confirmation_kb


def city_kb(result):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=city) for city in result[i:i+2]]for i in range(0, len(result), 2)],
        resize_keyboard=True
        )
    return keyboard


def back_to_loc_or_book():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add a book", callback_data="add_book")],
            [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back_to_loc_menu")],
            [InlineKeyboardButton(text="❌ Close Menu", callback_data="close_menu")],
        ]
    )
