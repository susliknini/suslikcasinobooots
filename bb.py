import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
API_TOKEN = '8319799543:AAG8ttS8fLk4FUrVJPnsxIO-5EkZS2J7-ug'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Эмодзи для оформления
EMOJI_COINS = "🪙"
EMOJI_DICE = "🎲"
EMOJI_SUPPORT = "🛟"
EMOJI_COMPLAINT = "⚠️"
EMOJI_MONEY = "💵"
EMOJI_SLOT = "🎰"
EMOJI_CARDS = "🎴"

# Клавиатура главного меню
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(f"{EMOJI_MONEY} Баланс", callback_data="balance"),
        InlineKeyboardButton(f"{EMOJI_DICE} Игры", callback_data="games"),
        InlineKeyboardButton(f"{EMOJI_SUPPORT} Поддержка", callback_data="support"),
        InlineKeyboardButton(f"{EMOJI_COMPLAINT} Пожаловаться", callback_data="complaint")
    ]
    keyboard.add(*buttons)
    return keyboard

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_text = f"""
    🎰 *Добро пожаловать в МАНЕТКИ ВИЗУАЛЬНЫЕ* 🎰

    {EMOJI_COINS} Играй и наслаждайся нашей платформой!
    {EMOJI_DICE} Попробуй свою удачу в различных играх!
    {EMOJI_MONEY} Выигрывай монеты и получай призы!

    *Выбери действие:* 👇
    """
    await message.reply(welcome_text, 
                       parse_mode=types.ParseMode.MARKDOWN, 
                       reply_markup=get_main_keyboard())

# Обработчик инлайн кнопок
@dp.callback_query_handler(lambda c: c.data in ['balance', 'games', 'support', 'complaint'])
async def process_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    if callback_query.data == 'balance':
        text = f"""
        {EMOJI_MONEY} *Твой баланс* {EMOJI_MONEY}

        💰 Монеты: 1000 {EMOJI_COINS}
        🏆 Бонусы: 50 {EMOJI_COINS}

        Пополни баланс или играй, чтобы получить больше!
        """
        await bot.send_message(callback_query.from_user.id, 
                             text, 
                             parse_mode=types.ParseMode.MARKDOWN)
    
    elif callback_query.data == 'games':
        text = f"""
        {EMOJI_DICE} *Доступные игры* {EMOJI_DICE}

        1. {EMOJI_SLOT} Слот-машины
        2. {EMOJI_CARDS} Карточные игры
        3. {EMOJI_DICE} Кости
        4. 🏀 Баскетбол

        Выбери игру и испытай удачу!
        """
        await bot.send_message(callback_query.from_user.id, 
                             text, 
                             parse_mode=types.ParseMode.MARKDOWN)
    
    elif callback_query.data == 'support':
        text = f"""
        {EMOJI_SUPPORT} *Поддержка* {EMOJI_SUPPORT}

        По всем вопросам обращайся к нашему менеджеру:
        @manager_username

        Или пиши на почту:
        support@manetki-visual.ru
        """
        await bot.send_message(callback_query.from_user.id, 
                             text, 
                             parse_mode=types.ParseMode.MARKDOWN)
    
    elif callback_query.data == 'complaint':
        text = f"""
        {EMOJI_COMPLAINT} *Пожаловаться* {EMOJI_COMPLAINT}

        Если у тебя есть жалобы или предложения, напиши нам:
        @complaints_bot

        Мы ценим твое мнение и улучшим сервис!
        """
        await bot.send_message(callback_query.from_user.id, 
                             text, 
                             parse_mode=types.ParseMode.MARKDOWN)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
