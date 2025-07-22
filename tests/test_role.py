import pytest

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from uuid6 import uuid7

from db.models import Roles
from db.queries.role_crud import RoleObj


@pytest.mark.asyncio
async def test_role_model(db_session, sample_roles):
    result = await db_session.execute(select(Roles).order_by(Roles.id))
    roles = result.scalars().all()
    role_1, role_2 = roles[0], roles[1]

    assert role_1.name == "User"
    assert role_1.description == "Default user role"

    assert role_2.name == "Admin"
    assert role_2.description == "Administrator role"


@pytest.mark.asyncio
async def test_role_get_obj(db_session, sample_roles, mocker):
    result = await db_session.execute(select(Roles).order_by(Roles.id))
    roles = result.scalars().all()

    role_1 = await RoleObj().get_obj(session=db_session, role_id=roles[0].id)
    role_2 = await RoleObj().get_obj(session=db_session, role_id=roles[1].id)
    role_3 = await RoleObj().get_obj(session=db_session, role_id=uuid7())

    assert role_1.name == "User"
    assert role_2.name == "Admin"
    assert role_3 is None

    # Invalid data
    invalid_role_1 = await RoleObj().get_obj(session=db_session, role_id=None)
    assert invalid_role_1 is None

    invalid_role_2 = await RoleObj().get_obj(session=db_session, role_id="")
    assert invalid_role_2 is None

    invalid_role_3 = await RoleObj().get_obj(session=db_session, role_id=12345)
    assert invalid_role_3 is None

    mocker.patch.object(db_session, 'get', side_effect=SQLAlchemyError("DB error"))
    db_error_role = await RoleObj().get_obj(session=db_session, role_id=roles[0].id)
    assert db_error_role is None


@pytest.mark.asyncio
async def test_role_get_obj_by_name(db_session, sample_roles, mocker):
    result = await db_session.execute(select(Roles).order_by(Roles.id))
    roles = result.scalars().all()

    role_1 = await RoleObj().get_obj_by_name(session=db_session, name="User")
    role_2 = await RoleObj().get_obj_by_name(session=db_session, name="Admin")
    role_3 = await RoleObj().get_obj_by_name(session=db_session, name="Librarian")

    assert role_1.id == roles[0].id
    assert role_1.description == "Default user role"
    assert role_2.id == roles[1].id
    assert role_2.description == "Administrator role"
    assert role_3 is None

    # Invalid data
    invalid_role_1 = await RoleObj().get_obj_by_name(session=db_session, name=None)
    assert invalid_role_1 is None

    invalid_role_2 = await RoleObj().get_obj_by_name(session=db_session, name="")
    assert invalid_role_2 is None

    invalid_role_3 = await RoleObj().get_obj_by_name(session=db_session, name=12345)
    assert invalid_role_3 is None

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    db_error_role = await RoleObj().get_obj_by_name(session=db_session, name="Admin")
    assert db_error_role is None


@pytest.mark.asyncio
async def test_role_create():
    role = await RoleObj().create()
    assert role is None


@pytest.mark.asyncio
async def test_role_read():
    role = await RoleObj().read()
    assert role is None


@pytest.mark.asyncio
async def test_role_update():
    role = await RoleObj().update()
    assert role is None


@pytest.mark.asyncio
async def test_role_remove():
    role = await RoleObj().remove()
    assert role is None
