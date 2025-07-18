import pytest

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from uuid6 import uuid7

from db.models import AppUsers, TelegramUsers, Employees, Roles
from db.queries.app_user_crud import AppUserObj


@pytest.mark.asyncio
async def test_app_user_model(db_session, sample_app_users):
    result = await db_session.execute(select(AppUsers))
    app_users = result.scalars().all()

    app_users_1 = await db_session.get(AppUsers, app_users[0].id)
    app_users_2 = await db_session.get(AppUsers, app_users[1].id)

    assert app_users_1.tg_user_id == app_users[0].tg_user_id
    assert app_users_1.employee_id == app_users[0].employee_id
    assert app_users_1.role_id == app_users[0].role_id
    assert app_users_1.is_active is False

    assert app_users_2.tg_user_id == app_users[1].tg_user_id
    assert app_users_2.employee_id == app_users[1].employee_id
    assert app_users_2.role_id == app_users[1].role_id
    assert app_users_2.is_active is True


@pytest.mark.asyncio
async def test_app_user_create(db_session, sample_tg_users, sample_employees, sample_roles):
    result = await db_session.execute(select(TelegramUsers))
    tg_users = result.scalars().all()
    result = await db_session.execute(select(Employees))
    employees = result.scalars().all()
    result = await db_session.execute(select(Roles))
    roles = result.scalars().all()

    tg_user_1_tg_id, tg_user_1_id, employee_1_id, role_1_id = (tg_users[0].telegram_id, tg_users[0].id,
                                                               employees[0].id, roles[0].id)

    tg_user_2_tg_id, tg_user_2_id, employee_2_id, role_2_id = (tg_users[1].telegram_id, tg_users[1].id,
                                                               employees[1].id, roles[1].id)

    await AppUserObj().create(session=db_session, telegram_id=tg_user_1_tg_id,
                              tg_user_id=tg_user_1_id, employee_id=employee_1_id, role_id=role_1_id)

    app_user_2 = await AppUserObj().create(session=db_session, telegram_id=tg_user_2_tg_id,
                                           tg_user_id=tg_user_2_id, employee_id=employee_2_id, role_id=role_2_id)

    app_user_3 = await AppUserObj().create(session=db_session, telegram_id=tg_user_2_tg_id,
                                           tg_user_id=tg_user_2_id, employee_id=employee_2_id, role_id=role_2_id)

    app_user_4 = await AppUserObj().create(session=db_session, telegram_id="11111",
                                           tg_user_id=uuid7(), employee_id=uuid7(), role_id=uuid7())

    result = await db_session.execute(select(AppUsers).order_by(AppUsers.id))
    app_users = result.scalars().all()
    app_user_1 = app_users[0]

    assert len(app_users) == 2
    assert app_user_1.tg_user_id == tg_user_1_id
    assert app_user_1.employee_id == employee_1_id
    assert app_user_1.role_id == role_1_id
    assert app_user_1.is_active is True
    assert app_user_2 is True
    assert app_user_3 is False and app_user_4 is False


@pytest.mark.asyncio
async def test_app_user_create_invalid(db_session, sample_tg_users, sample_employees, sample_roles):
    result = await db_session.execute(select(TelegramUsers))
    tg_users = result.scalars().all()
    result = await db_session.execute(select(Employees))
    employees = result.scalars().all()
    result = await db_session.execute(select(Roles))
    roles = result.scalars().all()

    telegram_id, tg_user_id, employee_id, role_id = (tg_users[0].telegram_id, tg_users[0].id,
                                                     employees[0].id, roles[0].id)

    # Invalid data
    invalid_app_user_1 = await AppUserObj().create(session=db_session, telegram_id=None,
                                                   tg_user_id=tg_user_id, employee_id=employee_id, role_id=role_id)
    assert invalid_app_user_1 is False
    invalid_app_user_1 = await AppUserObj().create(session=db_session, telegram_id="",
                                                   tg_user_id=tg_user_id, employee_id=employee_id, role_id=role_id)
    assert invalid_app_user_1 is False
    invalid_app_user_1 = await AppUserObj().create(session=db_session, telegram_id=12345,
                                                   tg_user_id=tg_user_id, employee_id=employee_id, role_id=role_id)
    assert invalid_app_user_1 is False

    invalid_app_user_2 = await AppUserObj().create(session=db_session, telegram_id=telegram_id,
                                                   tg_user_id=None, employee_id=employee_id, role_id=role_id)
    assert invalid_app_user_2 is False
    invalid_app_user_2 = await AppUserObj().create(session=db_session, telegram_id=telegram_id,
                                                   tg_user_id="", employee_id=employee_id, role_id=role_id)
    assert invalid_app_user_2 is False

    invalid_app_user_3 = await AppUserObj().create(session=db_session, telegram_id=telegram_id,
                                                   tg_user_id=tg_user_id, employee_id=None, role_id=role_id)
    assert invalid_app_user_3 is False
    invalid_app_user_3 = await AppUserObj().create(session=db_session, telegram_id=telegram_id,
                                                   tg_user_id=tg_user_id, employee_id="", role_id=role_id)
    assert invalid_app_user_3 is False

    invalid_app_user_4 = await AppUserObj().create(session=db_session, telegram_id=telegram_id,
                                                   tg_user_id=tg_user_id, employee_id=employee_id, role_id=None)
    assert invalid_app_user_4 is False
    invalid_app_user_4 = await AppUserObj().create(session=db_session, telegram_id=telegram_id,
                                                   tg_user_id=tg_user_id, employee_id=employee_id, role_id="")
    assert invalid_app_user_4 is False


