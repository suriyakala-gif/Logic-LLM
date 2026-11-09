#!/usr/bin/env python3
"""Build the comparison table (Step 2) from your runs and the paper's values.

Reads:
    results/my_results.csv     written by run_reproduction.py
    results/paper_values.csv   YOU fill this in from the paper's results table
Writes:
    results/summary.csv        mean, std, difference and verdict per dataset
    results/table1.tex         ready to \\input{} in the Overleaf report

Difference (%) is relative, as in the instruction sheet's example:
    (yours - paper) / paper * 100      e.g. 89.8 vs 91.2 -> -1.5
Verdict: |diff| <= 2 Reproduced, <= 10 Partly reproduced, else Not reproduced.
(The 10% cut-off for "Partly" is my choice; state it in the report.)
"""
import csv
import math
import os
import statistics

REPRODUCED, PARTLY = 2.0, 10.0


def fnum(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def main():
    runs = {}
    order = []
    with open(os.path.join("results", "my_results.csv")) as f:
        for r in csv.DictReader(f):
            ds = r["dataset"]
            if ds not in runs:
                runs[ds] = {"acc": [], "exe": [], "n": r["n_questions"], "status": []}
                order.append(ds)
            runs[ds]["status"].append(r["status"])
            a, e = fnum(r["accuracy"]), fnum(r["exec_rate"])
            if a is not None:
                runs[ds]["acc"].append(a)
            if e is not None and not math.isnan(e):
                runs[ds]["exe"].append(e)

    paper = {}
    with open(os.path.join("results", "paper_values.csv")) as f:
        for r in csv.DictReader(f):
            paper[r["dataset"]] = (fnum(r["paper_accuracy"]), r.get("note", ""))

    summary, tex_rows = [], []
    for ds in order:
        acc = runs[ds]["acc"]
        mean = statistics.mean(acc) if acc else None
        std = statistics.stdev(acc) if len(acc) > 1 else (0.0 if acc else None)
        exe = statistics.mean(runs[ds]["exe"]) if runs[ds]["exe"] else None
        p, note = paper.get(ds, (None, ""))
        if mean is not None and p:
            diff = (mean - p) / p * 100
            verdict = ("Reproduced" if abs(diff) <= REPRODUCED
                       else "Partly" if abs(diff) <= PARTLY else "Not reproduced")
        else:
            diff = None
            verdict = "Not reproduced (did not run)" if mean is None else "No paper value"
        summary.append(dict(dataset=ds, n_seeds=len(acc), n_questions=runs[ds]["n"],
                            paper_accuracy="" if p is None else p,
                            my_mean="" if mean is None else f"{mean:.2f}",
                            my_std="" if std is None else f"{std:.2f}",
                            exec_rate="" if exe is None else f"{exe:.1f}",
                            diff_pct="" if diff is None else f"{diff:+.1f}",
                            verdict=verdict, note=note))

        mine = "--" if mean is None else f"{mean:.1f} $\\pm$ {std:.1f}"
        tex_rows.append(" & ".join([
            ds.replace("_", r"\_"),
            "--" if p is None else f"{p:.2f}",
            mine,
            "--" if diff is None else f"{diff:+.1f}",
            note.replace("%", r"\%").replace("_", r"\_") or verdict,
        ]) + r" \\")

    with open(os.path.join("results", "summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)

    tex = [r"\begin{table}[t]",
           r"\caption{Logic-LM accuracy (\%): paper vs.\ this reproduction (mean $\pm$ std over 3 seeds).}",
           r"\label{tab:results}",
           r"\centering\footnotesize",
           r"\setlength{\tabcolsep}{3pt}",
           r"\begin{tabular}{lcccp{2.2cm}}",
           r"\hline",
           r"Dataset & Paper & Mine & Diff.\ (\%) & Note \\",
           r"\hline",
           *tex_rows,
           r"\hline",
           r"\end{tabular}",
           r"\end{table}"]
    with open(os.path.join("results", "table1.tex"), "w") as f:
        f.write("\n".join(tex) + "\n")

    for s in summary:
        print(f"{s['dataset']:<17} paper={s['paper_accuracy']!s:>6}  mine={s['my_mean']:>6} "
              f"+/- {s['my_std']:<5} diff={s['diff_pct']:>6}%  exec={s['exec_rate']:>5}  {s['verdict']}")
    print("\nWrote results/summary.csv and results/table1.tex")


if __name__ == "__main__":
    main()
