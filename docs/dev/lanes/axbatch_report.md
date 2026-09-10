# lane axbatch — HARNESS_BATCH adoption in the axes (test-axes) stage

STATUS: IN PROGRESS — this file is being written incrementally as measurement
legs complete; see the "Owed" section at the bottom for what is not yet filled in.

## Charter

Thread `HARNESS_BATCH` (the [TT-4M] STEP 2c batched compile+dispatch axis,
`docs/design/tt4m_harness_batching.md`, `docs/testing.md`'s "HARNESS_BATCH"
section) through `tests/axes/run_axes.sh`'s own `tests/harness/run.sh`
invocations, verify the axes driver's own assumptions (per-case RXTDUMP
comparison, RXTFLAGS threading, K55's REFUSAL_PATTERN entry) survive
batching, measure a representative before/after, and — if green — prepare
(not activate) `scripts/battery.sh`'s axes-stage adoption.

## (1) Implementation

`tests/axes/run_axes.sh` gained one new env var, `HARNESS_BATCH`, forwarded
verbatim into BOTH the baseline `tests/harness/run.sh` invocation and every
axis's own invocation — default 0 (today's unbatched path, byte-for-byte
unchanged, the same house rule every other forwarded var in this file
follows). **Design decision: INHERITED from the caller's env, not given its
own axes-stage default.** This script does not decide axes-stage policy; it
carries whatever the caller (a developer's quick check, or
`scripts/battery.sh`) sets, exactly like `PCREC`/`CC`/`GENCFLAGS` already do.
Baseline and axis are always compiled under the IDENTICAL value — never
split, since a batched axis compared against an unbatched baseline would be
comparing two different compile shapes, not one optimization axis.

Three small print additions (no logic change): a line at run start naming
whether this run is batched, and `HARNESS_BATCH: N` in both the per-run and
closing summary — matching the file's existing convention of stating which
tier/shape a run swept (`--vm-entry-shape tier: ...`).

Also documented in `tests/axes/CLAUDE.md` (new "`HARNESS_BATCH` adoption"
section) and `scripts/battery.sh` (see (4) below).

## (2) Driver-assumption verification (read, not just measured)

Read `tests/harness/run.sh`'s HARNESS_BATCH implementation closely
(`flush_block`'s eligibility check, `stage_block_for_batch`,
`run_case_loop`, `flush_batch`) against every mechanism `run_axes.sh`
depends on:

- **RXTDUMP per-case comparison**: `run_case_loop(exe, mode, [idx])` is the
  SAME function for `mode=standalone` and `mode=batched` (extracted
  verbatim at STEP 2c), so every RXTDUMP row a case produces is identical
  in shape regardless of path. A pcrec-level compile REFUSAL (the case
  `--engine=vm`'s K55 entry exercises) is reported by `stage_block_for_batch`
  in the byte-identical shape `flush_block`'s own standalone refusal path
  uses (compared the two RXTDUMP-writing blocks directly,
  `tests/harness/run.sh:1105-1112` vs `:1323-1330` — same six-field
  `printf`, same `REFUSED` sentinel). Confirmed by targeted leg 3 below.
- **RXTFLAGS threading**: applies at the `pcrec` invocation
  (`flush_block`'s `pflags` array, `RXTFLAGS` appended LAST), which is
  IDENTICAL whether the block goes on to compile standalone or join a
  batch — the eligibility decision and the batching mechanism only affect
  the later `gcc` step. Unaffected by construction; no separate
  verification needed beyond reading the code path once (done).
- **The three batching exclusions (`perr`, H11, routed cells)**: computed
  from the block's own parsed state (`cur_is_perr`, `head_target_def`,
  `case_route`) before `RXTFLAGS`/`HARNESS_BATCH` are consulted at all — an
  axis flag cannot change which blocks are batching-eligible, only what
  `pcrec` emits for an eligible one.
- **K55's `--engine=vm` REFUSAL_PATTERN entry**: `\P{Unknown}`'s block
  (`tests/utf8/axis12_scripts.rxt:295-297`) is an ordinary, non-routed,
  non-`perr`, non-H11 block, so under `HARNESS_BATCH` it IS
  batching-eligible — but its refusal fires at the `pcrec` compile step
  (VM emit-code-bytes cap), before the batch-vs-standalone fork has any
  effect. Verified live (leg 3): `refused_doc=3 refused_undoc=0`,
  identical under `HARNESS_BATCH=0` and `HARNESS_BATCH=64`.

No gap found between the axes driver's assumptions and what batching
changes — the two are cleanly separated (compile-time pcrec decision vs.
compile-time gcc/link decision) by the same design property
`docs/design/tt4m_harness_batching.md` item 4 states for the deny/force
axis family generally.

## (3) Targeted before/after (2-3 representative axes)

Command shape: `SKIP_ORACLE=1 AXES="<axis>" HARNESS_BATCH=<0|64> PROCS=8
bash tests/axes/run_axes.sh` (SKIP_ORACLE=1: the PC-4 libpcre2 cross-check
is orthogonal to batching and not part of what's being measured here).
PROCS=8 per tt4m2's own measured knee on this box (8 of 10 logical CPUs —
the performance-core count).

Axes chosen: `-fno-possessify` (an ordinary bit-flag axis with NO
`REFUSAL_PATTERN` entry — pure AGREE population), `-fno-counter` (has a
documented refusal population, `REFUSAL_FLOOR=180` — tests the
batched-refusal-reporting path at scale), `--engine=vm` (K55's newest
entry, the one axis whose corpus population reaches a real refusal this
sweep had never had a witness for before).

OWED (leg results not yet in — see status line at top): [TABLE]

## (4) Battery wiring (prepared, not activated)

`scripts/battery.sh`'s `axes` stage case gained a comment block naming the
one-line swap (`AXES_FULL=1 HARNESS_BATCH=64 PROCS="$AXES_PROCS" make
test-axes`) and leaves the CURRENT line (unbatched) as the one that
actually runs — per the standing "no merge mid-battery" lesson, activation
is the manager's call at the START of a battery, not something this lane
flips.

## (5) Full before/after sweep

OWED — the manager reads this report; the launch command and expected
completion shape are named in the handback message (do-then-finish: this
report is committed and the handback sent BEFORE the full sweep is
launched in background, per the lane boilerplate).

## Out of scope, flagged rather than built

`docs/design/tt4m_harness_batching.md` item 5 owes ONE new mech sabotage
row (a planted "batch link never falls back to per-pattern recovery"
detector) to the HARNESS_BATCH mechanism's own implementation lane
(tt4m3/[TT-4M] STEP 2c), not to this lane's charter (threading the var
through the axes stage). Not built here; named so it isn't lost.
