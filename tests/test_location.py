import pytest
from aiogram.types import BufferedInputFile

from io import BytesIO
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from uuid6 import uuid7

from db.models import City, Location
from db.queries.location_crud import LocationObj


@pytest.mark.asyncio
async def test_location_model(db_session, sample_locations):
    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()
    location_1, location_2 = locations[0], locations[1]

    assert len(locations) == 2
    assert location_1.city == "Almaty" and location_1.room == "Room 22"
    assert location_2.city == "Berlin" and location_2.room == "Room 33"


@pytest.mark.asyncio
async def test_location_create(db_session, mocker):
    await LocationObj().create(session=db_session, city=City.Sofia, room="Room 12")
    location_2 = await LocationObj().create(session=db_session, city=City.Bishkek, room="Room 13")
    location_3 = await LocationObj().create(session=db_session, city="not_existing_city", room="Room 14")

    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()
    location_1 = locations[0]

    assert len(locations) == 2
    assert location_1.city == "Sofia" and location_1.room == "Room 12"
    assert location_2 is True
    assert location_3 is False

    # Invalid data
    invalid_location_1 = await LocationObj().create(session=db_session, city=None, room="Room 12")
    assert invalid_location_1 is False
    invalid_location_1 = await LocationObj().create(session=db_session, city="", room="Room 12")
    assert invalid_location_1 is False
    invalid_location_1 = await LocationObj().create(session=db_session, city=12345, room="Room 12")
    assert invalid_location_1 is False

    invalid_location_2 = await LocationObj().create(session=db_session, city=City.Almaty, room=None)
    assert invalid_location_2 is False
    invalid_location_2 = await LocationObj().create(session=db_session, city=City.Almaty, room="")
    assert invalid_location_2 is False
    invalid_location_2 = await LocationObj().create(session=db_session, city=City.Almaty, room=12345)
    assert invalid_location_2 is False

    mocker.patch.object(db_session, 'add', side_effect=SQLAlchemyError("DB error"))
    db_error_location = await LocationObj().create(city=City.Almaty, room="Room 12", session=db_session)
    assert db_error_location is False


@pytest.mark.asyncio
async def test_location_read(db_session, sample_locations, mocker):
    locations = await LocationObj().read(db_session)
    location_1, location_2 = locations[0], locations[1]

    assert len(locations) == 2
    assert location_1.city == "Almaty" and location_1.room == "Room 22"
    assert location_2.city == "Berlin" and location_2.room == "Room 33"

    # Invalid data
    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    db_error_locations = await LocationObj().read(db_session)
    assert len(db_error_locations) == 0


@pytest.mark.asyncio
async def test_location_update(db_session, sample_locations, mocker):
    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()
    location_1_id, location_2_id = locations[0].id, locations[1].id

    location_1 = await LocationObj().update(session=db_session, location_id=location_1_id,
                                            city=City.London, room="Room 2222")
    location_2 = await LocationObj().update(session=db_session, location_id=location_2_id,
                                            city=City.New_York, room="Room 3333")
    location_3 = await LocationObj().update(session=db_session, location_id=uuid7(), city=City.Almaty, room="Room 12")

    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()
    location_4, location_5 = locations[0], locations[1]

    assert len(locations) == 2
    assert location_1 is True and location_2 is True and location_3 is False
    assert location_4.city == "London" and location_4.room == "Room 2222"
    assert location_5.city == "New York" and location_5.room == "Room 3333"

    # Invalid data
    invalid_location_1 = await LocationObj().update(session=db_session, location_id=None,
                                                    city=City.Almaty, room="Room 12")
    assert invalid_location_1 is False
    invalid_location_1 = await LocationObj().update(session=db_session, location_id="",
                                                    city=City.Almaty, room="Room 12")
    assert invalid_location_1 is False

    invalid_location_2 = await LocationObj().update(session=db_session, location_id=location_1_id,
                                                    city=None, room="Room 12")
    assert invalid_location_2 is False
    invalid_location_2 = await LocationObj().update(session=db_session, location_id=location_1_id,
                                                    city="", room="Room 12")
    assert invalid_location_2 is False
    invalid_location_2 = await LocationObj().update(session=db_session, location_id=location_1_id,
                                                    city=12345, room="Room 12")
    assert invalid_location_2 is False

    invalid_location_3 = await LocationObj().update(session=db_session, location_id=location_1_id,
                                                    city=City.Almaty, room=None)
    assert invalid_location_3 is False
    invalid_location_3 = await LocationObj().update(session=db_session, location_id=location_1_id,
                                                    city=City.Almaty, room="")
    assert invalid_location_3 is False
    invalid_location_3 = await LocationObj().update(session=db_session, location_id=location_1_id,
                                                    city=City.Almaty, room=12345)
    assert invalid_location_3 is False

    mocker.patch.object(db_session, 'commit', side_effect=SQLAlchemyError("DB error"))
    db_error_location = await LocationObj().update(session=db_session, location_id=location_1_id,
                                                   city=City.Almaty, room="Room 12")
    assert db_error_location is False


