from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from db.database import async_session_factory
from db.models import OrderStatus
from db.queries.book_crud import BookObj
from db.queries.employee_crud import EmployeeObj
from db.queries.order_crud import OrderObj
from db.queries.role_crud import RoleObj
from db.queries.tg_user_crud import TgUserObj
from db.queries.app_user_crud import AppUserObj
from states.main_states import Reg
from keyboards import order_kbs

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    args = command.args
    telegram_id = message.from_user.id

    async with async_session_factory() as session:
        is_user_registered = await AppUserObj().is_user_registered(session=session, telegram_id=str(telegram_id))

    if not is_user_registered:
        await message.answer(
            "Welcome! 👋 To get started, please enter your email address. We'll use it to verify your identity."
        )
        await state.set_state(Reg.email)
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


@router.message(Reg.email)
async def send_verification_code(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    # send_verification_code(email)
    # add user in table Employees
    await message.answer("A 6-digit verification code has been sent to your email address."
                         "Please enter the code here in the bot to verify your email.")
    await state.set_state(Reg.code)


@router.message(Reg.code)
async def reg_code(message: Message, state: FSMContext):
    data = await state.get_data()

    async with async_session_factory() as session:
        tg_user = await TgUserObj().get_obj_by_telegram_id(session=session, telegram_id=str(message.from_user.id))
        employee = await EmployeeObj().get_obj_by_email(session=session, email=data.get('email'))
        role = await RoleObj().get_obj_by_name(session=session, name='user')

        if not tg_user or not employee or not role:
            await message.answer("❌ Registration failed. Some data is missing or incorrect.")
            return

        success = await AppUserObj().create(
            session=session,
            telegram_id=str(message.from_user.id),
            tg_user_id=tg_user.id,
            employee_id=employee.id,
            role_id=role.id
        )

    if success:
        await message.answer(
            f"✅ <b>Registration Complete!</b>\n"
            f"👤 You are now registered!</b>\n\n"
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
