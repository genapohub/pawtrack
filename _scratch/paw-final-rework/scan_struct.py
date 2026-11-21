# -*- coding: utf-8 -*-
import json, sys
from pathlib import Path
sys.path.insert(0, "/Users/macos/Downloads/WorkBuddy/pawtrack/_scratch/paw-final-rework")
from kit import Client, save_payload

c = Client()
res=c.batch_read(nodeIds=["189:18","189:19","189:33","190:18","190:19","179:19","179:35","197:16","198:32","201:26"], readDepth=3)
dest,_=save_payload("pre-struct", res)
print("SAVED", dest)

def walk(n, indent=0, maxd=3):
    if not isinstance(n, dict): return
    extra=""
    if n.get("characters"): extra=f" chars={n.get('characters')!r}"
    fills=n.get("fills")
    fill=""
    if fills and isinstance(fills, list) and fills:
        col=fills[0].get("color") if isinstance(fills[0], dict) else None
        if col: fill=f" fill={col}"
    print("  "*indent + f"{n.get('id')} {n.get('type')} {n.get('name')} layout={n.get('layout')} w={n.get('width')} h={n.get('height')} x={n.get('x')} y={n.get('y')} r={n.get('cornerRadius')}{fill}{extra}")
    if indent>=maxd: return
    ch=n.get("children") or []
    if ch=="...":
        print("  "*(indent+1)+"..."); return
    for c in ch if isinstance(ch, list) else []:
        if isinstance(c, dict):
            walk(c, indent+1, maxd)

text=Path(dest).read_text(encoding="utf-8")
try:
    o=json.loads(text); nodes=(o.get("data") or o).get("nodes")
    for n in nodes or []:
        walk(n,0,3); print("---")
except Exception:
    for line in text.splitlines():
        if not line.strip() or line.startswith('{"_meta"'): continue
        try: n=json.loads(line)
        except: continue
        if n.get("id"):
            walk(n,0,3); print("---")
