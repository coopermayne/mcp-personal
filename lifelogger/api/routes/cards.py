"""Card routes for the API."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from lifelogger.db.database import get_db
from lifelogger.db.models import Card, Review
from lifelogger.core.sm2 import calculate_sm2
from lifelogger.api.schemas import (
    CardCreate,
    CardResponse,
    CardListResponse,
    ReviewCreate,
    ReviewResponse,
    ReviewResultResponse,
)

router = APIRouter(prefix="/cards", tags=["cards"])


@router.get("", response_model=CardListResponse)
def list_cards(
    tags: Optional[list[str]] = Query(None),
    card_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List cards with optional filters."""
    query = db.query(Card)

    if tags:
        for tag in tags:
            query = query.filter(Card.tags.contains([tag]))

    if card_type:
        query = query.filter(Card.card_type == card_type)

    total = query.count()
    cards = query.order_by(Card.created_at.desc()).offset(offset).limit(limit).all()

    return CardListResponse(cards=cards, total=total)


@router.get("/due", response_model=CardListResponse)
def get_due_cards(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get cards that are due for review."""
    now = datetime.now(timezone.utc)

    query = db.query(Card).filter(Card.due_at <= now)
    total = query.count()
    cards = query.order_by(Card.due_at.asc()).limit(limit).all()

    return CardListResponse(cards=cards, total=total)


@router.post("/{card_id}/review", response_model=ReviewResultResponse)
def record_review(
    card_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db),
):
    """Record a review for a card."""
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    now = datetime.now(timezone.utc)

    # Calculate new SM-2 values
    result = calculate_sm2(
        rating=review.rating,
        current_ease_factor=card.ease_factor,
        current_interval_days=card.interval_days,
        now=now,
    )

    # Update card
    card.ease_factor = result.ease_factor
    card.interval_days = result.interval_days
    card.due_at = result.due_at

    # Create review record
    db_review = Review(card_id=card_id, rating=review.rating, reviewed_at=now)
    db.add(db_review)
    db.commit()
    db.refresh(card)
    db.refresh(db_review)

    rating_names = {0: "again", 1: "hard", 2: "good", 3: "easy"}
    message = f"Recorded {rating_names[review.rating]} ({review.rating}). Next review in {result.interval_days} day(s)."

    return ReviewResultResponse(review=db_review, card=card, message=message)
