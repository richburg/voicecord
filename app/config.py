from os import getenv

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(getenv("BOT_TOKEN"))
DEBUG_FEATURES: bool = False

JOIN_TO_CREATE_CHANNEL_ID: int = 1407392358336561203
CHANNELS_CATEGORY_ID: int = 1407392315177304136
GUILD_ID: int = 1357037414689800502
