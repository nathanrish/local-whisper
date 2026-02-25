from app.models import MeetingCreate, TranscriptSegmentCreate
from app.service import MeetingAssistantService


def test_meeting_lifecycle_and_notes() -> None:
    service = MeetingAssistantService()
    meeting = service.create_meeting(MeetingCreate(title="Sprint Planning", participants=["Ava", "Liam"]))

    service.add_segment(
        meeting.id,
        TranscriptSegmentCreate(
            speaker="Ava",
            text="Decision: We will launch beta next Tuesday",
            start_seconds=0,
            end_seconds=6,
        ),
    )
    service.add_segment(
        meeting.id,
        TranscriptSegmentCreate(
            speaker="Liam",
            text="Action: Liam to publish release notes by Friday",
            start_seconds=7,
            end_seconds=13,
        ),
    )

    notes = service.get_notes(meeting.id)
    assert "launch beta" in notes.notes.summary.lower()
    assert len(notes.notes.decisions) == 1
    assert len(notes.notes.action_items) == 1
    assert notes.notes.action_items[0].owner == "Liam"
    assert len(notes.evidence_segment_ids) >= 2

    ended = service.end_meeting(meeting.id)
    assert ended.status == "ended"


def test_validation_errors() -> None:
    service = MeetingAssistantService()
    meeting = service.create_meeting(MeetingCreate(title="Daily"))

    try:
        service.add_segment(
            meeting.id,
            TranscriptSegmentCreate(
                speaker="Ava",
                text="hello",
                start_seconds=10,
                end_seconds=9,
            ),
        )
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "end_seconds" in str(exc)
