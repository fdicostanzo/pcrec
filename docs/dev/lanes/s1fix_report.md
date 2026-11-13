# s1fix report — review 2026-11-12 r1 memfn-s1 applied to plan_frame 3.0b and span_runs_sheet K38-3

STATE: done. Lane s1fix (opus), 2026-11-12, branch lane/memfn-s1design (worktree `worktrees/s1design`). Design
text only: no code, no make, no suites, no queue jobs.

## Summary

The kit manager ruled every finding of `docs/dev/reviews/2026-11-12-r1-memfn-s1.md` as proposed: FIX-NOW S1-1..S1-7
and S1-10..S1-16, DOC S1-8 and S1-9. All 16 are applied, each marked `[r1s1 S1-n]` in place:
`docs/design/memfn/plan_frame.md` carries S1-1..S1-9 and S1-16 (§5 3.0b and the sections it reads), and
`docs/design/memfn/span_runs_sheet.md` §5 carries S1-10..S1-16 (the K38-3 row and the Order paragraph). Every cite
added was read at main 35bee4da9 by grep over `git show`. `git log 35bee4da9..main` touches none of the files 3.0b
or K38-3 reads (main 781275381; its only code-adjacent commit, 623afcb3d, re-pins start-set manifests), so the cites
also hold at main's tip. Choices the review left open, taken here:

- S1-1: the traced `fxt --purity` pass is E/E2's carrier. The optional traced window-family pass is TAKEN as well,
  because S1-7/S1-8 name G2's k3_inrun sites as the lever population, and those sites carry the agreement only on
  a traced kit. Its runtime is measured at the build; if it does not fit `make test-memfn-g2`, it goes to `-full`.
- S1-2: Q16's general form is a PLAN row (ASK-DEFINE-FRAME), not 3.0b content. It goes in at 3.0b only if its cost
  is ASK-1's.
- S1-3: the successor probe asks NONE; the JSONL stays byte-equal.
- S1-13: the K38-3 card cells are PLANNED (J5 arms of the next owner-cleared window), not merely listed.
- S1-16: the Order paragraph now takes the review's leaning, 3.0b first and K38-3 in parallel.

## Per-finding fixes

