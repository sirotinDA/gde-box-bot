from aiogram.dispatcher.filters.state import State, StatesGroup

class AddBox(StatesGroup):
    waiting_for_photo = State()
    waiting_for_description = State()
    waiting_for_location = State()

class SearchState(StatesGroup):
    waiting_for_keyword = State()

class AddItemToBox(StatesGroup):
    waiting_for_text = State()

class AddItemFromMenu(StatesGroup):
    waiting_for_location = State()
    waiting_for_box = State()
    waiting_for_item_text = State()
