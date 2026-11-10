# k381 report — R-38 K38-1: one run decision inside the kit

STATE: delivered (gate jobs 510-519 written and dry-run, NOT queued: the kit manager queues them).
Branch lane/memfn-k381, base main 1c043835d (+ the R-38 sheet merge). Charter: the brief from
the kit manager, 2026-11-10, and `docs/design/memfn/span_runs_sheet.md` rev 1.2 §5's K38-1 row.

## Summary

The kit now has ONE run decision, `kit_run_decide` (memfn/src/presence.c, declared in kit.h).
Every pre-check run reader asks it: P3's run scan and window (and through them P4, P2 and the
twin's mass), the whole-run keep of P0/P9 (finder.c `fd_pres`), the window family's member for a
verify-YES (pre-check) run part, and translate's RQ-2 ranking (window.c, asked once per ranked
position with the previous answer handed back, option A). Its first and only rule reproduces
today: the scan is `kit_run_member` over every position (ties T_MASS_STRETCH, the higher), the
stretch is the whole run or P3's MF_PRES_WINDOW window (ties T_WINDOW, the leftmost; the window
loop moved in from `kit_pres_picks` verbatim).

`kit_run_member(` is now called only from `kit_run_decide` and the verify-NO prefilter member
(window.c `run_member`, a different site's decision, sheet §2.5). It gained a `tie` argument (the
TIE row its caller passes): that is what lets a plant, and later K38-2a's `run-tie-left` lever,
act on the run decision without touching the prefilter member.

No emitted byte moves: 320 BASE-vs-SUBJECT single-pattern artifacts are identical (below). The
full identity sweep, reach equality, make test, the G2 plants and the mech rows are the gate jobs
510-519, owed to the kit manager's queue. MF_SITE_ABI and pcrec's abi do not change.

New checks: `tests/memfn/run_decide_check.c` reads each reader where it lands (11 cases, part
`rundec` of test-memfn-finder). The RUN CALLERS section D of `tests/memfn/decider_census.py`
counts the callers exactly and has its own plants. Sabotage rows: S1095 and S1096 re-aimed onto
the run decision, S1107 kept, and new rows S3005 and S3006.

**A finding for the kit manager (a design question, not fixed here).** A tie change in
`kit_run_decide` alone does not move the window family's A-mass STOP. Inside a run stretch,
A-mass reads T_MASS_STRETCH through `kit_pick_takes` directly (window.c `a_mass_choose`). Under
the S1095 plant the stop stays rightmost while the member goes leftmost. C-pin then no longer
fires on the verify-YES part, and the ranking disappears: translate writes no RUN term, so
`rank_n` is 0. That is the observed effect on both witnesses. K38-2a's `run-tie-left` lever, if it
acts only on `kit_run_decide`, will hit the same thing. The lever's design has to say whether
A-mass's in-stretch tie is a reader of the run decision. If it is, that is one more call site
(the stop) and one more counted reader. If it is not, a pinned part de-pins under the lever, which
moves bytes on its own. The sheet's "moves scan, stretch, twin mass and ranking together" holds
for those four readers, not for the plan's stop.

## run_decide

