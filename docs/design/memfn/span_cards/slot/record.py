# span_cards/slot/record.py — THE RUN RECORD's one writer (span_cards.md §3.5 "The run record", rev 1.3
# READY-2, [rev1.3 r9-G6]): the window's working copy RUNDIR/run_record.tsv.
#   record.py window RUNDIR RUN_ID CODE_COMMIT   THE WINDOW FACTS (`set`, `rules`, `run_id`, `code_commit`, `box`,
#                                                `isa`, `libc`, `gcc`), idempotent: written at every job's start (run.py
#                                                run) and at finalize, so a run whose J1 failed still names its
#                                                run; a record naming another run id or commit REFUSES
#   record.py j1 RUNDIR RUN_ID CODE_COMMIT       J1's END: the window facts, `j1_verdict`, `j1_widths` and
#                                                `j1_cells` from RUNDIR/j1_cells.tsv (j1_rule.py)
#   record.py ready-j2p RUNDIR                   J2p's --ready after J1 ended green: 75 no verdict yet, 77 under
#                                                (b), 0 under (a)/(c) (J1 ended non-green: the job script's 77)
#   record.py finalize RUNDIR RUN_ID CODE_COMMIT STATES
#                                                the window's last step (job J9): the window facts, `jobs` from
#                                                STATES (lines `job TAB state`, boxqueue's end states) by the
#                                                CAUSE table below, `plan` and `floor` from the DRY RUN's frozen
#                                                plan RUNDIR/plan.tsv (never a live rebuild, r9 G3), and
#                                                `transcript_sha256` (RUNDIR/transcript.tsv)
# table_contract.md's section shape: `#section NAME`, a `#`-header line, TAB fields. Sections in this order:
# run, jobs, plan, floor, j1_cells. Exit 2 on a refused input.
import hashlib, os, platform, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plan  # noqa: E402

SECTIONS = [("run", ["key", "value"]), ("jobs", ["job", "state", "cause"]), ("plan", ["key", "group", "job"]),
            ("floor", ["clause", "key", "when"]),
            ("j1_cells", ["cell", "pattern", "subject", "regime", "width", "launch", "ns_e6"])]
JOBS = ("J1", "J2", "J2p", "J3", "J4", "J5")
SET = "zen4-grid3@1"
RULES = "kit-grid@" + plan.METHOD_VER     # the owner of the producer's rules (measures.md §3.5¶8a): span_cards

# THE CAUSE TABLE (first match; r9 G6): a job's queue end state (boxqueue's `state`, J9's `wait-timeout` read
# from the transcript, `none` for a job never queued) -> its record state and cause. A state no line names
# REFUSES (never a silent `failed`).
CAUSE = (
    ("green",        lambda j, v: True,                ("ran", "-")),
    ("failed",       lambda j, v: True,                ("never-ran", "failed")),
    ("wait-timeout", lambda j, v: True,                ("never-ran", "wait-timeout")),
    ("cancelled",    lambda j, v: j == "J2p" and v == "b", ("never-ran", "declined-j1b")),
    ("cancelled",    lambda j, v: True,                ("never-ran", "cancelled")),
    ("none",         lambda j, v: True,                ("never-ran", "never-queued")),
)


def refuse(msg):
    print("record: REFUSED: " + msg)
    sys.exit(2)


def read(path):
    rec = {name: [] for name, _ in SECTIONS}
    if not os.path.exists(path):
        return rec
    sec = None
    for ln in open(path):
        ln = ln.rstrip("\n")
        if ln.startswith("#section "):
            sec = ln.split()[1]
        elif ln and not ln.startswith("#") and sec in rec:
            rec[sec].append(ln.split("\t"))
    return rec


def write(path, rec):
    t = ["# span_cards stage-2 run record (span_cards.md §3.5; the kit's, outside the set)"]
    for name, cols in SECTIONS:
        t += ["#section " + name, "#" + "\t".join(cols)] + ["\t".join(r) for r in rec[name]]
    tmp = path + ".tmp"
    open(tmp, "w").write("\n".join(t) + "\n")
    os.replace(tmp, path)


def getrun(rec, k):
    v = [r[1] for r in rec["run"] if r[0] == k]
    return v[0] if v else None


def setrun(rec, k, v):
    rec["run"] = [r for r in rec["run"] if r[0] != k] + [[k, v]]


