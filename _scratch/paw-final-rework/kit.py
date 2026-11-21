# -*- coding: utf-8 -*-
import json, sys, os, re
sys.path.insert(0, "/Users/macos/Downloads/WorkBuddy/宠宝树/_scratch")
from ardot_mcp import ArdotMcp

FILE_URL = "cocraft://localhost/file/747621516726578"
PAGE = "2:87"
OUT = "/Users/macos/Downloads/WorkBuddy/pawtrack/_scratch/paw-final-rework"

def unwrap(res):
    if not isinstance(res, dict):
        return res
    if "result" in res:
        res = res["result"]
    content = res.get("content") if isinstance(res, dict) else None
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                texts.append(item.get("text") or "")
        raw = "\n".join(texts)
        try:
            return json.loads(raw)
        except Exception:
            return raw
    return res

class Client:
    def __init__(self):
        self.c = ArdotMcp()
        self.c.session()

    def call(self, name, args, timeout=180):
        res = self.c.rpc("tools/call", {"name": name, "arguments": args}, timeout=timeout)
        return unwrap(res)

    def batch_read(self, **kwargs):
        kwargs.setdefault("fileUrl", FILE_URL)
        return self.call("batch_read", kwargs, timeout=180)

    def capture_layout(self, parentId, maxDepth=8, problemsOnly=False):
        return self.call("capture_layout", {
            "fileUrl": FILE_URL,
            "parentId": parentId,
            "maxDepth": maxDepth,
            "problemsOnly": problemsOnly,
        }, timeout=180)

    def batch_edit(self, operations):
        return self.call("batch_edit", {
            "fileUrl": FILE_URL,
            "operations": operations,
        }, timeout=180)

    def editor_state(self):
        return self.call("fetch_editor_state", {
            "includeSchema": False,
            "includeGeneralEditInstructions": False,
        }, timeout=60)

def jsonl_path_from(obj):
    s = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False)
    m = re.search(r"(/var/folders/[^\s]+\.jsonl)", s)
    return m.group(1) if m else None

def save_payload(name, obj):
    s = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False, indent=2)
    path = jsonl_path_from(s)
    dest = os.path.join(OUT, name)
    if path:
        raw = open(path, encoding="utf-8").read()
        if not dest.endswith(".jsonl"):
            dest = dest + ".jsonl"
        open(dest, "w", encoding="utf-8").write(raw)
        return dest, s
    if not dest.endswith(".json"):
        dest = dest + ".json"
    open(dest, "w", encoding="utf-8").write(s)
    return dest, s
