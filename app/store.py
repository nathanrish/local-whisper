from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from app.models import Meeting, MeetingCreate, TranscriptSegment, TranscriptSegmentCreate


@dataclass
class InMemoryStore:
    meetings: dict[str, Meeting] = field(default_factory=dict)
    segments: dict[str, list[TranscriptSegment]] = field(default_factory=lambda: defaultdict(list))

    def create_meeting(self, payload: MeetingCreate) -> Meeting:
        meeting = Meeting(
            id=str(uuid4()),
            title=payload.title,
            participants=payload.participants,
            created_at=datetime.now(timezone.utc),
        )
        self.meetings[meeting.id] = meeting
        return meeting

    def get_meeting(self, meeting_id: str) -> Meeting | None:
        return self.meetings.get(meeting_id)

    def list_meetings(self) -> list[Meeting]:
        return sorted(self.meetings.values(), key=lambda m: m.created_at, reverse=True)

    def end_meeting(self, meeting_id: str) -> Meeting | None:
        meeting = self.get_meeting(meeting_id)
        if meeting is None:
            return None
        meeting.status = "ended"
        return meeting

    def add_segment(self, meeting_id: str, payload: TranscriptSegmentCreate) -> TranscriptSegment | None:
        if meeting_id not in self.meetings:
            return None
        segment = TranscriptSegment(
            id=str(uuid4()),
            meeting_id=meeting_id,
            speaker=payload.speaker,
            text=payload.text,
            start_seconds=payload.start_seconds,
            end_seconds=payload.end_seconds,
            created_at=datetime.now(timezone.utc),
        )
        self.segments[meeting_id].append(segment)
        self.segments[meeting_id].sort(key=lambda s: s.start_seconds)
        return segment

    def list_segments(self, meeting_id: str) -> list[TranscriptSegment] | None:
        if meeting_id not in self.meetings:
            return None
        return self.segments[meeting_id]
