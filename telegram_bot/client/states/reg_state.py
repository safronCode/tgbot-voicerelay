from aiogram.fsm.state import StatesGroup, State

class RegState(StatesGroup):
    name = State()
    email = State()