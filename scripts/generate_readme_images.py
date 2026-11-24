#!/usr/bin/env python3
"""
Regenerate every image used in README.md.

    pip install -r requirements.txt       # + the Graphviz system package
    python scripts/generate_readme_images.py
"""
import os
import subprocess
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "docs", "images")
SCRIPT = os.path.join(ROOT, "src", "health_insurance_eligibility_tree.py")
sys.path.insert(0, os.path.join(ROOT, "src"))

import health_insurance_eligibility_tree as t  # noqa: E402

SURFACE, INK, GRID = "#fcfcfb", "#0b0b0b", "#d9d8d3"
plt.rcParams.update({"figure.facecolor": SURFACE, "savefig.facecolor": SURFACE, "font.family": "DejaVu Sans"})


def render_graph(name, **kwargs):
    tree = t.create_insurance_tree(fontname="DejaVu Sans", **kwargs)
    tree.attr(dpi="170")
    tree.format = "png"
    tree.render(name, directory=OUT, cleanup=True)
    print("wrote", os.path.join("docs", "images", name + ".png"))


def img_table():
    rows = []
    for i, trail in enumerate(t.root_to_leaf_paths(), 1):
        answers = [lbl for _, lbl in trail if lbl]
        leaf = trail[-1][0]
        label = t.NODES[leaf][0]
        rows.append([str(i), answers[0], answers[1] if len(answers) > 1 else "-", answers[2] if len(answers) > 2 else "-",
                     label, "Eligible" if t.is_eligible(leaf) else "Not eligible"])
    head = ["#", "Kenyan citizen?", "Employment status", "Income / age", "Leaf node", "Result"]
    fig, ax = plt.subplots(figsize=(13, 4.4))
    ax.axis("off")
    tb = ax.table(cellText=rows, colLabels=head, cellLoc="center", loc="center",
                  colWidths=[0.04, 0.15, 0.17, 0.14, 0.35, 0.12])
    tb.auto_set_font_size(False)
    tb.set_fontsize(10.5)
    tb.scale(1, 1.9)
    for (r, c), cell in tb.get_celld().items():
        cell.set_edgecolor(GRID)
        if r == 0:
            cell.set_facecolor("#e9f1fb")
            cell.set_text_props(fontweight="bold")
        elif c == 5:
            ok = cell.get_text().get_text() == "Eligible"
            cell.set_facecolor("#e3f5ed" if ok else "#fdecea")
            cell.set_text_props(fontweight="bold", color="#0f7d57" if ok else "#b3302f")
        else:
            cell.set_facecolor(SURFACE)
    ax.set_title("All 7 root-to-leaf paths of the decision tree", fontsize=13.5, fontweight="bold", pad=12)
    fig.savefig(os.path.join(OUT, "04_all_seven_outcomes.png"), dpi=160, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print("wrote docs/images/04_all_seven_outcomes.png")


def img_terminal():
    cmd = "python src/health_insurance_eligibility_tree.py --list-paths"
    out = subprocess.run([sys.executable, "-I", SCRIPT, "--list-paths"], capture_output=True, text=True, check=True).stdout
    lines = [("$ " + cmd, "#0ca30c")] + [(l, "#f0efec") for l in out.rstrip().splitlines()]
    width, h = 13.2, 0.5 + 0.32 * len(lines)
    fig = plt.figure(figsize=(width, h + 0.5))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(0, h + 0.5)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.05, 0.05), width - 0.1, h + 0.4, boxstyle="round,pad=0,rounding_size=0.15",
                                fc="#1a1a19", ec="#3a3a38", lw=1.5))
    for i, c in enumerate(("#e66767", "#c98500", "#0ca30c")):
        ax.add_patch(Circle((0.35 + i * 0.28, h + 0.17), 0.08, fc=c, ec="none"))
    ax.text(width / 2, h + 0.17, "terminal - every decision path", color="#c3c2b7", ha="center", va="center", fontsize=10)
    for i, (txt, col) in enumerate(lines):
        ax.text(0.35, h - 0.12 - i * 0.32, txt, color=col, family="DejaVu Sans Mono", fontsize=10.5, va="center")
    fig.savefig(os.path.join(OUT, "05_terminal_list_paths.png"), dpi=160, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print("wrote docs/images/05_terminal_list_paths.png")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    render_graph("01_eligibility_decision_tree")
    render_graph("02_example_path_informal_income_below_threshold", highlight_leaf="I")
    render_graph("03_example_path_unemployed_over_65", highlight_leaf="L")
    img_table()
    img_terminal()
