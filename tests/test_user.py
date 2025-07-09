import pytest

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from db.models import User
from db.queries.user_crud import UserObj


@pytest.mark.asyncio
async def test_user_model(db_session, sample_users):
    result = await db_session.execute(select(User).where(User.telegram_id == 12345))
    user_from_db = result.scalar_one()

    assert user_from_db.telegram_id == 12345
    assert user_from_db.name == "A"
    assert user_from_db.surname == "B"
    assert user_from_db.is_admin is False

    result = await db_session.execute(select(User).where(User.telegram_id == 77777))
    user_from_db_2 = result.scalar_one()

    assert user_from_db_2.telegram_id == 77777
    assert user_from_db_2.name == "Admin"
    assert user_from_db_2.surname == "Vention"
    assert user_from_db_2.is_admin is True

    result = await db_session.execute(select(User))
    users_from_db = result.scalars().all()

    assert len(users_from_db) == 3


@pytest.mark.asyncio
async def test_user_create(db_session, sample_users, mocker):
    await UserObj().create(session=db_session, telegram_id=123456789, name="John", surname="Doe")
    await UserObj().create(session=db_session, telegram_id=987654321, name="Jane", surname="Doe")
    user_3 = await UserObj().create(session=db_session, telegram_id=12345, name="A", surname="DD")

    result = await db_session.execute(select(User))
    users = result.scalars().all()

    user_1, user_2 = users[3], users[4]

    assert len(users) == 5
    assert user_1.telegram_id == 123456789 and user_1.name == "John" and user_1.surname == "Doe"
    assert user_1.is_admin is False
    assert user_2.telegram_id == 987654321 and user_2.name == "Jane" and user_2.surname == "Doe"
    assert user_2.is_admin is False
    assert user_3 is False

    mocker.patch.object(db_session, 'add', side_effect=SQLAlchemyError("DB error"))

    user_4 = await UserObj().create(session=db_session, telegram_id=123456, name="Jane", surname="Doe")
    assert user_4 is False


@pytest.mark.asyncio
async def test_user_get_obj(db_session, sample_users, mocker):
    user_1 = await UserObj().get_obj(session=db_session, telegram_id=12345)
    user_2 = await UserObj().get_obj(session=db_session, telegram_id=54321)

    assert user_1.telegram_id == 12345 and user_1.name == "A" and user_1.surname == "B"
    assert user_1.is_admin is False
    assert user_2.telegram_id == 54321 and user_2.name == "C" and user_2.surname == "D"
    assert user_2.is_admin is False

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    user_3 = await UserObj().get_obj(session=db_session, telegram_id=12345)

    assert user_3 is None


@pytest.mark.asyncio
async def test_user_read(db_session, sample_users, mocker):
    users = await UserObj().read(session=db_session)
    user_1, user_2 = users[0], users[1]

    assert len(users) == 3
    assert user_1.telegram_id == 12345 and user_1.name == "A" and user_1.surname == "B"
    assert user_1.is_admin is False
    assert user_2.telegram_id == 54321 and user_2.name == "C" and user_2.surname == "D"
    assert user_2.is_admin is False

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    users_2 = await UserObj().read(session=db_session)

    assert len(users_2) == 0


@pytest.mark.asyncio
async def test_user_get_id_by_name(db_session, sample_users, mocker):
    user_1_telegram_id = await UserObj().get_user_id_by_name(session=db_session, name="A", surname="B")
    user_2_telegram_id = await UserObj().get_user_id_by_name(session=db_session, name="AAA", surname="DDD")

    assert user_1_telegram_id == 12345
    assert user_2_telegram_id is None

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    user_1 = await UserObj().get_user_id_by_name(session=db_session, name='C', surname='D')

    assert user_1 is None


@pytest.mark.asyncio
async def test_is_user_registered(db_session, sample_users, mocker):
    is_user_1 = await UserObj().is_user_registered(session=db_session, telegram_id=12345)
    is_user_2 = await UserObj().is_user_registered(session=db_session, telegram_id=987654321)

    assert is_user_1 is True
    assert is_user_2 is False

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))

    is_user_3 = await UserObj().is_user_registered(session=db_session, telegram_id=12345)
    assert is_user_3 is False


@pytest.mark.asyncio
async def test_is_admin(db_session, sample_users, mocker):
    is_user_1_admin = await UserObj().is_admin(session=db_session, telegram_id=12345)
    is_user_2_admin = await UserObj().is_admin(session=db_session, telegram_id=77777)

    assert is_user_1_admin is False
    assert is_user_2_admin is True

    mocker.patch.object(db_session, 'get', side_effect=SQLAlchemyError("DB error"))
    is_user_3_admin = await UserObj().is_admin(session=db_session, telegram_id=12345)

    assert is_user_3_admin is False


@pytest.mark.asyncio
async def test_user_update():
    user = await UserObj().update()

    assert user is None


@pytest.mark.asyncio
async def test_user_remove():
    user = await UserObj().remove()

    assert user is None
