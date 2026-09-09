# Day-1/day-2 review amendment

Reviewed day-1 `043fba9d6039b239f9a0099e37dd4c802ed58719` and day-2
`8eb9356617fdefe9ffc81e172086a1939a17f073`. No source measurements or site
verification were supplied. This amendment addresses CR-D02's existing acceptance
criteria; it does not start another road-detection workstream.

## Findings and corrections

- **Medium — rehearsal does not preserve literal file paths.** At the reviewed
  day-2 head, `analysis/tests/test_runbook_rehearsal.py:53` substituted paths into
  a shell string. Three added cases (`export files`, `export (July)`,
  `export's files`) all failed before the correction, with empty CLI stdout and
  JSONDecodeError. The helper now parses the documented invocation into arguments
  before substituting paths and runs without a shell. The runbook quotes export
  placeholders. These are harness counterexamples, not a demonstrated defect in
  the production CLI argument parser.
- **Medium — no hosted CI for the manual stack.** The existing workflow filtered
  pull-request bases to `main`; PR #7 targets the day-1 branch. The filter now also
  includes `task/priority-one-*`. Push targets stay unchanged. Hosted execution
  is verified separately after pushing, not inferred from local success.
- **Low — installation language exceeded the test.** Importability can come from
  PYTHONPATH. Renamed/reworded the precondition test so it no longer purports to
  install a package. This suite parses and exercises a documented invocation;
  it is not a fresh-environment distribution test.

## Checks

Python 3.11.8; Node 22.21.0. Workdir: repository root of the isolated review
checkout. No configured typechecker/linter was found; compile and whitespace
checks serve the configured syntax/style scope.

| Check | Before | After |
| --- | --- | --- |
| Full Python suite | 55 passed | 58 passed |
| Three new literal-path regressions | 3 failed | 3 passed within full suite |
| Static GEE configuration | PASS | PASS |
| Local temporal QA branch/schema model | PASS | PASS |
| compileall / whitespace | not baseline rerun | exit 0 / exit 0 |

[Captured red/green outputs](checks.json). Reproduce:

```sh
PYTHONPATH=analysis python -c 'import sys,types; sys.modules["readline"]=types.ModuleType("readline"); import pytest; raise SystemExit(pytest.main(["analysis/tests","-q"]))'
node tools/validate_phase1.mjs
node tools/test_temporal_qa.mjs
python -m compileall -q analysis/catanroads analysis/tests
git diff --check
```

The readline workaround is local-environment setup, not a product change. Day-1
missing-year masking remains a local test-double check, not Earth Engine runtime
validation. Do not change thresholds or declare roads from synthetic fixtures.

## Direction

Keep the fail-closed intake and negative controls. The next scientific deliverable
is still CR-08: independently verify the development/control sites, then run the
fixed export and retain scene provenance. More synthetic rehearsal does not remove
that dependency. No novelty, imagery, precision/recall or field result is claimed.
