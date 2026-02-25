from __future__ import annotations

import json
from dataclasses import fields
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from app.models import MeetingCreate, TranscriptSegmentCreate
from app.serialization import to_jsonable
from app.service import MeetingAssistantService


class ApiServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], service: MeetingAssistantService):
        self.service = service
        super().__init__(server_address, ApiHandler)


class ApiHandler(BaseHTTPRequestHandler):
    server: ApiServer

    def _read_json_body(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length == 0:
            return {}
        raw_body = self.rfile.read(content_length)
        return json.loads(raw_body.decode("utf-8"))

    def _write_json(self, status: HTTPStatus, payload: dict[str, Any] | list[Any]) -> None:
        encoded = json.dumps(to_jsonable(payload)).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _write_error(self, status: HTTPStatus, message: str) -> None:
        self._write_json(status, {"error": message})

    def do_GET(self) -> None:  # noqa: N802
        try:
            if self.path == "/health":
                self._write_json(HTTPStatus.OK, {"status": "ok"})
                return

            if self.path == "/meetings":
                self._write_json(HTTPStatus.OK, self.server.service.list_meetings())
                return

            if self.path.startswith("/meetings/") and self.path.endswith("/segments"):
                meeting_id = self.path.split("/")[2]
                segments = self.server.service.list_segments(meeting_id)
                self._write_json(HTTPStatus.OK, segments)
                return

            if self.path.startswith("/meetings/") and self.path.endswith("/notes"):
                meeting_id = self.path.split("/")[2]
                notes = self.server.service.get_notes(meeting_id)
                self._write_json(HTTPStatus.OK, notes)
                return

            self._write_error(HTTPStatus.NOT_FOUND, "Not found")
        except ValueError as exc:
            self._write_error(HTTPStatus.NOT_FOUND, str(exc))

    def do_POST(self) -> None:  # noqa: N802
        try:
            if self.path == "/meetings":
                payload = self._read_json_body()
                title = str(payload.get("title", ""))
                participants = payload.get("participants", [])
                if not isinstance(participants, list):
                    self._write_error(HTTPStatus.BAD_REQUEST, "participants must be a list")
                    return
                meeting = self.server.service.create_meeting(
                    MeetingCreate(title=title, participants=[str(p) for p in participants])
                )
                self._write_json(HTTPStatus.CREATED, meeting)
                return

            if self.path.startswith("/meetings/") and self.path.endswith("/end"):
                meeting_id = self.path.split("/")[2]
                meeting = self.server.service.end_meeting(meeting_id)
                self._write_json(HTTPStatus.OK, meeting)
                return

            if self.path.startswith("/meetings/") and self.path.endswith("/segments"):
                meeting_id = self.path.split("/")[2]
                payload = self._read_json_body()
                missing = [f.name for f in fields(TranscriptSegmentCreate) if f.name not in payload]
                if missing:
                    self._write_error(HTTPStatus.BAD_REQUEST, f"missing fields: {', '.join(missing)}")
                    return
                segment = self.server.service.add_segment(
                    meeting_id,
                    TranscriptSegmentCreate(
                        speaker=str(payload["speaker"]),
                        text=str(payload["text"]),
                        start_seconds=float(payload["start_seconds"]),
                        end_seconds=float(payload["end_seconds"]),
                    ),
                )
                self._write_json(HTTPStatus.CREATED, segment)
                return

            self._write_error(HTTPStatus.NOT_FOUND, "Not found")
        except ValueError as exc:
            status = HTTPStatus.BAD_REQUEST
            if "not found" in str(exc).lower():
                status = HTTPStatus.NOT_FOUND
            self._write_error(status, str(exc))


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    service = MeetingAssistantService()
    server = ApiServer((host, port), service)
    print(f"Meeting assistant API listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
