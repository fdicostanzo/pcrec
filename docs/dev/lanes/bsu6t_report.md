# bsu6t report: R-47 U6, the C6/C6c TIMER in cards.py (no timing run)

Lane bsu6t (opus), branch lane/bsu6t, cut from lane/bsu6 (its tip ace36d05c, one commit past the brief's 09c206cb0: bsu6's R-1
estimate fix, docs only). Test harness code only: `memfn/tests/span_forms/cards.py`. Nothing under `src/`, `memfn/src/`, `lib/`,
`cli/`; no emitted byte; `c6_rule.md` and `rule_710.md` unedited (rule sha 9a2875a6bf089837, 710's 6351bff3901e3955, both
computed and checked by `c6selftest`). NO timing run, probe or real launch of any kind.

## STATE AT HANDOFF

- STATE: delivered. Committed on lane/bsu6t. The timer `cards.py time` and the reader `cards.py c6decide` are built. The
  CPU-quiet control is ported into cards.py once (R-1). `c6selftest` has 52 rows, 0 failed (it had 27). Three DRY runs went end to
  end and each record round-trips through the standalone reader.
- Rulings file `docs/dev/lanes/bsu6t_rulings.md`: re-read at each checkpoint (before the dry runs, before make strict, before
  this report). Last entry applied: **R-1** (kit manager, 2026-11-23: plan APPROVED; conditions (a)-(d), each answered below).
- Premise finding, sent to the kit manager before R-1. The brief said the quiet gate is in cards.py, and it is not. It lived only in
  710's untracked harness `scratch/memfn/blockconfirm/confirm.py`, and the 600 s quiet wait is the job script's (the slot
  Waiter). R-1 ruled the port.
- One process breach to disclose: the first DRY run (`--patterns c6_hex32,c6_dig32`) compiled the fresh re-time pools of 18
  texts. That is 72 gcc/clang compiles at JOBS=4, about 100 s, outside `scripts/boxlock run`. RUNS.md's sweep cap is 50. I had
  counted 12 pools (48 compiles) and forgot that c6_hex32 is in C6c as well. The box lock was held by `kit-bsu6-axes`
  (`make test-axes`, not a timing job). Later runs compiled nothing (every exe cached).

## WHAT THE TIMER DOES

`cards.py time RUNDIR [--cards C6,C6c] [--deadline EPOCH|+SECONDS] [--dry [--dry-model tie|exercise] [--patterns P,..]]`
(`cmd_time` / `_time`). The steps, in order:

1. Refusals: rule_710.md's sha must equal 710's recorded sha. `--cards` takes only C6 and C6c. `--dry-model` and `--patterns`
   work only under `--dry`, so a timing always covers the whole population.
