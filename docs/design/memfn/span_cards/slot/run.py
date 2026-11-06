# span_cards/slot/run.py — ONE JOB of the stage-2 window (span_cards.md §3.3): its dry run and its work.
#   run.py dry JOB RUNDIR RUN_ID    freezes the plan (RUNDIR/plan.tsv, the same bytes for every job of the run,
#                                   r9 G3), builds or checks `ctl` (its sha-256), links the job's seven launch
#                                   executables and asserts placement (link.py), runs THE ANSWER GATE on ctl and
#                                   on EVERY launch (no clock; the timed entry over the timed population, its
#                                   arms, pools, subjects and timed calls asserted against the plan, r9 G1), and
#                                   writes the job's MANIFEST (RUNDIR/JOB/manifest.tsv: the run id and the sha-256
#                                   of every input and executable the work will time); prints the group count
#   run.py run JOB RUNDIR RUN_ID    the work: the MANIFEST first (a mismatch refuses: the work times only the
#                                   dry run's executables), the window facts into the run record (record.py
#                                   window), then per launch l = 1..L the per-launch quiet check (one load sample,
#                                   the queue and the box lock; if not quiet, wait for the start gate's two-sample
#                                   quiet, the job's WAITING bounded at WAIT_BOUND in total, else the job FAILS),
#                                   then R rounds, each `ctl` once and the launch executable once, pinned to the
#                                   plan's CPU; then the cells (the median over rounds per point, §3.4 step 1)
#                                   into RUNDIR/cells.<JOB>.tsv under a `#run_id` line and `== s2 GROUP done
#                                   <group>` per group
#   run.py screen RUNDIR RUN_ID     THE PLACEMENT SCREEN (§3.2): J2's unit group (walk and twin) at its seven
#                                   placements (J2's dry-run executables, by its manifest), one round each, and the
#                                   unit's §3.4 noise against its half gate
# Every command it runs is printed to RUNDIR/transcript.tsv (the per-round evidence, its sha in the record).
# Exit codes: dry 0 (green) or a refusal's 1/3; run 0, 1 (a round or record step failed), 5 (wait-timeout);
# screen 0 (under the half gate), 3 (over).
# Environment: BQ_JOB (boxqueue's job name: the quiet check ignores this job's own queue entry and lock),
# CODE_COMMIT (the window's frozen commit, else the tree's HEAD), SLOT_TREE (plan.py).
import hashlib, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plan, link, est  # noqa: E402

TREE = plan.TREE
CPU = plan.TIMING_CPU
WAIT_BOUND = 300                    # the job's total quiet wait (§3.3): UNMEASURED DEFAULT (D149)
QUIET_LOAD = 2.0                    # load1 below which the box is quiet (§3.3): UNMEASURED DEFAULT (D149)
QUIET_HOLD = 55                     # seconds of continuous quiet that end a wait (§3.3): UNMEASURED DEFAULT (D149)
QUIET_POLL = 5                      # the wait's sample period, seconds: UNMEASURED DEFAULT (D149)


def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return r.returncode, r.stdout, r.stderr


def main_tree():
    """the main checkout (the box queue and lock live there): the parent of the tree's common git dir"""
    rc, out, err = sh(["git", "-C", TREE, "rev-parse", "--path-format=absolute", "--git-common-dir"])
    if rc:
        raise SystemExit("run: git rev-parse --git-common-dir in %s: rc %d %s" % (TREE, rc, err[-200:]))
    return os.path.dirname(out.strip())


def code_commit():
    c = os.environ.get("CODE_COMMIT")
    if c:
        return c
    rc, out, err = sh(["git", "-C", TREE, "rev-parse", "HEAD"])
    if rc or not out.strip():
        raise SystemExit("run: git rev-parse HEAD in %s: rc %d %s" % (TREE, rc, err[-200:]))
    return out.strip()


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def ctl_check(rundir):
    exe = link.link_ctl(rundir)
    want = open(os.path.join(rundir, "ctl.sha256")).read().strip()
    got = sha(exe)
    if got != want:
        raise SystemExit("run: ctl's sha-256 %s is not the window's %s" % (got, want))
    return exe, got


