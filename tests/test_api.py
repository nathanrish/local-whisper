import json
import threading
import urllib.error
import urllib.request
from http import HTTPStatus

from app.api import ApiServer
from app.service import MeetingAssistantService


def _request(method: str, url: str, payload: dict | None = None) -> tuple[int, dict | list]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url=url, method=method, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_http_meeting_flow() -> None:
    server = ApiServer(("127.0.0.1", 0), MeetingAssistantService())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        base = f"http://127.0.0.1:{server.server_port}"

        code, payload = _request("GET", f"{base}/health")
        assert code == HTTPStatus.OK
        assert payload == {"status": "ok"}

        code, meeting = _request("POST", f"{base}/meetings", {"title": "Demo", "participants": ["Ava"]})
        assert code == HTTPStatus.CREATED
        meeting_id = meeting["id"]

        code, _ = _request(
            "POST",
            f"{base}/meetings/{meeting_id}/segments",
            {
                "speaker": "Ava",
                "text": "Action: Ava to share notes by tomorrow",
                "start_seconds": 0,
                "end_seconds": 4,
            },
        )
        assert code == HTTPStatus.CREATED

        code, notes = _request("GET", f"{base}/meetings/{meeting_id}/notes")
        assert code == HTTPStatus.OK
        assert notes["notes"]["action_items"][0]["owner"] == "Ava"
        assert notes["notes"]["action_items"][0]["due_hint"].lower() == "by tomorrow"

        code, ended = _request("POST", f"{base}/meetings/{meeting_id}/end")
        assert code == HTTPStatus.OK
        assert ended["status"] == "ended"
    finally:
        server.shutdown()
        server.server_close()
