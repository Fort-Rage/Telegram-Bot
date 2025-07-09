import pytest

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from db.models import WishList
from db.queries.wishlist_crud import WishlistObj


@pytest.mark.asyncio
async def test_wish_create(db_session, sample_users):
    wl = await WishlistObj().create(
        session=db_session,
        user_id=12345,
        book_title="Title",
        author="Author",
        comment="Good!"
    )

    error_wl = await WishlistObj().create(
        session=db_session,
        user_id=543212,
        book_title="Title",
        author="Author",
        comment="Error"
    )

    result = await db_session.execute(select(WishList).where(WishList.wish_list_id == 1))
    wish_list = result.scalar_one()

    assert wl is True
    assert error_wl is False
    assert wish_list.user_id == 12345
    assert wish_list.book_title == "Title"
    assert wish_list.author == "Author"
    assert wish_list.comment == "Good!"


@pytest.mark.asyncio
async def test_wish_get_obj(db_session, sample_users, sample_wishlists, mocker):
    wish_1 = await WishlistObj().get_obj(session=db_session, wish_id=1)

    assert wish_1.user_id == 12345
    assert wish_1.book_title == "Title"
    assert wish_1.author == "Author"
    assert wish_1.comment == "Good!"

    wish_2 = await WishlistObj().get_obj(session=db_session, wish_id=2)

    assert wish_2.user_id == 54321
    assert wish_2.book_title == "No Title"
    assert wish_2.author == "No Author"
    assert wish_2.comment == "Bad!"

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    wish_3 = await WishlistObj().get_obj(session=db_session, wish_id=3)

    assert wish_3 is None


@pytest.mark.asyncio
async def test_wish_read(db_session, sample_users, sample_wishlists, mocker):
    result = await WishlistObj().read(session=db_session, user_id=12345)
    wish_1 = result[0]

    assert len(result) == 1
    assert wish_1.book_title == "Title"
    assert wish_1.author == "Author"

    result = await WishlistObj().read(session=db_session, user_id=54321)

    assert len(result) == 1
    assert result[0].comment == "Bad!"

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    wish_3 = await WishlistObj().read(session=db_session, user_id=54321)

    assert wish_3 == []


@pytest.mark.asyncio
async def test_wish_remove(db_session, sample_users, sample_wishlists, mocker):
    removed_wishlist = await WishlistObj().remove(session=db_session, wish_id=1)
    await db_session.get(WishList, 1)
    wishlist_false = await WishlistObj().remove(session=db_session, wish_id=3)

    assert removed_wishlist is True
    assert wishlist_false is False

    mocker.patch.object(db_session, 'delete', side_effect=SQLAlchemyError("DB error"))
    wishlist_false_2 = await WishlistObj().remove(session=db_session, wish_id=1)

    assert wishlist_false_2 is False


@pytest.mark.asyncio
async def test_wish_update(db_session, sample_users, sample_wishlists, mocker):
    wish_true = await WishlistObj().update(session=db_session, field="book_title", wish_id=1, new_value="Upd Title")
    wish_false = await WishlistObj().update(session=db_session, field="book_title", wish_id=5, new_value="Upd Title")

    await WishlistObj().update(session=db_session, field="author", wish_id=1, new_value="Upd Author")
    await WishlistObj().update(session=db_session, field="comment", wish_id=1, new_value="Bad!")

    result = await db_session.execute(select(WishList).where(WishList.user_id == 12345))
    wish = result.scalars().first()

    assert wish_true is True
    assert wish_false is False
    assert wish.book_title == "Upd Title"
    assert wish.author == "Upd Author"
    assert wish.comment == "Bad!"

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    wish_error = await WishlistObj().update(session=db_session, field="book_title", wish_id=1, new_value="Upd Title")

    assert wish_error is False
