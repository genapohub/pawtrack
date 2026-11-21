# -*- coding: utf-8 -*-
import json, sys
from pathlib import Path
sys.path.insert(0, "/Users/macos/Downloads/WorkBuddy/pawtrack/_scratch/paw-final-rework")
from kit import Client, save_payload

c = Client()
FRAMES = ["189:1","190:1","179:1","197:1","198:1","199:1","201:1","2:128","161:1"]

def load(path):
    text=Path(path).read_text(encoding="utf-8")
    try:
        return [json.loads(text)]
    except:
        return [json.loads(l) for l in text.splitlines() if l.strip()]

def walk(o, acc, parent=None, origin=None, fid=None):
    if isinstance(o, dict):
        nid=o.get("id")
        typ=o.get("type")
        name=o.get("name") or ""
        b=o.get("bounds") or {}
        if fid is None and nid in FRAMES:
            fid=nid
            origin=b or origin
        if nid==fid:
            origin=b or origin
        if typ=="TEXT" or any(k in name for k in ("胶囊","发送","保存","圆心","围栏","服务","扫码","失败","推送","主路径","入口","本轮","模拟","验收")):
            loc=None
            if b and origin:
                loc=(round(b.get("x",0)-origin["x"],1), round(b.get("y",0)-origin["y"],1),
                     round(b.get("width",0),1), round(b.get("height",0),1))
            acc.append((fid or "?", nid, typ, name, loc, o.get("layoutMode"), parent))
        for ch in o.get("children") or []:
            walk(ch, acc, nid, origin, fid)
        if "data" in o:
            walk(o["data"], acc, nid, origin, fid)
    elif isinstance(o, list):
        for it in o:
            walk(it, acc, parent, origin, fid)

for fid in FRAMES:
    lay=c.capture_layout(fid, maxDepth=8, problemsOnly=False)
    dest,_=save_payload(f"pre-layout-{fid.replace(':','-')}", lay)
    print("SAVED", dest, fid)
    objs=load(dest)
    acc=[]
    walk(objs, acc)
    texts=[a for a in acc if a[2]=="TEXT"]
    print(f"\n======== {fid} TEXTS={len(texts)} ========")
    for a in texts:
        print(f"  {a[1]} local={a[4]} parent={a[6]} {a[3]!r}")
