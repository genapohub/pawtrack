# -*- coding: utf-8 -*-
import json, sys
from pathlib import Path
sys.path.insert(0, "/Users/macos/Downloads/WorkBuddy/pawtrack/_scratch/paw-final-rework")
from kit import Client, save_payload

c = Client()
st = c.editor_state()
data = st.get("data") or st if isinstance(st, dict) else {}
print("EDITOR currentPage", data.get("currentPage"))

page = c.batch_read(nodeIds=["2:87"], readDepth=1)
dest, raw = save_payload("page-2-87-depth1", page)
print("PAGE SAVED", dest)

def frames_from(dest):
    text=Path(dest).read_text(encoding="utf-8")
    try:
        o=json.loads(text)
    except:
        return []
    data=o.get("data") or o
    nodes=data.get("nodes") if isinstance(data, dict) else data
    acc=[]
    for n in (nodes if isinstance(nodes, list) else [nodes]):
        for ch in n.get("children") or []:
            acc.append((ch.get("id"), ch.get("type"), ch.get("name"), ch.get("x"), ch.get("y"), ch.get("width"), ch.get("height")))
    return acc

frames=frames_from(dest)
print("FRAMES", len(frames))
for f in frames:
    print(f)
