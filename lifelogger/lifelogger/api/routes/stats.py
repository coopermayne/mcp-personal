"""Stats routes for the API."""

from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from lifelogger.db.database import get_db
from lifelogger.db.models import Entry, Card, Review
from lifelogger.api.schemas import StatsResponse

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Get basic statistics."""
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    total_entries = db.query(Entry).count()
    total_cards = db.query(Card).count()
    due_today = db.query(Card).filter(Card.due_at <= now).count()
    reviews_this_week = db.query(Review).filter(Review.reviewed_at >= week_ago).count()

    return StatsResponse(
        total_entries=total_entries,
        total_cards=total_cards,
        due_today=due_today,
        reviews_this_week=reviews_this_week,
    )
