# Setup

Values taken from `logs/00_environment.log`.

| Item | Value |
|---|---|
| Date of run | 2026-11-09 |
| Platform | Google Colab, CPU runtime |
| Operating system | Ubuntu 24.04.5 LTS |
| Python | 3.13.18 |
| CPU / RAM | 2 vCPUs, 12 GiB RAM |
| GPU | None. The symbolic solvers run on CPU. |
| Original code | teacherpeterpan/Logic-LLM, commit `d29f1e5` |
| Package versions | `requirements.txt` (the 8 packages used, from `pip freeze`); full Colab environment in `requirements_full_colab_freeze.txt`; the authors' file is `requirements_original.txt` |
| Symbolic solvers | Pyke (`scitools-pyke` 1.1.1) for ProntoQA and ProofWriter; Prover9 (binary in the repo, via `nltk` 3.9.1) for FOLIO; `python-constraint` 1.4.0 for LogicalDeduction; Z3 (`z3-solver`) for AR-LSAT |
| Seeds | 0, 1, 2 (`random.seed` and `numpy.random.seed`, set before each run) |
| Memory cap | `ulimit -v 4000000` (about 4 GB) |
| Total runtime | about 6 minutes for 5 datasets × 3 seeds |

## Why seeds matter

Nothing is trained. When a logic program cannot be parsed or executed, the `random` backup picks a random answer, and the seed controls that guess. So mean ± std over 3 seeds is reported. ProntoQA and LogicalDeduction execute 100% of programs, so their std is 0.
