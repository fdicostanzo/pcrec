# tt4m3 — [TT-4M] STEP 2c: HARNESS_BATCH=N implementation

Lane tt4m3 (sonnet), 2026-09-08. Implements `docs/design/
tt4m_harness_batching.md` as revised under r55 (`docs/dev/reviews/
2026-09-08-r55-tt4m-batching.md`) in `tests/harness/run.sh`. Box rules held
for this whole lane (utf8s4 has the box tonight): CONSTRUCTION plus
SMALL-SLICE SMOKES ONLY — no `make test`, no full corpus, no multi-minute
sweeps. The full acceptance battery (2d) is explicitly the manager's, run
after the box frees; every item below that needed it is marked **OWED**
with the exact command.

## What shipped

- `HARNESS_BATCH=N` (unset/`0` = today's per-pattern path, byte-for-byte
  unchanged — verified, not assumed, see "Smoke results" below).
- `tests/harness/dispatch_gen.sh` (new file): `gen_dispatch_c PREFIX...`, a
  bash port of `studies/tt4m_batchrun/dispatch_gen.py`'s dispatch.c
  generator (same `decode()`, same give-up-word switch, default-route-only
  scope). Kept in bash so `run.sh`'s dependency profile does not grow.
- `run_case_loop <exe> <mode> [idx]` — the per-case verification loop
  (H11 cross-check, `gu`/give-up/timeout/crash arms, `m`/`n` compare, `g`/
  `gp` checks, RXTDUMP) extracted VERBATIM out of `flush_block`'s body so
  both the unbatched (`mode=standalone`) and batched (`mode=batched`) paths
  share one implementation — they cannot silently drift apart because
  there is only one copy of the logic.
- `flush_block` gains a batching-eligibility check, computed right where
  `cur_route` is already computed per case (item 1 of the design), BEFORE
  its own compile-time decision: a `perr` block, an H11-targeted block, or
  a block carrying any routed cell (`frames-buffer=`, or a non-`default`/
  non-empty `RXTROUTE` floor) is NEVER eligible and always takes the
  unchanged standalone path regardless of `HARNESS_BATCH`.
- `stage_block_for_batch` / `flush_batch` / `unpack_batch_member` /
  `batch_member_compile` (new functions): stage an eligible block's own
  pcrec compile under a fresh run-wide-unique prefix; flush at N members or
  at end of file (batches never cross files); per-member `-c` sub-compiles
  at the ordinary UNSCALED D45 budget (so SIZELOG's per-pattern gcc CPU/
  wall stays exact and the budget is never diluted N-fold); one
  `dispatch.c` sub-compile; one link; an N-scaled WALL-ONLY backstop around
  the whole sequence (item 6 step 3). A member's own `-c` failure is
  dropped from the link and reported in the IDENTICAL shape an unbatched
  compile failure is reported in.
- `tests/lib/size_count.sh`'s `size_count_row` fix (see Findings).

## Findings

**F1 — a real, non-batching-specific bug in `size_count_row`.** It
hardcoded the literal macro names `RX_ENGINE`/`RX_VM_PREFILTER`/
`RX_VM_RUNGS`, which only exist under those spellings when the artifact's
own `-p` prefix is exactly `rx`. Every caller in the tree used that prefix
until HARNESS_BATCH's per-member sub-compiles (`hbNNNNNN` prefixes), so the
assumption never showed up as false — SILENTLY: three blank stamp columns,
not a loud failure, on every batched SIZELOG row (measured:
`tests/base/dot.rxt:12` read `dfa` unbatched, empty batched, byte count
unaffected). Fixed by taking the prefix as an explicit third parameter
(default `"rx"`, byte-for-byte unchanged for both pre-existing call sites).
**A first attempt at the fix was itself wrong** — it derived the prefix
from `FILE_H`'s own basename, which broke the UNBATCHED case too, because
`run.sh`'s unbatched path always names its output `gen.c`/`gen.h`
regardless of `-p` (the prefix and the filename are independent facts).
Caught by re-running the *unbatched* leg of the SIZELOG smoke after the
first fix, not assumed correct from the batched leg alone.

