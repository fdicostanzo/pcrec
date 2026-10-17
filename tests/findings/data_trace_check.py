#!/usr/bin/env python3
"""tests/findings/data_trace_check.py -- `emit_sweep.py --data`'s `data_trace`
drops ONLY `KSRCTRACE\\t` lines from stderr ([WINDOW-E1], e1val).

    data_trace_check.py EMIT_SWEEP_PY

The mover test of the --data census compares the CLEAN stderr of the two
sides (`a[3] != z[3]`), so the drop is a blind spot: whatever it swallows can
never be a mover. Five assertions, over hand-written stderr blobs:

  1. two sides differing ONLY in a KSRCTRACE line compare equal (not a mover);
  2. two sides differing in a plain diagnostic line compare unequal;
  3. the same for near-misses a widened drop would swallow: a line starting
     `KSRCTRACE` with no tab, and `KSTRACEX\\t` (neither the record nor the
     attempt record the function consumes);
  4. a KSTRACE record still never reaches the clean text.
Prints PASS:/FAIL: lines; exit 1 on a FAIL.
"""
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("emit_sweep", sys.argv[1])
es = importlib.util.module_from_spec(spec)
spec.loader.exec_module(es)

fails = 0


def check(name, cond):
    global fails
    print(("PASS: " if cond else "FAIL: ") + name)
    fails += 0 if cond else 1


def clean(*lines):
    return es.data_trace(b"\n".join(lines) + b"\n")[0]


KS = b"KSRCTRACE\tobject\tT\tbyte-rate\tPRESENT"
check("data_trace: a differing KSRCTRACE line is not a mover",
      clean(b"w: x", KS + b"\tAAAA") == clean(b"w: x", KS + b"\tBBBB"))
check("data_trace: a differing plain diagnostic line IS a mover",
      clean(b"w: one") != clean(b"w: two"))
check("data_trace: a differing `KSRCTRACE` line without the tab IS a mover",
      clean(b"KSRCTRACE object 1") != clean(b"KSRCTRACE object 2"))
check("data_trace: a differing `KSTRACEX` line IS a mover",
      clean(b"KSTRACEX\t1") != clean(b"KSTRACEX\t2"))
check("data_trace: a KSTRACE record never reaches the clean text",
      b"KSTRACE\t" not in clean(b"w: x", b"KSTRACE\t1\tq\tr\tb"))
sys.exit(1 if fails else 0)