GATE_LINE = re.compile(r"== s2 GATE ok: (\d+) arms, (\d+) pools, (\d+) subjects, (\d+) timed calls, 0 misses$")


def gate(exe, arms):
    """THE ANSWER GATE on one executable, its population asserted against the arms it was linked from: every arm,
    every length, every pool subject (1 for a whole artifact, else POOL_BYTES / length), each timed once (r9 G1)"""
    rc, out, err = sh([exe, "gate"])
    last = (out.strip().splitlines() or ["(no output)"])[-1]
    if rc:
        raise SystemExit("run: THE ANSWER GATE refused %s:\n%s%s" % (exe, out[-2000:], err[-500:]))
    m = GATE_LINE.match(last)
    want = (len(arms), sum(len(a.lengths) for a in arms),
            sum(1 if a.kind in ("enter", "j1") else plan.POOL_BYTES // x for a in arms for x in a.lengths))
    if not m or tuple(int(g) for g in m.groups()[:3]) != want or m.group(4) != m.group(3):
        raise SystemExit("run: THE ANSWER GATE's population on %s is %r; the plan's is %d arms, %d pools, %d "
                         "subjects, each timed once" % (exe, last, *want))
    return last


def job_arms(job):
    jobs, _r, _f, _u = plan.build()
    if job not in jobs:
        raise SystemExit("run: no job %s in the plan (%s)" % (job, ",".join(sorted(jobs))))
    return jobs[job]


def freeze(rundir):
    """the run's frozen plan: written by the first dry run, every later one must equal it"""
    p = os.path.join(rundir, "plan.tsv")
    t = plan.frozen_text()
    if os.path.exists(p) and open(p).read() != t:
        raise SystemExit("run: REFUSED: %s differs from today's plan (an input moved inside the run; a new RUNDIR)" % p)
    if not os.path.exists(p):
        open(p + ".tmp", "w").write(t)
        os.replace(p + ".tmp", p)
    return p


def manifest(job, rundir, run_id, exes):
    """{name: value}: the run id and the sha-256 of every input and executable the job's work times"""
    m = {"run_id": run_id, "plan": sha(os.path.join(rundir, "plan.tsv")), "fx": sha(link.fx_path(rundir)),
         "libpcrec": sha(link.FX_INPUTS[1]), "ctl": open(os.path.join(rundir, "ctl.sha256")).read().strip(),
         "placement": sha(os.path.join(rundir, job, "placement.tsv")),
         "cell_text": sha(os.path.join(rundir, job, "cell_text.tsv"))}
    for l in range(1, plan.L_LAUNCHES + 1):
        m["L%d" % l] = sha(exes[l])
    return m


def launch_exe(rundir, job, l):
    return os.path.join(rundir, job, "L%d" % l, "%s.L%d" % (job, l))


def verify_manifest(job, rundir, run_id):
    """the work's first act: today's inputs and the RUNDIR's executables are the dry run's, under this run id"""
    p = os.path.join(rundir, job, "manifest.tsv")
    if not os.path.exists(p):
        raise SystemExit("run: REFUSED: %s is absent (run.py dry %s first)" % (p, job))
    want = dict(ln.rstrip("\n").split("\t", 1) for ln in open(p) if ln.strip() and not ln.startswith("#"))
    if open(os.path.join(rundir, "plan.tsv")).read() != plan.frozen_text():
        raise SystemExit("run: REFUSED: today's plan is not the run's frozen plan.tsv")
    got = manifest(job, rundir, run_id, {l: launch_exe(rundir, job, l) for l in range(1, plan.L_LAUNCHES + 1)})
    bad = sorted(k for k in set(want) | set(got) if want.get(k) != got.get(k))
    if bad:
        raise SystemExit("run: REFUSED: %s's manifest differs in %s (the dry run linked other executables or "
                         "inputs, or another run id)" % (job, ",".join(bad)))


def dry(job, rundir, run_id):
    os.makedirs(rundir, exist_ok=True)
    arms = [a for a in job_arms(job) if a.kind != "ctl"]
    print("plan: %s frozen (%s)" % (freeze(rundir), sha(os.path.join(rundir, "plan.tsv"))[:16]))
    exe_ctl, csha = ctl_check(rundir)
    print("ctl: %s sha256 %s" % (exe_ctl, csha))
    print("ctl gate: " + gate(exe_ctl, [plan.Arm("ctl", "ctl", "ctl", "walk", lengths=plan.LENGTHS)]))
    exes = link.link_job(job, rundir, run_id)
    for l in range(1, plan.L_LAUNCHES + 1):
        print("%s launch %d gate: %s" % (job, l, gate(exes[l], arms)))
    m = manifest(job, rundir, run_id, exes)
    open(os.path.join(rundir, job, "manifest.tsv"), "w").write(
        "#name\tvalue\n" + "".join("%s\t%s\n" % kv for kv in sorted(m.items())))
    g = plan.groups(plan.build()[0], job)
    print("would run in %s: run.py run %s (run id %s), %d launches x %d rounds pinned to cpu %s, groups %d"
          % (rundir, job, run_id, plan.L_LAUNCHES, plan.R_ROUNDS, CPU, len(g)))
    return len(g)


def quiet_now(main):
    rq = os.path.join(main, "worktrees", ".boxqueue", "running")
    mine = os.environ.get("BQ_JOB", "")
    others = [e.name for e in os.scandir(rq) if not mine or mine not in e.name] if os.path.isdir(rq) else []
    rc, out, _e = sh([os.path.join(main, "scripts", "boxlock"), "status"])
    if rc not in (0, 1):
        raise SystemExit("run: boxlock status rc %d" % rc)
    held = out.startswith("HELD") and not (mine and ("queue:" + mine) in out)
    load = float(open("/proc/loadavg").read().split()[0])
    return load < QUIET_LOAD and not held and not others, "load1 %.2f lock %s queue %s" % (
        load, "held" if held else "free", ",".join(others) or "-")


class Waiter:
    """the job's quiet waits, bounded in TOTAL waiting time (r9 W3: never from the job's start)"""
    def __init__(self, main, log):
        self.main, self.log, self.waited = main, log, 0.0

    def quiet(self):
        ok, why = quiet_now(self.main)
        self.log("quiet\t%s\t%s" % ("yes" if ok else "no", why))
        if ok:
            return True
        first = None
        while self.waited < WAIT_BOUND:
            time.sleep(QUIET_POLL)
            self.waited += QUIET_POLL
            ok, why = quiet_now(self.main)
            if not ok:
                first = None
                continue
            first = first if first is not None else self.waited
            if self.waited - first >= QUIET_HOLD:
                self.log("quiet\tyes-after-wait\t%s (waited %ds of %ds)" % (why, self.waited, WAIT_BOUND))
                return True
        self.log("quiet\twait-timeout\t%s" % why)
        return False


def run(job, rundir, run_id):
    verify_manifest(job, rundir, run_id)
    exe_ctl, csha = ctl_check(rundir)
    commit = code_commit()
    rc, out, err = sh([sys.executable, "-I", os.path.join(HERE, "record.py"), "window", rundir, run_id, commit])
    if rc:
        print("== s2 JOB %s FAILED: record.py window rc %d %s%s" % (job, rc, out[-300:], err[-300:]))
        return 1
    arms = {a.name: a for a in job_arms(job)}
    pts = {}
    with open(os.path.join(rundir, "transcript.tsv"), "a") as tp:
        def log(s):
            tp.write("%s\t%s\n" % (job, s))
            tp.flush()
        log("start\trun %s ctl %s commit %s" % (run_id, csha, commit))
        w = Waiter(main_tree(), log)
        for l in range(1, plan.L_LAUNCHES + 1):
            if not w.quiet():
                print("== s2 JOB %s FAILED wait-timeout at launch %d" % (job, l))
                return 5
            exe = launch_exe(rundir, job, l)
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
    want = {(a.name, x, l) for a in arms.values() for x in a.lengths for l in range(1, plan.L_LAUNCHES + 1)}
    if set(pts) != want or any(len(v) != plan.R_ROUNDS for v in pts.values()):
        print("== s2 JOB %s FAILED: the rounds timed %d points, the plan names %d (x %d rounds)"
              % (job, len(pts), len(want), plan.R_ROUNDS))
        return 1
    if job == "J1":
        return run_j1(rundir, run_id, pts, arms, commit)
    rows = [est.cell_row(arms[arm], length, l, est.med(v)) for (arm, length, l), v in sorted(pts.items())]
    open(os.path.join(rundir, "cells.%s.tsv" % job), "w").write(est.cells_text(run_id, rows))
    for g in plan.groups(plan.build()[0], job):
        print("== s2 GROUP done %s" % g)
    return 0


J1_COLS = ["cell", "pattern", "subject", "regime", "width", "launch", "ns_e6"]


def run_j1(rundir, run_id, pts, grp, commit):
    """J1's END (§3.5 "The run record" step 1, §3.6): its cells (each the median over rounds, §3.4 step 1) into
    RUNDIR/j1_cells.tsv in j1_rule.py's columns (width `128#b` the twin; the control's points stay in the
    transcript), then record.py j1, the run record's one writer"""
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
    rc, out, err = sh([sys.executable, "-I", os.path.join(HERE, "record.py"), "j1", rundir, run_id, commit])
    sys.stdout.write(out)
    if rc:
        print("== s2 JOB J1 FAILED: record.py j1 rc %d %s" % (rc, err[-300:]))
        return 1
    for g in plan.groups(plan.build()[0], "J1"):
        print("== s2 GROUP done %s" % g)
    return 0


def screen(rundir, run_id):
    """J2's unit group only: the walk and its twin at their seven placements, ONE round each, on J2's dry-run
    executables (its manifest)"""
    verify_manifest("J2", rundir, run_id)
    exe_ctl, _sha = ctl_check(rundir)
    x, xb = [], []
    for l in range(1, plan.L_LAUNCHES + 1):
        u = None
        for who, e in (("ctl", exe_ctl), ("arm", launch_exe(rundir, "J2", l))):
            nf = os.path.join(rundir, "J2", "L%d" % l, "N.screen.%s" % who)
            rc, out, err = sh(["taskset", "-c", CPU, e, "round", "1", nf])
            if rc:
                raise SystemExit("screen: %s rc %d %s" % (e, rc, err))
            c = {(p[1], int(p[2])): int(p[5]) for p in (ln.split("\t") for ln in out.splitlines())}
            if who == "ctl":
                u = est.slope([(n, c[("ctl", n)]) for n in plan.LENGTHS])
            else:
                for arm, dst in ((plan.UNIT_KEY, x), (plan.UNIT_KEY + "#b", xb)):
                    a = est.slope([(n, c[(arm, n)]) for n in plan.LENGTHS])
                    dst.append(est.rhafz(a * 10**6, u))
    W = est.med(x)
    xa = [est.rhafz(t * 10**6, W) for t in x]
    xba = [est.rhafz(t * 10**6, W) for t in xb]
    aa = est.med([abs(xba[i] - xa[i]) for i in range(plan.L_LAUNCHES)])
    noise = est.isqrt_rn(aa * aa + est.sp2(xa))
    G = plan.GATE_E6
    under = 2 * noise <= G             # §3.5¶2's half gate on the unit's value 10^6, compared doubled (r9 G7)
    print("screen: unit x_l %s, twin %s" % (xa, xba))
    print("== s2 SCREEN unit noise_e6 %d (%.3f %%) vs the half gate %d/2 (%.2f %%): %s"
          % (noise, noise / 1e4, G, G / 2e4, "UNDER" if under else "OVER: do not request the window"))
    return 0 if under else 3


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "dry" and len(sys.argv) == 5:
        sys.exit(0 if dry(sys.argv[2], sys.argv[3], sys.argv[4]) else 1)
    if cmd == "run" and len(sys.argv) == 5:
        sys.exit(run(sys.argv[2], sys.argv[3], sys.argv[4]))
    if cmd == "screen" and len(sys.argv) == 4:
        sys.exit(screen(sys.argv[2], sys.argv[3]))
    raise SystemExit("usage: run.py dry JOB RUNDIR RUN_ID | run JOB RUNDIR RUN_ID | screen RUNDIR RUN_ID")
