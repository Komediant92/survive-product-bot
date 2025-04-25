import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import os

API_TOKEN = os.getenv("BOT_TOKEN")

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Игровое состояние
user_state = {}

# События и последствия
events = [
    {
        "text": "Дизайнер предлагает редизайн онбординга. Что делать?",
        "options": {
            "Игнорировать": {"psy": -10, "growth": 0},
            "Поддержать": {"psy": -5, "growth": 5},
            "Перенести на Q3": {"psy": 0, "growth": -5}
        }
    },
    {
        "text": "Пользователи жалуются на UX формы. Что делаем?",
        "options": {
            "Приоритизировать багфикс": {"psy": -5, "growth": 5},
            "Ответить в чат: «запишем»": {"psy": 0, "growth": -2},
            "Проигнорировать": {"psy": -10, "growth": -5}
        }
    }
]

# Кнопки
def get_keyboard(options):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for option in options:
        keyboard.add(KeyboardButton(option))
    return keyboard

# Команды
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    user_state[message.from_user.id] = {"psy": 100, "growth": 0, "event": 0}
    await message.answer("Добро пожаловать в 'Выживи как продакт'! 🚀

Готов начать?", reply_markup=types.ReplyKeyboardRemove())
    await send_event(message.from_user.id)

@dp.message_handler(commands=["stats"])
async def send_stats(message: types.Message):
    state = user_state.get(message.from_user.id, {})
    await message.answer(f"🧠 Психика: {state.get('psy', 0)}
📈 Рост: {state.get('growth', 0)}")

async def send_event(user_id):
    state = user_state[user_id]
    event_index = state["event"] % len(events)
    event = events[event_index]
    state["current_event"] = event
    keyboard = get_keyboard(event["options"].keys())
    await bot.send_message(user_id, f"{event['text']}", reply_markup=keyboard)

@dp.message_handler()
async def handle_choice(message: types.Message):
    state = user_state.get(message.from_user.id)
    if not state or "current_event" not in state:
        await message.answer("Напиши /start, чтобы начать игру.")
        return
    event = state["current_event"]
    choice = message.text
    if choice not in event["options"]:
        await message.answer("Выбери вариант с клавиатуры.")
        return
    outcome = event["options"][choice]
    state["psy"] += outcome["psy"]
    state["growth"] += outcome["growth"]
    state["event"] += 1
    await message.answer(f"🧠 {outcome['psy']} к психике
📈 {outcome['growth']} к росту", reply_markup=types.ReplyKeyboardRemove())
    await send_event(message.from_user.id)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
