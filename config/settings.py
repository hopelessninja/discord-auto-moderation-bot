import os
from dotenv import load_dotenv

load_dotenv()
"""from dotenv import load_dotenv

load_dotenv()
"""
# Application constants
MAXIMUM_CONFIRMATION_CHECKS = 20

# blockchain network

API_KEY = os.environ.get('API_K')
PRIV_KEY = os.environ.get('PRIV_KEY')

BASE_URL = "https://api-rinkeby.etherscan.io/api"
BANK_IP = '20.98.98.0'
BANK_PROTOCOL = 'http'
BOT_ACCOUNT_NUMBER = '0x5E5196925df2E3a1eA7aF2cDC22EE3DC80959994'
ETHER_VALUE = 10 ** 18

# Discord token
DISCORD_TOKEN = os.environ.get('my_secret')

# Mongo database
MONGO_DB_NAME = 'discord-db'
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_CLIENT_ADDRESS = f"mongodb+srv://usamasaleem:{os.environ.get('MONGO_USERNAME_PASSWORD')}@discord-bot.pg0f5.mongodb.net/?retryWrites=true&w=majority"

