from TonTools import TonCenterClient

from backend.config import settings

client = TonCenterClient(settings.ton_api_key)


async def get_ton_balance(address: str):
    return await client.get_balance(address)


async def get_ton_transactions(address: str):
    return len(await client.get_transactions(address=address, limit=31))
