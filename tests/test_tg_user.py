import pytest

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from db.models import TelegramUsers
from db.queries.tg_user_crud import TgUserObj


@pytest.mark.asyncio
async def test_tg_user_model(db_session, sample_tg_users):
    result = await db_session.execute(select(TelegramUsers))
    tg_users = result.scalars().all()

    tg_user = await db_session.get(TelegramUsers, tg_users[0].id)
    tg_user_2 = await db_session.get(TelegramUsers, tg_users[1].id)

    assert tg_user.telegram_id == "12345"
    assert tg_user.username == "user_a"

    assert tg_user_2.telegram_id == "54321"
    assert tg_user_2.username == "admin_user"


@pytest.mark.asyncio
async def test_tg_user_create(db_session, mocker):
    await TgUserObj().create(session=db_session, telegram_id="12345", username="user_a")
    await TgUserObj().create(session=db_session, telegram_id="54321", username="user_b")
    tg_user_3 = await TgUserObj().create(session=db_session, telegram_id="00000", username="user_c")

    result = await db_session.execute(select(TelegramUsers).order_by(TelegramUsers.id))
    tg_users = result.scalars().all()
    tg_user_1, tg_user_2 = tg_users[0], tg_users[1]

    assert len(tg_users) == 3
    assert tg_user_1.telegram_id == "12345" and tg_user_1.username == "user_a"
    assert tg_user_2.telegram_id == "54321" and tg_user_2.username == "user_b"
    assert tg_user_3 is True

    # Invalid data
    invalid_tg_user_1 = await TgUserObj().create(session=db_session, telegram_id="11111", username=None)
    assert invalid_tg_user_1 is False

    invalid_tg_user_2 = await TgUserObj().create(session=db_session, telegram_id=None, username="valid_username")
    assert invalid_tg_user_2 is False

    invalid_tg_user_3 = await TgUserObj().create(session=db_session, telegram_id="", username="valid_username")
    assert invalid_tg_user_3 is False

    invalid_tg_user_4 = await TgUserObj().create(session=db_session, telegram_id="11111", username="")
    assert invalid_tg_user_4 is False

    invalid_tg_user_5 = await TgUserObj().create(session=db_session, telegram_id=12345, username="valid_username")
    assert invalid_tg_user_5 is False

    invalid_tg_user_6 = await TgUserObj().create(session=db_session, telegram_id="11111", username=12345)
    assert invalid_tg_user_6 is False

    invalid_tg_user_7 = await TgUserObj().create(session=db_session, telegram_id="12345", username="user_a")
    assert invalid_tg_user_7 is False

    mocker.patch.object(db_session, 'add', side_effect=SQLAlchemyError("DB error"))
    db_error_tg_user = await TgUserObj().create(session=db_session, telegram_id="123456", username="db_error_user")
    assert db_error_tg_user is False


@pytest.mark.asyncio
async def test_tg_user_get_obj_by_telegram_id(db_session, sample_tg_users, mocker):
    tg_user_1 = await TgUserObj().get_obj_by_telegram_id(session=db_session, telegram_id="12345")
    tg_user_2 = await TgUserObj().get_obj_by_telegram_id(session=db_session, telegram_id="54321")
    tg_user_3 = await TgUserObj().get_obj_by_telegram_id(session=db_session, telegram_id="11111")

    assert tg_user_1.telegram_id == "12345" and tg_user_1.username == "user_a"
    assert tg_user_2.telegram_id == "54321" and tg_user_2.username == "admin_user"
    assert tg_user_3 is None

    # Invalid data
    invalid_tg_user_1 = await TgUserObj().get_obj_by_telegram_id(session=db_session, telegram_id=None)
    assert invalid_tg_user_1 is None

    invalid_tg_user_2 = await TgUserObj().get_obj_by_telegram_id(session=db_session, telegram_id="")
    assert invalid_tg_user_2 is None

    invalid_tg_user_3 = await TgUserObj().get_obj_by_telegram_id(session=db_session, telegram_id=12345)
    assert invalid_tg_user_3 is None

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    db_error_tg_user = await TgUserObj().get_obj_by_telegram_id(session=db_session, telegram_id="12345")
    assert db_error_tg_user is None


@pytest.mark.asyncio
async def test_tg_user_read():
    tg_user = await TgUserObj().read()
    assert tg_user is None


@pytest.mark.asyncio
async def test_app_user_update():
    tg_user = await TgUserObj().update()
    assert tg_user is None


@pytest.mark.asyncio
async def test_app_user_remove():
    tg_user = await TgUserObj().remove()
    assert tg_user is None


@pytest.mark.asyncio
async def test_app_user_get_obj():
    tg_user = await TgUserObj().get_obj()
    assert tg_user is None
