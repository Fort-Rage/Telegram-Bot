from datetime import timedelta
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from uuid6 import UUID

from db.database import async_session_factory
from db.queries.app_user_crud import AppUserObj
from db.queries.wishlist_crud import WishlistObj
from handlers.registration_handler import cmd_start
from states.main_states import Wish, WishUpdBookTitle, WishUpdAuthor, WishUpdComment
from keyboards import wishlist_kbs as wish_kbs

router = Router()


@router.message(Command("wishlists"))
async def wishlist_handler(message: Message):
    telegram_id = message.from_user.id

    async with async_session_factory() as session:
        app_user_id = await AppUserObj().get_app_user_id(session=session, telegram_id=str(telegram_id))
        wishlist_items = await WishlistObj().read(session=session, app_user_id=app_user_id)
        is_user_registered = await AppUserObj().is_user_registered(session=session, telegram_id=str(telegram_id))
        is_admin = await AppUserObj().is_admin(session=session, app_user_id=app_user_id)

        if is_user_registered:
            if is_admin:
                message_text = "⭐ List of all wishlists:\n\n" if wishlist_items else ("📭 The wishlist is "
                                                                                      "currently empty!")
                keyboard = wish_kbs.admin_wishlist_kb if wishlist_items else None
            else:
                message_text = "⭐ Your wishlist:\n\n" if wishlist_items else ("Your wishlist is empty. "
                                                                              "Add a book you'd like to read! 📘")
                keyboard = wish_kbs.wishlist_kb if wishlist_items else wish_kbs.add_wishlist_kb

            if wishlist_items:
                message_text += "\n".join(
                    [f"📖 {i + 1}. {item.book_title} — {item.author}" for i, item in enumerate(wishlist_items)])

            await message.answer(message_text, reply_markup=keyboard)
        else:
            await cmd_start(message)


