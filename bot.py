import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

TOKEN = "9039056446:AAGKcvNtiFC5UnAH0h_YuXxwiut-FEq6320" 

bot = Bot(token=TOKEN)
dp = Dispatcher()

TEXTS = {
    "ru": {"start": "Салом! Выбери игру:", "play": "🍚 Собери плов", "district": "🗺️ Угадай район", "pilaf": "🍲 Плов или не плов?", "donate": "💎 Поддержать", "lang": "🌐 Язык"},
    "uz": {"start": "Salom! O'yinni tanlang:", "play": "🍚 Palov yig'", "district": "🗺️ Rayonni top", "pilaf": "🍲 Palovmi yoki yo'qmi?", "donate": "💎 Qo'llab-quvvatlash", "lang": "🌐 Til"}
}
user_lang = {} 

def main_menu(lang="ru"):
    t = TEXTS[lang]
    builder = ReplyKeyboardBuilder()
    builder.button(text=t["play"])
    builder.button(text=t["district"])
    builder.button(text=t["pilaf"])
    builder.button(text=t["donate"])
    builder.button(text=t["lang"])
    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: Message):
    user_lang[message.from_user.id] = "ru"
    await message.answer(TEXTS["ru"]["start"], reply_markup=main_menu("ru"))

@dp.message(F.text.in_([TEXTS["ru"]["lang"], TEXTS["uz"]["lang"]]))
async def switch_lang(message: Message):
    uid = message.from_user.id
    new_lang = "uz" if user_lang.get(uid, "ru") == "ru" else "ru"
    user_lang[uid] = new_lang
    await message.answer(TEXTS[new_lang]["start"], reply_markup=main_menu(new_lang))

@dp.message(F.text.in_([TEXTS["ru"]["play"], TEXTS["uz"]["play"]]))
async def play_pilaf(message: Message):
    lang = user_lang.get(message.from_user.id, "ru")
    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Рис" if lang=="ru" else "Guruch", callback_data="pilaf_rice")],
        [InlineKeyboardButton(text="Мясо" if lang=="ru" else "Go'sht", callback_data="pilaf_meat")],
        [InlineKeyboardButton(text="Морковь" if lang=="ru" else "Sabzi", callback_data="pilaf_carrot")]
    ])
    await message.answer("Шаг 1: Выбери главный ингредиент:", reply_markup=builder)

@dp.callback_query(F.data.startswith("pilaf_"))
async def pilaf_step(callback):
    await callback.answer()
    choice = callback.data.split("_")[1]
    results = {
        "rice": "🍚 Ты выбрал Рис! Без него плова не бывает.",
        "meat": "🥩 Ты выбрал Мясо! Баранина или говядина — выбор настоящего джигита.",
        "carrot": "🥕 Ты выбрал Морковь! Желтая или красная — главный секрет вкуса."
    }
    await callback.message.edit_text(f"{results[choice]}\n\n(Остальные шаги добавим на следующем этапе!)")

@dp.message(F.text.in_([TEXTS["ru"]["district"], TEXTS["uz"]["district"]]))
async def guess_district(message: Message):
    await message.answer("Викторина про районы скоро появится! 🗺️")

@dp.message(F.text.in_([TEXTS["ru"]["pilaf"], TEXTS["uz"]["pilaf"]]))
async def pilaf_or_not(message: Message):
    await message.answer("Игра «Плов или не плов?» скоро появится! 🍲")

@dp.message(F.text.in_([TEXTS["ru"]["donate"], TEXTS["uz"]["donate"]]))
async def donate(message: Message):
    await message.answer("💎 Донат через Telegram Stars скоро будет подключён.")

# --- ЗАГЛУШКА ДЛЯ RENDER ---
class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), WebServer)
    server.serve_forever()

async def main():
    threading.Thread(target=run_server, daemon=True).start()
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())