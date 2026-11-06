# span_cards/slot/run.py — ONE JOB of the stage-2 window (span_cards.md §3.3): its dry run and its work.
#   run.py dry JOB RUNDIR RUN_ID    links the job's seven launch executables and asserts placement (link.py),
#                                   builds or checks `ctl` (its sha-256), runs THE ANSWER GATE on launch 1
#                                   and on ctl (no clock); prints the job's group count
#   run.py run JOB RUNDIR RUN_ID    the work: per launch l = 1..7, the per-launch quiet check (one load sample,
#                                   the queue and the box lock; if not quiet, wait for the start gate's
#                                   two-sample quiet, at most 5 minutes per job, else the job FAILS), then R
#                                   rounds, each `ctl` once and the launch executable once, pinned to CPU 7;
#                                   then the cells (the median over rounds per point, §3.4 step 1) into
#                                   RUNDIR/cells.<JOB>.tsv and `== s2 GROUP done <group>` per group
#   run.py screen RUNDIR            THE PLACEMENT SCREEN (§3.2): J2's unit group (walk and twin) at its seven
#                                   placements, one round each, and the unit's §3.4 noise against its half gate
# Every command it runs is printed to RUNDIR/transcript.tsv (the per-round evidence, its sha in the record).
import hashlib, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plan, link, est  # noqa: E402

TREE = plan.TREE
MAIN = "/home/pcrec/projects/pcrec"
CPU, SIB = "7", "15"
WAIT_BOUND = 300                    # the per-job quiet wait bound (§3.3): UNMEASURED DEFAULT (D149)

def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return r.returncode, r.stdout, r.stderr

def ctl_check(rundir):
    exe = link.link_ctl(rundir)
    want = open(os.path.join(rundir, "ctl.sha256")).read().strip()
    got = hashlib.sha256(open(exe, "rb").read()).hexdigest()
    if got != want:
        raise SystemExit("run: ctl's sha-256 %s is not the window's %s" % (got, want))
    return exe, got

def gate(exe):
    rc, out, err = sh([exe, "gate"])
    last = (out.strip().splitlines() or ["(no output)"])[-1]
    if rc:
        raise SystemExit("run: THE ANSWER GATE refused %s:\n%s%s" % (exe, out[-2000:], err[-500:]))
    return last

def groups(job):
    jobs, _r, _f, _u = plan.build()
    return sorted({a.group for a in jobs[job]})

def dry(job, rundir, run_id):
    os.makedirs(rundir, exist_ok=True)
    exe_ctl, sha = ctl_check(rundir)
    print("ctl: %s sha256 %s" % (exe_ctl, sha))
    print("ctl gate: " + gate(exe_ctl))
    exes = link.link_job(job, rundir, run_id)
    print("%s launch 1 gate: %s" % (job, gate(exes[1])))
    g = groups(job)
    print("would run in %s: run.py run %s (run id %s), 7 launches x 7 rounds pinned to cpu %s, groups %d"
          % (rundir, job, run_id, CPU, len(g)))
    return len(g)

def quiet_now():
    rq = os.path.join(MAIN, "worktrees", ".boxqueue", "running")
    mine = os.environ.get("BQ_JOB", "")
    others = [e.name for e in os.scandir(rq) if mine not in e.name] if os.path.isdir(rq) and mine else \
             ([e.name for e in os.scandir(rq)] if os.path.isdir(rq) else [])
    rc, out, _e = sh([os.path.join(MAIN, "scripts", "boxlock"), "status"])
    held = out.startswith("HELD") and not (mine and ("queue:" + mine) in out)
    load = float(open("/proc/loadavg").read().split()[0])
    return load < 2.0 and not held and not others, "load1 %.2f lock %s queue %s" % (
        load, "held" if held else "free", ",".join(others) or "-")

def wait_quiet(t0, log):
    ok, why = quiet_now()
    log("quiet\t%s\t%s" % ("yes" if ok else "no", why))
    if ok:
        return True
    first = None
    while time.time() - t0 < WAIT_BOUND:
        time.sleep(5)
        ok, why = quiet_now()
        if not ok:
            first = None
            continue
        first = first or time.time()
        if time.time() - first >= 55:
            log("quiet\tyes-after-wait\t%s" % why)
            return True
    log("quiet\twait-timeout\t%s" % why)
    return False