@pytest.mark.asyncio
async def test_location_remove(db_session, sample_locations, mocker):
    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()
    location_1_id, location_2_id = locations[0].id, locations[0].id

    location_1 = await LocationObj().remove(session=db_session, location_id=location_1_id)
    location_2 = await LocationObj().remove(session=db_session, location_id=uuid7())

    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()

    assert len(locations) == 1
    assert location_1 is True
    assert location_2 is False

    # Invalid data
    invalid_location_1 = await LocationObj().remove(session=db_session, location_id=None)
    assert invalid_location_1 is False

    invalid_location_2 = await LocationObj().remove(session=db_session, location_id="")
    assert invalid_location_2 is False

    mocker.patch.object(db_session, 'delete', side_effect=SQLAlchemyError("DB error"))
    db_error_location = await LocationObj().remove(session=db_session, location_id=location_2_id)
    assert db_error_location is False


@pytest.mark.asyncio
async def test_location_get_obj(db_session, sample_locations, mocker):
    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()

    location_1 = await LocationObj().get_obj(session=db_session, location_id=locations[0].id)
    location_2 = await LocationObj().get_obj(session=db_session, location_id=locations[1].id)
    location_3 = await LocationObj().get_obj(session=db_session, location_id=uuid7())

    assert location_1.city == "Almaty" and location_1.room == "Room 22"
    assert location_2.city == "Berlin" and location_2.room == "Room 33"
    assert location_3 is None

    # Invalid data
    invalid_location_1 = await LocationObj().get_obj(session=db_session, location_id=None)
    assert invalid_location_1 is None

    invalid_location_2 = await LocationObj().get_obj(session=db_session, location_id="")
    assert invalid_location_2 is None

    mocker.patch.object(db_session, 'get', side_effect=SQLAlchemyError("DB error"))
    db_error_location = await LocationObj().get_obj(session=db_session, location_id=locations[0].id)
    assert db_error_location is None


@pytest.mark.asyncio
async def test_location_get_location_id(db_session, sample_locations, mocker):
    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()

    location_1 = await LocationObj().get_location_id(session=db_session, city=City.Almaty, room="Room 22")
    location_2 = await LocationObj().get_location_id(session=db_session, city=City.Berlin, room="Room 33")
    location_3 = await LocationObj().get_location_id(session=db_session, city="not_existing_city", room="Room 33")
    location_4 = await LocationObj().get_location_id(session=db_session, city=City.Almaty, room="not_existing_room")

    assert location_1 != location_2
    assert location_1 == locations[0].id
    assert location_2 == locations[1].id
    assert location_3 is None and location_4 is None

    # Invalid data
    invalid_location_1 = await LocationObj().get_location_id(session=db_session, city=None, room="Room 12")
    assert invalid_location_1 is None
    invalid_location_1 = await LocationObj().get_location_id(session=db_session, city="", room="Room 12")
    assert invalid_location_1 is None

    invalid_location_2 = await LocationObj().get_location_id(session=db_session, city=City.Almaty, room=None)
    assert invalid_location_2 is None
    invalid_location_2 = await LocationObj().get_location_id(session=db_session, city=City.Almaty, room="")
    assert invalid_location_2 is None

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    db_error_location = await LocationObj().get_location_id(session=db_session, city=City.Almaty, room="Room 12")
    assert db_error_location is None


@pytest.mark.asyncio
async def test_location_get_cities():
    result = await LocationObj().get_cities()

    assert len(result) == 18
    assert result[0] == City.Almaty
    assert result[17] == City.Wroclaw


@pytest.mark.asyncio
async def test_location_get_location_qr_code(db_session):
    await LocationObj().create(session=db_session, city=City.Almaty, room="Room 12")
    await LocationObj().create(session=db_session, city=City.Berlin, room="Room 22")
    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()

    location_1 = await LocationObj().get_location_qr_code(session=db_session, location_id=locations[0].id)
    location_2 = await LocationObj().get_location_qr_code(session=db_session, location_id=locations[1].id)

    assert isinstance(location_1, BufferedInputFile)
    assert location_1.filename == "qr.png"
    assert location_1.data == locations[0].qr_code

    assert isinstance(location_2, BufferedInputFile)
    assert location_2.filename == "qr.png"
    assert location_2.data == locations[1].qr_code
