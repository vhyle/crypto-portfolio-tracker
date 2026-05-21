from fastapi import APIRouter, status, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models import User, PriceAlert
from rate_limit import limiter
from schemas import PriceAlertCreate, PriceAlertUpdate, PriceAlertResponse
from security import get_current_user
from services import validate_coin, cache_price

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=list[PriceAlertResponse])
def list_alerts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    alerts = db.query(PriceAlert).filter(PriceAlert.user_id == current_user.id).all()
    return alerts


@router.get("/{alert_id}", response_model=PriceAlertResponse)
def get_alert(alert_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id,
                                        PriceAlert.user_id == current_user.id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


@router.post("/", response_model=PriceAlertResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20 per minute")
def create_alert(request: Request, alert: PriceAlertCreate, current_user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    # Check if coin is valid
    if not validate_coin(alert.coin_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid coin")

    # Reject if greater than 10 alerts per coin
    alert_count = db.query(PriceAlert).filter(PriceAlert.user_id == current_user.id,
                                              PriceAlert.coin_name == alert.coin_name).count()
    if alert_count >= 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User has the maximum alerts per coin (10)")

    # Cache price if missing (handles new coins yet to run in background task)
    cache_price(alert.coin_name)

    new_alert = PriceAlert(
        coin_name=alert.coin_name,
        target_price=alert.target_price,
        direction=alert.direction,
        user_id=current_user.id
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert


@router.put("/{alert_id}", response_model=PriceAlertResponse)
@limiter.limit("20 per minute")
def update_alert(request: Request, alert_id: int, new_alert: PriceAlertUpdate,
                 current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id,
                                        PriceAlert.user_id == current_user.id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    alert.target_price = new_alert.target_price
    alert.direction = new_alert.direction
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20 per minute")
def delete_alert(request: Request, alert_id: int, current_user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id,
                                        PriceAlert.user_id == current_user.id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    db.delete(alert)
    db.commit()
