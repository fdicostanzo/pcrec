# bsu6fix3: the full selftest's one red (r38 J2) on R-47 U6, fixed

Lane bsu6fix3 (opus), worktree `worktrees/bsu6fix3`, branch `lane/bsu6fix3`, cut from `lane/bsu6fix2` 9986aca43. Test-harness
code only:
- nothing changed under `memfn/src/` or `src/`;
- no emitted byte moved; no abi event;
- `c6_rule.md` and `rule_710.md` are unchanged;
- no timing of any kind ran (the J2 drill and the DRY chain stub or synthesize every launch; no clock).

## STATE AT HANDOFF

- **DONE and committed.** In-lane runs are listed in IN-LANE RUNS with their numbers.
- **OWED:** one job, `kit-bsu6fix3-selftest` (the full `cards.py selftest`), see OWED RUNS.
- **Rulings file** `docs/dev/lanes/bsu6fix3_rulings.md`: re-read at every checkpoint and before this report; it is EMPTY,
  so no entry was applied beyond the brief's RULINGS ALREADY MADE.
- `memfn/tests/span_forms/CLAUDE.md`, named in the brief, does not exist; `memfn/tests/CLAUDE.md` covers `span_forms/`.
- **For the reviewer:** time_cells' C1-C5 path is NOT changed. The red was the drill's own stub, stale since bsu6t. The fix
  is in the drill (signature + a stricter "every row ok" clause), and the drill now also runs inside `c6selftest`.

## CAUSE

- **Commit:** bsu6t's 56a625b09 ("WIP C6/C6c timer ..."). It changed `time_cells`' call to
  `prepare_cell(rundir, c, SUBJECT_N, retime)` (a 4th argument, `retime`, C6's fresh re-time pool; C1-C5 pass the default
  0). The J2 drill (selftest, `cards.py` before this lane: inline in `cmd_selftest`) stubs `prepare_cell` with
  `lambda _rd, c, _n: list(c)`, three positional parameters.