@pytest.mark.asyncio
async def test_app_user_read(db_session, sample_app_users, mocker):
    app_users = await AppUserObj().read(session=db_session)
    app_user_1, app_user_2 = app_users[0], app_users[1]

    result = await db_session.execute(select(TelegramUsers))
    tg_users = result.scalars().all()
    result = await db_session.execute(select(Employees))
    employees = result.scalars().all()
    result = await db_session.execute(select(Roles))
    roles = result.scalars().all()

    assert len(app_users) == 2
    assert (app_user_1.tg_user_id == tg_users[0].id and app_user_1.employee_id == employees[0].id and
            app_user_1.role_id == roles[0].id and app_user_1.is_active is False)
    assert (app_user_2.tg_user_id == tg_users[1].id and app_user_2.employee_id == employees[1].id and
            app_user_2.role_id == roles[1].id and app_user_2.is_active is True)

    # Invalid data
    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    db_error_app_users = await AppUserObj().read(session=db_session)
    assert len(db_error_app_users) == 0
    assert db_error_app_users == []


@pytest.mark.asyncio
async def test_app_user_get_obj(db_session, sample_app_users, mocker):
    result = await db_session.execute(select(AppUsers))
    app_users = result.scalars().all()
    result = await db_session.execute(select(TelegramUsers))
    tg_users = result.scalars().all()
    result = await db_session.execute(select(Employees))
    employees = result.scalars().all()
    result = await db_session.execute(select(Roles))
    roles = result.scalars().all()

    app_user_1 = await AppUserObj().get_obj(session=db_session, app_user_id=app_users[0].id)
    app_user_2 = await AppUserObj().get_obj(session=db_session, app_user_id=app_users[1].id)
    app_user_3 = await AppUserObj().get_obj(session=db_session, app_user_id=uuid7())

    assert (app_user_1.tg_user_id == tg_users[0].id and app_user_1.employee_id == employees[0].id and
            app_user_1.role_id == roles[0].id and app_user_1.is_active is False)
    assert (app_user_2.tg_user_id == tg_users[1].id and app_user_2.employee_id == employees[1].id and
            app_user_2.role_id == roles[1].id and app_user_2.is_active is True)
    assert app_user_3 is None

    # Invalid data
    invalid_app_user_1 = await AppUserObj().get_obj(session=db_session, app_user_id=None)
    assert invalid_app_user_1 is None

    invalid_app_user_2 = await AppUserObj().get_obj(session=db_session, app_user_id="")
    assert invalid_app_user_2 is None

    mocker.patch.object(db_session, 'get', side_effect=SQLAlchemyError("DB error"))
    db_error_app_user = await AppUserObj().get_obj(session=db_session, app_user_id=app_users[0].id)
    assert db_error_app_user is None


@pytest.mark.asyncio
async def test_app_user_is_registered(db_session, sample_app_users, mocker):
    result = await db_session.execute(select(TelegramUsers))
    tg_users = result.scalars().all()

    app_user_1 = await AppUserObj().is_registered(session=db_session, telegram_id=tg_users[0].telegram_id)
    app_user_2 = await AppUserObj().is_registered(session=db_session, telegram_id=tg_users[1].telegram_id)
    app_user_3 = await AppUserObj().is_registered(session=db_session, telegram_id="11111")

    assert app_user_1 is True and app_user_2 is True
    assert app_user_3 is False

    # Invalid data
    invalid_app_user_1 = await AppUserObj().is_registered(session=db_session, telegram_id=None)
    assert invalid_app_user_1 is False

    invalid_app_user_2 = await AppUserObj().is_registered(session=db_session, telegram_id="")
    assert invalid_app_user_2 is False

    invalid_app_user_3 = await AppUserObj().is_registered(session=db_session, telegram_id=12345)
    assert invalid_app_user_3 is False

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    db_error_app_user = await AppUserObj().is_registered(session=db_session, telegram_id=tg_users[0].id)
    assert db_error_app_user is False