| id | the text change | where |
|---|---|---|
| S1-1 | 3.0b adds a TRACED `"$WORK/fxt" --purity` pass in `run_finder.sh` and a TRACED window-family pass (`run_g2_win.sh` against `libpcrec_mftrace.a`, `kit_objs` with `-DMF_TRACE`). Row E's detector is corrected (the plain-library window family and the plain `fx` carry no agreement), and E2 inherits it. The G2 agreement witness names the traced pass | plan_frame §5 3.0b Content, Witnesses, row (E) |
| S1-2 | ASK-6's refusal becomes LOUD: a pcrec same-commit hunk, flagged "main approves at the GO", with `has_stop` 0 keeping `at = -1`. Its reach witness is emit_sweep's cover-route `@` (the literal `@` checkers deny the cover route). Q1 is shown not to cover ASK-6. New §7 Q16 and plan row ASK-DEFINE-FRAME hold the general form. §6 ¶1 is restated | plan_frame §0 row 1, §2.1, §4.2 ASK-6 row, §5 re-base ASK-6 bullet, Content, Witnesses, §6, §7 Q16, plan-rows table |
| S1-3 | The successor probe is specified: it is broken already since U2 (six vs five `mf_art_begin` parameters; `an` read from an unset register, deny bits 32-63 dropped). Also: the jobs (240/241 in tree, 440/488 in the queue), two successor job scripts, call NONE, the `wr` JSONL keys, a `__typeof__` prototype check plus one `gcc -fsyntax-only` line in `tests/memfn/run_link_checks.sh`, and `collect.py` COPIED beside the probe. Main's PLAN item: the census sweeps since U2 | plan_frame §5 re-base "The probe" bullet; §3 package |
| S1-4 | G2's `table_name` class prints and floors a third member, "B-walk sites whose stop marker is read" (24 at seed 20261022/1500, floor measured less ~10%, 0 a named failure). The (AF) row notes 3 non-B-walk E-find sites | plan_frame §5 3.0b Content; row (AF) |
| S1-5 | §2.2's allocation bullet names the parameter's readers at 35bee4da9: `wf_find_decide` :2245-2248, `why_room` :2303-2308 (inside `wf_plan_site`), and `build_runs` :1742-1754 (define). The counting arena's population gains one PAIR-picking framed ask and one refused framed ask, each counted | plan_frame Goal 3, §2.2 Allocation, §5 Content, row (AC) |
| S1-7 | The lever cites are corrected: `decide` reads at :664 (`a_mass_choose`, the in-run stop) and :938 (`run_member`); :1563 is `translate`, reached by the plan function's Table E walk via `e_legacy_holds` :1623 and by the define. `mf_lever` is named the plan face's second art-state writer in §2.2 Purity and Goal 3. G2's k3_inrun sites are named as the existing lever population | plan_frame Goal 3, §2.2 Purity, §5 re-base lever bullet |
| S1-6 | One `[r1s1 S1-6]` clause at each stale place: §0 row 1; §2.1's caller paragraph; §2.2 contract lines 2 and 3; §3's package (ASK list, callers, "left to break"); §5 header (AF); (AB) "its plant is (AF)"; §6 ¶1; §7 Q1 (subject void), Q14 and Q15 RULED with the journal's wording; §R2.2 intro, R22, R23; STATE AT HANDOFF. A "§2.1-§2.3" row group is added to the re-base table. The re-base block's "every cite re-read" is narrowed. K38-2's ids are restated as S3040-S3048, S3059-S3064, S3069 | plan_frame header, §R2.2, §0, §2.1, §2.2, §3, §5, §6, §7, STATE AT HANDOFF |
| S1-8 | The open question (`--harness=run-tie-left` in `reach_equal.py`) is answered NO. The reasons are stated: `run_lever_fence.sh` (c)'s `ALLOW`, and the plain pcrec refusing `--harness=`. A yes would state the `ALLOW` growth and `pcrec-harness` as the binary | plan_frame §5 re-base lever bullet |
| S1-9 | `struct wf_plan` runs :1299-1341 (members at :1326-1329). The G2 reply copy is :942-949. `req_run_at`'s second reader also reads `us.wr_stated`/`us.wr.pinned` | plan_frame §5 re-base block |
| S1-10 | K38-3's cells count arm ENTRIES (loads of width W in the `G2P_REC` recording build), with the text census as the denominator. Layout A becomes `n = run_len + rnd(2W + 24)`. The w32 layout-A cell is stated as 0 today. NOTED for K38-2's record: W-K4b at W 32 never ran a w32 arm | span_runs_sheet §5 K38-3 row |
| S1-11 | The W-K4b plant gets an ASan runner: a per-plant ASan opt-in plus a `g2pres-asan` mech arm, whose cost is measured at the build. The alignment wording is fixed (the ADDRESS `s + floor` plus the load offset; off >= 8 only). K38-3 also edits `run_sabotage_matrix.sh` | span_runs_sheet §5 K38-3 row (plant, last column) |
| S1-12 | The card goes to VER 4 (`kit enter_back 4`), and zen4-grid3@1 stays valid. `plan.py`'s single `METHOD_VER` becomes the producer's ver set; `est.py` (via `parse_cards`/`base_of`) and `record.py`'s `RULES` learn the second ver. The check column names `check_store` | span_runs_sheet §5 K38-3 row item (2), check column |
| S1-13 | The planner's four pieces are listed (`DIM_FIELD`, `build()` rows with t-stating fixtures, `FLOOR`, `base_of`), plus `card_facts`'s requirements. The refusal today fires only at link time, so K38-3 adds a `build()`-time dim check and the DRY RUN refuses. The cells are PLANNED: J5's group count and `expect groups=` move | span_runs_sheet §5 K38-3 row item (2), check and plant columns |
| S1-14 | The floors follow the family rule (least over the admitting passes, less ~10%; 0 a named failure). The no-margin ruling is quoted as the three-floor exception it is | span_runs_sheet §5 K38-3 row item (1) |
| S1-15 | Admission reuses `target_text.admitted()` over `simd_levels.c` (or `mf_level.test_march`) and writes no new copy of the rule. The coverage plant's vehicle is a mech row with `SAB_FILE` `memfn/tests/run_g2_pres.sh` | span_runs_sheet §5 K38-3 row |
| S1-16 | "Disjoint CODE files". The shared hands are named: the generated `cloud_mech_shards.tsv` (the second lander regenerates it), the kit ledgers and `memfn/tests/CLAUDE.md`. The expected ids follow K38-3's if it goes first. The Order recommendation is restated (3.0b first, K38-3 in parallel) | span_runs_sheet §5 Order and the K38-3 ids cell; plan_frame §5 Concurrency, re-base ids bullet |

## The probe

`docs/dev/lanes/r33_sim/probe.c` has been broken since U2, not only by 3.0b. Its `__wrap_pcrec_mf_art_begin`
(:36-40) declares SIX parameters, and `memfn.h` :1425-1426 at 35bee4da9 has FIVE. 3.0b's successor (kit-owned,
under `docs/design/memfn/span_pick/`) is specified in plan_frame §5 3.0b's re-base block:

