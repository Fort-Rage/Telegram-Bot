from aiogram.fsm.state import StatesGroup, State


class Reg(StatesGroup):
    email = State()
    code = State()


class Wish(StatesGroup):
    book_title = State()
    author = State()
    comment = State()


class WishUpdBookTitle(StatesGroup):
    book_title = State()


class WishUpdAuthor(StatesGroup):
    author = State()


class WishUpdComment(StatesGroup):
    comment = State()


class LocationForm(StatesGroup):
    add_location_city = State()
    add_location_room = State()
    waiting_for_confirmation = State()
    update_location_id = State()
    update_location_name = State()
    remove_location_id = State()
    update_location_city = State()


class Books(StatesGroup):
    author = State()
    description = State()
    categories = State()
    waiting_for_confirmation = State()
    location = State()
    owner = State()
    select_categories = State()
    save_book = State()
    delete_book = State()


class BookUpdate(StatesGroup):
    title = State()
    author = State()
    description = State()
    category = State()
    location = State()
    save_book = State()
    owner = State()
