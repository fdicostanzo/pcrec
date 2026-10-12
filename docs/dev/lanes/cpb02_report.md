# cpb02 — [COMPOUND] B0-B2, the no-mover train (2026-10-12, opus)

Branch `lane/cpb02` from main `804c741fd`: B0 `fab99660e`, B1 `f523bd947`, B2
`f023f35b6`. Design: `docs/design/compound.md` rev 2.1 §A.1, §A.4-§A.5, §B.1, §F;
D163 + add. 1-4. Zero movers and no abi event at each step; no spec hunk (all internal).

## What landed
- **B0** (`src/gen/entries.c`): `PcrecEntry` table (public + internal rows: the VM's
  three `_run` bodies, the hybrid's embedded search), per-shape edge table, closure,
  `pcrec_entry_linkage`/`_storage`/`_emitted` at every definition and declaration site
  (`.h`, self-contained `.c`, header-form `.c` static forward decls, the src/enc/
  residuals via new drop/static masks). The request is the driver-tier `PcrecEmitIn`
  (new last param of `compile_driver`/`pcrec_compile_driver`); NULL = default request =
  today's linkage. The hybrid's `"static "` is now its closure answer.
- **B1** (`src/core/compound.c`): `CompPart` (every field stated; enums' zero = UNSTATED),
  `pcrec_comp_part_check` (table-build self-check), `pcrec_compile_part`. Part mode:
  prefix = placeholder + `__<role>` (K79 per part), shared blocks dropped,
  `PB_ONE_ATTEMPT` takes BOUND's `attempt-gstart` row (bot row denied); refusal off the
  DFA attempt route.
- **B2** (`src/opt/derive.c`): tree-hook list in `compile_driver` (composer, then
  derivation); `pcrec_derive_split_q` (kill, prune, group-keep, G5 independent walk,
  `PcrecDeriveReport`); `RF_CROSSES_ATTEMPTS` on the callout row (`GROUP_XA`) +
  `pcrec_ast_crosses_attempts`.

## Validation (Linux dev box)
- `make`, `make strict` green; `flag_access_check` clean; all 701 sabotage anchors found.
- emit_sweep vs a `git archive 804c741fd` build, default streams (11) and `--arms start`
  (byte+utf8 deny arms, `-e utf8`, `-i`, null): **0 movers, EXIT=0 at B0, B1, B2**.
  Logs `worktrees/cpb02/build/sc/es_b{0,1,2}{,_arms}.log`.
- New section `make test-compound` (`tests/compound/`, docs/testing.md line), 35 s:
  - B0: every 8th distinct corpus pattern x 3 arms x 3 requests, `-Werror` + `nm`
    against the plain artifact's `nm -g`: 4,854 cells, 0 failures (full corpus run
    once: 37,596 cells, 0). Both failing directions seen live while building: a missing
    edge (the `rev-end` tie calls `<p>_match`) and an over-wide one (vars on byte).
  - B1: 6 witnesses x 5 arms x 2 prefixes (60-byte one), one TU `-Werror` with a hand
    controller, run vs the plain artifact: 438,462 cells, 0 diffs; K79; self-check.
    Plant (no prologue) fails 12 answer cases + 12 builds.
  - B2: vs `twin2.derive` on cases2(+owed): 103 compared by language, 1,149,584 cells,
    0 diffs. Plants: kill `(?m)^` fails 2; kill skips `\G` fails 29 (G5).

## Findings
1. **Edge found by the check**: a `rev-end` tie finished `verify-at` makes `<p>_search`
   call `<p>_match` (shape `search_match`, asked quietly so the trace stream is unchanged).
2. **Decline list in §E.4 is stale for the AST derivation**: `^x|\n(?m)^b$` does NOT decline
   A2 (the per-node `(?m)` scope kills `^x`; sound). Also `(?:(?m:^a)|^b)` and a `(?m)`
   pattern's `\A` derive where the twin declined. B4's decline controls need re-aiming.
3. F's emitted bound reads `start_max = search_from /* fully \G-anchored */` (the row's
   payload text); cosmetic, a B4 abi event if changed.
4. Attempt-scope column: only the callout row carries it; COMMIT/SKIP/PRUNE/THEN are
   ROADMAP_NEVER (refused at parse) and verb nodes have no per-name row today.
5. B0 limits (internal errors, D77): a request must reach `_search`; `info`/`main` cannot
   be kept static. `need`'s VALID_UPTO is the controller's edge (the unit drive drops it
   without `-futf-check`).

## Owed
Full `make test` via `scripts/perfrun` after the box hold lifts — not run by this lane
(hold active at hand-back). No sabotage rows added (none named for B0-B2).

## Triage of the full `make test` (tree fb5395a0): four reds, all bookkeeping (lane cpb02 triage, sonnet)

No red was a behaviour change; B0-B2's zero-mover claim stands. Each section re-run solo green on the fixed tree, then again after merging main (rc lines in `build/tri/m_*.log`).

1. **test-registry** (`limits_check.sh` [code]): `internal.h`'s `PCREC_PART_NEED_*` (4 bit positions) and `PCREC_PART_ROLE_MAX` (the role grammar's width, "1 to 3 characters") are on neither allowlist. Added to the NON-LIMIT list with an "eighth kind" reason (interface shape, not a resource bound).
2. **test-codegen** ([K37]): `tests/compound/run_compound_unit.sh:37` passes `"$PCREC"` as argv to `check_entries.py`. That script bounds its own compiles (`timeout=GEN_TIMEOUT`) and the drive call (`timeout=3600`). Added a reasoned allowlist entry beside the longprefix one; it matches a real line, so the non-vacuity rule holds.
3. **test-cpset-structure**: [2b] flagged `src/opt/derive.c` `is_never_leaf` reading `u.cls.n`. It is a cardinality question above the lowering, so a bitmap render would be wrong. The one-liner became a headed multi-line function (HDR-1) with a function-scoped `ALLOW_FN` entry, so the rest of derive.c stays policed. Fixing [2b] exposed [5b], which the earlier abort had hidden: `A_WCLASS` shared an arm with `A_CLASS` at two derive.c switches (`qf_walk`, `qp_walk`). Each now has its own leaf arm. Section 28/1 -> 59/0.
4. **test-spec-history**: `spec_cites.py` `line_re` used `\d+(?![A-Za-z])`, which backtracks, so a "registry", colon, "12fail" token in k110fix_report.md line 38 matched on its first digit. The lookahead is now `(?![A-Za-z0-9])`. This red exists on main too. 144/1 -> 145/0.

Not touched: `docs/dev/artifact_size_log.tsv` (a test side effect, restored).
