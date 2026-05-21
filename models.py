from decimal import Decimal

from sqlalchemy import String, ForeignKey, UniqueConstraint, Numeric
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
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    # Reject if user has duplicate portfolio name
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="unique_portfolio_name_per_user"),
    )


class Holding(Base):
    __tablename__ = "holdings"

    id: Mapped[int] = mapped_column(primary_key=True)
    coin_name: Mapped[str] = mapped_column(String(60), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=20, scale=8))
    buy_price: Mapped[Decimal] = mapped_column(Numeric(precision=20, scale=8))
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolios.id", ondelete="CASCADE"))

    # Reject duplicate coins in the same portfolio
    __table_args__ = (
        UniqueConstraint("portfolio_id", "coin_name", name="unique_holding_name_per_portfolio"),
    )


class PriceAlert(Base):
    __tablename__ = "price_alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    coin_name: Mapped[str] = mapped_column(String(60), index=True)
    target_price: Mapped[Decimal] = mapped_column(Numeric(precision=20, scale=8))
    direction: Mapped[str] = mapped_column(String(10))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))


# TODO: Show Price History Over ? Figure Out Duration
# class PriceHistory(Base):
#    __tablename__ = "price_histories"
#    pass
