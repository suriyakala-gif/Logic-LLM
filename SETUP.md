# Setup

Copy these values from `logs/00_environment.log`.

| Item | Value |
|---|---|
| Date of run | [FILL, e.g. 2026-11-12] |
| Platform | Google Colab ([FILL: CPU / T4 GPU] runtime) |
| Operating system | [FILL, e.g. Ubuntu 22.04.4 LTS] |
| Python | [FILL, e.g. 3.12.x] |
| CPU / RAM | [FILL] |
| GPU | None used. The symbolic solvers run on CPU. |
| Original commit | [FILL: `git log -1 --format=%H` of the authors' last commit before your changes] |
| Package versions | `requirements.txt` (from `pip freeze` after my run); the authors' original file is `requirements_original.txt` |
| Symbolic solvers | Pyke (ProntoQA, ProofWriter), Prover9 (FOLIO), python-constraint (LogicalDeduction), Z3 (AR-LSAT) |
| Seeds | 0, 1, 2 (`random.seed` and `numpy.random.seed`, set before each run) |
| Total runtime | [FILL] min |

## Why seeds matter here

Nothing is trained. The solvers are deterministic, but when a logic program fails to parse or execute, the authors' `random` backup picks a random answer. The seed controls those guesses, so I report mean ± std over 3 seeds.
