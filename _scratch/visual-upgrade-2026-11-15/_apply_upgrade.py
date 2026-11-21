#!/usr/bin/env python3
"""Apply Pawtrack visual refinement to artboards under page 2:87 only.
Resumable: skips IDs listed in _inventory/applied_ids.txt
Never touches other pages. apply_variables already done separately.
"""
import json, sys, time, re
from pathlib import Path

sys.path.insert(0, "/Users/macos/Downloads/WorkBuddy/pawtrack/_scratch")
from ardot_mcp import ArdotMcp

FILE = "cocraft://localhost/file/747621516726578?node_id=2%3A87"
INV = Path("/Users/macos/Downloads/WorkBuddy/pawtrack/_scratch/visual-upgrade-2026-11-15/_inventory/nodes.json")
LOGDIR = Path("/Users/macos/Downloads/WorkBuddy/pawtrack/_scratch/visual-upgrade-2026-11-15/_inventory")
APPLIED = LOGDIR / "applied_ids.txt"
FAILS = LOGDIR / "failed_batches.jsonl"

COLOR_MAP = {
    "#F4F6FB": "#F6F3EE",
    "#EAEEF6": "#EFEBE6",
    "#D8DEEA": "#E4DFD8",
    "#B4BCCE": "#C9C2B8",
    "#1C2430": "#2A2622",
    "#5A6472": "#6B645C",
    "#8B93A0": "#746C64",
    "#2B4F8A": "#3E5470",
    "#234274": "#32445C",
    "#E6ECF7": "#E8EDF1",
    "#8A5A12": "#6F6250",
    "#F6EBD3": "#F3EEE6",
    "#E2C98A": "#E4D9C8",
    "#2A7A4A": "#4A635E",
    "#E3F3EA": "#E8EEEC",
    "#C07A1A": "#8F6240",
    "#F8EED8": "#F4EDE4",
    "#C0392B": "#9A5848",
    "#F8E6E4": "#F3E8E4",
    "#D5DCEC": "#E6E4DE",
    "#9AA8C4": "#C2BDB4",
    "#1B2433": "#2A2724",
    "#E8EAEE": "#E8E4DE",
    "#EEE6DA": "#EDE6DC",
    "#6A4A28": "#6A5240",
    "#2A3548": "#3A3531",
    "#9AA4B5": "#A39A90",
    "#C5CDD8": "#D8D2CA",
    "#6B7585": "#7A736C",
    "#222222": "#2A2622",
    "#444444": "#6B645C",
    "#E3E6EE": "#E6E4DE",
    "#D3D3D3": "#E4DFD8",
    "#757575": "#746C64",
}

def hex_of(c):
    r, g, b = c.get("r", 0), c.get("g", 0), c.get("b", 0)
    if r <= 1 and g <= 1 and b <= 1:
        ri, gi, bi = int(round(r * 255)), int(round(g * 255)), int(round(b * 255))
    else:
        ri, gi, bi = int(r), int(g), int(b)
    return f"#{ri:02X}{gi:02X}{bi:02X}"

def rgba(h):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    return {"r": round(r, 2), "g": round(g, 2), "b": round(b, 2)}

def num(v):
    if isinstance(v, (int, float)):
        return float(v)
    return None

