import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ParseMode
from binance.client import AsyncClient, BinanceAPIException
from dotenv import load_dotenv

load_dotenv()

# Load Telegram bot token from environment variable
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Set up logger
logging.basicConfig(filename="bot.log", level=logging.ERROR)

# Create asynchronous Binance API client
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY")
BINANCE_API_SECRET = os.environ.get("BINANCE_API_SECRET")
client = AsyncClient(BINANCE_API_KEY, BINANCE_API_SECRET)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply("Hi there! I'm a bot that can retrieve the current price of cryptocurrencies from Binance. To get started, type /price [symbol], where [symbol] is the ticker symbol of the cryptocurrency you want to get the price for.")


@dp.message_handler(Command("price"))
async def cmd_price(message: types.Message):
    symbol = message.get_args().upper()
    if not symbol:
        await message.reply("Please enter a cryptocurrency symbol after the command. For example: /price BTCUSDT")
        return
    try:
        ticker = await client.get_symbol_ticker(symbol=symbol)
        price = ticker['price']
        await message.reply(f"{symbol} current price is {price}")
    except BinanceAPIException as e:
        if e.code == -1121:
            await message.reply(f"Invalid symbol {symbol}. Please enter a valid symbol.")
        elif e.code == -2010:
            await message.reply(f"{symbol} withdrawals are disabled.")
        else:
            await message.reply(f"An error occurred while retrieving {symbol} price. {e}")
    except Exception as e:
        logging.error(e)
        await message.reply("An error occurred. Please try again later.")


async def main():
    await dp.start_polling()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
