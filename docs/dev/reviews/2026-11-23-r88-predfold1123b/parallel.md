# PARALLEL findings — r88 predfold1123b

## Findings


### PARALLEL-1 (CONFIRMED, speed/doc) — the "over ten minutes single-process" claim is false at this tree
Measured serially, one run each, 16-core box, load ~2 before: FULL run 5.2 s wall (User 3.98, Sys 1.23, 100% CPU, 81 MB RSS;
output byte-identical to the committed predfold1123b_model.out); LIGHT run (`PREDFOLD1123B_LIGHT=1`) 3.2 s; plant run
(`PREDFOLD1123B_SABOTAGE=all`) 79.7 s, output byte-identical to the committed predfold1123b_sabotage.out. Each single plant 3.2 s
(heavy s19: 5.4 s). Attribution: ~3.2 s = base (load of the older models through predfix86, then the checks; cProfile: ~3.5 of 5.6
profiled s is the ENGINE matcher `m/at/mseq` over the 582 programs run by the checks, SWEEP's 295 lines included); SUCCESSOR = ~2.0 s
for 13 subprocesses (~0.15 s each). Why not ten minutes: the 13 older models each end at an early AssertionError (full.out lines
210-246: all die on the first superseded assertion, e.g. "`rx\.digits := ...`"), so SUCCESSOR runs almost nothing of them; the
"ten minutes" figure matches the `timeout 5400/7200/3600` ceilings in the model (lines 44, 113, 1126), not a measured time. The
phrase is not in the evidence dir's own files; whoever carries it (report/brief) should drop it. Witness: the runs above.
Also note (design, for CHECK): SUCCESSOR's 13 "re-runs" are 13 copies of an immediate load-time assertion, so the check's real
content is the digest of the first FAIL line, not a re-run of each model's checks.

### PARALLEL-2 (CONFIRMED) — independent units and their independence
- Plants (25): each is a fresh `subprocess.run([python,-I,-B,__file__])` with an env COPY carrying one SABOTAGE name; they read the
  tree and `git show` read-only; the model has no file writes, no tempfile, no PCREC_TMPDIR use, no randomness (grep: none), libpcre2
  via ctypes is per-process. Truly independent. Only shared thing: output order (printed in PLANTSB order) and the final count.
- SUCCESSOR's 13 models: independent subprocesses, read-only; results are consumed in MODELSB order into `succB_bad`; same
  independence. Their own children (predfix86 etc. set *_LIGHT) do not recurse.
- SWEEP's 295 lines: NOT cheaply splittable: one process, one engine instance with module globals (the XB[0] switch flips the engine
  between FOLD-on and FOLD-off), and NULLABLE counts programs run by "the checks above (SWEEP's included)" (582), a cross-check
  coupled to everything before it. Do not split it.

### PARALLEL-3 (CONFIRMED, design) — not worth parallelising at today's sizes; what to do instead
Proposal if the owner wants it anyway: a ThreadPool-free `concurrent.futures.ProcessPoolExecutor`-style pool of min(nproc,25) over
the 25 plants only (units = plant names, each the same subprocess.run as today), results stored by index and PRINTED in PLANTSB order
after all finish (or by `ex.map`, which keeps order). Expected: 25 x 3.2 s = 80 s serial -> ceil(25/16)=2 waves x ~3.3 s ~ 7-10 s
on 16 cores (~8-10x), saving ~70 s on a run done once per fold. Control: run both, require `cmp` of the two stdouts BYTE-IDENTICAL
with NO sort (order is fixed by index; today's serial output already is the committed file, and I verified the serial run
reproduces it exactly). SUCCESSOR parallel gain: 2.0 s -> ~0.3 s, not worth any code. Verdict: at 5 s full / 80 s plants the owner's
"review for parallelism" is answered NO: the added pool, ordering control and death handling would cost more reading than 70 s saved;
revisit only if a plant or a model grows past ~minutes (trigger: plant run > 10 min).

### PARALLEL-4 (CONFIRMED by code reading; SUSPECTED for the hang path, not run) — dead or hung worker, serial runner today
- Hang: both runners use `subprocess.run(..., timeout=5400)` (plants, line 113) and `timeout=3600` (SUCCESSOR, line 1126) with
  NO try/except: a hung worker blocks 90 / 60 minutes (1700x / 1100x its 3.2 s / 0.15 s normal time), then `TimeoutExpired`
  propagates as a traceback and the run ends non-zero WITHOUT a verdict line. The exception text carries the command, which is
  identical for all plants (the plant is only in env), so the traceback does NOT name which plant (or in SUCCESSOR, it names the
  model path, so that one is named). Fails, but late and unnamed for plants. Fix: timeout ~60 s per plant (20x margin) and catch
  `TimeoutExpired` -> print "HUNG sN" as NOT CAUGHT.
- Death (os._exit / SIGKILL / OOM) of a plant worker: stdout empty or partial, returncode != 0 (or -9); `ok = bool(fl_) and not tb and
  returncode != 0 and target in last` is then False unless the worker printed its FAIL line AND its last printed line mentions the
  target. Mostly named and counted as NOT CAUGHT (prompt, correct). Narrow hole: target DOC (s21, s22) is the LAST check, so a worker
  killed right after printing `FAIL DOC: ...` and before the verdict line has last line containing "DOC" and returncode -9 -> counted
  CAUGHT with no verdict. Cheap fix: require `last` to match `^predfold1123b_model: \d+ checks, \d+ failed \(.*target.*\)$`.
- SUCCESSOR worker dead/empty: last line "" or a partial line -> `reds["TRACEBACK"]=last`, digest differs from the declared one ->
  `CONTENT CHANGED`, check fails and names the model. Prompt and named. But a model killed AFTER printing the same declared
  FAIL/AssertionError line passes as "superseded" (its death after the declared line is invisible; the returncode is never read).
  Low.
- Proposed pool: same per-unit bounds; a future whose worker dies yields NOT CAUGHT/UNIT DIED naming the plant; `BrokenProcessPool`
  must not be used as the unit of failure (it kills ALL pending futures with no name): so use plain `subprocess.Popen` workers
  (nproc at a time) polled with a per-unit deadline, which preserves per-unit naming. Fail promptly = first dead/hung unit named,
  remaining workers killed by PID (scripts/safekill), run exits non-zero with no verdict line.

## PROBED-AND-HELD
- Full run, LIGHT run, plant run each executed once serially: 18/18, 18/18, 25/25 caught; full and plant outputs byte-identical to the
  committed .out files (diff empty) = determinism of order and content across runs (2 runs each: committed vs mine).
- Independence of 25 plants and 13 models: grep for writes/tmp/random in the model and four older models: none. No order switch exists;
  its absence cannot hide a parallelism defect (units do not interact).
- Smallest witness: 25 plant subprocesses, 13 model subprocesses; 295 SWEEP lines, 582 programs.

CRITIC COMPLETE
