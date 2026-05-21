import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from models import User, Portfolio, Holding, PriceAlert #PriceHistory
from database import engine, Base
from routers import auth, portfolio, holding, alert
from background import refresh_prices_loop, refresh_valid_coins_loop

# Drop tables
# Base.metadata.drop_all(bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    price_task = asyncio.create_task(refresh_prices_loop())
    coin_task = asyncio.create_task(refresh_valid_coins_loop())

    yield

    # SHUTDOWN
    price_task.cancel()
    coin_task.cancel()
    await asyncio.gather(price_task, coin_task, return_exceptions=True)


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(holding.router)
app.include_router(alert.router)
