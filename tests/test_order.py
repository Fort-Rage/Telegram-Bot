# import pytest
# from sqlalchemy import select
# from sqlalchemy.exc import SQLAlchemyError
#
# from db.models import Order, OrderStatus
# from db.queries.order_crud import OrderObj
#
#
# @pytest.mark.asyncio
# async def test_order_create(db_session, sample_users, sample_locations, sample_books, mocker):
#     new_order = await OrderObj().create(
#         session=db_session,
#         app_user_id=(await sample_users)[0].id,
#         book_id=(await sample_books)[0].id,
#         taken_from_id=(await sample_locations)[0].id,
#         returned_to_id=(await sample_locations)[0].id
#     )
#
#     result = await db_session.execute(select(Order))
#     test_order = result.scalars().all()
#
#     assert len(test_order) == 1
#     assert test_order[0].telegram_id == 12345
#     assert new_order is True
#
#     mocker.patch.object(db_session, 'add', side_effect=SQLAlchemyError("DB error"))
#
#     fail_order = await OrderObj().create(
#         session=db_session,
#         user_id=54321,
#         book_id=2,
#         taken_from_id=1,
#         returned_to_id=2
#     )
#
#     result = await db_session.execute(select(Order))
#     test_order = result.scalars().all()
#
#     assert len(test_order) == 1
#     assert fail_order is False
#
#
# @pytest.mark.asyncio
# async def test_order_read(db_session, sample_users, sample_locations, sample_books, sample_orders, mocker):
#     orders = await OrderObj().read(session=db_session, user_id=12345)
#
#     assert len(orders) == 2
#     assert orders[0].telegram_id == 12345
#
#     mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
#     fail_orders = await OrderObj().read(session=db_session, user_id=54321)
#
#     assert fail_orders == []
#
#
# @pytest.mark.asyncio
# async def test_order_update(db_session):
#     a = await OrderObj().update(db_session)
#     assert a is None
#
#
# @pytest.mark.asyncio
# async def test_order_remove(db_session, sample_users, sample_locations, sample_books, sample_orders, mocker):
#     removed_order_1 = await OrderObj().remove(session=db_session, order_id=1)
#     removed_order_2 = await OrderObj().remove(session=db_session, order_id=4)
#
#     assert removed_order_1 is True
#     assert removed_order_2 is False
#
#     mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
#
#     removed_order_3 = await OrderObj().remove(session=db_session, order_id=3)
#     assert removed_order_3 is False
#
#
# @pytest.mark.asyncio
# async def test_order_get_obj(db_session, sample_users, sample_locations, sample_books, sample_orders, mocker):
#     order_1 = await OrderObj().get_obj(session=db_session, order_id=1)
#
#     assert order_1 is not None
#     assert order_1.telegram_id == 12345
#
#     mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
#
#     order_2 = await OrderObj().get_obj(session=db_session, order_id=2)
#
#     assert order_2 is None
#
#
# @pytest.mark.asyncio
# async def test_order_update_status(db_session, sample_users, sample_locations, sample_books, sample_orders, mocker):
#     order_upd = await OrderObj().update_status(session=db_session, order_id=1, new_status=OrderStatus.CANCELLED)
#     order_upd2 = await OrderObj().update_status(session=db_session, order_id=5, new_status=OrderStatus.CANCELLED)
#     order_upd3 =  await OrderObj().get_obj(session=db_session, order_id=1)
#
#     assert order_upd is True
#     assert order_upd2 is False
#     assert order_upd3.status == OrderStatus.CANCELLED
#
#     mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
#     order_upd4 = await OrderObj().update_status(session=db_session, order_id=1, new_status=OrderStatus.CANCELLED)
#     assert order_upd4 is False
#
#
# @pytest.mark.asyncio
# async def test_status_and_location(db_session, sample_users, sample_locations, sample_books, sample_orders, mocker):
#     order_1 = await OrderObj().update_status_and_location(
#         session=db_session, order_id=1, new_status=OrderStatus.CANCELLED, location_id=2
#     )
#     order_2 = await OrderObj().update_status_and_location(
#         session=db_session, order_id=5, new_status=OrderStatus.CANCELLED, location_id=2
#     )
#     assert order_1 is True
#     assert order_2 is False
#
#     mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
#     order_3 = await OrderObj().update_status_and_location(
#         session=db_session, order_id=1, new_status=OrderStatus.CANCELLED, location_id=2
#     )
#
#     assert order_3 is False
#
#
# @pytest.mark.asyncio
# async def test_is_order_exist(db_session, sample_users, sample_locations, sample_books, sample_orders):
#     order_1 = await OrderObj().is_order_exist(session=db_session,user_id=12345, book_id=1)
#     order_2 = await OrderObj().is_order_exist(session=db_session,user_id=12345, book_id=412)
#
#     assert order_1 is True
#     assert order_2 is None
#
#
# @pytest.mark.asyncio
# async def test_is_book_taken(db_session, sample_users, sample_locations, sample_books, sample_orders, mocker):
#     order_1 = await OrderObj().is_book_taken(session=db_session,book_id=1)
#
#     assert order_1 is True
