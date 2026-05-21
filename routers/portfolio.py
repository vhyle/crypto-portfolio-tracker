from fastapi import APIRouter, status, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import User, Portfolio
from rate_limit import limiter
from schemas import PortfolioCreate, PortfolioResponse
from security import get_current_user

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.get("/", response_model=list[PortfolioResponse])
def list_portfolios(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    portfolios = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).all()
    return portfolios


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
def get_portfolio(portfolio_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id,
                                           Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return portfolio


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10 per minute")
def create_portfolio(request: Request, portfolio: PortfolioCreate, current_user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    # Reject if user has duplicate portfolio name
    existing_portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id,
                                                    Portfolio.name == portfolio.name).first()
    if existing_portfolio:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Portfolio name already exists")

    # Reject if greater than 10 portfolios
    portfolio_count = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).count()
    if portfolio_count >= 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User has the maximum amount of portfolios (10)")

    new_portfolio = Portfolio(
        name=portfolio.name,
        user_id=current_user.id
    )
    try:
        db.add(new_portfolio)
        db.commit()
        db.refresh(new_portfolio)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Portfolio name already exists")
    return new_portfolio


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
@limiter.limit("10 per minute")
def update_portfolio(request: Request, portfolio_id: int, new_portfolio: PortfolioCreate,
                     current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Reject if user has duplicate portfolio name
    existing_portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id,
                                                    Portfolio.name == new_portfolio.name,
                                                    # Exclude current portfolio (can be a duplicate of itself)
                                                    # It would catch itself if it tried to update other fields
                                                    Portfolio.id != portfolio_id).first()
    if existing_portfolio:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Portfolio name already exists")

    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id,
                                           Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

    portfolio.name = new_portfolio.name
    try:
        db.commit()
        db.refresh(portfolio)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Portfolio name already exists")
    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10 per minute")
def delete_portfolio(request: Request, portfolio_id: int, current_user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id,
                                           Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    db.delete(portfolio)
    db.commit()
