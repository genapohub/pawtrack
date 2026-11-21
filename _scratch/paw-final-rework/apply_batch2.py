# -*- coding: utf-8 -*-
import json, sys
sys.path.insert(0, "/Users/macos/Downloads/WorkBuddy/pawtrack/_scratch/paw-final-rework")
from kit import Client, save_payload

c = Client()
# shift existing blocks first, grow parent, then insert card
ops = '''
U("189:19", {height: 607})
U("189:45", {y: 468})
U("189:54", {y: 551})
D("199:56")
card=I("189:19", {type: "frame", name: "围栏圆心", x: 16, y: 256, width: 343, height: 196, cornerRadius: 14, fill: "#FFFCF8", layout: "vertical", padding: {left: 15, right: 15, top: 14, bottom: 14}, gap: 8})
head=I(card, {type: "frame", name: "圆心标题行", layout: "horizontal", width: 313, height: 21, primaryAxisAlignItems: "SPACE_BETWEEN", counterAxisAlignItems: "CENTER"})
t1=I(head, {type: "text", content: "围栏圆心", fontSize: 15, fontName: {family: "PingFang SC", style: "Medium"}, fill: "#2A2622", textAutoResize: "WIDTH_AND_HEIGHT"})
st=I(head, {type: "text", content: "未选择", fontSize: 13, fontName: {family: "PingFang SC", style: "Regular"}, fill: "#6B645C", textAutoResize: "WIDTH_AND_HEIGHT"})
map=I(card, {type: "frame", name: "圆心示意地图", width: 313, height: 100, cornerRadius: 10, fill: "#E6E4DE"})
ring=I(map, {type: "ellipse", name: "待选范围", x: 106, y: 20, width: 100, height: 60, fills: [{type: "SOLID", color: {r: 0.243, g: 0.329, b: 0.439}, opacity: 0.12, visible: true, blendMode: "NORMAL"}], strokes: [{type: "SOLID", color: {r: 0.243, g: 0.329, b: 0.439}, opacity: 0.55, visible: true, blendMode: "NORMAL"}], strokeWeight: 1.5})
mh=I(map, {type: "text", content: "点击地图点选圆心", fontSize: 12, fontName: {family: "PingFang SC", style: "Regular"}, fill: "#6B645C", x: 109, y: 42, textAutoResize: "WIDTH_AND_HEIGHT"})
btn=I(card, {type: "frame", name: "在地图上点选圆心", width: 313, height: 36, cornerRadius: 12, fill: "#FFFCF8", strokes: [{type: "SOLID", color: {r: 0.239, g: 0.329, b: 0.439}, opacity: 1, visible: true, blendMode: "NORMAL"}], strokeWeight: 1, layout: "horizontal", primaryAxisAlignItems: "CENTER", counterAxisAlignItems: "CENTER"})
bl=I(btn, {type: "text", content: "在地图上点选圆心", fontSize: 13, fontName: {family: "PingFang SC", style: "Medium"}, fill: "#3E5470", textAlignHorizontal: "CENTER", textAlignVertical: "CENTER", textAutoResize: "WIDTH_AND_HEIGHT"})
'''
res = c.batch_edit(ops)
dest,_=save_payload("apply-batch2-189-center", res)
print("SAVED", dest)
if isinstance(res, dict):
    print("success", res.get("success"), "issues", (res.get("data") or {}).get("potentialIssues"))
    for op in (res.get("data") or {}).get("operations") or []:
        node=op.get("node")
        if isinstance(node, dict):
            print(op.get("type"), node.get("id"), node.get("name"), node.get("characters") or node.get("content"), "y", node.get("y"), "h", node.get("height"), "w", node.get("width"))
        else:
            print(op.get("type"), node, op.get("updated") or "")
else:
    print(str(res)[:2500])
