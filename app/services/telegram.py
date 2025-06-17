from hashlib import sha256
from hmac import compare_digest, new
from urllib import parse


bot_token = "TODO: bot token"

bot_username = "TODO: bot username"


async def get_invitation_link(telegram_id: int) -> str:
    return f"https://t.me/{bot_username}?start={telegram_id}"


def is_telegram(init_data: str) -> bool:
    vals = {}

    for item in init_data.split("&"):
        if "=" in item:
            key, value = item.split("=", 1)
            vals[key] = value

    hash_received = vals.pop("hash", None)

    if hash_received is None:
        return False

    data_check_string = "\n".join(
        f"{k}={parse.unquote(v)}" for k, v in sorted(vals.items())
    )

    secret_key = new(b"WebAppData", bot_token.encode(), sha256).digest()
    computed_hash = new(secret_key, data_check_string.encode(), sha256).hexdigest()

    return compare_digest(computed_hash, hash_received)
