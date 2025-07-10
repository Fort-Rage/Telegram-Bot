import pytest

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from db.models import City, Location
from db.queries.location_crud import LocationObj


@pytest.mark.asyncio
async def test_location_model(db_session, sample_locations):
    result = await db_session.execute(select(Location))
    saved_locations = result.scalars().all()

    assert len(saved_locations) == 2
    assert {loc.city for loc in saved_locations} == {City.Almaty, City.Berlin}


@pytest.mark.asyncio
async def test_location_create(db_session, mocker):
    await LocationObj().create(city=City.Sofia, room="Room 12", session=db_session)
    await LocationObj().create(city=City.Bishkek, room="Room 13", session=db_session)
    await LocationObj().create(city=City.Krakow, room="Room 14", session=db_session)

    result = await db_session.execute(select(Location))
    locations = result.scalars().all()

    assert len(locations) == 3
    assert {loc.city for loc in locations} == {City.Sofia, City.Bishkek, City.Krakow}
    assert {loc.room for loc in locations} == {'Room 12', 'Room 13', 'Room 14'}

    error_city = await LocationObj().create(city='Astana', room="Room 224", session=db_session)
    assert error_city is False

    mocker.patch.object(db_session, 'add', side_effect=SQLAlchemyError("DB error"))
    error_location = await LocationObj().create(city=City.Sofia, room="Room 224", session=db_session)

    assert error_location is None


@pytest.mark.asyncio
async def test_location_update(db_session, sample_locations, mocker):
    loc_id_1 = await LocationObj.get_location_id(city=City.Almaty, room="Room 22", session=db_session)
    loc_id_2 = await LocationObj.get_location_id(city=City.Berlin, room="Room 33", session=db_session)

    await LocationObj().update(location_id=loc_id_1, session=db_session, city=City.London, room="Room 2222")
    await LocationObj().update(location_id=loc_id_2, session=db_session, city=City.New_York, room="Room 3333")

    result = await db_session.execute(select(Location))
    locations = result.scalars().all()

    assert len(locations) == 2
    assert {loc.city for loc in locations} == {City.London, City.New_York}
    assert {loc.room for loc in locations} == {'Room 2222', 'Room 3333'}

    error_loc = await LocationObj().update(location_id=4, session=db_session, city=City.London, room="Room 333")
    assert error_loc is None

    mocker.patch.object(db_session, 'commit', side_effect=SQLAlchemyError("DB error"))
    error_loc2 = await LocationObj().update(location_id=1, session=db_session, city=City.Almaty, room="Room 344")

    assert error_loc2 is None


@pytest.mark.asyncio
async def test_location_delete(db_session, sample_locations, mocker):
    result = await db_session.execute(select(Location))
    locations_before = result.scalars().all()
    assert len(locations_before) == 2

    loc_id_1 = await LocationObj.get_location_id(city=City.Almaty, room="Room 22", session=db_session)
    await LocationObj().remove(location_id=loc_id_1, session=db_session)

    result = await db_session.execute(select(Location))
    locations = result.scalars().all()
    assert len(locations) == 1

    error_loc = await LocationObj().remove(location_id=3, session=db_session)
    assert error_loc is False

    mocker.patch.object(db_session, 'delete', side_effect=SQLAlchemyError("DB error"))
    error_delete = await LocationObj().remove(location_id=2, session=db_session)
    assert error_delete is None


@pytest.mark.asyncio
async def test_location_read(db_session, sample_locations, mocker):
    result = await LocationObj().read(db_session)

    assert len(result) == 2
    assert result[0].city == City.Almaty
    assert result[1].room == "Room 33"

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    result = await LocationObj().read(db_session)

    assert result is None


@pytest.mark.asyncio
async def test_location_get_object(db_session, sample_locations, mocker):
    location1 = await LocationObj().get_obj(1, db_session)
    location2 = await LocationObj().get_obj(2, db_session)
    location3 = await LocationObj().get_obj(3, db_session)

    assert location1 == "Room 22"
    assert location2 == "Room 33"
    assert location3 is None

    mocker.patch.object(db_session, 'get', side_effect=SQLAlchemyError("DB error"))
    location4 = await LocationObj().get_obj(1, db_session)

    assert location4 is None


@pytest.mark.asyncio
async def test_location_get_id(db_session, sample_locations, mocker):
    loc_id_1 = await LocationObj().get_location_id(city=City.Almaty, room="Room 22", session=db_session)
    loc_id_2 = await LocationObj().get_location_id(city=City.Berlin, room="Room 33", session=db_session)

    assert loc_id_1 != loc_id_2
    assert loc_id_1 == 1
    assert loc_id_2 == 2

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    loc_id_3 = await LocationObj().get_location_id(city=City.Berlin, room="Room 33", session=db_session)

    assert loc_id_3 is None


@pytest.mark.asyncio
async def test_location_get_cities():
    result = await LocationObj().get_cities()

    assert len(result) == 18
    assert result[0] == City.Almaty
    assert result[17] == City.Wroclaw
