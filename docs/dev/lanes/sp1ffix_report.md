# sp1ffix — review fixes for span_pick unit 1f

Lane sp1ffix (sonnet), branch `lane/memfn-sp1f`, from 98145b3d5 (unit 1f). Source: the FIX-NOW items of
`docs/dev/reviews/2026-11-03-r4-memfn-sp1f.md` and its RULINGS. Emitted bytes do not change: the edits
are an option description string, comments, a check tool, its self-test and one sabotage row's text.

## Fixes by id

- **CONTRACT-1** (`memfn/src/options.def`): fd-d1's description no longer says "(ASSERT_ZERO until it
  routes at B2)"; it says it is a MOVING deny that moves bytes at a one-byte search site. The group
  comment above it no longer claims every member is ASSERT_ZERO; it names fd-d1 as the one left and as
  DIFFER since B2. **Intended caller-visible TEXT change: the `fd-d1` row of `--list-axes` moves** (no
  other row, no flag, no byte). The docs/spec hunk is none: `docs/spec/registry.md` §6 words the deny in
  its own text and does not quote the dump text (grep of docs/spec/ for the old words: no hit). The
  identity jobs now declare it: `--dumps-declared-rows=--list-axes:fd-d1` beside the `fd-r8`/`fd-ndisp`
  gone declaration.
- **CONTRACT-2** (`memfn/include/memfn.h`): three stale comments reworded: the `start` hook ("No row
  reads it now (the dispatch rows retired at span_pick 1f)"), `mf_form_hash`'s unknown-form case ("a form
  this kit does not render"), the listing's `needs` field ("P E (A I M N: no row)"). The carrier-less
  KN_A/I/M/N bits are PLAN, untouched.
- **CHECK-1** (`scripts/tests/emit_sweep.py.test`): two controls added. "dumps declared gone: both
  directions" has the passing case and six failing ones (still listed, missing from REF, extra removal,
  addition, reorder, duplicate REF lines), plus a gone-and-declared-moved pair. "dumps declarations:
  selfcheck gate" tests the gate itself, which is now a function (`dumps_declarations` in
  `scripts/emit_sweep.py`) instead of an inline expression.
- **CHECK-2** (`scripts/emit_sweep.py`): the self-check exemption is `label.startswith("selfcheck")`,
  so a variant's `selfcheck-NAME` label is exempt too (control above).
- **CHECK-3** (`scripts/emit_sweep.py`, `dumps_declared_delta`): a gone key must be listed exactly once
  in REF; a key listed twice is a problem and no longer swallows its twin.
- **CHECK-4** (`tests/mech/sabotages/S919_*.sh`): SAB_REACH_POP re-aimed from the deleted
  `"body:R1:UNSTATED"` line to the use-site shape, `^FD_CT(_T)?\(.*, *MF_BODY_[A-Z]+, *LY_` in
  `memfn/src/finder.c` (an FD_CT row whose body argument is a mode, MIN 1). It counts 0 at HEAD, so the
  row stays UNREACHED, now truthfully; the header, SAB_EXPECT_REASON and "where it is seen" text no
  longer name R1/R2/R8 as live. It did not reach, so the UNREACHED declaration stays and the shard-3
  `unreached: 2` is unchanged.

## Checks run

- `scripts/tests/emit_sweep.py.test` (run directly): 28 pass, 0 fail (a first run showed one FAIL, the
  vm-arm composition rc=1, while I rebuilt `build/pcrec` under it; the solo rerun is clean).
- PLANTS, each FAILS the new control and passes on the tree (scratch
  `/var/tmp/pcrec-pcrec/scratch/memfn/sp1ffix/plant/`): a copy of emit_sweep.py with the gate back to
  `label == "selfcheck"` and the duplicate test removed makes both new controls print FAIL (the gate
  control on `selfcheck-plain`, the gone control on the duplicate REF case); the real file prints PASS
  for both.
- S919 plant: a copy of finder.c with one FD_CT row changed to `MF_BODY_ONESHOT` makes the new probe
  count 1 (real tree: 0), so the row would read NOW REACHED. `bash tests/mech/run_sabotage_matrix.sh
  S919` at 4005e17d5: `== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 1,
  anomalies: 0 ...)`, probe `=0(want>=1)`, UNREACHED (EXPECTED).
- `make test-memfn-rows` and `make test-memfn-finder`: rc 0 each. `nice make -j4`: clean.
- Not run here: strict, test-registry (the gate set below).

## Queue jobs

Copied from `/var/tmp/pcrec-pcrec/scratch/memfn/sp1f/jobs/` into
`/var/tmp/pcrec-pcrec/scratch/memfn/sp1ffix/jobs/`, renumbered 340-349, keys `kit-sp1f2-*`, labels
`sp1f2`, same chain (340 has no predecessor; each later job `after` the one before as in 330-339).
Changed: the identity jobs' base arm adds `--dumps-declared-rows=--list-axes:fd-d1`; outputs
(ident, mech, test, the MF_TRACE head build) go under `scratch/memfn/sp1ffix/`, the frozen inputs (ref
builds, patterns files) stay under `scratch/memfn/sp1f/`. Each job passed `--dry-run`; every expect
regex matches its own label (digits included). Keys: kit-sp1f2-strict kit-sp1f2-memfn kit-sp1f2-reach
kit-sp1f2-ident1 kit-sp1f2-ident2 kit-sp1f2-ident3 kit-sp1f2-test kit-sp1f2-mech kit-sp1f2-mech2
kit-sp1f2-mech3. S919's expected UNREACHED is unchanged (shard 3 unreached: 2).

## STATE AT HANDOFF

Fixes committed on `lane/memfn-sp1f`; the gate set is OWED, queued as the keys above (the original
330-339 were cancelled before any ran). Verdicts: `scripts/boxqueue status`. Not for this lane: the
PLAN items (KN_A/I/M/N bits, CHECK-6, CHECK-7, the declared-delta unification row). No rulings file.
