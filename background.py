import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal

import httpx

from cache import async_redis
from connection_manager import manager
from database import SessionLocal
from models import Holding, PriceAlert, PriceHistory
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
        # Get all coins that need prices - held and alerts
        held_coins = db.query(Holding.coin_name).distinct().all()
        alert_coins = db.query(PriceAlert.coin_name).distinct().all()
        all_coins = set([row[0] for row in held_coins] + [row[0] for row in alert_coins])
        coin_names = list(all_coins)

        # Possibly no holdings or alerts exist
        if not coin_names:
            return

        prices = await fetch_prices_batch(coin_names)

        for coin, price in prices.items():
            await async_redis.set(f"coingecko:price:{coin}", price, ex=180)

        # Check alerts against current prices
        alerts = db.query(PriceAlert).all()
        for alert in alerts:
            if alert.coin_name not in prices:
                continue  # No price available for this coin, skip

            current_price = Decimal(str(prices[alert.coin_name]))
            trigger_alert = False

            if alert.direction == "above" and current_price >= alert.target_price:
                trigger_alert = True
            elif alert.direction == "below" and current_price <= alert.target_price:
                trigger_alert = True

            if trigger_alert:
                # Alert connected user that their price goal has been reached
                await manager.send_to_user(alert.user_id, {
                    "type": "triggered_alert",
                    "coin_name": alert.coin_name,
                    "target_price": str(alert.target_price),
                    "current_price": str(current_price),
                    "direction": alert.direction
                })
                db.delete(alert)

        # Broadcast price update to all connected users
        await manager.broadcast({
            "type": "price_update",
            "prices": {coin: str(price) for coin, price in prices.items()}
        })

        db.commit()


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


async def save_price_history_loop():
    while True:
        try:
            await save_price_history()
        except Exception as e:
            print(f"Something went wrong capturing prices: {e}")

        # Runs every 2 hours
        await asyncio.sleep(7200)


async def save_price_history():
    with SessionLocal() as db:
        # Get current prices for all coins whether held or alert
        held_coins = db.query(Holding.coin_name).distinct().all()
        alert_coins = db.query(PriceAlert.coin_name).distinct().all()
        all_coins = set([row[0] for row in held_coins] + [row[0] for row in alert_coins])

        # Save price history for each coin
        now = datetime.now(timezone.utc)
        for coin in all_coins:
            price = await async_redis.get(f"coingecko:price:{coin}")
            if price is None:
                continue

            price_history = PriceHistory(
                coin_name=coin,
                price=Decimal(str(price)),
                timestamp=now
            )
            db.add(price_history)

        # Delete price history older than 120 days
        cutoff = now - timedelta(days=120)
        db.query(PriceHistory).filter(PriceHistory.timestamp < cutoff).delete()
        db.commit()
