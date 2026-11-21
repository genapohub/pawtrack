# -*- coding: utf-8 -*-
import json, sys
sys.path.insert(0, "/Users/macos/Downloads/WorkBuddy/pawtrack/_scratch/paw-final-rework")
from kit import Client, save_payload

c = Client()
ops = '''
U("190:19", {height: 571})
U("190:45", {y: 515})
c190=C("290:489", "190:19", {x: 16, y: 303, name: "围栏圆心"})
'''
res = c.batch_edit(ops)
dest,_=save_payload("apply-batch3-190-copy", res)
print("SAVED", dest)
if isinstance(res, dict):
    print("success", res.get("success"), "issues", (res.get("data") or {}).get("potentialIssues"))
    for op in (res.get("data") or {}).get("operations") or []:
        node=op.get("node")
        if isinstance(node, dict):
            print(op.get("type"), "id", node.get("id"), "name", node.get("name"), "x", node.get("x"), "y", node.get("y"), "w", node.get("width"), "h", node.get("height"))
        else:
            print(op.get("type"), node, op.get("updated") or "")
else:
    print(str(res)[:2000])
