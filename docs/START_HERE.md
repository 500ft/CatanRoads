# Start here

## Two-minute project review

1. Read the [overview and evidence boundary](../README.md).
2. Inspect the [synthetic demonstration](../results/method_demo_synthetic.png).
3. Read the [Phase-1 runbook](PHASE1_RUNBOOK.md) and [review index](REVIEW_READY.md).
   The contribution so far is tested screening/extraction tooling and a
   falsifiable evaluation design—not a demonstrated road map.

## Reproduce the local checks

Follow the [README setup](../README.md#getting-started), from the repository root.
The import name remains `catanroads`, even though the repository is now
`informal-road-mapping`.

The maintained checks are the Python tests and both Node scripts in
[CI](../.github/workflows/ci.yml). They use synthetic fixtures and static
configuration checks; none queries Earth Engine.

If this workstation's known `readline` import issue prevents pytest startup,
the explicit local workaround is:

```sh
PYTHONPATH=analysis python -c 'import sys,types; sys.modules["readline"]=types.ModuleType("readline"); import pytest; raise SystemExit(pytest.main(["analysis/tests","-q"]))'
```

This is a local runtime workaround, not a missing or skipped suite.

## Optional synthetic demonstration

After installing `analysis[dev]`:

```sh
python analysis/demo_synthetic.py
```

This **regenerates** `results/method_demo_synthetic.png`. Run it in a disposable
clone or inspect the resulting diff; do not mistake regeneration for fresh
evaluation. The [figure guide](data-and-figures.md) records its source and role.

The existing [method illustration](../assets/method.png) depicts the intended
full pipeline. Its network-conditioning and confirmation stages are plans,
not an implemented end-to-end detector.

## Real-imagery route

Use [the generated inspection form](SITE_VERIFICATION_WORKSHEET.md), not model
output, to record source-image judgments. The form excludes the holdout.
An absent or ambiguous image is an unresolved input, not a negative label.

Only after evidence-backed development/control verification should an authorized
Earth Engine user execute [the Phase-1 runbook](PHASE1_RUNBOOK.md).
Exported numeric metrics—not map colors—determine the gate. Keep the primary
configuration intact before sensitivity studies.

The positive-disturbance gate is not a test for recovery, traffic volume or
all stable bare tracks. Preserve the recovering-site mismatch and any failed
comparison rather than swapping sites after results.

## Contributor route

Read [Contributing](../CONTRIBUTING.md), then identify the source of the change:

| Layer | Canonical location |
| --- | --- |
| Study design and admission rules | [Design](design.md), [runbook](PHASE1_RUNBOOK.md) |
| Reference manifest and inspection form | [Site manifest](../config/sites.geojson), [worksheet](SITE_VERIFICATION_WORKSHEET.md) |
| Earth Engine screening | [gee/ndvi_change.js](../gee/ndvi_change.js) |
| Extraction and gate implementation | [Python package](../analysis/catanroads/) |
| Regression and counterexample tests | [Analysis tests](../analysis/tests/) |
| Figures and their interpretation | [Figure guide](data-and-figures.md), [results](../results/README.md) |

Do not fill verification fields from assumptions or treat this reading guide
as permission to inspect the held-out site.

See [repository identity notes](REPOSITORY_IDENTITY.md) for the rename,
unchanged package names and presentation references.
