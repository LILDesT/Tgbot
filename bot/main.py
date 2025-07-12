# bot/main.py
from aiogram import Dispatcher, Bot, F
from handlers.resume import pdf_received
import os

bot = Bot(os.environ["TG_TOKEN"])
dp  = Dispatcher()

dp.message(F.document.mime_type == "application/pdf")(pdf_received)

if __name__ == "__main__":
    dp.run_polling(bot)