- It is built against the build tree's five-argument `mf_art_begin` and 3.0b's `mf_wdecide`.
- It asks NONE with `def` NULL. Its `wr` JSONL keys are exactly today's (`rc`; on rc 0 `alt`, `reseed`, `has_stop`,
  `stop`, `stop_set`, `plan`, `pinned`, `run_stated`, `run_member`, `run_lo`, `run_len`, `path`), so job 488's
  byte-for-byte compare holds.
- Two successor job scripts copy 240/241, with `TREE` stated as an argument. `span_pick/CLAUDE.md`'s Re-run section
  names them.
- `__typeof__` declares its wrapper prototypes, and `tests/memfn/run_link_checks.sh` gains one `gcc -fsyntax-only`
  line over it.
- `collect.py` is copied beside the successor.

PLAN for main: check whether any census sweep since U2's landing used the broken probe. If one did, re-make
`census0.out`/`census0_cards.out` from the successor.

## The card at ver 4

K38-3's step-back card is `kit enter_back 4`, keyed `kind;entry;back`. Ver 3 is closed: `measure_store/zen4-grid3/1`
pins kit-grid@3's whole card list, and `finder_check.py`'s `check_store` would red a fifth ver-3 card. Ver 4 leaves
that store valid and `check_store` green. The producer learns a second ver:

- `plan.py`'s `METHOD_VER` (`"3"`) becomes the set of planned vers, each card read at its own ver.
- `est.py` reads both through `plan.parse_cards`/`plan.base_of`.
- `record.py`'s `RULES` (`"kit-grid@" + plan.METHOD_VER`) names the rules per ver.

The planner's four pieces and the new `build()`-time dim check make the dry run refuse a dim with no `DIM_FIELD`
line. The cells are planned into the next owner-cleared window.

## Checks

- Cites: every line number added was read at main 35bee4da9 (`git show main:<file> | grep -n`, with main's tip
  carrying no change to those files since 35bee4da9). Files: `src/gen/emit_dfa.c`, `src/gen/known.c`,
  `memfn/src/{window,compose,finder,gate,ofsskip}.c`, `memfn/include/memfn.h`, `tests/memfn/run_finder.sh`,
  `memfn/tests/{run_g2.sh,run_g2_win.sh,run_g2_pres.sh}`, `memfn/tests/g2/{g2_win_gen.c,g2_pres_run.c}`,
  `tests/mech/run_sabotage_matrix.sh`, `tests/memfn/finder_check.py`, `docs/design/memfn/span_cards/slot/{plan,
  est,record}.py` and `jobs/common.sh`, `tests/memfn/target_text.py`, `tests/codegen/{reqcube_check.py,
  run_prechecks.sh,run_encoding_checks.sh}`, `docs/dev/lanes/r33_sim/{probe.c,240-kit-r33-sweep.sh}`,
  `docs/design/memfn/span_pick/CLAUDE.md`. The K38-2 sabotage ids were checked with `git grep` at main.
- The spec and plan are cited by section or tag only. `match_api.md §6.3.7` exists at main. A grep of the diff for
  spec or plan line cites finds none.
- The kit journal's Q14/Q15 ruling text was read at 35bee4da9 (`memfn/docs/journal.md`, entry 11-07 ~23:10).
- Commits pass the staged pre-commit checks (52 passed, 0 failed, twice).
- No compile, make, suite or queue job ran. The review's own probe counts (24 AF sites, 89 traced purity defines,
  w32 thresholds) are quoted from its verified critic files, not re-run.

## Charter-vs-committed checklist

| brief item | committed |
|---|---|
| every FIX-NOW S1-1..S1-7, S1-10..S1-16, marked `[r1s1 S1-n]` | yes, table above |
| DOC S1-8, S1-9 | yes |
| S1-2: loud refusal in 3.0b's pcrec same-commit hunks, flagged "main approves at GO"; §7 Q16 | yes (§4.2 ASK-6 row, re-base bullet, §7 Q16, plan row) |
| S1-3: jobs, call NONE, JSONL keys, `mf_art_begin` arity at the build tree, compile-only prototype check, `collect.py`'s home | yes (re-base "The probe" bullet) |
| S1-12: K38-3's card at ver 4, naming plan.py, est.py, record.py's change | yes (K38-3 row item (2)) |
| cites verified at main 35bee4da9 or later by grep; spec and plan by section or tag | yes |
| no code under `memfn/src` or `src/`; no suites, queue jobs or make; `part_d.md` untouched; `monread` not run | yes |
| report sections per `s1fix_deliver.txt`; lanecheck ends DONE rc=0 | yes |

OWED: none.
