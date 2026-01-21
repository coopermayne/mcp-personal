"""Entry routes for the API."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from lifelogger.db.database import get_db
from lifelogger.db.models import Entry
from lifelogger.api.schemas import EntryCreate, EntryResponse, EntryListResponse

router = APIRouter(prefix="/entries", tags=["entries"])


@router.get("", response_model=EntryListResponse)
def list_entries(
    tags: Optional[list[str]] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List entries with optional tag filter and pagination."""
    query = db.query(Entry)

    if tags:
        for tag in tags:
            query = query.filter(Entry.tags.contains([tag]))

    total = query.count()
    entries = query.order_by(Entry.created_at.desc()).offset(offset).limit(limit).all()

    return EntryListResponse(entries=entries, total=total)


@router.get("/{entry_id}", response_model=EntryResponse)
def get_entry(entry_id: int, db: Session = Depends(get_db)):
    """Get a single entry by ID."""
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.post("", response_model=EntryResponse, status_code=201)
def create_entry(entry: EntryCreate, db: Session = Depends(get_db)):
    """Create a new entry."""
    db_entry = Entry(content=entry.content, tags=entry.tags)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry
