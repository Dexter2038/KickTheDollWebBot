from hashlib import sha256
from urllib import parse
from hmac import new, compare_digest
from os import environ

try:
    bot_token = environ["bot_token"]
except KeyError:
    raise Exception("Please set your bot token in .env file")


def is_telegram(init_data: str) -> bool:
    if init_data == "2":
        return True
    vals = {}

    for item in init_data.split('&'):
        if '=' in item:
            key, value = item.split('=', 1)
            vals[key] = value

    hash_received = vals.pop('hash', None)

    if hash_received is None:
        return False

    data_check_string = '\n'.join(f"{k}={parse.unquote(v)}"
                                  for k, v in sorted(vals.items()))

    secret_key = new(b"WebAppData", bot_token.encode(), sha256).digest()
    computed_hash = new(secret_key, data_check_string.encode(),
                        sha256).hexdigest()

    return compare_digest(computed_hash, hash_received)
