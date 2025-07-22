import pytest

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from uuid6 import uuid7

from db.models import WishList, AppUsers
from db.queries.wishlist_crud import WishlistObj


@pytest.mark.asyncio
async def test_wishlist_model(db_session, sample_wishlists):
    result = await db_session.execute(select(WishList).order_by(WishList.id))
    wishlists = result.scalars().all()
    result = await db_session.execute(select(AppUsers))
    app_users = result.scalars().all()

    wishlist_1 = await db_session.get(WishList, wishlists[0].id)
    wishlist_2 = await db_session.get(WishList, wishlists[1].id)

    assert wishlist_1.app_user_id == app_users[0].id
    assert wishlist_1.book_title == "Title"
    assert wishlist_1.author == "Author"
    assert wishlist_1.comment == "Good!"

    assert wishlist_2.app_user_id == app_users[0].id
    assert wishlist_2.book_title == "No Title"
    assert wishlist_2.author == "No Author"
    assert wishlist_2.comment is None


@pytest.mark.asyncio
async def test_wishlist_create(db_session, sample_app_users):
    result = await db_session.execute(select(AppUsers).order_by(AppUsers.id))
    app_users = result.scalars().all()
    app_user_id = app_users[0].id

    await WishlistObj().create(session=db_session, app_user_id=app_user_id,
                               book_title="Title", author="Author", comment="Good!")

    wishlist_2 = await WishlistObj().create(session=db_session, app_user_id=app_user_id,
                                            book_title="No Title", author="No Author")

    wishlist_3 = await WishlistObj().create(session=db_session, app_user_id=app_user_id,
                                            book_title="No Title", author="No Author", comment=None)

    wishlist_4 = await WishlistObj().create(session=db_session, app_user_id=uuid7(),
                                            book_title="Title", author="Author", comment="Good!")

    result = await db_session.execute(select(WishList).order_by(WishList.id))
    wishlists = result.scalars().all()
    print(wishlists)
    wishlist_1 = wishlists[0]

    assert len(wishlists) == 3
    assert wishlist_1.app_user_id == app_user_id
    assert wishlist_1.book_title == "Title" and wishlist_1.author == "Author" and wishlist_1.comment == "Good!"
    assert wishlist_2 is True
    assert wishlist_3 is True
    assert wishlist_4 is False


@pytest.mark.asyncio
async def test_wishlist_create_invalid(db_session, sample_app_users, mocker):
    result = await db_session.execute(select(AppUsers).order_by(AppUsers.id))
    app_users = result.scalars().all()
    app_user_id = app_users[0].id

    # Invalid data
    invalid_wishlist_1 = await WishlistObj().create(session=db_session, app_user_id=None,
                                                    book_title="Title", author="Author", comment="Good!")
    assert invalid_wishlist_1 is False
    invalid_wishlist_1 = await WishlistObj().create(session=db_session, app_user_id="",
                                                    book_title="Title", author="Author", comment="Good!")
    assert invalid_wishlist_1 is False

    invalid_wishlist_2 = await WishlistObj().create(session=db_session, app_user_id=app_user_id,
                                                    book_title=None, author="Author", comment="Good!")
    assert invalid_wishlist_2 is False
    invalid_wishlist_2 = await WishlistObj().create(session=db_session, app_user_id=app_user_id,
                                                    book_title="", author="Author", comment="Good!")
    assert invalid_wishlist_2 is False
    invalid_wishlist_2 = await WishlistObj().create(session=db_session, app_user_id=app_user_id,
                                                    book_title=12345, author="Author", comment="Good!")
    assert invalid_wishlist_2 is False

    invalid_wishlist_3 = await WishlistObj().create(session=db_session, app_user_id=app_user_id,
                                                    book_title="Title", author=None, comment="Good!")
    assert invalid_wishlist_3 is False
    invalid_wishlist_3 = await WishlistObj().create(session=db_session, app_user_id=app_user_id,
                                                    book_title="Title", author="", comment="Good!")
    assert invalid_wishlist_3 is False
    invalid_wishlist_3 = await WishlistObj().create(session=db_session, app_user_id=app_user_id,
                                                    book_title="Title", author=12345, comment="Good!")
    assert invalid_wishlist_3 is False

    invalid_wishlist_4 = await WishlistObj().create(session=db_session, app_user_id=app_user_id,
                                                    book_title="Title", author="Author", comment=12345)
    assert invalid_wishlist_4 is False

    mocker.patch.object(db_session, 'add', side_effect=SQLAlchemyError("DB error"))
    db_error_wishlist = await WishlistObj().create(session=db_session, app_user_id=app_user_id,
                                                   book_title="Title", author="Author", comment="Good!")
    assert db_error_wishlist is False


