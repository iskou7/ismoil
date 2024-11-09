from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging

API_TOKEN = '6979098008:AAHhh2cMUO15rQMoPwaRtVC07gnRVYqLyPw'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class OrderStates(StatesGroup):
    waiting_for_address = State()
    waiting_for_items = State()
    confirming_order = State()

menu_items = {
    'pizza': {
        'Margaritta': 10,
        'Pepperoni': 12,
        'Hawaiian': 11
    },
    'burgers': {
        'Classic': 8,
        'Cheeseburger': 9,
        'CHefBurger': 13
    },
    'turkish': {
        'Döner': 7,
        'Lahmacun': 8, 
        'İskender': 12,
        'Pide': 9,
        'Kebab': 11
    },
    'uzbek': {
        'Palov': 8,
        'Lagman': 7,
        'Shashlik': 10,
        'Manti': 6,
        'Somsa': 4
    },
    'drinks': {
        'Cola': 2,
        'Water': 1,
        'Juice': 3,
        'Ayran': 2
    }
}

texts = {
    'uz': {
        'welcome': 'Ismoil Kebab botiga xush kelibsiz!\n\nMenudan buyurtma bering!',
        'help': 'Men sizga ovqat buyurtma qilish va yetkazib berishni kuzatishda yordam beraman.',
        'contact_thanks': "Kontakt uchun rahmat! Yetkazib berish uchun foydalanamiz.\nTelefon: {}\nIsm: {}",
        'menu': 'Menuni tanlang:',
        'ask_address': 'Yetkazib berish manzilini kiriting:',
        'ask_items': 'Nimani buyurtma qilmoqchisiz? (Ro\'yxatni kiriting)',
        'confirm_order': 'Sizning buyurtmangiz:\nManzil: {}\nMahsulotlar: {}\nShundaymi?'
    }
}

main_button_mrk = ReplyKeyboardMarkup(resize_keyboard=True)
main_button_mrk.add(
    KeyboardButton("Kontakt ulashish", request_contact=True),
    KeyboardButton("📋 Menu"),
    KeyboardButton("🛍 Buyurtmalarim"),
    KeyboardButton("📍 Lokatsiya", request_location=True)
)

menu_kb = InlineKeyboardMarkup(row_width=2)
menu_kb.add(
    InlineKeyboardButton("🍕 Pizza", callback_data='menu_pizza'),
    InlineKeyboardButton("🍔 Burgerlar", callback_data='menu_burgers'),
    InlineKeyboardButton("🥙 Turkish", callback_data='menu_turkish'),
    InlineKeyboardButton("🥘 Ozbek", callback_data='menu_uzbek'),
    InlineKeyboardButton("🥤 Ichimliklar", callback_data='menu_drinks')
)

ADMIN_CHAT_ID = "753797411"

@dp.callback_query_handler(lambda c: c.data == 'confirm_order', state=OrderStates.confirming_order)
async def process_order_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        cart = data.get('cart', [])
        address = data.get('address')
        total = sum(item['price'] for item in cart)
        
   
        await callback_query.message.answer("Buyurtmangiz tasdiqlandi! Tez orada yetkazib beramiz.")
        
      
        admin_message = f"🆕 Yangi buyurtma!\n\n"
        admin_message += f"👤 Mijoz: {callback_query.from_user.full_name}\n"
        admin_message += f"📞 ID: {callback_query.from_user.id}\n"
        admin_message += f"📍 Manzil: {address}\n\n"
        admin_message += "🛍 Buyurtma:\n"
        admin_message += "\n".join(f"• {item['item']} - ${item['price']}" for item in cart)
        admin_message += f"\n\n💰 Jami: ${total}"
        
        await bot.send_message(ADMIN_CHAT_ID, admin_message)
        data['cart'] = []
        
    await state.finish()


import sqlite3

