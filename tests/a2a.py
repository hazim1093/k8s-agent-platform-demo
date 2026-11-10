import os
import uuid

import httpx

BASE_URL = os.environ.get("KAGENT_A2A_URL", "http://localhost:8083/api/a2a/kagent").rstrip("/")
CONFIRM = "adk_request_confirmation"


def _parts(task):
    for msg in task.get("history", []):
        yield from msg.get("parts", [])
    for art in task.get("artifacts", []):
        yield from art.get("parts", [])
    yield from (task.get("status", {}).get("message") or {}).get("parts", [])


def _kind(part):
    meta = part.get("metadata") or {}
    return next((v for k, v in meta.items() if k.endswith("type")), None)


def _short(name):
    return name.rsplit("__", 1)[-1].rsplit("-", 1)[-1] if name else name


class Result:
    def __init__(self, task):
        self.task = task
        self.calls, self.responses, self.requested = [], [], []
        for p in _parts(task):
            if p.get("kind") != "data":
                continue
            data, kind = p.get("data") or {}, _kind(p)
            if kind == "function_call":
                if data.get("name") == CONFIRM:
                    orig = (data.get("args") or {}).get("originalFunctionCall") or {}
                    self.requested.append(orig.get("name"))
                else:
                    self.calls.append(data.get("name"))
            elif kind == "function_response" and data.get("name") != CONFIRM:
                self.responses.append(data.get("name"))
        self.calls = [c for c in self.calls if c]
        self.executed = [r for r in self.responses if r]

    @property
    def tools(self):
        return list(dict.fromkeys(self.calls))

    def ran(self, tool):
        return any(_short(n) == tool for n in self.executed)

    def attempted(self, tool):
        return any(_short(n) == tool for n in self.calls + self.requested)

    @property
    def text(self):
        out = []
        for art in self.task.get("artifacts", []):
            out += [p["text"] for p in art.get("parts", []) if p.get("kind") == "text"]
        if not out:
            for msg in reversed(self.task.get("history", [])):
                if msg.get("role") == "agent":
                    out = [p["text"] for p in msg.get("parts", []) if p.get("kind") == "text"]
                    if out:
                        break
        return "\n".join(out)


def ask(agent, text, context_id=None):
    body = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "kind": "message",
                "role": "user",
                "messageId": str(uuid.uuid4()),
                "parts": [{"kind": "text", "text": text}],
                **({"contextId": context_id} if context_id else {}),
            },
            "configuration": {"blocking": True},
        },
    }
    r = httpx.post(f"{BASE_URL}/{agent}/", json=body, timeout=180)
    r.raise_for_status()
    payload = r.json()
    if "error" in payload:
        raise RuntimeError(payload["error"])
    return Result(payload["result"])
