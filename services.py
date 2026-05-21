from decimal import Decimal, ROUND_HALF_UP

import httpx

from cache import sync_redis
from models import Holding


def validate_coin(coin_name) -> bool:
    return sync_redis.sismember("coingecko:valid_coins", coin_name)


async def fetch_prices_batch(coin_names: list[str]) -> dict:
    # One string - no list
    coins_batch = ",".join(coin_names)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coins_batch}&vs_currencies=usd"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=20.0)
        data = response.json()
        prices = {coin: info["usd"] for coin, info in data.items()}
        return prices


def cache_price(coin_name: str) -> None:
    if sync_redis.exists(f"coingecko:price:{coin_name}"):
        return

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_name}&vs_currencies=usd"
    response = httpx.get(url, timeout=5.0)
    data = response.json()
    price = data.get(coin_name, {}).get("usd")
    if price is not None:
        sync_redis.set(f"coingecko:price:{coin_name}", price, ex=180)


def calculate_holding_price(holding: Holding) -> dict:
    # Calculate then round
    cached_price = sync_redis.get(f"coingecko:price:{holding.coin_name}")
    current_price = Decimal(cached_price)
    current_value = holding.amount * current_price
    buy_total = holding.amount * holding.buy_price
    profit_loss_percent = ((current_value - buy_total) / buy_total) * Decimal("100")

    current_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    current_value = current_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    profit_loss_percent = profit_loss_percent.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "id": holding.id,
        "coin_name": holding.coin_name,
        "amount": holding.amount,
        "buy_price": holding.buy_price,
        "portfolio_id": holding.portfolio_id,
        "current_price": current_price,
        "current_value": current_value,
        "profit_loss_percent": profit_loss_percent,
    }
