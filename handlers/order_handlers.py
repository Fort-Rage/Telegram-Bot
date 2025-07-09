from datetime import timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from db.database import async_session_factory
from db.models import OrderStatus
from db.queries.order_crud import OrderObj
from keyboards import order_kbs

router = Router()


@router.message(Command("orders"))
async def order_handler(message: Message):
    async with async_session_factory() as session:
        orders = await OrderObj().read(session=session, user_id=message.from_user.id)

    if not orders:
        await message.answer("📋 You don't have any orders yet", reply_markup=order_kbs.no_order_kb)
        return

    messages = ["📋 <b>Orders:</b>"]

    for idx, order in enumerate(orders, 1):
        text = f"📖 {idx}. <b>{order.book.title}</b>\n"

        if order.status.value == 'Reserved':
            text += f"📍 <b>Location:</b> {order.taken_from.city.value}: Room #{order.taken_from.room}\n"
        elif order.status.value == 'Returned' and order.returned_to:
            text += f"📍 <b>Returned to:</b> {order.returned_to.city.value}: Room #{order.returned_to.room}\n"

        text += f"ℹ️ {order.status.value}"

        messages.append(text)

    has_reserved = any(order.status.value == "Reserved" for order in orders)

    await message.answer("\n\n".join(messages), reply_markup=await order_kbs.get_order_kb(has_reserved),
                         parse_mode='HTML')


@router.callback_query(F.data.startswith("order-book_"))
async def create_order(callback: CallbackQuery):
    await callback.answer()

    _, book_id, location_id = callback.data.split("_")

    async with async_session_factory() as session:
        success = await OrderObj().create(session=session, user_id=callback.from_user.id,
                                          book_id=int(book_id), taken_from_id=int(location_id))

    if success:
        await callback.message.edit_text(
            "✅ Your order has been successfully created!\n\n"
            "📋 To view your orders, press /orders"
        )
    else:
        await callback.message.edit_text(
            f"❌ Oops! Failed to create order\n\n<i>🔄 Please try again later</i>", parse_mode='HTML'
        )


@router.callback_query(F.data.startswith("order-"))
async def action_order(callback: CallbackQuery):
    await callback.answer()
    action = callback.data.split("-")[1]

    message_text = ""

    async with async_session_factory() as session:
        orders = await OrderObj().read(session=session, user_id=callback.from_user.id)

    if action == 'cancel':
        message_text = "🚫 Choose an order to cancel:"
    elif action == 'detail':
        message_text = "ℹ️ Choose an order to view details:"

    await callback.message.edit_text(message_text, reply_markup=await order_kbs.action_order_kb(action, orders))


@router.callback_query(F.data.startswith("order_detail_"))
async def detail_order(callback: CallbackQuery):
    await callback.answer()
    order_id = callback.data.split("_")[2]

    async with async_session_factory() as session:
        order = await OrderObj().get_obj(session=session, order_id=int(order_id))

    message_text = (
        f"📚 <b>{order.book.title}</b>\n"
        f"✍️ <b>Author:</b> {order.book.author}\n"
        f"📖 <b>Description:</b> {order.book.description}\n\n"
        f"📍 <b>Location:</b>\n"
        f"• <b>Taken from:</b> {order.taken_from.city.value}: Room #{order.taken_from.room}\n"
    )

    if order.returned_to_id:
        message_text += (
            f"• <b>Returned to:</b> {order.returned_to.city.value}: Room #{order.returned_to.room}\n"
        )

    message_text += (
        f"\n📅 <b>Order date:</b> {(order.created_at + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M')}\n"
        f"ℹ️ <b>Status:</b> {order.status.value}\n\n"
    )

    keyboard = order_kbs.back_to_detail_order_kb

    await callback.message.edit_text(message_text, reply_markup=keyboard, parse_mode='HTML')


@router.callback_query(F.data.startswith("return_book_"))
async def confirm_return_order(callback: CallbackQuery):
    await callback.answer()
    location_id = int(callback.data.split("_")[2])

    async with async_session_factory() as session:
        orders = await OrderObj().read(session=session, user_id=callback.from_user.id)

    await callback.message.edit_text("↩️ Choose a book to return:",
                                     reply_markup=await order_kbs.return_order_kb(orders, location_id))


@router.callback_query(F.data.startswith("order_return_"))
async def return_order(callback: CallbackQuery):
    await callback.answer()
    order_id, location_id = int(callback.data.split("_")[2]), int(callback.data.split("_")[3])

    async with async_session_factory() as session:
        success = await OrderObj().update_status_and_location(
            session=session,
            order_id=int(order_id),
            new_status=OrderStatus.RETURNED,
            location_id=int(location_id)
        )
        order = await OrderObj().get_obj(session=session, order_id=int(order_id))

    message_text = (
        f"✅ The book <b>\"{order.book.title}\"</b> has been returned to <b>{order.returned_to.city.value}: "
        f"Room #{order.returned_to.room}</b>"
        if success else
        "❌ Oops! Failed to return a book\n\n<i>🔄 Please try again later</i>"
    )

    await callback.message.edit_text(message_text, reply_markup=order_kbs.back_to_order_kb, parse_mode='HTML')


@router.callback_query(F.data.startswith("order_cancel_"))
async def cancel_order(callback: CallbackQuery):
    await callback.answer()
    order_id = callback.data.split("_")[2]

    async with async_session_factory() as session:
        success = await OrderObj().update_status(session=session, order_id=int(order_id),
                                                 new_status=OrderStatus.CANCELLED)
        order = await OrderObj().get_obj(session=session, order_id=int(order_id))

    message_text = (
        f"🚫 The order for <b>\"{order.book.title}\"</b> has been successfully cancelled"
        if success else
        "❌ Oops! Failed to cancel the order\n\n<i>🔄 Please try again later</i>"
    )
    await callback.message.edit_text(message_text, reply_markup=order_kbs.back_to_order_kb, parse_mode='HTML')


@router.callback_query(F.data == "back_to_order")
async def back_to_order(callback: CallbackQuery):
    async with async_session_factory() as session:
        orders = await OrderObj().read(session=session, user_id=callback.from_user.id)

    if not orders:
        await callback.message.edit_text("📋 You don't have any orders yet", reply_markup=order_kbs.no_order_kb)
        return

    messages = ["📋 <b>Orders:</b>"]

    for idx, order in enumerate(orders, 1):
        text = f"📖 {idx}. <b>{order.book.title}</b>\n"

        if order.status.value == 'Reserved':
            text += f"📍 <b>Location</b> {order.taken_from.city.value}: Room #{order.taken_from.room}\n"
        elif order.status.value == 'Returned' and order.returned_to:
            text += f"📍 <b>Returned to:</b> {order.returned_to.city.value}: Room #{order.returned_to.room}\n"

        text += f"ℹ️ {order.status.value}"

        messages.append(text)

    has_reserved = any(order.status.value == "Reserved" for order in orders)

    await callback.message.edit_text("\n\n".join(messages), reply_markup=await order_kbs.get_order_kb(has_reserved),
                                     parse_mode='HTML')


@router.callback_query(F.data == "close_order")
async def close_order(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