- **Why "0 launches":** every cell's `prepare_cell` call raised `TypeError: <lambda>() takes 3 positional arguments but 4 were
  given`. `time_cells` catches any Exception at prepare as a VOID (F7's "a void, re-run once"), so all 40 cells became
  `void` rows, no cell reached the rounds, and the stubbed `_exec` was never called. The drill's other clauses read 40 rows
  (`nrows == len(cl)` held: void rows count as rows), `rr` held vacuously (no rounds), and `same_order` (200 expected vs 0
  calls) failed: hence "every round of 10 holds each arm once: True; the drills' order: False".
  - Evidence `docs/dev/lanes/bsu6fix3_evidence/j2stale.py` (the drill's own stubs on a cards.py copy):
    at 412afe9f5 `launches 200, rows 40, statuses ['ok']`; at 9986aca43 `launches 0, rows 40, statuses ['void']`, first
    note `<lambda>() takes 3 positional arguments but 4 were given`.
- **Expectation vs regression:** the drill's EXPECTATION is right (the rounds and the order are unchanged; see FIX); its
  STUB no longer fits the call. Not a regression in C1-C5's time_cells path:
  - every other change on the C1-C5 path at retime 0 is behaviour-neutral: `build_cell` takes `arm_pool(key, layer, arm, 0)`
    = `pool_variants(key, aligns, pool_salt(arm), pool_shift(arm))`, and `pool_shift` is 0 for every arm not in
    POOL_SALT (only `H64.b`, a C6/C6c arm); `timed_launch` is the old `float(_exec(...).split()[1])`; a GateFail at a
    timed launch stays `void` unless `c6`; the "no valid launch" void cannot fire with `timed_launch` (it never returns None);
    `stop=None`, `prefix=""`, `salt=None` keep the old rows and draws.
  - Direct comparison of the launch plan for the drill's input (C1 hex24 hit-dense + near-miss, 40 arm cells), with
    arity-tolerant stubs and a fixed run id (`bsu6fix3_evidence/j2plan.py`): 412afe9f5 vs 9986aca43 and 412afe9f5 vs this
    tip: `cells 40/40 same; launches 200/200, launch plan (cell, argv incl. the drawn variant, in order) same; output file
    4712/4712 bytes, statuses ['ok']/['ok'], same bytes (sha 94efdfe5fed0216f)`; `j2plan: SAME`.

## FIX

Commit 83db51f47 (`memfn/tests/span_forms/cards.py` only):
- The J2 block moves VERBATIM into `selftest_j2(check)` (called from `cmd_selftest` at the same point, so the full
  selftest's order and row are unchanged), with two changes:
  1. the `prepare_cell` stub takes the real parameters: `lambda _rd, c, _n, _retime=0: list(c)`;
  2. the check also requires EVERY row to read `ok`, and prints the count of rows not ok and the first one's status and
     note. A stub that stops fitting the call now names itself (`40 not ok: void ...takes 3 positional arguments but 4 were
     given`) rather than reading as an order mismatch; and `rr` no longer holds vacuously on zero rounds.
- `cmd_c6selftest` runs `selftest_j2` as a row (`c6selftest: (r38 J2) ...`), right after the CONSTANTS row; see WHY EARLIER
  GATES MISSED IT.
- time_cells itself is untouched by this lane.

## WHY EARLIER GATES MISSED IT

- The J2 drill ran ONLY in the full `cards.py selftest` (~90 min, a queue job). Every gate U6's lanes ran in-lane ran
  something else:
  - **bsu6t's c15 identity** (`bsu6t_evidence/c15_identity.py`, 8/0) compares time_cells' OUTPUT at two cards.py copies
    under ITS OWN stubs, which take `*a` (`def prep(rundir, cell, nn, *a)`). It proves the C1-C5 path unchanged (and it
    is: see CAUSE), but it never runs the selftest's drill or its stub, so the drill's stale arity was invisible to it.
  - **c6selftest** (`inlane.sh selftest`) drills C6's rule, record, DRY chain and plants, never C1-C5's rounds.
  - **mutants / dryfull / g1 / strict / arch** run C6 paths, G1 and the build.
  - bsu6fix and bsu6fix2 queued the full selftest as their OWED run; job 756 is the first full run after 56a625b09.
- The class: a drill monkeypatches a function whose CALL signature the code under test then changes; the code's broad
  `except Exception` (F7's void) converts the stub's TypeError into ordinary void rows, so the drill fails on a downstream
  clause, if at all.
- **The missing control, added:** `c6selftest` (which every lane touching time_cells runs in-lane, in seconds) now runs the
  J2 drill. Shown to fail with 9986aca43's stub and pass at the tip:
  - `bsu6fix3_evidence/j2drill.py CARDS` calls `selftest_j2` directly: tip `ok ... 200 launches over 40 arm cells (40 rows,
    0 not ok) ... True; ... True`, `j2drill: 0 failed`, rc 0;
  - `j2drill.py CARDS --plant-stale-stub` (the tip's drill with 9986aca43's 3-argument stub restored, in memory): `FAIL
    ... 0 launches over 40 arm cells (40 rows, 40 not ok: void selftest_j2.<locals>.<lambda>() takes 3 positional arguments
    but 4 were given) ...`, rc 1;
  - the same plant through `c6selftest` itself: see IN-LANE RUNS (control row).

## IN-LANE RUNS

All on the tip's cards.py (83db51f47; later commits touch only docs/evidence), each compiling step under
`scripts/boxlock run --label bsu6fix3`, TMPDIR `$PCREC_TMPDIR/scratch/bsu6fix3/tmp`, logs in `$PCREC_TMPDIR/scratch/bsu6fix3/`.

| run | file / command | result |
|---|---|---|
| J2 drill, direct | `python3 -I bsu6fix3_evidence/j2drill.py memfn/tests/span_forms/cards.py` (calls `selftest_j2`) | `ok (r38 J2) ... 200 launches over 40 arm cells (40 rows, 0 not ok): every round of 10 holds each arm once: True; the drills' order: True`, `j2drill: 0 failed`, rc 0 (`j2drill.out`) |
| J2 drill, planted stale stub | `j2drill.py ... --plant-stale-stub` | `FAIL ... 0 launches ... (40 rows, 40 not ok: void ... takes 3 positional arguments but 4 were given)`, rc 1 |
| launch plan, 412afe9f5 vs tip | `bsu6fix3_evidence/j2plan.py` | 200/200 launches, plan same, output 4712 bytes same (sha 94efdfe5fed0216f), `j2plan: SAME` (also 412afe9f5 vs 9986aca43: SAME; `j2plan_412_vs_9986.out`) |
| c6selftest | `inlane.sh selftest` (`python3 -I cards.py c6selftest RUNDIR`) | `c6selftest: 95 rows, 0 failed` (94 before + the J2 row), rc 0 |
| CONTROL: c6selftest with 9986aca43's stub | tip's span_forms copy, the stub reverted (`plant_stale/`), same RUNDIR (`control_c6selftest_stale.log`) | `FAIL c6selftest: (r38 J2) ... 0 launches ... 40 not ok: void ... takes 3 positional arguments but 4 were given`; `c6selftest: 95 rows, 1 failed`, rc 1 |
| mutants | `inlane.sh mutants` (`bsu6fix3_evidence/mutb.py`, bsu6fix2's re-aimed, paths only) | `TOTALS: 81 mutants, 79 KILLED, 2 SURVIVED, 0 NOT-APPLIED`; the survivors R13, X6 are bsu6fix2's argued-equivalent pair, unchanged |
| dryfull | `inlane.sh dryfull` (prepare + `time --dry`, synthetic launches) | 92 cells, 84 pools; `DRY: 1573 synthetic launches, clock calls 0, timed execs refused 0`; C6 on / C6c off-clang / off-os NO LOSS; `c6decide rc=0`; `ROUND TRIP: identical (41 lines)` |
| g1 | `inlane.sh g1` (bsu6fix2's case setup copied, wrap.sh re-aimed) | base ok; wrap ok (red by design: deny-fail only); crlf ok |
| make strict | `inlane.sh strict` | rc 0 |
| test-memfn-arch | `inlane.sh arch` | `checks failed: 0`, rc 0 |
| consolidated | `bsu6fix3_evidence/inlane.sh all` | `INLANE ALL DONE rc=0` (`inlane_all.log`) |

Not run in-lane, per the brief: the full 90-minute `cards.py selftest` (OWED).

## OWED RUNS

- `757-kit-bsu6fix3-selftest`: QUEUED (`scripts/boxqueue add`, "queued ... cap 7200, patience none, expect none"; status
  `pending: 757-kit-bsu6fix3-selftest`). Script `docs/dev/lanes/bsu6fix3_evidence/jobs/selftest`, modelled on bsu6fix2's.
  - `--dry-run`: `would run in worktrees/bsu6fix3: TMPDIR=/var/tmp/pcrec-pcrec/scratch/b6f3 python3 -I
    memfn/tests/span_forms/cards.py selftest > /var/tmp/pcrec-pcrec/scratch/bsu6fix3/selftest_full.log`; cap 7200,
    patience none, not-before 2026-11-23T01:00, est 5400, expect none; rc 0.
  - `--ready`: 75 unless 01:00 <= now < 16:30 (a 2 h cap cannot reach 18:15); read 0 at queue time (~12:40).
  - VERDICT: the job's rc (cards.py is exec'd) and the trailer of `/var/tmp/pcrec-pcrec/scratch/bsu6fix3/selftest_full.log`,
    which must read `selftest: 222 checks, 0 failed` (the J2 line: `ok   (r38 J2) time_cells interleaves the arms in rounds
    200 launches over 40 arm cells (40 rows, 0 not ok) ...`). The check count is unchanged: J2 is still one row.
  - The job runs the worktree's cards.py as committed at 83db51f47; nothing after it touches cards.py.
