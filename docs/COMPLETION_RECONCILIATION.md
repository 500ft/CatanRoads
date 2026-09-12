# Completion reconciliation and imagery return
Prepared 2026-09-11. A worksheet is not inspected imagery; an inspected image is not a detector evaluation. Task status authority: [SPRINT_TASKS.csv](SPRINT_TASKS.csv), CR-08 and CR-COR-01.

## Each recommendation, separately

| Recommendation | What is implemented | What is not completed |
| --- | --- | --- |
| Prepare reference inspection | [Five generated development/control forms](SITE_VERIFICATION_WORKSHEET.md) | Actual dated source-image judgments |
| Protect unseen evaluation | Holdout is omitted from the inspection worksheet | Holdout evaluation; do not open it for tuning |
| Admit site/export evidence | [Phase-1 gate](../analysis/catanroads/phase1_gate.py), tests and [runbook](PHASE1_RUNBOOK.md) | Real Earth Engine exports and real-site screen verdict |
| Verify candidate-road identity | A method and synthetic tests exist | Real precision/recall or confirmation of the six initial site guesses |
| Close CR-08 | Input requirements are prepared | Site approval and access to the required actual runtime inputs |

At this correction's base all six manifest flags are false. No site imagery was inspected and no Earth Engine run occurred in this correction. Source manifest SHA-256: `137f00927a8d46bcb55bb95f75a33ebf71c704905a24b2777577d52355cc88c1`.

## Return a judgment, not just a boolean

Use [SITE_VERIFICATION_WORKSHEET.md](SITE_VERIFICATION_WORKSHEET.md) as the single inspection form. For each non-holdout site return:

- Stable site ID, actual inspector identity and inspection date.
- Image provider, scene/view identifier or authorized access reference, and **image acquisition date**, not merely access/copyright date.
- Inspected area/extent and scale or resolution; missing/obscured area.
- Expected feature confirmed / rejected / uncertain, with counter-evidence and reason.
- Source image/screenshot reference where authorized; retain attribution and access limits.
- For temporal recovery claims, at least two dated observations and the actual temporal comparison.
- Whether this supports the manifest's exact `verified`, `ref_imagery_date`, and `provenance` fields.

Do not set `verified=true` for a rejected/uncertain guess merely to proceed. A basemap search, this blank form, or an automated text answer cannot supply a visual judgment. AI-assisted image review must be labeled as such; it is not independent human review.

## Order and stopping rules

1. Record development/control reference judgments before model predictions. Keep holdout imagery uninspected until a candidate and evaluation procedure are frozen.
2. If source imagery is inaccessible or the scene date/feature is unclear, retain an unresolved outcome. Send the exact access reference or dated authorized image so inspection can proceed; no credentials belong in the repo.
3. Apply only reviewed source-supported manifest changes, with the old coordinates retained if a prospective amendment is needed. Do not replace sites after looking at poor gate outputs.
4. Mirror accepted metadata to the GEE configuration and follow the runbook. Preserve all per-year scene/coverage QA; do not manufacture missing columns for old exports.
5. Run the exported metrics through the actual gate. A SCREEN_PASS is only the registered disturbance-screen result, not road detection precision or external validation.

Smallest unblock action: return the first dated development/control image and its completed judgment fields. This is incremental evidence intake; five successful verifications or a real screening result are not assumed from one image.

## Reproduce the preparation checks

```sh
PYTHONPATH=analysis python -m catanroads.site_worksheet --check
node tools/validate_phase1.mjs
node tools/test_temporal_qa.mjs
```

The full 63-test analysis baseline and these checks are retained in [correction evidence](../evidence/correction-2026-09-11/README.md). The generated worksheet, site manifest, frozen thresholds and original reference judgments remain unchanged.
