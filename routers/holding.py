from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import User, Portfolio, Holding
from schemas import HoldingCreate, HoldingUpdate, HoldingResponse
from security import get_current_user

router = APIRouter(prefix="/portfolios/{portfolio_id}/holdings", tags=["holdings"])


@router.get("/", response_model=list[HoldingResponse])
def list_holdings(portfolio_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    holdings = db.query(Holding).join(Portfolio).filter(Holding.portfolio_id == portfolio_id,
                                                        Portfolio.user_id == current_user.id).all()
    return holdings


@router.get("/{holding_id}", response_model=HoldingResponse)
def get_holding(portfolio_id: int, holding_id: int, current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    holding = db.query(Holding).join(Portfolio).filter(Holding.id == holding_id,
                                                       Holding.portfolio_id == portfolio_id,
                                                       Portfolio.user_id == current_user.id).first()
    if not holding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holding not found")
    return holding


@router.post("/", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
def create_holding(portfolio_id: int, holding: HoldingCreate, current_user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    ## TODO: ADD COIN VERIFICATION

    # Verify portfolio belongs to user
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id,
                                           Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

    # Reject duplicate coins holding in the same portfolio
    existing_coin = db.query(Holding).filter(Holding.portfolio_id == portfolio_id,
                                             Holding.coin_name == holding.coin_name).first()
    if existing_coin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Coin already exists")

    # Reject if greater than 25 holdings per portfolio
    holding_count = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).count()
    if holding_count >= 25:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User has the maximum amount of coins per portfolio (25)")

    new_holding = Holding(
        coin_name=holding.coin_name,
        amount=holding.amount,
        buy_price=holding.buy_price,
        portfolio_id=portfolio_id
    )
    try:
        db.add(new_holding)
        db.commit()
        db.refresh(new_holding)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Coin already exists")
    return new_holding


@router.put("/{holding_id}", response_model=HoldingResponse)
def update_holding(portfolio_id: int, holding_id: int, new_holding: HoldingUpdate,
                   current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    holding = db.query(Holding).join(Portfolio).filter(Holding.id == holding_id,
                                                       Holding.portfolio_id == portfolio_id,
                                                       Portfolio.user_id == current_user.id).first()
    if not holding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holding not found")

    holding.amount = new_holding.amount
    holding.buy_price = new_holding.buy_price
    db.commit()
    db.refresh(holding)
    return holding


@router.delete("/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(portfolio_id: int, holding_id: int, current_user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    holding = db.query(Holding).join(Portfolio).filter(Holding.id == holding_id,
                                                       Holding.portfolio_id == portfolio_id,
                                                       Portfolio.user_id == current_user.id).first()
    if not holding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holding not found")
    db.delete(holding)
    db.commit()
