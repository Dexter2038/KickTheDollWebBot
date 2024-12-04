from os import environ

try:
    bot_username = environ["bot_username"]
except KeyError:
    raise Exception("Please set your bot username in .env file")


async def get_invitation_link(telegram_id):
    return f"https://t.me/{bot_username}?start={telegram_id}"
