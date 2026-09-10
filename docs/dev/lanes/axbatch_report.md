# lane axbatch — HARNESS_BATCH adoption in the axes (test-axes) stage

STATUS: BLOCKED on a real HARNESS_BATCH finding (see (3a) below) — the
implementation/threading work (1)/(2)/(4) is done and green; the full sweep
(5) is withheld pending the manager's direction, since launching it as
specified would currently FATAL in minutes rather than produce acceptance
evidence. See "Headline finding" immediately below.

## Headline finding (3a): HARNESS_BATCH=64 makes the axes BASELINE itself fail

Not an axes-stage-specific bug, and not a defect in this lane's threading
change — a real gap in HARNESS_BATCH's own mechanism, found by this lane's
targeted measurement and reported upstream (manager thread, 2026-09-10).

Under `HARNESS_BATCH=64`, `run_axes.sh`'s baseline pass (no `RXTFLAGS` at
all) fails outright:

    tests/utf8/axis12_scripts.rxt:295-297 pattern '\P{Unknown}' failed to
    compile: pcrec: pattern too large: 1000584 bytes of emitted C source
    (limit 1000000, ~166 KB .o)

Verified directly, isolated from the harness entirely:

    build/pcrec -p rx       --features unicode-props -e utf8 -o /tmp/a.c -- '\P{Unknown}'
      -> pcrec: warning: large artifact: 999932 bytes of emitted C source (13216 of code) ... compiles.
    build/pcrec -p hb000001 --features unicode-props -e utf8 -o /tmp/b.c -- '\P{Unknown}'
      -> pcrec: pattern too large: 1000586 bytes of emitted C source (limit 1000000) — REFUSED.

`\P{Unknown}` (K55's stage-5 witness, `tests/utf8/axis12_scripts.rxt`,
landed 2026-09-09 the same session as HARNESS_BATCH itself) sits 68 bytes
under `PCREC_MAX_EMIT_BYTES`'s 1,000,000-byte cap under the harness's
default `-p rx` (2-character) prefix. `HARNESS_BATCH`'s own batch-member
prefix is `hbNNNNNN` (`printf 'hb%06d'`, always 8 characters, fixed-width
regardless of N) — 6 characters longer than `rx`, and this pattern's
emitted source references its own prefix roughly 109 times (back-of-
envelope from the byte delta), so ANY prefix even 1-2 characters longer
than `rx` would already push it over. **This is deterministic and
independent of batch size** — the `hb` prefix format doesn't vary with
N=1 vs N=64 — and it fires on the DEFAULT axis (no `RXTFLAGS` involved),
so nothing about this is axes-specific: it should reproduce identically
under a plain `make test-corpus HARNESS_BATCH=64` on the current tree
(not yet confirmed by this lane — see "Owed").

`docs/testing.md`'s HARNESS_BATCH section already documents that a longer
generated prefix inflates the reported SIZELOG byte count — but that
caveat is framed as a measurement-cosmetics issue ("worth knowing before
comparing size logs"), not as something that can flip a real compile
REFUSAL. This lane's measurement is the first to show it can.

Why 2d's evidence (`docs/dev/tt4m_2d_evidence/`) never saw this: that
acceptance run's `make test` legs almost certainly predate
`tests/utf8/axis12_scripts.rxt` joining the corpus (both landed the same
session, 2026-09-09) — population drift, not a contradiction of 2d's own
gate.

**Consequence for this lane's charter**: `scripts/battery.sh`'s axes-stage
HARNESS_BATCH=64 activation (prepared in (4) below) must NOT be flipped on
until this is resolved — activating it today would make every
`test-axes` run FATAL at the baseline step, before any axis is even
compared. Likely also blocks activating HARNESS_BATCH for `make
test`/`test-corpus` generally, pending confirmation.

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

| axis | unbatched | batched (HARNESS_BATCH=64) |
|---|---|---|
| `-fno-possessify` | rc=0, baseline 24194 keys/932s, axis agree=24194/0 mismatch/0 lost/0 gained, total 1972s | rc=1 — baseline itself FATAL (headline finding above), 280s |
| `-fno-counter` | rc=0 (in progress at report time — baseline 24194 keys/1044s green; axis result pending) | not yet run — expected to FATAL identically at the baseline step |
| `--engine=vm` | not yet run | not yet run — expected to FATAL identically at the baseline step |

The two batched legs not yet run are queued (background) but are not
expected to add information beyond confirming the headline finding, since
the FATAL fires at the baseline step — before `AXES`/`RXTFLAGS` are even
consulted — identically regardless of which axis the leg names.

## (4) Battery wiring (prepared, not activated)

`scripts/battery.sh`'s `axes` stage case gained a comment block naming the
one-line swap (`AXES_FULL=1 HARNESS_BATCH=64 PROCS="$AXES_PROCS" make
test-axes`) and leaves the CURRENT line (unbatched) as the one that
actually runs — per the standing "no merge mid-battery" lesson, activation
is the manager's call at the START of a battery, not something this lane
flips.

## (5) Full before/after sweep

WITHHELD, not merely owed — launching `AXES_FULL=1 HARNESS_BATCH=64
PROCS=8 make test-axes` as chartered would currently FATAL in minutes at
the baseline step (headline finding above), not produce the hours-scale
answer-identity evidence the row wants. Held pending the manager's
direction (asked, 2026-09-10): fix the byte-cap issue first, or run the
sweep anyway for the record, or confirm scope via a `make test-corpus`
check first.

## Owed

- Confirm the headline finding also reproduces under a plain `make
  test-corpus HARNESS_BATCH=64` (not axes-specific — expected but not yet
  run by this lane).
- The two remaining batched targeted legs (`-fno-counter`, `--engine=vm`)
  — running in background, expected to reproduce the headline finding
  identically rather than add new information.
- The full sweep (5), once unblocked.

## Out of scope, flagged rather than built

`docs/design/tt4m_harness_batching.md` item 5 owes ONE new mech sabotage
row (a planted "batch link never falls back to per-pattern recovery"
detector) to the HARNESS_BATCH mechanism's own implementation lane
(tt4m3/[TT-4M] STEP 2c), not to this lane's charter (threading the var
through the axes stage). Not built here; named so it isn't lost.
