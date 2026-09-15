# battriage report — triage of the W23 battery's two non-chartered reds

Lane `battriage` (sonnet), branch `lane/battriage` off main @ `7d128adf`
(right after the [W23.3a] merge-review correction). Worktree
`worktrees/battriage`. Task: triage and fix the two non-chartered reds in
`build/battery_20260915_072130/{test,san}.log` — (a) inline_capability was
already dispositioned as chartered pre-existing [CC-DIFF], not this lane's.
The remaining two:

## (b) [K37] "2 site(s) invoke the compiler with NO bound"

**Cause.** `tests/rxtsource/run_rxtsource_tests.sh:2184-2185` — the W23-S6
arm-2 build (format_design.md §2.27.3 clause 5's compiled-artifact
byte-identity check for an aux-body edit) invoked `"$PCREC" --source ... -o
out.c` directly inside two `( cd ... && ... )` subshells, with no
`pcrec_run`/`"$TIMEOUT_BIN"`/`gen_run`/`gen_cc` on the line and no match in
`run_codegen_tests.sh`'s K37 allowlist. Reproduced on the branch point
before touching anything: `run_codegen_tests.sh`'s K37 block named exactly
these two `file:line`s.

**Fix.** Wrapped both invocations in `"$TIMEOUT_BIN" 30`, matching arm 1's
own budget two lines above in the same check and every other `--source`
call site already in this file (all of which route through
`"$TIMEOUT_BIN" 60` or `30`). Commit `a42fb528`.

**Verification.**
- `bash tests/codegen/run_codegen_tests.sh`: 109/0 (was 108/1 at the branch
  point). K37 now reads `738 site(s) across 150 script(s)` — the population
  grew since the battery's own snapshot (55/427) because the tree has moved
  forward under active W23 lanes; the two named sites are gone and no new
  ones appeared.
- `bash tests/rxtsource/run_rxtsource_tests.sh`: 201/0, with `W23-S6 arm 2:
  the compiled artifact (.c and .h) is byte-identical across the same
  aux-body edit` still PASS — the fix changed only the invocation's
  boundedness, not its behaviour.

## (c) [3] "the recorded manifest has drifted from this run"

**Where.** `tests/codegen/run_cpset_structure.sh`'s CHECK 3 (the [M5.0]
stage-1 stamp-census manifest, `tests/codegen/manifests/
m5_stage1_stamps.tsv`), inside `make test-cpset-structure`.

**Cause — a legitimate consequence of an already-merged, already-ratified
change, not a regression.** The diff the check printed was exactly two of
its 76 stamp readings, both `EMITTED_BYTES`:

```
[a-z]+@[a-z]+	EMITTED_BYTES	39496 -> 39499
(?i)HeLLo	EMITTED_BYTES	42414 -> 42416
```

Traced to `05c27b43`/`e1bf0025` (`[PORTFIX]`, both already on this branch,
the ratified `abi` 24 -> 25 D76 event): `emit_scan_loop` in
`src/gen/emit_dfa.c` changed its two label-emission sites from
`"%s  %s:\n"` to `"%s  %s:;\n"` (the gcc-vs-clang21 "label immediately
followed by a declaration" fix) — one extra byte per label instance the
emitter actually writes. Verified directly rather than inferred: compiling
`'[a-z]+@[a-z]+'` and `'(?i)HeLLo'` with `--emit-main` shows the first
emits three `_scan_views:;` labels (forward, reverse, anchored — exactly
+3 bytes) and the second emits two (reverse, anchored only; the forward
machine here has no `view_decl` line to guard — exactly +2 bytes),
matching both manifest deltas precisely. No other stamp on any of the 12
census witnesses moved.

`e1bf0025`'s own commit message describes a reader list "found by grep
(not hand-enumerated)" over the literal strings `.abi = 24`,
`ABI_EXPECT=24`, and the two `match_api.md` history-chain sentences — and
re-pinned every site that grep found (`run_codegen_tests.sh`'s
`ABI_EXPECT`, `run_recursion_identity.sh`'s new comparison-B comment
block, both `match_api.md` reflection-facts paragraphs). This manifest is
not among them, and could not have been: it is a table of pattern/stamp/
byte-count rows that never mentions the number "24" or "25" anywhere, so a
grep for abi-digit literals structurally cannot find it as a reader of an
abi-bumping scaffolding change. The generalisable form (for the abi-bump
ritual's own future sweeps, per D76/D94): grepping for the OLD NUMBER
finds readers that CITE the abi value; it does not find readers whose
CONTENT silently depends on the scaffolding the bump changed (any
recorded byte-count, any identity-gate manifest keyed on artifact size).
That is a second, distinct site class the ritual's grep needs to widen to
cover, or accept as a residual `make test` will catch on the next run —
which is exactly what happened here.

**Disposition: re-recorded, not escalated.** Every moved stamp is
accounted for by a change already on this branch with its own ratified
abi-bump commit; nothing here is an unexplained or unreviewed movement.
Re-recorded deliberately per r49's own rule ("a DIFF TO REVIEW, not a
number to bump"): re-ran the check with `KEEP=1`, confirmed the freshly
computed census differs from the old manifest in exactly these same two
rows (`diff` before copying, not after), then copied the fresh census over
the manifest. Commit `f6e45b98`.

**Verification.** `bash tests/codegen/run_cpset_structure.sh`: 28/0
(was 27/1), with `[3] the recorded manifest (.../m5_stage1_stamps.tsv)
matches this run exactly` now PASS.

## Other validation run on this branch

- `make -j4 CC=gcc-16`: clean build.
- `make strict`: `strict: whole tree compiles clean with -Werror -Wshadow`.

## Scope

Both fixes are test-infrastructure only (`tests/rxtsource/
run_rxtsource_tests.sh`, `tests/codegen/manifests/m5_stage1_stamps.tsv`) —
no `src/`, no `docs/spec/` surface changed, so no D80 spec hunk is owed.
No CLAUDE.md role changed (a bound fixed, a manifest re-recorded — both
already-documented maintenance the owning directories' own CLAUDE.md
entries anticipate).

The battery's `mech`/`san`/`axes`/`lint` stages were still running for this
lane's whole working period per the box constraint; this lane never ran
`make test`, `make mech`, `make san`, `make lint`, or `make test-axes`, and
touched neither those processes nor their scratch directories. The full
battery is the manager's to re-run at merge.

## Delivery

Branch `lane/battriage`, two WIP commits (`a42fb528`, `f6e45b98`) plus this
report, PARKED — not merged, per the brief.
