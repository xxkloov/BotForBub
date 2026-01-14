import os
from typing import Optional

def get_env(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    value = os.getenv(key, default)
    if required and not value:
        raise ValueError(f"Required environment variable {key} is not set")
    return value

DISCORD_BOT_TOKEN = get_env("DISCORD_BOT_TOKEN", required=True)
DISCORD_CHANNEL_ID = int(get_env("DISCORD_CHANNEL_ID", "0", required=True))
API_KEY = get_env("API_KEY", "")
HOST = get_env("HOST", "0.0.0.0")
PORT = int(get_env("PORT", "5000"))

ADMIN_USER_IDS = []
admin_ids_str = get_env("ADMIN_USER_IDS", "")
if admin_ids_str:
    try:
        ADMIN_USER_IDS = [int(uid.strip()) for uid in admin_ids_str.split(",") if uid.strip()]
    except ValueError:
        pass

RATE_LIMIT_REQUESTS = int(get_env("RATE_LIMIT_REQUESTS", "10"))
RATE_LIMIT_WINDOW = int(get_env("RATE_LIMIT_WINDOW", "60"))
ADMIN_PASSWORD = get_env("ADMIN_PASSWORD", "admin")
PLACE_ID = get_env("PLACE_ID", "132682513110700")

