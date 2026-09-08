# CR-D01 — Temporal evidence QA

Date: 2026-09-08. Base `b4cee1fcb2d6e0cc62b4c48699fa692e7b774ef9`.
Branch `task/priority-one-20260908`. Candidate identity is the containing PR head.

## Why this task

The prior integrity sprint is implemented; real site verification CR-08 is still
owner-blocked. Before an expensive real export, close the remaining CR-3 audit
requirement: distinguish absent imagery from observed no-change. The existing
script printed source scene counts only to the console and returned a bandless
median for empty annual collections. The intake ignored scene availability.
This is a software preparation task, not completion of CR-08.

## Deliverable and acceptance

- [Annual composites](../../gee/ndvi_change.js) use a fully masked expected-band
  fallback for empty S2 and Dynamic World collections. No zero-reflectance data
  is fabricated and the chosen years, sites and mask thresholds are unchanged.
- CSV exports retain all eight S2 scene counts. The
  [intake](../../analysis/catanroads/phase1_gate.py) requires finite nonnegative
  integers, any early-year support and the existing two-recent-year minimum.
  Missing years are reported; scene availability never replaces pixel coverage.
- [Python regressions](../../analysis/tests/test_temporal_qa.py) exercise negative,
  fractional, nonfinite, boolean, absent and insufficient counts; valid partial
  years; and actual CLI CSV parsing from a temporary consumer directory.
- [Node checks](../../tools/test_temporal_qa.mjs) exercise the source functions
  with a minimal local collection/image double and check export wiring. This is
  branch/schema verification, **not** server execution or pixel-math validation.
- [Runbook](../../docs/PHASE1_RUNBOOK.md) states the new required columns and
  owner runtime procedure. Historical CSVs must be regenerated, not guessed.

## Reproduce

From the repo root with project dependencies installed (local Python 3.11.8,
Node v22.21.0):

```sh
PYTHONPATH=analysis python -c 'import sys, types; sys.modules["readline"] = types.ModuleType("readline"); import pytest; raise SystemExit(pytest.main(["analysis/tests", "-q"]))'
node tools/test_temporal_qa.mjs
node tools/validate_phase1.mjs
python -m compileall -q analysis/catanroads analysis/tests
git diff --check
```

[Recorded outputs](checks.json): baseline 35 passed; new Python tests initially
10 failed / 1 passed, Node empty-year branch failed `requested band absent`.
Final suite: 48 passed. Both Node checks, syntax and whitespace checks passed.
No separate lint/typecheck is configured. Source-path CLI checks are not a fresh
package-install claim. No dependency was added.

## Limits and next action

All fixtures are developer-created synthetic inputs, not independent evaluation.
No Earth Engine runtime, verified Mongolia imagery or road accuracy is claimed.
Scene counts are AOI/date/cloud-filter counts, not usable-pixel counts or independent
sampling units. Source authenticity remains a human review requirement. An
all-masked collection with nonzero scenes still depends on downstream coverage.
The old sprint replay is tied to its original hashes and must be reproduced at
its recorded candidate, not silently rewritten for this interface change.

Next: CR-08 owner site/access verification, then run the documented real exports
and retain QA even if inconclusive. No site substitutions or threshold tuning.
