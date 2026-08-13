# [STD1] phase C spec — check09 per-name arming + check01 aperture/floors

Working spec for the STD1 landing, written by the manager session
2026-08-13 BEFORE implementation (per the standing lesson: check design at
manager level, implementation delegable, sabotage validation before either
check counts). Delete or archive into the review file when STD1 closes.

Sequencing: phase C runs AFTER the default flip + re-baseline merge — the
new floors are measured against the flipped build. Owed by D37: these land
WITH the flip's landing (same STD1 row), never before it.

## Verified premises (2026-08-13, manager session)

- check07 passes an explicit `--features` on EVERY pcrec invocation
  (check07_gate_equivalence.c:311,408) — its three configurations never
  rely on the bare default. The default flip therefore does NOT change
  check07's semantics; phase C makes NO change to its transition rule or
  eligibility definition. (The re-baseline lane still re-runs it and
  re-measures its populations.)
- check09 assertion 2 (every PERNAME nonzero) arms only when
  `gate.compared_pairs` is floored above 0, and that floor is 0
  DELIBERATELY: arming it globally would demand all 17 registry modules
  toggle, when only {classes, modifiers} can. The global arming trigger is
  the wrong shape forever; per-name is the fix, not a bigger floor alone.
- check01 discovers the enabled-set symbol and recogniser TUs by naming
  convention (`ENABLED_RE`, `RECOG_RE`) over `nm` output, and FAILS on
  empty discovery (vacuity-guarded). STD1's new globals (named-set table,
  bare-default resolution point) are new machinery the aperture must
  catch and the isolation promise must extend over.

## check09 — per-name arming

1. **floors.txt gains per-name buckets**: `gate.pairs.classes <N>` and
   `gate.pairs.modifiers <M>`, N and M MEASURED on a real post-flip run
   (expectation: classes ≥ 24 = 12 eligible rows × 2 configs; modifiers
   measured, not guessed). `gate.compared_pairs` rises from 0 to the
   measured total; replace its "deliberately 0" comment with a dated note
   pointing here. Post-flip data point (oracle lane, 2026-08-13, real
   run): check07 measures gate.eligible_rows 22 (floor 12) and
   gate.baseline_accepted_rows 23 (floor 13) — raise BOTH ratchets here
   with the per-name work, from the same run that measures N and M.
2. **Assertion 2 restructured**: check09 reads `gate.pairs.<name>` lines
   from floors.txt; for each, check07's PERNAME count for `<name>` must
   meet the floor. A `gate.pairs.<name>` whose name is not in the registry
   is itself a FAIL (stale pin). The old global-floor arming condition is
   removed.
3. **New assertion 3 — set-membership honesty (D37's no-false-promise
   rule)**: obtain std1's expansion from the BUILT pcrec (the artifact
   stamp or whatever introspection surface phase A shipped) and assert
   every member has a `gate.pairs.<name>` line. Direction matters:
   members ⊆ floored-names (every set member demonstrably toggles);
   a toggling module not yet graduated is fine.
   Source independence (the project's check-failure lesson): pcrec's own
   claim (the stamp) is one side; the hand-pinned floors file — which
   only changes at a reviewed graduation ruling — is the other. No shared
   source.
4. **Sabotage validations, run and recorded before the check counts**:
   (a) zero modifiers' PERNAME line in a copied check07 output → check09
   must fail naming modifiers; (b) add `gate.pairs.backrefs 1` → must
   fail (PERNAME 0 < 1); (c) delete the `gate.pairs.modifiers` line while
   the stamp still lists modifiers → assertion 3 must fail.

## check01 — aperture + floors

1. **Widen `ENABLED_RE`** to match phase A's actual new global symbols
   (named-set table, default-set resolution) — taken from `nm` over the
   merged build and the impl lane's report, not guessed from source text.
2. **Isolation promise extends**: every recogniser/extent-scan TU's
   undefined list must contain NONE of the discovered symbols — a
   recogniser's answer to "is this construct real" must not depend on the
   enabled set, including the new default machinery.
3. **Floors**: the two discovery populations (`isolation.enabled_symbols`,
   `isolation.recogniser_tus`) get ratcheting minima, preferably in
   floors.txt (check01 gains the floors argument the other shell checks
   already take); measured post-merge, not guessed. Fail-on-empty stays.
4. **Sabotage validations**: (a) narrow ENABLED_RE to miss the new symbol
   → must fail as missing surface (proves the vacuity guard still arms);
   (b) in a scratch build tree, add one reference to the named-set symbol
   from a recogniser TU and rebuild (async, background task) → check
   names the object and symbol.

## Explicitly out of scope for phase C

- check07's transition rule, eligibility definition, membership
  measurement — unchanged (premise 1).
- Any new check. This is re-arming, not new invariants.
- Diagnostic wording anywhere (D26).