def js(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

def map_hex(h):
    return COLOR_MAP.get(h, h)

def load_applied():
    if not APPLIED.exists():
        return set()
    return set(APPLIED.read_text().split())

def mark_applied(ids):
    with APPLIED.open("a") as f:
        for i in ids:
            f.write(i + "\n")

# --------- build ops ---------
inv = json.loads(INV.read_text())
ops = []  # list of (node_id, props_dict)

TEXT_CONTENT = {
    "2:129": "宠迹 · 视觉气质升级（待复核）· 本地 Mock 示意",
    "2:130": "主路径：Mock 登录到添加宠物、绑定设备、位置与轨迹、围栏告警，以及我的与设置底线、管理端登录与设备告警看数。全程须能看出是本地 Mock / 示意，不是真实硬件、微信、短信、支付或地图已接入。Tab 为首页 / 社交 / 报警 / 我的，围栏并入报警设置。会员购买、积分兑换、邀请、社交碰头不是本轮必做。本稿为评审通过后的视觉气质升级，待复核，通过前不要交给前端。Token：Pawtrack Tokens（雾蓝 #3E5470），未使用宠宝树绿。Logo 精稿未放入。未改写宠迹PRD完整版 V2.1。",
    "161:4": "评审通过后的视觉气质升级 · 待复核 · 本地 Mock 示意",
    "161:8": "登录（Mock 预览）到添加宠物、绑定设备、位置与轨迹、围栏告警，以及我的与设置底线、管理端登录与设备告警看数。全程为",
    "161:9": "本地示意，不是真实硬件、微信、短信、支付或地图服务已接入。会员购买、积分兑换、邀请、社交碰头不是本轮必做。Tab 为首页 /",
    "161:10": "社交 / 报警 / 我的，围栏并入报警设置。Token：Pawtrack Tokens（雾蓝 #3E5470）。待复核，通过前勿交前端。Logo 精稿未放入。",
}

# admin banners that still say 待设计评审
for nid, n in inv.items():
    if n.get("type") == "TEXT" and n.get("characters") == "本地 Mock 可预览 · 非真实硬件与第三方 · 待设计评审":
        TEXT_CONTENT[nid] = "本地 Mock 可预览 · 非真实硬件与第三方 · 待复核"

MOCK_TEXTS = {
    "本地 Mock 预览 · 不接真实微信 / 短信 · 非验收",
    "本地 Mock 预览 · 非真实硬件 / 微信 / 短信 / 地图 / 支付",
}
TAB_LABELS = {"首页", "社交", "报警", "我的"}

for nid, n in inv.items():
    props = {}
    typ = n.get("type")

    # fills
    fills = n.get("fills") or []
    new_fills = None
    if fills:
        changed = False
        rebuilt = []
        for f in fills:
            if not isinstance(f, dict):
                rebuilt.append(f)
                continue
            f2 = dict(f)
            if f.get("type") == "GRADIENT_LINEAR" or "GRADIENT" in str(f.get("type") or ""):
                stops = []
                stop_ch = False
                for s in f.get("gradientStops") or []:
                    s2 = dict(s)
                    col = s.get("color") or {}
                    if "r" in col:
                        old = hex_of(col)
                        new = map_hex(old)
                        if old == "#FFFFFF":
                            new = "#FFFCF8"  # skeleton mid
                        if new != old:
                            stop_ch = True
                        c = rgba(new)
                        c["a"] = round(col.get("a", 1) or 1, 2)
                        s2["color"] = c
                    stops.append(s2)
                f2["gradientStops"] = stops
                if stop_ch:
                    changed = True
            elif f.get("color"):
                old = hex_of(f["color"])
                op = f.get("opacity", 1) or 1
                new = old
                if old == "#FFFFFF":
                    if typ == "TEXT":
                        new = "#FFFFFF"
                    elif op < 0.99:
                        new = "#FFFFFF"
                    elif typ == "ELLIPSE" and (num(n.get("width")) or 99) <= 28:
                        new = "#FFFFFF"  # switch knobs
                    else:
                        new = "#FFFCF8"
                else:
                    new = map_hex(old)
                # special opacities
                new_op = op
                if old == "#1C2430" and abs(op - 0.86) < 0.03:
                    new = "#2A2622"
                    new_op = 0.72
                if old == "#2B4F8A" and op < 0.2:
                    new = "#3E5470"
                    new_op = 0.10
                if new != old or abs(new_op - op) > 0.01:
                    changed = True
                f2["color"] = rgba(new)
                # keep a in color if present
                if "a" in (f.get("color") or {}):
                    f2["color"]["a"] = round(f["color"].get("a", 1) or 1, 2)
                f2["opacity"] = new_op
            rebuilt.append(f2)
        if changed:
            new_fills = rebuilt

    # strokes
    strokes = n.get("strokes") or []
    new_strokes = None
    if strokes:
        changed = False
        rebuilt = []
        for f in strokes:
            if not isinstance(f, dict) or not f.get("color"):
                rebuilt.append(f)
                continue
            old = hex_of(f["color"])
            if old == "#000000":
                rebuilt.append(f)
                continue
            new = "#FFFFFF" if old == "#FFFFFF" else map_hex(old)
            f2 = dict(f)
            if new != old:
                changed = True
                f2["color"] = rgba(new)
            rebuilt.append(f2)
        if changed:
            new_strokes = rebuilt

    if new_fills is not None:
        # prefer shorthand when single solid opaque
        if (
            len(new_fills) == 1
            and new_fills[0].get("type") == "SOLID"
            and abs((new_fills[0].get("opacity") or 1) - 1) < 0.01
            and typ != "TEXT"
        ):
            h = None
            col = new_fills[0].get("color")
            if col:
                h = "#{:02X}{:02X}{:02X}".format(
                    int(round(col["r"] * 255)), int(round(col["g"] * 255)), int(round(col["b"] * 255))
                )
            if h:
                props["fill"] = h
            else:
                props["fills"] = new_fills
        else:
            props["fills"] = new_fills

    if new_strokes is not None:
        props["strokes"] = new_strokes

    # radius: 12 -> 14 on larger surfaces only
    cr = n.get("cornerRadius")
    if cr == 12:
        w, h = num(n.get("width")), num(n.get("height"))
        if (w and w >= 80) or (h and h >= 80) or (w and h and min(w, h) >= 48):
            props["cornerRadius"] = 14
    if cr == 10:
        h = num(n.get("height"))
        w = num(n.get("width"))
        # buttons / inputs ~40-44 tall
        if h and 36 <= h <= 48:
            props["cornerRadius"] = 12

    # typography
    if typ == "TEXT":
        fn = n.get("fontName") or {}
        family = fn.get("family") if isinstance(fn, dict) else "PingFang SC"
        style = fn.get("style") if isinstance(fn, dict) else "Regular"
        chars = n.get("characters") or ""
        size = n.get("fontSize")
        new_style = "SemiBold" if style == "Semibold" else style
        new_size = size
        if chars in MOCK_TEXTS and style == "Medium":
            new_style = "Regular"
        if chars in TAB_LABELS and size == 10:
            new_size = 11
        # always pin font if we touch a text node
        text_touched = bool(props) or nid in TEXT_CONTENT or new_style != style or new_size != size
        if nid in TEXT_CONTENT:
            props["content"] = TEXT_CONTENT[nid]
            text_touched = True
        if text_touched:
            props["fontName"] = {"family": "PingFang SC", "style": new_style}
            if new_size:
                props["fontSize"] = new_size

    # 说明 board paper
    if nid == "2:128":
        props["fill"] = "#F6F3EE"
        props["cornerRadius"] = 14

    if props:
        ops.append((nid, props))

print("OPS", len(ops), "of", len(inv), "nodes")

applied = load_applied()
pending = [(i, p) for i, p in ops if i not in applied]
print("PENDING", len(pending), "already", len(applied))

def render_ops(batch):
    lines = []
    for nid, props in batch:
        lines.append(f'U({json.dumps(nid)}, {js(props)})')
    return "\n".join(lines)

def find_text(obj):
    if isinstance(obj, dict):
        if obj.get("type") == "text" and "text" in obj:
            return obj["text"]
        for v in obj.values():
            r = find_text(v)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_text(v)
            if r:
                return r
    return None

c = ArdotMcp()
c.session()

BATCH = 18
ok = 0
fail = 0
i = 0
while i < len(pending):
    batch = pending[i : i + BATCH]
    ops_str = render_ops(batch)
    try:
        res = c.rpc(
            "tools/call",
            {"name": "batch_edit", "arguments": {"fileUrl": FILE, "operations": ops_str}},
            timeout=120,
        )
        text = find_text(res) or json.dumps(res, ensure_ascii=False)
        # success?
        low = text.lower()
        bad = ("error" in low and "success\":false" in low.replace(" ", "")) or "\"success\":false" in low or "HTTP Error" in text
        # also potentialIssues
        if "\"success\":false" in text or (text.startswith("ERR")):
            raise RuntimeError(text[:1500])
        # treat validation failures
        if "rolled back" in low or "failed" in low and "success" not in low:
            raise RuntimeError(text[:1500])
        mark_applied([nid for nid, _ in batch])
        ok += len(batch)
        print(f"OK {ok}/{len(pending)} last={batch[-1][0]} preview={text[:180].replace(chr(10),' ')}")
        i += BATCH
    except Exception as e:
        msg = str(e)
        print("FAIL batch at", i, "size", len(batch), ":", msg[:500])
        FAILS.open("a").write(json.dumps({"i": i, "ids": [b[0] for b in batch], "err": msg[:2000]}, ensure_ascii=False) + "\n")
        # if 502, stop for caller to restart
        if "502" in msg or "Bad Gateway" in msg:
            print("STOP due to 502")
            sys.exit(2)
        # if whole batch failed, try splitting to isolate
        if len(batch) > 1:
            print("  retrying one-by-one")
            for item in batch:
                try:
                    res = c.rpc(
                        "tools/call",
                        {"name": "batch_edit", "arguments": {"fileUrl": FILE, "operations": render_ops([item])}},
                        timeout=90,
                    )
                    text = find_text(res) or ""
                    if "\"success\":false" in text:
                        raise RuntimeError(text[:800])
                    mark_applied([item[0]])
                    ok += 1
                    print("  ok", item[0])
                except Exception as e2:
                    fail += 1
                    print("  fail", item[0], str(e2)[:300])
                    FAILS.open("a").write(json.dumps({"id": item[0], "err": str(e2)[:2000]}, ensure_ascii=False) + "\n")
            i += BATCH
        else:
            fail += 1
            i += BATCH
        # re-session after a failure
        try:
            c = ArdotMcp()
            c.session()
        except Exception as e3:
            if "502" in str(e3):
                print("STOP re-session 502")
                sys.exit(2)
            raise

print("DONE ok", ok, "fail", fail, "pending leftover", max(0, len(pending) - ok - fail))
