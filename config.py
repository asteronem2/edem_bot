import os
from typing import List

from aiogram.types import InlineKeyboardMarkup
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID'))
TO_ADDRESS = os.environ.get('TO_ADDRESS')
BOT_USERNAME = os.environ.get('BOT_USERNAME')

CHATS_FOLDER_IDS: List[int] = [int(id_) for id_ in os.environ.get('CHATS_FOLDER_IDS').split(',')]