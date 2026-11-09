#!/usr/bin/env python3
"""Reproduce the Logic-LM accuracy table (Pan et al., Findings of EMNLP 2023).

Runs the authors' symbolic-solver stage (models/logic_inference.py) on the
logic programs THEY generated with GPT-4 (outputs/logic_programs), so no
OpenAI API key and no GPU are needed. Each dataset is run with 3 random seeds,
because programs that fail to execute fall back to a random-guess answer.

The authors' code is NOT modified: each run is launched through a tiny wrapper
that sets the seed and then executes models/logic_inference.py exactly as the
README does.

Usage (from the repo root):
    python run_reproduction.py --seeds 0 1 2 --split dev --model gpt-4

Writes:
    results/my_results.csv           one row per dataset x seed
    results/raw/<...>_seed<k>.json   the authors' per-question output, per seed
    logs/inference_<dataset>_seed<k>.log  full stdout/stderr of every run
"""
import argparse
import csv
import glob
import json
import os
import shutil
import subprocess
import sys
import time

DATASETS = ["ProntoQA", "ProofWriter", "FOLIO", "LogicalDeduction", "AR-LSAT"]

# Sets the seed, then runs the authors' script unchanged, as if called with
# `python models/logic_inference.py ...` (same sys.argv and sys.path[0]).
WRAPPER = r"""
import random, runpy, sys
seed = int(sys.argv[1])
random.seed(seed)
try:
    import numpy as np
    np.random.seed(seed)
except ImportError:
    pass
sys.argv = ["models/logic_inference.py"] + sys.argv[2:]
sys.path.insert(0, "models")
runpy.run_path("models/logic_inference.py", run_name="__main__")
"""


def norm(x):
    """Normalise an answer label so 'A', ' a ', '(A)' compare equal."""
    if x is None:
        return None
    return str(x).strip().strip("()").strip().upper()


def score(path):
    """Accuracy and executable rate from the authors' inference JSON."""
    with open(path) as f:
        records = json.load(f)
    n = len(records)
    correct = sum(norm(r.get("answer")) == norm(r.get("predicted_answer")) for r in records)
    flags = [r.get("flag") for r in records if "flag" in r]
    exec_rate = (sum(fl == "success" for fl in flags) / len(flags) * 100) if flags else float("nan")
    return n, correct / n * 100 if n else float("nan"), exec_rate


def find_output(dataset, split, model, since):
    """The inference file the authors' script just wrote."""
    pattern = os.path.join("outputs", "logic_inferences", f"*{dataset}*{split}*{model}*.json")
    files = [p for p in glob.glob(pattern) if os.path.getmtime(p) >= since]
    return max(files, key=os.path.getmtime) if files else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", nargs="+", default=DATASETS)
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--split", default="dev")
    ap.add_argument("--model", default="gpt-4")
    ap.add_argument("--timeout", type=int, default=1800, help="seconds per run")
    args = ap.parse_args()

    os.makedirs("logs", exist_ok=True)
    os.makedirs(os.path.join("results", "raw"), exist_ok=True)
    out_csv = os.path.join("results", "my_results.csv")
    fields = ["dataset", "split", "model", "seed", "n_questions",
              "accuracy", "exec_rate", "runtime_s", "status"]
    rows = []

    for ds in args.datasets:
        programs = os.path.join("outputs", "logic_programs", f"{ds}_{args.split}_{args.model}.json")
        if not glob.glob(os.path.join("outputs", "logic_programs",
                                      f"*{ds}*{args.split}*{args.model}*")):
            print(f"[skip] {ds}: no saved logic programs at {programs}")
            rows.append(dict(dataset=ds, split=args.split, model=args.model, seed="",
                             n_questions="", accuracy="", exec_rate="", runtime_s="",
                             status="missing_logic_programs"))
            continue
        for seed in args.seeds:
            log_path = os.path.join("logs", f"inference_{ds}_seed{seed}.log")
            cmd = [sys.executable, "-c", WRAPPER, str(seed),
                   "--model_name", args.model,
                   "--dataset_name", ds,
                   "--split", args.split,
                   "--backup_strategy", "random",
                   "--backup_LLM_result_path",
                   f"./baselines/results/CoT_{ds}_{args.split}_{args.model}.json"]
            print(f"[run] {ds} seed={seed}", flush=True)
            t0 = time.time()
            status = "ok"
            with open(log_path, "w") as log:
                log.write("$ " + " ".join(cmd[:2]) + " <wrapper> " + " ".join(cmd[3:]) + "\n\n")
                log.flush()
                try:
                    proc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT,
                                          timeout=args.timeout)
                    if proc.returncode != 0:
                        status = f"exit_{proc.returncode}"
                except subprocess.TimeoutExpired:
                    status = "timeout"
            runtime = time.time() - t0

            out = find_output(ds, args.split, args.model, t0)
            if out is None:
                status = status if status != "ok" else "no_output_file"
                rows.append(dict(dataset=ds, split=args.split, model=args.model, seed=seed,
                                 n_questions="", accuracy="", exec_rate="",
                                 runtime_s=f"{runtime:.1f}", status=status))
                print(f"      -> FAILED ({status}); see {log_path}")
                continue

            keep = os.path.join("results", "raw",
                                f"{ds}_{args.split}_{args.model}_random_seed{seed}.json")
            shutil.copy(out, keep)

            # Cross-check with the authors' own evaluation script; output goes to the log.
            with open(log_path, "a") as log:
                log.write("\n\n===== models/evaluation.py =====\n")
                log.flush()
                subprocess.run([sys.executable, "models/evaluation.py",
                                "--dataset_name", ds, "--model_name", args.model,
                                "--split", args.split, "--backup", "random"],
                               stdout=log, stderr=subprocess.STDOUT)

            n, acc, exe = score(keep)
            rows.append(dict(dataset=ds, split=args.split, model=args.model, seed=seed,
                             n_questions=n, accuracy=f"{acc:.2f}", exec_rate=f"{exe:.2f}",
                             runtime_s=f"{runtime:.1f}", status=status))
            print(f"      -> acc={acc:.2f}%  exec_rate={exe:.2f}%  n={n}  ({runtime:.0f}s)")

    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {out_csv}")


if __name__ == "__main__":
    main()
