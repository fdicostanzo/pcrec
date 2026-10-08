# admin1008b — report (2026-10-07, sonnet, admin)

Branch `lane/admin1008b` from main `d33e1d55`. Four items, one commit each.
Scratch (gitignored): `build/adm/` in the worktree.

## 1. `scripts/emit_sweep.py`: one pool across the streams

**Reading of the brief.** The "per-arm pool then wait" barrier is the
per-STREAM one in `run_full_sweep`: each argv stream (1, 2, 3, 6) and the
composition stream (4) built its own `ThreadPoolExecutor` and drained it before
the next began. (`sweep_arms` already runs every arm inside one pool over the
patterns; the line numbers in the brief do not match this file.) The script has
no checkpoint or resume of any kind, so there was none to keep.

**Change.** `argv_stream_task` / `composition_task` do one item's compile and
comparison INSIDE the worker and return a small tuple (never the artifacts);
`run_pooled` runs every stream's tasks in one pool and returns the results in
TASK order; `merge_argv_stream` / `merge_composition` fold them into the same
`StreamResult`s in the old stream order. Composition tasks (heavy,
long-tailed) are submitted first and capped at `--comp-jobs` concurrent, so
bsweep S1.4's contention cap is unchanged while their tail overlaps the cheap
argv work; a worker with no eligible task retires and the running ones carry
on. Exceptions are re-raised in task order after the pool drains. `sweep_arms`,
`sweep_trace` and `sweep_dumps` are untouched.

**Byte identity (old = `main`'s script, new = this branch, same tree, same
binaries).** Stdout compared with the one non-deterministic line (`elapsed:`)
removed:

| run | old vs new stdout |
|---|---|
| `--ref HEAD~45 --limit 300` with self-check, ref+real runs | identical |
| `--ref-bin` copy, `--limit 1000`, `--no-self-check` | identical (old x2, new x2 all four pairwise) |
| FULL population (floors applied), `--no-self-check`, old x2 vs new x2 | identical, rc 0 on all four |
| `--ref HEAD~250 --limit 150` (abi 59 vs 65: 130 movers, hunks printed, rc 1) | identical, movers and diff hunks included |

`scripts/tests/emit_sweep.py.test` 7/0 and `trace_diff.py.test` 17/0 after.

**Wall (load 10-15 from other lanes throughout; indicative, not quiet-box).**
`--jobs 16 --no-self-check`, full population, a distinct-path copy of the binary
as the reference so both sides compile:

| order | old | new |
|---|---|---|
| run 1 / 2 | 61.3 s (user 112 s) | 25.8 s (user 109 s) |
| run 3 / 4 | 38.7 s (user 99 s) | 23.3 s (user 104 s) |

User CPU is the same (same work); wall drops 1.5x-2.4x. At `--limit 1000` and
`--limit 300` the two scripts are within noise (21/24/20 s vs 21/30 s; 68 vs 71
s with three reference builds dominating): the barrier cost is the composition
stream's tail, which only the full population has. The first small pair (250 s
vs 102 s) ran at load 58 and is not evidence either way.

## 2. `sabotage_anchors.py`: `rerun_at` from the commit's actual diff

Lives at `docs/design/start_table/sabotage_anchors.py` (the brief's
`scripts/` path does not exist).

**Change.** New options `--step NAME=A..B` (repeatable), `--repo`,
`--reach-hops K` (default 2), `--compare NAME=S1,S2,...`; a trailing
`rerun_via` column (`C5:hunk`, `C5:reach(<via>)`, `C5:edit-set`). ROOT is the
PRE tree (`git archive A`), so the diff's old-side line numbers are the
anchors' own coordinates. Per step:

- **hunk**: `git diff -U0 A B -- src`, each hunk's old-side range to the
  definitions of `call_graph.py`'s parse it overlaps (a pure insertion counts
  when it lands inside the body). Hunks that only rename identifiers,
  consistently across the whole step (the `DfaSel -> CandSel` sweep: 70 of
  them at C4), are ignored.
