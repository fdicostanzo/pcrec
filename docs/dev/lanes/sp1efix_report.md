# sp1efix — the review fixes for span_pick stage 1, unit 1e

Lane sp1efix (sonnet), the kit manager's brief of 2026-11-05. Branch `lane/memfn-sp1efix`, cut from `lane/memfn-sp1e`
9de5b5638 (base main 20fb73159). Brief source: `docs/dev/reviews/2026-11-05-r2-memfn-sp1e.md`, "Rulings".

**Result.** Every FIX-NOW id is in, none moved a byte. MF_SITE_ABI is 23, MF_CLASS_V is 8, no pcrec abi change.
The byte-identity spot (1116 compiles, 558 ref/head pairs over default, `-e utf8`, the all-tie regime, `--analysis
weblog`, `--engine=vm`, `-fmemfn-simd`, and six multi-target .rxt compiles) reads differ 0.

Plant classes below are: SAME (the plant moves no byte and no check), SILENT-MOVE (bytes move, every check green),
LOUD (a check goes red). Old outputs were deleted before each compare; every plant was reverted.

## What changed, by id

| id | change | evidence |
|---|---|---|
| F1 | `fd_decide` takes the asker's `gate_in` (finder.c): `fd_find` hands the same `in` (`st->wf`, `def`) to the walk and to the trace context, so `cl_core` reads the window family's facts and D-hors's `core` CORED clause can refuse. The clause stays (it is Table D's contract, moved unchanged, and a window with no core is not D-hors's). PRES passes its own `in`. | `test-memfn-finder` 3163/0, `test-memfn-rows` 235/0, reach_equal smoke differ 0 (D-hors BASE 8 = HEAD 8), ident spot differ 0, so D1..R7w serve as before. Plant `CM(NOCORE)` on `ct_d_hors`: bytes MOVED (`..`, `[0-9a-f]{8}`: D-hors's shift table lost; three other patterns SAME), LOUD: G2 window plant S1549 RED ("a dense window renders no D-hors table"), and run_rows red on the `fd/D-hors` witness. At the subject the same plant was SAME (the clause was dead). |
| F2 | S1079's `SAB_DOC_FIGURE` restated: measured by hand at lane/memfn-sp1efix 695a83447 (git archive, plant applied, built, `run_finder.sh`): 6fail/3155pass. The review's runs read 3/3160; not reproduced by hand, so the figure of record is named as gate job 437's mech run. | `tests/mech/sabotages/S1079_fd-d1-unrouted.sh`; `VALIDATE_ONLY` reads it; anchor check 1102 sabotages, all resolve. |
| F3 | The row map checked both ways. ONE parser `tests/memfn/row_map.py` (5 non-empty columns, `-`/`-` paired, no duplicate), read by `rows_check.py` and `reach_equal.py`. `reach_of` returns a `Reach` tuple (counts, dropped, why, tables, ends); no in-band keys. `reach_equal --map` is red when: a map from-row has no BASE selection; a map from-table has no BASE record; a BASE-only table is named by no map line (or `--gone` row); BASE selected a row of a mapped table that no line names. rows_check M holds the map's `table:row` set to the literal `ROW_MAP_PIN` in run_rows.sh. | Plants in both readers, each RED: DELETED D-one line (reach_equal: "BASE selected wfD/D-one 21 times and no map line names it"; rows_check: pin lost `wfD:D-one`); DELETED D-hors line (both red); INVENTED `zzT zzR fd D1` (reach_equal: from-table and from-row have no BASE record; rows_check: pin new `zzT:zzR`); INVENTED `wfD D-two` (both red); a DUPLICATE line (parser error). Real map: green, BASE D-hors 8 / D-one 68 over the smoke sample. |
| F4 | `MFTRACE FDROUTE` prints `ren=` (Table B's row for E-find; the composer's arm otherwise), via new `wf_plan_bren`. `tests/memfn/renderer_rows.tsv` (14 declared pairs) and rows_check section R: every printed pair is declared, every declared pair with a witness is printed by it, a record without `ren=` is red. Documented in `memfn/docs/trace_format.md`. | Plant B (`if (fx->pick == FF_PAIR) fx->pick = FF_WALK;` after `fd_find`): bytes MOVED on all four PAIR patterns tried, and the check is LOUD: rows_check 15 failed (10 are section R: the B-fn and B-pair witnesses and eight undeclared `(PAIR, B-walk)` pairs; 5 are older fn-row witnesses). 11 pairs witnessed, 3 UNREACHED (D1c/B-memchr, D1w/B-walk, D1w/pf_walk_bounded: no pattern found for them). |
| F5 | Designated initializers at the `fd_stop` in `wf_find_decide`. (The asker restatement is PLAN, not done.) | build, strict, ident spot differ 0. |
| F6 | `wf_b_text` (the new renderer-text struct array) renamed `wf_b_render`; `wf_b_find` keeps its role; `d_one_head`/`d_one_next` renamed `find_head`/`resume_next`; the "D-one" comments (window.c, finder.c) reworded as the `c + 1` resume. | no `D-one` left under memfn/src; strict. |
| F7 | plan_cost.def comment (D-hors is finder.c's, every reader takes `KIT_COST_`); trace_format.md (`WPATH fd=` gloss); window_site.md (one dated revision line, §2.5 rewritten as the D-hors row, §2.6's E-find row); units_inventory.md (the SKIP rows); span_pick.md (the MF_CLASS_V event lists now name 1e). | grep for `Table D`, `wf_dtable`, `wf_d_text` in those files. |
| F8 | One `KIT_COST_<name>` enum in kit.h from plan_cost.def, read by finder.c (HORS_MIN) and window.c (`COST()`); the two private enums are gone. | strict; ident spot differ 0; `--finder-rows` row numbers unchanged (MF_CLASS_V 8 holds, `test-memfn-rows`). |
| F11 | `run_g2_win.sh` plants S1405 (now `cands`'s `any_empty` line) and S1410 (now `bound_by`'s drop) re-anchored on the code they test. | `run_g2_win.sh --plants` to completion: 22 RED, 0 GREEN. |
| F12 | Reason class `pcrec:trace-only` (closed set in rows_check, read by n2_report.py) on `fd` D1c, D1w, R7w in rows.tsv; row_floors.tsv header says their census floor is their only observation. | `test-memfn-rows` 235/0. |
| F13 | One trace_format.md paragraph: the composer's fd walk writes a D-hors ROW record it can never answer, and "not applicable" and "asked, false" print the same line. | doc. |
| F14 | HOUSE-7: `END_EITHER` names the renderer rows' wildcard; `select_arm` documents `*row` (not the return) as the signal and kit.h's `fd_find` comment says why. HOUSE-12: the over-width comment block in window.c reflowed. | strict. |

