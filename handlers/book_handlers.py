import os

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from db.database import async_session_factory
from db.queries.book_crud import BookObj
from db.queries.location_crud import LocationObj
from db.queries.user_crud import UserObj
from keyboards import book_kbs as bk_kb
from keyboards import location_kbs as loc_kb
from states.main_states import Books, BookUpdate

book_router = Router()

# region Create book


@book_router.message(Command('books'))
async def books_command(message: Message):
    async with async_session_factory() as session:
        books = await BookObj().read(available_books=True, session=session)
        is_admin = await UserObj().is_admin(session=session, telegram_id=message.from_user.id)

    reply_markup = bk_kb.books_kb if is_admin else bk_kb.user_book_kb
    if books:
        text = '📚 Books:\n'
        text += '\n'.join(f'📖 {index+1}: {book.title} - {book.author}' for index, book in enumerate(books))
        await message.answer(text, reply_markup=reply_markup)
    else:
        async with async_session_factory() as session:
            is_admin = await UserObj().is_admin(session=session, telegram_id=message.from_user.id)

        kb = bk_kb.no_books_kb_admin if is_admin else bk_kb.no_books_kb_user
        await message.answer('📚 The library is currently empty', reply_markup=kb)


@book_router.callback_query(F.data == 'add_book')
async def add_book_handler(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(prev_callback=callback_query.data)
    async with async_session_factory() as session:
        if await LocationObj().read(session=session):
            await callback_query.message.edit_text("📖 Enter the book title:")
            await state.set_state(Books.author)
            await callback_query.answer()
        else:
            await callback_query.message.edit_text(
                'Before adding a book to the library, please create a location first.',
                reply_markup=bk_kb.create_loc_or_exit()
            )


@book_router.message(Books.author)
async def add_book_handler_author(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("✍️ Great! Now enter the author's name:")
    await state.set_state(Books.description)


@book_router.message(Books.description)
async def show_book_handler_desc(message: Message, state: FSMContext):
    await state.update_data(author=message.text)
    await message.answer('📝 Enter the book description:')
    await state.set_state(Books.owner)


@book_router.message(Books.owner)
async def add_book_handler_owner(message: Message, state: FSMContext):
    await state.update_data(description=message.text)

    async with async_session_factory() as session:
        result = await UserObj().read(session=session)

    kb = bk_kb.owners_kb(result)
    await message.answer('👤 Select the owner:', reply_markup=kb)
    await state.set_state(Books.select_categories)


@book_router.message(Books.select_categories)
async def show_books_handler(message: Message, state: FSMContext):
    owner = message.text.split(" ")
    async with async_session_factory() as session:
        if len(owner) > 1:
            owner_id = await UserObj().get_user_id_by_name(session=session, name=owner[0], surname=owner[1])
        else:
            owner_id = int(os.getenv('ADMIN_TG_ID'))

    await state.update_data(owner_id=owner_id)
    await state.update_data(owner=message.text)
    result = await BookObj().get_categories()
    keyboard = bk_kb.category_kb(result)
    await message.answer("🏷 Choose categories:", reply_markup=keyboard)
    await state.set_state(Books.categories)


@book_router.message(Books.categories)
async def add_book(message: Message, state: FSMContext):
    selected_category = message.text
    data = await state.get_data()
    chosen_categories = data.get("chosen_categories", [])
    async with async_session_factory() as session:
        result = await LocationObj().read(session=session)
    keyboard = loc_kb.locations_kb(result)

    if selected_category == "✅ Done":
        if not chosen_categories:
            await message.answer("❌ You haven't selected any categories. Please choose at least one.")
            return

        await state.update_data(categories=chosen_categories)
        await state.set_state(Books.save_book)
        await message.answer('📍 Choose location', reply_markup=keyboard)
        return

    available_categories = await BookObj().get_categories()
    if selected_category in available_categories:
        if selected_category not in chosen_categories:
            chosen_categories.append(selected_category)
            await state.update_data(chosen_categories=chosen_categories)
            await message.answer(f"{selected_category} added!\nSelect more or press '✅ Done'.")
        else:
            await message.answer(f"{selected_category} is already selected. Choose another or press '✅ Done'.")
    else:
        await message.answer("Invalid category. Please choose from the buttons.")


async def save_book_update(state: FSMContext, field: str, value: str):
    data = await state.get_data()
    updates = data.get("updates", {})
    updates[field] = value
    await state.update_data(updates=updates)


@book_router.message(Books.save_book)
async def show_book_handler(message: Message, state: FSMContext):
    loc_city = message.text.split(':')[0]
    loc_room = message.text.split(':')[1].strip()
    await state.update_data(loc_city=loc_city)
    await state.update_data(loc_room=loc_room)
    data = await state.get_data()
    chosen_categories = data.get("chosen_categories", [])
    new_book = (
        '<b>Do you want to confirm the creation of this book?</b>\n\n'
        f"📚 <b>{data.get('title')}</b>\n"
        f"✍️ <b>Author:</b> {data.get('author')}\n\n"
        f"📍 <b>Location:</b> {loc_city}: Room #{loc_room}\n"
        f"👤 <b>Owner:</b> {data.get('owner')}\n\n"
        f"📖 <b>Description:</b>\n{data.get('description')}\n\n"
        f"🏷 <b>Category:</b>\n{', '.join(chosen_categories)}"
    )
    await message.answer(new_book, reply_markup=bk_kb.create_book_kb(), parse_mode=ParseMode.HTML)


@book_router.callback_query(F.data == 'create_book_confirm')
async def create_book_handler(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    async with async_session_factory() as session:
        loc_id = await LocationObj().get_location_id(data.get('loc_city'), data.get('loc_room'), session)

    if await BookObj().create(
        data.get('title'),
        data.get('author'),
        data.get('description'),
        data.get('owner_id'),
        data.get('categories'),
        loc_id,
        session
    ):
        await callback_query.message.answer(
            "📚 Book successfully created!",
            reply_markup=ReplyKeyboardRemove()
        )

        await callback_query.message.delete()

        await callback_query.message.answer(
            "Would you like to return to the menu or exit?",
            reply_markup=bk_kb.back_to_books_menu_kb()
        )
    else:
        await callback_query.message.edit_text(
            '❌ Something went wrong. Please try again later', reply_markup=None
        )

    await state.clear()
    await callback_query.answer()


@book_router.callback_query(F.data == 'create_book_cancel')
async def cancel_book_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('You’ve canceled the book creation process.', reply_markup=None)
    await callback_query.message.answer("Hope to see you again soon!", reply_markup=ReplyKeyboardRemove())
    await state.clear()
    await callback_query.answer()

# endregion


# region Remove book
@book_router.callback_query(F.data == 'remove_book')
async def delete_book_handler(callback_query: CallbackQuery, page: int = 1, per_page: int = 5):
    async with async_session_factory() as session:
        result = await BookObj().read(available_books=True, session=session)

    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, len(result))
    books_page = result[start_idx:end_idx]

    text = '\n'.join(f"📖 {index+1}: {book.title} - {book.author}" for index, book in enumerate(books_page))
    kb = bk_kb.book_list_kb(result, 'remove', page=page, per_page=per_page)

    if callback_query.message:
        await callback_query.message.edit_text(text=text, reply_markup=kb)
    else:
        await callback_query.message.answer(text=text, reply_markup=kb)


@book_router.callback_query(F.data.startswith('remove_page_'))
async def change_page(callback_query: CallbackQuery):
    page = int(callback_query.data.split('_')[-1])
    await delete_book_handler(callback_query, page=page)


@book_router.callback_query(F.data.startswith("remove_select_"))
async def select_book(callback_query: CallbackQuery, state: FSMContext):
    book_id = int(callback_query.data.split("_")[2])
    await state.update_data(selected_book=book_id)
    async with async_session_factory() as session:
        book = await BookObj().get_obj(book_id, session=session)

    confirm_kb = bk_kb.book_confirmation_kb

    await callback_query.message.edit_text(
        f"Are you sure you want to remove '{book.title}'?",
        reply_markup=confirm_kb
    )


@book_router.callback_query(F.data == 'book_confirm_remove')
async def delete_book_confirm(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    book_id = data.get('selected_book')

    try:
        async with async_session_factory() as session:
            success = await BookObj().remove(book_id, session)
        if success:
            await callback_query.message.edit_text(
                "✅ Book successfully removed!",
                reply_markup=bk_kb.back_to_books_menu_kb()
            )
        else:
            await callback_query.message.edit_text("⚠️ Failed to remove the book. It may not exist.")

    except ValueError as e:
        await callback_query.message.edit_text(f"⚠️ Error: {e}")

    await state.clear()


@book_router.callback_query(F.data == 'book_cancel_remove')
async def delete_book_cancel(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        "The book removal process has been cancelled.", reply_markup=None
    )
    await state.clear()

# endregion


# region Update book

async def display_books_page(callback_query: CallbackQuery, page: int = 1, per_page: int = 5):
    async with async_session_factory() as session:
        result = await BookObj().read(available_books=True, session=session)

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    books_page = result[start_idx:end_idx]

    text = '\n'.join(f"📖  {index+1}: {book.title} - {book.author}" for index, book in enumerate(books_page))
    kb = bk_kb.book_list_kb(result, action='update', page=page, per_page=per_page)

    if callback_query.message:
        await callback_query.message.edit_text(text=text, reply_markup=kb)
    else:
        await callback_query.message.answer(text=text, reply_markup=kb)


@book_router.callback_query(F.data == 'update_book')
async def update_book_handler(callback_query: CallbackQuery, page: int = 1, per_page: int = 5):
    await display_books_page(callback_query, page, per_page)


@book_router.callback_query(F.data == "book_update_back")
async def book_update_back(callback_query: CallbackQuery, page: int = 1, per_page: int = 5):
    await display_books_page(callback_query, page, per_page)


@book_router.callback_query(F.data.startswith('update_page_'))
async def change_page(callback_query: CallbackQuery):
    page = int(callback_query.data.split('_')[-1])
    await update_book_handler(callback_query, page=page)


@book_router.callback_query(F.data.startswith("update_select_"))
async def select_book(callback_query: CallbackQuery, state: FSMContext):
    book_id = int(callback_query.data.split("_")[2])
    async with async_session_factory() as session:
        book = await BookObj().get_obj(book_id, session=session)

    book_categories = await BookObj().get_book_categories(book_id, session)
    categories = "\n".join(f"• {cat}" for cat in book_categories)
    kb = bk_kb.book_update_kb()

    async with async_session_factory() as session:
        owner = await UserObj().get_obj(session=session, telegram_id=book.owner_id)
        location_name = await LocationObj().get_obj(book.location_id, session)

    text = (
        f"📚 <b>{book.title}</b>\n"
        f"✍️ <b>Author:</b> {book.author}\n\n"
        f"👤 <b>Owner:</b> {owner.name} {owner.surname}\n\n"
        f"📍 <b>Location:</b> {location_name}\n\n"
        f"📝 <b>Description:</b>\n{book.description}\n\n"
        f"🏷 <b>Category:</b>\n{categories}"
    )

    await callback_query.message.edit_text(text=text, reply_markup=kb, parse_mode='HTML')
    await state.update_data(selected_book=book_id)


@book_router.callback_query(F.data == "update_title")
async def update_title(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer('Input new book title:')
    await state.set_state(BookUpdate.title)
    await callback_query.answer()


@book_router.message(BookUpdate.title)
async def set_title(message: Message, state: FSMContext):
    await save_book_update(state, "title", message.text)
    await message.answer(f"New title: {message.text}")
    await message.answer(f"To save all changes, press «💾 Save Changes»", reply_markup=bk_kb.book_update_kb())


@book_router.callback_query(F.data == "update_author")
async def update_author(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer('Input new book author:')
    await state.set_state(BookUpdate.author)
    await callback_query.answer()


@book_router.message(BookUpdate.author)
async def set_author(message: Message, state: FSMContext):
    await save_book_update(state, "author", message.text)
    await message.answer(f"New author: {message.text}")
    await message.answer(f"To save all changes, press «💾 Save Changes»", reply_markup=bk_kb.book_update_kb())


@book_router.callback_query(F.data == "update_description")
async def update_description(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer('Input new description:')
    await state.set_state(BookUpdate.description)
    await callback_query.answer()


@book_router.message(BookUpdate.description)
async def set_description(message: Message, state: FSMContext):
    await save_book_update(state, "description", message.text)
    await message.answer(f"New description: {message.text}")
    await message.answer(f"To save all changes, press «💾 Save Changes»", reply_markup=bk_kb.book_update_kb())


@book_router.callback_query(F.data == "update_owner")
async def update_owner(callback_query: CallbackQuery, state: FSMContext):
    async with async_session_factory() as session:
        all_users = await UserObj().read(session=session)

    kb = bk_kb.owners_kb(all_users)
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer("Choose a new owner:", reply_markup=kb)
    await state.set_state(BookUpdate.owner)
    await callback_query.answer()


@book_router.message(BookUpdate.owner)
async def set_owner(message: Message, state: FSMContext):
    new_owner = message.text.split(" ")
    async with async_session_factory() as session:
        if len(new_owner) > 1:
            new_owner_id = await UserObj().get_user_id_by_name(session=session, name=new_owner[0], surname=new_owner[1])
        else:
            new_owner_id = int(os.getenv('ADMIN_TG_ID'))

        user = await UserObj().get_obj(session=session, telegram_id=new_owner_id)

    if user:  # TODO fix it
        await save_book_update(state, "owner_id", str(new_owner_id))
        await message.answer(f"New owner: {message.text}", reply_markup=ReplyKeyboardRemove())
        await message.answer(
            f"To save all changes, press «💾 Save Changes»", reply_markup=bk_kb.book_update_kb()
        )
    else:
        await message.answer('User with this ID does not exist', reply_markup=bk_kb.book_update_kb())


@book_router.callback_query(F.data == 'update_book_location')
async def update_location(callback_query: CallbackQuery, state: FSMContext):
    async with async_session_factory() as session:
        result = await LocationObj().read(session)

    kb = loc_kb.locations_kb(result)
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer('Input new book location:', reply_markup=kb)
    await state.set_state(BookUpdate.location)
    await callback_query.answer()


@book_router.message(BookUpdate.location)
async def set_location(message: Message, state: FSMContext):
    loc_city = message.text.split(':')[0]
    loc_room = message.text.split(':')[1].strip()
    async with async_session_factory() as session:
        location_id = await LocationObj.get_location_id(loc_city, loc_room, session)

    if location_id is None:
        await message.answer("❌ Location not found. Please try again.", reply_markup=bk_kb.book_update_kb())
        return

    await save_book_update(state, "location_id", location_id)
    await message.answer(f'New location: {loc_city}: Room #{loc_room}', reply_markup=ReplyKeyboardRemove())
    await message.answer(f"To save all changes, press «💾 Save Changes»", reply_markup=bk_kb.book_update_kb())


@book_router.callback_query(F.data == 'update_categories')
async def update_category(callback_query: CallbackQuery, state: FSMContext):
    result = await BookObj().get_categories()
    keyboard = bk_kb.category_kb(result)
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer("Choose categories:", reply_markup=keyboard)
    await state.set_state(BookUpdate.category)
    await callback_query.answer()


@book_router.message(BookUpdate.category)
async def update_category(message: Message, state: FSMContext):
    selected_category = message.text
    data = await state.get_data()
    chosen_categories = set(data.get("chosen_categories", []))

    if selected_category == "✅ Done":
        if not chosen_categories:
            await message.answer("❌ You haven't selected any categories. Please choose at least one.")
            return
        categories_str = ", ".join(chosen_categories)
        await save_book_update(state, "categories", categories_str)

        await message.answer(
            f"✅ Selected categories: {categories_str}",
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(f"To save all changes, press «💾 Save Changes»", reply_markup=bk_kb.book_update_kb())
        return

    available_categories = await BookObj().get_categories()

    if selected_category in available_categories:
        if selected_category in chosen_categories:
            chosen_categories.remove(selected_category)
            await message.answer(f"❌ {selected_category} removed!\nSelect more or press '✅ Done'.")
        else:
            chosen_categories.add(selected_category)
            await message.answer(f"✅ {selected_category} added!\nSelect more or press '✅ Done'.")

        await state.update_data(chosen_categories=list(chosen_categories))
        categories_str = ", ".join(chosen_categories)
        await save_book_update(state, "categories", categories_str)

    else:
        await message.answer("⚠️ Invalid category. Please choose from the buttons.")


@book_router.callback_query(F.data == "save_changes")
async def save_changes(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    book_id = int(data.get("selected_book"))
    updates = data.get("updates", {})

    if not updates:
        await callback_query.answer("❗ No changes to save!", show_alert=True)
        return

    async with async_session_factory() as session:
        updated_book = await BookObj().update(book_id, updates, session=session)

    if updated_book:
        await callback_query.message.edit_text(
            "✅ Changes saved successfully!",
            reply_markup=bk_kb.back_to_books_menu_kb())
    else:
        await callback_query.message.edit_text("❌ Failed to update book!")

    await state.clear()


@book_router.callback_query(F.data == "book_cancel_update")
async def cancel_changes(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('🚫 All changes have been discarded!', reply_markup=None)
    await state.clear()
    await callback_query.answer()

# endregion


# region Read book

@book_router.callback_query(F.data == "book_detail")
async def book_detail(callback_query: CallbackQuery, page=1, per_page=5):
    async with async_session_factory() as session:
        books = await BookObj().read(available_books=True, session=session)

    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, len(books))
    books_page = books[start_idx:end_idx]
    text = '📚 Books \n'
    text += '\n'.join(f"📖 {index + 1}: {book.title} - {book.author}" for index, book in enumerate(books_page))

    await callback_query.message.edit_text(
        text, reply_markup=bk_kb.book_list_kb(books, 'view', page=page, per_page=per_page))


@book_router.callback_query(F.data.startswith('view_page_'))
async def view_page(callback_query: CallbackQuery):
    page = int(callback_query.data.split('_')[-1])
    await book_detail(callback_query, page=page)


@book_router.callback_query(F.data.startswith('view_select_'))
async def book_open(callback_query: CallbackQuery):
    data = callback_query.data.split('_')
    book_id = int(data[-1])
    async with async_session_factory() as session:
        book = await BookObj().get_obj(book_id, session=session)

    book_categories = await BookObj().get_book_categories(book_id, session)
    categories = "\n".join(f"• {cat}" for cat in book_categories)
    async with async_session_factory() as session:
        location = await BookObj().get_book_location(book.location_id, session)

    if book:
        text = (
            f"📚 <b>{book.title}</b>\n"
            f"✍️ <b>Author:</b> {book.author}\n"
            f"📖 <b>Description:</b>\n{book.description}\n\n"
            f"📍 <b>Location:</b>\n{location.city.value}: Room #{location.room}\n\n"
            f"🏷 <b>Category:</b>\n{categories}"
        )
        is_admin = await UserObj().is_admin(telegram_id=callback_query.from_user.id, session=session)
        await callback_query.message.edit_text(
            text,
            reply_markup=bk_kb.order_cancel_kb(
                book_id=book_id,
                location_id=location.location_id,
                is_admin=is_admin
            ), parse_mode='HTML')
    else:
        await callback_query.message.edit_text('Book not found')


@book_router.callback_query(F.data.startswith("qr_book_"))
async def get_book_qr(callback: CallbackQuery):
    book_id = int(callback.data.split("_")[2])
    async with async_session_factory() as session:
        qr_img = await BookObj().get_book_qr(session=session, book_id=book_id)
        if qr_img:
            await callback.message.answer_photo(photo=qr_img)
        else:
            await callback.message.answer("QR has not found ❌")


@book_router.callback_query(F.data == "book_view_back")
async def book_update_back(callback_query: CallbackQuery, page: int = 1, per_page: int = 5):
    await book_detail(callback_query, page, per_page)


@book_router.callback_query(F.data == 'qrcode_book')
async def books_qr(callback: CallbackQuery):
    await callback.answer()

    async with async_session_factory() as session:
        books = await BookObj().read(session=session, available_books=False)

    await callback.message.edit_text(
        "Choose a book to view the QR code:",
        reply_markup=bk_kb.show_books_kb(books)
    )


@book_router.callback_query(F.data.startswith('qr_book_'))
async def book_qr_code(callback: CallbackQuery):
    await callback.answer()
    book_id = callback.data.split("_")[2]

    async with async_session_factory() as session:
        qr_code = await BookObj().get_book_qr(int(book_id), session)

    await callback.message.answer_photo(qr_code)
# endregion


# region Navigating Buttons
@book_router.callback_query(F.data == 'back_to_list')
async def back_to_list(callback_query: CallbackQuery):
    async with async_session_factory() as session:
        books = await BookObj().read(available_books=True, session=session)

    if books:
        text = '📚 Books:\n'
        text += '\n'.join(f'📖 {index + 1}: {book.title} - {book.author}' for index, book in enumerate(books))
        await callback_query.message.edit_text(text, reply_markup=bk_kb.books_kb)
    else:
        await callback_query.message.edit_text(
            '📚 The library is currently empty', reply_markup=bk_kb.no_books_kb_admin
        )

    await callback_query.answer()


@book_router.callback_query(F.data == 'back_button')
async def back_button(callback_query: CallbackQuery, state: FSMContext):
    async with async_session_factory() as session:
        books = await BookObj().read(available_books=True, session=session)
        is_admin = await UserObj().is_admin(session=session, telegram_id=callback_query.from_user.id)

    reply_markup = bk_kb.books_kb if is_admin else bk_kb.user_book_kb

    if books:
        text = '📚 Books:\n'
        text += '\n'.join(f'📖 {index+1}: {book.title} - {book.author}' for index, book in enumerate(books))
        await callback_query.message.edit_text(text, reply_markup=reply_markup)
    else:
        await callback_query.message.edit_text('No books found', reply_markup=reply_markup)

    await state.clear()
    await callback_query.answer()

# endregion
