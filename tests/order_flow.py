import sys, json, uuid, httpx
agent, token, user_text = sys.argv[1], sys.argv[2], sys.argv[3]
URL = f"http://localhost:8083/api/a2a/kagent/{agent}/"
H = {"content-type": "application/json"}
if token != "-": H["Authorization"] = f"Bearer {token}"
def send(parts, ctx=None, task=None):
    msg = {"kind":"message","role":"user","messageId":str(uuid.uuid4()),"parts":parts}
    if ctx: msg["contextId"] = ctx
    if task: msg["taskId"] = task
    r = httpx.post(URL, headers=H, timeout=180, json={"jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":msg,"configuration":{"blocking":True}}})
    t = r.json()["result"]
    return t
def show(t):
    print("state:", t["status"]["state"])
    for m in t.get("history", [])[-6:]:
        for p in m.get("parts", []):
            if p.get("kind") == "data":
                d = p["data"]; n = d.get("name")
                if n == "adk_request_confirmation":
                    print("  approval requested for", d["args"]["originalFunctionCall"]["name"])
                elif n: print("  ", m["role"], n, str(d.get("args") or d.get("response"))[:130])
    for a in t.get("artifacts", []):
        for p in a["parts"]:
            if p.get("kind") == "text": print("  >", p["text"][:500].replace("\n", "\n    "))
t = send([{"kind":"text","text":user_text}]); show(t)
ctx, tid = t["contextId"], t["id"]
if len(sys.argv) > 4 and sys.argv[4] == "confirm":
    t = send([{"kind":"text","text":"Yes, I confirm this exact quote. Place the order."}], ctx, None); show(t)
    if t["status"]["state"] == "input-required":
        print("-- approving")
        t = send([{"kind":"data","data":{"decision_type":"approve"}}], t["contextId"], t["id"]); show(t)
