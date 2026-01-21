"""SM-2 spaced repetition algorithm implementation.

The SM-2 algorithm calculates the next review interval based on:
- The current ease factor (how easy the card is to remember)
- The current interval (days since last review)
- The user's rating (0=again, 1=hard, 2=good, 3=easy)

Reference: https://en.wikipedia.org/wiki/SuperMemo#Description_of_SM-2_algorithm
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


# Minimum ease factor to prevent cards from becoming too hard
MIN_EASE_FACTOR = 1.3

# Default ease factor for new cards
DEFAULT_EASE_FACTOR = 2.5

# Default interval for new cards (in days)
DEFAULT_INTERVAL = 0

# Rating constants
RATING_AGAIN = 0
RATING_HARD = 1
RATING_GOOD = 2
RATING_EASY = 3


@dataclass
class SM2Result:
    """Result of SM-2 algorithm calculation."""

    ease_factor: float
    interval_days: int
    due_at: datetime


def calculate_sm2(
    rating: int,
    current_ease_factor: float,
    current_interval_days: int,
    now: datetime | None = None,
) -> SM2Result:
    """Calculate the next review parameters using SM-2 algorithm.

    Args:
        rating: User's rating of recall quality (0-3)
            0 = again (complete failure, reset)
            1 = hard (correct with difficulty)
            2 = good (correct with some effort)
            3 = easy (perfect recall)
        current_ease_factor: Current ease factor (minimum 1.3)
        current_interval_days: Current interval in days (0 for new cards)
        now: Current timestamp (defaults to UTC now)

    Returns:
        SM2Result with new ease_factor, interval_days, and due_at

    Raises:
        ValueError: If rating is not in range 0-3
    """
    if rating not in (RATING_AGAIN, RATING_HARD, RATING_GOOD, RATING_EASY):
        raise ValueError(f"Rating must be 0-3, got {rating}")

    if now is None:
        now = datetime.now(timezone.utc)

    ease_factor = current_ease_factor
    interval_days = current_interval_days

    # For new cards (interval 0), first successful review sets interval to 1
    if interval_days == 0:
        interval_days = 1

    if rating == RATING_AGAIN:
        # Complete failure: reset interval to 1 day, reduce ease factor
        interval_days = 1
        ease_factor = max(MIN_EASE_FACTOR, ease_factor - 0.2)

    elif rating == RATING_HARD:
        # Hard: interval × 1.2, slight ease factor reduction
        interval_days = max(1, int(interval_days * 1.2))
        ease_factor = max(MIN_EASE_FACTOR, ease_factor - 0.15)

    elif rating == RATING_GOOD:
        # Good: interval × ease_factor
        interval_days = max(1, int(interval_days * ease_factor))

    elif rating == RATING_EASY:
        # Easy: interval × ease_factor × 1.3, increase ease factor
        interval_days = max(1, int(interval_days * ease_factor * 1.3))
        ease_factor = ease_factor + 0.15

    # Calculate next due date
    due_at = now + timedelta(days=interval_days)

    return SM2Result(
        ease_factor=round(ease_factor, 2),
        interval_days=interval_days,
        due_at=due_at,
    )


def get_default_card_values() -> tuple[float, int, datetime]:
    """Get default values for a new card.

    Returns:
        Tuple of (ease_factor, interval_days, due_at)
    """
    return (
        DEFAULT_EASE_FACTOR,
        DEFAULT_INTERVAL,
        datetime.now(timezone.utc),
    )
