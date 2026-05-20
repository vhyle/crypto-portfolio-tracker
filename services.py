import httpx

from cache import sync_redis


def validate_coin(coin_name) -> bool:
    # Does coin exist? Or fetch
    if not sync_redis.exists("coingecko:valid_coins"):
        url = "https://api.coingecko.com/api/v3/coins/list"
        response = httpx.get(url, timeout=12.5)
        coins = response.json()
        coin_ids = [coin["id"] for coin in coins]
        sync_redis.sadd("coingecko:valid_coins", *coin_ids)
        sync_redis.expire("coingecko:valid_coins", 86400)

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
