# Reproduction of Logic-LM (Findings of EMNLP 2023)

> This is a fork of the authors' repository, made for a course reproduction assignment.
> The authors' original README is kept as `README_original.md`.

## Overview

- **Paper:** L. Pan, A. Albalak, X. Wang, W. Y. Wang, "Logic-LM: Empowering Large Language Models with Symbolic Solvers for Faithful Logical Reasoning," *Findings of EMNLP 2023*, pp. 3806–3824.
- **DOI:** [10.18653/v1/2023.findings-emnlp.248](https://doi.org/10.18653/v1/2023.findings-emnlp.248)
- **Original code:** <https://github.com/teacherpeterpan/Logic-LLM>
- **What is reproduced:** the Logic-LM (GPT-4) accuracy on [FILL: datasets] from Table [FILL] of the paper, re-running the symbolic-solver stage on the authors' saved GPT-4 logic programs, with 3 seeds.
- **Outcome:** [FILL: Reproduced / Partly reproduced / Not reproduced]. See `results/summary.csv`.

## Setup

Tested on Google Colab, CPU runtime, Python [FILL] (full details in `SETUP.md`). No GPU or OpenAI API key is needed.

```bash
git clone https://github.com/suriyakala-gif/Logic-LLM.git
cd Logic-LLM
pip install -r requirements.txt          # exact versions from my run (pip freeze)
chmod +x models/symbolic_solvers/Prover9/bin/*   # [FILL: confirm path] needed for FOLIO
```

## How to run

The easiest way is to open `reproduce_logiclm.ipynb` in Colab (File → Open notebook → GitHub → paste this repo URL) and run all cells.

From a terminal, at the repo root:

```bash
python run_reproduction.py --seeds 0 1 2 --split dev --model gpt-4   # ~[FILL] min on CPU
python make_table.py      # comparison table -> results/summary.csv, results/table1.tex
python make_figure.py     # Figure 1 -> fig1.pdf
```

`run_reproduction.py` does not change the authors' code. For each dataset and seed it sets `random.seed(seed)`, runs `models/logic_inference.py` with the arguments from the original README (`--backup_strategy random`), then runs `models/evaluation.py`.

## Expected output

| File | Content |
|---|---|
| `results/my_results.csv` | accuracy and executable rate per dataset × seed |
| `results/paper_values.csv` | values copied from the paper |
| `results/summary.csv` | mean ± std, difference (%), verdict |
| `results/raw/*.json` | per-question predictions for every run |
| `logs/` | full output of every command |
| `fig1.pdf` | Figure 1 (paper vs. reproduction) |

Expected values (from my run): [FILL: paste the summary table printed by make_table.py].

## Differences from the paper

- **No LLM calls.** I reused the authors' saved GPT-4 logic programs (`outputs/logic_programs`) instead of calling GPT-4 again.
- **No self-refinement.** `models/self_refinement.py` needs a paid OpenAI API key, so it was not run.
- **Backup strategy:** `random`, run with 3 seeds (0, 1, 2). [FILL: which backup the paper's table uses]
- **Split:** `dev` [FILL: confirm this matches the split the paper reports].
- **Datasets skipped:** [FILL or "none"] — reason: [FILL].
- **Code changes to the authors' files:** [FILL: "none", or list each one; also in NOTES.md].

## Citation

If you use this reproduction, cite the original paper:

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

To cite this reproduction repository itself, see `CITATION.cff`.
