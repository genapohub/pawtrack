"""生成宠迹小程序 tabBar 图标与地图 marker 图标"""
from PIL import Image, ImageDraw
import os

BASE = os.path.join(os.path.dirname(__file__), "..", "src", "static")
TAB = os.path.join(BASE, "tab")
MARKER = os.path.join(BASE, "marker")
os.makedirs(TAB, exist_ok=True)
os.makedirs(MARKER, exist_ok=True)

GRAY = (154, 160, 166, 255)    # 未选中 #9aa0a6
BLUE = (61, 108, 245, 255)     # 选中 #3d6cf5


def draw_icon(size: int, color, shape: str) -> Image:
    """画 81x81 图标（shape: home/social/alarm/me）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size / 81  # 缩放系数

    if shape == "home":
        # 房子：屋顶三角 + 方形
        d.polygon([(40 * s, 12 * s), (10 * s, 40 * s), (20 * s, 40 * s),
                   (20 * s, 68 * s), (60 * s, 68 * s), (60 * s, 40 * s),
                   (70 * s, 40 * s)], fill=color)
        d.rectangle([(34 * s, 44 * s), (46 * s, 68 * s)], fill=color)
    elif shape == "social":
        # 爪印：一个大圆 + 四个小圆
        r = 12 * s
        d.ellipse([(31 * s, 40 * s), (31 * s + 2 * r, 40 * s + 2 * r)], fill=color)
        for dx, dy in [(-18, -6), (18, -6), (-12, -22), (12, -22)]:
            d.ellipse([(40.5 * s + (dx - 7) * s, 40.5 * s + (dy - 7) * s),
                       (40.5 * s + (dx + 7) * s, 40.5 * s + (dy + 7) * s)], fill=color)
    elif shape == "alarm":
        # 铃铛
        d.ellipse([(24 * s, 18 * s), (56 * s, 56 * s)], fill=color)
        d.rectangle([(22 * s, 52 * s), (58 * s, 62 * s)], fill=color)
        d.ellipse([(34 * s, 62 * s), (46 * s, 72 * s)], fill=color)
        d.ellipse([(24 * s, 14 * s), (32 * s, 22 * s)], fill=color)
        d.ellipse([(48 * s, 14 * s), (56 * s, 22 * s)], fill=color)
    elif shape == "me":
        # 人形：头 + 肩
        d.ellipse([(29 * s, 12 * s), (51 * s, 36 * s)], fill=color)
        d.pieslice([(14 * s, 38 * s), (66 * s, 86 * s)], 180, 360, fill=color)
    return img


def draw_marker(size: int, color, kind: str) -> Image:
    """画地图 marker（猫/狗头像圆形徽章）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size / 96

    # 圆底 + 白色描边
    d.ellipse([(6 * s, 6 * s), (90 * s, 90 * s)], fill=color)
    d.ellipse([(10 * s, 10 * s), (86 * s, 86 * s)], fill=color, outline=(255, 255, 255, 255), width=int(3 * s))

    if kind == "cat":
        # 猫：三角耳 + 脸 + 眼睛 + 胡须
        d.polygon([(22 * s, 30 * s), (32 * s, 12 * s), (42 * s, 26 * s)], fill=color)
        d.polygon([(54 * s, 26 * s), (64 * s, 12 * s), (74 * s, 30 * s)], fill=color)
        d.ellipse([(22 * s, 22 * s), (74 * s, 70 * s)], fill=(255, 255, 255, 255))
        d.ellipse([(36 * s, 42 * s), (44 * s, 50 * s)], fill=(40, 40, 40, 255))
        d.ellipse([(52 * s, 42 * s), (60 * s, 50 * s)], fill=(40, 40, 40, 255))
        d.polygon([(46 * s, 52 * s), (50 * s, 58 * s), (54 * s, 52 * s)], fill=(255, 150, 180, 255))
        d.line([(22 * s, 58 * s), (34 * s, 54 * s)], fill=(40, 40, 40, 255), width=int(2 * s))
        d.line([(74 * s, 58 * s), (62 * s, 54 * s)], fill=(40, 40, 40, 255), width=int(2 * s))
    else:
        # 狗：垂耳 + 脸 + 鼻子
        d.ellipse([(14 * s, 26 * s), (34 * s, 58 * s)], fill=color)
        d.ellipse([(62 * s, 26 * s), (82 * s, 58 * s)], fill=color)
        d.ellipse([(22 * s, 22 * s), (74 * s, 70 * s)], fill=(255, 255, 255, 255))
        d.ellipse([(36 * s, 42 * s), (44 * s, 50 * s)], fill=(40, 40, 40, 255))
        d.ellipse([(52 * s, 42 * s), (60 * s, 50 * s)], fill=(40, 40, 40, 255))
        d.ellipse([(45 * s, 52 * s), (51 * s, 58 * s)], fill=(40, 40, 40, 255))
    return img


# ── tabBar 图标（81x81）─────────────────────────────
for shape in ["home", "social", "alarm", "me"]:
    draw_icon(81, GRAY, shape).save(os.path.join(TAB, f"{shape}.png"))
    draw_icon(81, BLUE, shape).save(os.path.join(TAB, f"{shape}-active.png"))

# ── marker 图标（96x96）─────────────────────────────
CAT = (249, 115, 22, 255)   # 橙色猫
DOG = (61, 108, 245, 255)   # 蓝色狗
draw_marker(96, CAT, "cat").save(os.path.join(MARKER, "marker-cat.png"))
draw_marker(96, DOG, "dog").save(os.path.join(MARKER, "marker-dog.png"))

print("✅ 图标生成完成:")
for f in sorted(os.listdir(TAB)) + sorted(os.listdir(MARKER)):
    print("  ", os.path.join(os.path.relpath(BASE), os.path.basename(os.path.dirname(os.path.join(TAB, f))) , f) if False else f)
