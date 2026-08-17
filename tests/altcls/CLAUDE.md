# tests/altcls — the [OPT-ALTCLS] pass's validation

`docs/dev/plan.md`'s `[OPT-ALTCLS]` row is the design; `src/opt/altcls.c` is
the pass (stage 1: single-char alternation runs -> one class; stage 2:
literal-prefix factoring on stage 1's output); `src/gen/emit_dfa.c`'s shared
`pcrec_emit_prologue` is what stamps it. This directory is the evidence that
neither stage changes what a pattern matches.

**Not a module directory.** Like tests/possessify/ and tests/mrl/, ALTCLS is
an optimization over the base tier, not a regex feature — no block here
carries a `features` directive.

## The three checks see three different things, and none replaces another

Same structure tests/possessify/CLAUDE.md establishes one rung over, restated
here because it is worth reading before adding to any of the three:

- **`altcls.rxt`** pins what each pattern MATCHES, oracle-verified against
  python3 `re`. It is structurally BLIND to the pass itself: a merged or
  factored pattern matches identically to its unmerged/unfactored spelling,
  which IS the claim, so a green corpus alone proves nothing about whether
  either stage fired.
- **`run_altdiff.sh`** — the row's PRIMARY validation instrument. The same
  pattern compiled twice — once with the pass live, once with
  `-fno-altcls-merge -fno-altcls-factor` — linked into ONE translation unit
  via the SHARED `tests/possessify/possdiff_driver.c` (not a second copy of
  the same span/capture/failure-surface comparison; only the `DIFF_A_LABEL`/
  `DIFF_B_LABEL` defines differ), and swept over subjects built from the
  pattern's own alphabet (D47.6's rule: a generator whose alphabet omits a
  pattern character measures the generator). UNLIKE the possessify/revdet/
  counter-K differentials, this one does NOT force `--engine=vm` — the pass
  runs before engine selection and touches both artifacts, so the default
  (auto) engine choice is the honest comparison, and NCAPS always agrees
  between the two builds because altcls never creates or removes an A_CAP
  node (by construction, see src/opt/altcls.c's header). Carries its own
  NON-VACUITY control: if no pattern in the sweep merged or factored, the run
  fails loudly rather than reporting a silent pass.
- **`run_altcls_tests.sh`** — that the rewrite HAPPENED where the stamp says
  it did (with the EXACT count, not just presence — a five-branch single run
  stamps `ALTCLS_MERGES=1`, Frank's own five-name exemplar stamps
  `ALTCLS_FACTORED=2`), NOWHERE when denied (D46's no-trace rule, asserted
  against the artifact), that the two stages are INDEPENDENTLY controllable
  (denying one must not silently deny the other), that `rx_info.flags` does
  not leak either deny bit, that a verdict-free pattern is byte-identical
  with the pass on and off, and that factoring never moves `RX_NCAPS`.
  Nothing else in the tree asserts any of these.

## Files

- **`altcls.rxt`** — oracle-verified corpus (python3 `re`) covering: stage 1
  plain and quantified (the plan row's own `a(b|c)+d` motivating shape),
  stage 1's adjacency boundary (`b|ab|c` must NOT merge across the
  non-single-char branch in the middle), stage 1's decline on a captured
  branch (`(b)|c`), stage 2 on Frank's own exemplars, stage 2's
  empty-remainder case (`f|frank`), three-way and deeper splits, stage 2's
  declines (no shared first byte, a wide-class first atom, a captured
  branch, a quantifier before any split), and both stages composing on one
  pattern.
- **`patterns.txt`** — `run_altdiff.sh`'s designed population, the same
  families as `altcls.rxt` restated as bare patterns (the differential needs
  patterns, not oracle expectations) plus the row's own `-15%` quantified
  keyword-list shape at a size the differential can afford per-cell.
- **`run_altdiff.sh`** — links `tests/possessify/possdiff_driver.c` against
  the pass-on and `-fno-altcls-merge -fno-altcls-factor` artifacts.
  `--corpus` derives every `.rxt` corpus pattern that stamps a positive
  `ALTCLS_MERGES`/`ALTCLS_FACTORED` count and sweeps those too — a different,
  adversarial population from `patterns.txt`'s designed one. Last full sweep:
  38 designed patterns / 33,984 cells and 78 corpus-derived patterns / 47,950
  cells, both at zero divergences (re-run rather than trust this number —
  see the sibling directories' own recorded lesson about copied figures).
- **`run_altcls_tests.sh`** — the structural checks: stamp presence and
  EXACT count on both engines (a capture-free pattern routes to the DFA, a
  capture-bearing one to the VM, and both must carry the stamp — this pass
  is not VM-only), D46 do-or-die/no-trace, independent stage control,
  `rx_info.flags` non-leak, byte-identity on a verdict-free pattern, and
  `RX_NCAPS` invariance under factoring.

## Failing-direction controls

`tests/mech/sabotages/S66_altcls_merge_drops_union.sh` (stage 1's union loop
removed — a merged class silently keeps only its first branch, deleting real
matches; caught by `run_altdiff.sh`) and
`tests/mech/sabotages/S67_altcls_flags_mask.sh` (the two deny bits dropped
from `emit_info_def`'s `rx_info.flags` mask — caught only by
`run_altcls_tests.sh`'s byte-identity check, the S65 shape one pass over).
Validate with `bash tests/mech/run_sabotage_matrix.sh S66` / `S67`.

Maintenance: update this file when files are added/removed or their roles
change.