**F2 — bash's `read` collapses/strips TAB-delimited empty fields even
under a single-character `IFS`.** The first implementation packed a batch
member's per-case data with TAB as the field separator (`IFS=$'\t'`). This
is WRONG: TAB (like space and newline) is classified as "IFS whitespace"
and bash collapses consecutive occurrences and strips them at field
boundaries regardless of what else IFS contains — a fact that does not
depend on IFS having other characters in it, only on IFS containing
*any* whitespace character at all. Since an `n`/`ns` case's `start`/`end`
fields are always empty, this shifted every field after them on the very
first such case, so `case_startpos` silently read as `""` instead of
`"0"`. Found via a LIVE answer-identity mismatch (`nomatch` cases reading
`got ''` instead of `nomatch`, isolated with a temporary debug trace,
confirmed by a standalone `bash -c` reproduction of the exact byte
sequence before touching the fix) — not assumed from reading the packing
code. Fixed by using `\x01` (SOH) as the delimiter, verified with the same
standalone reproduction before re-testing the harness.

**F3 (named, not a defect) — SIZELOG's per-pattern gcc CPU/wall column
changes MEANING under batching, and the byte count is not perfectly
axis-invariant.** The per-member `-c` sub-compile times ONLY that compile
(no `driver.c`, no link), where the unbatched number always included
compile+link+driver.c — so a `scripts/size_diff` comparison across the
`HARNESS_BATCH` axis will show a systematic CPU/wall DROP for every
pattern that reflects this shape change, not a real emitter/compiler
speed improvement. The byte count is also a function of the artifact's own
identifiers, which embed the `-p` prefix, so a longer generated prefix
(`hb000042` vs `rx`) inflates the reported source-byte count by the
prefix's own length times its occurrence count. Both are documented in
`docs/testing.md`'s new "`HARNESS_BATCH`" section so nobody reads either as
a finding when comparing size logs across the axis later.

**F4 — the item-5-owed mech sabotage row needs a suite-wiring decision
first, not just a new file.** `docs/design/tt4m_harness_batching.md` item 5
asks 2c to add ONE new sabotage row for "batch link never falls back to
per-pattern recovery" (the rare solo-relink path in `flush_batch`). I
checked `tests/mech/run_sabotage_matrix.sh`'s `harness)` suite arm
(line ~1930): it invokes `tests/harness/run.sh` with `PCREC`/`CC`/`PROCS`
set and **`HARNESS_BATCH` is not among them** — so under `make mech`'s
CURRENT wiring, the harness suite arm never sets `HARNESS_BATCH` at all,
which means every line of code this lane added (not just the fallback
path) is structurally unreached by `make mech` today, for a reason that
has nothing to do with the sabotage itself. Writing the row without also
adding a suite-wiring change (a new mech suite name, e.g. `harnessbatch`,
that runs `tests/harness/run.sh` with `HARNESS_BATCH=N` set) would either
score the row a hand-waved `SAB_EXPECT=UNDETECTED` forever (defeating its
purpose) or silently do nothing. That wiring decision is bigger than one
row and is either the manager's call or STEP 2d's — see OWED below for the
drafted row text, ready to add the moment the wiring lands.

## Rulings received

None — no ruling was requested or needed; the design note (as revised)
answered every implementation question this lane hit.

## Smoke results (this box, HARNESS_BATCH unset vs N in {1,2,3,4,5,8},
answer-identity by full stdout diff unless noted)

