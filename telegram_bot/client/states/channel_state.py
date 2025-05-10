from aiogram.fsm.state import StatesGroup, State

class RegState(StatesGroup):
    current_channel = State()
    last_save_time = State()