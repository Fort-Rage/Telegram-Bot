from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

registration_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Yes, let's start", callback_data="reg_yes"),
         InlineKeyboardButton(text="No, maybe later", callback_data="reg_no")]
    ]
)
