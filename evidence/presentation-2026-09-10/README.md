# Presentation migration verification

Date: September 10, 2026. Base commit: `6ce841289d5fa53a552b0b3effd0caf6f03f2e9e`.
New identity: [500ft/informal-road-mapping](https://github.com/500ft/informal-road-mapping).

## Scope

The README, reviewer entry points, conceptual overview and contribution templates
were updated. CI now checks local navigation, anchors, identity and SVG accessibility,
with four offline positive/negative-control tests. The diagrams are hand-authored
concepts, not new simulation results or hardware photographs.

[Repository identity and design references](../../docs/REPOSITORY_IDENTITY.md)
explain the rename and intentionally retained historical names. See
[checks.json](checks.json) for the local baseline and comparison outputs,
commands, runtime and preservation check. Source/candidate identity and hosted
CI are verified separately on this change's pull request.

## Reproduce navigation checks

```sh
python tools/check_presentation.py . "Informal Road Mapping" informal-road-mapping
python tools/test_presentation.py
```

Run from the root after cloning and installing the repository's documented
requirements. Existing project checks are in the [CI workflow](../../.github/workflows/ci.yml)
and [reading guide](../../docs/START_HERE.md).

## Boundaries

The scientific datasets, paper sources, frozen protocols, site/parameter
registers and existing release artifacts were not altered. No existing research
gate was closed by presentation work. This is a software/documentation review,
not independent human or physical validation. Repository-license terms were
preserved, including the absence of an open-source license for Enclosure.
