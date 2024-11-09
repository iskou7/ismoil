from aiogram.dispatcher.filters.state import State,StatesGroup

class IshJoyiState(StatesGroup):
    yosh = State()
    texnologiya = State()
    aloqa = State()
    hudud = State()
    narxi = State()
    kasb  = State()
    murojat_qilish_vaqti = State()
    maqsad = State()
   
from aiogram.types import ReplyKeyboardMarkup,KeyboardButton


main_button_mrk  = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2,one_time_keyboard=True)

btn1 = KeyboardButton(text='Sherik kerak ')
btn2 = KeyboardButton(text='Ish joy kerak ')
btn3 = KeyboardButton(text='Hodim kerak ')
btn4 = KeyboardButton(text='Ustoz kerak ')
btn5 = KeyboardButton(text='Shogird kerak ')

main_button_mrk.add(btn1,btn2,btn3,btn4,btn5)

