def run(job, rundir, run_id):
    exe_ctl, sha = ctl_check(rundir)
    tp = open(os.path.join(rundir, "transcript.tsv"), "a")
    def log(s):
        tp.write("%s\t%s\n" % (job, s))
        tp.flush()
    log("start\trun %s ctl %s" % (run_id, sha))
    pts = {}
    t0 = time.time()
    for l in range(1, plan.L_LAUNCHES + 1):
        if not wait_quiet(t0, log):
            print("== s2 JOB %s FAILED wait-timeout at launch %d" % (job, l))
            return 5
        exe = os.path.join(rundir, job, "L%d" % l, "%s.L%d" % (job, l))
        for r in range(1, plan.R_ROUNDS + 1):
            for who, x in (("ctl", exe_ctl), ("arm", exe)):
                nf = os.path.join(rundir, job, "L%d" % l, "N.%s" % who)
                rc, out, err = sh(["taskset", "-c", CPU, x, "round", str(r), nf])
                if rc:
                    print("== s2 JOB %s FAILED: %s round %d rc %d %s" % (job, x, r, rc, err[-300:]))
                    return 1
                for ln in out.splitlines():
                    p = ln.split("\t")
                    log("L%d\tR%d\t%s" % (l, r, ln))
                    pts.setdefault((p[1], int(p[2]), l), []).append(int(p[5]))
    tp.close()
    jobs, _r, _f, _u = plan.build()
    grp = {a.name: a for a in jobs[job]}
    if job == "J1":
        return run_j1(rundir, run_id, pts, grp)
    rows = []
    for (arm, length, l), v in sorted(pts.items()):
        a = grp[arm]
        base = a.base if a.base and not arm.startswith("base.") else None
        cid = "%s/%s/%d/%d" % (a.group, arm, length, l) + ("/" + base if base else "")
        ev = "-" if a.events is None else str(a.events)
        rows.append("\t".join([cid, a.group, arm, str(length), str(l), "med", ev, str(est.med(v))]))
    open(os.path.join(rundir, "cells.%s.tsv" % job), "w").write(
        "#" + "\t".join(est.CELL_COLS) + "\n" + "\n".join(rows) + "\n")
    for g in groups(job):
        print("== s2 GROUP done %s" % g)
    return 0

J1_COLS = ["cell", "pattern", "subject", "regime", "width", "launch", "ns_e6"]

def run_j1(rundir, run_id, pts, grp):
    """J1's END (§3.5 "The run record" step 1, §3.6): its cells (each the median over rounds, §3.4 step 1) into
    RUNDIR/j1_cells.tsv in j1_rule.py's columns (width `128#b` the twin; the control's points stay in the
    transcript), then record.py j1, the run record's one writer, with the frozen code commit (CODE_COMMIT, else
    the tree's HEAD)."""
    rows = []
    for (arm, length, l), v in sorted(pts.items()):
        a = grp[arm]
        if a.kind != "j1":
            continue
        pid, subj, regime, w = a.fixture
        wt = "%d#b" % w if arm.endswith("#b") else str(w)
        rows.append("\t".join(["J1/%s/%s/%s/%s/%d" % (pid, subj, regime, wt, l), pid, subj, regime, wt, str(l),
                               str(est.med(v))]))
    open(os.path.join(rundir, "j1_cells.tsv"), "w").write("#" + "\t".join(J1_COLS) + "\n" + "\n".join(rows) + "\n")
    commit = os.environ.get("CODE_COMMIT") or sh(["git", "-C", TREE, "rev-parse", "HEAD"])[1].strip()
    rc, out, err = sh([sys.executable, "-I", os.path.join(HERE, "record.py"), "j1", rundir, run_id, commit])
    sys.stdout.write(out)
    if rc:
        print("== s2 JOB J1 FAILED: record.py j1 rc %d %s" % (rc, err[-300:]))
        return 1
    for g in groups("J1"):
        print("== s2 GROUP done %s" % g)
    return 0

def screen(rundir, run_id):
    """J2's unit group only: the walk and its twin at their seven placements, ONE round each."""
    exe_ctl, _sha = ctl_check(rundir)
    exes = link.link_job("J2", rundir, run_id)
    x, xb = [], []
    for l in range(1, 8):
        u = None
        for who, e in (("ctl", exe_ctl), ("arm", exes[l])):
            nf = os.path.join(rundir, "J2", "L%d" % l, "N.screen.%s" % who)
            rc, out, err = sh(["taskset", "-c", CPU, e, "round", "1", nf])
            if rc:
                raise SystemExit("screen: %s rc %d %s" % (e, rc, err))
            c = {(p[1], int(p[2])): int(p[5]) for p in (ln.split("\t") for ln in out.splitlines())}
            if who == "ctl":
                u = est.slope([(n, c[("ctl", n)]) for n in plan.LENGTHS])
            else:
                for arm, dst in (("kit.find_byte.walk", x), ("kit.find_byte.walk#b", xb)):
                    a = est.slope([(n, c[(arm, n)]) for n in plan.LENGTHS])
                    dst.append(est.rhafz(a * 10**6, u))
    W = est.med(x)
    xa = [est.rhafz(t * 10**6, W) for t in x]
    xba = [est.rhafz(t * 10**6, W) for t in xb]
    aa = est.med([abs(xba[i] - xa[i]) for i in range(7)])
    noise = est.isqrt_rn(aa * aa + est.sp2(xa))
    half = plan.GATE_E6 // 2
    print("screen: unit x_l %s, twin %s" % (xa, xba))
    print("== s2 SCREEN unit noise_e6 %d (%.3f %%) vs the half gate %d (%.1f %%): %s"
          % (noise, noise / 1e4, half, half / 1e4, "UNDER" if noise * 10**6 <= half * 10**6 else "OVER: do not request the window"))
    return 0 if noise <= half else 3

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "dry":
        sys.exit(0 if dry(sys.argv[2], sys.argv[3], sys.argv[4]) else 1)
    if cmd == "run":
        sys.exit(run(sys.argv[2], sys.argv[3], sys.argv[4]))
    if cmd == "screen":
        sys.exit(screen(sys.argv[2], sys.argv[3]))
    raise SystemExit("run.py: dry | run | screen")
