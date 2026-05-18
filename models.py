from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True)
    password: Mapped[str] = mapped_column(String(60))

class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Reject if user has duplicate portfolio name
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="unique_portfolio_name_per_user"),
    )

# TODO: Complete Holding/s Per Portfolio
#class Holding(Base):
#    __tablename__ = "holdings"
#    pass

# TODO: Complete Price Alert Notification // Notify When Certain Price
#class PriceAlert(Base):
#    __tablename__ = "price_alerts"
#    pass

# TODO: Show Price History Over ? Figure Out Duration
#class PriceHistory(Base):
#    __tablename__ = "price_histories"
#    pass