@pytest.mark.asyncio
async def test_app_user_is_admin(db_session, sample_app_users, mocker):
    result = await db_session.execute(select(AppUsers))
    app_users = result.scalars().all()

    app_user_1 = await AppUserObj().is_admin(session=db_session, app_user_id=app_users[0].id)
    app_user_2 = await AppUserObj().is_admin(session=db_session, app_user_id=app_users[1].id)
    app_user_3 = await AppUserObj().is_admin(session=db_session, app_user_id=uuid7())

    assert app_user_1 is False
    assert app_user_2 is True
    assert app_user_3 is False

    # Invalid data
    invalid_app_user_1 = await AppUserObj().is_admin(session=db_session, app_user_id=None)
    assert invalid_app_user_1 is False

    invalid_app_user_2 = await AppUserObj().is_admin(session=db_session, app_user_id="")
    assert invalid_app_user_2 is False

    mocker.patch.object(db_session, 'get', side_effect=SQLAlchemyError("DB error"))
    db_error_app_user = await AppUserObj().is_admin(session=db_session, app_user_id=app_users[0].id)

    assert db_error_app_user is False


@pytest.mark.asyncio
async def test_app_user_get_app_user_id(db_session, sample_app_users, mocker):
    result = await db_session.execute(select(AppUsers))
    app_users = result.scalars().all()
    result = await db_session.execute(select(TelegramUsers))
    tg_users = result.scalars().all()

    app_user_1 = await AppUserObj().get_app_user_id(session=db_session, telegram_id=tg_users[0].telegram_id)
    app_user_2 = await AppUserObj().get_app_user_id(session=db_session, telegram_id=tg_users[1].telegram_id)
    app_user_3 = await AppUserObj().get_app_user_id(session=db_session, telegram_id="11111")

    assert app_user_1 == app_users[0].id
    assert app_user_2 == app_users[1].id
    assert app_user_3 is None

    # Invalid data
    invalid_app_user_1 = await AppUserObj().get_app_user_id(session=db_session, telegram_id=None)
    assert invalid_app_user_1 is None

    invalid_app_user_2 = await AppUserObj().get_app_user_id(session=db_session, telegram_id="")
    assert invalid_app_user_2 is None

    invalid_app_user_3 = await AppUserObj().get_app_user_id(session=db_session, telegram_id=12345)
    assert invalid_app_user_3 is None

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    db_error_app_user = await AppUserObj().get_app_user_id(session=db_session, telegram_id=tg_users[0].id)
    assert db_error_app_user is None


@pytest.mark.asyncio
async def test_app_user_get_employee_fullname(db_session, sample_app_users, mocker):
    result = await db_session.execute(select(AppUsers))
    app_users = result.scalars().all()
    result = await db_session.execute(select(Employees))
    employees = result.scalars().all()

    app_user_1 = await AppUserObj().get_employee_fullname(session=db_session, app_user_id=app_users[0].id)
    app_user_2 = await AppUserObj().get_employee_fullname(session=db_session, app_user_id=app_users[1].id)
    app_user_3 = await AppUserObj().get_employee_fullname(session=db_session, app_user_id=uuid7())

    assert app_user_1 == employees[0].full_name
    assert app_user_2 == employees[1].full_name
    assert app_user_3 is None

    # Invalid data
    invalid_app_user_1 = await AppUserObj().get_employee_fullname(session=db_session, app_user_id=None)
    assert invalid_app_user_1 is None

    invalid_app_user_2 = await AppUserObj().get_employee_fullname(session=db_session, app_user_id="")
    assert invalid_app_user_2 is None

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    db_error_app_user = await AppUserObj().get_employee_fullname(session=db_session, app_user_id=app_users[0].id)

    assert db_error_app_user is None


@pytest.mark.asyncio
async def test_app_user_update():
    app_user = await AppUserObj().update()
    assert app_user is None


@pytest.mark.asyncio
async def test_app_user_remove():
    app_user = await AppUserObj().remove()
    assert app_user is None