- **reach** (the walk-reach relation): the owner is (0) named by the changed
  text on either side; (1) stored in a TABLE the REMOVED text names (the walk
  that was replaced; `req_admits`, `pcrec_reseed_rows`); (2..K) called by what
  hop 1 reached; or a CALLER of a definition whose removed text names a table
  (the walker's consumers).
- Derived steps are added for every class except a row the same commit
  RE-AIMs. Without `--step` the output is the old output plus an empty last
  column (checked: `diff` of the first 13 columns is empty on the pre-C4 tree).

**Reproduction of the lanes' judgment re-runs.**

stc4 (`bc8277d4..ea3e3aff`, edit set as of `bc8277d4`). Old derivation:
`rerun_at` C4 = none. New: 40 rows (7 hunk, 33 reach) against 23 judged.

- Both (14): S269 S274 S276 S278 S457 S458 S460 S467 S475 S476 S594 S595 S598 S599.
- Judged, not derived (9):
  - S265 — anchor in `memfn/src/precheck.c`, outside the `src/`-only call
    graph and diff path.
  - S277 S316 S459 (`req_set_rest_members`) and S463 S470 S471
    (`emit_req_handoff_rest`) — consumers two calls from the walk, reached
    through `req_site_define` / `pcrec_emit_req_byte_check`, which the changed
    text does not name; hop 3 does not reach them either. The lane took
    S277/S278/S316 from stc1 §3.1's trace-based proposal.
  - S495 — `pcrec_dfa_cand_ppm`, reached through `cand_rs_dense_applies` via
    `cand_rows`, which C4 edits but whose removed text does not name it (it IS
    derived at C5, below).
  - S597 — owner `cand_bound_anchored_vm_applies`; the lane re-ran it because
    the trace code beside it changed.
- Derived, not judged (26): S07 S221 S223 S566 (callers of `req_use`:
  `emit_unanchored`); S449 S572 (callers of `req_admit`); S140 S494 S83 and
  S266 S270 S286 S288 S294 S299 S317 (stored in / called by `req_uses` /
  `req_admits`); S518-S521 S527 S529 (`req_handoff_applies`, the re-aimed
  signature sweep); S282 (`DfaCand`); S283 S284 S596 (`cand_rows`, hunk).
  These are a conservative superset: every one's owner is a definition whose
  walk or table changed.

stc5 (`8cada7b9..6ad08436`, edit set as of `8cada7b9`). Old derivation:
`rerun_at` C5 = 22 sites / 21 rows. New: 38 rows (31 hunk, 7 reach) against 33
(the 21 plus the 12 by judgment).

- Both (32): the 21 edit-set rows, S594-S596 S598-S600, S283 S284 S462 S473
  (`cand_rows` hunk), S495 (reach: `pcrec_dfa_cand_ppm` through the removed
  `pcrec_reseed_rows` walk).
- Judged, not derived (1): S597 — the predicate's text is unchanged and its
  role changed (B3 now decides the bound); only a slot-keyed reach (C5's new
  `cand_select(BOUND...)` against the `.slot` column of `cand_rows`) would
  see it. Not built: it is a `cand_rows`-specific parse.
- Derived, not judged (6): S297 S405 (callers of `vm_plan_reseed`), S338 S339
  S340 and S432 (hop-2 callees of the removed `pcrec_look_rows` /
  `ROWS` names).

Cost: one `git diff` and one pass over the def bodies per step, ~1 s.
Precision is about 0.35 (C4) and 0.84 (C5) against the lanes' lists; the
recommendation for C6/C7 is to run the derived list and treat the
`reach` rows as the cheap-to-skip tier.

## 3. `run_cpset_structure.sh` [2b]: function-scoped allowance

Cheap, so done. `ALLOW_FN` (space-separated `FILE:FUNCTION`; empty on main) is
read by a new `cls_scan` (the old grep pipeline plus the scoping) which exempts
`u.cls.` reads between the function's column-0 definition (`fn_span`, awk) and
its column-0 `}` and nothing else in the file. Controls: an entry whose
function is missing or holds no read prints `STALE:` and fails [2b]; new check
[2b'] runs the mechanism on a two-function fixture every time (2 reads
unscoped, 1 scoped and it is the other function's, both STALE shapes). The
script is 29 checks (was 28), 0 failed, 12 s.

**posstri's rewrite at merge.** Take main's `ALLOW` line (without
`|src/opt/possessify.c`), set `ALLOW_FN='src/opt/possessify.c:cls_polarity'`,
and keep their comment block, reworded "the function `cls_polarity`". Checked
by simulation on `lane/posstri`'s own `src` (git archive, read-only): with no
entry, 2 offenders (possessify.c:1416, 1417); with the entry, none; a planted
`u.cls` read in `a1_pmask` is reported; a stale name is `STALE`.

**Should altcls.c / ctxnode.c follow?** Yes, and so should parse.c and
lower_enc.c; only cpset.c and internal.h are the representation. Reads by
function today: ctxnode.c `lang_charset` 1; altcls.c `altcls_walk_alt` 1;
parse.c `p_class` 3; lower_enc.c `lower_class_byte` 3, `lower_class_utf8` 7,
`subtree_is_identity` 2, `wclass_of` 2. Not converted here (scope: posstri's
entry and the mechanism); each is a one-token move to `ALLOW_FN`, and the
STALE control catches a rename.

## 4. BOILERPLATE.md

Two short rules added to §Process: lanes never idle-wait for a box slot or a
long run (commit, arm the chain detached on `.lift`, hand back, END; the
manager lifts, a fresh agent reads the verdicts); mech ids are passed without
a suffix and the verdict is read from each row's `== mech run COMPLETE`
trailer.

## Validation

`make -j16` and `make strict` clean (10.6 s). Light runs as in §1-§3. The full
`make -k -j16 -Otarget test` is OWED, armed detached (below).

## STATE AT HANDOFF

- Commits on `lane/admin1008b`: emit_sweep pool, sabotage_anchors, cpset [2b],
  BOILERPLATE, and this report.
- Owed: the full `make test` on the branch tip. Chain: `build/adm/chain.sh`
  (log `build/adm/maketest.log`, verdict lines `build/adm/verdict.txt`, then
  `docs/dev/artifact_size_log.tsv` restored and `build/adm/DONE` touched),
  armed by a `nohup setsid` waiter that starts it when
  `worktrees/admin1008b/.lift` exists. Green = `verdict.txt` carries no
  `*** [Makefile:N: test-X] Error` line.
- Nothing else owed. The `cpset` ALLOW_FN rewrite for posstri is the merger's
  one edit (§3).
