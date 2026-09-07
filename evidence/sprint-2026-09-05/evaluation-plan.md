# Bounded intake delivery evaluation — 2026-09-06

The three reviewer cases (subset coverage, duplicate headers, geographic bounds)
informed fixes and are development regressions, not evaluation results. Freeze
current source hashes before the six cases below are run through the installed
CLI from a temporary consumer directory. Exact expected statuses precede outputs.

1. Synthetic fixture, negative=0, development=[0.0001,0.0001,0]: DEVELOPMENT_ONLY/3.
2. Same arithmetic with the actual unverified manifest: INCONCLUSIVE/2.
3. Synthetic fixture with coverage string 'NaN': INCONCLUSIVE/2.
4. Synthetic fixture with one CSV row missing its final cell: INCONCLUSIVE/2.
5. Synthetic fixture with an extra unheaded cell: INCONCLUSIVE/2.
6. Synthetic fixture with only one passing development site: DEVELOPMENT_ONLY/3,
   arithmetic SCREEN_FAIL.

All six retained, no exclusions. These are developer-selected software cases,
not unseen satellite imagery, independent human review or accuracy estimates.
Real-data evaluation is blocked by dated imagery verification and runtime access.
