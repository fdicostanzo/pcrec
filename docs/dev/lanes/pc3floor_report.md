# Lane pc3floor report — PC-3 probe-count pin -> floor

Branch `lane/pc3floor`, 1 commit on top of main (`c3a4f86e`), built and
validated in this worktree.

## What changed

`tests/registry/pcre2_check.c`'s POSIX-class-names probe-count check
(the one `expect_probes()` pin fed by `pool_from_library()`, i.e. the
RESOLVED LIBRARY BINARY's own ASCII strings) is now a FLOOR, not an
exact pin. New `expect_probes_floor(what, got, floor, recorded)`:
asserts `got >= floor` and unconditionally prints a `RECORD:` line
naming every measured (box, toolchain, count) for the resolved version,
so a real coverage drop (below floor) still fails loudly while an
ordinary different-build-same-version reading does not.

Floors: 149804 at 10.46 (the smallest of three now-known values:
149804 ubuntubudu / 154210 ubuntu-latest CI run 35681785230 / 155742
darwin), 187872 at 10.48 (one measurement so far, darwin Homebrew). An
unrecognized version still fails loudly naming itself, same as before.

**Checked and left alone, per the brief**: the other four `expect_probes()`
exact pins in the file (class-bracket doorway 2772, class delimiter byte
sweep 1275, POSIX name x position 80, uprops differential 1976) all
iterate pcrec-owned generator loops/tables, not `pool_from_library()` —
build-invariant, correctly still exact. "Verb names probed" is a
`printf` only, never asserted (`expect_probes` is not called on it) —
correctly left alone. No literal "34 real names" assertion exists in
code (that figure is only in a comment describing Homebrew's build);
nothing to change there. `n_lib < 1000` in `check_verb_names` is already
a floor, not an exact pin — no change needed.

Spec hunks (D80): `docs/spec/registry.md`'s PC-3 paragraph gained a
`[pc3floor]` note; `docs/testing.md`'s "Residual risk, not yet measured"
paragraph is rewritten as "CONFIRMED and closed", describing the fix.
`tests/registry/CLAUDE.md` needed no edit — grepped, no exact figure or
`expect_probes` reference to this count lives there.

## Validation (darwin, this worktree, CC=gcc-16)

- `make -j4 CC=gcc-16` — clean.
- `make strict CC=gcc-16` — clean (`whole tree compiles clean with
  -Werror -Wshadow`).
- `make test-registry CC=gcc-16` (solo, async, log at
  `pc3floor_final.log` in this session's scratchpad) — **PC-3 209/0**;
  RECORD line reads `POSIX class names: 187872 probes (floor 187872;
  recorded 187872 darwin (Homebrew 10.48))` (this box resolves 10.48).
  Other registry sub-checks: 225/0, 108/0, 24/0, 54/0.
- **Failing direction**, measured then reverted: temporarily set the
  10.48 floor to 200000000 in a scratch edit, rebuilt, re-ran
  `make test-registry` solo. Result: `FAIL: POSIX class names: 187872
  probes, expected at least 200000000 (floor). If you widened or
  trimmed a table on purpose and this is a genuine increase, update the
  floor AND the RECORD list in the same commit — if not, coverage was
  removed`; PC-3 dropped to 208/1, RECORD line still printed showing
  187872 against the inflated floor. Reverted via the `sed -i.bak`
  backup, rebuilt, re-ran — back to PC-3 209/0 clean (log above).

All validation numbers above are MEASURED, not inferred.

## Not touched

`docs/dev/decisions.md` D98 (historical ADR entry) and the lane report
narratives (`cifix_report.md`, `oralink_report.md`, `linktest_report.md`)
are append-only historical record, not live spec — left as-is per the
brief's explicit doc list (`docs/spec/registry.md`, `docs/testing.md`,
`tests/registry/CLAUDE.md`).
