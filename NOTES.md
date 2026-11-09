# Reproduction notes

A log of every problem and every fix attempt. Failed attempts are kept on purpose. Full output is in `logs/`.

## Repository check

| Check | Result |
|---|---|
| README with run instructions | Yes, but it states no Python version, and its output folder name (`outputs/logic_inferences`) differs from the code (`outputs/logic_inference`). |
| Licence | Yes, a LICENSE file is present (kept). |
| Data | Yes, preprocessed in `./data`. |
| Saved LLM outputs | Yes: GPT-4, GPT-3.5 and text-davinci-003 logic programs for all 5 datasets (dev) in `outputs/logic_programs`. |
| CoT baseline answers (`baselines/results/`) | **Missing.** These are needed for the paper's CoT backup. |
| Python / package versions | Not stated. `requirements.txt` is a raw conda freeze. |

## Attempts

### Attempt 1: install with the authors' requirements.txt
- **Ran:** `pip install -r requirements.txt`
- **Error:** `OSError: [Errno 2] No such file or directory: '/croot/certifi_1671487769961/work/certifi'` (`logs/01_install.log`)
- **Reason:** the file lists packages by local paths on the authors' computer (`@ file:///croot/...`).
- **Outcome:** failed

### Attempt 2: remove the local-path lines, keep the pinned versions
- **Ran:** `grep -v "@ file://" requirements.txt > requirements_clean.txt; pip install -r requirements_clean.txt`
- **Error:** `Failed to build 'blis' when getting requirements to build wheel` (`logs/01b_install_attempt2.log`)
- **Reason:** the file is a full 139-package snapshot of a 2023 environment; old pins such as `blis==0.7.10` cannot be built on Python 3.13.
- **Outcome:** failed

### Attempt 3: install only the solver packages
- **Ran:** `pip install z3-solver python-constraint nltk tqdm pyke3`
- **Error:** `No matching distribution found for pyke3`, so pip installed nothing (`logs/01c_install_attempt3.log`)
- **Outcome:** failed

### Attempt 4: install the packages separately
- z3-solver, python-constraint and func_timeout installed. `pip install pyke` also failed.
- The real name, found in the authors' file, is `scitools-pyke==1.1.1` (`logs/01d_install_attempt4.log`).
- **Outcome:** partly worked

### Attempt 5: install scitools-pyke
- **Error:** installed, but `import pyke` failed with `ModuleNotFoundError: No module named 'imp'` (Python 3.12+ removed `imp`).
- **Fix:** `pip install zombie-imp`, plus a `.pth` file that imports it automatically, so the authors' code is unchanged (`logs/01e_install_pyke.log`).
- **Outcome:** worked

### Attempt 6: run the README command for FOLIO
- **Error:** `ModuleNotFoundError: No module named 'ply'` (used by the Prover9 parser; not listed anywhere).
- **Fix:** `pip install ply==3.11` (`logs/01f_install_ply.log`). My run script was also changed to accept both `logic_inference` and `logic_inferences` output folders.
- **Outcome:** worked

### Attempt 7: FOLIO inference killed at example 68/204
- **Error:** `Killed`, exit code 137 (out of memory; `logs/04b_FOLIO_diagnose.log`).
- **Reason:** one FOLIO program makes the solver use all 12 GB of RAM; the code has no memory limit.
- **Fix:** `ulimit -v 4000000`. That program now fails cleanly and gets the backup answer. FOLIO completed 204/204 with exit code 0 (`logs/04c_FOLIO_memlimit.log`).
- **Outcome:** worked

### Attempt 8: LogicalDeduction failed in all 3 seeds
- **Error:** `ValueError: Invalid dataset name: LogicalDeduction` in `models/backup_answer_generation.py` (`logs/inference_LogicalDeduction_seed0.log` from run 1).
- **Reason 1 (repo bug):** `random_backup()` has no case for LogicalDeduction.
- **Reason 2:** the backup was needed at all because 0 of 299 programs executed, which contradicts the paper's 100%.
- **Outcome:** diagnosed, see Attempt 9

### Attempt 9: LogicalDeduction programs return None on Python 3.13
- **Debug run:** the generated CSP program is valid, but `execute_program()` returned `(None, '')`.
- **Reason:** `safe_execute` calls `exec(x)` and then reads `locals()`. From Python 3.13 (PEP 667), `exec()` inside a function no longer writes into `locals()`, so `ans` is silently lost.
- **Fix (code change):** in `models/symbolic_solvers/csp_solver/csp_solver.py`, `exec(x)` + `locals_ = locals()` became `locals_ = {}` + `exec(x, globals(), locals_)`.
- **Outcome:** worked. 299/299 programs executed, accuracy 87.63% (= paper). All 5 datasets were then re-run (`logs/06_reproduction_after_fix.log`); run 1 is kept in `results/my_results_run1_before_fix.csv`.

## Things missing from the paper or repo
- No Python version or usable package list.
- The CoT answers used as the paper's backup (`baselines/results/`) are not released, so FOLIO and AR-LSAT cannot be reproduced exactly without a paid OpenAI API key.
- `random_backup()` does not support LogicalDeduction.
- No memory or time limit around the solvers.
- The README's output folder name does not match the code.

## Observation
The FOLIO executable rate changes between runs (78.92% or 79.90%): one program sits near the solver's time limit, so the solver stage is not fully deterministic.

## Changes to the authors' code
- `models/symbolic_solvers/csp_solver/csp_solver.py`: the 2-line Python 3.13 fix above. No other authors' file was changed.
