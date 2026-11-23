# CRITIC PARALLELISM: memfn-bsu6par (r86)

## Findings

PARALLEL-1..8 below (1 hang on dead worker, 2 FIFO tail, 3 multi-drill units, 4 --units closure, 5 subset label, 6 default -j, 7 stderr order, 8 single control); updates and the generalization follow.

## PROBED-AND-HELD

See the final PROBED-AND-HELD list at the end of this file (selftest, -j1/2/4 identity, needs chain, parsing, scratch).


## PARALLEL-1 (design, SUSPECTED) a dead worker hangs the run forever
parpool.py `run` (the wait loop, ~l.158-176): `multiprocessing.Pool` replaces a worker that dies (OOM kill, os._exit,
SIGKILL, segfault in a C call) but the task it held is LOST: its AsyncResult never becomes ready. The parent then
loops on `pending[nxt].wait(0.05)` for ever (the "no unit runnable" UnitError only fires when `pending` is empty).
Confirm: a unit `lambda: os._exit(3)` in `run([...], 2)` should never return. Owner-visible: a 4g watchdog -m kill of
one worker (tree RSS is summed, so it kills the whole tree: fine) differs from a kernel OOM-kill of one worker (hang,
no output, no diagnostic). Fix: `concurrent.futures.ProcessPoolExecutor` (BrokenProcessPool) or poll
`pool._pool` pids / use per-unit Process objects. Effort S. Blast: only -j N>1 runs.

## PARALLEL-2 (design, CONFIRMED by reading) dispatch is FIFO by index, not heaviest-first; no weights anywhere
`submit_ready` applies every ready unit with apply_async in LIST order; the workers drain that queue in that order.
Consequence for the SPEED-UP (structure only, no clocks): the units are ~1 "drill" (300 synthetic nights) each, but
the units with 2-3 drills sit LATE in the list: rev12 power tau x3 (n5 + n10 + multi = 3 drills each, cards.py
~4626-4648), rev12 R2 B control (2 noise_drill), H2 gate void rate x2 (2 drills each, ~5309), rev12 GAP_K (two
gapk_rate with texts=4000 per tau). List scheduling in index order bounds the makespan by total/N + max unit, so
a 3-drill unit that starts last adds ~3 drills to a ~13-drill-per-worker plan (N=16, ~215 drill-equivalents): about
-20 % of the ideal speed-up. `-j N` is therefore NOT heaviest-first; the sibling mechanism g2_parts.py assign
(memfn/tests/g2_units.tsv: weighted greedy, heaviest first) solved exactly this. Fix S: carry an optional `weight`
on Unit (or order submission by a declared weight, writing stays in list order), or split the multi-drill units
(PARALLEL-3). Expected effect: tail shrinks from <=3 drills to <=1.

