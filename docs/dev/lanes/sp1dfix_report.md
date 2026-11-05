# sp1dfix — the review fixes for span_pick stage 1, unit 1d (lane sp1dfix, sonnet)

Branch `lane/memfn-sp1dfix`, cut from `lane/memfn-sp1d` @ e9e5f035e (base main daf6f002b). Brief source: the review
`docs/dev/reviews/2026-11-05-r1-memfn-sp1d.md` ("Rulings"). Stage-1 bar held: zero emitted-byte movers, no pcrec abi
change, `memfn/include/memfn.h` untouched (MF_SITE_ABI 23, MF_CLASS_V 7). F4 changes MF_TRACE output only.

NOTE ON THE DELIVER FILE: `docs/dev/lanes/sp1dfix_deliver.txt` was not in the tree at start (the brief lists it as a
deliverable), so this lane wrote it, mirroring `sp1d_deliver.txt` with this report's sections.

## By id

| id | change | evidence |
|---|---|---|
| F1 | `tests/memfn/purity_rows.tsv` + `tests/memfn/run_purity_reach.sh`: a per-row REACH table (population = window.c's 22 Table A / M / T-VERIFY row ids, found in its tables; a row missing from the table, or extra, reads red). Each row is DROPPED unconditionally in a copy of memfn/src (one text replaced exactly once; `pur_never_x`/`_d` injected) and the plant's `--purity-control` print is compared with this build's: REACH rows must move, UNREACHED rows (with their reason) must stay equal. The fixture grows from 5 to 11 sites (A-empty; A-floor with a full-set position for C-floor/C-bound(floor); a full-set verify-YES position for C-bound(yes); RESEED-first/PARKED-second for M-parked; a verify-NO run for the exact member; a rare non-scan walked offset for a C-model pick) and the skewed rates gain f=500000, j,k=100, p=100000, r,R=300. `--purity-control` now also prints `stop_set`. run_finder.sh: floor is `-eq` 1157 (was `-ge` 287); the plant is a function (`purity_plant`) run for the A-mass row and the NEW M-parked row (`na == 2 && !art->nsites`); the control requires BOTH prints non-empty. | finder log (`finder2.log`): `purity checks passed: 1157 failed: 0`; plant a-mass RED (352 failed), control reached; plant m-parked RED (44 failed), control reached; `purity_reach checks passed: 24 failed: 0`: 16 rows dropped -> a reply moves (A-empty A-parked A-model A-mass MARGIN M-parked C-member C-floor C-bound(floor) C-yes C-bound(yes) C-model C-pin C-stop C-run, plus the sub-branch `+C-member(verify-NO)`), 3 dropped -> no reply moves as declared (M-one: the walk's fallthrough picks alternative 0; C-none: a no-op row; C-asc: C-run orders first), 4 declared unreached with no plant (A-floor: the walk's fallback IS the floor row; C-meet: runs in `cands`; C-table, C-own: `plan_of`, phase 2). Plant classification (compare = the control print, old output deleted before each run): every REACH row LOUD at the harness (moves), the 3 plantable declared rows SAME. |
| F2 | `decider_census.py`: BACKSTOP split into LIVE shapes (`kit_walk(`, `< best`, `tie_takes`, `TIE_`, `pick_takes(`: each must hit >= 1 line, so a dead shape is red) and BYPASS shapes (`< b.v`, `<= b.v`, `< b->v`, `<= b->v`, `.v <`, `->v <`: the spellings a twin argmin that does not ask `kit_pick_takes` must use). The six dead shapes (`< bm`, `< lo`, `< b.mass`, `< after->mass`, `< wl`, `< inc`) are gone. HIT_FLOOR -> `HITS = 37`, EXACT. THREE new plants: an unlisted function with a `kit_pick` argmin spelled `<= b.v`, `< b.v`, `b.v < v[j]`; the script asserts none holds the text `pick_takes(`. | `make test-memfn-rows`: census 67 passed, 0 failed; backstop hits 37 (expected 37), 0 outside a member; bypass plants `<= b.v` / `< b.v` / `.v <`: 1 stray hit each (RED as it must be); the 3 old conforming plants still 1/1/2. Plant classification: all three bypass plants LOUD at the census (the old SAME-source control gap closed). A kit.h comment of mine that spelled `kit_tie_takes(` tripped the live shape and was reworded (the census working). |
| F3 | S1096's header and `SAB_DESC` name the flags the witness needs: `(?i:x)abcdefg(?i:y)` reaches the window loop ONLY under `-e utf8 --memfn=no-window-search` (the review probed without the flag; since D172 S3 the default render never enters the loop; `tests/memfn/pres_pick_witnesses.tsv`'s window line carries the flag). SAB_DOC_FIGURE now says NOT RE-MEASURED here (the figure is from WIP commit 9eb7d7837). | LIGHT PROBE of REACH (S1096's own SAB_BEFORE/SAB_AFTER on presence.c, object swapped into a copy of build/libpcrec.a, same-basename `x.c` in two dirs, old outputs deleted): `-e utf8 --memfn=no-window-search` LOUD (rc 1, "mf_define: the pre-check's parts are not its pr..."); `-e utf8`, default, `--engine=vm`: SAME. Never a SILENT-MOVE. DETECTED is re-measured at the gate's mech shard (job 417; no mech run here). |
| F4 | WCAND records now carry the KEY facts. `src=pos` gains `stretch=` and renames `stop` to `stop_ok`; NEW `src=f0` (F0's `own_members`, `own_mass`) and `src=walk` (per walked offset, in LISTED order: `idx`, `off`, `own_members`, `own_mass`, `scan`) records follow each alternative's positions. `gate_cand` gets `src`/`idx`/`stretch`/`scan`; `wf_walk.members`, `wf_alt.f0_members` added. trace_format.md: the `walked` sentence now says "the alternative lists a walked span there, whatever its entry"; the WPATH sentence fixed (a define with no WPATH, `(^)*ab`, writes WCAND and none); one line says M's inputs (A-parked's k0 facts, each `entry`, the verify-YES meet at 0) are NOT in the records yet (row 1). | SEAM's three drivers (rebuilt in scratch against the -DMF_TRACE libpcrec, variant pairs): seam_drv (own set {g} vs {gG}) records DIFFER (own_members/scan); seam_o (walk list order 1,2,3 vs 3,2,1) DIFFER (`idx`/`off` order); seam_m DIFFER, but only incidentally: the PARKED alternative's `{z}` vs `{za}` span is also its F0, so the `src=f0` record differs; A-parked's k0 and `entry` in general are still not traced (PLAN, ruled). `-e utf8` `[ac][ac]` vs `[ab][ab]`: `stretch=1` vs `0`, `key` at off 1 vs 0, DIFFER. Emitted C unchanged (below). |
| F5 | window.c: Table C header rewritten (C-meet runs in `cands` before Table A and before C-member; C-bound is the subtraction after each adder, the design lists it first as the rule); `wf_crows` order and steps (C-meet 0, C-member 1); a comment at `plan_add` says the plan is a SET until C-asc (`plan_drop` swaps). compose.c: the rate-reader comment lists run_member / translate's ranking / D-hors, "the readers of `d->rate`, found by grep". trace_format.md (above). arm_fixtures.c: the dead `"?"` snprintf deleted. ofsskip.c header: scanned term and verify order are pcrec's stated facts, no kit decider (U10). | `make strict` clean; comments only (no byte). |
| F6 | ofsskip.c `ofs_fn_applies`: the dead fourth normal-form spelling `(sc->run[p->plan_pos] & ~m & 0xFF)` deleted (the loop above already refused every RUN term failing `run_cmp_sat`); the comment says so. | Byte identity: 765 pairs SAME (below); `test-memfn-arms` 374 passed. The ofsskip mech rows (S1421 S686 S687 S689 S690 S691 S692 S694 S695) are added to the gate. |
| F7 | window.c: `c_bound` split into two declared rows `C-bound(floor)` (holds c_floor_holds, after C-floor) and `C-bound(yes)` (holds c_stop_holds, after C-yes), over a shared `bound_by(d, yes)`; no apply re-derives which adder ran. | Same truth table as `has_stop ? yset : rd_set` (the two holds partition on has_stop); byte identity SAME; the reach table drops each row and moves a reply (site 6 / site 7). |
| F9 | kit.h: the strict-order precondition at `kit_pick_takes` (a TIE row must answer 1 for exactly one operand order of two distinct keys; `kit_run_member`'s `after` filter swaps the operands). | Doc line. |
| F11 | arm_fixtures.c: `an_make(digest, rates)` is the one analysis-object builder (`fd_an_make` and `pur_rated` ask it); `set_add` replaces four inline set-bit loops. | `--purity` 1157 passed; finder 3162 passed, 0 failed. |

Out of scope, untouched: F8, F10, F12, F13, F4's M inputs, F9's U-1/U-2/P4.

## Validation

All light; no mech, no emit_sweep run, no `make test`, no queue use. Scratch under `/var/tmp/pcrec-pcrec/scratch/memfn/sp1dfix/`.

- `make`: clean. `make strict`: "whole tree compiles clean with -Werror -Wshadow".
- `make test-memfn-rows`: 67 passed, 0 failed (census). `make test-memfn-arms`: 374 passed, 0 failed (112 arm pins, 89 gate cases).
- `make test-memfn-finder` (= run_finder.sh, includes purity, both plants RED, controls reached, the reach table): `checks passed: 3162`, `checks failed: 0`. (sp1d's count was 2266; the +896 is the larger purity harness 287 -> 1157 and the 24 reach checks.)
- Anchor checker `python3 -I scripts/m6read_check_sab_anchors.py`: "sabotages checked: 1102 (1143 anchor sites); all anchors resolve".
- `VALIDATE_ONLY=1 tests/mech/run_sabotage_matrix.sh` over the 9 added rows + S1095 + S1096: 11 definitions valid (no row measured).
- BYTE IDENTITY vs the frozen base (`.../sp1d/ref/build/pcrec`, daf6f002b), my own loop (not emit_sweep): every third pattern of the four patterns files (147) x 5 arms (default, `-e utf8`, `--engine=vm`, `-fmemfn-simd`, `--analysis weblog`) = 735 pairs, plus 30 multi-target `.rxt` FILE operands (`-o DIR`, all files compared by name and bytes): 765 pairs, 1530 compiles, **765 SAME, 0 DIFF** (rc and bytes; 138/147 patterns compile per arm and the same 9 reject on both sides; 28 of 30 multi-target files compile).
- TRACE EQUALITY: base and head `-DMF_TRACE` builds, 100 patterns x 2 arms (default, `-e utf8`): rc, stdout C and EVERY `MFTRACE` line other than WCAND (REACH, ROW, END, SEL, WPATH, FDROUTE) identical, 200/200; WCAND lines 0 at base, 1775 at head (by design).
- `reach_equal.py --limit 20` (pextra + pzzz patterns files, 4 arms): `LIMITED rc=0 keys=120 differ=0`; derived gone rows none. It reads only `MFTRACE REACH` lines, so the WCAND change cannot move it.
- Total compiles about 1.9k (under the 2.5k bar).
- `make test-memfn-g2` once after the last code commit (3eec641ff; ~8 min; log `g2.log` in the scratch dir): `checks passed: 70358652`, `checks failed: 0` (no `*** [` make error; identical to sp1d's count).
- Plant compare classification summary: S1096 plant: LOUD (flags above) / SAME elsewhere, never SILENT-MOVE; purity plants (A-mass, M-parked): RED + control moved; 16 reach-table drops LOUD at the harness, 3 SAME as declared; 3 census bypass plants LOUD. No plant is a SILENT-MOVE.

## Gate jobs

`/var/tmp/pcrec-pcrec/scratch/memfn/sp1dfix/jobs/` (copied from sp1d's, keys `kit-sp1d2-*`, ids 410-419, TREE worktrees/sp1dfix, the same frozen base builds under `scratch/memfn/sp1d/`). Each job file dry-ran rc 0 and was ACCEPTED by `boxqueue add` against the scratch queue `PCREC_BOXQUEUE_DIR=.../sp1dfix/bqtest`; none was queued in the real queue and none ran. Chain: 410 -> 411 -> 412 -> 413/414/415 -> 416 -> 417/418/419.

| id | key | what | est |
|---|---|---|---|
| 410 | kit-sp1d2-strict | make; make strict | 240 s |
| 411 | kit-sp1d2-memfn | test-memfn-rows, -finder, -link, -g2, -arms, -stamps, -deleg, -manifest, test-findings, test-registry | 1100 s |
| 412 | kit-sp1d2-reach | reach_equal over the 18 arms. The comparison reads `MFTRACE REACH` lines and rc/failing sets only (its LINE regexp), so the F4 WCAND change is tolerated by construction; REACH/ROW/END must be equal, which is the check. | 1250 s |
| 413-415 | kit-sp1d2-ident1..3 | the 67 identity arms + 2 weblog analysis arms (69), 3 shards, base vs head, 440 extra patterns | 2450 s each |
| 416 | kit-sp1d2-test | make test alone via perfrun | 1800 s |
| 417-419 | kit-sp1d2-mech, mech2, mech3 | 73 sabotage rows in shards of 25/24/24: sp1d's 64 (INCLUDING S1096, whose DETECTED figure is re-measured here, and S1095) plus 9 ofsskip.c rows (S1421 S686 S687 S689 S690 S691 S692 S694 S695) for F6; window.c / gate.c / compose.c rows were already in; shard 1 keeps `unreached: 2` (S917 S919) | 2200 s each |

## Charter vs committed

- [x] F1 reach table, M-row plant, exact floor, non-empty plant log: committed (purity_rows.tsv, run_purity_reach.sh, run_finder.sh, arm_fixtures.c).
- [x] F2 census: live/bypass shapes, exact HITS, three no-`pick_takes(` plants: committed (decider_census.py).
- [x] F3 S1096 witness flags + REACH probe + figure marked not re-measured: committed; DETECTED left to the gate shard (417).
- [x] F4 KEY facts, `stop_ok`, `walked` sentence, M-inputs line: committed (window.c, gate.c, kit.h, trace_format.md); acceptance drivers differ (seam_m only through F0, see By id).
- [x] F5 stale comments and docs: committed.
- [x] F6 ofsskip.c dead clause: committed.
- [x] F7 C-bound split into declared rows: committed.
- [x] F9 doc line at kit_pick_takes: committed.
- [x] F11 fixture duplication: committed.
- [x] Not touched: F8, F10, F12, F13, F4's M inputs, F9's U-1/U-2/P4.
- [x] Stage-1 bar: zero emitted-byte movers (765/765 SAME + 200/200 trace-equal), no pcrec abi, MF_SITE_ABI 23 / MF_CLASS_V 7 untouched.
- [x] Gate jobs 410-419 built, dry-run rc 0, accepted by the scratch queue.

## STATE AT HANDOFF

Validation COMPLETE (g2 read: green) except the gate jobs above (the manager queues them) and the mech re-measure of S1096's DETECTED figure (job 417). OWED: none from this lane.
Non-routine, for the manager:
- `emit_sweep.py` was launched once by mistake (my spot script) and waited on the box lock held by job 300; it never compiled anything and I killed it with `scripts/safekill` within a minute.
- `boxqueue add` against the SCRATCH queue arms a runner; it logged job 410 START (waiting on the box lock behind job 300, "stays pending") before I `safekill`ed the runner (pid 1590008). No job body ran. The scratch queue dir `bqtest/` still lists the ten jobs; nothing consumes them.
- `deliver.txt` was absent from the tree and written by this lane.
