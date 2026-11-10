import sys, json, httpx
url, key = sys.argv[1], sys.argv[2]
H = {"content-type": "application/json", "accept": "application/json, text/event-stream"}
if key != "-": H["Authorization"] = f"Bearer {key}"
def post(body, sid=None):
    h = dict(H); 
    if sid: h["mcp-session-id"] = sid
    r = httpx.post(url, headers=h, json=body, timeout=40)
    txt = r.text
    for line in txt.splitlines():
        if line.startswith("data:"): txt = line[5:].strip()
    return r, txt
r, t = post({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"t","version":"1"}}})
print("init", r.status_code, t[:100])
if r.status_code != 200: sys.exit()
sid = r.headers.get("mcp-session-id")
post({"jsonrpc":"2.0","method":"notifications/initialized"}, sid)
r, t = post({"jsonrpc":"2.0","id":2,"method":"tools/list"}, sid)
try: print("tools", [x["name"] for x in json.loads(t)["result"]["tools"]])
except Exception: print("tools", r.status_code, t[:200])
for name, args in [("get_inventory", {}), ("find_pets_by_status", {"status":"available"})]:
    r, t = post({"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":name,"arguments":args}}, sid)
    print("call", name, r.status_code, t[:140].replace("\n"," "))
