from database import engine, Base
from fastapi import FastAPI
from models import User, Portfolio #Holding, PriceAlert, PriceHistory
from routers import auth, portfolio

# Drop tables
#Base.metadata.drop_all(bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router)
app.include_router(portfolio.router)