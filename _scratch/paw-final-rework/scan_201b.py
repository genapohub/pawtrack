# -*- coding: utf-8 -*-
import json, sys
from pathlib import Path
sys.path.insert(0, "/Users/macos/Downloads/WorkBuddy/pawtrack/_scratch/paw-final-rework")
from kit import Client, save_payload

c = Client()
res=c.batch_read(nodeIds=["201:19"], readDepth=6)
dest,_=save_payload("pre-tree-201-19-d6", res)
print("SAVED", dest)

def walk(n, indent=0, maxd=6):
    if not isinstance(n, dict): return
    extra=""
    if n.get("characters"): extra=f" chars={n.get('characters')!r}"
    print("  "*indent + f"{n.get('id')} {n.get('type')} {n.get('name')} w={n.get('width')} h={n.get('height')} x={n.get('x')} y={n.get('y')}{extra}")
    if indent>=maxd: return
    ch=n.get("children") or []
    if ch=="...":
        print("  "*(indent+1)+"..."); return
    for c in ch if isinstance(ch, list) else []:
        if c=="...":
            print("  "*(indent+1)+"..."); continue
        walk(c, indent+1, maxd)

text=Path(dest).read_text(encoding="utf-8")
try:
    o=json.loads(text)
    data=o.get("data") or o
    nodes=data.get("nodes") if isinstance(data, dict) else data
    for n in (nodes if isinstance(nodes, list) else [nodes]):
        walk(n,0,6)
except Exception:
    for line in text.splitlines():
        if not line.strip() or line.startswith('{"_meta"'): continue
        try: n=json.loads(line)
        except: continue
        if n.get("id"):
            walk(n,0,6)
