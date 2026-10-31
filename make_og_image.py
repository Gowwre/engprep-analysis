#!/usr/bin/env python3
"""Create the 1200×630 Open Graph image for the EngPrep analysis report."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
SANS_REGULAR = "/usr/share/fonts/noto/NotoSans-Regular.ttf"
SANS_MEDIUM = "/usr/share/fonts/noto/NotoSans-Medium.ttf"
SANS_BOLD = "/usr/share/fonts/noto/NotoSans-Bold.ttf"

BG = "#F7F2E7"
INK = "#20261F"
MUTED = "#626A5F"
CLAY = "#B0472A"
CLAY_LIGHT = "#F8E6DD"
CREAM = "#FFF8EC"
LINE = "#E2D6C2"

W, H = 1200, 630


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


serif_bold = font("/usr/share/fonts/noto/NotoSerif-Bold.ttf", 64)
serif_bold_small = font("/usr/share/fonts/noto/NotoSerif-Bold.ttf", 52)
serif_number = font("/usr/share/fonts/noto/NotoSerif-Bold.ttf", 148)
serif_score = font("/usr/share/fonts/noto/NotoSerif-Bold.ttf", 44)
sans_regular = font(SANS_REGULAR, 26)
sans_medium = font(SANS_MEDIUM, 22)
sans_bold = font(SANS_BOLD, 19)
sans_small = font(SANS_MEDIUM, 18)

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img, "RGBA")

# Subtle dot grid, matching the report background.
for y in range(0, H, 26):
    for x in range(0, W, 26):
        draw.ellipse((x, y, x + 2, y + 2), fill=(32, 38, 31, 18))

# Top accent.
draw.rectangle((0, 0, W, 10), fill=CLAY)

# Left column.
x = 72
draw.text((x, 58), "ENGPREP  ·  PHÂN TÍCH DỮ LIỆU", font=sans_bold, fill=CLAY, anchor="lt")

title_y = 104
draw.text((x, title_y), "Phân tích 4 đề thi", font=serif_bold, fill=INK, anchor="lt")
draw.text((x, title_y + 78), "Tiếng Anh vào lớp 10", font=serif_bold, fill=INK, anchor="lt")
draw.text((x, title_y + 156), "TP.HCM 2023–2026", font=serif_bold_small, fill=CLAY, anchor="lt")

draw.text(
    (x, 354),
    "160 câu hỏi  ·  4 đề chính thức  ·  90 phút",
    font=sans_regular,
    fill=MUTED,
    anchor="lt",
)

# Three takeaway chips.
chips = [
    ("40 câu", "mỗi đề"),
    ("10 điểm", "thang điểm"),
    ("3 nhóm", "mỗi nhóm 15%"),
]
chip_y = 418
chip_x = x
for big, small in chips:
    width = 214
    draw.rounded_rectangle((chip_x, chip_y, chip_x + width, chip_y + 92), radius=14, fill="#FFFDF8", outline=LINE, width=1)
    draw.text((chip_x + 18, chip_y + 14), big, font=font(SANS_BOLD, 30), fill=CLAY, anchor="lt")
    draw.text((chip_x + 18, chip_y + 56), small, font=sans_small, fill=MUTED, anchor="lt")
    chip_x += width + 12

# URL.
draw.text(
    (x, 574),
    "gowwre.github.io/engprep-analysis",
    font=sans_medium,
    fill=MUTED,
    anchor="lt",
)

# Right panel.
px, py, pw, ph = 790, 78, 338, 474
draw.rounded_rectangle((px + 8, py + 10, px + pw + 8, py + ph + 10), radius=30, fill=(70, 50, 35, 34))
draw.rounded_rectangle((px, py, px + pw, py + ph), radius=30, fill=CLAY)

draw.text((px + 34, py + 32), "CẤU TRÚC ĐỀ", font=sans_bold, fill=CLAY_LIGHT, anchor="lt")
draw.text((px + 30, py + 72), "40", font=serif_number, fill=CREAM, anchor="lt")
draw.text((px + 36, py + 230), "câu hỏi", font=font(SANS_MEDIUM, 32), fill=CLAY_LIGHT, anchor="lt")

draw.line((px + 34, py + 300, px + pw - 34, py + 300), fill=(255, 248, 236, 80), width=2)

draw.text((px + 34, py + 326), "10 điểm", font=serif_score, fill=CREAM, anchor="lt")
draw.text((px + 34, py + 390), "90 phút  ·  7 phần", font=sans_medium, fill=CLAY_LIGHT, anchor="lt")
draw.text((px + 34, py + 430), "Đáp án chính thức 2023–2025", font=sans_small, fill=CLAY_LIGHT, anchor="lt")

img.save(BASE / "og-image.png", optimize=True)
print("wrote", BASE / "og-image.png")
