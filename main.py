from fastapi import FastAPI

from models import User, Portfolio, Holding  # PriceAlert, PriceHistory
from database import engine, Base
from routers import auth, portfolio, holding

# Drop tables
# Base.metadata.drop_all(bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(holding.router)
