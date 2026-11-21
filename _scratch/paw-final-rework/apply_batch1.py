# -*- coding: utf-8 -*-
import json, sys
sys.path.insert(0, "/Users/macos/Downloads/WorkBuddy/pawtrack/_scratch/paw-final-rework")
from kit import Client, save_payload

c = Client()
ops = '''
D("189:44")
U("189:42", {height: 18})
U("179:36", {layoutMode: "HORIZONTAL", primaryAxisAlignItems: "CENTER", counterAxisAlignItems: "CENTER", paddingLeft: 0, paddingRight: 0, paddingTop: 0, paddingBottom: 0, itemSpacing: 0})
U("179:37", {characters: "扫码绑定", fontName: {family: "PingFang SC", style: "Semibold"}, fontSize: 14, textAlignHorizontal: "CENTER", textAlignVertical: "CENTER", textAutoResize: "WIDTH_AND_HEIGHT"})
D("179:38")
U("179:32", {characters: "请输入设备机身的 SN 或激活码。", fontName: {family: "PingFang SC", style: "Regular"}, fontSize: 12, textAutoResize: "WIDTH_AND_HEIGHT"})
D("179:33")
U("197:18", {characters: "告警列表加载失败，请重试。", fontName: {family: "PingFang SC", style: "Regular"}, fontSize: 12, textAutoResize: "WIDTH_AND_HEIGHT"})
D("197:19")
U("198:33", {characters: "这是应用内报警通知。", fontName: {family: "PingFang SC", style: "Regular"}, fontSize: 12})
U("198:34", {characters: "短信、电话通知暂不可用。", fontName: {family: "PingFang SC", style: "Regular"}, fontSize: 12})
D("199:32")
D("199:44")
D("199:50")
U("201:27", {characters: "仅好友 / 全部可见 / 不可见。", fontName: {family: "PingFang SC", style: "Regular"}, fontSize: 12, textAutoResize: "WIDTH_AND_HEIGHT"})
U("201:28", {characters: "附近曝光与地图分享暂不可用。", fontName: {family: "PingFang SC", style: "Regular"}, fontSize: 12, textAutoResize: "WIDTH_AND_HEIGHT"})
U("201:35", {characters: "500 米 / 1 千米 / 3 千米", fontName: {family: "PingFang SC", style: "Regular"}, fontSize: 12})
U("201:51", {characters: "查看", fontName: {family: "PingFang SC", style: "Regular"}, fontSize: 12})
'''
res = c.batch_edit(ops)
dest,_=save_payload("apply-batch1-copy", res)
print("SAVED", dest)
if isinstance(res, dict):
    print("success", res.get("success"), "issues", (res.get("data") or {}).get("potentialIssues"))
    for op in (res.get("data") or {}).get("operations") or []:
        print(op.get("type"), op.get("node") if not isinstance(op.get("node"), dict) else op["node"].get("id"))
else:
    print(str(res)[:2000])
