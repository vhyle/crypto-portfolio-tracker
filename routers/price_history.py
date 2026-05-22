from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User, PriceHistory
from schemas import PriceHistoryResponse
from security import get_current_user

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{coin_name}", response_model=list[PriceHistoryResponse])
def get_price_history(coin_name: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    history = db.query(PriceHistory).filter(PriceHistory.coin_name == coin_name).order_by(
        PriceHistory.timestamp.desc()).all()
    return history


@router.get("/{coin_name}/range", response_model=list[PriceHistoryResponse])
def get_price_history_range(coin_name: str, days: int = Query(default=7, ge=1, le=120),
                            current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    history = db.query(PriceHistory).filter(PriceHistory.coin_name == coin_name,
                                            PriceHistory.timestamp >= cutoff).order_by(
        PriceHistory.timestamp.desc()).all()
    return history
