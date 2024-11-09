from aiogram import Bot,Dispatcher,types,executor
from default import Ustoz_shogirt_Default
import logging

from state import IshJoyiState
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

API_TOKEN='6979098008:AAEU0F7Fb9Dyirs_mD5BpcZivjTjNYkF3GU'



bot = Bot(token=API_TOKEN,parse_mode='HTML')
xotira = MemoryStorage()
dp = Dispatcher(bot=bot,storage=xotira)

@dp.message_handler(commands='start')
async def start_handler(message: types.Message):
    await message.answer(text=f'''<b>Assalom alaykum</b> {message.from_user.first_name}
UstozShogird kanalining rasmiy botiga xush kelibsiz!

/help yordam buyrugi orqali nimalarga qodir ekanligimni bilib oling!''',reply_markup=main_button_mrk)
    
@dp.message_handler(text='Ish joy kerak')
async def ish_joy_handler(message: types.Message):
    await message.reply('''<b>Ish joyi topish uchun ariza berish</b>

Hozir sizga birnecha savollar beriladi. 
Har biriga javob bering. 
Oxirida agar hammasi to`g`ri bo`lsa, HA tugmasini bosing va arizangiz Adminga yuboriladi.''')
    await message.answer('<b>Ism, familiyangizni kiriting?</b>')
    await IshJoyiState.yosh.set()
    
@dp.message_handler(content_types=types.ContentType.TEXT,state=IshJoyiState.yosh)
async def ism_fimilia_handler(message: types.Message):
    print(f"{message.text}")
    await message.answer('''🕑 Yosh: 

Yoshingizni kiriting?
Masalan, 19''')
    await IshJoyiState.texnologiya.set()
    
@dp.message_handler(content_types="text",state=IshJoyiState.texnologiya)
async def yosh_handler(message:types.Message):
    print(message.text) 
    await message.answer("""📚 Texnologiya:

Talab qilinadigan texnologiyalarni kiriting?
Texnologiya nomlarini vergul bilan ajrating. Masalan, 

Java, C++, C#""")
    await IshJoyiState.aloqa.set()

@dp.message_handler(content_types="text",state=IshJoyiState.aloqa)
async def aloqa_handler(message: types.Message):
    print(message.text)
    await message.answer("""📞 Aloqa: 

Bog`lanish uchun raqamingizni kiriting?к
Masalan, +998 90 123 45 67""")
    await IshJoyiState.hudud.set()

    

if __name__ =='__main__':
    executor.start_polling(dispatcher=dp)










