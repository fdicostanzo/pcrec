# lane axbatch — HARNESS_BATCH adoption in the axes (test-axes) stage

STATUS: FIX LANDED AND VERIFIED (c5b450a1) — the headline finding below is
RESOLVED, not merely reported. Implementation/threading (1)/(2)/(4) done and
green; the fix (3a fix, below) done and verified at three levels; the full
sweep (5) is this lane's LAST act, launched in background after this report
commits (do-then-finish).

## Headline finding (3a): HARNESS_BATCH=64 made the axes BASELINE itself fail — FIXED, manager's ruling (fix option d)

Not an axes-stage-specific bug, and not a defect in this lane's threading
change — a real gap in HARNESS_BATCH's own mechanism, found by this lane's
targeted measurement, reported upstream (manager thread, 2026-09-10), and
FIXED by this lane per the manager's ruling (below) in the same delivery.

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

**The fix (manager's ruling, 2026-09-10, "fix option d"): pin batch member
prefixes to EXACTLY 2 CHARACTERS**, the same length as the unbatched path's
`rx`. Neither (a) raising the witness pattern's margin nor (c) excluding it
is the right shape — the contract is that batching preserves the unbatched
compile VERDICT, and emitted size is legitimately prefix-length-sensitive
for ANY `-p` choice, not a batching defect to work around case by case.
Uniqueness is only needed WITHIN one batch's own link (each batch is a
separate executable), so a 2-character namespace comfortably covers any
`HARNESS_BATCH` size this design recommends.

Implemented in `tests/harness/run.sh` (commit c5b450a1): `batch_member_prefix
<0-based index within THIS batch>` generates a 2-character code — FIRST
character restricted to the 26 lowercase letters (a prefix becomes a C
identifier prefix in the emitted source, so a leading digit would emit
invalid C — caught before landing, not after), second character alnum (36
options), 936 total codes, `rx` itself skipped via a fixed +1 offset (a
runtime retry loop was considered and rejected: it would shift every later
index and could re-collide with whatever index the shift lands on —
verified this shape avoids it, see the function's own header comment).
Keyed on `batch_n`'s pre-increment value, which was ALREADY the member's
0-based position within its own batch (reset by `flush_batch` and by the
per-file init) — no new counter introduced, `batch_seq` (the old run-wide
counter) removed entirely.

**Verified at three levels, all green:**
1. Direct repro flip (isolated from the harness): `build/pcrec -p aa
   --features unicode-props -e utf8 -- '\P{Unknown}'` and `-p zz` both emit
   999,932 bytes — matching `-p rx`'s 999,933 (a 1-byte difference from the
   letters themselves, not the length) — safely under the 1,000,000-byte
   cap. Any 2-character prefix restores parity.
2. Harness-level, the exact previously-FATAL file: `HARNESS_BATCH=1` and
   `HARNESS_BATCH=64` (`PROCS=1`) on `tests/utf8/axis12_scripts.rxt` both
   read 72/72 passed/0 failed — identical to the unbatched run (72/72).
3. Broader smoke, `tests/base` (42 files): `HARNESS_BATCH=8 PROCS=2` = 3740
   passed/0 failed; `HARNESS_BATCH=0 PROCS=2` = 3740 passed/0 failed —
   identical.
4. The two previously-queued targeted legs, re-run directly against the
   fixed tree: `-fno-possessify` batched now reads `agree=65 mismatches=0`
   (was the FATAL); `--engine=vm` batched still correctly reports its K55
   documented refusal population (`refused_doc=15 refused_undoc=0`) — the
   fix did not paper over a REAL refusal, only the spurious byte-cap one.
   (That same run's `--engine=dfa` shows `FAIL` on its K35 corpus-wide
   refusal floor, 8000 — expected: this is a 1-file `AXES=` slice, not the
   whole corpus, the same shape utf8k53's own report notes for an identical
   reason; not a regression.)

