# local-whisper

Meeting assistant MVP core service for ingesting transcript segments and generating structured notes.

## Quickstart
### 1) Run the local demo
```bash
python -m app.main
```

### 2) Run the HTTP API
```bash
python -m app.main api
```

## Implemented MVP capabilities
- Create and manage meeting sessions
- Ingest ordered transcript segments with speaker/time metadata
- Generate structured notes from transcript:
  - Summary
  - Decisions
  - Action items (owner + due hint extraction)
  - Evidence segment IDs for traceability
- Serve a dependency-free HTTP API for `/health`, meetings, segments, notes, and meeting end

## API endpoints
- `GET /health`
- `POST /meetings`
- `GET /meetings`
- `POST /meetings/{meeting_id}/segments`
- `GET /meetings/{meeting_id}/segments`
- `GET /meetings/{meeting_id}/notes`
- `POST /meetings/{meeting_id}/end`

## Testing
```bash
pytest
```

## Product architecture
- See `docs/meeting-assistant-architecture.md` for the full architecture plan.
