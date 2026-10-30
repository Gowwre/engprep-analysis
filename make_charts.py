#!/usr/bin/env python3
"""Generate the charts used in the EngPrep exam analysis report."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch

BASE = Path(__file__).resolve().parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)

BG = "#F7F2E7"
INK = "#2E2A24"
MUTED = "#7A7065"
GRID = "#DED3C2"
PRIMARY = "#B0472A"
SECONDARY = "#D98E5F"
OLIVE = "#6E7B4B"
BLUE = "#3F6C7A"
GOLD = "#C9A227"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.unicode_minus": False,
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "savefig.facecolor": BG,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK,
        "xtick.color": MUTED,
        "ytick.color": INK,
        "text.color": INK,
        "axes.titleweight": "bold",
        "axes.titlesize": 16,
    }
)

summary = json.loads((BASE / "summary.json").read_text(encoding="utf-8"))
passages = list(__import__("csv").DictReader((BASE / "passages.csv").open(encoding="utf-8-sig")))


def clean_axes(ax: plt.Axes, grid_axis: str = "x") -> None:
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8, alpha=0.9)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG / name, dpi=180, bbox_inches="tight", pad_inches=0.28)
    plt.close(fig)
    print("wrote", FIG / name)


def title_block(ax: plt.Axes, title: str, subtitle: str) -> None:
    """Title + subtitle placed above the axes without overlapping each other."""
    ax.text(
        0,
        1.105,
        title,
        transform=ax.transAxes,
        fontsize=16,
        fontweight="bold",
        va="bottom",
        ha="left",
    )
    ax.text(
        0,
        1.035,
        subtitle,
        transform=ax.transAxes,
        fontsize=10,
        color=MUTED,
        va="bottom",
        ha="left",
    )


# ---------------------------------------------------------------- fig 01 sections
sections = [
    ("I", "I. Ngữ âm, ngữ pháp,\ntừ vựng, giao tiếp", 14, 3.5),
    ("II", "II. Biển báo /\nthông báo", 2, 0.5),
    ("III", "III. Cloze test", 6, 1.5),
    ("IV", "IV. Đọc hiểu", 6, 1.5),
    ("V", "V. Word formation", 6, 1.5),
    ("VI", "VI. Sắp xếp câu /\ntừ điển / cụm từ", 2, 0.5),
    ("VII", "VII. Viết lại câu", 4, 1.0),
]
fig, ax = plt.subplots(figsize=(10.5, 5.4))
labels = [s[1] for s in sections]
points = [s[3] for s in sections]
colors = [PRIMARY if s[3] >= 1.5 else SECONDARY for s in sections]
y = np.arange(len(sections))[::-1]
bars = ax.barh(y, points, color=colors, height=0.62, edgecolor="none")
for bar, (_, _, n, p) in zip(bars, sections):
    ax.text(
        p + 0.06,
        bar.get_y() + bar.get_height() / 2,
        f"{n} câu  ·  {p:g} đ  ·  {p/10:.0%}",
        va="center",
        ha="left",
        fontsize=10,
        color=MUTED,
    )
ax.set_yticks(y, labels, fontsize=10.5)
ax.set_xlim(0, 4.5)
ax.set_xlabel("Điểm trên thang 10")
title_block(
    ax,
    "Cấu trúc đề: 40 câu · 10 điểm · 90 phút",
    "Mỗi câu 0,25 điểm. Tỉ lệ này giống nhau ở cả 4 đề.",
)
clean_axes(ax)
save(fig, "fig01_sections.png")

# ---------------------------------------------------------------- fig 02 skills
skill_labels = {
    "Word formation": "Word formation",
    "Cloze": "Cloze test",
    "Reading": "Đọc hiểu",
    "Grammar": "Ngữ pháp (Section I)",
    "Sentence transformation": "Viết lại câu",
    "Vocabulary": "Từ vựng (Section I)",
    "Pronunciation": "Phát âm",
    "Stress": "Trọng âm",
    "Communication": "Giao tiếp",
    "Sign/Notice": "Biển báo / thông báo",
    "Sentence construction": "Sắp xếp / cụm từ",
}
skills = sorted(summary["overall"]["skills"].items(), key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(10.5, 6.0))
y = np.arange(len(skills))
vals = [v for _, v in skills]
cols = [PRIMARY if v >= 23 else (SECONDARY if v >= 8 else "#C9BBA6") for v in vals]
bars = ax.barh(y, vals, color=cols, height=0.62, edgecolor="none")
for bar, (name, v) in zip(bars, skills):
    ax.text(
        v + 0.35,
        bar.get_y() + bar.get_height() / 2,
        f"{v} câu  ·  {v/160:.1%}",
        va="center",
        fontsize=9.5,
        color=MUTED,
    )
ax.set_yticks(y, [skill_labels[n] for n, _ in skills], fontsize=10.5)
ax.set_xlim(0, 30)
ax.set_xlabel("Số câu trên tổng 160 câu (4 đề)")
title_block(
    ax,
    "Nhóm kỹ năng nào chiếm nhiều điểm nhất?",
    "Word formation, cloze và đọc hiểu mỗi nhóm chiếm 15% tổng số câu.",
)
clean_axes(ax)
save(fig, "fig02_skills.png")

# ---------------------------------------------------------------- fig 03 grammar heatmap
exams = ["2023", "2024", "2025", "2026R"]
topic_labels = {
    "preposition": "Giới từ",
    "connector": "Liên từ / connector",
    "tense/verb form": "Thì & dạng động từ",
    "relative clause": "Mệnh đề quan hệ",
    "comparison": "So sánh",
    "verb pattern": "Cấu trúc động từ",
    "wish": "Câu ước (wish)",
    "causative": "Causative (have sb do)",
    "tag question": "Câu hỏi đuôi",
    "determiner": "Từ hạn định",
    "quantifier": "Lượng từ",
}
topics = sorted(
    topic_labels,
    key=lambda t: sum(summary["exams"][e]["grammar_topics"].get(t, 0) for e in exams),
    reverse=True,
)
mat = np.array(
    [[summary["exams"][e]["grammar_topics"].get(t, 0) for e in exams] for t in topics]
)
cmap = LinearSegmentedColormap.from_list("engprep", ["#F7F2E7", "#EBC7AD", "#C96A45", "#8E2F1B"])
fig, ax = plt.subplots(figsize=(8.6, 7.0))
im = ax.imshow(mat, cmap=cmap, aspect="auto", vmin=0, vmax=3)
ax.set_xticks(range(len(exams)), ["2023", "2024", "2025", "2026R"], fontsize=11)
ax.set_yticks(range(len(topics)), [topic_labels[t] for t in topics], fontsize=10.5)
for i in range(len(topics)):
    for j in range(len(exams)):
        v = mat[i, j]
        ax.text(
            j,
            i,
            str(v) if v else "–",
            ha="center",
            va="center",
            fontsize=11.5,
            fontweight="bold" if v else "normal",
            color="white" if v >= 2 else INK,
        )
title_block(
    ax,
    "Chủ điểm ngữ pháp lặp lại qua 4 đề",
    "Đếm trong Section I (câu 5–12) và các chỗ trống ngữ pháp của cloze.",
)
ax.tick_params(length=0)
for side in ax.spines.values():
    side.set_visible(False)
save(fig, "fig03_grammar_heatmap.png")

# ---------------------------------------------------------------- fig 04 answer balance
letters = ["A", "B", "C", "D"]
letter_colors = [PRIMARY, BLUE, GOLD, OLIVE]
counts = {e: summary["exams"][e]["mcq_answers"] for e in exams}
x = np.arange(len(exams))
width = 0.19
fig, ax = plt.subplots(figsize=(10.0, 5.4))
for k, (letter, col) in enumerate(zip(letters, letter_colors)):
    vals = [counts[e].get(letter, 0) for e in exams]
    bars = ax.bar(x + (k - 1.5) * width, vals, width, label=letter, color=col, edgecolor="none")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.12, str(v), ha="center", fontsize=9, color=MUTED)
ax.axhline(6, color=MUTED, linestyle=(0, (4, 4)), linewidth=1)
ax.set_xticks(x, ["2023", "2024", "2025", "2026R"], fontsize=11)
ax.set_ylim(0, 9.2)
ax.set_ylabel("Số đáp án đúng / 24 câu MCQ")
title_block(
    ax,
    "Phân bố đáp án trắc nghiệm theo từng đề",
    "2024 là đáp án chính thức; các đề còn lại là gợi ý. Đường đứt: mức cân bằng 6/24.",
)
ax.legend(ncol=4, frameon=False, loc="upper left", bbox_to_anchor=(0, 0.98))
clean_axes(ax, grid_axis="y")
save(fig, "fig04_answers.png")

# ---------------------------------------------------------------- fig 05 reading load
by_exam = {e: {"cloze": 0, "reading": 0} for e in exams}
for row in passages:
    by_exam[row["exam_id"]][row["kind"]] = int(row["words"])
fig, ax = plt.subplots(figsize=(9.4, 5.2))
x = np.arange(len(exams))
cloze = [by_exam[e]["cloze"] for e in exams]
reading = [by_exam[e]["reading"] for e in exams]
ax.bar(x, cloze, 0.55, label="Cloze", color=SECONDARY, edgecolor="none")
ax.bar(x, reading, 0.55, bottom=cloze, label="Đọc hiểu", color=BLUE, edgecolor="none")
for i, e in enumerate(exams):
    total = cloze[i] + reading[i]
    ax.text(i, total + 9, f"{total} từ", ha="center", fontsize=11, fontweight="bold", color=INK)
    ax.text(i, cloze[i] / 2, str(cloze[i]), ha="center", va="center", fontsize=9.5, color="white")
    ax.text(i, cloze[i] + reading[i] / 2, str(reading[i]), ha="center", va="center", fontsize=9.5, color="white")
ax.set_xticks(x, ["2023", "2024", "2025", "2026R"], fontsize=11)
ax.set_ylim(0, 540)
ax.set_ylabel("Số từ phải đọc")
title_block(
    ax,
    "Khối lượng đọc của mỗi đề",
    "Trung bình ~380 từ/đề; dao động 321–467 từ.",
)
ax.legend(ncol=2, frameon=False, loc="upper right")
clean_axes(ax, grid_axis="y")
save(fig, "fig05_reading_load.png")

# ---------------------------------------------------------------- fig 06 cognitive
cog_order = ["Recognition", "Application", "Inference", "Production"]
cog_labels = {
    "Recognition": "Nhận biết",
    "Application": "Vận dụng",
    "Inference": "Suy luận / đọc hiểu",
    "Production": "Sản sinh (viết)",
}
cog = summary["overall"]["cognitive"]
fig, ax = plt.subplots(figsize=(9.6, 4.6))
vals = [cog.get(k, 0) for k in cog_order]
cols = [GOLD, PRIMARY, BLUE, OLIVE]
bars = ax.barh(np.arange(len(cog_order))[::-1], vals, color=cols, height=0.58, edgecolor="none")
for bar, v in zip(bars, vals):
    ax.text(
        v + 1.2,
        bar.get_y() + bar.get_height() / 2,
        f"{v} câu  ·  {v/160:.0%}",
        va="center",
        fontsize=10,
        color=MUTED,
    )
ax.set_yticks(np.arange(len(cog_order))[::-1], [cog_labels[k] for k in cog_order], fontsize=11)
ax.set_xlim(0, 82)
ax.set_xlabel("Số câu trên tổng 160 câu")
title_block(
    ax,
    "Mức độ nhận thức: đề thi nghiêng về vận dụng",
    "44% số câu yêu cầu áp dụng quy tắc; 25% là suy luận đọc hiểu; 15% là viết.",
)
clean_axes(ax)
save(fig, "fig06_cognitive.png")
