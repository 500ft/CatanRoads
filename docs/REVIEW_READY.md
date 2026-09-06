# CatanRoads — partial handoff, local software ready for review

Prepared 2026-09-05; resumed and checked 2026-09-06. Budget: six workload days,
30 focused hours per repository; estimates are not recorded time spent.

Canonical checkout: `/Users/redhose/Developer/research-sprints/2026-09-05/CatanRoads`.
Remote: https://github.com/500ft/CatanRoads.
Branch: `sprint/evidence-integrity-20260905`.
Base commit: `690c2fcf88bbe689bd006cce91863821a39edb2a`.
Final commit: this review packet's containing commit; its SHA is reported in the PR
because a commit cannot embed its own identity. No deployment, publication,
outreach or spending occurred. Original checkout/user changes were preserved.

[Roadmap](SPRINT_ROADMAP.md) · [Authoritative ledger](SPRINT_TASKS.csv) ·
[Progress](SPRINT_PROGRESS.md) · [Selected candidate hashes](../evidence/sprint-2026-09-05/candidate.json).

## Completed deliverables and evidence

The new intake rejects unverified references, missing/duplicate metrics, non-finite values, mismatched settings, invalid AOIs, impossible component/coverage fractions and malformed CSV headers/rows. Registered thresholds and site flags are unchanged. Workflow is installed locally.

Implementation: [intake](../analysis/catanroads/phase1_gate.py), [tests](../analysis/tests/test_phase1_gate.py), [runbook](PHASE1_RUNBOOK.md), [workflow](../.github/workflows/ci.yml).

- [Baseline identity, commands and outputs](../evidence/sprint-2026-09-05/baseline.json).
- [Original failing evidence](../evidence/sprint-2026-09-05/intake-red.json).
- [Implementation checks](../evidence/sprint-2026-09-05/implementation-green.json).
- [Final verification](../evidence/sprint-2026-09-05/final-checks.json).
- [Predeclared evaluation procedure](../evidence/sprint-2026-09-05/evaluation-plan.md),
  [retained replay](../evidence/sprint-2026-09-05/evaluate_candidate.py),
  [actual outputs](../evidence/sprint-2026-09-05/evaluation.json).
- [Three review-discovered failures, now regressions](../evidence/sprint-2026-09-05/reviewer-red.json).

- [Consumer delivery evidence](../evidence/sprint-2026-09-05/consumer.json).

35 tests passed (9 existing plus26 intake cases); static GEE validator passed; 6/6 installed-CLI cases matched.

No Earth Engine run, verified Mongolia site, road accuracy estimate or hosted Actions execution. Metadata labels/hashes cannot authenticate imagery. Positive disturbance is not recovery or stable-track detection.

## Reproduce

Run from the canonical checkout using the recorded Python3.11 environment and
repository dependencies. The local pytest workaround stubs readline before import;
it is not a skipped test or changed product requirement.

```sh
PYTHONPATH=analysis python -c 'import sys, types; sys.modules["readline"] = types.ModuleType("readline"); import pytest; raise SystemExit(pytest.main(["-q"]))'
node tools/validate_phase1.mjs
python evidence/sprint-2026-09-05/evaluate_candidate.py
git diff --check
```


Delivery route: editable catanroads0.1.0 installed with `python -m pip install -e ./analysis --no-deps --no-build-isolation`; dependencies were already available. CLI replay launches from temporary consumer directories. This is not a fresh-environment or registry-publication claim.


No separate configured lint/typecheck is claimed. Syntax checks are compilation,
not static typing. Saved output truncation, if present, is indicated by the tool
result metadata; no omitted output is called a full log.

## Evaluation meaning and remaining work

Selected implementation/protocol hashes and expectations were saved before the
additional cases ran. Existing tests, reviewed fixtures and reviewer-discovered
bugs are development material. All additional cases were retained. These small
developer-selected checks establish behavior on those inputs, not independent
scientific validation or general accuracy. Another agent is not a human reviewer.
External feedback: pending.

1. Owner verifies dated imagery for existing development/control sites before gate predictions; no post-hoc site swap.
2. Obtain actual GEE exports and scene/coverage provenance; real-data evaluation remains blocked.
3. Hosted workflow needs an authorized push with workflow permission; network-conditioned detection is future research.

Next action: CR-08: provide dated site verification and actual GEE exports per docs/PHASE1_RUNBOOK.md.

Evidence-supported portfolio bullet: “Implemented and tested a fail-closed satellite-screening intake that separates unverified QA and synthetic examples from eligible disturbance-screen results.”
This concerns engineering quality, not adoption or measured scientific performance.

## Ready-to-send review request

“Review CatanRoads against docs/SPRINT_ROADMAP.md. Repository: /Users/redhose/Developer/research-sprints/2026-09-05/CatanRoads. Base commit: 690c2fcf88bbe689bd006cce91863821a39edb2a. Final commit: PR head (see GitHub PR). Review index: docs/REVIEW_READY.md. Incomplete work: Owner verifies dated imagery for existing development/control sites before gate predictions; no post-hoc site swap. Obtain actual GEE exports and scene/coverage provenance; real-data evaluation remains blocked. Hosted workflow needs an authorized push with workflow permission; network-conditioned detection is future research. Reproduce the changed behaviors and counterexamples, rerun appropriate checks, and assess the code and evidence independently. Review first; make further changes only if requested.”
