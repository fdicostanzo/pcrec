# CRITIC IDENTITY: memfn-bsu6par (r86)

## Findings

### IDENTITY-1 -- SUSPECTED; severity maintenance (robustness, -j only); effort small; blast radius: a `-j N` selftest whose worker dies
memfn/tests/parpool.py:150-178 (`run`'s wait loop). A worker that DIES mid-unit (OOM kill, a segfault in a C extension,
`os._exit` anywhere under a unit, a stray signal) is silently replaced by `multiprocessing.Pool`, but the AsyncResult of
the unit it was running never becomes ready: `pending[nxt].wait(0.05)` then loops forever. BASE's serial run (and `-j 1`)
dies loudly at that point. Under -j N the run HANGS until the job's watchdog fires, and the log shows the earlier units'
rows and nothing naming the dead unit. Not seen in normal runs (no unit calls os._exit; the units are pure Python).
Confirm: a constructed unit list with `Unit("die", lambda: os._exit(9))` run at jobs 2 hangs (run under a 30 s watchdog).
Fix shape: `concurrent.futures.ProcessPoolExecutor` (raises BrokenProcessPool) with the fork context, or a per-unit
deadline / worker-pid liveness check in the wait loop that raises UnitError naming the unit.

### IDENTITY-2 -- CONFIRMED by reading; severity design/doc; effort trivial; blast radius: every queued `cards.py selftest` without `-j`
memfn/tests/span_forms/cards.py `cmd_selftest` (`pp.jobs_from_args(args)`, no default) and parpool.py `default_jobs`.
The promise reads "`-j 1` is today's serial path", but the DEFAULT is no longer the serial path: with no `-j` the
selftest now forks one worker per CPU this process may use (16 on the dev box). Output is identical (part (b) below),
so this is not an answer risk; it is a footprint change for any existing caller (a job, a script, a lane brief) that
ran `cards.py selftest` expecting one core, e.g. beside a timing window or another heavy suite. Either say so in the
docstring/usage line and NOTES.md ("default: every CPU"), or make the default 1 and have the box job pass `-j N`.
(Not checked: which callers invoke `cards.py selftest`; the box-queue files are denylisted for this lens.)
IDENTITY-2 AMENDED (same session, on re-reading the usage text): cards.py's usage line DOES say "-j N workers, default
every CPU, -j 1 the serial path". The doc half of IDENTITY-2 is withdrawn; what remains is a nit for the manager: the
default changed from one core to every CPU for existing callers of `cards.py selftest` (a box-footprint change, not an
answer change). Severity nit/design.

IDENTITY-1 UPGRADED to CONFIRMED (repro): $D/die.py builds [Unit a: print("before"), Unit die: os._exit(9), Unit c:
print("after")] and calls parpool.run(units, 2). Command: `scripts/boxlock run --label crit-bsu6par --no-wait --
scripts/watchdog -s 30 -m 1g -S crit-bsu6par -- env PCREC_TMPDIR=$D TMPDIR=$D python3 -I $D/die.py
<tree>/memfn/tests/parpool.py`. Observed: "before", then nothing until "watchdog: wall timeout after 30s", rc 124.
Expected: UnitError naming unit 1 (die) and a non-zero exit, as with a unit that raises. Side effect: the pool's scratch
root (`$D/parpool.rfm7wqnt`) is left behind, because the watchdog's kill skips run()'s `finally: rmtree`. Today's units
do not die this way, so this is robustness only (a hang in place of a loud failure, under -j N only).

## PROBED-AND-HELD (identity lens)

(a) Faithfulness, BASE c8116f8cb vs SUBJECT 2061e7e98, by text:
- Whitespace-normalized unified diff of BASE selftest_rev12..cmd_selftest (lines 4428-5420) against SUBJECT
  rev12_units..selftest_units (4431-5596): every removed line is structural (def/cmd_selftest/check plumbing) or
  reappears unchanged inside a unit. Held.
- Every `check(` call site's name string, extracted in order from both regions: 66 = 66, IDENTICAL SEQUENCE (diff empty).
  `print("REC` RECORD rows: 9 = 9 (printed, not counted, in both). DRILLS rows: same print, counted via `tally`
  (BASE: nchk = len(DRILLS) + bad +=). Held.
