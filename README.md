# Reproduction of Logic-LM (Findings of EMNLP 2023)

> A fork of the authors' repository, made for a course reproduction assignment.
> The authors' original README is kept as `README_original.md`.

## Overview

- **Paper:** L. Pan, A. Albalak, X. Wang, W. Y. Wang, "Logic-LM: Empowering Large Language Models with Symbolic Solvers for Faithful Logical Reasoning," *Findings of EMNLP 2023*, pp. 3806–3824.
- **DOI:** [10.18653/v1/2023.findings-emnlp.248](https://doi.org/10.18653/v1/2023.findings-emnlp.248)
- **Original code:** <https://github.com/teacherpeterpan/Logic-LLM> (forked at commit `d29f1e5`)
- **What is reproduced:** Table 2 of the paper, the Logic-LM (GPT-4, without self-refinement) accuracy on all five datasets (ProntoQA, ProofWriter, FOLIO, LogicalDeduction, AR-LSAT; dev split). I re-ran the symbolic-solver stage on the authors' saved GPT-4 logic programs with 3 seeds.
- **Outcome: Partly reproduced.** Three of the five datasets match within 0.2%. FOLIO (−8.3%) and AR-LSAT (−23.9%) are lower because the paper fills non-executable programs with chain-of-thought (CoT) answers, which are not in the repository, so random answers had to be used instead. Executable rate and accuracy on executed programs match the paper (Table 3) on all five datasets.

## Setup

Tested on Google Colab (CPU runtime, Python 3.13.18, Ubuntu 24.04.5). No GPU or OpenAI API key is needed. Full details are in `SETUP.md`.

```bash
git clone https://github.com/suriyakala-gif/Logic-LLM.git
cd Logic-LLM
pip install -r requirements.txt     # the 8 solver packages, pinned to the versions I used
# Pyke 1.1.1 needs the 'imp' module that Python 3.12+ removed; zombie-imp restores it in every run:
python -c "import site,os; open(os.path.join(site.getsitepackages()[0],'zombie_imp_autoload.pth'),'w').write('import zombie_imp\n')"
chmod +x models/symbolic_solvers/Prover9/bin/*
```

Do **not** use the authors' original requirements file (`requirements_original.txt`). It contains local conda paths and 2023 version pins that cannot be installed (see `NOTES.md`).

## How to run

The easiest way is to open `reproduce_logiclm.ipynb` in Colab and run it top to bottom. From a terminal at the repo root:

```bash
ulimit -v 4000000     # ~4 GB memory cap: one FOLIO program otherwise exhausts RAM and kills the run
python run_reproduction.py --seeds 0 1 2 --split dev --model gpt-4    # ~6 minutes on Colab CPU
python make_table.py   # -> results/summary.csv, results/table1.tex
python make_figure.py  # -> fig1.pdf
```

`run_reproduction.py` sets `random.seed(seed)` and then runs the authors' `models/logic_inference.py` with the arguments from their README (`--backup_strategy random`), followed by `models/evaluation.py`.

## Expected output

| Dataset | Paper (Table 2) | Mine, mean ± std (3 seeds) | Diff. (%) | Exe_Rate (mine) | Exe_Acc paper / mine |
|---|---|---|---|---|---|
| ProntoQA | 83.20 | 83.20 ± 0.00 | 0.0 | 100.0 | 83.2 / 83.20 |
| ProofWriter | 79.66 | 79.50 ± 0.17 | −0.2 | 99.0 | 79.6 / 79.63 |
| FOLIO | 78.92 | 72.39 ± 2.83 | −8.3 | 78.9–79.9 | 80.4 / 80.37 |
| LogicalDeduction | 87.63 | 87.63 ± 0.00 | 0.0 | 100.0 | 87.6 / 87.63 |
| AR-LSAT | 43.04 | 32.75 ± 2.66 | −23.9 | 32.6 | 60.0 / 60.00 |

Files: `results/my_results.csv` (every dataset × seed), `results/summary.csv`, `results/exec_accuracy_seed0.csv`, `results/raw/` (per-question predictions), `logs/` (full output of every command), `fig1.pdf`.

## Differences from the paper

- **No LLM calls.** I reused the authors' saved GPT-4 logic programs (`outputs/logic_programs`).
- **Backup for non-executable programs:** random answer with 3 seeds (0, 1, 2), not the paper's CoT answers, because `baselines/results/` is not included in the repository. This is the cause of the FOLIO and AR-LSAT gaps.
- **No self-refinement.** This matches Table 2, which reports Logic-LM without self-refinement.
- **Python 3.13 fix (code change):** in `models/symbolic_solvers/csp_solver/csp_solver.py`, `exec(x); locals_ = locals()` became `locals_ = {}; exec(x, globals(), locals_)`. Without it, every LogicalDeduction program returns `None` on Python 3.13 (PEP 667).
- **Memory cap:** `ulimit -v 4000000`. Without it, one FOLIO program exhausts memory and the process is killed.
- **Packages:** `ply`, `func_timeout` and `zombie-imp` added; `scitools-pyke` is the Pyke package name.

## Citation

Please cite the original paper:

```bibtex
@inproceedings{pan-etal-2023-logic,
  title     = {Logic-{LM}: Empowering Large Language Models with Symbolic Solvers for Faithful Logical Reasoning},
  author    = {Pan, Liangming and Albalak, Alon and Wang, Xinyi and Wang, William},
  booktitle = {Findings of the Association for Computational Linguistics: EMNLP 2023},
  pages     = {3806--3824},
  year      = {2023},
  address   = {Singapore},
  publisher = {Association for Computational Linguistics},
  doi       = {10.18653/v1/2023.findings-emnlp.248}
}
```

To cite this reproduction repository, see `CITATION.cff`.
