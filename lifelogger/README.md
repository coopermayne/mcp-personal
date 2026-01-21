# Lifelogger

A personal knowledge system with spaced repetition, designed to be used via MCP with Claude and optionally via a web interface.

## Features

- **Knowledge Entries**: Store and organize information with tags
- **Flashcards**: Create flashcards (basic, reversible, cloze) for spaced repetition
- **SM-2 Algorithm**: Industry-standard spaced repetition scheduling
- **MCP Integration**: Use with Claude via the Model Context Protocol
- **REST API**: FastAPI-powered web interface

## Tech Stack

- Python 3.11+
- PostgreSQL
- FastAPI (web API)
- MCP Python SDK (Claude integration)
- SQLAlchemy (database ORM)
- Alembic (migrations)

## Setup

### 1. Install Dependencies

```bash
cd lifelogger
pip install -e .
```

### 2. Configure Environment

Copy the example environment file and configure your database:

```bash
cp .env.example .env
```

Edit `.env` and set your PostgreSQL connection string:

```
DATABASE_URL=postgresql://user:password@localhost:5432/lifelogger
```

### 3. Create Database

Create the PostgreSQL database:

```bash
createdb lifelogger
```

### 4. Run Migrations

```bash
alembic upgrade head
```

## Usage

### MCP Server

Run the MCP server for use with Claude:

```bash
python -m lifelogger.mcp.server
```

To configure Claude Desktop to use this server, add to your `claude_desktop_config.json`:

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

### Web API

Start the FastAPI server:

```bash
uvicorn lifelogger.api.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## MCP Tools

The following tools are available via MCP:

| Tool | Description |
|------|-------------|
| `log_entry` | Add a new knowledge entry (content, optional tags) |
| `search_entries` | Search entries by text content and/or tags |
| `create_card` | Create a flashcard (basic/reversible/cloze) |
| `suggest_cards` | Get suggested flashcard formats for an entry |
| `get_due_cards` | Get cards due for review |
| `record_review` | Record a review with rating (0-3) |
| `browse_cards` | List cards with optional filters |

### Review Ratings

- **0 (Again)**: Complete failure - reset interval to 1 day
- **1 (Hard)**: Correct with difficulty - interval × 1.2
- **2 (Good)**: Correct with effort - interval × ease factor
- **3 (Easy)**: Perfect recall - interval × ease factor × 1.3

## API Endpoints

### Entries

- `GET /entries` - List entries (with pagination and tag filter)
- `GET /entries/{id}` - Get single entry
- `POST /entries` - Create entry

### Cards

- `GET /cards` - List cards (with filters)
- `GET /cards/due` - Get due cards
- `POST /cards/{id}/review` - Record a review

### Stats

- `GET /stats` - Basic statistics (total cards, due today, reviews this week)

## Project Structure

```
lifelogger/
├── alembic/                 # Database migrations
│   ├── versions/
│   └── env.py
├── lifelogger/
│   ├── api/                 # FastAPI application
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── routes/
│   │       ├── entries.py
│   │       ├── cards.py
│   │       └── stats.py
│   ├── core/
│   │   └── sm2.py          # SM-2 algorithm
│   ├── db/
│   │   ├── models.py       # SQLAlchemy models
│   │   └── database.py     # Connection management
│   └── mcp/
│       └── server.py       # MCP server
├── pyproject.toml
├── alembic.ini
├── .env.example
└── README.md
```

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Creating New Migrations

After modifying models:

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## License

MIT
