# bsu6par — `cards.py selftest` on the box's cores (lane report)

Owner ruling (Frank, 2026-11-23): "current test isn't using much cpu. if its a test to be run repeatedly or it takes a long
time it should be reviewed for parallelism". Branch `lane/bsu6par`, cut from `lane/bsu6fix3` c8116f8cb (job 757's code).

## STATE AT HANDOFF

STATE: IN PROGRESS (draft; rewritten at handoff).

## SURVEY

### What the selftest spends its time on

`cards.py selftest` is pure CPU in one Python process: no compile, no timed launch, no box lock, no file the night uses.
222 checks (job 757's predecessors: bsu5fix2 and bsu6fix2, 256 lines each). Its cost is the SYNTHETIC NIGHT
(`synth_night`: `synth_rows` plus one to several `analyse` passes), run hundreds of times per check:

| family (units after the split) | per unit | units |
|---|---|---|
| `noise_drill` (300 nights): F2, G2, H1, H2, r38 class noise, r38 controls, void rates, rev 12 layout/regime | 300 nights | ~105 |
| `time_drill` (300 nights): r38 steps and drifts in six launch-order blocks | 300 nights | 36 |
| inline night loops: F2 power 60, G4 200, F3 300, G3 300 x 4, converse 100 x 2, FAST split 100 x 2 | 60-300 nights | 11 |
| `power_rate` / `inter_rate` (300 nights each): r38 power (4), rev 11 K4 (3 x 300), rev 12 B (2), FORMS8-1/-3/-4 (2-3 each), rev 12 power rows (900 nights each) | 300-900 nights | ~20 |
| the H2 gate rows (two drills each) | 600 nights | 2 |
| rev 11 K6 (16 + 16 nights through `rule`/`rerun` on disk) | 32 command nights | 4 (a chain) |
| GAP_K rate (10000 + 4000 synthetic texts, no nights) | | 4 |
| the rule drills (24), the rule's cases (H3 .. H7), rev 12's pool/L6/E/I/K rows, FORMS8-2, J2, J7 | well under 1 s each (measured: the 24 drills 0.09 s with interpreter start; the H3-H7 block 0.7 s; rev 12's cheap block 0.25 s) | 29 |

Job 757's log (serial, one core) reached its 107th line 21 minutes in, in the r38 class noise: about 12 s per 300-night
drill on this box. So the selftest is ~180 drill-equivalents of 300 nights in a row: dominated by the drills, which are
INDEPENDENT of each other (see below), each 5-35 s. No single check dominates; the longest units are the 900-night rev 12
power rows and the 600-night H2 gate rows (UNMEASURED per unit: the owed job writes the per-unit profile).

### Shared state that would race (and why processes, not threads)

- **Rundirs, `bin/`, the exe cache, run ids**: the selftest builds nothing. Its only RUNDIRs are `tempfile`
  directories under the temp root (rev 12's L6 and r44 E, rev 11's K6, the J2 drill), each `mkdtemp`-unique; run ids are
  minted inside them. One printed value is NOT deterministic even serially: the r44 E row's `draws [..] / [..]`, drawn from
  two run ids minted by `os.urandom` (bsu5fix2's and bsu6fix2's serial logs differ there and only there, besides the J2 fix).
- **Env, cwd**: nothing set; FORMS8-2's subprocess (`cards.py plan`, POOL_SIZE=8) gets a copied env. cwd untouched.
- **The box lock**: none taken (the job runner holds it for the whole job).
- **Random draws**: every check seeds its own `random.Random(seed)`; the module `random` state is never drawn from. So a
  check's numbers do not depend on what ran before it.
- **Module globals (the real hazard)**: the controls switch rule flags (`POOL_TERM`, `TWIN_TERM`, `AGREE_GATE`,
  `PAT_TWIN`, `CONFIRM`, `POOL_I`, `READING_B`, `LAYOUT_TEXT_TERM`, `VARIANT_BIMODAL`, `INTERACTION_VOID`,
  `INTER_PE_PER_TEXT`, `PER_HEAD_FLOOR`, `APPROX`) and monkeypatch functions (`check_deny`, `identical_to_I`,
  `time_cells`, `cc_ident`, `prepare_cell`, `_exec`), each restored in `finally`; every `noise_drill` writes `NOISE_LAST`,
  which its caller reads at once. Under THREADS these race (and the GIL would serialize the pure-Python CPU anyway); in a
  FORK pool each worker owns its copy, so a switch in one unit cannot reach another.
- **`lru_cache`s** (`cc_ident`, `chi2_lower`, `f_lower`, `death_depth`, `launch_slots`, `night_blocks`): pure functions of
  constants; their values are read, never mutated.
- **The one value passed between checks**: F2's first drill (`noise_drill()`): its median floor `fmed` sizes G3's splits,
  and H2 re-ran the SAME drill (`noise_drill(seed=1)`) for `NOISE_LAST["fcell"]`. Both now read F2's unit (`needs`).

### Other kit runners that run long or repeatedly (listed, nothing built)

| runner | wall / core use (measured or recorded) | verdict |
|---|---|---|
| `memfn/tests/run_g2.sh --quick` (`make test-memfn-g2`, every `make test`) | 1004 s alone, 29 units summing 1791 s (~1.8 cores average; docs/testing.md, job 205); `win` alone 288 s | already parallel (units concurrent, `--part K/N` shards); its critical path is the `win` unit: split `run_g2_win.sh`'s passes (one per head) into units |
| `run_g2.sh` full (`make test-memfn-g2-full`, opt-in) | 538 s (Mac, stale, 2026-10-05) | same shape as quick; same verdict, lower priority (opt-in) |
| `run_g2_win.sh` (inside g2; alone ~150 s, now 288 s as g2's `win` unit) | one pass per finite grid head, sequential | the best single target: the head passes are independent processes; a pool over heads |
| `cards.py c6selftest` (every lane touching `time_cells`) | seconds given a RUNDIR (bsu6fix3 report) | not worth it |
| the mutant harness `mutb.py` (`docs/dev/lanes/bsu6fix3_evidence`, `bsu6fix2_evidence`) | 81 mutants SEQUENTIAL: 27 min in bsu6fix2 (10:26-10:53), ~5 min in bsu6fix3 (most mutants killed by c6selftest at once) | embarrassingly parallel (each mutant its own copy and rundir `m_ID`; the base chain once, first): one parpool unit per mutant, the base as their `needs` |
| `tests/memfn/g1_span_vector.py manifest` | `--jobs 4` already | fine; default its jobs to nproc |
| `tests/memfn/run_libc_census.sh` (`test-memfn-stamps`) | ~40 s, 8 jobs | fine |
| `memfn/tests/run_g2_any.py`, `run_g2_gate.sh`, `g2_vspan.py` | ~25 s, ~30 s, ~30 s | short: not worth it |

## DESIGN

**One general helper, `memfn/tests/parpool.py`** (0BSD, ~150 lines, its own `selftest`), for any kit runner:

- a runner lists UNITS (`Unit(name, fn, needs=())`); `run(units, jobs)` returns their values in order and writes each
  unit's printed text to stdout IN LIST ORDER;
- `jobs <= 1` is today's serial path: each unit called in order in this process, its output streamed as printed; no fork,
  no capture, no scratch change;
- `jobs > 1`: a `fork` pool of N workers (`multiprocessing.get_context("fork")`; closures are inherited, not pickled).
  Each worker gets ITS OWN scratch: `PCREC_TMPDIR`, `TMPDIR` and `tempfile.tempdir` point at `<root>/w<pid>`, `root` a
  fresh `mkdtemp` under the caller's temp root, removed at the end. A unit's stdout is captured in its worker; the parent
  writes it once every earlier unit's text is written. Units are submitted as soon as their `needs` are done;
- `needs=(i, j)`: the unit is called with units i and j's values (earlier units only; checked) on both paths, so the
  serial and the pooled run compute the same thing;
- a unit that raises stops the run: the text of every unit before it is written, then the failing unit's, then
  `UnitError` with the worker's traceback (the serial path raises the exception itself);
- `jobs_from_args` strips `-j N` / `-jN` / `--jobs N` / `--jobs=N` (default: every CPU in the process's affinity mask);
- `PARPOOL_TIMES=FILE`: one `name, seconds, pid` line per unit (a profile for sizing; never stdout);
- `PARPOOL_PLANT=shared-scratch`: every worker the SAME scratch, the pool's own control.

Limits, named: fork only (Linux; macOS has `fork` but it is not Python's default there); stdout only (a unit's stderr goes
straight to the inherited descriptor: the selftest writes none outside `redirect_stderr`).

**`cards.py selftest` as units** (`selftest_units`, `rev11_units`, `rev12_units`; 218 units in the serial order):
each former check block became a nested `def u(check, ...)` holding its ORIGINAL lines, re-indented (the splice script
asserted the first line of every moved range, so nothing was retyped), loops turned into one unit per iteration (loop
variables bound as defaults). `check` is a per-unit `SelftestRows` that prints the row exactly as before and counts it;
the rule drills `tally` their own rows. The trailer `selftest: N checks, M failed` is summed over the units. No
assertion, threshold, seed or printed text changed. Three structural moves, each output-neutral:

- F2's first drill is the one unit others NEED (G3's `fmed`, H2's `fcell`); H2 used to re-run that identical drill
  (`noise_drill(seed=1)`) for its floor and now reads F2's (one drill less, serially too);
- a few multi-drill checks split into value units feeding a row unit (r38 J2: arm-major and rounds; the r38 power row:
  four `power_rate`s; rev 11 K6: placed, nights, control nights; the FAST split and its control: one unit each);
- rev 11's K6 reads its temp root INSIDE `k6_night` (a worker's own scratch), not once when the units are listed.

CLI: `selftest [-j N] [--rev11] [--rev12] [--list-units] [--units SPEC]` (`--units` takes indices/ranges and pulls in
every unit they need; used for the in-lane subset). `--rev11` / `--rev12` run on the same pool. The docstring's
"bound it at >= 7200 s" now applies to `-j 1`.

## IDENTITY CONTROL

- **The named exception** (the only text that differs between two SERIAL runs of the same code): the r44 E row's
  `draws [..] / [..]` suffix, from two run ids minted by `os.urandom`. bsu5fix2's and bsu6fix2's serial full logs differ in
  exactly that line plus bsu6fix2's J2 FAIL (a code difference); with the suffix masked they differ only in J2 (checked).
  No other printed value is drawn from the clock, the pid, a hash seed or the order of work (job 757's first 63 lines,
  a different process and hash seed, are byte-identical to bsu6fix2's).
- **Owed (the real control)**: job `kit-bsu6par-selftest` runs the full selftest at `nproc` workers on this branch and
  diffs its log against job 757's SERIAL log of the same code (`lane/bsu6fix3` c8116f8cb = this branch's base), the r44 E
  suffix masked in both; red on ANY other difference, on exactly-one-masked-line failing, on a reference without its
  trailer, or on the selftest's own rc != 0.
- **In-lane**: serial vs `-j 4` over a subset that crosses every structural move (drills, the F2 need and two units
  needing it, the r38 J2 value chain, rev 11's K6 chain, FORMS8-2's subprocess, rev 12's temp-dir block, J2, J7),
  byte-compared; the subset's rows also read against job 757's log, present and in order.
- **Planted race**: `parpool.py selftest` runs eight units that write their id to ONE fixed file name in their scratch,
  sleep, and read it back: serial and 4 workers byte-identical with a scratch per worker; with
  `PARPOOL_PLANT=shared-scratch` the output DIFFERS (red as designed). On the cards subset the same plant is expected
  NOT to differ: no selftest unit names a fixed scratch file (every temp dir is `mkdtemp`-unique), which is why the plant
  lives in the pool's own check.

## IN-LANE RUNS

TBD at handoff.

## OWED RUNS

TBD at handoff.