`kit_run_reply kit_run_decide(const uint32_t *rate, kit_run_stretch st, kit_pos_at *at, const void
*src, unsigned n, const kit_run_reply *after)` (presence.c; `kit_run_reply` = `{ has_scan, scan,
mass, ver_lo, ver_len }`, kit.h). It is the sheet's `run_decide(rates, opts, span) -> (has_scan,
scan, ver)`, spelled in house style:
- rates: the byte-rate table (NULL = NONE).
- opts: `st`, the stretch the reader renders (KIT_RUN_WHOLE: P0/P9's keep, the verify-YES member,
  the ranking; KIT_RUN_WINDOW: P3). K38-2a's lever will join here.
- span: `at`/`src`/`n`, the existing accessor form, so a RUN term (`kit_run_at`, now exported from
  presence.c) and a run stated as sets (window.c `sets_at`) are asked alike.
- `after`: the ranking's previous answer.

It cannot be static: presence.c, finder.c and window.c call it.

Rule (the incumbent, reproduced): `kit_run_member(rate, at, src, n, 0, after, T_MASS_STRETCH)`;
the stretch is `[0, n)` under WHOLE, after `after`, or where `n <= MF_PRES_WINDOW`; otherwise it
is P3's window loop, unchanged, except that it reads positions through `at`.

What each reader reads:
| reader | where | reads |
|---|---|---|
| P3 run scan + window | presence.c `kit_pres_picks` | `scan` -> `run_scan`, `ver_lo` -> `run_window` (KIT_RUN_WINDOW) |
| P4 set-leads, P2 lead | presence.c `kit_pres_picks` | `mass`, `scan` of the same reply |
| the twin's mass term | presence.c `kit_pres_picks` (landmark) | `[ver_lo, ver_lo + ver_len)` of the same reply (was `at`, `min(n - at, 8)`: equal by construction) |
| P0/P9 whole-run keep | finder.c `fd_pres` | KIT_RUN_WHOLE; `member` 0 where the reply covers `[0, n)` (always, today) |
| P3's link member | finder.c `fd_pres` | `pk.run_window + 1` (the ports' reply) |
| pres_layout_check | compose.c | `pk` (the ports' reply), unchanged |
| verify-YES member | window.c `run_member` | KIT_RUN_WHOLE: `scan`, `[ver_lo, ver_lo + ver_len)` |
| RQ-2 ranking | window.c `translate` | KIT_RUN_WHOLE with `after`: `scan` -> `rank_pos[k]`, `mass` -> `rank_ppm[k]` |

## Callers and counts

RUN CALLERS (decider_census.py section D; exact maps, comment- and string-stripped text, each
call attributed to its enclosing definition):
- `kit_run_member(`: `kit_run_decide` 1, `run_member` 1 (the verify-NO branch). The sheet's Goal 2
  allowed a third (the RQ-2 ranking "IF the ranking must call it"); under option A it does not.
- `kit_run_decide(`: `kit_pres_picks` 1, `fd_pres` 1, `run_member` 1, `translate` 1.
- `T_WINDOW, key)` (P3's window pick, `kit_pres_picks`' run half): `kit_run_decide` 1.

Plants (inside decider_census.py, run by `make test-memfn-rows`): an unlisted function calling
`kit_run_member` directly turns D red (1 error), and so does one asking `T_WINDOW` (1 error). The
same section runs with `--no-plants` as part `census` of test-memfn-finder, so the mech arm
`memfnfinder` sees a real-tree bypass (S3006).

decider_census.tsv (MEMBER_COUNT 64 -> 65; HITS stays 60):
- Sheet row 56, `kit_run_member`: kept; its note now names its two callers.
- Sheet row 69, `kit_pres_picks:run-window`: moved into the new fn row `presence.c kit_run_decide`.
- New: `window.c translate:run-rank`, a part anchored on its `kit_run_decide(` call (the RQ-2
  ranking as a row, as the sheet asks).
- `run_member`'s note names the split (verify YES -> run decision, verify NO -> its own member).

The prefilter window site's own member (verify NO) remains a second run decider for a different
site (sheet §2.5). `pcrec_run_pin`'s rate pick is pcrec's and was not touched.

## Identity and reach

- Build: `nice make -j2` clean, no warnings. `make strict` rc 0
  (/var/tmp/pcrec-pcrec/scratch/memfn/k381/strict.log).
- Zero-byte sample: BASE = `git archive 1c043835d` built at
  /var/tmp/pcrec-pcrec/scratch/memfn/k381/base/build/pcrec. 32 patterns (the pres_pick and C10
  witnesses, S1095/S1096's, P0/P9 whole-run routes, cut runs at `at > 0`, runs over 8 positions,
  masked and caseless runs, a lookbehind ASSIGN site) x 10 arms (`--features all` alone, with
  `-e utf8` and with `--memfn=no-window-search`; default; `-e utf8`; `--engine=vm`;
  `--memfn=no-window-search`, with and without `-e utf8`; `-fmemfn-simd`; `--engine=vm -e utf8`;
  `--memfn=no-pres-set-lead`). 320 outputs: `diff -r` IDENTICAL (artifacts and diagnostics; the 32
  backreference refusals off `--features all` are identical too). Script and lists:
  /var/tmp/pcrec-pcrec/scratch/memfn/k381/hs/.
- `make test-memfn-finder`: 3417 passed, 0 failed (rundec 11/0, census 84/0, mass 41/0, the purity
  harness and its reach table included).
- The purity reach row `+C-member(verify-NO)` was re-anchored with the same intent: the verify-NO
  branch dropped, so a verify-NO site takes the verify-YES path. It moved from `int exact = ...` to
  the branch's `if (r->verify == MF_VERIFY_NO) {`.
- G2 quick (`make test-memfn-g2`, under `taskset -c 0,1`, so its `xargs -P nproc` ran on 2 CPUs):
  70,358,660 checks passed, 0 failed. The window family's own run is in it: "PASS: window family
  (checks passed: 10444)". Log: /var/tmp/pcrec-pcrec/scratch/memfn/k381/g2.log.
- `make test-codegen` (PROCS=2, 2 CPUs): 20 of 21 scripts passed on the first run. The red was
  tests/codegen/run_codegen_tests.sh's [K37] check, which read the "build/pcrec -e utf8 ..." text
  of my new S1095/S1096 doc figures as an unbounded compiler call. I reworded both figures and
  re-ran tests/codegen/run_codegen_tests.sh standalone: 336 passed, 0 failed. That file is the one
  test-codegen's group runs for it; the other 20 scripts did not change. Log:
  /var/tmp/pcrec-pcrec/scratch/memfn/k381/codegen.log.
- `make test-memfn-rows test-memfn-link` (2 CPUs): rc 0, rows 239/0, census with plants 94/0,
  link 11/0 (C15 holds for the new exported `pcrec_mf_kit_run_decide`/`pcrec_mf_kit_run_at`).
- Anchors: `python3 -I scripts/m6read_check_sab_anchors.py`: 1215 sabotages, 1258 anchor sites,
  all resolve.
- OWED (queue, the kit manager): emit_sweep on every arm (jobs 511-513, 71 arms) and REACH
  equality on 21 arms (job 514).

## Sabotage fates

| row | fate | anchor / suites | measured by hand (lane k381) |
|---|---|---|---|
| S1095 | RE-AIMED onto `kit_run_decide`'s tie: the plant hands its `kit_run_member` call T_MASS_SET's LOWER row | presence.c; candoracle + memfnfinder | run_decide_check 8 fail / 3 pass: scan W1 W2, member W1 W2, rank W1 W2, window W2, twin W2 (5 readers). pcrec `-e utf8 abcd` (also `--memfn=no-window-search`, `--engine=vm`): `req_run_member`'s agreement check fires ("run member 0 is not the run window's own index 3"). With that check switched off by hand, `pres_layout_check`'s run half refuses the same witnesses and the 12-position twin witness ("its run part is not the WINDOW its presence link verifies") |
| S1096 | RE-AIMED onto `kit_run_decide`'s stretch choice (the window loop, moved in); same `<=` plant | presence.c; candoracle + memfnfinder | run_decide_check 1 fail (window W3: 6, want 0). pcrec `-e utf8 --memfn=no-window-search '(?i:x)abcdefg(?i:y)'` refused by pres_layout_check |
| S1107 | KEPT (its fate moves to K38-2; pres_layout_check's run half is the live two-source check and S1096's control) | compose.c, unchanged anchor; memfnfinder | not re-measured (unchanged) |
| S3005 NEW | the twin's mass term reads the run's head `[0, ver_len)` instead of the decision's stretch | presence.c; memfnfinder | run_decide_check 1 fail (twin W2: bit 1, want 0) |
| S3006 NEW | translate's ranking asks `kit_run_member` directly (zero bytes) | window.c; memfnfinder | decider_census --no-plants 3 fail (RUN CALLERS of `kit_run_member` and of `kit_run_decide`, and translate:run-rank's anchor) |

Witnesses (run_decide_check.c; expected values are literals derived from the stated rule in
each comment, never computed by a kit function):
- W1 is S1095's `abcd` under NONE.
- W2 is the sheet's second, twin witness: `qzeeeeeeeeeq`, 12 positions, a tie between q at 0
  and q at 11. Under rates q 100, z 300000, e 900000 the decision's window is [4,12) and h is 48.
  At K 30000 the bit is 0; the plant's [0,8) gives h 18 and bit 1.
- W3 is the window tie: `eeeeeeqeeeeeee`, seven equal windows.

On W1 the window and twin are tie-blind (four positions), as the sheet notes. The P0/P9 keep is
tie-blind on every witness: it is the whole run whatever the scan.

REACH_ONLY: I ran `REACH_ONLY=1 JOBS=2 bash tests/mech/run_sabotage_matrix.sh S1095 S1096 S1107
S3005 S3006` at 2117f335b. Result: `mech-reach-only: DONE rc=0 rows=5 ... no-probe=5`. None of
the five rows declares a `SAB_REACH` probe (S1095, S1096 and S1107 had none before either), so
their reach is shown by the hand-built plants above. The per-reader check's witnesses are pinned
by its own case floor (RUNDEC_FLOOR 11), and each witness's reader lines are green on the clean
tree. Log: /var/tmp/pcrec-pcrec/scratch/memfn/k381/reach/reach.log.

## Gate jobs

The jobs are in /var/tmp/pcrec-pcrec/scratch/memfn/k381/jobs/, copied from the 3.0a set and
re-pointed: `common.sh` has TREE=worktrees/k381, BASE=1c043835d, REF = my BASE build, and REFTR
built by job 514. Keys are kit-k381-*. The HOLD (`s2a/jobs/hold.sh`) is kept. Every `--dry-run`
passes (rc 0, checked 2026-11-10).

| # | key | content |
|---|---|---|
| 510 | kit-k381-strict | make strict (cap 1200) |
| 511-513 | kit-k381-ident1..3 | the byte-identity witness: 67 declared arms at 1c043835d + 4 target arms = 71 (24/24/23); tgt-generic is the direct generic == plain check; zero movers |
| 514 | kit-k381-reach | reach_equal.py, 21 arms, no --map, no gone set; basis.py |
| 515 | kit-k381-test | make test via perfrun; witnesses S2983/S2984/S2988 and K38-1's two RUN CALLERS plants red |
| 516 | kit-k381-plants | run_g2_win.sh --plants, 26 plants |
| 517-519 | kit-k381-mech1..3 | 75 mech rows (25 per shard, cap 7200 s): the 3.0a set's 64 + rows_for over K38-1's files (S1096 S1097 S1098 S1099 S270 S286 S288 S317 S458) + S3005 S3006 |

## Charter-vs-committed checklist

| promise (brief / sheet §5 K38-1) | artifact |
|---|---|
| one `run_decide(rates, opts, span) -> (has_scan, scan, ver)`, first rule = incumbent | presence.c `kit_run_decide`, kit.h `kit_run_reply`/`kit_run_stretch` |
| P3's run scan and stretch call it | presence.c `kit_pres_picks` |
| whole-run keep (P0/P9) calls it | finder.c `fd_pres` |
| window family's member for pre-check run parts calls it | window.c `run_member` (verify YES) |
| twin admission's mass term reads it | presence.c `kit_pres_picks` landmark loop over `[ver_lo, ver_lo + ver_len)` |
| RQ-2 ranking from it, previous answer passed back (option A) | window.c `translate`, `after` |
| `kit_run_member(` only from run_decide + verify-NO member (+ ranking only if needed) | decider_census.py D: `kit_run_decide` 1, `run_member` 1 |
| `kit_pres_picks`' run half only from run_decide | D: `T_WINDOW` pick in `kit_run_decide` only; the scan via `kit_run_member` above |
| CALLER CHECK with named callers and counts; a planted direct caller reds it | decider_census.py D + its two plants; S3006 (real tree, memfnfinder) |
| decider_census.tsv: ranking a row; rows 56 and 69 move | `translate:run-rank` added; `kit_run_member` note; `kit_pres_picks:run-window` -> `kit_run_decide` (MEMBER_COUNT 65) |
| tie plant moving every reader together, counted per reader, on S1095's witness | S1095 re-aimed; run_decide_check.c 8 lines over 5 readers |
| observed via req_run_member's check and pres_layout_check's run half | hand-measured (see Sabotage fates) |
| SECOND witness for the twin, a tied stretch over 8 positions | run_decide_check.c W2; S3005 |
| S1095 re-aimed onto the tie; S1096 onto the stretch choice; S1107 kept | row files; fates table |
| new ids from the top of the free range | S3005, S3006 (highest before: S3004) |
| REACH_ONLY=1 on every moved fate | run on S1095 S1096 S1107 S3005 S3006: rc 0, no-probe 5 (no row declares SAB_REACH; reach shown by the hand plants) |
| zero bytes; MF_SITE_ABI and pcrec abi unchanged | 320-artifact sample identical; full sweep OWED (jobs 511-513, kit manager) |
| `nice make -j2`, `make strict` | clean; strict rc 0 |
| G2 window family + finder families (parallelism capped at 2) | finder 3417/0; G2 quick 70,358,660/0 (window family 10444) |
| BASE-vs-SUBJECT hand sample | done, identical |
| caller check and its plant | green, plants red |
| anchors check | all resolve |
| `make test-codegen` | 20/21 first run, the K37 red mine (doc text) and fixed; run_codegen_tests.sh re-run 336/0 |
| gate jobs 510-519, dry-run, not queued | scratch/memfn/k381/jobs/, all dry-runs rc 0; QUEUE OWED by the kit manager |
| kit docs (CLAUDE.md) | memfn/src/CLAUDE.md (presence.c), tests/memfn/CLAUDE.md (run_decide_check.c, census D) |
| no seam move, no byte move found | none found; no STOP needed |

## STATE AT HANDOFF

Tip: the last commit on lane/memfn-k381 (this report). Everything the brief puts in the lane's own
validation has run and is green; the numbers are above.

OWED, kit manager (queue): jobs 510-519 under /var/tmp/pcrec-pcrec/scratch/memfn/k381/jobs/
(dry-runs rc 0). The byte-identity witness over 71 arms, reach equality over 21 arms, make test
(with the RUN CALLERS plants witnessed), the 26 G2 window plants, and the 75 mech rows. The mech
figures for S1095/S1096 (candoracle + memfnfinder) and S3005/S3006 are the shards'.

OPEN for the kit manager: the A-mass stop finding in Summary. It decides what K38-2a's
`run-tie-left` lever must also move. No byte moved and no STOP was needed in K38-1.

Not done: window.c's C-member rule text (`wf_crows[]`, "kit_run_member, ties per
T_MASS_STRETCH") still names kit_run_member. It is a trace-visible string, and I left it so that
no trace byte moves; K38-2a can respell it together with the lever.
