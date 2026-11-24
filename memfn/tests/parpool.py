#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (lane bsu6par, the owner's ruling 2026-11-23: "if its a test to be run
# repeatedly or it takes a long time it should be reviewed for parallelism").
"""memfn/tests/parpool.py -- ONE ordered process pool for the kit's long test runners.

A runner splits its work into UNITS, each a callable that prints what the serial run printed at that point and returns a
value. `run(units, jobs)` runs them and writes every unit's printed text to stdout IN THE LIST ORDER, so the output of
`jobs` N is byte-identical to `jobs` 1 provided the units are independent (no unit reads state another unit left behind).

  jobs <= 1   today's serial path: each unit called in order, in this process, its output streamed as it prints; no
              fork, no capture, no scratch change
  jobs N > 1  up to N forked processes, ONE FORK PER UNIT (no interpreter state carries between units); each gets ITS
              OWN scratch directory (PCREC_TMPDIR, TMPDIR and `tempfile.tempdir` point at <root>/u<index>, root a fresh
              directory under the caller's PCREC_TMPDIR or TMPDIR, removed at the end); a unit's stdout is captured in
              its process and written by the parent once every earlier unit's has been written. Ready units start
              LONGEST `Unit.cost` FIRST (ties in list order): speed only, never the output order

A unit may NEED earlier units' values: `Unit(name, fn, needs=(i, j))` calls fn(value_i, value_j) once both are done (an
index into the list, earlier than the unit itself), in the serial path too, so both paths compute the same thing.
A unit that raises stops the run: the parent writes the output of every unit before it, then the failing unit's
captured output, then raises UnitError carrying the worker's traceback (the serial path raises the exception itself).
A worker that DIES without a result (os._exit, a kill) fails the run within a second: UnitError naming the unit.

PARPOOL_TIMES=FILE appends one `name<TAB>seconds<TAB>pid` line per unit (a profile for sizing units; never stdout).
PARPOOL_PLANT=shared-scratch gives EVERY worker the SAME scratch directory: the control that a race between workers
shows up as a difference (`python3 memfn/tests/parpool.py selftest` reads it red as designed).

Fork only (the units are closures, inherited by the workers rather than pickled): Linux; on macOS `fork` is
available but not Python's default; stdout only (a unit's stderr goes straight to the inherited descriptor).
"""
import io, os, shutil, sys, tempfile, time, traceback


class Unit:
    __slots__ = ("name", "fn", "needs", "cost")

    def __init__(self, name, fn, needs=(), cost=0.0):
        """`cost`: seconds the unit is expected to take; only the SUBMISSION order reads it (longest first)."""
        self.name, self.fn, self.needs, self.cost = name, fn, tuple(needs), cost


class UnitError(RuntimeError):
    pass


def default_jobs():
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:
        return os.cpu_count() or 1


def jobs_from_args(args, default=None):
    """Strip `-j N`, `-jN`, `--jobs N`, `--jobs=N` from args; returns (jobs, the rest). No option: `default`, else
    every CPU this process may run on. A missing or non-positive value raises ValueError (the caller refuses)."""
    rest, jobs, i = [], None, 0
    while i < len(args):
        a = args[i]
        val = None
        if a in ("-j", "--jobs"):
            if i + 1 >= len(args):
                raise ValueError("%s needs a value" % a)
            i += 1
            val = args[i]
        elif a.startswith("--jobs="):
            val = a[len("--jobs="):]
        elif a.startswith("-j") and not a.startswith("--"):
            val = a[2:]
        else:
            rest.append(a)
            i += 1
            continue
        if not val.isdigit() or int(val) < 1:
            raise ValueError("-j takes a positive count, got %r" % val)
        jobs = int(val)
        i += 1
    return (jobs if jobs is not None else (default if default is not None else default_jobs())), rest


_UNITS = None           # the unit list, set before the children fork: they inherit it
_SCRATCH = None


def _times(name, secs):
    path = os.environ.get("PARPOOL_TIMES")
    if path:
        with open(path, "a") as f:
            f.write("%s\t%.2f\t%d\n" % (name, secs, os.getpid()))


def _scratch_init(root, plant, i):
    global _SCRATCH
    _SCRATCH = os.path.join(root, "w-shared" if plant == "shared-scratch" else "u%d" % i)
    os.makedirs(_SCRATCH, exist_ok=True)
    os.environ["PCREC_TMPDIR"] = os.environ["TMPDIR"] = _SCRATCH
    tempfile.tempdir = _SCRATCH


def _run_index(i, vals):
    u = _UNITS[i]
    buf, real = io.StringIO(), sys.stdout
    sys.stdout = buf
    t0 = time.monotonic()
    try:
        v = u.fn(*vals)
        err = None
    except BaseException:           # noqa: B036 -- a SystemExit in a unit is a unit failure too
        v, err = None, traceback.format_exc()
    finally:
        sys.stdout = real
    _times(u.name, time.monotonic() - t0)
    return buf.getvalue(), v, err


def _child(i, vals, conn, root, plant):
    """One forked process per unit (STATE-CONTROL: no unit sees interpreter state another left behind)."""
    try:
        _scratch_init(root, plant, i)
        conn.send(_run_index(i, vals))
        conn.close()
    finally:
        os._exit(0)


