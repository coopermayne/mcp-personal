# Lifelogger

A personal knowledge system with spaced repetition, designed primarily for use with Claude via MCP.

## What is this?

Lifelogger helps you capture and retain knowledge through two core concepts:

- **Entries**: Raw knowledge—facts, notes, concepts, anything you want to remember
- **Cards**: Flashcards for spaced repetition, optionally linked to entries

The idea is to use Claude as your interface. As you chat, you can ask Claude to save interesting facts, create flashcards, and quiz you on what you've learned. Claude decides how to phrase cards and when to create them—the MCP tools just handle the database operations and scheduling.

### Example conversation with Claude

> **You**: I just learned that mass extinction events have happened 5 times in Earth's history, and we might be in the 6th one now caused by humans.
>
> **Claude**: That's a significant fact. Want me to save this and create some flashcards?
>
> **You**: Yeah, save it and make a card
>
> **Claude**: *[calls log_entry, then create_card]*
> Done! I've saved the entry tagged with "science" and "ecology", and created a card:
> - Q: "How many mass extinction events have occurred in Earth's history?"
> - A: "5, with a potential 6th currently caused by humans"

Later:

> **You**: Quiz me on something
>
> **Claude**: *[calls get_due_cards]*
> Here's one: **How many mass extinction events have occurred in Earth's history?**
>
> **You**: 5, and we're in the 6th
>
> **Claude**: Correct! How did that feel—easy, good, hard, or did you forget?
>
> **You**: Good
>
> **Claude**: *[calls record_review with rating=2]*
> Got it. You'll see this card again in 4 days.

## MCP Tools

| Tool | Purpose |
|------|---------|
| `log_entry` | Save knowledge (content, tags) |
| `search_entries` | Find entries by text/tags |
| `create_card` | Make a flashcard (basic/reversible/cloze) |
| `browse_cards` | List/filter existing cards |
| `get_due_cards` | Get cards due for review |
| `record_review` | Record rating (0-3), update schedule |

### Card types

- **basic**: One-way Q→A
- **reversible**: Creates two cards (A→B and B→A)
- **cloze**: Fill-in-the-blank style

### Review ratings

| Rating | Meaning | Effect |
|--------|---------|--------|
| 0 (again) | Forgot completely | Reset to 1 day |
| 1 (hard) | Barely remembered | interval × 1.2 |
| 2 (good) | Remembered with effort | interval × ease factor |
| 3 (easy) | Perfect recall | interval × ease factor × 1.3 |

The scheduling uses the SM-2 algorithm, the same algorithm Anki is based on.

## Setup

### 1. Install

```bash
pip install -e .
```

### 2. Database

Set up PostgreSQL and configure the connection:

```bash
cp .env.example .env
# Edit .env with your DATABASE_URL
```

Run migrations:

```bash
alembic upgrade head
```

### 3. Configure Claude

Add to your Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "lifelogger": {
      "command": "python",
      "args": ["-m", "lifelogger.mcp.server"],
      "env": {
        "DATABASE_URL": "postgresql://user:password@localhost:5432/lifelogger"
      }
    }
  }
}
```

## Web Interface (Optional)

There's also a React frontend for browsing entries/cards and doing reviews outside of Claude.

```bash
# Terminal 1 - Backend
export DATABASE_URL="postgresql://..."
uvicorn lifelogger.api.main:app --port 8000

# Terminal 2 - Frontend
cd frontend && npm install && npm run dev
```

Open http://localhost:5173

## Tech Stack

- Python 3.11+, FastAPI, SQLAlchemy, Alembic
- PostgreSQL
- MCP Python SDK
- React + Vite (frontend)

## Project Structure

```
lifelogger/
├── alembic/              # Database migrations
├── frontend/             # React web UI
├── lifelogger/
│   ├── api/              # FastAPI REST API
│   ├── core/sm2.py       # Spaced repetition algorithm
│   ├── db/               # SQLAlchemy models
│   └── mcp/server.py     # MCP server
└── pyproject.toml
```
