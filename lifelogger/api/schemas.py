"""Pydantic schemas for the API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Entry schemas
class EntryBase(BaseModel):
    content: str
    tags: list[str] = Field(default_factory=list)


class EntryCreate(EntryBase):
    pass


class EntryResponse(EntryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EntryListResponse(BaseModel):
    entries: list[EntryResponse]
    total: int


# Card schemas
class CardBase(BaseModel):
    card_type: str = Field(..., pattern="^(basic|reversible|cloze)$")
    front: str
    back: Optional[str] = None
    entry_id: Optional[int] = None
    tags: list[str] = Field(default_factory=list)


class CardCreate(CardBase):
    pass


class CardResponse(CardBase):
    id: int
    ease_factor: float
    interval_days: int
    due_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class CardListResponse(BaseModel):
    cards: list[CardResponse]
    total: int


# Review schemas
class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=0, le=3)


class ReviewResponse(BaseModel):
    id: int
    card_id: int
    rating: int
    reviewed_at: datetime

    class Config:
        from_attributes = True


class ReviewResultResponse(BaseModel):
    review: ReviewResponse
    card: CardResponse
    message: str


# Stats schema
class StatsResponse(BaseModel):
    total_entries: int
    total_cards: int
    due_today: int
    reviews_this_week: int
