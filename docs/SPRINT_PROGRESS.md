# Sprint progress — CatanRoads

## 2026-09-09 — CR-D02 runbook rehearsal

Executed the Phase-1 runbook's gate command *as written in the document* against synthetic
fixtures, through a subprocess, in [7 tests](../analysis/tests/test_runbook_rehearsal.py): synthetic
→ `DEVELOPMENT_ONLY` (3); the committed unverified manifest → `INCONCLUSIVE` (2) even with good
metrics; missing export → `INCONCLUSIVE`, no traceback; exit table equals the CLI mapping. Renaming a
flag or altering the exit table in the runbook fails the suite. Full suite 55 passed. Software
preparation only; CR-08 unchanged. [Verification](../evidence/task-2026-09-09/README.md).
Branch `task/priority-two-20260909`.

## 2026-09-08 — CR-D01 temporal QA follow-up

Completed one bounded P1 software task after the original 30h sprint; its original
rows and evidence are preserved. Base `b4cee1fcb2d6e0cc62b4c48699fa692e7b774ef9`,
branch `task/priority-one-20260908`, isolated worktree under
`/Users/redhose/Developer/daily-prs/2026-09-08/CatanRoads`.
[Review and reproduction](../evidence/task-2026-09-08/README.md): 48 Python tests,
Node branch/schema and static checks pass. Empty annual collections retain
masked bands; exported scene QA is required at intake. Candidate commit/push
identity is recorded in the PR. CR-08 remains owner-blocked; no imagery run.
Next command: `node tools/test_temporal_qa.mjs`; next external task CR-08.

## 2026-09-06 — Partial handoff

- Sprint start2026-09-05; canonical checkout `/Users/redhose/Developer/research-sprints/2026-09-05/CatanRoads`.
- Branch `sprint/evidence-integrity-20260905`; HEAD/base `690c2fcf88bbe689bd006cce91863821a39edb2a`.
- Seven Agent tasks done with linked evidence; CR-08 blocked on: Dated imagery/site verification and Earth Engine runtime credentials are not supplied. The existing unverified sites remain unverified. Hosted Actions requires a separately authorized push.
- 35 tests passed (9 existing plus26 intake cases); static GEE validator passed; 6/6 installed-CLI cases matched.
- [Final checks](../evidence/sprint-2026-09-05/final-checks.json), [candidate](../evidence/sprint-2026-09-05/candidate.json), [original expectations](../evidence/sprint-2026-09-05/evaluation-plan.md), [outcomes](../evidence/sprint-2026-09-05/evaluation.json).
- These are developer software checks; no physical/new scientific results. Catan's real-data arm, where applicable, stays blocked despite its software fallback evaluation.
- Handoff was prepared before commit; the PR records the final commit and push. Original user changes remain untouched.
- Next verification command: `python evidence/sprint-2026-09-05/evaluate_candidate.py`.
- Exact next task: CR-08: provide dated site verification and actual GEE exports per docs/PHASE1_RUNBOOK.md.
- Owner action moved to Day1 (2h); Day1 now7h, Day6 now2h, total30h. External turnaround is not accelerated.

## Baseline and interrupted execution

Baseline commands, outputs and identity remain in [evidence](../evidence/sprint-2026-09-05/baseline.json). Plans were saved before behavior changes. Runtime-limit pauses were followed by resuming the existing worktree; no baseline or external reply was invented. Original failing cases and corrected behavior are linked in [REVIEW_READY.md](REVIEW_READY.md).
