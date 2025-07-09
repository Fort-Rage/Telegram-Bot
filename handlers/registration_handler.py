from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from db.database import async_session_factory
from db.models import OrderStatus
from db.queries.book_crud import BookObj
from db.queries.order_crud import OrderObj
from db.queries.user_crud import UserObj
from states.main_states import Reg
from keyboards import user_kbs, order_kbs

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    args = command.args
    telegram_id = message.from_user.id

    async with async_session_factory() as session:
        is_user_registered = await UserObj().is_user_registered(session=session, telegram_id=telegram_id)

    if not is_user_registered:
        await message.answer(
            "Welcome! 👋 Let's get you registered so I can better assist you. "
            "It will only take a minute. Shall we get started?",
            reply_markup=user_kbs.registration_kb
        )
        return

    if args:
        if args.startswith("location_"):
            location_id = int(args.split("_")[1])
            orders = await OrderObj().read(session=session, user_id=telegram_id)

            await message.answer("↩️ Choose a book to return:",
                                 reply_markup=await order_kbs.return_order_kb(orders, location_id))
            return

        elif args.startswith("book_"):
            book_id = int(args.split("_")[1])

            order = await OrderObj.is_order_exist(session=session, user_id=telegram_id, book_id=book_id)

            if order:
                await message.answer("✅ Reservation confirmed! Feel free to pick up your book 📚")
            else:
                is_taken = await OrderObj.is_book_taken(session=session, book_id=book_id)
                if is_taken:
                    await message.answer("❌Unfortunately, this book has been taken already!")
                else:
                    book_loc = await BookObj().get_obj(session=session, book_id=book_id)
                    new_order = await OrderObj().create(
                        session=session,
                        user_id=telegram_id,
                        book_id=book_id,
                        status=OrderStatus.IN_PROCESS,
                        taken_from_id=book_loc.location_id,
                    )
                    if new_order:
                        await message.answer("📚 Your reservation is ready! You can pick up your book.")
            return

    await message.answer(
        "You are already registered. Feel free to take advantage of all the features! 🚀"
    )


@router.callback_query(F.data == "reg_no")
async def reg_stop(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await callback.message.answer("If you change your mind, just type /start. See you soon!")


@router.callback_query(F.data == "reg_yes")
async def reg_start(callback: CallbackQuery, state: FSMContext):
    async with async_session_factory() as session:
        is_user_registered = await UserObj().is_user_registered(session=session, telegram_id=callback.from_user.id)

    if is_user_registered:
        await callback.answer("You are already registered!")
        await callback.message.delete_reply_markup()
    else:
        await callback.answer()
        await callback.message.delete_reply_markup()
        await callback.message.answer("What's your first name? 😊 Please enter your name:")
        await state.set_state(Reg.name)


@router.message(Reg.name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.lower().capitalize())
    state_data = await state.get_data()
    await message.answer(f"Great, {state_data.get('name')}! Now, please enter your last name:")
    await state.set_state(Reg.surname)


@router.message(Reg.surname)
async def reg_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text.lower().capitalize())
    state_data = await state.get_data()

    async with async_session_factory() as session:
        success = await UserObj().create(session=session,
                                         telegram_id=message.from_user.id,
                                         name=state_data.get('name'),
                                         surname=state_data.get('surname'))

    if success:
        await message.answer(
            f"✅ <b>Registration Complete!</b>\n"
            f"👤 You are now registered as <b>{state_data.get('name')} {state_data.get('surname')}</b>\n\n"
            f"🚀 Enjoy using the bot! Here are some useful commands to get started:\n\n"
            f"📚 /books – Explore our full book collection\n"
            f"📍 /locations – Discover available pickup locations\n"
            f"📋 /orders – View and manage your orders\n"
            f"⭐ /wishlists – View and manage your wishlists",
            parse_mode='HTML'
        )
    else:
        await message.answer("❌ <b>Registration failed!</b>\n An error occurred while saving your data"
                             "\n\n<i>Please try again later</i>", parse_mode='HTML')

    await state.clear()
