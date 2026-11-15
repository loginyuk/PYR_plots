"""
Графік до індивідуального завдання з прийняття управлінських рішень:
стиль прийняття рішень Г. Форда за опитувальником GDMS (Скотт і Брюс, 1995).

Скрипт генерує рисунок:
    fig3_1_gdms_profile.png — профіль Форда за п'ятьма стилями GDMS (рис. 3.1).

Вхідні дані — оцінки 25 тверджень із табл. 3.1 (по 5 на стиль, шкала 1–5).
Бал стилю, нейтральний рівень і виділення домінантних стилів розраховуються
в коді, а не задаються вручну.

Запуск:
    pip install matplotlib
    python gdms_profile_chart.py            # збереже PNG у поточну папку
    python gdms_profile_chart.py --out img  # збереже PNG у папку img/
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

# ---------------------------------------------------------------------------
# Дані: оцінки тверджень GDMS за табл. 3.1 (номери тверджень у коментарях)
# ---------------------------------------------------------------------------
SCORES = {
    "Раціональний": [2, 3, 3, 3, 1],  # 1–5
    "Інтуїтивний":  [5, 5, 5, 4, 4],  # 6–10
    "Залежний":     [1, 1, 1, 2, 1],  # 11–15
    "Уникаючий":    [3, 2, 2, 3, 1],  # 16–20
    "Спонтанний":   [4, 4, 5, 4, 4],  # 21–25
}
SCALE_MIN, SCALE_MAX = 1, 5
N_ITEMS = 5
NEUTRAL = N_ITEMS * (SCALE_MIN + SCALE_MAX) / 2  # 5 × 3 = 15 балів
MAX_SCORE = N_ITEMS * SCALE_MAX                  # 25 балів

# ---------------------------------------------------------------------------
# Оформлення
# ---------------------------------------------------------------------------
C_HIGHLIGHT = "#2B7BD9"  # стилі, вищі за нейтральний рівень
C_MUTED = "#C4C4B7"      # решта стилів
C_TEXT = "#1A1A1A"       # заголовок, підписи, значення
C_SUBTLE = "#5C5C5C"     # підзаголовок, підпис нейтрального рівня
C_RULE = "#7A7A7A"       # пунктир нейтрального рівня

FIG_W, FIG_H = 8.5, 3.4                       # дюйми
AX_LEFT, AX_BOTTOM, AX_W, AX_H = 0.268, 0.059, 0.641, 0.709
BAR_HEIGHT = 0.56
CORNER_RADIUS_PT = 3


def pick_font(candidates=("Inter", "Arial", "Liberation Sans", "DejaVu Sans")):
    """Перший доступний шрифт зі списку (усі підтримують кирилицю)."""
    installed = {f.name for f in font_manager.fontManager.ttflist}
    return next((name for name in candidates if name in installed), "DejaVu Sans")


def style_totals(scores):
    """Бал за кожним стилем — сума оцінок його п'яти тверджень."""
    for style, items in scores.items():
        assert len(items) == N_ITEMS, f"{style}: потрібно {N_ITEMS} оцінок"
        assert all(SCALE_MIN <= s <= SCALE_MAX for s in items), f"{style}: оцінка поза шкалою"
    return {style: sum(items) for style, items in scores.items()}


def rounded_barh(ax, y, width, height, color):
    """Горизонтальний стовпець із заокругленими кутами однакового радіуса по x і y."""
    x_per_in = (ax.get_xlim()[1] - ax.get_xlim()[0]) / (FIG_W * AX_W)
    y_per_in = (ax.get_ylim()[1] - ax.get_ylim()[0]) / (FIG_H * AX_H)
    radius = CORNER_RADIUS_PT / 72 * x_per_in
    ax.add_patch(FancyBboxPatch(
        (0, y - height / 2), width, height,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        mutation_aspect=y_per_in / x_per_in,
        facecolor=color, edgecolor="none",
    ))


# ---------------------------------------------------------------------------
# Рисунок
# ---------------------------------------------------------------------------
def fig_gdms_profile(path, totals):
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    dominant = [style.lower() for style, total in ranked if total > NEUTRAL]
    positions = range(len(ranked) - 1, -1, -1)  # найвищий бал — угорі

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    ax = fig.add_axes([AX_LEFT, AX_BOTTOM, AX_W, AX_H])
    ax.set(xlim=(0, MAX_SCORE), ylim=(-0.6, len(ranked)))

    for y, (style, total) in zip(positions, ranked):
        is_dominant = total > NEUTRAL
        rounded_barh(ax, y, total, BAR_HEIGHT, C_HIGHLIGHT if is_dominant else C_MUTED)
        ax.annotate(str(total), (total, y), xytext=(8, 0), textcoords="offset points",
                    va="center_baseline", fontsize=10.5, color=C_TEXT,
                    fontweight="bold" if is_dominant else "normal")

    top = len(ranked) - 1
    ax.plot([NEUTRAL, NEUTRAL], [-0.6, top + 0.5], color=C_RULE, lw=0.9, ls=(0, (4, 3)),
            zorder=3, clip_on=False)
    ax.text(NEUTRAL + 0.3, top + 0.62, f"нейтральний рівень {NEUTRAL:.0f}",
            fontsize=9.5, color=C_SUBTLE, va="bottom", clip_on=False)

    ax.set_yticks(list(positions), [style for style, _ in ranked], fontsize=10.5, color=C_TEXT)
    ax.tick_params(axis="y", length=0, pad=14)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    title = "Профіль Форда за GDMS: домінують " + " і ".join(dominant) + " стилі"
    fig.text(0.033, 0.926, title, fontsize=13, fontweight="bold", color=C_TEXT, va="center")
    fig.text(0.033, 0.838,
             f"Бал за кожним стилем, від {N_ITEMS * SCALE_MIN} до {MAX_SCORE} "
             f"({N_ITEMS} тверджень за шкалою {SCALE_MIN}–{SCALE_MAX})",
             fontsize=10, color=C_SUBTLE, va="center")

    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Профіль стилю прийняття рішень Г. Форда за GDMS")
    parser.add_argument("--out", default=".", help="папка для збереження PNG")
    out = Path(parser.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)

    plt.rcParams["font.family"] = pick_font()

    totals = style_totals(SCORES)
    print(f"Бали за стилями GDMS (нейтральний рівень {NEUTRAL:.0f} з {MAX_SCORE}):")
    for style, total in sorted(totals.items(), key=lambda kv: kv[1], reverse=True):
        mark = "  ← вище нейтрального" if total > NEUTRAL else ""
        print(f"  {style:<13} {total:>2}{mark}")

    fig_gdms_profile(out / "fig3_1_gdms_profile.png", totals)
    print(f"Графік збережено в: {out.resolve()}")


if __name__ == "__main__":
    main()
