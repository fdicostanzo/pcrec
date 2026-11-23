# bsu6 report: R-47 unit U6 (everything except the timing itself)

Lane bsu6 (sonnet), branch lane/bsu6, cut from the kit branch lane/memfn-k1108 at 9d796f4ec (main with U1-U5 landed, abi 112).
U6 adds no product code: the only new file outside docs is `tests/memfn/g1_span_vector.py` (pcrec-side test tooling) and its
CLAUDE.md line. Nothing under `src/`, `lib/`, `cli/` or `memfn/src/` changed.

## STATE AT HANDOFF

- Delivered: the abi decision (no bump), the G1 manifest and dry run (with a harness this lane had to write; see G1), the C6
  timing plan, the charter checklist. Committed on lane/bsu6.
- OWED: two box-queue jobs, `kit-bsu6-axes` (`make test-axes`) and `kit-bsu6-reach` (REACH_ONLY over every mech row, after the
  axes job). Neither has a verdict yet. `make test` was not re-run on this tree (see OWED RUNS).
- Two findings for main and the kit manager (details in TIMING PLAN and CHARTER CHECKLIST):
  1. `cards.py` has NO command that times C6 or C6c: `run` reads STEP1 cards only (a comment at C6_CARDS in `cards.py` says "no step of `run`
     reads it"), and c6_rule.md says "the writer that fills the header is U6's timer". The timer does not exist; the cell
     machinery (`time_cells`) and the verdict reader (`c6_decide`) do. A timer is code under `memfn/tests/` and is outside
     this brief ("write NO timing job").
  2. §9.4 and the brief speak of "the G1 harness's DRY mode"; no such script existed in the tree (the nearest,
     `docs/dev/optloop/alpha_vedge.sh`, is a per-feature timing script for another feature). This lane wrote the manifest and
     dry mode as `tests/memfn/g1_span_vector.py`.
- Rulings file `docs/dev/lanes/bsu6_rulings.md`: re-read at the start and before this report; it was EMPTY both times. No
  ruling applied.
- Tree state for the owed jobs: product bytes identical to 9d796f4ec; the lane's commits add only docs, evidence and the one
  test-tooling file.

## ABI

Decision: NO abi event at U6, no bump. Evidence:
- U6 changes no emitted byte: no file under `src/` or `memfn/src/` is touched. U2 (abi 111, landed first) and U3 (abi 112 at L3's
  landing) were the byte movers; U4 and U5 moved none.
- §9.2's UNFILTERED grep at the base: `git grep -n -w 112 -- src tests docs/spec docs/testing.md memfn` = 149 hits (regenerate with that command), every hit reviewed by hand. The readers of the abi number are all at 112, none stale:
  - `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI 112`;
  - `docs/spec/match_api.md` §1 (the K80 guard's `!= 112`, the `#error` text, `#define PCREC_RX_ABI_H 112`), §6 (the
    `abi` row), §6 para 17 ( "It is `112` on every artifact", which has no "abi" word on its line: the D94 case, found by
    the unfiltered grep);
  - `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT=112`;
  - `tests/mech/sabotages/S693_abi_not_bumped.sh` `SAB_BEFORE='#define PCREC_ARTIFACT_ABI 112'`;
  - `docs/dev/history/abi_changelog.md` (outside the grep's paths, read by hand): "is `112` on every artifact today".
  - The rest of the 149 hits are unrelated numbers (112 bytes, 112 cases, mech timings, corpus rows).
  - `git grep -n 'v112'` over the same paths: no hit (no tree reader spells the subst `_v<N>` suffix).
- The (B) pin: `tests/codegen/run_recursion_identity.sh` `FILEPIN=d92d672be` (L3's landing pin). Three src commits followed it
  (K159: dc08453cc, 154d68d64, f77aeff78, "answers unchanged", merged at b4c2d4431), none an emitted-text move; the kit tip's
  `make test` (job 750, 26ef32ad5, GREEN) runs that identity gate over this same product tree. Not stale on that evidence.
- If a bump were needed the number is main's to give (113 or later); none is.

## AXES AND REACH

- REACH_ONLY's invocation, found in `tests/mech/run_sabotage_matrix.sh` ([MECH-REACHONLY], line 809): `REACH_ONLY=1 bash
  tests/mech/run_sabotage_matrix.sh` (all rows; it takes the box lock, builds nothing but the clean reference, ends with the
  `mech-reach-only: DONE rc=N` trailer, rc 1 when a row NOT declared UNREACHED reads unreached). Earlier counts for comparison:
  bsu3, 1,372 rows: 666 reached, 8 unreached (fixed), 16 declared unreached.
- Jobs (scripts in `$PCREC_TMPDIR/scratch/bsu6/`, queued copies under `worktrees/.boxqueue`):
  - `752-kit-bsu6-axes` (key `kit-bsu6-axes`): `make -j16 all` then `make test-axes` in worktrees/bsu6. cap 28800 (over the 3600
    soft limit and says why in its header: the target is one indivisible run, last full job altcatch-axes 19,687 s wall), est 19700.
  - `753-kit-bsu6-reach` (key `kit-bsu6-reach`): `make -s -j16 all` then `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh`,
    `--ready` = `boxqueue after kit-bsu6-axes`, cap 3600, est 900.
  - Both declare `boxqueue: not-before 2026-11-23T01:00` and both `--ready` gates return 75 from 18:15 through 00:59 (as in the
    u5tip job). The axes gate ALSO returns 75 for a start after 14:30, so a 5.5 h run cannot run into Frank's 20:00 hold; this is a
    deliberate addition to the brief. Dry-run and `--ready` output: "IN-LANE RUNS".
- Verdict reading: axes = the make error lines in the job log (`'\*\*\* \[(Makefile:[0-9]+: )?test-'`), never "sections ran"; reach =
  the `mech-reach-only: DONE rc=0` trailer plus the unreached list.

## G1 MANIFEST AND DRY RUN

Tool: `tests/memfn/g1_span_vector.py` (new; pcrec side; opt-in, heavy, no make target). `manifest` compiles every distinct corpus
pattern (every `.rxt` under the tree, source file kept) and every bench pattern file (392 `*.rx` read from
`/home/pcrec/projects/pcrec-bench/bench/*/patterns/`, read only), default vs `--memfn=no-span-vector`, at BOTH layers (no flag, and
`-fmemfn-simd=x86-64-v3`) x byte/utf8 x c-default/c-vm, and writes one row per (pattern, layer) that differs in at least one cell. It
reads nothing of the kit's (`moved` plays no part). `dry` bins the REAL movers and times nothing.
- Population compiled: 6,109 distinct patterns. Run under `scripts/boxlock run --label bsu6-g1`.
- Movers per layer (manifest rows 56 = 28 x 2):

| layer | movers (distinct patterns) | real (SPAN-SEED excluded by path) | SPAN-SEED-only |
|---|---|---|---|
| SIMD-off | 28 | 3 (corpus 0, bench 3) | 25 |
| SIMD-on (x86-64-v3) | 28 | 3 (corpus 0, bench 3) | 25 |

- The 3 real movers at each layer, byte and utf8 on c-default, none on c-vm: `[0-9a-f]{32}` (window), `\b[0-9a-f]{32}\b` (window),
  `\d{32}` (scan). This matches §0.1 (3 real sites, 0 real corpus sites). 28 = §9.3's measured byte floor.
- Bins (op, length decade), floor 8, real movers only: `(window, 10-99)` 2 and `(scan, 10-99)` 1 at each layer: all
  `UNREACHED (n < 8)`, printed. op and length are binning labels read off the default artifact's added lines (`_sh[` present =
  window; length = 1 + the largest `_c + N` offset: all three read 32).
- Floor witness (K35): SPAN-SEED movers 25 at each layer, printed separately, so the manifest is not empty-blind.
- Dry verdict: `g1 dry: OK`, rc 0. Timing: NOT RUN (no window booked, §9.4); trigger: a bin reaches 8 real movers.
- Controls run: the manifest with its SPAN-SEED rows deleted fails the dry run ("floor witness is EMPTY", rc 1); the manifest with
  its bench rows deleted fails it ("real site ... is not a mover" for all three, rc 1).
- Evidence: `docs/dev/lanes/bsu6_evidence/manifest.tsv`, `g1_dry.txt`.

## TIMING PLAN

For main to ask Frank for a window. Text only; no timing job written. Source: `cards.py plan` (kept as `bsu6_evidence/plan.txt`) and
`cards.py dry RUNDIR --cards C6,C6c` (276 cells built and answer-gated, failures 0, 28 distinct compiles, 42 timed texts x 4 layout
variants = 168 exes, pools refused 0; deny and reach check 14 pairs, failures 0; reach build 92 cells, N/A 8).

Cells (a cell = pattern x regime x layer, three arms V / H64 / H64.b, 15 launches = 5 rounds x 3 arms):

| card | layer | cells | not timed (void by method: not-warm, short-subject) | N/A (reach 0 calls) | timed and readable |
|---|---|---|---|---|---|
| C6 | on (gcc -O2, -fmemfn-simd=x86-64-v3) | 52 (156 arm rows) | 16 | 4 (near-miss at hex17, hex32, hex33, hexb32) | 32 |
| C6c | off-clang (clang -O2, SIMD-off) | 20 (60 arm rows) | 6 | 2 (near-miss at hex32, hexb32) | 12 |
| C6c | off-os (gcc -Os, SIMD-off) | 20 (60 arm rows) | 6 | 2 | 12 |
| total | | 92 (276 arm rows) | 28 | 8 | 56 (840 first-pass launches) |

(plan's own "108 timed" / "84 timed" count the N/A cells, which the reach build removes.) LAUNCHES = 5. Launch unit and re-time rule
(c6_rule.md): an arm's reading is the median of its 5 launches, spread = middle three; FLOOR = max(0.15, spreads); a floor above 0.30 is
INCONCLUSIVE-NOISE. Every reading LOSS and WIN and every A/A non-TIE is re-timed on a FRESH pool (4 new layouts per text, so up to 168
more compiles) with fresh launch draws; it stands only if the re-time agrees. A/A rate above 0.05 makes the (card, layer) verdict on that
box VOID. Verdict is first-match; V stays CANDIDATE until every bench box that runs it reads NO LOSS; a repeated LOSS on any box blocks the
level. Rule sha 9a2875a6bf089837.

Wall time:
- MEASURED (this box, 02:35, box lock free, outside 18:15-01:00; one probe, no quiet gate, so a bound on cost not a reading): cell
  `c6_hex32` hit-dense, 15 launches in 0.88 s; `c6_hex32` miss-heavy, 15 launches in 0.84 s (about 0.057 s per launch, 1 MiB subject;
  the plan's UNMEASURED constant is 0.080).
- ESTIMATED, dev box (Zen 4), basis the probe: first pass 840 launches x 0.06 s = about 50 s; a worst-case re-time of every cell (WINs
  are re-timed everywhere) doubles it, plus up to 168 fresh-pool compiles (the dry built the same count in about 100 s at JOBS=12);
  plus 710's fixed overhead (quiet sample: 60 s of /proc/stat samples and 10 calibration repeats, about 80 s with the void allowance).
  Measuring about 5-6 min; with 710's 600 s quiet wait about 16 min. Ask for a 30 min window (cap 3600 s, the soft limit).
  Cross-check from the kit's earlier timed card job 710 (`rule_710.md`, job `710-kit-blockconfirm`, run record
  `.boxqueue/done/20261120T232303.*-710-kit-blockconfirm`): 4,200 arm-cells in 6,821 s (1.6 s per arm-cell, 0.81 of its own 8,392 s
  estimate), with 494 re-timed; C6's 168 timed arm-rows by that rate would be about 270 s. The two bases agree to within a factor of
  about 1.5.
- ESTIMATED, ubuntubudu (Zen 1): NOT queried (ssh to the box returned "No route to host" at 02:36). From the house record
  (Ryzen 5 1600, AVX2 as 2x128, no AVX-512; 6 cores / 12 threads) per-launch cost is likely about 2x and compiles about 2x slower:
  about 15 min measuring, ask for 45 min. UNMEASURED; the per-launch figure there is the first thing the run should read.
- G1: no timing length (none booked; §9.4). If its trigger ever fires, its cells are C6's, so about the same length.

Box needs:
- Quiet-gated, taskset pinned to ONE core and its SMT sibling idle (CPU default 15, sibling 7 on the dev box, read from sysfs).
  `CPU=` must be set on ubuntubudu (12 threads: 15 does not exist). No other job, no Frank sessions, the ghostty iowait caveat applies;
  host the session in tmux. Not in 20:00-01:00. `boxqueue: idle-ok` (quiet healthy stage).
- Needs gcc 15.2, clang (clang 21.1.8 here; C6c's off-clang layer) and the frozen `build/pcrec`; the run is one binary (RECORD header
  names its sha).
- Dev box (Zen 4): verdict-grade for the x86-64-v3 layer. ubuntubudu (Zen 1): the second verdict box, via main (D144 add. 4), slot
  request, nothing runs there from this lane. Mac: directional only (Q43); C6's layer is x86-64-v3, so it cannot run there at all; C6c's
  SIMD-off cells could give a regression check of the portable text, never a verdict.
- BLOCKER (finding 1 above): no command times C6/C6c. Before any window is asked for, the kit needs the timer: a `cards.py` command
  that drives `time_cells` over `cells(cards=C6_CARDS)`, the re-time on a fresh pool, the quiet sample and the window deadline (710's),
  writes the `#c6` RECORD header (`c6_header`) and feeds `c6_decide`. Untimed machinery exists for each part; none is wired.
- Observation, not a reading: in the probe V read 0.1115 ns/B against H64's 2.02 at hit-dense and a tie at miss-heavy; the hit-dense gap
  is far above anything the claim predicts, so the first thing the real run should check is that the arms answer the same work there
  (the gate printed `ok 32768` for all three arms and all four variants).

## IN-LANE RUNS

All outside 18:15-01:00 (02:25-02:45 local), box lock free at each start (`scripts/boxlock status`), TMPDIR under scratch/bsu6.
- `make -j8` of the lane tree (build/pcrec for the G1 manifest and the dry).
- `cards.py plan`: rc 0, 1,741 lines (evidence copy).
- G1 manifest (boxlock label bsu6-g1, -j12) twice (the second after a label fix): 6,109 patterns, 56 rows; `g1_span_vector.py dry`: OK;
  both controls red as designed.
- `cards.py dry RUNDIR --cards C6,C6c` (boxlock label bsu6-dry): cells 276 built and gated, 0 failures.
- One-cell timing probe (boxlock label bsu6-probe): two cells, 15 launches each, 0.88 s and 0.84 s (TIMING PLAN).
- `tests/memfn/run_arch_blind.sh` (new file contains the word `x86-64-v3` only): 32 passed, 0 failed. `scripts/check_claudemd_size.sh
  --all`: within limits.
- The queued jobs' `--dry-run` and `--ready`, shown below after queueing.

Queued at 02:47 with `scripts/boxqueue add` (each dry-run again at enqueue, accepted). Dry-run output (identical to the queued copies):

    752-kit-bsu6-axes --dry-run:
      would run in worktrees/bsu6: make -j16 all && make test-axes
      boxqueue: cap 28800 / patience none / not-before 2026-11-23T01:00 / est 19700
      boxqueue: expect none reason=make test-axes is exec'd, so its rc is the job's rc; ...
    753-kit-bsu6-reach --dry-run (after VALIDATE_ONLY field validation passed):
      would run in worktrees/bsu6: make -s -j16 all && REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh
      boxqueue: cap 3600 / patience none / not-before 2026-11-23T01:00 / est 900
      boxqueue: expect none reason=the matrix is exec'd, ...

`--ready` once, at 02:4x (inside the allowed hours): axes rc 0; reach rc 1 "no job kit-bsu6-axes in the queue" before the axes job was
queued (it is a dependency gate; the reach job is held until the axes job ends). The clock gates were drilled with a faked `date` (axes:
00:30 rc 75, 00:59 rc 75, 01:00 rc 0, 10:00 rc 0, 14:30 rc 0, 14:31 rc 75, 18:15 rc 75, 19:00 rc 75; reach: 00:30 and 18:15 rc 75). The axes
job is expected to START NOW (box free, gate open); the reach job follows it.

## OWED RUNS

| key | what | verdict line |
|---|---|---|
| `kit-bsu6-axes` | `make test-axes` on lane/bsu6, cap 28800 s, est about 5.5 h; start 01:00-14:30 only | make error lines in the job log; GREEN = no `*** [Makefile:N: test-...] Error` line |
| `kit-bsu6-reach` | `REACH_ONLY=1` over every mech row, after the axes job | `mech-reach-only: DONE rc=0`; list any row not declared UNREACHED that reads unreached |

Not queued (not in the brief): `make test` async on this tree. The kit tip's job 750 (26ef32ad5, abi 112, GREEN) covers the same
product bytes; the landing lane runs its own `make test` at the landing base. No mech detection row was added (no new check besides the
G1 tool, which has its own two controls), so no sabotage id was taken (S3555-S3559 unused).

## CHARTER CHECKLIST

| promise (source) | artifact, or OWED with owner and trigger |
|---|---|
| U6: the abi package at the landing base, §9.2's unfiltered grep (§14) | ABI above: grep done and reviewed, all readers at 112, no bump. The re-pins list of §9.2 is empty because no byte moves |
| §9.1 the number at landing | none taken; if a bump arises it is main's (113+) |
| U6: `make test` async (§14) | OWED to the landing lane (job 750 covers the same product bytes at the kit tip; see OWED RUNS) |
| U6: `make test-axes` (§14) | job `kit-bsu6-axes`; owner: the kit manager reads the verdict |
| U6: REACH_ONLY (§14, BOILERPLATE) | job `kit-bsu6-reach`, after the axes job |
| §9.3 stamps, pins, axes row | unchanged by U6 (U2/U3/U4 delivered them); `make test-axes` re-checks the `span-vector` DIFFER rows (28 / 20 floors) |
| §9.4 G1 manifest before any timing, with its count; both layers; pcrec-side diff, never the kit's `moved` | `g1_span_vector.py manifest`, `bsu6_evidence/manifest.tsv` (28 movers per layer, 3 real) |
| §9.4 bins (op, length decade), floor 8, real movers only, SPAN-SEED excluded by path and printed separately as the floor witness | `g1_span_vector.py dry`, `bsu6_evidence/g1_dry.txt`, both controls red |
| §9.4 dry run: counts printed, UNREACHED printed | done, `g1 dry: OK` |
| §9.4 trigger to time G1 (a bin reaches 8 real movers): "a row for main (§17)" | OWED: owner main (files the plan row); trigger as stated. Not filed by this lane (plan.md is main's) |
| §8 C6's timing on each bench box; V stays CANDIDATE until then | OWED: owner main (Frank's window) after the kit builds the timer; boxes: dev box Zen 4, ubuntubudu Zen 1 via main. Plan in TIMING PLAN |
| c6_rule.md: "the writer that fills the header is U6's timer" | OWED and NOT BUILT: the kit manager charters it (code under `memfn/tests/span_forms/`, outside this brief); trigger: before main asks Frank for the window |
| §8 rows for main: `--harness=span-vector=force` lever and `span-vector-body` lever; trigger a C6 or Zen 1 run questions a bound | OWED: owner main to file; not build scope |
| §8 plan row for the clang/PIC gaps (C6c named gaps: clang -O3, `-fPIC -shared`) | OWED: stated in c6_rule.md CLAIM; no lane action |
| §9.5 spec hunk | none: U6 changes nothing a caller observes (D80) |
| §14 note: the identity gate is a delivery step of U2/U3 | not U6's; not re-run (no byte moves) |
| `plan` / `dry` green with no timing (U5's promise, re-checked) | re-run here: plan rc 0; dry 276 cells, 0 failures |
| `tests/memfn/CLAUDE.md` names the new file | done |
