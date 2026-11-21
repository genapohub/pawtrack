# -*- coding: utf-8 -*-
import json, sys
sys.path.insert(0, "/Users/macos/Downloads/WorkBuddy/pawtrack/_scratch/paw-final-rework")
from kit import Client, save_payload

c = Client()
ops = '''
U("290:503", {characters: "小区西门附近", fontName: {family: "PingFang SC", style: "Regular"}, fontSize: 13, fills: [{type: "SOLID", color: {r: 0.243, g: 0.329, b: 0.439}, opacity: 1, visible: true, blendMode: "NORMAL"}]})
U("290:505", {characters: "已选圆心", fontName: {family: "PingFang SC", style: "Regular"}, fontSize: 12, fills: [{type: "SOLID", color: {r: 0.419, g: 0.392, b: 0.361}, opacity: 1, visible: true, blendMode: "NORMAL"}], x: 132, y: 78})
U("290:506", {characters: "重新点选圆心", fontName: {family: "PingFang SC", style: "Medium"}, fontSize: 13, textAlignHorizontal: "CENTER", textAlignVertical: "CENTER", textAutoResize: "WIDTH_AND_HEIGHT"})
U("290:501", {name: "重新点选圆心"})
pin=I("290:500", {type: "ellipse", name: "已选圆心针", x: 150, y: 44, width: 12, height: 12, fills: [{type: "SOLID", color: {r: 0.243, g: 0.329, b: 0.439}, opacity: 1, visible: true, blendMode: "NORMAL"}]})
'''
res = c.batch_edit(ops)
dest,_=save_payload("apply-batch4-190-selected", res)
print("SAVED", dest)
if isinstance(res, dict):
    print("success", res.get("success"), "issues", (res.get("data") or {}).get("potentialIssues"))
    for op in (res.get("data") or {}).get("operations") or []:
        node=op.get("node")
        if isinstance(node, dict):
            print(op.get("type"), "id", node.get("id"), "name", node.get("name"), "x", node.get("x"), "y", node.get("y"))
        else:
            print(op.get("type"), node, op.get("updated") or "")
else:
    print(str(res)[:2000])
