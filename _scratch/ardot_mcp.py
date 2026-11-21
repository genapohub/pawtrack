#!/usr/bin/env python3
"""Call local Ardot MCP on this Mac: http://127.0.0.1:50501/api/v1/mcp
Usage:
  python3 ardot_mcp.py tools
  python3 ardot_mcp.py resources
  python3 ardot_mcp.py read text://ardot/tool-usage/batch-edit
  python3 ardot_mcp.py call fetch_editor_state includeSchema=false includeGeneralEditInstructions=false
  python3 ardot_mcp.py call locate_available_space width=375 height=812 direction=right
"""
import json, sys, urllib.request

URL = "http://127.0.0.1:50501/api/v1/mcp"

def parse_sse(body: bytes):
    text = body.decode("utf-8", "replace")
    out = []
    for block in text.split("\n\n"):
        for line in block.splitlines():
            if line.startswith("data:"):
                raw = line[5:].strip()
                if raw:
                    out.append(json.loads(raw))
    return out

class ArdotMcp:
    def __init__(self, url=URL):
        self.url = url
        self.n = 0

    def rpc(self, method, params=None, is_notify=False, timeout=60):
        self.n += 1
        if is_notify:
            payload = {"jsonrpc": "2.0", "method": method}
        else:
            payload = {"jsonrpc": "2.0", "id": self.n, "method": method}
        if params is not None:
            payload["params"] = params
        data = json.dumps(payload).encode()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        req = urllib.request.Request(self.url, data=data, method="POST", headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            ctype = r.getheader("Content-Type") or ""
            if not body:
                return {"status": r.status, "empty": True}
            if "event-stream" in ctype or body.startswith(b"event:"):
                msgs = parse_sse(body)
                return msgs[0] if len(msgs) == 1 else {"msgs": msgs}
            return json.loads(body.decode())

    def session(self):
        init = self.rpc(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "grok-bot-ui", "version": "0"},
            },
        )
        try:
            self.rpc("notifications/initialized", {}, is_notify=True)
        except Exception:
            pass
        return init

def parse_arg(raw):
    if "=" not in raw:
        raise SystemExit(f"bad arg: {raw}")
    k, v = raw.split("=", 1)
    if v.lower() == "true":
        return k, True
    if v.lower() == "false":
        return k, False
    if v.startswith("{") or v.startswith("["):
        return k, json.loads(v)
    try:
        if "." in v:
            return k, float(v)
        return k, int(v)
    except ValueError:
        return k, v

def main(argv):
    c = ArdotMcp()
    c.session()
    if not argv or argv[0] in {"tools", "tools/list"}:
        res = c.rpc("tools/list", {})
        tools = res.get("result", {}).get("tools") or res.get("msgs", [{}])[0].get("result", {}).get("tools")
        if not tools and isinstance(res, dict) and "result" in res:
            tools = res["result"].get("tools")
        # unwrap sse wrapper
        if tools is None and "result" in res:
            tools = res["result"].get("tools")
        print(json.dumps(res, ensure_ascii=False, indent=2)[:20000])
        return
    if argv[0] in {"resources", "resources/list"}:
        print(json.dumps(c.rpc("resources/list", {}), ensure_ascii=False, indent=2)[:20000])
        return
    if argv[0] in {"read", "resources/read"}:
        uri = argv[1]
        print(json.dumps(c.rpc("resources/read", {"uri": uri}, timeout=90), ensure_ascii=False, indent=2)[:50000])
        return
    if argv[0] == "call":
        name = argv[1]
        args = {}
        for raw in argv[2:]:
            k, v = parse_arg(raw)
            args[k] = v
        res = c.rpc("tools/call", {"name": name, "arguments": args}, timeout=120)
        print(json.dumps(res, ensure_ascii=False, indent=2)[:50000])
        return
    raise SystemExit("usage: ardot_mcp.py tools|resources|read <uri>|call <tool> k=v...")

if __name__ == "__main__":
    main(sys.argv[1:])
