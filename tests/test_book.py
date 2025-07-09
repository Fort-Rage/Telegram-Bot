import pytest

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from db.models import Book, Category, City, BookCategory
from db.queries.book_crud import BookObj
from db.queries.location_crud import LocationObj


@pytest.mark.asyncio
async def test_book_create(db_session, sample_users, sample_locations, mocker):
    await BookObj().create(
        title='Python',
        author='Someone',
        description='Some description',
        owner_id=12345,
        location_id=1,
        categories=[Category.DATABASES, Category.ALGORITHMS],
        session=db_session
    )

    result = await db_session.execute(select(Book))
    books = result.scalars().all()

    assert len(books) == 1
    assert books[0].title == 'Python'
    assert books[0].author == 'Someone'
    assert books[0].description == 'Some description'

    book = await BookObj().create(
        title="Book",
        author="Nobody",
        description="Fail",
        owner_id=9999,
        categories=["Fantasy"],
        location_id=1,
        session=db_session,
    )

    assert book is None

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    book_2 = await BookObj().create(
        title="Book2",
        author="Nobody2",
        description="Fail2",
        owner_id=2,
        categories=["Fantasy"],
        location_id=1,
        session=db_session,
    )

    assert book_2 is None


@pytest.mark.asyncio
async def test_book_update(db_session, sample_users, sample_locations, sample_books, mocker):
    await BookObj().update(
        book_id=1,
        session=db_session,
        updates={'title': 'Updated title',
                 'owner_id': 54321,
                 'description': 'Updated description',
                 'categories': 'Category.DATA_SCIENCE, Category.DEVOPS',
                 'location_id': 2,
                 }
    )

    updated_book = await BookObj().read(db_session)

    assert len(updated_book) == 2
    assert updated_book[1].title == 'Updated title'
    assert updated_book[1].owner_id == 54321

    mocker.patch.object(db_session, 'get', side_effect=SQLAlchemyError("DB error"))
    updated_book_2 = await BookObj().update(
        book_id=1,
        session=db_session,
        updates={'title': 132,
                 'owner_id': 54321,
                 'description': 'Updated description',
                 'categories': 'Category.COMEDY',
                 'location_id': 2,
                 }
    )

    assert updated_book_2 is None


@pytest.mark.asyncio
async def test_update_del_old_categories(db_session,  sample_users, sample_locations, sample_books):
    await BookObj().update(
        book_id=1,
        session=db_session,
        updates={
            'categories': 'DevOps, Data Science'
        }
    )

    updated = await db_session.execute(
        select(BookCategory).where(BookCategory.book_id == 1)
    )
    categories = updated.scalars().all()
    category_set = {c.category for c in categories}

    assert Category.ALGORITHMS not in category_set
    assert Category.DEVOPS in category_set
    assert Category.DATA_SCIENCE in category_set


@pytest.mark.asyncio
async def test_book_read(db_session, sample_users, sample_locations, sample_books, mocker):
    books = await BookObj().read(db_session)

    assert len(books) == 2
    assert books[0].title == 'Java'
    assert books[1].owner_id == 12345
    assert books[1].location_id == 1

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    error_books = await BookObj().read(db_session)

    assert error_books is None


@pytest.mark.asyncio
async def test_book_delete(db_session, sample_users, sample_locations, sample_books, mocker):
    await BookObj().remove(session=db_session, book_id=1)
    books = await BookObj().read(db_session)
    assert len(books) == 1

    removed_book = await BookObj().remove(session=db_session, book_id=99)
    assert removed_book is False

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))

    error_book = await BookObj().remove(session=db_session, book_id=2)
    assert error_book is False


@pytest.mark.asyncio
async def test_book_get_object(db_session, sample_users, sample_locations, sample_books, mocker):
    book1 = await BookObj().get_obj(1, db_session)
    book2 = await BookObj().get_obj(2, db_session)

    assert book1.title == 'Python'
    assert book1.owner_id == 12345
    assert book2.title == 'Java'
    assert book2.owner_id == 54321

    get_book_obj = await BookObj().get_obj(book_id=121, session=db_session)
    assert get_book_obj is None

    mocker.patch.object(db_session, 'get', side_effect=SQLAlchemyError("DB error"))
    get_error_obj = await BookObj().get_obj(book_id=1, session=db_session)
    assert get_error_obj is None


@pytest.mark.asyncio
async def test_book_get_book_categories(
        db_session,
        sample_users, sample_locations, sample_books, sample_books_categories):
    book_categories = await BookObj.get_book_categories(book_id=1, session=db_session)
    assert len(book_categories) == 2
    assert book_categories[0] == Category.DEVOPS
    assert book_categories[1] == Category.ALGORITHMS


@pytest.mark.asyncio
async def test_get_categories():
    categories = await BookObj().get_categories()
    assert len(categories) == 10
    assert categories[0] == Category.PROGRAMMING
    assert categories[-1] == Category.ALGORITHMS


@pytest.mark.asyncio
async def test_get_book_location(db_session, mocker):
    await LocationObj().create(city=City.New_York, room='33', session=db_session)
    await LocationObj().create(city=City.Tashkent, room='44', session=db_session)

    book_location_1 = await BookObj().get_book_location(loc_id=1, session=db_session)
    book_location_2 = await BookObj().get_book_location(loc_id=2, session=db_session)
    book_location_3 = await BookObj().get_book_location(loc_id=22323, session=db_session)

    assert book_location_1.city == City.New_York
    assert book_location_2.room == '44'
    assert book_location_3 is None

    mocker.patch.object(db_session, 'get', side_effect=SQLAlchemyError("DB error"))
    error_book_location = await BookObj().get_book_location(loc_id=3, session=db_session)

    assert error_book_location is None
