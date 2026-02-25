from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MeetingCreate:
    title: str
    participants: list[str] = field(default_factory=list)


@dataclass
class Meeting:
    id: str
    title: str
    participants: list[str]
    created_at: datetime
    status: str = "active"


@dataclass
class TranscriptSegmentCreate:
    speaker: str
    text: str
    start_seconds: float
    end_seconds: float


@dataclass
class TranscriptSegment(TranscriptSegmentCreate):
    id: str
    meeting_id: str
    created_at: datetime


@dataclass
class ActionItem:
    task: str
    owner: str | None = None
    due_hint: str | None = None


@dataclass
class MeetingNotes:
    meeting_id: str
    generated_at: datetime
    summary: str
    decisions: list[str]
    action_items: list[ActionItem]


@dataclass
class NotesResponse:
    notes: MeetingNotes
    evidence_segment_ids: list[str]
