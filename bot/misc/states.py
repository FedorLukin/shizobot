from aiogram.fsm.state import State, StatesGroup


class RegistrationSteps(StatesGroup):
    start = State()
    age_request = State()
    gender_request = State()
    interest_request = State()
    location_request = State()
    name_request = State()
    description_request = State()
    media_request = State()
    media_confirmation = State()
    anket_confirmation = State()


class MainStates(StatesGroup):
    edit_anket_or_start = State()
    option_selection = State()
    search = State()
    message_request = State()
    likes_answer = State()
    anket_state_switch = State()
    inactive = State()
    subscription_check = State()
    description_edit = State()


class AdminPanelStates(StatesGroup):
    message_request = State()
    notification_start = State()