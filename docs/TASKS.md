# CatanRoads — tasks to completion

> **Objective.** Produce the strongest, most honestly-packaged evidence — not a completed
> project. Priority flows from leverage (does it unblock other work, or add decisive evidence)
> and from executability. Never from a calendar, and never from this project's ceiling.

Generated from an audit of the committed state of this repository. Every task is anchored to a
checked fact; no dates or estimates appear anywhere, by design.

## Two finish lines

**Ceiling.** Measured precision@k on real Mongolian terrain, a published false-positive taxonomy, active-versus-abandoned classification, and adoption by a named user.

**Floor.** The synthetic validation as it stands: a numeric reproducibility gate that catches a 0.01 px endpoint change, a negative control, and no real-terrain claim made.

The floor is the realistic finish line for anything gated on a measurement, and its tasks are
listed alongside the ceiling's — so the project is presentable even if the measurement never
happens.

> **Not in the portfolio.** The portfolio declares eight projects — `pv-fatigue-manifold-proprioception`, `roboracer-validation`, `self-stabilizing-drone`, `mechaudit`, `nomad`, `v-aid-climbing`, `outdoor-air-quality-sensor-enclosure`, `robotic-gripper-v2` — and this is not among them; searching its source for `Catan`, `Mongol` and `road` returns nothing. Worth knowing, given this is the project with the largest gap between what it does and what a reader can see.

_11 tasks · 3 Tier 0 · 3 executable now._

**Gate types.** `preregister` — write the threshold down *before* the thing it judges;
`external` — needs a resource or a person outside this repo; `build` — new work;
`hygiene` — reproducibility debt.

**Tiers.** 0 finish · 1 package · 2 park. A task whose blocker is not secured cannot be Tier 0
however decisive it is, which is why several measurements sit in Tier 2 with their
preregistration in Tier 0 ahead of them.

---

## Tier 0 — finish

### CR-01 · Apply ci-proposed/ci-analysis-tests.patch and merge PR #3

`hygiene` · **blocked-on-workflow-scope** · after XC-02

**Why it matters.** The repo has no CI at all. The numeric reproducibility gate is on main and runs only when someone invokes pytest by hand, so a change to the extractor or the scene would land unnoticed - the exact failure the gate was written to prevent.

**What it adds.** An automatic barrier around the extraction geometry.

**Done when.** A workflow runs the 9 tests on push and pull request; perturbing an endpoint by 0.01 px goes red.

### CR-02 · Freeze dated imagery provenance for the three development sites and negative-01

`preregister` · executable now

**Why it matters.** Nothing about real terrain can be claimed while the imagery underlying it can shift. negative-01 is what stops the detector being scored only where roads are already known to be.

**What it adds.** A fixed, citable input set - the precondition for every real-terrain claim.

**Done when.** config/sites.geojson carries frozen dated scene identifiers for all four sites, committed before any scoring.

### CR-03 · Commit the precision@k protocol before any scoring run

`preregister` · executable now · after CR-02

**Why it matters.** k, the match radius and what counts as a true positive decide the headline number. Chosen after seeing candidates, they are free parameters.

**What it adds.** Makes precision@k a measurement rather than a presentation choice.

**Done when.** Protocol committed - k, match tolerance, positive/negative definitions, adjudication rule - with no scores computed.

## Tier 1 — package

### CR-06 · Publish the false-positive taxonomy

`build` · **blocked-on-imagery-access** · after CR-05

**Why it matters.** A detector that never says what it confuses roads with cannot be trusted or improved, and reviewers reach for exactly this.

**What it adds.** The most unusual single artifact in the project - it demonstrates you looked at failures rather than only the score.

**Done when.** Taxonomy committed with a worked example image per category and its frequency in the CR-05 run.

### CR-07 · Replace results/ndvi_change.png with a gated figure, or keep it labelled placeholder

`hygiene` · **blocked-on-imagery-access** · after CR-04

**Why it matters.** It is currently a placeholder correctly marked as such. Either state closes the loop; leaving it ambiguous after the gate runs does not.

**What it adds.** A results directory in which every figure's evidence status is unambiguous.

**Done when.** The figure is either regenerated from gated data or its placeholder label restated with the blocking dependency named.

### CR-08 · Write the synthetic-only floor package

`build` · executable now

**Why it matters.** Imagery access may not arrive. The method, the numeric gate and the negative control are already real and presentable without it.

**What it adds.** A defensible case study that stands on the synthetic validation alone - the honest finish line if the terrain work never happens.

**Done when.** One document committed stating what is validated synthetically, what real-terrain claims are not yet made, and why.

## Tier 2 — park

### CR-04 · Run the preregistered Phase-1 gate at the four registered sites, and let it fail if it fails

`external` · **blocked-on-imagery-access** · after CR-03

**Why it matters.** results/README.md already forbids replacing the placeholder before this gate. A gate that cannot fail is decoration.

**What it adds.** The first honest statement about whether the method works on real imagery.

**Done when.** Gate outcome committed for all four sites including negative-01, pass or fail, with no threshold changed afterwards.

### CR-05 · Measure precision@k on real Mongolian terrain under the CR-03 protocol

`external` · **blocked-on-imagery-access** · after CR-04

**Why it matters.** Every current number comes from a synthetic scene. Without this the method is a demo.

**What it adds.** The project's central empirical claim.

**Done when.** Scores committed per site with the adjudicated match list.

### CR-09 · Add active-versus-abandoned classification from revegetation trajectory

`build` · **blocked-on-imagery-access** · after CR-05

**Why it matters.** Detecting a corridor says nothing about whether it is in use, which is the question a planner actually asks.

**What it adds.** A capability no baseline detector has, and the strongest methodological differentiator in the project.

**Done when.** Classifier committed with its own preregistered evaluation on the CR-02 sites.

### CR-10 · Produce the ranked-corridor map for one aimag

`build` · **blocked-on-imagery-access** · after CR-09

**Why it matters.** A per-site score is not a product; a ranked map is the thing someone could act on.

**What it adds.** The artifact that makes external adoption possible at all.

**Done when.** Map committed with the ranking rule and its uncertainty stated.

### CR-11 · Put the map in front of a named user and record the response

`external` · **blocked-on-external-party** · after CR-10

**Why it matters.** Adoption is the one ceiling here that depends on someone you do not control, and it is the only thing that would take this beyond a portfolio piece.

**What it adds.** External use - the project's actual ceiling.

**Done when.** A named contact, what they were shown, and their response recorded.

---

## Cross-cutting

These span repositories and are tracked identically in the others they touch.

### XC-02 · Obtain a token with workflow scope, or route the three CI patches to a session that has one

`hygiene` · **blocked-on-workflow-scope**

**Why it matters.** Three CI barriers exist as reviewed patches and none of them run. Each guards a defect class that has already occurred once.

**Done when.** RR-01, CR-01 and ER-02 are applied and their checks appear on subsequent pull requests.