@pytest.mark.asyncio
async def test_wishlist_read(db_session, sample_app_users, sample_wishlists, mocker):
    result = await db_session.execute(select(AppUsers).order_by(AppUsers.id))
    app_users = result.scalars().all()

    wishlists_1 = await WishlistObj().read(session=db_session, app_user_id=app_users[0].id)
    wishlist_1, wishlist_2 = wishlists_1[0], wishlists_1[1]

    wishlists_2 = await WishlistObj().read(session=db_session, app_user_id=app_users[1].id)
    wishlists_3 = await WishlistObj().read(session=db_session, app_user_id=uuid7())

    assert len(wishlists_1) == 2 and len(wishlists_2) == 2 and len(wishlists_3) == 0
    assert wishlist_1.app_user_id == app_users[0].id
    assert wishlist_1.book_title == "Title" and wishlist_1.author == "Author" and wishlist_1.comment == "Good!"
    assert wishlist_2.app_user_id == app_users[0].id
    assert wishlist_2.book_title == "No Title" and wishlist_2.author == "No Author" and wishlist_2.comment is None

    # Invalid data
    invalid_wishlists_1 = await WishlistObj().read(session=db_session, app_user_id=None)
    assert len(invalid_wishlists_1) == 0

    invalid_wishlists_2 = await WishlistObj().read(session=db_session, app_user_id="")
    assert len(invalid_wishlists_2) == 0

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    db_error_wishlists = await WishlistObj().read(session=db_session, app_user_id=app_users[0].id)
    assert len(db_error_wishlists) == 0


@pytest.mark.asyncio
async def test_wishlist_update(db_session, sample_wishlists, mocker):
    result = await db_session.execute(select(WishList).order_by(WishList.id))
    wishlists = result.scalars().all()
    wishlist_1_id, wishlist_2_id = wishlists[0].id, wishlists[1].id

    wishlist_1 = await WishlistObj().update(session=db_session, field="book_title",
                                            wish_id=wishlist_1_id, new_value="New Title")
    wishlist_2 = await WishlistObj().update(session=db_session, field="book_title",
                                            wish_id=uuid7(), new_value="New Title")
    wishlist_3 = await WishlistObj().update(session=db_session, field="not_existing_field",
                                            wish_id=wishlist_1_id, new_value="New Value")
    await WishlistObj().update(session=db_session, field="author", wish_id=wishlist_2_id, new_value="New Author")
    await WishlistObj().update(session=db_session, field="comment", wish_id=wishlist_2_id, new_value="Bad!")

    result = await db_session.execute(select(WishList).order_by(WishList.id))
    wishlists = result.scalars().all()
    wishlist_4, wishlist_5 = wishlists[0], wishlists[1]

    assert wishlist_1 is True
    assert wishlist_2 is False
    assert wishlist_3 is False
    assert wishlist_4.book_title == "New Title"
    assert wishlist_5.author == "New Author"
    assert wishlist_5.comment == "Bad!"

    # Invalid data
    invalid_wishlist_1 = await WishlistObj().update(session=db_session, field=None,
                                                    wish_id=wishlist_1_id, new_value="New Value")
    assert invalid_wishlist_1 is False
    invalid_wishlist_1 = await WishlistObj().update(session=db_session, field="",
                                                    wish_id=wishlist_1_id, new_value="New Value")
    assert invalid_wishlist_1 is False
    invalid_wishlist_1 = await WishlistObj().update(session=db_session, field=12345,
                                                    wish_id=wishlist_1_id, new_value="New Value")
    assert invalid_wishlist_1 is False

    invalid_wishlist_2 = await WishlistObj().update(session=db_session, field="book_title",
                                                    wish_id=None, new_value="New Title")
    assert invalid_wishlist_2 is False
    invalid_wishlist_2 = await WishlistObj().update(session=db_session, field="book_title",
                                                    wish_id="", new_value="New Title")
    assert invalid_wishlist_2 is False
    invalid_wishlist_2 = await WishlistObj().update(session=db_session, field="book_title",
                                                    wish_id=uuid7(), new_value="New Title")
    assert invalid_wishlist_2 is False

    invalid_wishlist_3 = await WishlistObj().update(session=db_session, field="book_title",
                                                    wish_id=wishlist_1_id, new_value=None)
    assert invalid_wishlist_3 is False
    invalid_wishlist_3 = await WishlistObj().update(session=db_session, field="book_title",
                                                    wish_id=wishlist_1_id, new_value="")
    assert invalid_wishlist_3 is False
    invalid_wishlist_3 = await WishlistObj().update(session=db_session, field="book_title",
                                                    wish_id=wishlist_1_id, new_value=12345)
    assert invalid_wishlist_3 is False

    mocker.patch.object(db_session, 'commit', side_effect=SQLAlchemyError("DB error"))
    db_error_wishlist = await WishlistObj().update(session=db_session, field="book_title",
                                                   wish_id=wishlist_1_id, new_value="New Title")
    assert db_error_wishlist is False


