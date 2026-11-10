import base64
import json
import logging
import os
import random
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from fastmcp.server.dependencies import get_http_headers

BASE_URL = os.environ.get("PETSTORE_BASE_URL", "http://petstore-api.petstore.svc:8080").rstrip("/")
QUOTE_TTL_SECONDS = 600
CATEGORY_PRICES = {"dogs": 120.0, "cats": 90.0, "birds": 45.0, "fish": 15.0, "lions": 900.0}

quotes: dict[str, dict[str, Any]] = {}


log = logging.getLogger("petstore-mcp")


def token_sub(auth: str) -> str | None:
    try:
        payload = auth.split()[-1].split(".")[1]
        return json.loads(base64.urlsafe_b64decode(payload + "==="))["sub"]
    except Exception:
        return None


def request(method: str, path: str, **kwargs: Any) -> Any:
    headers = {}
    incoming = get_http_headers(include_all=True)
    auth = incoming.get("authorization")
    if auth:
        headers["Authorization"] = auth
    log.warning("call %s %s sub=%s actor=%s", method, path, token_sub(auth or ""), incoming.get("x-agent-actor"))
    response = httpx.request(
        method, f"{BASE_URL}/api/v3{path}", headers=headers, timeout=10.0, **kwargs
    )
    response.raise_for_status()
    return response.json()


def demo_price(pet: dict[str, Any]) -> float:
    category = (pet.get("category") or {}).get("name", "").lower()
    base = CATEGORY_PRICES.get(category, 50.0)
    return base + (int(pet["id"]) % 5) * 5.0


def summarize(pet: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": pet.get("id"),
        "name": pet.get("name"),
        "category": (pet.get("category") or {}).get("name"),
        "status": pet.get("status"),
        "tags": [t.get("name") for t in pet.get("tags", [])],
        "demo_unit_price": demo_price(pet),
    }


def new_quote(pet: dict[str, Any], quantity: int) -> dict[str, Any]:
    now = time.time()
    for qid in [k for k, v in quotes.items() if v["expires_at"] < now]:
        del quotes[qid]
    unit = demo_price(pet)
    quote = {
        "quote_id": uuid.uuid4().hex[:12],
        "pet": summarize(pet),
        "quantity": quantity,
        "unit_price": unit,
        "total": round(unit * quantity, 2),
        "currency": "USD",
        "expires_at": now + QUOTE_TTL_SECONDS,
        "order_id": None,
    }
    quotes[quote["quote_id"]] = quote
    return quote


def order_payload(quote: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": random.randint(1, 10**9),
        "petId": quote["pet"]["id"],
        "quantity": quote["quantity"],
        "shipDate": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
        "status": "placed",
        "complete": False,
    }