2. `check_c6` (the C6 deny-and-reach text check, as `dry` runs it): any failure refuses.
3. The REACH build (`c6_reach`): one untimed, instrumented pass per (card, pattern, regime, layer) over the 1 MiB timed subject.
   A cell with 0 calls is N/A and is not timed. A hit-dense cell with 0 calls refuses (the build's own control).
4. Every pool the run can time is BUILT and PROVED before the clock. These are the first-pass pool and the re-time's FRESH pool
   (`arm_pool(..., retime=1)`) of every timed (pattern, arm, layer). `pool_proof`/`pool_refusal` run on both, exactly as `dry`
   runs them, and any refused pool refuses the run.
5. The record's head, written before any timing (`c6_record_head`), in `RUNDIR/results_c6_<run>.tsv`:
   - line 1: the `#c6` header (`c6_header`), with rule, rule710, form (`mf_form_hash("span-vector")` from
     `tests/memfn/arm_fixtures.c --hash` linked against the frozen `libpcrec.a`), binary (sha-256 of the frozen `build/pcrec`, 16
     hex), `cc.<layer>` per layer, widths and run;
   - `#run`: launches, pool, cpu, deadline, dry, cards and subject;
   - the column line;
   - one `cell` line per population cell with its span calls.

   The run id is a fresh one (`start_timing`).
6. The QUIET SAMPLE (`QuietControl.sample`): 60 one-second /proc/stat samples of the pin's SMT sibling and of the pin, then 10
   launches of the calibration exe (H64 of the first timed cell, variant 0). The thresholds come from rule_710.md:
   - CPU7_MAX = min(20 %, max(5 %, 2 x the sample's maximum)), with the QUIET SAMPLE BUSY banner when capped;
   - NIVCSW_MAX = max(2, 2 x the calibration's maximum), per T_CAL.

   They are written to `quiet_sample_c6_<run>.tsv` and to the `#qc` record line.
7. The FIRST PASS goes through `time_cells`, the one copy, extended with keyword hooks. Each cell is timed in LAUNCHES rounds of
   one launch per arm, in `round_arms` order, and each launch's variant is drawn by `launch_variant` from the arm's own pool.
   The draw is recorded per launch in the row's `variants`. Each launch goes through `QuietControl.launch`, which reads the
   sibling's busy fraction over at least 100 ms and the child's nivcsw delta. A VOID launch is re-timed up to 2 more times on
   the same variant, and logged to `voids_c6_<run>.tsv`. An arm still short of 5 valid launches reads None, which makes the cell
   INCONCLUSIVE-NOISE.
8. The RE-TIME covers every cell whose first pass owes one (`c6_owes`: a reading WIN or LOSS, or an A/A non-TIE). It times all
   three arms on the fresh pool, with fresh draws (salt `retime`, against `first`), under the same unit and floor.
9. The WINDOW: `--deadline` (absolute epoch, or `+SECONDS` from the start). No cell group of either pass starts at or after it,
   and its rows are written `notrun`. The job script computes 710's min(STOP_AT, start + cap - 600 s).
10. The record ends with `#end` (status, NOT-RUN counts, owed, void launches, wall). The timer then runs `c6decide` on its own
    file. Exit codes: 0; 1 when a gate failed (a wrong answer); 2 when refused; 4 when TRUNCATED, i.e. a cell of either pass was
    not started.

`cards.py c6decide RESULTS` (`c6_read` + `c6_decide` + `c6_report`) gives the verdict from the record alone. It refuses (exit 2)
in these cases:
- a missing or stale `#c6` header;
- a record without `#end` (the run died);
- a record made at another LAUNCHES;
- rows outside the population;
- a re-time row set that differs from what the first pass owes, either way.

It prints:
- the VERDICT per (card, layer), and W/T/L per (card, layer), per pattern and per regime;
- the A/A line, with the standing rate, the single-pass rate and AA_VOID_MAX;
- the N/A, LOSS, INCONCLUSIVE-NOISE, INCONCLUSIVE-HARNESS and NOT-RUN lists;
- the standing WINs, the not-repeated list and the re-time NOT-RUN list;
- every GATE FAIL;
- a DRY RECORD banner on a dry record.

DRY (`--dry`): the same code path with a `DryProbe`. Every reading is a synthetic `DRY_MODELS` value; nothing is run. The quiet
sample reads a quiet box, and the wall is SIMULATED (1 s per sample, 0.06 s per launch), so `--deadline` truncates
deterministically. `dry_guard` replaces the clock call `timed_launch` and wraps `subprocess.run`, so a `taskset` argv or a
`CARD_TIME` env raises `ClockCalled`, a BaseException that time_cells' `except Exception` cannot swallow. Builds, the untimed
answer gates and objdump still run; they are the "builds cells" half of the dry. Every dry ends with `clock calls 0, timed execs
refused 0`.

Code changes besides the new section:
- `prepare_cell` and `pool_proof` gain a `retime` argument.
- `time_cells` gains `retime`, `launch`, `stop`, `prefix` and `salt`, whose defaults are C1-C5's behaviour (R-1 (a), below).
- `read_rows` is factored into `row_of`.
- `c6_decide` returns its per-cell `rows` (additive).
- `arm_pool` (below) is new.
- The docstring is updated (`time`, `c6decide`; "NO command times it" is gone).

## RULE FIDELITY

Clause by clause (c6_rule.md):
- ARMS / CELL: V, H64 and H64.b, each on its OWN pool (POOL_SALT), in LAUNCHES rounds of one launch per arm, `round_arms` order,
  the draw recorded per launch. Done.
- UNIT / FLOOR / SPREAD_MAX: `c6_arm` / `c6_cmp`, unchanged (U5's, reviewed at r79).
- RE-TIME: every reading WIN/LOSS and every A/A non-TIE, all three arms, fresh pool, fresh draws, same unit. The standing rules
  are `_standing`, unchanged.
  - **A FIX, flagged for the code round.** U5's re-time salt alone did NOT guarantee "four new layouts, never the first pass's".
    One salted draw repeats a first-pass (prelude, flags) with probability about 1 in 64 per variant, and `build_cell`'s cache
    name is (text, prelude, flags), so a collision would have re-timed the SAME exe.
  - `arm_pool` redraws the re-time pool (`|redraw<t>`) until no variant repeats any first-pass variant of the same text, under
    any arm's salt. The drill found 1,059 of 18,000 re-time pools needing a redraw.
  - The first pass's pools are byte-for-byte unchanged (R-1 (a)).
- N/A: the reach build's count, untimed, listed with the count and excluded. N/A cells are not timed at all: the rule excludes
  them from every count, so their launches would buy nothing.
- CPU-QUIET CONTROL: rule_710.md's, ported clause by clause (60 s sample, 10 calibration launches, CPU7_MAX with its 20 % cap and
  banner, NIVCSW_MAX scaled by T / T_CAL, the 100 ms observation floor, 2 more re-times, short arm -> NOISE).
  - The calibration exe is "H64 of the first timed cell, variant 0"; 710's was "H64@on of the first cell". This is my reading.
- WINDOW: no cell starts at or after the deadline; NOT-RUN rows are listed; the verdict carries the TRUNCATED prefix through
  `c6_decide`.
  - **READING TO RULE (the code round): a re-time NOT-RUN is not prefixed.** If only a cell's re-time missed the window,
    `c6_decide` (unchanged) does NOT prefix "TRUNCATED: ". The rule's WINDOW says "a cell not started", and that cell did
    start; its RE-TIME clause rules the re-time NOT-RUN case separately (LOSS stands, WIN -> TIE, A/A non-TIE stands).
  - The reader lists those cells and exits 4, and the timer prints `TRUNCATED`.
  - If the code round reads "Any NOT-RUN cell" as covering the re-time too, it is a one-line change in `c6_decide`, plus a drill.
- RECORD: the header as the rule names it; `c6_header_check` refuses another rule sha or a missing header. The decider also
  refuses no `#end`, a LAUNCHES mismatch and an inconsistent re-time set. These are additions, all on the refusing side.
  - `cc.off-os` and `cc.on` hash alike: one gcc. The rule keys the compiler identity, not the level.
- VERDICT / A/A rate / VOID / READABLE: `c6_decide`, unchanged.
- REPORTED: every list the rule names. The A/A single-pass RATE is added beside the count.
- Gates: each arm cell's untimed answer gate runs in the timing pass right before its rounds, as for C1-C5. A gate failure
  makes the arm unreadable and the run red (reader exit 1).

R-1's conditions:
- (a) C1-C5 unchanged:
  - `docs/dev/lanes/bsu6t_evidence/c15_identity.py` loads the base cards.py (09c206cb0) and the lane's as two modules. It
    compares the cell lists at every h*, both launch orders, every pool (400 keys x 4 layers x 13 arms), the default-salt draws,
    and time_cells' OUTPUT FILE byte for byte over STEP1 (with and without approx) and STEP2B at h*=8. `prepare_cell`/`_exec`
    are stubbed (no exe, no clock), and a GateFail, a void and a mid-launch void are planted.
  - Result: 8 checks, 0 differ (`c15_identity.out`).
  - Control: a plant changing the default draw salt gives 3 differ, rc 1 (`c15_identity_plant.out`).
  - `cards.py plan`: 1,741 lines identical base vs lane; the base copy's rule-file path is the one differing line.
- (b) The port's comment cites rule_710.md, and confirm.py by path as provenance. confirm.py is untouched (mtime 2026-11-20
  19:02:56).
- (c) The stubbed-probe drills are in DRILLS.
- (d) The job-level 600 s quiet wait stays in the job script (WINDOW REQUEST).

## DRILLS

All are in `cards.py c6selftest RUNDIR`: 52 rows, 0 failed (`TMPDIR=$PCREC_TMPDIR/scratch/bsu6t/tmp python3
memfn/tests/span_forms/cards.py c6selftest $PCREC_TMPDIR/scratch/bsu6t/rd`, about 20 s). The new rows are below.

Constructed RECORDS: C6/C6c's real population (92 cells, the 8 named N/A cuts), written by the timer's own head and end writers
and `row_line`, and read by `c6_read` alone. Each row reads as c6_rule.md says:

| drill | reads |
|---|---|
| design (V WINs repeated at hit-dense, TIE elsewhere) | NO LOSS x 3; standing WINs = the hit-dense cells (8 / 3 / 3), each "repeated" |
| all-TIE | NO LOSS x 3 |
| high A/A rate (3 standing A/A non-TIE per (card, layer)) | VOID (A/A FAILED: rate 0.094 / 0.250 / 0.250 > 0.050) |
| all-unreadable (every arm short) | VOID (A/A UNREAD) x 3 (first match: VOID before INCONCLUSIVE) |
| all readings unreadable, A/A clean (every V short) | INCONCLUSIVE-NOISE x 3 |
| truncated (60 % NOT-RUN per (card, layer)) | TRUNCATED: INCONCLUSIVE-NOT-RUN x 3, exit 4 |
| reading LOSS repeated / not repeated | LOSS at its (card, layer) / NO LOSS |
| truncated re-time (a LOSS whose re-time did not start) | LOSS (stands), exit 4 |
| one N/A cell per regime per (card, layer) | N/A 9 / 7 / 7 listed, population 27 / 7 / 7, NO LOSS |

Reader refusals, each exit 2: no `#end`, another rule sha, another LAUNCHES, an owed re-time missing, an un-owed re-time present.

CPU-QUIET (R-1 (c); a stub probe with stubbed busy, nivcsw and seconds, no clock):
- thresholds from a quiet sample (the 5 % floor, NIVCSW_MAX 2) and from a 15 % sample (capped at 20 %, flagged);
- a noisy launch is VOID and re-timed once;
- a launch void on every attempt is re-timed exactly 2 more times, then counts as SHORT (None);
- the nivcsw limit scales with launch length (3 switches in 0.5 s valid; in 0.06 s VOID);
- a short arm reads NOISE while its A/A reads on.

DRY guard: `timed_launch`, a taskset exec and a CARD_TIME exec each raise `ClockCalled` (a BaseException), and an untimed exec
runs.

RE-TIME pool: retime 0 equals the base pool. Over 2,000 texts x 3 layers x 3 arms there are 0 first-pass clashes, and 1,059
redraws.

End-to-end DRY runs. The records and logs are in `bsu6t_evidence/` (`dry1*`, `dry_tie*`, `dry_trunc*`). Each is
`--patterns c6_hex32,c6_dig32`: 39 cells, 3 N/A, 12 void by method, 72 timed arm cells. In each, the standalone `c6decide` output
equals the timer's own read-back:

| run | owed | void launches | synthetic launches | clock calls / timed execs refused | reads | rc |
|---|---|---|---|---|---|---|
| `exercise` | 18 | 72 | 697 | 0 / 0 | NO LOSS x 3: hit-dense WINs repeated; the miss-heavy LOSS and random A/A LOSS "not repeated"; near-miss-in NOISE (V void on every attempt); near-miss voids re-timed and valid | 0 |
| `tie` | 0 | 0 | 370 | 0 / 0 | NO LOSS x 3, W/T/L 0/8/0 | 0 |
| `exercise --deadline +75` | (12 owed) | | | | first-pass NOT-RUN rows 63, re-time 36. C6 on: VOID (A/A FAILED 0.250), its LOSSes standing because the re-time did not run; C6c: TRUNCATED: VOID | 4 |

## IN-LANE RUNS

All ran 02:43-02:57 local (outside 18:15-01:00), with TMPDIR=$PCREC_TMPDIR/scratch/bsu6t/tmp. `scripts/boxlock status` was checked
before each run longer than a few seconds: HELD by `queue:752-kit-bsu6-axes` (make test-axes, not a timing job) throughout.
- `make -j16` (the lane build).
- `arm_fixtures --hash` build, one compile (the form hash e62da1e2d786d8c5).
- `cards.py c6selftest`: 27/0 at the base, then 49/0 and finally 52/0.
- Three DRY timer runs (above). The first compiled 72 re-time exes (the disclosed breach); the second and third compiled none.
- Three standalone `c6decide` runs.
- `c15_identity.py` and its plant.
- `cards.py plan` (base and lane).
- `make strict`: rc 0 ("whole tree compiles clean with -Werror -Wshadow").
- `make test-memfn-arch`: rc 0, 32 passed, 0 failed.

The RUNDIR is a copy of lane bsu6's dry RUNDIR (`scratch/bsu6/rd` -> `scratch/bsu6t/rd`; its two erroneous-probe files were
deleted from the copy). The first-pass exes were cache hits (32 of 32 checked): the artifact text is the same, and only `art/`
re-keyed on this tree's binary.

Not run: the full `cards.py selftest` (~90 min; brief) and any timing.

## OWED RUNS

None queued by this lane (brief). For the kit manager, after the code round:
- the full `cards.py selftest` (>= 7200 s bound; the C1-C5 drills ride time_cells, though R-1 (a) shows its output identical);
- a full-population `cards.py time RUNDIR --dry --dry-model tie` as a box-queue job (it builds the 42 x 4 = 168 fresh re-time
  exes, so it is heavy under the sweep cap);
- the timing itself, in main's window (below).

## WINDOW REQUEST

For main's window ask to Frank. One job per box; nothing here is queued.

Job body, dev box (Zen 4; pin CPU 15, SMT sibling 7, read from sysfs; the timer refuses a pin without exactly one sibling):
1. Freeze the tree at the landed commit and build: `make -j16`.
2. Before the quiet wait, build every pool and drive the whole timer once, with no clock:
   `TMPDIR=$PCREC_TMPDIR/scratch/<job>/tmp JOBS=12 python3 -I -B memfn/tests/span_forms/cards.py time RUNDIR --cards C6,C6c --dry --dry-model tie`
   It must end `cards: time: DONE rc=0` and print `clock calls 0`. About 3-4 min, mostly the 168 re-time compiles.
3. The 600 s quiet wait (R-1 (d)): the slot Waiter, as 710's job ran it (`wait_quiet`, `scratch/memfn/fcards/jobs/common.sh` ->
   `waitquiet.py` on `docs/design/memfn/span_cards/slot`).
4. The timing (no compile happens after the quiet wait, since every exe is cached by step 2):
   `CPU=15 nice -n 5 python3 -I -B memfn/tests/span_forms/cards.py time RUNDIR --cards C6,C6c --deadline <min(STOP_AT, start + cap - 600 s) as epoch>`
5. The verdict: the job log's own read-back, or `cards.py c6decide RUNDIR/results_c6_<run>.tsv`.

Job settings:
- `boxqueue: idle-ok`.
- `--ready` refuses 18:15-01:00 and any start where now + est passes STOP_AT.
- The box must be quiet: no other job, no Frank sessions, tmux (the ghostty caveat).

Expect lines:
- `done=1 lines=^cards: time: DONE rc=0$`
- `truncated=0 lines=^cards: time: TRUNCATED$`
- `verdict=3 lines=^C6c? [a-z-]+: (TRUNCATED: )?(NO LOSS|LOSS|VOID|INCONCLUSIVE)`

Estimate on the dev box (ESTIMATED, UNMEASURED):
- First pass: 56 timed cells x 3 arms x 5 = 840 launches, each at least the control's 0.1 s observation floor. About 0.1-0.15
  s a launch plus 4 gate calls per arm cell, so 2-3 min.
- Re-time: the design predicts WINs at about 14 hit-dense cells, about 1 min. The worst case, all 56 owed, is a second 2-3 min.
- Quiet sample 70 s, void relaunches a few %.
- Total: about 5-7 min measuring, plus the 600 s quiet wait, plus 3-4 min for step 2, so about 20-22 min. Ask for a 30 min
  window: cap 3600, est 1300.

ubuntubudu (Zen 1, the second verdict box, via main, D144 add. 4):
- The same body under `gnutimeout`, with `CPU=` set to a core with one sibling. CPU 15 does not exist there (12 threads); read
  thread_siblings_list first.
- Needs clang for C6c `off-clang`.
- Estimate about 2x the dev box's (UNMEASURED): ask for 45 min, cap 3600, est 2400.
- C6's layer is x86-64-v3, which Zen 1 runs (AVX2 as 2x128).

Mac: no C6 cell can run (x86-64-v3). C6c's SIMD-off cells would be directional only, never a verdict; not requested.
