#!/usr/bin/env python3
"""Figure 1: Logic-LM accuracy per dataset, paper vs. this reproduction.

Reads results/my_results.csv (your runs) and results/paper_values.csv (the
paper's table) and writes fig1.pdf: vector, 3.5 in wide (one IEEE column),
8-pt text, Okabe-Ito colour-blind-safe colours plus hatching so the two bars
stay distinguishable in grayscale. Error bars = std over seeds.

Run:  python make_figure.py            -> fig1.pdf
      python make_figure.py --gray     -> also fig1_gray.png for the grayscale check
"""
import argparse
import csv
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PAPER_COLOUR = "#0072B2"   # Okabe-Ito blue
MINE_COLOUR = "#E69F00"    # Okabe-Ito orange
SHORT = {"LogicalDeduction": "Logical\nDeduction", "ProofWriter": "Proof\nWriter",
         "ProntoQA": "Pronto\nQA", "FOLIO": "FOLIO", "AR-LSAT": "AR-LSAT"}


def load():
    acc, order = {}, []
    with open(os.path.join("results", "my_results.csv")) as f:
        for r in csv.DictReader(f):
            if r["dataset"] not in acc:
                acc[r["dataset"]] = []
                order.append(r["dataset"])
            try:
                acc[r["dataset"]].append(float(r["accuracy"]))
            except ValueError:
                pass
    paper = {}
    with open(os.path.join("results", "paper_values.csv")) as f:
        for r in csv.DictReader(f):
            try:
                paper[r["dataset"]] = float(r["paper_accuracy"])
            except ValueError:
                pass
    return order, acc, paper


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gray", action="store_true", help="also save a grayscale PNG preview")
    args = ap.parse_args()

    order, acc, paper = load()
    plt.rcParams.update({
        "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 8, "ytick.labelsize": 8,
        "legend.fontsize": 8, "font.family": "serif", "pdf.fonttype": 42,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.6, "hatch.linewidth": 0.6,
    })
    fig, ax = plt.subplots(figsize=(3.45, 2.1))
    w = 0.38
    x = list(range(len(order)))

    p_vals = [paper.get(d, float("nan")) for d in order]
    m_vals = [statistics.mean(acc[d]) if acc[d] else float("nan") for d in order]
    m_err = [statistics.stdev(acc[d]) if len(acc[d]) > 1 else 0 for d in order]

    ax.bar([i - w / 2 for i in x], p_vals, w, label="Paper",
           color=PAPER_COLOUR, edgecolor="black", linewidth=0.5, hatch="")
    ax.bar([i + w / 2 for i in x], m_vals, w, yerr=m_err, capsize=2,
           error_kw={"elinewidth": 0.7, "capthick": 0.7},
           label="Ours (mean $\\pm$ std, 3 seeds)",
           color=MINE_COLOUR, edgecolor="black", linewidth=0.5, hatch="////")

    # Mark datasets that produced no result instead of leaving a silent gap.
    for i, v in enumerate(m_vals):
        if v != v:  # NaN
            ax.text(i + w / 2, 2, "n/a", ha="center", va="bottom", fontsize=7, rotation=90)

    ax.set_xticks(x)
    ax.set_xticklabels([SHORT.get(d, d) for d in order])
    ax.set_xlabel("Dataset (dev split)")
    ax.set_ylabel("Accuracy (%)")
    ax.set_ylim(0, 105)
    ax.yaxis.grid(True, linewidth=0.4, color="#d0d0d0")
    ax.set_axisbelow(True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=2, frameon=False,
              handlelength=1.6, columnspacing=1.0)

    fig.savefig("fig1.pdf", bbox_inches="tight")
    print("Wrote fig1.pdf")
    if args.gray:
        fig.savefig("fig1_preview.png", dpi=200, bbox_inches="tight")
        from PIL import Image
        Image.open("fig1_preview.png").convert("L").save("fig1_gray.png")
        os.remove("fig1_preview.png")
        print("Wrote fig1_gray.png (grayscale check)")


if __name__ == "__main__":
    main()