def box_facts():
    """the box, its ISA features (cpuid's flags the kit's arms and gcc's levels read), libc and gcc"""
    cpu = {}
    for ln in open("/proc/cpuinfo"):
        k, _, v = ln.partition(":")
        cpu.setdefault(k.strip(), v.strip())
        if not ln.strip():
            break
    fl = set(cpu.get("flags", "").split())
    lvl = ("x86-64-v4" if {"avx512f", "avx512bw", "avx512cd", "avx512dq", "avx512vl"} <= fl else
           "x86-64-v3" if {"avx2", "bmi1", "bmi2", "fma", "movbe"} <= fl else
           "x86-64-v2" if {"sse4_2", "popcnt", "ssse3"} <= fl else "x86-64")
    isa = " ".join([lvl] + [f.replace("sse4_2", "sse4.2") for f in ("avx512f", "avx2", "sse4_2", "popcnt", "bmi2")
                            if f in fl])
    lib, ver = platform.libc_ver()
    r = subprocess.run(["gcc", "-dumpfullversion"], capture_output=True, text=True)
    if r.returncode or not r.stdout.strip():
        refuse("gcc -dumpfullversion: rc %d" % r.returncode)
    return (("box", "%s, CPU %s" % (cpu.get("model name", "?"), plan.TIMING_CPU)), ("isa", isa),
            ("libc", "%s %s" % (lib, ver) if lib else "-"), ("gcc", r.stdout.strip()))


def window(rec, run_id, commit):
    """the window facts, idempotent; another run's record or an empty commit REFUSES"""
    if not run_id or not re.fullmatch(r"[0-9a-f]{7,40}", commit or ""):
        refuse("run id %r / code commit %r: both required (a commit is a hex object name)" % (run_id, commit))
    for k, v in (("run_id", run_id), ("code_commit", commit)):
        if getrun(rec, k) not in (None, v):
            refuse("the record names %s %s, this step %s" % (k, getrun(rec, k), v))
    setrun(rec, "set", SET)
    setrun(rec, "rules", RULES)
    setrun(rec, "run_id", run_id)
    setrun(rec, "code_commit", commit)
    for k, v in box_facts():
        if getrun(rec, k) not in (None, v):
            refuse("the record's %s is %r, this box's %r: one window, one box" % (k, getrun(rec, k), v))
        setrun(rec, k, v)


def main():
    cmd, rundir = sys.argv[1], sys.argv[2]
    path = os.path.join(rundir, "run_record.tsv")
    rec = read(path)
    if cmd == "window":
        window(rec, sys.argv[3], sys.argv[4])
        write(path, rec)
        return 0
    if cmd == "j1":
        window(rec, sys.argv[3], sys.argv[4])
        r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "j1_rule.py"),
                            os.path.join(rundir, "j1_cells.tsv")], capture_output=True, text=True)
        if r.returncode:
            refuse("j1_rule.py rc %d: %s" % (r.returncode, r.stderr[-300:]))
        kv = dict(ln.split("\t", 1) for ln in r.stdout.splitlines()[:2])
        setrun(rec, "j1_verdict", kv["j1_verdict"])
        setrun(rec, "j1_widths", kv["j1_widths"])
        rec["j1_cells"] = [ln.rstrip("\n").split("\t") for ln in open(os.path.join(rundir, "j1_cells.tsv"))
                           if ln.strip() and not ln.startswith("#")]
        write(path, rec)
        print("== s2 J1 VERDICT %s widths %s (record %s)" % (kv["j1_verdict"], kv["j1_widths"], path))
        return 0
    if cmd == "ready-j2p":
        v = getrun(rec, "j1_verdict")
        if v is None:
            print("J1's verdict is not in %s yet" % path)
            return 75
        if v == "b":
            print("J1 (b): a PAIR width beats 128; J2p never runs in this window (§3.6)")
            return 77
        return 0
    if cmd == "finalize":
        window(rec, sys.argv[3], sys.argv[4])
        st = {}
        for ln in open(sys.argv[5]):
            if ln.strip() and not ln.startswith("#"):
                f = ln.rstrip("\n").split("\t")
                st[f[0]] = f[1]
        if sorted(st) != sorted(JOBS):
            refuse("STATES names %s, the window's jobs are %s" % (sorted(st), sorted(JOBS)))
        v = getrun(rec, "j1_verdict")
        jobs = []
        for j in JOBS:
            hit = next((c for s, test, c in CAUSE if s == st[j] and test(j, v)), None)
            if not hit:
                refuse("job %s's state %r is in no CAUSE line" % (j, st[j]))
            jobs.append([j, hit[0], hit[1]])
        fp = os.path.join(rundir, "plan.tsv")
        if not os.path.exists(fp):
            refuse("%s is absent: finalize writes the DRY RUN's frozen plan, never a live one" % fp)
        fr = plan.read_frozen(fp)
        rec["jobs"] = jobs
        rec["plan"] = [r[:3] for r in fr["rows"]]
        rec["floor"] = fr["floor"]
        tp = os.path.join(rundir, "transcript.tsv")
        setrun(rec, "transcript_sha256", hashlib.sha256(open(tp, "rb").read()).hexdigest() if os.path.exists(tp) else "-")
        write(path, rec)
        print("== s2 FINALIZE %s: %d jobs (%d ran), %d plan keys, %d floor lines"
              % (path, len(jobs), sum(1 for r in jobs if r[1] == "ran"), len(rec["plan"]), len(rec["floor"])))
        return 0
    raise SystemExit("record.py: window | j1 | ready-j2p | finalize")


if __name__ == "__main__":
    sys.exit(main())