New plant id: **S1549** (G2 window plant, `memfn/tests/run_g2_win.sh`), taken from the kit's S1540-S1559 range because the
brief named none; S1543 and S1544 are also mech rows in that range, so the free number above S1548 was used.

Not done (out of scope per the brief): F5's asker restatement, F6's struct, F9, F10, F11's tooling, HOUSE-10, HOUSE-11, HOUSE-13.

Housekeeping: `tests/memfn/CLAUDE.md` and `memfn/src/CLAUDE.md` updated within their limits (`tests/memfn/NOTES.md` is new:
the run_proof.sh history moved out of CLAUDE.md to make room); `run_rows.sh` gained `export LC_ALL=C` (it already has its
`san_excluded` row); `memfn/docs/journal.md` entry; the lanes history index entry.

## Validation

All on worktrees/sp1efix, light, outside Frank's hold (run before 20:00).

| check | result |
|---|---|
| `make`, `make strict` | clean; strict rc 0 |
| `make test-memfn-finder` (incl. purity) | checks passed 3163, failed 0 |
| `make test-memfn-rows` (rows_check incl. M and R, decider census) | 235 / 0; decider census 67 / 0 |
| `make test-memfn-arms` | 374 / 0 |
| `make test-codegen` | rc 0 (21 of 21 scripts passed; log scratch/memfn/sp1efix/val_test-codegen.log) |
| anchor checker `scripts/m6read_check_sab_anchors.py` | 1102 sabotages checked, all anchors resolve |
| `run_g2_win.sh --plants` | to completion: 22 plants (the 21 listed plus S1549), every one applied and RED, 0 GREEN (log scratch/memfn/sp1efix/g2win_plants2.log); S1405 and S1410 RED on their new anchors |
| `make test-memfn-g2` (once, after the last code commit, a window.c comment reflow) | checks passed 70358652, failed 0; no `*** [test-` line (log scratch/memfn/sp1efix/val_g2.log) |
| byte-identity spot vs the frozen 20fb73159 build | 1116 compiles = 558 pairs over 6 regimes/arms (default, `-e utf8`, all-tie `-I tests/findings/adversarial --analysis=uniform`, `--analysis weblog`, `--engine=vm`, `-fmemfn-simd`; ~88 patterns of the four patterns files plus 14 witnesses), stdout/rc/non-MFTRACE stderr: differ 0; 34 patterns fail identically on both sides; 6 multi-target .rxt compiles (offset_skip.rxt, run_pinned.rxt x default/simd/vm): SAME |
| `reach_equal.py --map` over 29 patterns x 4 arms (default, vm, `-e utf8`, `--memfn=no-window-skip`) | differ 0, rows base 31 head 31, mapped D-hors BASE 8 = HEAD 8 |
| `--finder-rows` row numbers / MF_CLASS_V / MF_SITE_ABI | unchanged (8 / 23); `git diff 20fb73159 -- src cli lib docs/spec` is empty |
| plants (F1, F3, F4) | see the by-id table |

