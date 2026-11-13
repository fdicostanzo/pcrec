# k383 — kit unit K38-3 (R-38): per-level W-K4 cells, the W-K4b ASan plant path, the step-back card at ver 4

Lane k383 (opus), branch lane/memfn-k383, cut from main a9fc6dbd8; build GO Frank 2026-11-12. Design of record:
docs/design/memfn/span_runs_sheet.md §5 K38-3 row with [s1d], [r1s1 S1-10..S1-15], [r2s1 RK383-1..6]. The card
half was built by a sonnet sub-lane in this worktree (commits 2a03255d7, 985bd9aa1), reviewed here.

## Summary

- The presence family (memfn/tests/run_g2_pres.sh, g2/g2_pres_run.c) now counts ARM ENTRIES per (level, layout U/L/A)
  in the recording build, floors them by the family rule, holds non-admitting and generic cells at exactly 0, and
  checks that every kit level is run by a pass target on this host. The level list and admission are read from the
  kit (tests/memfn/simd_levels.c against $LIB, tests/memfn/target_text.py `admitted()`), never a script literal.
- The W-K4 plants exist per admitted level (S3098/S3099 unaligned at floor - 1, S3100/S3101 aligned down), with a
  per-plant ASan opt-in (`plant_asan`) and the plant path reading each pass's asan.log; mech rows S3098-S3104 and
  a new mech arm `g2pres-asan`.
- The step-back card `kit enter_back 4` (dims kind;entry;back) is in memfn/data/cards/kit-grid.tsv; plan.py, est.py,
  record.py and tests/knowledge/meas_recompute.py learn the second ver; the build()-time dim check is scoped to the
  planned vers; control S3105 (slot row d1). Visibly UNMEASURED; zen4-grid3@1 untouched and check C green.
- No pcrec or kit emitted byte moves (no file under src/, cli/, lib/, memfn/src, memfn/include changed; the card
  table is not read by the build); the emit_sweep zero-mover proof is the queued job's stage 1.
