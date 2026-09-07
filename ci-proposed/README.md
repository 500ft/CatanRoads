# Historical CI transport patch — superseded locally, 2026-09-06

A reviewed workflow now exists at [ci.yml](../.github/workflows/ci.yml) in this
local sprint worktree, including analysis tests and static GEE validation.
It has not been pushed or run on GitHub. The old patch below records the previous
permission gap; **do not apply it again**. Hosted execution still needs an
authorized push with workflow permissions. No new credential check is claimed.

## Why it is a patch rather than the workflow file

The token used to open this pull request carries Contents and Pull requests scope but not
`workflow`, so it cannot write `.github/workflows/**`. That was confirmed two ways rather
than assumed:

```
git push      -> ! [remote rejected] refusing to allow a Personal Access Token to create
                 or update workflow `.github/workflows/ci.yml` without `workflow` scope
Contents API  -> 403 Resource not accessible by personal access token
```

That restriction is deliberate: it stops an automated token from silently changing what CI
runs. Shipping the change as a patch keeps that property — the diff is reviewable, and it
does nothing until a human or an authorised token installs it.

## Historical application instructions (superseded; do not execute)

```bash
git apply ci-proposed/ci-analysis-tests.patch
git add .github/workflows/ci.yml
git commit -m "ci: run the analysis tests"
```

`git apply --check ci-proposed/ci-analysis-tests.patch` was run against this branch and succeeds.

Once applied, delete this directory — it exists only to carry the change across the
permission gap.
