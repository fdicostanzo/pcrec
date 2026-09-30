# tests/clskit/ref/loadgate.py — FROZEN COPY of studies/cls_tree_study/loadgate.py
# at commit 3ee12ed08131e22d45653f1343949550b58576ce, copied 2026-09-29 (lane clss1b). A transitive
# import of tests/clskit/ref's six named modules (imported by
# bench_bytes.py at module load).
#
# WHY A COPY. docs/CLAUDE.md: studies/ is "never built or tested by
# pcrec's make"; tests/clskit/ imports these modules as the reference
# src/gen/clskit.c is cross-checked against (design cls_tree_design.md §6's S1 row), which
# makes them a load-bearing part of `make test` and not merely study
# code any more — so `make test` cannot reach into studies/ live. This
# file is the FROZEN reference tests/clskit/ compares clskit.c against;
# edit it with the same care as a test oracle (crosscheck.py's own
# header says so). To pick up a real change from the study, re-copy from
# studies/cls_tree_study/ by hand (never patch this file to differ from
# its source) and update this header's commit.
"""loadgate.py -- the ONE load-average gate every stopwatch target in this
study uses (bench.py, bench_bytes.py, and the isolated re-run, which is
bench.py invoked directly).

WHY THIS EXISTS (lane clsgate, 2026-09-29, diagnosing the [CLS-TREE] S0
double-REFUSED session, pcrec-bench branch scratch/clstree-s0 0d7392c):
`bench2`/`bench2-bytes` checked load1 ONCE PER SET (bench.py) or ONCE PER N
(bench_bytes.py) and refused instantly on a stale reading, but the gate was
being tripped by the HARNESS'S OWN WORK, not by anything else on the box.
Each set's `gen()` compiles a fresh `.c` (bitmap + 3 kit policies + the
wholeset PageW2/PageW3 arms under --whole) and then runs the resulting
binary once per regime for `rounds` interleaved-arm timing loops -- that is
sustained, single-core, back-to-back CPU work with no idle gaps built in.
A 1-minute load average is an exponential moving average with time
constant ~1 min; ubuntubudu's attempt 2 (README.md in pcrec-bench's
clstree_s0/, pre-wait load1 0.07, NOTHING else running) still crossed 0.52
after ~10 of the 12 k53 sets -- exactly what continuous single-core work
does to load1 with no cooldown, independent of any other process. Compile
times measured here (Mac, gcc-16) run ~0.25s/set and are not the driver;
the five regime *runs* per set (bitmap1/refbs/three kit lams/two wholeset
arms x 11 rounds x 1M probes) are the sustained load.

THE FIX, per Frank's ruling (0.5 threshold UNCHANGED -- calibrated
2026-09-11 for headless ubuntubudu):
  (a) callers build EVERY arm for EVERY unit before any timing starts, so
      the compile-heavy phase never straddles a gate check;
  (b) `wait_for_quiet()` is called immediately before each TIMED unit (one
      regime run, not one whole set) and POLLS rather than refusing on the
      first over-threshold reading -- logging every reading -- up to a
      bounded wait (10 minutes by default). A self-inflicted reading decays
      on its own once the harness stops feeding it work; genuine external
      contention does not, and only THAT case reaches the bound and
      refuses.
  (c) no attempt to fingerprint / exclude the harness's own PID tree from
      the raw load1 reading: the bounded wait-and-poll already absorbs
      self-inflicted spikes (they decay once the harness is idle waiting on
      the next poll), and during an ACTUAL timed run the harness's CPU use
      is not noise to be subtracted -- it's the thing being measured. A
      fingerprinting mechanism would be a second, fragile gate answering a
      question the wait loop already answers cleanly.
"""

import os
import subprocess
import sys
import time


def loadavg():
    # os.getloadavg() first: it is the portable path (Linux AND darwin), so
    # the ubuntubudu run no longer reaches its gate through the sysctl
    # branch's exception handler (r1 panel, lane clsdes88).
    try:
        return os.getloadavg()[0]
    except OSError:
        pass
    out = subprocess.run(["sysctl", "-n", "vm.loadavg"],
                         capture_output=True, text=True).stdout
    try:
        return float(out.strip().strip("{}").split()[0])
    except (IndexError, ValueError):
        try:
            return os.getloadavg()[0]
        except OSError:
            return 99.0


def wait_for_quiet(max_load, bound_s=600.0, poll_s=10.0, tag="",
                   stream=sys.stderr):
    """Block until load1 < max_load, logging every over-threshold reading
    to `stream`. Refuses (sys.exit) ONLY if the box never goes quiet within
    `bound_s` seconds -- a genuinely loaded box still gets an honest
    refusal with its load readings, same as before; a box that is only
    busy with THIS harness's own preceding work gets a short wait instead
    of an aborted multi-hour run. Returns the quiet reading on success.
    """
    t0 = time.time()
    la = loadavg()
    n = 0
    while la >= max_load:
        elapsed = time.time() - t0
        if elapsed >= bound_s:
            sys.exit("%s: REFUSING -- load1 %.2f >= %.2f after waiting "
                     "%.0fs for a quiet box (bound %.0fs, %d readings, "
                     "last reading %.2f; this harness does not caveat a "
                     "noisy measurement)"
                     % (tag or "loadgate", la, max_load, elapsed, bound_s,
                        n, la))
        stream.write("%s: load1 %.2f >= %.2f -- waiting for quiet "
                     "(%.0fs elapsed, bound %.0fs)\n"
                     % (tag or "loadgate", la, max_load, elapsed, bound_s))
        stream.flush()
        time.sleep(poll_s)
        la = loadavg()
        n += 1
    return la
