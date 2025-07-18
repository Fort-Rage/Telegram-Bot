import pytest

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from db.models import Employees
from db.queries.employee_crud import EmployeeObj


@pytest.mark.asyncio
async def test_employee_model(db_session, sample_employees):
    result = await db_session.execute(select(Employees))
    employees = result.scalars().all()

    employee_1 = await db_session.get(Employees, employees[0].id)
    employee_2 = await db_session.get(Employees, employees[1].id)

    assert employee_1.full_name == "User A"
    assert employee_1.email == "user_a@example.com"
    assert employee_1.is_verified is False

    assert employee_2.full_name == "Admin"
    assert employee_2.email == "admin@example.com"
    assert employee_2.is_verified is True


@pytest.mark.asyncio
async def test_employee_get_obj_by_email(db_session, sample_employees, mocker):
    employee_1 = await EmployeeObj().get_obj_by_email(session=db_session, email="user_a@example.com")
    employee_2 = await EmployeeObj().get_obj_by_email(session=db_session, email="admin@example.com")
    employee_3 = await EmployeeObj().get_obj_by_email(session=db_session, email="librarian@example.com")

    assert employee_1.full_name == "User A"
    assert employee_2.full_name == "Admin"
    assert employee_3 is None

    # Invalid data
    invalid_employee_1 = await EmployeeObj().get_obj_by_email(session=db_session, email=None)
    assert invalid_employee_1 is None

    invalid_employee_2 = await EmployeeObj().get_obj_by_email(session=db_session, email="")
    assert invalid_employee_2 is None

    invalid_employee_3 = await EmployeeObj().get_obj_by_email(session=db_session, email=12345)
    assert invalid_employee_3 is None

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    db_error_employee = await EmployeeObj().get_obj_by_email(session=db_session, email="admin@example.com")
    assert db_error_employee is None
