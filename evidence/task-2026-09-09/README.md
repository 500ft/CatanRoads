
# CR-D02 verification — 2026-09-09

Review amendment: [three reproduced path failures, corrections and 58-test
verification](../review-2026-09-09/README.md). The 55-test results below describe
the original day-2 head, not the revised candidate. Importability alone does not
verify the package-install step.

Base: head of `task/priority-one-20260908` (PR #6). Deliverable:
[`analysis/tests/test_runbook_rehearsal.py`](../../analysis/tests/test_runbook_rehearsal.py).
Authoritative status: [SPRINT_TASKS.csv](../../docs/SPRINT_TASKS.csv).

The day-1 gate is fail-closed in-process. What nobody had exercised is the thing the owner will
actually type: the command block in [`docs/PHASE1_RUNBOOK.md`](../../docs/PHASE1_RUNBOOK.md). These
tests parse that block out of the markdown, substitute the four placeholder paths with one-row
synthetic CSVs in the shape the `--metrics` help describes, and run it through a subprocess — so
the document and the CLI are held together by a test rather than by care.

| Check | Observed |
| --- | --- |
| `python -m compileall -q analysis/catanroads analysis/tests` | exit 0 |
| `python -m pytest analysis/tests -q` (as CI) | **55 passed** (7 new) |
| documented command, synthetic manifest + `--evidence-kind synthetic` | `DEVELOPMENT_ONLY`, exit 3 |
| documented command, committed `config/sites.geojson` (verified=false) + `earth-engine-export` | `INCONCLUSIVE`, exit 2 |
| documented command with one export missing | `INCONCLUSIVE`, exit 2, no traceback |
| runbook exit-code table vs `phase1_gate.main` mapping | equal |
| negative control: rename `--metrics` in the runbook | 5 of 7 tests fail |
| negative control: change `2 INCONCLUSIVE` to `4` in the runbook | 1 of 7 tests fail |

Runbook restored byte-identical after the controls. Precondition test names the runbook's own
install step if the CLI is not importable, instead of failing with a JSON decode error.

One limitation is now a tested fact rather than prose: synthetic fixtures declared as
`earth-engine-export` are screened arithmetically (`SCREEN_PASS`/`SCREEN_FAIL`). The CLI cannot
detect mislabelling, exactly as the runbook says; the evidence-kind declaration is the owner's.

Synthetic fixtures only. No Mongolia result, no imagery, no site verification (CR-08 unchanged).