- Ids taken: S3098-S3105 (above S3077 and 3.0b's S3078-S3097).

## Built vs designed

| design item | built | where |
|---|---|---|
| (1) cells per (level, layout), arm ENTRIES, counter live in U, L and A (S1-10, RK383-1) | yes: per-width bits from the load hooks' size, live only in entry/re-entry calls (`use_call`); L is count-only (no records); A is a count-only placement loop `lay_a_count` | g2_pres_run.c |
| RK383-6: A's loop on its OWN stream | yes: `rnd3`; every recording `G2P`/`G2PGEN` line identical before and after (diffed) | g2_pres_run.c |
| layout A widened `n = run_len + rnd(2W + 24)` | yes, in the ASan `lay_a` (on `rnd`, as ruled) and in `lay_a_count` (`rnd3`) | g2_pres_run.c |
| floors by the family rule, a 0 cell named (S1-14), exact 0 on non-admitting and generic passes (RK383-5) | yes: `CELL_FLOORS`, `cell_checks` | run_g2_pres.sh |
| level list from the kit, reuse `admitted()` (S1-15); coverage check, a named failure not a skip | yes: `level_table`, the coverage loop | run_g2_pres.sh |
| W-K4a plant (unaligned floor - 1) and W-K4b plant (address aligned down) per admitted level (S1-11) | S3098-S3101 | run_g2_pres.sh plant table, tests/mech/sabotages |
| per-plant ASan opt-in + mech arm `g2pres-asan` (S1-11); runner reads asan.log, `plant_expect` holds the ASan pattern (RK383-2) | yes | run_g2_pres.sh, tests/mech/run_sabotage_matrix.sh |
| cells' control (w32 entry threshold raised) | S3102 | as above |
| exact-0 control (w32 admitted on x86-64) | S3103 (kit admission widened + region given avx2; the listing's facts unchanged) | as above |
| coverage plant (v3 dropped from the pass list), mech vehicle with SAB_FILE the script | S3104 | tests/mech/sabotages |
| (2) card `enter_back` at ver 4 (S1-12) | yes | kit-grid.tsv |
| plan.py: vers {3,4}, DIM_FIELD `back`, enter_back rows over (kind, entry, t), FLOOR line (an exemption), base_of (S1-13) | yes | slot/plan.py |
| build()-time dim check scoped to planned vers (RK383-4) | yes `check_card_dims`; control S3105 | slot/plan.py, slot/sabotage.sh |
| est.py writes one set per ver, rules owner per ver; record.py RULES per ver; meas_recompute learns kit-grid@4 (RK383-3) | yes | slot/est.py, slot/record.py, tests/knowledge/meas_recompute.py |
| J5's `expect groups=` follows the plan | derived from `plan.py groups` (no literal); J5 groups now 4 | slot/jobs/common.sh (unchanged) |
| shared hands: cloud mech shard table regenerated | yes (`cloud_units_plan.py mech --setup 35 --slots 30 --waves 3 --write`) | tests/ci/cloud_mech_shards.tsv |

Not built (deliberately): any art.py artifact for a step-back arm (finding F1). Kit ledgers (memfn/docs/journal.md,
responses.md) are the kit manager's to write; not touched.

## The cells and their counters

Measured 2026-11-12, dev box, seed 20261110, 400 sites (`G2P cells vwW=U,L,A`; populations U 9280, L 2696, A16
8700, A32 17980 calls per pass):

| pass | w16 U | w16 L | w16 A | w32 U | w32 L | w32 A |
|---|---|---|---|---|---|---|
| x86-64-v3 default | 181 | 85 | 176 | 111 | 80 | 506 |
| x86-64-v3 lever | 181 | 84 | 176 | 111 | 81 | 506 |
| x86-64 default/lever | 292 | 165 | 291 | 0 | 0 | 0 |
| generic default/lever | 0 | 0 | 0 | 0 | 0 | 0 |

`CELL_FLOORS="w16:163:75:158 w32:100:72:455"` (least over admitting passes, less ~10%). The w32 layout-A cell, 0 at
35bee4da9 by construction, now reads 506 with the widened length. Coverage: `level w16: run by x86-64-v3 x86-64`,
`level w32: run by x86-64-v3`. Generic passes print vec_reads=0, so the exact-0 OFF cell holds without exceptions.

## The card at ver 4

`kit enter_back 4 kind;entry;back walkbytes "artifact die1 g256" "delta 1048576" 7 7 twin-per-arm - - -`, t in
{0,3,8,16,32}. Sub-lane validation (relayed by the kit manager): `plan.py report` rc 0 (25 enter_back lines listed,
re-run here: rc 0), `plan.py groups J5` = 4 (re-run here), `est.py selftest` 52/0, finder_check check C 906/0 with
check_store green on measure_store/zen4-grid3/1, S3105 DETECTED, the scoped dim check's control shown by hand.
Findings:
- F1: §5.2 names t but not how t enters the whole-artifact arm, so art.py REFUSES a step-back arm by name and
  `run.py dry J5` refuses until it is specified (no timing method invented). Consequence: J5 cannot be dry-run in
  the next window until the kit rules the arm's form (or moves the step-back arms out of J5).
- F2: the run record carries one `set` key, so a ver-4 set cannot pass meas_recompute's set check from a mixed
  record; it needs one record per ver.
- F3: job 486-kit-s2d-J5's est (250) is likely low: J5's arms go from 16 to 66.

## Plants and controls

`run_g2_pres.sh --plant ID` (dev box, nice):

| id | what | result | wall |
|---|---|---|---|
| S3098 | w16 arm's first load at floor - 1 | RED by `LAYOUT: L ...: the entry faulted`; oracle RED violations=796; generic unchanged | 44 s |
| S3099 | w32 arm's first load at floor - 1 | RED by the L fault; oracle RED violations=219; x86-64/generic unchanged | 44 s |
| S3100 | w16 first load aligned down (ASan) | RED by `ERROR: AddressSanitizer: use-after-poison` (layout A); oracle RED 1047 | 80 s |
| S3101 | w32 first load aligned down (ASan) | RED by `ERROR: AddressSanitizer: heap-buffer-overflow` (layout A); oracle RED 332 | 80 s |
| S3102 | w32 entry threshold raised (cells' control) | RED by `CELL: x86-64-v3.0: w32 A: 0 arm entries`; census green | 44 s |
| S3103 | kit admits w32 on x86-64 (exact-0 control) | RED by `CELL: x86-64.0: w32 U: 111 arm entries where the target admits none` | 46 s |
| S3104 | x86-64-v3 dropped from the pass list (mech only) | hand copy of the script: `FAIL: level w32 has no runnable target`, checks failed 1 | ~60 s |
| S3105 | DIM_FIELD `back` removed (slot row d1) | DETECTED (`plan: card enter_back@4 dim back has no DIM_FIELD line`) | — |

RK383-2's control, shown by hand: with the asan.log read removed, S3100 prints `PLANT S3100 RED BUT NOT BY ITS
DETECTOR (family ERROR: AddressSanitizer; oracle RED ...)`. `plant_absent` holds the passes a level's plant must
leave unchanged (none moved). The ASan plant cost is ~36 s over a NOASAN plant (~1.8x); the `g2pres-asan` rows carry
the median ESTIMATE weight in the cloud shard table until a cloud mech run measures them (tests/ci/cloud_reweight.sh).
Note: S3101's report is heap-buffer-overflow rather than use-after-poison (its first-block candidates move with i,
and a verify read leaves the block); still layout A's ASan detector.

## Checks

- `TMPDIR=scratch bash memfn/tests/run_g2_pres.sh` (with ASan): checks passed 1124582, failed 0 (was 1123853: +36
  cells, +2 coverage, the rest the ASan driver's rnd-dependent count after the widened `lay_a`); oracle green over
  53790 records; skipped arms 0.
- `run_g2_pres.sh --reach`: new tokens REACH-G2P-W16-ARM n=22, REACH-G2P-W32-ARM n=22, REACH-G2P-LEVELS n=2.
- `make strict`: clean. `make test-memfn-targets`: 42 passed, 0 failed.
- `make test-memfn-g2` (the quick tier, incl. 4p and 4w): rc 0, checks passed 70358669, failed 0 (10 m 51 s).
- `scripts/m6read_check_sab_anchors.py`: 1251 sabotages, all anchors resolve. `VALIDATE_ONLY=1
  tests/mech/run_sabotage_matrix.sh S3098..S3104`: 7 definitions valid. `tests/ci/cloud_mech_check.sh`: PASS, 90
  shards hold the 1251 ids exactly once.
- `CLAUDEMD_ROOT=worktree scripts/check_claudemd_size.sh --all`: 368 CLAUDE.md files within limits.

## Owed runs

OWED: kit-k383-gate (queued as 590-kit-k383-gate; script /var/tmp/pcrec-pcrec/scratch/memfn/k383/jobs/590-kit-k383-gate;
--ready gated by the evening hold, runs after 01:00): stage 1 emit_sweep zero movers vs a9fc6dbd8 (default sweep +
-fmemfn-simd=x86-64|x86-64-v3|armv8-a arms + generic==plain), stage 2 the presence family with ASan, stage 3 the
plants S3098-S3103 (S3100/S3101 under ASan). Completion line `k383-gate: DONE rc=N`, each stage's
`k383-gate: stage K ... rc=N`; logs in /var/tmp/pcrec-pcrec/scratch/memfn/k383/gate/.
Cloud kinds for the kit manager to dispatch: `mechrows` over S3098,S3099,S3100,S3101,S3102,S3103,S3104 (the first
measured seconds re-weigh the g2pres-asan rows), and the per-PR `test` kind.

## STATE AT HANDOFF

All work committed on lane/memfn-k383. OWED: none in this tree beyond the queued verdict named under Owed runs
(the deliver file says `owed: none`, while the brief asks for the queue key: both are stated here).

## Charter-vs-committed checklist

- [x] W-K4a/W-K4b cells per (level, layout), levels from mf_levels/mf_targets, arm ENTRIES, counters live in U, L, A
- [x] W-K4b plant ASan path: per-plant opt-in, --plant reads asan.log, reds by its own detector
- [x] step-back card at ver 4; plan.py, est.py, record.py learn the second ver; zen4-grid3@1 valid, check_store green; UNMEASURED
- [x] floors by the family rule (and the exact-0 rule)
- [x] every new check names its control, each shown red by hand (S3102, S3103, S3104, S3105, the asan.log read)
- [x] no emitted byte moves, no abi event (zero-mover proof OWED in kit-k383-gate stage 1)
- [x] make strict, targets family, presence family, anchors, check_store; CLAUDE.md files updated
- [ ] art.py step-back artifact: NOT built, finding F1 (needs a ruling)
