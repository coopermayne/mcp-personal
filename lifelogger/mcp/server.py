"""MCP server for lifelogger - personal knowledge system with spaced repetition."""

import json
from datetime import datetime, timezone
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from lifelogger.db.database import get_session_context
from lifelogger.db.models import Entry, Card, Review
from lifelogger.core.sm2 import calculate_sm2


# Create the MCP server
server = Server("lifelogger")


def entry_to_dict(entry: Entry) -> dict[str, Any]:
    """Convert an Entry to a dictionary."""
    return {
        "id": entry.id,
        "content": entry.content,
        "tags": entry.tags or [],
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
    }


def card_to_dict(card: Card) -> dict[str, Any]:
    """Convert a Card to a dictionary."""
    return {
        "id": card.id,
        "card_type": card.card_type,
        "front": card.front,
        "back": card.back,
        "entry_id": card.entry_id,
        "tags": card.tags or [],
        "ease_factor": card.ease_factor,
        "interval_days": card.interval_days,
        "due_at": card.due_at.isoformat() if card.due_at else None,
        "created_at": card.created_at.isoformat() if card.created_at else None,
    }


def review_to_dict(review: Review) -> dict[str, Any]:
    """Convert a Review to a dictionary."""
    return {
        "id": review.id,
        "card_id": review.card_id,
        "rating": review.rating,
        "reviewed_at": review.reviewed_at.isoformat() if review.reviewed_at else None,
    }


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="log_entry",
            description="Add a new knowledge entry to the system",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content of the entry",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional tags for categorization",
                    },
                },
                "required": ["content"],
            },
        ),
        Tool(
            name="search_entries",
            description="Search entries by text content and/or tags",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text to search for in entry content",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags (entries must have all specified tags)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default 20)",
                        "default": 20,
                    },
                },
            },
        ),
        Tool(
            name="create_card",
            description="Create a new flashcard for spaced repetition",
            inputSchema={
                "type": "object",
                "properties": {
                    "card_type": {
                        "type": "string",
                        "enum": ["basic", "reversible", "cloze"],
                        "description": "Type of card: basic (front->back), reversible (both directions), cloze (fill in blank)",
                    },
                    "front": {
                        "type": "string",
                        "description": "Front of the card (question or text with {{cloze}} markers)",
                    },
                    "back": {
                        "type": "string",
                        "description": "Back of the card (answer). Optional for cloze cards.",
                    },
                    "entry_id": {
                        "type": "integer",
                        "description": "Optional link to source entry",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional tags for the card",
                    },
                },
                "required": ["card_type", "front"],
            },
        ),
        Tool(
            name="get_due_cards",
            description="Get cards that are due for review",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of cards to return (default 10)",
                        "default": 10,
                    },
                },
            },
        ),
        Tool(
            name="record_review",
            description="Record a review for a card and update its schedule using SM-2 algorithm",
            inputSchema={
                "type": "object",
                "properties": {
                    "card_id": {
                        "type": "integer",
                        "description": "ID of the card being reviewed",
                    },
                    "rating": {
                        "type": "integer",
                        "enum": [0, 1, 2, 3],
                        "description": "Rating: 0=again (forgot), 1=hard, 2=good, 3=easy",
                    },
                },
                "required": ["card_id", "rating"],
            },
        ),
        Tool(
            name="browse_cards",
            description="List cards with optional filters for browsing/managing the deck",
            inputSchema={
                "type": "object",
                "properties": {
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags",
                    },
                    "card_type": {
                        "type": "string",
                        "enum": ["basic", "reversible", "cloze"],
                        "description": "Filter by card type",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of cards to return (default 20)",
                        "default": 20,
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of cards to skip for pagination (default 0)",
                        "default": 0,
                    },
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "log_entry":
            result = log_entry(arguments)
        elif name == "search_entries":
            result = search_entries(arguments)
        elif name == "create_card":
            result = create_card(arguments)
        elif name == "get_due_cards":
            result = get_due_cards(arguments)
        elif name == "record_review":
            result = record_review(arguments)
        elif name == "browse_cards":
            result = browse_cards(arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]


def log_entry(arguments: dict[str, Any]) -> dict[str, Any]:
    """Add a new entry."""
    content = arguments.get("content")
    tags = arguments.get("tags", [])

    if not content:
        return {"error": "Content is required"}

    with get_session_context() as session:
        entry = Entry(content=content, tags=tags)
        session.add(entry)
        session.flush()
        return {"entry": entry_to_dict(entry)}


def search_entries(arguments: dict[str, Any]) -> dict[str, Any]:
    """Search entries by text and/or tags."""
    query = arguments.get("query", "")
    tags = arguments.get("tags", [])
    limit = arguments.get("limit", 20)

    with get_session_context() as session:
        q = session.query(Entry)

        # Text search using ILIKE for case-insensitive matching
        if query:
            q = q.filter(Entry.content.ilike(f"%{query}%"))

        # Tag filtering - entries must have all specified tags
        if tags:
            for tag in tags:
                q = q.filter(Entry.tags.contains([tag]))

        q = q.order_by(Entry.created_at.desc()).limit(limit)
        entries = q.all()

        return {"entries": [entry_to_dict(e) for e in entries]}


def create_card(arguments: dict[str, Any]) -> dict[str, Any]:
    """Create a new flashcard."""
    card_type = arguments.get("card_type")
    front = arguments.get("front")
    back = arguments.get("back")
    entry_id = arguments.get("entry_id")
    tags = arguments.get("tags", [])

    if not card_type or card_type not in ("basic", "reversible", "cloze"):
        return {"error": "card_type must be 'basic', 'reversible', or 'cloze'"}

    if not front:
        return {"error": "front is required"}

    # For basic and reversible cards, back is required
    if card_type in ("basic", "reversible") and not back:
        return {"error": f"back is required for {card_type} cards"}

    with get_session_context() as session:
        # Verify entry exists if entry_id provided
        if entry_id:
            entry = session.query(Entry).filter(Entry.id == entry_id).first()
            if not entry:
                return {"error": f"Entry {entry_id} not found"}

        card = Card(
            card_type=card_type,
            front=front,
            back=back,
            entry_id=entry_id,
            tags=tags,
        )
        session.add(card)
        session.flush()

        result = {"card": card_to_dict(card)}

        # For reversible cards, create the reverse card as well
        if card_type == "reversible":
            reverse_card = Card(
                card_type="reversible",
                front=back,
                back=front,
                entry_id=entry_id,
                tags=tags,
            )
            session.add(reverse_card)
            session.flush()
            result["reverse_card"] = card_to_dict(reverse_card)

        return result


def get_due_cards(arguments: dict[str, Any]) -> dict[str, Any]:
    """Get cards due for review."""
    limit = arguments.get("limit", 10)
    now = datetime.now(timezone.utc)

    with get_session_context() as session:
        cards = (
            session.query(Card)
            .filter(Card.due_at <= now)
            .order_by(Card.due_at.asc())
            .limit(limit)
            .all()
        )

        return {
            "due_count": len(cards),
            "cards": [card_to_dict(c) for c in cards],
        }


def record_review(arguments: dict[str, Any]) -> dict[str, Any]:
    """Record a review and update card schedule."""
    card_id = arguments.get("card_id")
    rating = arguments.get("rating")

    if card_id is None:
        return {"error": "card_id is required"}

    if rating not in (0, 1, 2, 3):
        return {"error": "rating must be 0 (again), 1 (hard), 2 (good), or 3 (easy)"}

    now = datetime.now(timezone.utc)

    with get_session_context() as session:
        card = session.query(Card).filter(Card.id == card_id).first()
        if not card:
            return {"error": f"Card {card_id} not found"}

        # Calculate new SM-2 values
        result = calculate_sm2(
            rating=rating,
            current_ease_factor=card.ease_factor,
            current_interval_days=card.interval_days,
            now=now,
        )

        # Update card
        card.ease_factor = result.ease_factor
        card.interval_days = result.interval_days
        card.due_at = result.due_at

        # Create review record
        review = Review(card_id=card_id, rating=rating, reviewed_at=now)
        session.add(review)
        session.flush()

        rating_names = {0: "again", 1: "hard", 2: "good", 3: "easy"}

        return {
            "review": review_to_dict(review),
            "card": card_to_dict(card),
            "message": f"Recorded {rating_names[rating]} ({rating}). Next review in {result.interval_days} day(s).",
        }


def browse_cards(arguments: dict[str, Any]) -> dict[str, Any]:
    """List cards with optional filters."""
    tags = arguments.get("tags", [])
    card_type = arguments.get("card_type")
    limit = arguments.get("limit", 20)
    offset = arguments.get("offset", 0)

    with get_session_context() as session:
        q = session.query(Card)

        # Filter by tags
        if tags:
            for tag in tags:
                q = q.filter(Card.tags.contains([tag]))

        # Filter by card type
        if card_type:
            q = q.filter(Card.card_type == card_type)

        # Get total count before pagination
        total = q.count()

        # Apply pagination
        cards = q.order_by(Card.created_at.desc()).offset(offset).limit(limit).all()

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "cards": [card_to_dict(c) for c in cards],
        }


async def main_async():
    """Run the MCP server (async)."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main():
    """Run the MCP server."""
    import asyncio
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
