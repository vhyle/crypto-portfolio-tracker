import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from models import User, Portfolio, Holding, PriceAlert, PriceHistory
from background import refresh_prices_loop, refresh_valid_coins_loop, save_price_history_loop
from database import engine, Base
from rate_limit import limiter
from routers import auth, portfolio, holding, alert, history

# Drop tables
# Base.metadata.drop_all(bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    price_task = asyncio.create_task(refresh_prices_loop())
    coin_task = asyncio.create_task(refresh_valid_coins_loop())
    history_task = asyncio.create_task(save_price_history_loop())

    yield

    # SHUTDOWN
    price_task.cancel()
    coin_task.cancel()
    history_task.cancel()
    await asyncio.gather(price_task, coin_task, history_task, return_exceptions=True)


app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(holding.router)
app.include_router(alert.router)
app.include_router(history.router)
