import httpx

from cache import sync_redis


def validate_coin(coin_name) -> bool:
    return sync_redis.sismember("coingecko:valid_coins", coin_name)


async def fetch_prices_batch(coin_names: list[str]) -> dict:
    # One string - no list
    coins_batch = ",".join(coin_names)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coins_batch}&vs_currencies=usd"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=12.5)
        data = response.json()
        prices = {coin: info["usd"] for coin, info in data.items()}
        return prices
