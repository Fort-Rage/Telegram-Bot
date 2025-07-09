from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from db.database import async_session_factory
from db.queries.location_crud import LocationObj
from db.queries.user_crud import UserObj
from keyboards import location_kbs as loc_kbs
from states.main_states import LocationForm

router = Router()


@router.message(Command('locations'))
async def show_locations(message: Message):
    async with async_session_factory() as session:
        locations = await LocationObj().read(session)
        user_admin = await UserObj().is_admin(session=session, telegram_id=message.from_user.id)

        if locations:
            response_text = "📍Locations: \n"
            response_text += "\n".join(
                f"{index + 1:2}. {location.city.value}: {location.room}" for index, location in enumerate(locations)
            )
        else:
            response_text = "🔍 No locations available yet!"

    reply_markup = loc_kbs.location_menu_kb if user_admin and locations else \
        loc_kbs.add_location_kb if user_admin else None

    await message.answer(response_text, reply_markup=reply_markup, parse_mode="HTML")


@router.callback_query(F.data == 'add_location')
async def add_location_city(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    result = await LocationObj.get_cities()

    await callback.message.answer("🏙️ Choose city:", reply_markup=loc_kbs.city_kb(result))
    await state.set_state(LocationForm.add_location_city)


@router.message(LocationForm.add_location_city)
async def add_location_room(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("#️⃣ Enter room number:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(LocationForm.add_location_room)


@router.message(LocationForm.add_location_room)
async def confirmation_input(message: Message, state: FSMContext):
    await state.update_data(room=message.text)
    await message.answer(f"⏳ Confirm the new location {message.text}?", reply_markup=loc_kbs.location_confirm())


@router.callback_query(F.data == 'loc_confirm')
async def confirmation_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_location_city = data.get("city")
    new_location_room = data.get("room")
    call_from_book = data.get('prev_callback', 'no')
    async with async_session_factory() as session:
        location_id = await LocationObj.get_location_id(new_location_city, new_location_room, session)
        new_location = await LocationObj().get_obj(location_id, session)

    await callback.message.edit_reply_markup(reply_markup=None)
    kb = loc_kbs.back_to_loc_menu()
    if new_location:
        await callback.message.answer(
            f"🚫 New location '{new_location_city}: {new_location_room} ' already exists! Try again:",
            reply_markup=kb
        )
        await state.set_state(LocationForm.add_location_city)

    else:
        await LocationObj().create(
            city=new_location_city,
            room=new_location_room,
            session=session
        )
        if call_from_book != 'no':
            kb = loc_kbs.back_to_loc_or_book()

        await callback.message.answer(
            f"✅ The location <b>\"{new_location_city}: {new_location_room}\"</b> has been successfully created!",
            reply_markup=kb, parse_mode='HTML'
        )
        await state.clear()

    await callback.answer()


@router.callback_query(F.data == 'loc_cancel')
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("✖️ Location adding process cancelled.", reply_markup=loc_kbs.back_to_loc_menu())
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == 'update_location')
async def update_location(callback: CallbackQuery, state: FSMContext):
    async with async_session_factory() as session:
        result = await LocationObj().read(session)
    if result:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("📍Choose location to update: ", reply_markup=loc_kbs.locations_kb(result))
        await state.set_state(LocationForm.update_location_id)
        await callback.answer()
    else:
        await callback.message.edit_text('❌ We don’t have any locations', reply_markup=loc_kbs.back_to_loc_menu())


@router.message(LocationForm.update_location_id)
async def update_location_callback_id(message: Message, state: FSMContext):
    loc_city = message.text.split(':')[0]
    loc_room = message.text.split(':')[1].strip()
    async with async_session_factory() as session:
        location_id = await LocationObj.get_location_id(loc_city, loc_room, session)
        await state.update_data(location_id=location_id)
        if await LocationObj().get_obj(int(location_id), session):
            result = await LocationObj.get_cities()
            await message.answer("🏙 Choose City:", reply_markup=loc_kbs.city_kb(result))
            await state.set_state(LocationForm.update_location_city)
        else:
            await message.answer('🚫 Incorrect location ID. Please try again:')
            await state.set_state(LocationForm.update_location_id)


@router.message(LocationForm.update_location_city)
async def location_update_name_handler(message: Message, state: FSMContext):
    location_city = message.text
    await state.update_data(location_city=location_city)
    await message.answer("#️⃣ Enter room number:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(LocationForm.update_location_name)


@router.message(LocationForm.update_location_name)
async def update_location_callback_name(message: Message, state: FSMContext):
    data = await state.get_data()
    loc_room_number = message.text
    city = data.get('location_city')

    async with async_session_factory() as session:
        success = await LocationObj().update(
            location_id=int(data.get('location_id')),
            city=city,
            room=loc_room_number,
            session=session
        )

    if success:
        await message.answer(f"✅ The location has been successfully updated to <b>\"{city}: {loc_room_number}\"</b>",
                             reply_markup=loc_kbs.back_to_loc_menu(), parse_mode='HTML')

    await state.clear()


@router.callback_query(F.data == 'remove_location')
async def remove_location_callback(callback: CallbackQuery, state: FSMContext):
    async with async_session_factory() as session:
        result = await LocationObj().read(session)
    if result:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("📍 Choose a location to delete:", reply_markup=loc_kbs.locations_kb(result))
        await state.set_state(LocationForm.remove_location_id)
    else:
        await callback.message.edit_text('❌ We don’t have any locations', reply_markup=loc_kbs.back_to_loc_menu())


@router.message(LocationForm.remove_location_id)
async def remove_location_confirm(message: Message, state: FSMContext):
    loc_city = message.text.split(':')[0]
    loc_room = message.text.split(':')[1].strip()
    async with async_session_factory() as session:
        location_id = await LocationObj.get_location_id(loc_city, loc_room, session)

    await state.update_data(location_id=location_id)
    async with async_session_factory() as session:
        if await LocationObj().remove(int(location_id), session):
            await message.answer(
                "✅ The location has been successfully deleted!",
                reply_markup=ReplyKeyboardRemove()
            )
            await message.answer(
                "You can go back to the Locations menu 🔙 ",
                reply_markup=loc_kbs.back_to_loc_menu()
            )
            await state.clear()

        else:
            await message.answer(
                "⚠️ This location cannot be deleted while it contains books!",
                reply_markup=ReplyKeyboardRemove()
            )
            await message.answer(
                "You can go back to the Locations menu 🔙 ",
                reply_markup=loc_kbs.back_to_loc_menu()
            )


@router.callback_query(F.data == 'qrcode_location')
async def detail_location(callback: CallbackQuery):
    await callback.answer()

    async with async_session_factory() as session:
        locations = await LocationObj().read(session=session)

    await callback.message.edit_text(
        "Choose a location to view the QR code:",
        reply_markup=loc_kbs.show_locations_kb(locations)
    )


@router.callback_query(F.data.startswith('show_qrcode_'))
async def detail_location(callback: CallbackQuery):
    await callback.answer()
    location_id = callback.data.split("_")[2]

    async with async_session_factory() as session:
        qr_code = await LocationObj().get_qr_code(int(location_id), session)

    await callback.message.answer_photo(qr_code)


@router.callback_query(F.data == 'back_to_loc_menu')
async def back_to_loc_menu_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    async with async_session_factory() as session:
        locations = await LocationObj().read(session)

        if locations:
            response_text = "📍Locations: \n"
            response_text += "\n".join(
                f"{index + 1:2}. {loc.city.value}: {loc.room}" for index, loc in enumerate(locations)
            )

        else:
            response_text = "🔍 No locations available yet!"

    reply_markup = loc_kbs.location_menu_kb if locations else loc_kbs.add_location_kb
    await callback.message.edit_text(response_text, reply_markup=reply_markup, parse_mode="HTML")
