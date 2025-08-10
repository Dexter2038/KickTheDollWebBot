from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    Main = State()
    History = State()
    Users = State()
    Referrals = State()
    Balances = State()
    Tech = State()
    EditMoneyBalance = State()
    EditDollarBalance = State()
    CreateLottery = State()
    ChangeLotteryDate = State()
    LotteryHistory = State()
    ChangeMoneyBalance = State()
    ChangeDollarBalance = State()
    MoveTechWorks = State()
