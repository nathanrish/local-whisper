# local-whisper

Meeting assistant MVP core service for ingesting transcript segments and generating structured notes.

## Quickstart
Run the local demo:
```bash
python -m app.main
```

## Implemented MVP capabilities
- Create and manage meeting sessions
- Ingest ordered transcript segments with speaker/time metadata
- Generate structured notes from transcript:
  - Summary
  - Decisions
  - Action items
  - Evidence segment IDs for traceability

## Testing
```bash
pytest
```

## Product architecture
- See `docs/meeting-assistant-architecture.md` for the full architecture plan.