def save_order_to_db(user_id, items, total, address):
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''INSERT INTO orders 
                 (user_id, items, total, address, status) 
                 VALUES (?, ?, ?, ?, ?)''', 
              (user_id, str(items), total, address, 'new'))
    conn.commit()
    conn.close()






@dp.message_handler(commands='start')
async def start_handler(message: types.Message):
    await message.answer(
        text=f"Assalomu alaykum {message.from_user.first_name}!",
        reply_markup=main_button_mrk
    )
    await message.answer("Yetkazib berish uchun kontaktingizni ulashing", reply_markup=main_button_mrk)

@dp.message_handler(lambda message: message.text == "📋 Menu")
async def show_menu(message: types.Message):
    await message.answer("Kategoriyani tanlang:", reply_markup=menu_kb)

@dp.callback_query_handler(lambda c: c.data.startswith('menu_'))
async def process_menu_category(callback_query: types.CallbackQuery, state: FSMContext):
    category = callback_query.data.split('_')[1]
    
    category_kb = InlineKeyboardMarkup(row_width=2)
    for item, price in menu_items[category].items():
        category_kb.add(
            InlineKeyboardButton(f"{item} - ${price}", callback_data=f'add_{category}_{item}')
        )
    category_kb.add(
        InlineKeyboardButton("🛒 Savatcha", callback_data='view_cart'),
        InlineKeyboardButton("🔙 Orqaga qaytish", callback_data='back_to_menu')
    )
    
    await callback_query.message.edit_text(
        f"{category.title()} bolimidan tanlang:", 
        reply_markup=category_kb
    )

@dp.callback_query_handler(lambda c: c.data.startswith('add_'))
async def add_to_cart(callback_query: types.CallbackQuery, state: FSMContext):
    _, category, item = callback_query.data.split('_')
    async with state.proxy() as data:
        if 'cart' not in data:
            data['cart'] = []
        data['cart'].append({
            'item': item,
            'price': menu_items[category][item]
        })
    await callback_query.answer(f"{item} savatchaga qo'shildi!")

@dp.callback_query_handler(lambda c: c.data == 'view_cart')
async def view_cart(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        cart = data.get('cart', [])
        if not cart:
            await callback_query.message.answer("Savatchangiz bo'sh!")
            return
            
        total = sum(item['price'] for item in cart)
        cart_text = "Sizning savatchagiz:\n" + "\n".join(
            f"• {item['item']} - ${item['price']}" for item in cart
        ) + f"\n\nJami: ${total}"
        
        cart_kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Buyurtma berish", callback_data='checkout'),
            InlineKeyboardButton("🗑 Tozalash", callback_data='clear_cart')
        )
        await callback_query.message.answer(cart_text, reply_markup=cart_kb)

@dp.callback_query_handler(lambda c: c.data == 'clear_cart')
async def clear_cart(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['cart'] = []
    await callback_query.message.answer("Savatcha tozalandi!")

@dp.callback_query_handler(lambda c: c.data == 'checkout')
async def checkout(callback_query: types.CallbackQuery, state: FSMContext):
    await OrderStates.waiting_for_address.set()
    await callback_query.message.answer("Yetkazib berish manzilini kiriting:")

@dp.callback_query_handler(lambda c: c.data == 'back_to_menu')
async def back_to_main_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "Kategoriyani tanlang:", 
        reply_markup=menu_kb
    )

@dp.message_handler(state=OrderStates.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text
        cart = data.get('cart', [])
        total = sum(item['price'] for item in cart)
        order_text = f"Yetkazish manzili: {message.text}\n\nBuyurtma tafsilotlari:\n" + \
                    "\n".join(f"• {item['item']} - ${item['price']}" for item in cart) + \
                    f"\n\nJami: ${total}"
        
        confirm_kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Tasdiqlash", callback_data='confirm_order'),
            InlineKeyboardButton("❌ Bekor qilish", callback_data='cancel_order')
        )
        await message.answer(order_text, reply_markup=confirm_kb)
    await OrderStates.confirming_order.set()

@dp.callback_query_handler(lambda c: c.data in ['confirm_order', 'cancel_order'], state=OrderStates.confirming_order)
async def process_order_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'confirm_order':
        await callback_query.message.answer("Buyurtmangiz tasdiqlandi! Tez orada yetkazib beramiz.")
        async with state.proxy() as data:
            data['cart'] = []
    else:
        await callback_query.message.answer("Buyurtma bekor qilindi.")
    await state.finish()

@dp.message_handler(content_types=['contact'])
async def handle_contact(message: types.Message):
    phone = message.contact.phone_number
    first_name = message.contact.first_name
    await message.answer(f"Kontakt uchun rahmat!\nTelefon: {phone}\nIsm: {first_name}")

@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    await message.answer("Lokatsiya uchun rahmat! Yetkazib berish uchun foydalanamiz.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
