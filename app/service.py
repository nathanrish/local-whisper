from __future__ import annotations

from app.models import Meeting, MeetingCreate, NotesResponse, TranscriptSegment, TranscriptSegmentCreate
from app.notes import generate_notes
from app.store import InMemoryStore


class MeetingAssistantService:
    """MVP domain service for meeting sessions, transcript ingest, and note generation."""

    def __init__(self, store: InMemoryStore | None = None) -> None:
        self.store = store or InMemoryStore()

    def create_meeting(self, payload: MeetingCreate) -> Meeting:
        if not payload.title.strip():
            raise ValueError("title is required")
        return self.store.create_meeting(payload)

    def list_meetings(self) -> list[Meeting]:
        return self.store.list_meetings()

    def end_meeting(self, meeting_id: str) -> Meeting:
        meeting = self.store.end_meeting(meeting_id)
        if meeting is None:
            raise ValueError("Meeting not found")
        return meeting

    def add_segment(self, meeting_id: str, payload: TranscriptSegmentCreate) -> TranscriptSegment:
        if not payload.speaker.strip():
            raise ValueError("speaker is required")
        if not payload.text.strip():
            raise ValueError("text is required")
        if payload.start_seconds < 0:
            raise ValueError("start_seconds must be >= 0")
        if payload.end_seconds <= payload.start_seconds:
            raise ValueError("end_seconds must be greater than start_seconds")
        segment = self.store.add_segment(meeting_id, payload)
        if segment is None:
            raise ValueError("Meeting not found")
        return segment

    def list_segments(self, meeting_id: str) -> list[TranscriptSegment]:
        segments = self.store.list_segments(meeting_id)
        if segments is None:
            raise ValueError("Meeting not found")
        return segments

    def get_notes(self, meeting_id: str) -> NotesResponse:
        segments = self.list_segments(meeting_id)
        return generate_notes(meeting_id, segments)
