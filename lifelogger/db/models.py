"""SQLAlchemy models for lifelogger."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    Float,
    Integer,
    DateTime,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Entry(Base):
    """Knowledge entry - a piece of information to remember."""

    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    cards: Mapped[list["Card"]] = relationship(back_populates="entry")

    def __repr__(self) -> str:
        return f"<Entry(id={self.id}, content={self.content[:50]}...)>"


class Card(Base):
    """Flashcard for spaced repetition."""

    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    card_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'basic', 'reversible', 'cloze'
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    entry_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("entries.id", ondelete="SET NULL"), nullable=True
    )
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), default=list)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval_days: Mapped[int] = mapped_column(Integer, default=0)
    due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    entry: Mapped[Optional["Entry"]] = relationship(back_populates="cards")
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="card", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Card(id={self.id}, type={self.card_type}, front={self.front[:30]}...)>"


class Review(Base):
    """Review record for a flashcard."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    card_id: Mapped[int] = mapped_column(
        ForeignKey("cards.id", ondelete="CASCADE"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=again, 1=hard, 2=good, 3=easy
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    card: Mapped["Card"] = relationship(back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, card_id={self.card_id}, rating={self.rating})>"
