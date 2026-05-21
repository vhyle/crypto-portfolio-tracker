import asyncio

import httpx

from cache import async_redis
from database import SessionLocal
from models import Holding
from services import fetch_prices_batch


async def refresh_prices_loop():
    while True:
        try:
            await refresh_prices()
        except Exception as e:
            print(f"Something went wrong refreshing price: {e}")

        # Safeguard runs every 90 seconds, 180 seconds TTL
        await asyncio.sleep(90)


async def refresh_prices():
    with SessionLocal() as db:
        # Get all unique coin names from all user holdings
        coins = db.query(Holding.coin_name).distinct().all()

        coin_names = [row[0] for row in coins]

        # Possibly no holdings exist
        if not coin_names:
            return

        prices = await fetch_prices_batch(coin_names)

        for coin, price in prices.items():
            await async_redis.set(f"coingecko:price:{coin}", price, ex=180)


async def refresh_valid_coins_loop():
    while True:
        try:
            await refresh_valid_coins()
        except Exception as e:
            print(f"Something went wrong refreshing valid coins: {e}")
        # Safeguard runs every 12 hours, 24 hours TTL
        await asyncio.sleep(43200)


async def refresh_valid_coins():
    url = "https://api.coingecko.com/api/v3/coins/list"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30.0)
        coins = response.json()
        coin_ids = [coin["id"] for coin in coins]

    # Replace cache: delete old set, populate new set, 24 hours TTL
    await async_redis.delete("coingecko:valid_coins")
    await async_redis.sadd("coingecko:valid_coins", *coin_ids)
    await async_redis.expire("coingecko:valid_coins", 86400)