def _check(units):
    for i, u in enumerate(units):
        if any(not (isinstance(j, int) and 0 <= j < i) for j in u.needs):
            raise ValueError("unit %d (%s) needs %s: only earlier units" % (i, u.name, u.needs))


def closure(units, want):
    """The set `want` (unit indices) plus every unit they need, transitively (a need's own needs too)."""
    want, todo = set(want), list(want)
    while todo:
        for j in units[todo.pop()].needs:
            if j not in want:
                want.add(j)
                todo.append(j)
    return want


def run(units, jobs, out=None):
    """Run `units` (a list of Unit); returns their values in order. Output goes to `out` (default sys.stdout).
    Pool mode: one forked process per unit, at most `jobs` at once, ready units submitted LONGEST `cost` FIRST (ties in
    list order); a child that dies without a result fails the run at once, naming its unit (DEADWORKER)."""
    units = list(units)
    _check(units)
    out = out if out is not None else sys.stdout
    vals = [None] * len(units)
    if jobs <= 1 or len(units) <= 1:
        for i, u in enumerate(units):
            t0 = time.monotonic()
            if out is sys.stdout:
                vals[i] = u.fn(*[vals[j] for j in u.needs])
            else:
                real = sys.stdout
                sys.stdout = out
                try:
                    vals[i] = u.fn(*[vals[j] for j in u.needs])
                finally:
                    sys.stdout = real
            _times(u.name, time.monotonic() - t0)
        return vals
    import multiprocessing, multiprocessing.connection as mpc
    global _UNITS
    out.flush()
    sys.stdout.flush()
    base = os.environ.get("PCREC_TMPDIR") or os.environ.get("TMPDIR") or tempfile.gettempdir()
    os.makedirs(base, exist_ok=True)
    root = tempfile.mkdtemp(prefix="parpool.", dir=base)
    plant = os.environ.get("PARPOOL_PLANT", "")
    _UNITS = units
    done, live, started, written = {}, {}, set(), 0     # live: unit index -> (Process, parent's read end)
    ctx = multiprocessing.get_context("fork")
    try:
        while written < len(units):
            ready = sorted((i for i, u in enumerate(units)
                            if i not in started and all(j in done for j in u.needs)), key=lambda i: (-units[i].cost, i))
            for i in ready:
                if len(live) >= jobs:
                    break
                started.add(i)
                rc, wc = ctx.Pipe(duplex=False)
                pr = ctx.Process(target=_child, args=(i, [vals[j] for j in units[i].needs], wc, root, plant))
                pr.start()
                wc.close()
                live[i] = (pr, rc)
            if not live:
                raise UnitError("no unit runnable (a need never finished)")
            mpc.wait([rc for _p, rc in live.values()], timeout=1.0)
            for i in sorted(live):
                pr, rc = live[i]
                if not rc.poll():
                    continue
                try:
                    text, v, err = rc.recv()
                except EOFError:        # closed with no result: the child died (os._exit, a signal)
                    pr.join(5)
                    code = pr.exitcode
                    while written in done:      # whatever completed in order before the dead unit is still written
                        out.write(done[written][0])
                        written += 1
                    out.flush()
                    raise UnitError("unit %d (%s): its worker died without a result (exit code %s)"
                                    % (i, units[i].name, code))
                rc.close()
                pr.join()
                del live[i]
                done[i] = (text, err)
                vals[i] = v
            while written in done:
                text, err = done[written]
                out.write(text)
                out.flush()
                if err is not None:
                    raise UnitError("unit %d (%s) failed in its worker:\n%s" % (written, units[written].name, err))
                written += 1
    finally:
        for pr, rc in live.values():
            if pr.is_alive():
                pr.terminate()
            pr.join(5)
        _UNITS = None
        shutil.rmtree(root, ignore_errors=True)
    return vals


# ---- the pool's own checks ------------------------------------------------------------------------------------------
def _race_unit(k, sleep):
    """Writes its id to a FIXED name in its scratch, sleeps, reads it back: two units sharing a scratch read each other."""
    def fn():
        p = os.path.join(os.environ.get("PCREC_TMPDIR") or tempfile.gettempdir(), "race.txt")
        with open(p, "w") as f:
            f.write("unit %d\n" % k)
        time.sleep(sleep)
        print("unit %d read back: %s" % (k, open(p).read().strip()))
        return k
    return fn