| slice | files | what it covers | result |
|---|---|---|---|
| base/dot.rxt, base/literals.rxt | 2 | plain m/n cases, `HARNESS_BATCH=2` | byte-identical (31 cases) |
| assertions/dollar.rxt + base/{dot,literals}.rxt | 3 | run_case_loop extraction alone, HARNESS_BATCH unset, vs. main's run.sh | byte-identical (regression check on the refactor itself) |
| harness/giveup.rxt, captures/basic.rxt, base/syntax_errors.rxt, recursion/framebuffer.rxt | 4 | `engine vm`/`budget`/`gu`, `g`/`gp`, `perr` exclusion, `frames-buffer=` routed exclusion, `HARNESS_BATCH=3` | byte-identical (137 cases) |
| base/caseless.rxt, classes/classes.rxt, utf8/axis01_encoded_length.rxt | 3 | `flags i`/`features`/`encoding` directives, `HARNESS_BATCH=5` | byte-identical (374 cases) |
| captures/basic.rxt | 1 | `g`/`gp` + pending-vm counting, `HARNESS_BATCH=3` | byte-identical (45 cases, pending-vm 0/0) |
| base/dot.rxt, base/literals.rxt | 2 | `SIZELOG=...`, `HARNESS_BATCH=2` | 15/15 rows both; byte counts differ per F3 (expected); engine/rungs/prefilter stamps correct after F1's fix |
| base/dot.rxt, base/literals.rxt, harness/giveup.rxt | 3 | `PROCS=2` + `HARNESS_BATCH=3` together | byte-identical (33 cases; only the expected extra `parallel: N of N...` line differs) |
| base/dot.rxt, base/literals.rxt | 2 | `RXTDUMP=...`, `HARNESS_BATCH=1` (finest batch granularity) | RXTDUMP rows identical (sorted), summary identical |
| base/dot.rxt | 1 | degradation: one member's `.c` corrupted via a temporary, since-removed debug hook (`TT4M_TEST_CORRUPT_MEMBER`) | corrupted member reported EXACTLY as a standalone compile failure; 13 of 14 cases in that batch still pass via the free per-member attribution/relink path |
| (any) | — | `HARNESS_BATCH=abc` (invalid) | rejected: `HARNESS_BATCH must be a non-negative integer` |

Hash-pinned arm region (`tests/rxtsource/run_rxtsource_tests.sh`'s check):
diffed the exact BEGIN/END PINNED ARM REGION text between `main` and this
branch — byte-identical, confirmed by direct `diff`, not by grep-for-the-
markers-in-the-diff alone.

Existing SAB_FILE-anchored sabotage rows (`S11`, `S194`, `S196`, `S198`,
`S199`, `S203`, `S205`, `S43`): all eight anchor texts re-verified present,
byte-for-byte, in the current `tests/harness/run.sh`/`tests/lib/
gen_timeout.sh` by direct `grep -F` of each row's own `SAB_BEFORE` text —
none moved, matching the r55 design's item-5 disposition (they sit in the
`.rxt`-parsing arm chain or `gen_cc`'s own body, neither of which this
lane touched).

## OWED to the manager's 2d (exact commands + expected shape)

1. **Full `make test` at `HARNESS_BATCH` unset must be BYTE-IDENTICAL in
   counts to a pre-change `make test`.**
   ```
   make test 2>&1 | tee /tmp/test_before_batch.log   # on main, or this
                                                       # branch with
                                                       # HARNESS_BATCH unset
   ```
   Expect identical pass/fail/pattern-compile-failure/size-log-row counts
   in both runs (this lane's branch with `HARNESS_BATCH` unset should be
   indistinguishable from `main`).

2. **`HARNESS_BATCH=64` (the STEP 2a-recommended N) must be
   answer-identical, with wall/CPU recorded and ARCHIVED** (R55-10's
   evidence bar — 2a's own sweep evidence was scratch and unarchived; this
   is the first HARNESS_BATCH number that must not repeat that gap):
   ```
   HARNESS_BATCH=64 PROCS=8 make test 2>&1 | tee /tmp/test_batch64.log
   ```
   Compare pass/fail/pattern-compile-failure/size-log-row counts against
   item 1's baseline (must match exactly); record wall/CPU deltas; archive
   both logs plus a short summary under a `docs/dev/` evidence directory
   (e.g. `docs/dev/tt4m_2d_evidence/`) per R55-10's own naming — this
   report does not create that directory since it has no numbers to put in
   it yet.

3. **`make test-axes` under `HARNESS_BATCH=64`** — the design's own axis
   compatibility claims (GENCFLAGS/LINTGEN/CLANGGEN/the deny-family flags
   all still reach the right compile) are argued from reading the code in
   the design note; this is the first LIVE check of them together.
   ```
   HARNESS_BATCH=64 make test-axes 2>&1 | tee /tmp/axes_batch64.log
   ```

