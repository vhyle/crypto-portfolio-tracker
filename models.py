from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True)
    password: Mapped[str] = mapped_column(String(60))

# TODO: Complete Portfolio Per User
class Portfolio(Base):
    __tablename__ = "portfolios"
    pass

# TODO: Complete Holding/s Per Portfolio
class Holding(Base):
    __tablename__ = "holdings"
    pass

# TODO: Complete Price Alert Notification // Notify When Certain Price
class PriceAlert(Base):
    __tablename__ = "price_alerts"
    pass

# TODO: Show Price History Over ? Figure Out Duration
class PriceHistory(Base):
    __tablename__ = "price_histories"
    pass