def selftest():
    """The pool's checks: serial vs 4 workers byte-identical (with units finishing out of order), `needs` passes values,
    a failing unit is an error, and the planted shared scratch makes the race units' output DIFFER (red as designed)."""
    bad = 0

    def row(ok, what):
        nonlocal bad
        bad += not ok
        print("%s parpool: %s" % ("ok  " if ok else "FAIL", what))

    def units():
        us = [Unit("race%d" % k, _race_unit(k, 0.05 * ((7 - k) % 4) + 0.1)) for k in range(8)]
        us.append(Unit("sum", lambda *a: print("sum of the race units' values %d" % sum(a)) or sum(a), needs=range(8)))
        return us
    saved = {k: os.environ.get(k) for k in ("PCREC_TMPDIR", "PARPOOL_PLANT")}
    base = os.environ.get("PCREC_TMPDIR") or os.environ.get("TMPDIR") or tempfile.gettempdir()
    own = tempfile.mkdtemp(prefix="parpool_selftest.", dir=base)
    try:
        os.environ["PCREC_TMPDIR"] = own
        os.environ.pop("PARPOOL_PLANT", None)
        ser, par = io.StringIO(), io.StringIO()
        v1 = run(units(), 1, out=ser)
        v4 = run(units(), 4, out=par)
        row(ser.getvalue() == par.getvalue() and v1 == v4 and v1[-1] == 28 and ser.getvalue().count("\n") == 9,
            "serial and 4 workers byte-identical (%d lines; values %s)" % (ser.getvalue().count("\n"), v4))
        os.environ["PARPOOL_PLANT"] = "shared-scratch"
        planted = io.StringIO()
        run(units(), 4, out=planted)
        row(planted.getvalue() != ser.getvalue(),
            "CONTROL: the planted shared scratch DIFFERS from serial (%d of 8 race lines changed)"
            % sum(a != b for a, b in zip(planted.getvalue().splitlines(), ser.getvalue().splitlines())))
        os.environ.pop("PARPOOL_PLANT", None)
        failing = [Unit("a", lambda: print("before")), Unit("boom", lambda: 1 / 0), Unit("c", lambda: print("after"))]
        got, msg = io.StringIO(), ""
        try:
            run(failing, 3, out=got)
        except UnitError as e:
            msg = str(e)
        row("ZeroDivisionError" in msg and got.getvalue() == "before\n",
            "a failing unit is an error naming it, the units before it written, none after (%r)" % got.getvalue())
        # DEADWORKER: a unit whose worker dies (os._exit) fails the run within seconds, naming the unit; never a hang
        dying = [Unit("a", lambda: print("before")), Unit("dies", lambda: os._exit(7)),
                 Unit("slow", lambda: time.sleep(30) or print("never"))]
        got, msg, t0 = io.StringIO(), "", time.monotonic()
        try:
            run(dying, 3, out=got)
        except UnitError as e:
            msg = str(e)
        dt = time.monotonic() - t0
        row("dies" in msg and "died" in msg and dt < 10 and "never" not in got.getvalue(),
            "a worker killed with os._exit fails the run in %.1f s, naming its unit (%r)" % (dt, msg))
        # STATE-CONTROL: one fork per unit, so a global one unit sets is not seen by the next unit on any worker
        leak = {"v": 0}

        def setter():
            leak["v"] += 1
            return leak["v"]
        sc = [Unit("set%d" % k, setter) for k in range(6)]
        row(run(sc, 2, out=io.StringIO()) == [1] * 6 and leak["v"] == 0,
            "one fork per unit: six units on two workers each see a fresh interpreter state")
        # TAIL: submission order follows cost (longest first), the output stays in list order
        stamp = os.path.join(own, "order.txt")

        def logger(k):
            def fn():
                with open(stamp, "a") as f:
                    f.write("%d\n" % k)
                print("unit %d" % k)
            return fn
        cs = [Unit("c%d" % k, logger(k), cost=float(k)) for k in range(5)]
        o1, o2 = io.StringIO(), io.StringIO()
        run([Unit(u.name, u.fn) for u in cs], 1, out=o1)
        os.remove(stamp)
        run(cs, 1 + 1, out=o2)         # two workers: 4 and 3 start first
        started = open(stamp).read().split()
        row(o1.getvalue() == o2.getvalue() and sorted(started[:2]) == ["3", "4"],
            "longest-first submission (started %s) with the output still in list order" % " ".join(started))
        # CLOSURE: a depth-2 chain whose last unit lists only its direct need still pulls in the whole chain
        chain = [Unit("c0", lambda: 1), Unit("c1", lambda x: x + 1, needs=(0,)), Unit("c2", lambda x: x + 1, needs=(1,)),
                 Unit("c3", lambda x: x + 1, needs=(2,)), Unit("other", lambda: 9)]
        row(closure(chain, {3}) == {0, 1, 2, 3} and closure(chain, {4}) == {4} and closure(chain, {1}) == {0, 1},
            "closure of a depth-3 needs chain from its last unit: %s" % sorted(closure(chain, {3})))
        j = [jobs_from_args(a, default=5) for a in (["x"], ["-j", "3", "x"], ["-j7"], ["--jobs=2"], ["--jobs", "4"])]
        refused = 0
        for a in (["-j"], ["-j0"], ["--jobs=x"]):
            try:
                jobs_from_args(a)
            except ValueError:
                refused += 1
        row(j == [(5, ["x"]), (3, ["x"]), (7, []), (2, []), (4, [])] and refused == 3,
            "-j parsing %s, refusals %d of 3" % (j, refused))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(own, ignore_errors=True)
    print("parpool selftest: %d failed" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        sys.exit(selftest())
    sys.stderr.write("usage: parpool.py selftest\n")
    sys.exit(2)
