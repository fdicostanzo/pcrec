# span_cards/slot/record.py — THE RUN RECORD's one writer (span_cards.md §3.5 "The run record", rev 1.3
# READY-2): the window's working copy RUNDIR/run_record.tsv, written in two steps.
#   record.py j1 RUNDIR RUN_ID CODE_COMMIT       J1's END: `run` (set, run_id, code_commit, j1_verdict,
#                                                j1_widths) + `j1_cells` from RUNDIR/j1_cells.tsv (j1_rule.py)
#   record.py ready-j2p RUNDIR                   J2p's --ready: 75 no verdict yet, 77 under (b), 0 under (a)/(c)
#   record.py finalize RUNDIR STATES             the window's last step (job J9): `jobs` from STATES (lines
#                                                `job TAB state`, the queue's end states: green, failed,
#                                                wait-timeout, never), `plan` and `floor` (plan.py), and
#                                                `transcript_sha256` (RUNDIR/transcript.tsv); a job whose state
#                                                is not green is `never-ran` with its cause
# table_contract.md's section shape: `#section NAME`, a `#`-header line, TAB fields. Sections in this order:
# run, jobs, plan, floor, j1_cells.
import hashlib, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plan  # noqa: E402

SECTIONS = [("run", ["key", "value"]), ("jobs", ["job", "state", "cause"]), ("plan", ["key", "group", "job"]),
            ("floor", ["clause", "key", "when"]),
            ("j1_cells", ["cell", "pattern", "subject", "regime", "width", "launch", "ns_e6"])]
JOBS = ("J1", "J2", "J2p", "J3", "J4", "J5")

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

def setrun(rec, k, v):
    rec["run"] = [r for r in rec["run"] if r[0] != k] + [[k, v]]

def main():
    cmd, rundir = sys.argv[1], sys.argv[2]
    path = os.path.join(rundir, "run_record.tsv")
    rec = read(path)
    if cmd == "j1":
        out = subprocess.run([sys.executable, "-I", os.path.join(HERE, "j1_rule.py"),
                              os.path.join(rundir, "j1_cells.tsv")], capture_output=True, text=True, check=True).stdout
        kv = dict(ln.split("\t", 1) for ln in out.splitlines()[:2])
        for k, v in (("set", "zen4-grid3@1"), ("run_id", sys.argv[3]), ("code_commit", sys.argv[4]),
                     ("j1_verdict", kv["j1_verdict"]), ("j1_widths", kv["j1_widths"])):
            setrun(rec, k, v)
        rec["j1_cells"] = [ln.rstrip("\n").split("\t") for ln in open(os.path.join(rundir, "j1_cells.tsv"))
                           if ln.strip() and not ln.startswith("#")]
        write(path, rec)
        print("== s2 J1 VERDICT %s widths %s (record %s)" % (kv["j1_verdict"], kv["j1_widths"], path))
        return 0
    if cmd == "ready-j2p":
        v = [r[1] for r in rec["run"] if r[0] == "j1_verdict"]
        if not v:
            print("J1's verdict is not in %s yet" % path)
            return 75
        if v[0] == "b":
            print("J1 (b): a PAIR width beats 128; J2p never runs in this window (§3.6)")
            return 77
        return 0
    if cmd == "finalize":
        st = dict(ln.rstrip("\n").split("\t")[:2] for ln in open(sys.argv[3]) if ln.strip() and not ln.startswith("#"))
        jobs = []
        for j in JOBS:
            s = st.get(j, "never")
            if s == "green":
                jobs.append([j, "ran", "-"])
            else:
                cause = {"never": "declined-j1b" if j == "J2p" else "failed", "wait-timeout": "wait-timeout"}.get(s, "failed")
                jobs.append([j, "never-ran", cause])
        rec["jobs"] = jobs
        _jobs, rows, floor, _un = plan.build()
        rec["plan"] = [[k, g, j] for k, g, j, _e, _b in rows]
        rec["floor"] = [list(f) for f in floor]
        tp = os.path.join(rundir, "transcript.tsv")
        setrun(rec, "transcript_sha256", hashlib.sha256(open(tp, "rb").read()).hexdigest() if os.path.exists(tp) else "-")
        write(path, rec)
        print("== s2 FINALIZE %s: %d jobs (%d ran), %d plan keys, %d floor lines"
              % (path, len(jobs), sum(1 for r in jobs if r[1] == "ran"), len(rec["plan"]), len(rec["floor"])))
        return 0
    raise SystemExit("record.py: unknown command %s" % cmd)

if __name__ == "__main__":
    sys.exit(main())