# region Create Wishlist Logic
@router.callback_query(F.data == "add-wishlist")
async def add_wishlist(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("📖 Enter the book title:")
    await state.set_state(Wish.book_title)


@router.message(Wish.book_title)
async def wish_book_title(message: Message, state: FSMContext):
    await state.update_data(book_title=message.text)
    await message.answer("✍️ Great! Now enter the author's name:")
    await state.set_state(Wish.author)


@router.message(Wish.author)
async def wish_author(message: Message, state: FSMContext):
    await state.update_data(author=message.text)
    await message.answer("📝 Want to add a comment? (Type '-' to skip this step):")
    await state.set_state(Wish.comment)


@router.message(Wish.comment)
async def wish_comment(message: Message, state: FSMContext):
    data = await state.get_data()

    comment = None if message.text == "-" else message.text

    async with async_session_factory() as session:
        app_user_id = await AppUserObj().get_app_user_id(session=session, telegram_id=str(message.from_user.id))
        success = await WishlistObj().create(
            session=session,
            app_user_id=app_user_id,
            book_title=data.get('book_title'),
            author=data.get('author'),
            comment=comment
        )
    
    if success:
        await message.answer(
            f"✅ The book <b>\"{data.get('book_title')}\"</b> has been successfully added to your wishlist!",
            reply_markup=wish_kbs.back_to_wishlist_kb, parse_mode='HTML'
        )
    else:
        await message.answer(
            f"❌ Oops! Failed to add <b>\"{data.get('book_title')}\"</b> to your wishlist\n\n"
            f"🔄 <i>Please try again later</i>", reply_markup=wish_kbs.back_to_wishlist_kb, parse_mode='HTML'
        )

    await state.clear()
# endregion


# region Common Read, Update, Delete Logic
@router.callback_query(F.data.startswith("wishlist-"))
async def action_wishlist(callback: CallbackQuery):
    await callback.answer()

    async with async_session_factory() as session:
        app_user_id = await AppUserObj().get_app_user_id(session=session, telegram_id=str(callback.from_user.id))
        wishlist_items = await WishlistObj().read(session=session, app_user_id=app_user_id)
        is_admin = await AppUserObj().is_admin(session=session, app_user_id=app_user_id)

    action = callback.data.split("-")[1]
    message_text = ""

    if action == "detail":
        message_text = "ℹ️ Choose a book to view details:"
    elif action == "upd":
        message_text = "✏️ Choose a book to update from your wishlist:"
    elif action == "rm":
        message_text = (
            f"🗑 Choose a book to delete from "
            f"{'the wishlists' if is_admin else 'your wishlist'}:"
        )

    await callback.message.edit_text(message_text,
                                     reply_markup=await wish_kbs.action_wishlist_kb(wishlist_items, action))


@router.callback_query(F.data.startswith("wishlist_"))
async def action_wish_id(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    _, action, wish_id = callback.data.split("_")

    async with async_session_factory() as session:
        app_user_id = await AppUserObj().get_app_user_id(session=session, telegram_id=str(callback.from_user.id))
        wishlist_item = await WishlistObj().get_obj(session=session, wish_id=wish_id)
        is_admin = await AppUserObj().is_admin(session=session, app_user_id=app_user_id)

        if wishlist_item:
            comment, book_title, author = wishlist_item.comment, wishlist_item.book_title, wishlist_item.author
            created_at = wishlist_item.created_at

        app_user_full_name = await AppUserObj().get_employee_fullname(session=session, app_user_id=app_user_id)

    message_text = ""
    keyboard = None

    if action == "detail":
        comment = comment if comment else '<i>no comment</i>'
        message_text = (
                f"📖 <b>{book_title}</b>\n"
                f"✍️ <b>Author:</b> {author}\n"
                + (f"\n👤 <b>Added by:</b> {app_user_full_name or 'Unknown'}\n" if is_admin else "")
                + f"📝 <b>Comment:</b> {comment}\n\n"
                  f"📅 <b>Added on:</b> {(created_at + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M')}"
        )
        keyboard = wish_kbs.back_to_detail_wishlist_kb
    elif action == "upd":
        comment = comment if comment else '<i>no comment</i>'
        message_text = (
            f"📖 <b>{book_title}</b>\n"
            f"✍️ <b>Author:</b> {author}\n"
            f"📝 <b>Comment:</b> {comment}\n\n"
            f"📅 <b>Added on:</b> {(created_at + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M')}"
        )
        keyboard = wish_kbs.upd_wishlist_item_kb
        await state.update_data(wish_id=wish_id)
    elif action == "rm":
        message_text = (
            f"Are you sure you want to delete <b>\"{book_title}\"</b> from "
            f"{'the wishlists' if is_admin else 'your wishlist'}?\n\n"
            f"<i>This action cannot be undone!</i>"
        )
        keyboard = await wish_kbs.rm_confirm_kb(wish_id)

    await callback.message.edit_text(message_text, reply_markup=keyboard, parse_mode='HTML')
# endregion


# region Update Logic
@router.callback_query(F.data == "upd-wish-book-title")
async def wish_book_title(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await callback.message.answer("📖 Enter the new book title:")
    await state.set_state(WishUpdBookTitle.book_title)


@router.message(WishUpdBookTitle.book_title)
async def upd_wish_book_title(message: Message, state: FSMContext):
    data = await state.get_data()
    wish_id = data.get('wish_id')

    async with async_session_factory() as session:
        wishlist_item = await WishlistObj().get_obj(session=session, wish_id=wish_id)
        if wishlist_item:
            book_title = wishlist_item.book_title
        success = await WishlistObj().update(session=session, field="book_title",
                                             wish_id=wish_id, new_value=message.text)

    keyboard = await wish_kbs.back_to_wishlist_upd_kb(wish_id)
    
    if success:
        await message.answer(f"✅ The book title has been successfully updated to <b>\"{message.text}\"</b>",
                             reply_markup=keyboard, parse_mode='HTML')
    else:
        await message.answer(f"❌ Oops! Failed to update the title for <b>\"{book_title}\"</b>\n\n"
                             f"🔄 <i>Please try again later</i>",
                             reply_markup=keyboard, parse_mode='HTML')

    await state.clear()


@router.callback_query(F.data == "upd-wish-author")
async def wish_author(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await callback.message.answer("👤 Enter the new author's name:")
    await state.set_state(WishUpdAuthor.author)


@router.message(WishUpdAuthor.author)
async def upd_wish_author(message: Message, state: FSMContext):
    data = await state.get_data()
    wish_id = data.get('wish_id')

    async with async_session_factory() as session:
        wishlist_item = await WishlistObj().get_obj(session=session, wish_id=wish_id)
        if wishlist_item:
            book_title = wishlist_item.book_title
        success = await WishlistObj().update(session=session, field="author",
                                             wish_id=wish_id, new_value=message.text)

    keyboard = await wish_kbs.back_to_wishlist_upd_kb(wish_id)
    
    if success:
        await message.answer(f"✅ The author's name has been successfully updated to <b>\"{message.text}\"</b>",
                             reply_markup=keyboard, parse_mode='HTML')
    else:
        await message.answer(f"❌ Oops! Failed to update the author for <b>\"{book_title}\"</b>\n\n"
                             f"🔄 <i>Please try again later</i>",
                             reply_markup=keyboard, parse_mode='HTML')

    await state.clear()


@router.callback_query(F.data == "upd-wish-comment")
async def wish_comment(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await callback.message.answer("📝 Enter your new comment: \n\n(Type '-' to delete the comment)")
    await state.set_state(WishUpdComment.comment)


@router.message(WishUpdComment.comment)
async def upd_wish_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    wish_id = data.get('wish_id')

    new_comment = None if message.text == '-' else message.text
    keyboard = await wish_kbs.back_to_wishlist_upd_kb(wish_id)

    async with async_session_factory() as session:
        wishlist_item = await WishlistObj().get_obj(session=session, wish_id=wish_id)
        if wishlist_item:
            book_title = wishlist_item.book_title
        success = await WishlistObj().update(session=session, field="comment",
                                             wish_id=wish_id, new_value=new_comment)
    
    if success:
        if new_comment is None:
            await message.answer("✅ The comment has been successfully deleted",
                                 reply_markup=keyboard)
        else:
            await message.answer(f"✅ The comment has been successfully updated to <b>\"{new_comment}\"</b>",
                                 reply_markup=keyboard, parse_mode='HTML')
    else:
        if new_comment is None:
            await message.answer(f"❌ Oops! Failed to delete the comment for <b>\"{book_title}\"</b>\n\n"
                                 f"🔄 <i>Please try again later</i>",
                                 reply_markup=keyboard, parse_mode='HTML')
        else:
            await message.answer(f"❌ Oops! Failed to update the comment for <b>\"{book_title}\"</b>\n\n"
                                 f"🔄 <i>Please try again later</i>",
                                 reply_markup=keyboard, parse_mode='HTML')

    await state.clear()
# endregion


# region Delete Logic
@router.callback_query(F.data.startswith("wish_confirm_"))
async def remove_wish_id(callback: CallbackQuery):
    await callback.answer()
    wish_id = UUID(callback.data.split("_")[2])

    async with async_session_factory() as session:
        app_user_id = await AppUserObj().get_app_user_id(session=session, telegram_id=str(callback.from_user.id))
        wishlist_item = await WishlistObj().get_obj(session=session, wish_id=wish_id)
        if wishlist_item:
            book_title = wishlist_item.book_title
        success = await WishlistObj().remove(session=session, wish_id=wish_id)
        is_admin = await AppUserObj().is_admin(session=session, app_user_id=app_user_id)

    message_text = (
        f"🗑 <b>\"{book_title}\"</b> has been deleted from "
        f"{'the wishlists' if is_admin else 'your wishlist'}!" if success
        else f"❌ Oops! Failed to delete <b>\"{book_title}\"</b> from "
             f"{'the wishlists' if is_admin else 'your wishlist'}"
             f"\n\n<i>🔄 <i>Please try again later</i></i>"
    )

    await callback.message.edit_text(message_text, reply_markup=wish_kbs.back_to_wishlist_kb, parse_mode='HTML')


@router.callback_query(F.data.startswith("wish_cancel_"))
async def remove_wish_id(callback: CallbackQuery):
    wish_id = UUID(callback.data.split("_")[2])

    async with async_session_factory() as session:
        app_user_id = await AppUserObj().get_app_user_id(session=session, telegram_id=str(callback.from_user.id))
        wishlist_item = await WishlistObj().get_obj(session=session, wish_id=wish_id)
        if wishlist_item:
            book_title = wishlist_item.book_title
        is_admin = await AppUserObj().is_admin(session=session, app_user_id=app_user_id)

    await callback.message.edit_text(
        f"❌ Action canceled. The <b>\"{book_title}\"</b> remains in "
        f"{'the wishlists' if is_admin else 'your wishlist'}!",
        reply_markup=wish_kbs.back_to_wishlist_kb, parse_mode='HTML'
    )
# endregion


@router.callback_query(F.data == "back_to_wishlist")
async def back_to_wishlist(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    async with async_session_factory() as session:
        app_user_id = await AppUserObj().get_app_user_id(session=session, telegram_id=str(callback.from_user.id))
        wishlist_items = await WishlistObj().read(session=session, app_user_id=app_user_id)
        is_admin = await AppUserObj().is_admin(session=session, app_user_id=app_user_id)

        if is_admin:
            text = "⭐ List of all wishlists:\n\n" if wishlist_items else "📭 The wishlist is currently empty!"
            keyboard = wish_kbs.admin_wishlist_kb if wishlist_items else None
        else:
            text = "⭐ Your wishlist:\n\n" if wishlist_items else ("Your wishlist is empty. "
                                                                  "Add a book you'd like to read! 📘")
            keyboard = wish_kbs.wishlist_kb if wishlist_items else wish_kbs.add_wishlist_kb

        if wishlist_items:
            text += "\n".join([f"📖 {i + 1}. {item.book_title} — "
                               f"{item.author}" for i, item in enumerate(wishlist_items)])

        await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "close_menu")
async def close_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await state.clear()
