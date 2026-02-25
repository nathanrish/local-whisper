from __future__ import annotations

from datetime import datetime, timezone

from app.models import ActionItem, MeetingNotes, NotesResponse, TranscriptSegment


DECISION_PREFIXES = ("decide", "decision:", "agreed", "we will")
ACTION_PREFIXES = ("action:", "todo:", "follow up", "i will", "we should")


def _extract_owner(text: str) -> str | None:
    lowered = text.lower()
    if lowered.startswith("action:"):
        remainder = text.split(":", 1)[1].strip()
        first_token = remainder.split(" ", 1)[0].strip()
        return first_token or None
    if ":" in text:
        candidate = text.split(":", 1)[0].strip()
        if len(candidate.split()) <= 3 and candidate.lower() not in {"action", "todo"}:
            return candidate
    return None


def generate_notes(meeting_id: str, segments: list[TranscriptSegment]) -> NotesResponse:
    if not segments:
        empty = MeetingNotes(
            meeting_id=meeting_id,
            generated_at=datetime.now(timezone.utc),
            summary="No transcript segments captured yet.",
            decisions=[],
            action_items=[],
        )
        return NotesResponse(notes=empty, evidence_segment_ids=[])

    joined = " ".join(s.text for s in segments)
    summary = joined[:500] + ("..." if len(joined) > 500 else "")

    decisions: list[str] = []
    actions: list[ActionItem] = []
    evidence_ids: list[str] = []

    for segment in segments:
        normalized = segment.text.strip().lower()
        if normalized.startswith(DECISION_PREFIXES):
            decisions.append(segment.text)
            evidence_ids.append(segment.id)
        if normalized.startswith(ACTION_PREFIXES):
            actions.append(ActionItem(owner=_extract_owner(segment.text), task=segment.text))
            evidence_ids.append(segment.id)

    notes = MeetingNotes(
        meeting_id=meeting_id,
        generated_at=datetime.now(timezone.utc),
        summary=summary,
        decisions=decisions,
        action_items=actions,
    )
    return NotesResponse(notes=notes, evidence_segment_ids=evidence_ids)