- Seeds: every random.Random(...)/seed= literal unchanged (in the normalized diff no seed line is removed or added).
- Moved computations, each checked for print order and state: K4 control's `pma` drill (now after the power row, its own
  unit; prints unchanged order); G3 FAST split's check now printed before the flag-off control drill (same row order);
  r38 J1/J2/R2 controls split into units, each re-setting PAT_TWIN/CONFIRM off, printing J1, J2 x2, R2 in BASE's order;
  power line pw0/pw1 recomputed in units p0h, p1h, p0r, p1r -> same dict orders (hit-dense, random). Held.
- H2's floor: BASE re-ran `noise_drill(seed=1)`; SUBJECT reads F2's `noise_drill()`: defaults are trials=NOISE_TRIALS,
  sigma 0.01, noise normal, seed 1, i.e. the identical call; both run with every flag at its default True and APPROX
  restored, and noise_drill's only state is its own Random(seed) + pure lru caches: same fcell. Held.
- K6's `troot` moved from selftest_rev11's top into k6_night (now the worker's scratch under -j); no row prints it. Held.
- Summary line and exit: "%s: %d checks, %d failed" with what = selftest / selftest --rev11 / selftest --rev12, exit 1 iff
  any check false: same as BASE in all three forms; --rev12 alone and --rev11 [--rev12] dispatch identical to BASE.
  Only difference: BASE's --rev12-alone `check` printed with flush=True (no text change).
- --list-units: 218 units, needs only on 24 (F2) for G3/H2 (37 units), 160/161 -> 162, 164-167 -> 168, 176 -> 177/178,
  176/177/178 -> 179: each consumer's needed value is exactly the one its body reads.

(b) Cross-unit state:
- Statically: every globals() switch in the units (POOL_TERM, TWIN_TERM, AGREE_GATE, PAT_TWIN, CONFIRM, POOL_I, APPROX,
  READING_B, LAYOUT_TEXT_TERM, VARIANT_BIMODAL, INTERACTION_VOID, INTER_PE_PER_TEXT, PER_HEAD_FLOOR, check_deny,
  identical_to_I, time_cells, cc_ident, prepare_cell, _exec) is restored in a finally (hard-coded True restores match the
  module defaults, lines 2942-2979). NOISE_LAST is read only after the same unit's own noise_drill. lru caches
  (cc_ident, chi2_lower, f_lower, death_depth, launch_slots, night_blocks) are pure of flags. No module-level `random.*`
  calls, no chdir, no sys.path edits in the units; per-night layout stores are fresh dicts. PLANT/COMPILE_OK/REDRAW_MAX
  are touched only by `time`/c6selftest, not by any selftest unit.
- Dynamically (snap.py: each unit run in-process, all module globals + environ/cwd/sys.path/sys.modules snapshotted
  before/after): units 0-23, 74, 174, 175, 176, 205, 215, 216, 217 (32 units): globals changed "none" for 31; unit 74
  adds lazily imported modules only. All their checks ok (47/47 + K6 placed's value).
- `cards.py selftest --units 0-23,74,174,175,205,215,216,217` at -j 1, -j 2, -j 4: 54 lines each, "53 checks, 0
  failed", rc 0, empty stderr; the ONLY differing line is unit 215's (r44 E) "draws [..] / [..]", the urandom run-id
  suffix the promise names (it varies between two -j 1 runs as well, BASE too). No parpool.* root left after the clean runs.
- Units' stdout capture: no unit writes to sys.__stdout__ or fd 1 directly (FORMS8-2's and cc_ident's subprocesses use
  capture_output); time_cells under J2 is fully stubbed (no CPU-quiet probe), so -j load cannot void its rows.

Runs (all box-locked, watchdogged): --list-units; snap.py over 32 units; --units at -j 1/2/4; die.py (parpool) = 6 runs.
Not run: the noise-drill units (each ~300 synthetic nights, too long for 180 s) and K6 nights; covered by text only.

CRITIC COMPLETE