Not run (the brief's bar): the full `reach_equal` population, G2 full, any sweep or suite; those are the gate jobs.

## Gate jobs

Prepared in `/var/tmp/pcrec-pcrec/scratch/memfn/sp1efix/jobs/` (a copy of lane sp1e's 420-429 with keys
`kit-sp1e2-*`, ids 430-439, TREE=worktrees/sp1efix, the frozen base builds read from
`/var/tmp/pcrec-pcrec/scratch/memfn/sp1e/`; outputs under `scratch/memfn/sp1efix/`). Every job file carries
`# boxqueue: not-before 2026-11-06T01:05` as a comment and the same time as a `boxqueue: not-before` declaration in
its dry run (the declaration is what holds it). Each job dry-runs rc 0 and was accepted by the scratch queue
(`PCREC_BOXQUEUE_DIR=.../sp1efix/bqtest scripts/boxqueue add --no-start FILE`). Nothing was added to the real queue.

| id | job | work |
|---|---|---|
| 430 | kit-sp1e2-strict | `make -j16; make strict` |
| 431 | kit-sp1e2-memfn | test-memfn-rows, -finder, -link, -g2, -arms, -stamps, -deleg, -manifest, test-findings, test-registry |
| 432 | kit-sp1e2-reach | reach_equal through the row map, 19 arms, full corpus + the four patterns files (the map is now held to BASE's trace) |
| 433-435 | kit-sp1e2-ident1..3 | the identity gate's 70 arms in three shards |
| 436 | kit-sp1e2-test | `make test` via perfrun |
| 437-439 | kit-sp1e2-mech, mech2, mech3 | 50 sabotage rows (17/17/16): every row whose SAB_FILE is finder.c, compose.c, window.c or memfn.h (kit.h and plan_cost.def have none) plus the memfnfinder arm's rows; S1079 is in shard 1 |

## Charter vs committed

| charter item | committed |
|---|---|
| F1 gate_in + NOCORE plant | yes (finder.c; G2 plant S1549) |
| F2 S1079 figure at a named commit | yes (695a83447) |
| F3 both-ways map, one parser, `reach_of` result, two plants in both readers | yes |
| F4 `ren=`, trace_format.md, rows_check pairs, plant B loud | yes |
| F5 designated initializers | yes |
| F6 rename, D-one comments | yes |
| F7 stale Table D text (5 files) | yes |
| F8 one cost enum | yes |
| F11 run_g2_win.sh plants S1405, S1410, `--plants` complete | yes (22 RED) |
| F12 trace-only reason class | yes |
| F13 trace_format sentence | yes |
| F14 HOUSE-7, HOUSE-12 | yes |
| zero movers, no abi change, MF_SITE_ABI 23, MF_CLASS_V 8 | yes (ident spot, row listing) |
| gates 430-439, not-before on every file, dry-run rc 0, scratch-queue accepted | yes |
| report, deliver file committed, lanecheck DONE | yes (lanecheck run from the worktree after the commit) |

## STATE AT HANDOFF

OWED none from the lane: the gate jobs are prepared, not queued, for the manager to queue after 01:05.
