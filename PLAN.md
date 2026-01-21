# Plan: Notes-based Cloze Card System

## Goal

Support proper cloze deletions where one note with multiple `{{c1::text}}` markers generates multiple independently-tracked cards.

## Current State

- Cards are standalone entities
- Cloze cards store raw `{{text}}` in front field
- No way to generate multiple cards from one source
- Frontend doesn't render cloze blanks

## Proposed Data Model

### New `notes` table

```sql
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,           -- source text with {{c1::...}} markers
    note_type VARCHAR(20) NOT NULL,  -- 'basic', 'cloze'
    entry_id INT REFERENCES entries(id) ON DELETE SET NULL,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Updated `cards` table

```sql
ALTER TABLE cards ADD COLUMN note_id INT REFERENCES notes(id) ON DELETE CASCADE;
ALTER TABLE cards ADD COLUMN cloze_index INT;  -- which cloze deletion (1, 2, 3...)
```

Cards become "generated" from notes:
- Basic note → 1 card
- Reversible note → 2 cards
- Cloze note → N cards (one per `{{cN::...}}` marker)

## Cloze Syntax

Follow Anki's syntax:
```
{{c1::Berlin}} is the capital of {{c2::Germany}}
```

- `c1`, `c2`, etc. are cloze indices
- Same index can appear multiple times (both blanked together)
- Shorthand `{{text}}` auto-assigns next index

## Implementation Steps

### Phase 1: Database

1. Create `notes` table migration
2. Add `note_id` and `cloze_index` to cards
3. Update SQLAlchemy models
4. Migrate existing cards to have implicit notes (optional, for backwards compat)

### Phase 2: MCP Tools

1. New tool: `create_note` - creates a note and auto-generates cards
   ```
   create_note(
     note_type="cloze",
     content="{{c1::Berlin}} is the capital of {{c2::Germany}}",
     tags=["geography"]
   )
   → Creates 1 note + 2 cards
   ```

2. Update `browse_cards` to optionally show parent note content

3. New tool: `get_note` - retrieve a note with all its cards

4. Keep `create_card` for backwards compat (creates standalone card with no note)

### Phase 3: Card Generation Logic

```python
def generate_cards_from_note(note: Note) -> list[Card]:
    if note.note_type == "basic":
        # Parse "front || back" or similar delimiter
        return [Card(front=..., back=...)]

    elif note.note_type == "cloze":
        # Find all {{cN::text}} patterns
        clozes = parse_cloze_markers(note.content)
        cards = []
        for index, cloze in clozes.items():
            # Generate card where this cloze is blanked
            front = render_cloze_front(note.content, blank_index=index)
            back = cloze.text
            cards.append(Card(
                front=front,
                back=back,
                cloze_index=index,
                note_id=note.id
            ))
        return cards
```

### Phase 4: Frontend

1. Review page: detect cloze cards, render `[...]` for blanks
2. Cards browse: group by note, show cloze index
3. Note viewer: show source content with all clozes highlighted

## API Changes

### New MCP tools

| Tool | Description |
|------|-------------|
| `create_note` | Create note + auto-generate cards |
| `get_note` | Get note with all generated cards |
| `list_notes` | Browse notes |
| `delete_note` | Delete note and all its cards |

### New REST endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /notes` | Create note |
| `GET /notes` | List notes |
| `GET /notes/{id}` | Get note with cards |
| `DELETE /notes/{id}` | Delete note |

## Migration Strategy

1. Add new tables/columns (non-breaking)
2. New tools work alongside old ones
3. Existing cards continue to work (note_id = NULL)
4. Optionally: script to convert standalone cards to notes

## Future Possibilities

With notes as first-class entities:
- Edit note → regenerate cards (preserve scheduling where possible)
- Note templates
- Import/export Anki decks
- Better duplicate detection (compare notes, not cards)
