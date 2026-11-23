# bsu6fix — r80's fixes to R-47 U6 (the C6/C6c timer and reader, the G1 tool)

Lane bsu6fix (opus), worktree `worktrees/bsu6fix`, branch `lane/bsu6fix`, cut from `lane/bsu6t` 715a17a58. Test-harness code
only: nothing changed under `memfn/src/` or `src/`, no emitted byte moved, no abi event. `c6_rule.md` and `rule_710.md` are
unchanged (rule sha 9a2875a6bf089837, 710's 6351bff3901e3955). The review is
`worktrees/memfn/docs/dev/reviews/2026-11-23-r80-memfn-bsu6.md`, and its MANAGER RULING is applied as written. No timing of any
kind was run.

## STATE AT HANDOFF

- The code is DONE and committed: ba5f0deaf (the fixes), c715059b8 (a name clash, tuple-key dicts), a28b2c44d (C6-only exe ids;
  evidence), plus this report's commit.
- The checks are mostly UNRUN. The box lock was held by the kit's 752-kit-bsu6-axes (est 19700 s), with 753 queued after it.
  - R-1 (run beside 752 with `PCREC_BOXLOCK=0`) was refused by the session's permission system. I did not route around it.
  - R-2 (the kit manager) withdrew R-1 and ruled option (c): queue the in-lane checks as ONE job, then the owed selftest, then
    END.
- Three checks DID run in-lane. All are lock-free: no compile, under 10 s each.
  - **A no-compile smoke of `c6selftest`.** This is the whole c6selftest except its compile-backed end-to-end block, which
    starts at `hx = [...]`. It reads `c6selftest: 79 rows, 0 failed`; log in `bsu6fix_evidence/c6selftest_nocompile_smoke.log`.
    The smoke found two bugs, both fixed in c715059b8:
    - a second `reach_refusal` (the existing C1-C5 one) shadowed mine, which is now `c6_reach_refusal`;
    - `dict(**{tuple: ...})` raised TypeError.
  - **bsu6t's C1-C5 identity script**, re-run against base 09c206cb0 and my tip: `c15 identity: 8 checks, 0 differ`
    (`bsu6fix_evidence/c15_identity.out`).
    - Its first run read 3 DIFF: time_cells' output gained the new `exes` column for C1-C5 too.
    - Fixed in a28b2c44d: exe ids are recorded only when `c6=True`, so C1-C5's output files are byte-identical again.
  - **A check that every re-aimed mutant pattern matches its source exactly once**: 80 of 80.
- The rulings file `docs/dev/lanes/bsu6fix_rulings.md`, re-read at the last checkpoint. Its last entry is **R-2 (kit manager):
  "R-1 is WITHDRAWN. The permission system's denial stands; do not route around it. Take option (c)"**, which queues
  `NNN-kit-bsu6fix-inlane` after kit-bsu6-reach, then `NNN-kit-bsu6fix-selftest` after it, names both OWED, runs lanecheck and
  ENDs.
- A fresh agent finishes this lane from the two jobs' verdicts (OWED RUNS says what to read). Any failure is a fix in this tree.
  Every section below marked OWED is filled from those logs.

## FIXES BY ID

All in `memfn/tests/span_forms/cards.py` unless named otherwise.

**FIX-NOW**

- **RULE-1.** `c6_pass(arms)` reads BOTH comparisons as NOISE when any arm of the cell is short or void. Before the fix, a short
  H64.b NOISEd only the A/A, and V vs H64 still read. `c6_cell` (both passes) and `c6_owes` go through `c6_pass`.
  - New VERDICT drills:
    - an H64.b void or short beside a repeated V LOSS reads NO LOSS;
    - 36 TIE + 2 A/A standing + 4 V void reads `VOID (A/A FAILED: rate 0.053 > 0.050)`;
    - a re-time with V void leaves a first-pass A/A non-TIE standing.
- **FIDELITY-2 / CHECKS-3.**
  - Every C6 row carries the `exes` it launched (a 12th column; C6 only, see STATE).
  - The record head carries the proved pools (`pool pat arm layer rt ids`).
  - `c6_read` refuses each of these:
    - an ok row with no exes, or the wrong count of them;
    - an exe outside its recorded pool;
    - a cell whose re-time ran any first-pass exe;
    - a missing pool.
  - `_time` checks at every launch that the exe belongs to the (pat, arm, layer, pass) it is timed for, and raises `WiringFault`
    otherwise (exit 2, no `#end`).
  - The DRY probe keys its model on the exe's PROVED pool, not on the cell's label, so a mis-wired pass reads wrong in the drill.
- **FIDELITY-1 (ruling (c)).** Every pool a cell draws from is LAYOUT-DISJOINT by pool_proof's descriptor.
  - `pool_shift` puts H64.b's first-pass draw two classes from H64's. The draw is r .. r+3 under PHASE_ORDER/ALIGN_VARIANTS, so a
    shift of 2 is the exact complement.
  - Each re-time pool is shifted the same way and then redrawn (`|redraw<t>`, at most REDRAW_MAX = 64 times) until it shares no
    (prelude, flags) with any first-pass pool of the same text, over every arm. Past that bound it is REFUSED (CHECKS-9).
  - `pool_disjoint_refusal` checks the built descriptors pair by pair (`C6_DISJOINT`): H64/H64.b at each pass, and each arm's
    first pass vs its re-time. `prepare` refuses on any overlap.
  - The plant `--plant pool-overlap` gives H64.b H64's classes. It must be refused and print no manifest.
- **FIDELITY-4 / CHECKS-1.** A GateFail inside a C6 timed launch writes a `gatefail` row; before the fix it wrote `void`. The
  reader exits 1 and lists it, on either pass.
  - C1-C5's sibling path is kept unchanged on purpose: their rule reads gatefail rows by its own text.
- **CHECKS-7.** The record drills now carry expected-line regexes and run through `c6decide` itself (stdout captured), not just
  through `c6_read`.
- **CHECKS-5.** `untimed_env()` strips `CARD_TIME`; every untimed exec uses it, and so does the reach run.
  - The DRY guard now checks the EFFECTIVE environment (`os.environ` when `env` is None).
  - `time` pops an inherited `CARD_TIME` and says so.
  - Drill: 4 guard hits including an inherited CARD_TIME.
- **RULE-3.**
  - A timing needs its WINDOW: `--cap` and `--job-start`, with an optional `--stop-at`. The deadline is
    min(stop_at, job_start + cap - 600).
  - `--deadline` is DRY-only.
  - A deadline at or before now is refused.
- **CHECKS-2 / CHECKS-4.**
  - The reach and pool-proof refusals are named predicates (`c6_reach_refusal`, `proofs_refusal`), each with constructed rows.
  - The `reach-dead` plant must be refused at prepare.
- **RULE-2.** The report lists every LOSS or A/A that stands on a single pass (re-time noisy or NOT-RUN) by name, and marks
  `LOSS (standing)` with "(single pass)".
  - EXTRA, beyond the review: on a noisy or NOT-RUN re-time, a first-pass A/A *WIN* now stands too. Before, it fell to TIE.
    `_standing(..., aa=True)` holds any non-TIE A/A; it was found while writing RULE-1's drills. A/A asymmetry is a harness
    finding in either direction, so letting a WIN vanish on a noisy re-time would hide the very fault the A/A exists to catch.
    The rule text says the A/A "stands" on a single pass and does not limit that to LOSS. **The kit manager should confirm this
    reading.**
- **RULE-4 (ruling (a)).** The verdict is prefixed `TRUNCATED: ` whenever any owed run, first pass or re-time, is NOT-RUN.
  - The reader exits 4.
  - The `#end` status is cross-checked against the rows (CHECKS-10): a lying `#end` is refused.
- **FIDELITY-3.** The record header carries `harness` (the sha-256 of cards.py, 16 hex).
  - The reader requires the field to be present and does not refuse on its value. A re-read under a later harness stays
    possible; FIDELITY-7, below, is the plan row for that.
  - The rule block and its sha are untouched.
- **FIDELITY-5 (ruling (b)).** `time RUNDIR --prepare [--cards ..]` does every compile, the reach control and the pool proofs, and
  writes `c6_prepared.json`.
  - Plain `time` loads that manifest (refusing a harness, rule or binary mismatch, or a partial manifest when not DRY), clears
    `COMPILE_OK`, and refuses to compile (`compile_gate`).
  - `--cards`, `--patterns` and `--plant` are refused on plain `time`.
- **CHECKS-6.** The QUIET rows run at the boundaries: (0.5 s, 3) valid; (0.06, 3) VOID; (0.03, 2), (0.06, 2) valid; busy ==
  CPU7_MAX valid. The short-arm row expects (NOISE, AA-NOISE).
- **CHECKS-9.** The redraw is bounded. With REDRAW_MAX = 0 the drill must be refused (exit 2).
- **G1-1, G1-2, G1-6 (with G1-3's count).** In `tests/memfn/g1_span_vector.py`:
  - outcome counts per cell (moved / same / both-fail / default-fail / deny-fail / timeout);
  - `HIDING` (default-fail, deny-fail, timeout) listed in the manifest, with `dry` FAILING on any nonzero hiding count;
  - the outcomes summing to `cells=`;
  - the bench's stripped-LF and CRLF counts;
  - `LAYERS["off"] = ["-fno-memfn-simd"]`;
  - a cross-cell disagreement count on (op, length).

**DOC**

- **G1-4, G1-5.** In the G1 docstring and `docs/design/memfn/block_span.md` §9.4: the length is the read extent, and the witness
  is nonempty-only.
- **G1-7.** In block_span.md:
  - §9.1 gains an AS-BUILT note: abi 110 at U2, 111 at U3, 112 at L3;
  - §9.2 says the command is run by byte-moving units;
  - the §14 U6 row says "NO abi event".

**PLAN**

- **FIDELITY-6 and FIDELITY-7** are appended to `memfn/docs/ideas.md` as dated 2026-11-23 lines, each with its trigger. Neither
  is built.
  - FIDELITY-6's trigger is the next C1-C5 re-run.
  - FIDELITY-7's trigger is the first re-read of a record under a changed control threshold.

## MUTANT GATE

**OWED (job kit-bsu6fix-inlane, stage `mutants`).**

The harness is the checks critic's mut.py, mut2.py and mut3.py, re-aimed: `bsu6fix_evidence/mutb.py`, run copy
`$PCREC_TMPDIR/scratch/bsu6fix/mutants/mutb.py`. The critic's originals and outputs are in `mutants/orig/`.

- **The population is 80 mutants:**
  - the critic's 62, re-stated on the fixed code (same clause; new text where a fix moved it, e.g. O1-O4 over `c6_pass`, the
    D1/D2 effective-env guard, P1-P4 in the bounded redraw);
  - N1-N20, one or more per fix's own control (RULE-1/2/3/4, the A/A-WIN fix, FIDELITY-1/2/3/4/5, CHECKS-5/9/10).
- **How a mutant is judged:**
  - It is KILLED if the full `c6selftest` fails.
  - Otherwise it runs the critic's DRY chain re-aimed: prepare C6 c6_dig32, `time --dry`, then `--deadline +63.5` and `+65`.
    Any exit code or normalized output that differs from the unmutated tip's is KILLED.
  - The BASE must pass c6selftest first; otherwise the harness stops with rc 1.
- **The table** is written to `$PCREC_TMPDIR/scratch/bsu6fix/mutants/table.txt`, one line per mutant, plus
  `TOTALS: N mutants, K KILLED, S SURVIVED, U NOT-APPLIED`.

The critic's SURVIVORS at 715a17a58, which must now be KILLED or argued EQUIVALENT:

E1 E2 E3 O1 R3 R5 R7 R8 R9 R10 R13 R14 T1 T2 T3 T6 T7 V5 V6 X1 X2 X6 X8 X9 X11 X12 X13 X14.

- **Argued EQUIVALENT in advance:**
  - **R13** (`owed = c6_owes(...)` without `c["run"]`): under RULE-1 a cell with a NOT-RUN arm reads that arm as None, so
    `c6_pass` returns (NOISE, NOISE) and `c6_owes` is False. `c["run"]` adds no case.
  - **X6** (`_time`'s "every arm non-notrun" guard before `c6_owes`): equivalent for the same reason. A notrun arm's row has no
    launches, so it reads None, which gives NOISE, which owes nothing.
- **Expected killed, with the drill named:**
  - E1/E2/E3, R9/R10: the c6decide-level record drills (first and re-time gatefail exit 1; truncated re-time exit 4).
  - R3, R5, R7, R8: the refusals unknown, nofirst, rt2of3, stray.
  - X1, X2, X12: the reach-dead and pool-overlap plants, and the predicate rows.
  - X9 and T7: the WiringFault drill, plus the reader's re-time/first exe intersection.
  - X11: the endlies refusal.
  - X13: the gatefail rc row.
  - X14: the moved rule_710 copy.
  - X8 and T1: the deadline drill, which needs every re-time row NOT-RUN.
  - V5/V6: the boundary QUIET rows.
  - T2/T3/T6: the void and notrun drills.
- **Least sure: R14** (the reader's approx skip). No drill record carries an APPROX-regime cell. If R14 survives, the fresh agent
  adds a record drill with an approx cell, or argues it, and re-runs that one id (`mutb.py CARDS R14`).
- **The reader of the log must check:**
  - every id above reads `KILLED(...)`, except R13 and X6, whose equivalence is argued here;
  - every id the critic killed is still KILLED;
  - `NOT-APPLIED` is 0;
  - every N id is KILLED.

## POOL DISJOINTNESS

**OWED (job kit-bsu6fix-inlane, stage `dryfull`, plus the `selftest` stage's POOLS rows).**

- The full `time RUNDIR --prepare --cards C6,C6c` (`rd_full`) writes `c6_prepared.json`, whose `pools` hold, per (pat, arm,
  layer, rt), the exes and their pool_proof layouts.
  - It refuses on any overlap of the `C6_DISJOINT` pairs: H64 vs H64.b at the first pass and at the re-time, and each of V, H64,
    H64.b first pass vs re-time.
  - So `prepare` exiting 0 IS the disjointness proof over the real population. The manifest is the per-arm, per-cell descriptor
    listing the brief asks for.
  - The fresh agent prints it from `rd_full/c6_prepared.json`, one line per (pat, layer, arm, rt) with its 4 layouts, and pastes
    a summary plus a sample here.
- The c6selftest POOLS rows:
  - 2000 texts × 3 layers, with 0 class overlaps and 0 clashes across `C6_DISJOINT`, and redraws > 0 (the redraw path runs);
  - the `same0` row (r41's pools unmoved for V/H64/I/aa/aa.b/h8 at shift 0).
- The constructed refusals:
  - `--plant pool-overlap` (H64.b given H64's classes: refused at 100/100 texts, and the end-to-end prepare exits 2 with no
    manifest);
  - REDRAW_MAX = 0 (the re-time pool cannot be drawn disjoint and is REFUSED, exit 2);
  - the `proofs_refusal` rows on constructed layouts: clean / refused / bad_aa / bad_rt / missing pool. These ran in the smoke:
    79/0.

## DRY AND DRILLS

**Partly run (the smoke); the rest is OWED.**

- **c6selftest.**
  - The smoke covers everything except the compile-backed block: 79 rows, 0 failed. That includes the VERDICT drills, RULE-1's
    constructed cases, the record and c6decide drills, the refusals, QUIET, guard, POOLS and predicates.
  - The full c6selftest (with the end-to-end block) is stage `selftest`; it must print `c6selftest: N rows, 0 failed` with
    exit 0.
  - Its end-to-end block holds:
    - prepare;
    - a DRY with CARD_TIME preset: `clock calls 0, timed execs refused 0`, the record round-tripping through c6decide;
    - the deadline TRUNCATED drill (`C6 on: TRUNCATED: `, exit 4);
    - the gatefail model (exit 1);
    - the WiringFault plant;
    - the moved rule_710 copy;
    - the window refusals (no manifest; `--cap` without `--job-start`; a non-DRY `--deadline`);
    - the harness-mismatch manifest;
    - the compile gate.
- **The full DRY over C6,C6c (stage `dryfull`):**
  - `time rd_full --prepare --cards C6,C6c`, then `CARD_TIME=1 time rd_full --dry`;
  - the job log must show `clock calls 0, timed execs refused 0`, `cards: time: DONE rc=0`, `c6decide rc=0` and
    `ROUND TRIP: identical`.
  - The round trip is the time command's own read-back compared byte for byte with a separate `c6decide` of the same record.
- **RULE-1's constructed cases** are the three VERDICT drills named under FIXES. They passed in the smoke.

## IN-LANE RUNS

Every run used `TMPDIR=$PCREC_TMPDIR/scratch/bsu6fix/tmp`. None compiled, none took the lock, none was a timing.

| run | result |
|---|---|
| `make -j16` in the worktree (before the summary) | rc 0 |
| no-compile smoke of c6selftest, two rounds (the first found the two bugs above) | 79 rows, 0 failed |
| `bsu6t_evidence/c15_identity.py` base 09c206cb0 vs tip | 8 checks, 0 differ (after a28b2c44d) |
| mutant pattern self-check | 80 of 80 match exactly once |
| both job scripts `--dry-run` / `--ready` | dry rc 0; ready rc 75 (waiting on kit-bsu6-reach; waiting on kit-bsu6fix-inlane) |

- NOT run in-lane: the full c6selftest, the mutant gate, prepare/DRY, g1 dry, make strict and make test-memfn-arch. All of them
  are OWED in kit-bsu6fix-inlane.
- The one attempted bypass (`PCREC_BOXLOCK=0` under R-1) was DENIED by the permission system and NOT run. R-2 withdrew R-1.
- A stale `boxlock run` waiter of mine (pid 1311344) was safekilled by PID before that attempt.

## OWED RUNS

Both jobs are queued. Each declares `not-before 2026-11-23T01:00`, and its `--ready` returns 75 unless 01:00 <= now < 18:00.

1. **754-kit-bsu6fix-inlane** (key kit-bsu6fix-inlane), ready `after kit-bsu6-reach`.
   - Settings: cap 18000, est 7200, `expect stages=6 lines=^== STAGE `.
   - It is one job by R-2's ruling, which is why the cap is over an hour.
   - Body: `$PCREC_TMPDIR/scratch/bsu6fix/inlane.sh all` (copy in `bsu6fix_evidence/inlane.sh`; job script in
     `bsu6fix_evidence/jobs/inlane`).
   - job.log ends with `INLANE ALL DONE rc=N`. Each stage prints `== STAGE <name>: INLANE <name> DONE rc=N` and its verdict
     lines, and keeps its own log at `scratch/bsu6fix/inlane_<stage>.log`.
   - What the reader must check, per stage:
     - **selftest**: `c6selftest: N rows, 0 failed` and rc 0.
     - **mutants**: `mutants/table.txt`, per MUTANT GATE above. The stage's rc 0 only means the harness ran; survivors are read
       from the table.
     - **dryfull**: prepare rc 0, `clock calls 0, timed execs refused 0`, `DONE rc=0`, `c6decide rc=0`,
       `ROUND TRIP: identical`.
     - **g1**: three cases.
       - `base` (clean bench): `g1 dry base rc=0`.
       - `wrap` (`g1/wrap.sh` makes the deny-side compile of `[0-9a-f]{17}` exit 3, the critic's G1-1 repro):
         `g1 dry wrap rc=1`, with the deny-fail count 1 named. This one is RED BY DESIGN.
       - `crlf` (the critic's bench with the CRLF file): its manifest meta line shows `crlf=1` and the stripped-LF count.
       - The `g1` stage rc is the manifest steps' rc, not the dry verdicts.
     - **strict**: rc 0.
     - **arch** (`make test-memfn-arch`): rc 0.
2. **755-kit-bsu6fix-selftest** (key kit-bsu6fix-selftest), ready `after kit-bsu6fix-inlane`.
   - Settings: cap 7200, est 5400, `expect none` (exec'd).
   - Body: the full `cards.py selftest` (no args), modelled on 750-kit-u5tip-test. Log
     `$PCREC_TMPDIR/scratch/bsu6fix/selftest_full.log`.
   - The reader checks: rc 0 and the log's trailer with 0 failed. The C1-C5 drills ride time_cells, whose output c15 shows
     byte-identical.

## WINDOW REQUEST

For main's window ask to Frank. One job per box; nothing here is queued. The only change from bsu6t's request is the
prepare / time split (ruling (b)) and the window flags (RULE-3).

**Dev box** (Zen 4; pin CPU 15, SMT sibling 7, read from sysfs):

1. Freeze the tree at the landed commit and build: `make -j16`.
2. PREPARE, before the quiet wait. This is every compile, the reach control, and the pool proofs with the disjointness check:
   `TMPDIR=$PCREC_TMPDIR/scratch/<job>/tmp JOBS=12 python3 -I -B memfn/tests/span_forms/cards.py time RUNDIR --prepare --cards C6,C6c`
   - It must exit 0; any refusal is exit 2 and the job stops.
   - Then a no-clock rehearsal on the same manifest: `... time RUNDIR --dry --dry-model tie`. It must print `clock calls 0` and
     `DONE rc=0`.
   - About 3-5 min (UNMEASURED): the first-pass and re-time pools' compiles, cached afterwards.
3. The 600 s quiet wait: the slot Waiter, as 710's job ran it.
4. TIME. It compiles nothing, because `time` refuses to:
   `CPU=15 nice -n 5 python3 -I -B memfn/tests/span_forms/cards.py time RUNDIR --cap CAP --job-start JOB_START_EPOCH [--stop-at STOP_EPOCH]`
   - The deadline is min(stop_at, job_start + cap - 600).
   - A cell or re-time not started reads NOT-RUN, and the verdict is prefixed `TRUNCATED: ` (exit 4).
5. The verdict: the job log's read-back, or `cards.py c6decide RUNDIR/results_c6_<run>.tsv`.

Job settings:
- stages `prepare` (light), `quiet` (idle-ok), `time` (idle-ok);
- `--ready` refuses 18:15-01:00 and any start where now + est passes STOP_AT;
- the box must be quiet (no other job, no Frank sessions, tmux).

Expect lines:
- `done=1 lines=^cards: time: DONE rc=0$`
- `truncated=0 lines=^cards: time: TRUNCATED$`
- `verdict=3 lines=^C6c? [a-z-]+: (TRUNCATED: )?(NO LOSS|LOSS|VOID|INCONCLUSIVE)`

Estimates (ESTIMATED, UNMEASURED):
- **Dev box:** prepare 3-5 min; quiet wait 600 s; time 5-7 min (first pass about 840 launches, re-time about 14 cells to
  worst-case 56). Ask for 30 min: cap 3600, est 1400.
- **ubuntubudu** (Zen 1, via main, D144 add. 4): the same stages under `gnutimeout`, with `CPU=` set to a core with exactly one
  sibling. CPU 15 does not exist there; read thread_siblings_list first. It needs clang for C6c `off-clang`. Estimate about 2x:
  cap 3600, est 2600.
- **Mac:** no C6 cell (x86-64-v3); not requested.
