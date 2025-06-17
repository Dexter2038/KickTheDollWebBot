from TonTools import TonCenterClient

client = TonCenterClient(
    "0d7538e18bc61865ad01c859e12e90dcfdf72e4b348621c8db01996f78041ecf"
)


async def get_ton_balance(address: str):
    return await client.get_balance(address)


async def get_ton_transactions(address: str):
    return len(await client.get_transactions(address=address, limit=31))