## PARALLEL-3 (speed, CONFIRMED by reading; weight SUSPECTED) units that bundle several drills
By their bodies: "rev12 power tau 0/0.01/0.02" (cards.py ~4626) run power_rate(5 %), power_rate(10 %) and a multi-winner
300-night loop in ONE unit (3 drills, three independent seeds 3400+k/3410+k/3420+k): split into three units each and
print/check in a small collector unit with `needs` (the POWER_RECORD pin check needs all three: the `needs` form
exists already). "H2 gate void rate normal / t(5)" (2 drills each: AGREE_GATE off then on, ~5309) and "rev12 R2 B
control" (2 drills, ~4477) split the same way. "rev11 K6 nights" and "K6 control nights" are 16 sequential k6_night
(each up to 6 file-backed rule/rerun passes) and are independent per seed: splitting per seed (16 units each) is cheap
but only worth it if PARPOOL_TIMES shows them above 1 drill (SUSPECTED: ~0.3-0.6 drill by structure, so low
priority). The F2-normal -> (G3 x8, H2 x10) `needs` chain is NOT a ceiling: F2 normal is index ~7, starts at t0 and
its 18 dependents are submitted when it ends, behind the already-queued units but the queue is ~200 deep, so they
run in the middle; critical path F2 + one dependent = 2 drills, far under total/N (~13). Same for K6: placed (0.1 drill)
-> nights|control -> check, a 3-step chain of <1 drill each, but it is submitted last-ish (index ~190), so it is a
TAIL item, not a ceiling (PARALLEL-2 order fixes it). The ordered-output rule only delays WRITING, never compute
(parent harvests every finished unit and submits dependents at once): no critical-path cost from "parent holding
output"; its cost is memory (all text buffered) = trivial here.
Structural ceiling: no single unit exceeds ~3 drills of ~215, so the bound is ~min(N, 215/3.. ) i.e. N=16 is reachable
to within the tail of PARALLEL-2; N>~60 would stop helping (not a real limit on 16 cores). Dispatch itself is dynamic
(Pool's shared task queue, chunk of 1), default -j = len(sched_getaffinity) (all 16 CPUs).

## PARALLEL-4 (design, SUSPECTED, latent) `--units SPEC` closure is one level deep
cmd_selftest: `for i in sorted(want, reverse=True): want.update(units[i].needs)` iterates a SNAPSHOT, so a unit added
because something needs it is not itself expanded. Today every `needs` is depth 1 (K6 check lists ip, ir, ic
explicitly; power row lists all ipw), so it holds; the first chain A needs B needs C gives `renum[j]` KeyError for
`--units A`. Confirm by a 3-unit chain through cmd_selftest's code (no such chain exists to run today). Fix: loop to a
fixed point (or iterate from high to low index adding needs as you go, which works because needs are earlier). Effort XS.

## PARALLEL-5 (answer/doc, CONFIRMED by reading) a subset run prints the full run's verdict line
`--units SPEC` (and --rev11/--rev12) end with `selftest: N checks, 0 failed` / `selftest --rev11: ...`; a SPEC subset
prints the plain full-run label `selftest:` (what = "selftest"), so a green 4-unit run is textually a green selftest
(K35: a population nobody counts). Fix XS: `what += " --units SPEC (K of 218 units)"`.

## PARALLEL-6 (design, CONFIRMED by reading) default -j = every CPU, silently, on a shared box
`default_jobs()` = all 16 affinity CPUs; the kit/box rules (box shared with Frank; bench/timing windows; `scripts/
watchdog -m`) mean a bare `cards.py selftest` now takes the whole box and N x ~memory. Probably what the owner wants for a
queued job, but a human `python3 cards.py selftest` mid-day is a 16-way load with no nice and no message. Suggest:
print the chosen -j on stderr's first line, document in CLAUDE.md that timing windows must pass -j or run under nice,
and consider min(nproc, 8) as default until the box's pressure rules say otherwise. Effort XS.

## PARALLEL-7 (answer, SUSPECTED) stderr is not ordered/captured; the "byte-identical" claim is stdout-only
parpool docstring admits it. Units that write stderr (cmd_rule's refusal text, cards.py ~2616, reached by the K6 units
through `redirect_stdout` only) emit it live in worker order; `2>&1` output of -j N differs in placement from -j 1.
Confirm: K6 units at -j1 vs -j2 with `2>&1`, if the rule writes stderr there (not run: heavy). Fix S: capture
sys.stderr per unit and write it after the unit's stdout (parent), or state "stdout only" in the CLAUDE.md line.

## PARALLEL-8 (design, CONFIRMED by reading) only ONE control exists, and it plants scratch sharing only
The pool's byte-identity promise needs units independent in (a) scratch (controlled: PARPOOL_PLANT=shared-scratch) and
(b) interpreter state: a Pool worker runs many units in ONE process, so module globals a unit leaves behind
(NOISE_LAST, APPROX, _flags, PLANT, COMPILE_OK, REDRAW_MAX, monkeypatched prepare_cell/_exec/time_cells) reach whatever
unit that worker runs next, and WHICH unit follows which differs per run (-j 1: list order; -j N: by timing). No
control for (b): e.g. `PARPOOL_PLANT=reverse` (run the serial path in reverse order, output compared in list order)
or maxtasksperchild=1 as a cheap belt-and-braces would make "units are independent" a measured fact instead of the
docstring's `provided`. Today (b) rests on each unit restoring its globals in try/finally (spot-checked: the _flags /
globals()[...] sites at 5181-5455 all restore in finally). Effort S for the reversed-order control.

