from decimal import Decimal
from typing import Literal
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


# User Registration
class UserCreate(BaseModel):
    username: str = Field(min_length=6, max_length=20, pattern=r"^[a-zA-Z0-9]+$", description="Enter your username")
    password: str = Field(min_length=8, max_length=72, description="Enter your password")


# User Login
class UserLogin(BaseModel):
    username: str
    password: str


# User Response
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


# Authentication Response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Portfolio Creation
class PortfolioCreate(BaseModel):
    name: str = Field(min_length=2, max_length=40, description="Enter your portfolio name")


# Portfolio Object Response
class PortfolioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    user_id: int


# Crypto Holding Creation
class HoldingCreate(BaseModel):
    coin_name: str = Field(min_length=2, max_length=60, pattern=r"^[a-z0-9-]+$")
    amount: Decimal = Field(gt=0, max_digits=20, decimal_places=8)
    buy_price: Decimal = Field(gt=0, max_digits=20, decimal_places=8)


# Crypto Holding Update
class HoldingUpdate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=20, decimal_places=8)
    buy_price: Decimal = Field(gt=0, max_digits=20, decimal_places=8)


# Crypto Holding Object Response
class HoldingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    coin_name: str
    amount: Decimal
    buy_price: Decimal
    portfolio_id: int
    current_price: Decimal
    current_value: Decimal
    profit_loss_percent: Decimal


# Price Alert Notification Creation
class PriceAlertCreate(BaseModel):
    coin_name: str = Field(min_length=2, max_length=60, pattern=r"^[a-z0-9-]+$")
    target_price: Decimal = Field(gt=0, max_digits=20, decimal_places=8)
    direction: Literal["above", "below"]


# Price Alert Update
class PriceAlertUpdate(BaseModel):
    target_price: Decimal = Field(gt=0, max_digits=20, decimal_places=8)
    direction: Literal["above", "below"]


# Price Alert Object Response
class PriceAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    coin_name: str
    target_price: Decimal
    direction: str
    user_id: int


# Price History Response
class PriceHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    coin_name: str
    price: Decimal
    timestamp: datetime