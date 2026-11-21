# -*- coding: utf-8 -*-
import json, sys
from pathlib import Path
sys.path.insert(0, "/Users/macos/Downloads/WorkBuddy/pawtrack/_scratch/paw-final-rework")
from kit import Client, save_payload

c = Client()
res=c.batch_read(nodeIds=["290:498"], readDepth=5)
dest,_=save_payload("pre-190-center-290-498", res)
print("SAVED", dest)

def walk(n, indent=0):
    if not isinstance(n, dict): return
    extra=""
    if n.get("characters"): extra=f" chars={n.get('characters')!r}"
    print("  "*indent + f"{n.get('id')} {n.get('type')} {n.get('name')}{extra} w={n.get('width')} h={n.get('height')} x={n.get('x')} y={n.get('y')}")
    for ch in n.get("children") or []:
        if isinstance(ch, dict):
            walk(ch, indent+1)

text=Path(dest).read_text(encoding="utf-8")
try:
    o=json.loads(text)
    nodes=(o.get("data") or o).get("nodes")
    for n in nodes or []:
        walk(n)
except Exception:
    for line in text.splitlines():
        if not line.strip() or line.startswith('{"_meta"'): continue
        try: n=json.loads(line)
        except: continue
        if n.get("id"):
            walk(n)