## UPDATES from the locked runs (the list is now known: `selftest --list-units` = 218 units)
- PARALLEL-1 now CONFIRMED: probe_hang.py (scratch dir) `run([a, die(os._exit(3)), c], 2)`: printed `a`, then the
  watchdog 180 s wall kill (rc=124); nothing else, no diagnostic. Also left `<PCREC_TMPDIR>/parpool.XXXX/w<pid>` behind
  (the finally never ran on the watchdog kill): parpool.* roots leak on SIGKILL (S: sweep stale parpool.* at start).
- PARALLEL-7 now CONFIRMED: two units each writing stdout then stderr ("slow" sleeps first): -j1 stderr `err1 err2`,
  -j2 stderr `err2 err1`; stdout identical `out1 out2`. A `2>&1` run is not byte-identical across -j.
- PARALLEL-2/3 positions (from the list): drills 0-23, F2 normal 24 (its 18 dependents are submitted when it
  finishes), H2 gate void rate 72-73, H3.. 74, K6 placed/nights/control/check = 176-179 (chain of three steps, each
  <~1 drill by structure), rev12 R2 B control 192, GAP_K 208-211, rev12 power tau 212-214 (3 drills each, the heaviest
  units by body) then only 215-217 (J2 time_cells rounds, J7). So the three heaviest units are the LAST three real
  units dispatched: the tail is ~3 drills after everything else ends (about 3 of ~13-14 ideal per-worker drills at
  N=16, i.e. up to ~20 % of the possible speed-up). Fix: split them (PARALLEL-3) or submit heaviest-first (PARALLEL-2).

## Generalization / siblings (no runs)
Sibling runners under memfn/tests/ with their own hand-rolled pools: run_g2_simd.py, run_g2_mfind.py, run_g2_any.py,
g2_vspan.py (compile+run legs; would not fit parpool's captured-stdout model unchanged). The run_g2*.sh gates are split
the OTHER way: g2_parts.py assign + g2_units.tsv (`--part K/N`, weighted greedy heaviest-first). Two mechanisms now
split work in the kit: parpool (in-process units, FIFO) and g2_parts (shell units, weighted). parpool fits any
pure-Python runner with a long serial body (other cards.py drill sweeps).
General form + unlocks: one `Unit(name, fn, needs, weight)` where a measured weight (with a source column as in
g2_units.tsv) drives submission order here and `--part K/N` dealing there; the same table then lets a CI split (4-core
runner) deal parpool units across jobs, and PARPOOL_TIMES feeds a `reweight`. Trigger: the second runner adopting
parpool, or the first measured FIFO tail.

## PROBED-AND-HELD
- parpool.py selftest: ran once, 4 rows ok, 0 failed; the control reads red as designed (6 of 8 race lines changed
  under shared scratch).
- cards.py selftest --units 0-5,217 at -j1/-j2/-j4: stdout byte-identical (3 runs, 7 checks, stderr empty); scratch removed.
- --units 162 (needs 160,161, renumbering) at -j1 vs -j2: byte-identical, 2 checks.
- -j parsing, per-worker scratch (w<pid>, env + tempfile.tempdir), kit units' temp via PCREC_TMPDIR (cards.py 4733, 4932,
  5031), failure path (earlier units written, failing text, UnitError, terminate): read + selftest rows ok.
- No unseeded random in the selftest paths (only os.urandom run ids).
Units run: 0-5, 217 (j1/j2/j4), 162 (j1/j2), list-units; parpool probes die/stderr/chain.
CRITIC COMPLETE