4. **`make mech`** — confirm the eight SAB_FILE-anchored rows this report
   already grep-verified as unmoved still score DETECTED/UNDETECTED
   exactly as before (a grep check is not a mech run); separately, decide
   F4's suite-wiring question (does a new `harnessbatch` mech suite arm
   get added, running `tests/harness/run.sh` with `HARNESS_BATCH` set?)
   before adding the item-5-owed new row. Drafted row text (NOT committed,
   pending the wiring decision):

   ```
   # S237 (draft, NOT YET ADDED — see tt4m3_report.md F4 for why) — the
   # RARE link-only-failure fallback in flush_batch (tests/harness/run.sh)
   # is REMOVED: instead of relinking each surviving member SOLO when the
   # batch's shared link fails despite every member's own -c compile
   # succeeding, the sabotaged version just reports every survivor as a
   # compile failure with no attempt at recovery.
   #
   # Requires a mech suite arm that runs tests/harness/run.sh with
   # HARNESS_BATCH set (the plain `harness` arm never does) AND a way to
   # force the link-only-failure path (e.g. a corpus fixture whose
   # generated dispatch.c collides on a symbol, or a HARNESS_BATCH-test-only
   # hook analogous to this lane's temporary TT4M_TEST_CORRUPT_MEMBER, made
   # permanent and documented if this row needs it) -- neither exists yet.
   SAB_ID="S237-batch-link-fallback-removed"
   SAB_FILE="tests/harness/run.sh"
   SAB_SUITES="harnessbatch"   # DOES NOT EXIST YET -- see F4
   SAB_DESC="flush_batch's rare link-only-failure fallback (solo relink per
   surviving member) is removed; every survivor is reported as a compile
   failure instead of being individually recovered"
   SAB_BEFORE='    echo "$cur_file: HARNESS FAILURE: $CC failed to link the batch (N=${#survivors[@]} surviving members, dispatch.c: $dc); falling back to per-pattern relink to isolate the cause: $GEN_CC_LOG" >&2
       for mi in "${survivors[@]}"; do
           local px="${bm_prefix[$mi]}"'
   SAB_AFTER='    # SABOTAGE S237: no fallback -- every survivor just fails
       for mi in "${survivors[@]}"; do
           local px="${bm_prefix[$mi]}"
           unpack_batch_member "$mi"
           local ci
           for ci in "${!case_kind[@]}"; do
               record_fail "$cur_file" "${case_line[$ci]}" "compile failure (see above; SABOTAGE S237)"
           done
           continue
           local px="${bm_prefix[$mi]}"'
   ```
   (The `SAB_AFTER` above is a sketch, not verified against `lib/
   replace.py`'s anchor-occurrence-count rule — whoever adds this row for
   real should re-derive `SAB_BEFORE`/`SAB_AFTER` from the tree at merge
   time rather than copy this verbatim, per BOILERPLATE's "a re-anchor
   needs its intent re-verified.")

5. **The Linux executor arm** (per the design's item 7 validation plan and
   the travel-topology rule) — this lane never ran on Linux at all (Mac-only
   worktree, box rules). `studies/tt4m_batchrun/` tooling is portable; a
   live run.sh HARNESS_BATCH pass on ubuntubudu via pcrecdev2's executor
   channel is the remaining item the design's own §7 names.

## Files changed

- `tests/harness/run.sh` — `HARNESS_BATCH` env var + validation +
  `PROCS>1` threading; `run_case_loop` extraction; `stage_block_for_batch`/
  `flush_batch`/`unpack_batch_member`/`batch_member_compile`; the
  eligibility check inside `flush_block`; per-file batch-state resets and
  the end-of-file flush. Header comment documents the new env var.
- `tests/harness/dispatch_gen.sh` (new) — the dispatch.c generator.
- `tests/lib/size_count.sh` — `size_count_row` gains an explicit `PREFIX`
  parameter (F1).
- `tests/harness/CLAUDE.md`, `tests/lib/CLAUDE.md`, `docs/CLAUDE.md`,
  `docs/testing.md`, `docs/dev/plan.md` — documentation for all of the
  above, including F1-F3 as findings future readers of a size log need.

Never merged to `main`; branch `lane/tt4m3`, worktree `worktrees/tt4m3`.
