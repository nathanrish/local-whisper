from __future__ import annotations

import json
import sys
from dataclasses import asdict

from app.api import run as run_api
from app.models import MeetingCreate, TranscriptSegmentCreate
from app.service import MeetingAssistantService


def demo() -> None:
    service = MeetingAssistantService()
    meeting = service.create_meeting(MeetingCreate(title="Design Review", participants=["Ava", "Liam"]))
    service.add_segment(
        meeting.id,
        TranscriptSegmentCreate(
            speaker="Ava",
            text="Decision: We will ship the first MVP in four weeks",
            start_seconds=0,
            end_seconds=5,
        ),
    )
    service.add_segment(
        meeting.id,
        TranscriptSegmentCreate(
            speaker="Liam",
            text="Action: Liam to draft implementation plan by tomorrow",
            start_seconds=6,
            end_seconds=11,
        ),
    )

    notes = service.get_notes(meeting.id)
    print(json.dumps(asdict(notes), indent=2, default=str))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        run_api()
    else:
        demo()
