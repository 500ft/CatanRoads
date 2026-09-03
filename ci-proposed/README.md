# Proposed CI change — not active

`ci-proposed/ci-analysis-tests.patch` contains a workflow change that **is not installed**. Nothing in this
directory is executed by GitHub Actions; it only takes effect once someone applies it.

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

## Apply it

```bash
git apply ci-proposed/ci-analysis-tests.patch
git add .github/workflows/ci.yml
git commit -m "ci: run the analysis tests"
```

`git apply --check ci-proposed/ci-analysis-tests.patch` was run against this branch and succeeds.

Once applied, delete this directory — it exists only to carry the change across the
permission gap.
