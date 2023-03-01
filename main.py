import os
import requests
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Load environment variables from .env file
load_dotenv()

# Set logging level to WARNING
logging.basicConfig(level=logging.WARNING)

# Initialize Telegram bot and dispatcher
bot = Bot(token=os.environ['TELEGRAM_API_TOKEN'])
dp = Dispatcher(bot)

# Binance endpoint for getting the price of a specific cryptocurrency
binance_api_endpoint = 'https://api.binance.com/api/v3/ticker/price'

# Define a function to get the price of a cryptocurrency from Binance


def get_crypto_price(symbol):
    try:
        params = {'symbol': symbol}
        headers = {'X-MBX-APIKEY': os.environ['BINANCE_API_KEY']}
        response = requests.get(binance_api_endpoint,
                                params=params, headers=headers)
        response.raise_for_status()
        price = response.json()['price']
        return price
    except requests.exceptions.HTTPError as e:
        logging.warning(
            f'Binance API вернул {e.response.status_code} {e.response.reason}: {e.response.text}')
        return None
    except Exception as e:
        logging.warning(f'Ошибка получения цены для {symbol}: {str(e)}')
        return None

# Define a handler for the /start command


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Привет! Я бот для проверки цены криптовалют на Binance. Отправь мне команду /price и код валюты (например, /price BTCUSDT), чтобы получить её текущую цену. 😊")

# Define a handler for the /price command


@dp.message_handler(commands=['price'])
async def price_command(message: types.Message):
    try:
        symbol = message.text.split()[1].upper()
        price = get_crypto_price(symbol)
        if price is not None:
            await message.reply(f'Текущая цена {symbol} - {price} USDT. 🚀')
        else:
            await message.reply('Ошибка получения цены, попробуйте позже. 😕')
    except:
        await message.reply('Пожалуйста, введите корректный код валюты после команды /price. 😕')

# Start the bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