@pytest.mark.asyncio
async def test_wish_remove(db_session, sample_wishlists, mocker):
    result = await db_session.execute(select(WishList).order_by(WishList.id))
    wishlists = result.scalars().all()
    wishlist_1_id = wishlists[0].id

    wishlist_1 = await WishlistObj().remove(session=db_session, wish_id=wishlist_1_id)
    wishlist_2 = await WishlistObj().remove(session=db_session, wish_id=uuid7())

    assert wishlist_1 is True
    assert wishlist_2 is False

    # Invalid data
    invalid_wishlist_1 = await WishlistObj().remove(session=db_session, wish_id=None)
    assert invalid_wishlist_1 is False

    invalid_wishlist_2 = await WishlistObj().remove(session=db_session, wish_id="")
    assert invalid_wishlist_2 is False

    mocker.patch.object(db_session, 'delete', side_effect=SQLAlchemyError("DB error"))
    db_error_wishlist = await WishlistObj().remove(session=db_session, wish_id=wishlist_1_id)
    assert db_error_wishlist is False


@pytest.mark.asyncio
async def test_wish_get_obj(db_session, sample_app_users, sample_wishlists, mocker):
    result = await db_session.execute(select(AppUsers).order_by(AppUsers.id))
    app_users = result.scalars().all()
    result = await db_session.execute(select(WishList).order_by(WishList.id))
    wishlists = result.scalars().all()

    wishlist_1 = await WishlistObj().get_obj(session=db_session, wish_id=wishlists[0].id)
    wishlist_2 = await WishlistObj().get_obj(session=db_session, wish_id=wishlists[1].id)
    wishlist_3 = await WishlistObj().get_obj(session=db_session, wish_id=uuid7())

    assert wishlist_1.app_user_id == app_users[0].id
    assert wishlist_1.book_title == "Title" and wishlist_1.author == "Author" and wishlist_1.comment == "Good!"
    assert wishlist_2.app_user_id == app_users[0].id
    assert wishlist_2.book_title == "No Title" and wishlist_2.author == "No Author" and wishlist_2.comment is None

    assert wishlist_3 is None

    # Invalid data
    invalid_wishlist_1 = await WishlistObj().get_obj(session=db_session, wish_id=None)
    assert invalid_wishlist_1 is None

    invalid_wishlist_2 = await WishlistObj().get_obj(session=db_session, wish_id="")
    assert invalid_wishlist_2 is None

    mocker.patch.object(db_session, 'get', side_effect=SQLAlchemyError("DB error"))
    db_error_wishlist = await WishlistObj().get_obj(session=db_session, wish_id=wishlists[0].id)
    assert db_error_wishlist is None