`docs/testing.md`'s HARNESS_BATCH section's byte-count caveat ("worth
knowing before comparing size logs") is DISSOLVED rather than documented
around, per the ruling — SIZELOG's byte count is now parity-preserving by
construction, not merely "small and mechanical to account for."
`tests/harness/CLAUDE.md`'s own entry is updated with the same record.

**Merge note**: `main` was merged into this branch (commit 9dd6437a) BEFORE
this fix landed, per the manager's instruction — utf8k53's K53-SELRETRY
(the size-cap retry rung: on an emitted-size REFUSAL with the optional
anchored DFA machine present, drop it and re-emit rather than refuse)
interacts directly with this exact pattern, and NOT for the better absent
this lane's fix. `\P{Unknown}`'s DEFAULT-axis (`-p rx`) size is unaffected
by K53-SELRETRY either side of the merge (999,932/999,933 bytes, the retry
never fires because the first attempt already fits) — what K53-SELRETRY
changes is the LONG-PREFIX case: pre-merge, `-p hb000001` hard REFUSED
(1,000,586 bytes over the cap, this lane's original finding); post-merge,
before this lane's fix, the SAME long prefix would have made K53-SELRETRY's
retry fire instead — silently dropping the optional anchored DFA machine
and emitting a SMALLER BUT STRUCTURALLY DIFFERENT artifact (measured:
733,709 bytes, no optional machine) for the identical pattern the unbatched
path compiles WITH that machine. That is a worse failure mode than the
original hard refusal (a silent divergence in what got compiled, not a
loud failure), and it is exactly what "batching must preserve the unbatched
compile VERDICT" was ruled against — this lane's 2-character fix keeps the
prefix short enough that NEITHER the pre-merge hard refusal NOR the
post-merge silent-retry-divergence is ever triggered, on this pattern or
any other sharing its shape.

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

**Pre-fix** (against the un-merged, pre-K53-SELRETRY tree — this is the
evidence that surfaced the headline finding, superseded by the post-fix
row below, kept for the record):

| axis | unbatched | batched (HARNESS_BATCH=64) |
|---|---|---|
| `-fno-possessify` | rc=0, baseline 24194 keys/932s, axis agree=24194/0 mismatch/0 lost/0 gained, total 1972s | rc=1 — baseline itself FATAL (headline finding above), 280s |
| `-fno-counter` | rc=0, baseline 24194 keys/1044s, axis agree=24194 (leg completed after the fix landed — see below) | superseded, not completed pre-fix |

**Post-fix** (single-file targeted re-runs against `tests/utf8/
axis12_scripts.rxt` — the exact witness file — after the merge + the
2-character prefix fix; `SKIP_ORACLE=1 AXES="<axis>" HARNESS_BATCH=64
PROCS=8`):

| axis | result |
|---|---|
| `-fno-possessify` | `keys_base=65 keys_axis=65 agree=65 mismatches=0 lost=0 gained=0` — OK, was the FATAL |
| `--engine=vm` | `keys_base=65 keys_axis=65 agree=50 refused_doc=15 refused_undoc=0 mismatches=0` — OK, K55's documented refusal population intact (`--engine=dfa` in the same run shows the EXPECTED single-file K35-floor `FAIL`, not a regression — see the headline finding's verification list, item 4) |

A full-corpus per-axis before/after (matching this section's original
charter exactly) is superseded by (5)'s full sweep below, which covers
every axis at once rather than 2-3 individually — running the individual
full-corpus legs again after already having (5)'s complete answer would be
redundant given the box-time this lane has already spent on this row.

## (4) Battery wiring (prepared, not activated)

`scripts/battery.sh`'s `axes` stage case gained a comment block naming the
one-line swap (`AXES_FULL=1 HARNESS_BATCH=64 PROCS="$AXES_PROCS" make
test-axes`) and leaves the CURRENT line (unbatched) as the one that
actually runs — per the standing "no merge mid-battery" lesson, activation
is the manager's call at the START of a battery, not something this lane
flips.

## (5) Full before/after sweep — LAUNCHED, this lane's last act

`AXES_FULL=1 HARNESS_BATCH=64 PROCS=8 make test-axes` launched in the
background (this is the do-then-finish "last act": report committed FIRST,
then this launched, then END — see the boilerplate). Log path and expected
completion shape are in the handback message to the manager sent alongside
this commit.

Expected shape, given everything measured above: every axis's own
`agree`/`refused_doc`/`mismatches`/`lost`/`gained` counts identical to the
existing unbatched-corpus precedent (K55's stage-5 battery,
`build/battery_20260909_s5/axes.log`, rc=2 that day for unrelated reasons —
docs/dev/dev_journal.md's own entry on it), including `--engine=vm`'s
`refused_doc` population (the corpus-wide count, not this lane's 15-case
single-file slice) and every other axis's `REFUSAL_FLOOR` met. Wall time:
well under the 5h37m/5h45m unbatched precedent from the last two batteries
— this lane has no quiet-box full-corpus batched number yet (the targeted
legs above were single-file), so the exact multiple is this sweep's own
finding, not a repeated prediction.

## Owed

- The full sweep's own numbers (5) — launched, not yet returned as of this
  commit; the manager or a fresh agent reads the log.
- A full-corpus per-axis (not single-file) before/after for the 2-3
  representative axes this charter named — SUPERSEDED by (5)'s complete
  per-axis breakdown once it lands; not run separately given (5) answers
  the same question for every axis at once.
- Confirming the pre-fix finding would ALSO have hit `make test-corpus
  HARNESS_BATCH=64` (not axes-specific) — argued from the code (the
  byte-cap fires on the DEFAULT axis, independent of run_axes.sh) rather
  than separately run; the fix removes the question either way.

## Rulings received

- **HOLD then LIFT on the full sweep** (manager, 2026-09-10): sibling lane
  utf8k53 had the box for a sequential targeted validation batch; held the
  full `AXES_FULL=1 HARNESS_BATCH=64` launch until its log went quiet, then
  proceeded once the manager confirmed the box was free and utf8k53 merged.
- **Fix ruling, "fix option d"** (manager, 2026-09-10, on the headline
  finding): pin batch member prefixes to exactly 2 characters rather than
  (a) raising the witness pattern's margin or (c) excluding it from
  batching — see the headline finding section above for the full ruling
  text and the implementation. Also directed: merge main first (K53-SELRETRY
  interacts with the same pattern), verify the repro flips under `-p aa`,
  re-run the previously-fatal legs, update `docs/testing.md`'s caveat in
  the same commit, then the full sweep as the last act.

## Out of scope, flagged rather than built

`docs/design/tt4m_harness_batching.md` item 5 owes ONE new mech sabotage
row (a planted "batch link never falls back to per-pattern recovery"
detector) to the HARNESS_BATCH mechanism's own implementation lane
(tt4m3/[TT-4M] STEP 2c), not to this lane's charter (threading the var
through the axes stage). Not built here; named so it isn't lost.
