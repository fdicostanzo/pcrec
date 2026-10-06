"""timing.py -- [ARTREV] interleaved-round timing of arms (u3twin's shape).

`time` is the gated front end (bounds, identity-passed, locks, load gate,
watchdog, ledger, optional ubuntubudu); `_rawtime` is the engine that builds
every arm with the ONE fixed command line and runs the rounds (it is what
ships to the Linux box).  Verdict rule (charter 4 S4): an arm WINS if its
median beats the original's by more than BOTH the null twin's deviation from
the original AND the arms' IQR; LOSS by the same rule; else NOISE.

LAYOUT CONTROL (charter S4, the method of docs/dev/optloop/k87twin_align.sh): `time --pads
16,32,48,64 --pad-arms orig,L1,...` also builds each named arm at those code-offset pads (arm
`X@pK` = X's artifact.c with a file-scope `.skip K` ahead of everything, so every function in the
TU moves by K bytes) and times them in the SAME interleaved rounds.  A lead is then a WIN only
if its pad-median beats the original's pad-median by more than max(null deviation, both IQRs,
BOTH arms' spread across pads) AND every paired pad (orig@pK vs X@pK) agrees in sign; a
LOSS the mirror; else NOISE.  Without --pads the plain rule above applies and the verdict says
so ("no pad control": a confirmer must not report such a verdict).
"""
import os
import platform
import re
import shlex
import shutil
import statistics
import subprocess
import sys
import time

import common as C

HERE = C.HERE
REMOTE_HOST = "duxevents@100.69.121.107"
REMOTE_DIR = "scratch_lx/artrev"          # under the remote $HOME
REMOTE_WINDOW = (8, 19)
STD = ("orig", "orig2", "null")
PAD_RE = re.compile(r"^(.+)@p(\d+)$")


def pad_text(k):
    return '__asm__(".text\\n.skip %d,0x90\\n"); /* [ARTREV] layout control: code-offset pad %d bytes */\n' % (k, k)


def make_pad_arms(name, base_arms, pads):
    """Create arms/<base>@p<K> (the base arm's artifact.c behind a K-byte code pad); returns the names."""
    out = []
    for b in base_arms:
        src = os.path.join(C.art_dir(name), "arms", b)
        if not os.path.exists(os.path.join(src, "artifact.c")):
            C.die("--pad-arms: no arm %r" % b)
        text = open(os.path.join(src, "artifact.c")).read()
        for k in pads:
            d = os.path.join(C.art_dir(name), "arms", "%s@p%d" % (b, k))
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, "artifact.c"), "w").write(pad_text(k) + text)
            shutil.copy(os.path.join(src, "artifact.h"), os.path.join(d, "artifact.h"))
            out.append("%s@p%d" % (b, k))
    return out


def apply_layout(summ, arms):
    """Fold the pad variants into the verdict (see the module docstring).  Mutates summ."""
    pads = {}
    for a in arms:
        m = PAD_RE.match(a)
        if m:
            pads.setdefault(m.group(1), []).append(a)
    if "orig" not in pads:
        return False
    for s, per in summ.items():
        def meds(base):
            return [per[v]["med"] for v in [base] + pads.get(base, []) if v in per]
        o_meds = meds("orig")
        o_spread, o_pm = max(o_meds) - min(o_meds), statistics.median(o_meds)
        per["orig"]["layout"] = {"pad_med": o_pm, "spread": o_spread, "paired": []}
        for base, d in list(per.items()):
            if base.startswith("_") or PAD_RE.match(base) or base == "orig":
                continue
            if base not in pads:
                d["layout_note"] = "no pad control"
                continue
            ms = meds(base)
            spread, pm = max(ms) - min(ms), statistics.median(ms)
            paired = []
            for v in pads[base]:
                ov = "orig@p" + PAD_RE.match(v).group(2)
                if ov in per and v in per:
                    paired.append(per[ov]["med"] - per[v]["med"])
            nd = per["_null_dev"]
            thr = max(nd, d["iqr"], per["orig"]["iqr"], spread, o_spread)
            delta = o_pm - pm
            d["layout"] = {"pad_med": pm, "spread": spread, "paired": paired, "delta": delta, "thr": thr}
            plain = d["verdict"]
            if delta > thr and d["delta"] > 0 and all(x > 0 for x in paired):
                d["verdict"] = "WIN"
            elif -delta > thr and d["delta"] < 0 and all(x < 0 for x in paired):
                d["verdict"] = "LOSS"
            else:
                d["verdict"] = "NOISE"
            if plain != d["verdict"]:
                d["layout_note"] = "plain rule said %s; the pad control downgrades it" % plain
    return True


def selftest_only(flag):
    if os.environ.get("ARTREV_SELFTEST") != "1":
        C.die("%s is refused outside the selftest (ARTREV_SELFTEST=1 is set only by selftest.sh)" % flag, 5)
    sys.stderr.write("!!!!! ARTREV: %s IN EFFECT -- SELFTEST ONLY, nothing from this run is a measurement !!!!!\n" % flag)


# ------------------------------------------------------------------ summary
def quartiles(xs):
    if len(xs) < 2:
        return xs[0], xs[0]
    q = statistics.quantiles(xs, n=4, method="inclusive")
    return q[0], q[2]


def read_raw(path):
    rows, hdr = [], []
    with open(path) as f:
        for ln in f:
            if ln.startswith("#"):
                hdr.append(ln.rstrip("\n"))
            elif ln.startswith("subject\t"):
                continue
            elif ln.strip():
                t = ln.rstrip("\n").split("\t")
                rows.append({"subject": t[0], "arm": t[1], "round": int(t[2]), "ns": float(t[3]),
                             "matches": t[4], "checksum": t[5], "load": t[6], "reps": t[7]})
    return hdr, rows


def add_cell_rows(rows, labels):
    """Append the pseudo-subject CELL: per (arm, round) the median over the cell's subjects (the bench's
    cell number is the median over its subjects, so the subject that sets the median sets the verdict)."""
    by = {}
    for r in rows:
        if r["subject"] in labels:
            by.setdefault((r["arm"], r["round"]), []).append(r["ns"])
    out = [{"subject": "CELL", "arm": arm, "round": rnd, "ns": statistics.median(xs), "matches": "-",
            "checksum": "-", "load": "-", "reps": "-"} for (arm, rnd), xs in sorted(by.items()) if len(xs) == len(labels)]
    return rows + out


def summarize(rows, arms):
    """-> {subject: {arm: dict(med,q1,q3,iqr,delta,thr,verdict)}, '_null_dev': ...}"""
    out = {}
    subjects = []
    for r in rows:
        if r["subject"] not in subjects:
            subjects.append(r["subject"])
    for s in subjects:
        per = {}
        for a in arms:
            xs = [r["ns"] for r in rows if r["subject"] == s and r["arm"] == a]
            if not xs:
                continue
            q1, q3 = quartiles(xs)
            per[a] = {"med": statistics.median(xs), "q1": q1, "q3": q3, "iqr": q3 - q1, "n": len(xs)}
        o = per["orig"]
        nd = abs(per["null"]["med"] - o["med"]) if "null" in per else float("nan")
        for a, d in per.items():
            d["delta"] = o["med"] - d["med"]                    # >0: faster than the original
            d["thr"] = max(nd, d["iqr"], o["iqr"])
            if a == "orig":
                d["verdict"] = "BASE"
            elif d["delta"] > d["thr"]:
                d["verdict"] = "WIN"
            elif -d["delta"] > d["thr"]:
                d["verdict"] = "LOSS"
            else:
                d["verdict"] = "NOISE"
        per["_null_dev"] = nd
        out[s] = per
    return out


def write_summary(path_tsv, path_txt, summ, hdr, arms):
    with open(path_tsv, "w") as f:
        f.write("subject\tarm\tn\tmedian_ns_per_byte\tq1\tq3\tiqr\tdelta_vs_orig\tthreshold\tnull_dev\tverdict\n")
        for s, per in summ.items():
            for a in arms:
                if a in per and not PAD_RE.match(a):
                    d = per[a]
                    f.write("%s\t%s\t%d\t%.4f\t%.4f\t%.4f\t%.4f\t%+.4f\t%.4f\t%.4f\t%s\n" % (
                        s, a, d["n"], d["med"], d["q1"], d["q3"], d["iqr"], d["delta"], d["thr"], per["_null_dev"], d["verdict"]))
    lines = list(hdr)
    for s, per in summ.items():
        lines.append("")
        lines.append("subject %s   null-twin deviation %.4f ns/B   (rule: WIN/LOSS only past max(null dev, IQR_arm, IQR_orig))" % (s, per["_null_dev"]))
        for a in arms:
            if a in per and not PAD_RE.match(a):
                d = per[a]
                lines.append("  %-14s median %9.4f  IQR %7.4f  vs orig %+8.4f (%+6.2f%%)  threshold %7.4f  %s" % (
                    a, d["med"], d["iqr"], d["delta"], 100.0 * d["delta"] / per["orig"]["med"], d["thr"], d["verdict"]))
                if "layout" in d and "thr" in d["layout"]:
                    L = d["layout"]
                    lines.append("      layout: pad-median %.4f  spread across pads %.4f (orig %.4f)  pad-median delta %+.4f vs threshold %.4f  paired deltas %s%s" % (
                        L["pad_med"], L["spread"], per["orig"]["layout"]["spread"], L["delta"], L["thr"],
                        " ".join("%+.4f" % x for x in L["paired"]), ("  [" + d["layout_note"] + "]") if d.get("layout_note") else ""))
                elif d.get("layout_note") == "no pad control":
                    lines.append("      layout: no pad control for this arm (a verdict without it is not reportable)")
    open(path_txt, "w").write("\n".join(lines) + "\n")
    return "\n".join(lines)


# ---------------------------------------------------------------- the engine
def wait_quiet(load_max, max_wait, override):
    if override:
        return loadavg_safe()
    t0 = time.time()
    while True:
        l = C.loadavg1()
        if l <= load_max:
            return l
        if time.time() - t0 > max_wait:
            sys.stderr.write("REFUSED: load1 stayed above %.2f for %ds (last %.2f)\n" % (load_max, max_wait, l))
            sys.exit(7)
        time.sleep(3)


def loadavg_safe():
    return C.loadavg1()


def cmd_rawtime(a):
    if a.root:
        os.environ["ARTREV_ROOT"] = a.root
    if a.gate_override:
        selftest_only("--gate-override")
    meta = C.load_meta(a.name)
    C.check_cc_is_gcc(os.environ.get("ARTREV_REMOTE_CC") or os.environ.get("ARTREV_CC") or meta["cc"])
    arms = a.arms.split(",")
    exes = {}
    for arm in arms:                               # ALL arms built before ANY timing
        d = os.path.join(C.art_dir(a.name), "arms", arm)
        exes[arm] = C.compile_arm(meta, d, "bench")
    subjects = [s.split("=", 1) for s in a.subject]
    try:
        cpu = [l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")][0]
    except Exception:
        cpu = platform.processor() or platform.machine()
    ccv = C.cc_version(os.environ.get("ARTREV_REMOTE_CC") or meta["cc"])
    with open(a.out, "w") as f:
        f.write("#host\t%s\t%s\n#cpu\t%s\n#cc\t%s\t%s\n#date\t%s\n#rounds\t%d\t#load_max\t%.2f%s\n#artifact\t%s pin %s abi %s\n" % (
            platform.node(), platform.platform(), cpu, ccv, " ".join(C.BASE_FLAGS), time.strftime("%Y-%m-%d %H:%M:%S"),
            a.rounds, a.load_max, "\t#GATE-OVERRIDE-SELFTEST" if a.gate_override else "", a.name, meta["pin"][:12], meta["abi"]))
        f.write("subject\tarm\tround\tns_per_byte\tmatches\tchecksum\tload1_before\treps\n")
        for label, path in subjects:
            # reference answer + calibration, all arms
            ref = None
            for arm in arms:
                r = subprocess.run([exes[arm], path, "1"], capture_output=True, text=True)
                if r.returncode:
                    sys.stderr.write("bench %s/%s failed rc=%d: %s\n" % (arm, label, r.returncode, r.stderr[-300:]))
                    return 6
                t = r.stdout.strip().split("\t")[1:3]
                if ref is None:
                    ref = t
                elif t != ref:
                    sys.stderr.write("ANSWER MISMATCH on %s: arm %s (matches,checksum)=%s vs orig %s\n" % (label, arm, t, ref))
                    return 3
            cal = []
            for _ in range(3):
                r = subprocess.run([exes["orig"], path, "0"], capture_output=True, text=True)
                cal.append(float(r.stdout.split("\t")[1]))
            m = sorted(cal)[1]
            reps = max(1, min(400, int(0.08 / (m if m > 1e-6 else 1e-6))))
            for rnd in range(a.rounds):
                for k in range(len(arms)):
                    arm = arms[(k + rnd) % len(arms)]
                    load = wait_quiet(a.load_max, a.max_load_wait, a.gate_override)
                    r = subprocess.run([exes[arm], path, str(reps)], capture_output=True, text=True)
                    if r.returncode:
                        sys.stderr.write("bench %s/%s failed rc=%d\n" % (arm, label, r.returncode))
                        return 6
                    ns, cnt, ck = r.stdout.strip().split("\t")
                    if [cnt, ck] != ref:
                        sys.stderr.write("ANSWER DRIFT in arm %s round %d on %s\n" % (arm, rnd, label))
                        return 3
                    f.write("%s\t%s\t%d\t%s\t%s\t%s\t%.2f\t%d\n" % (label, arm, rnd, ns, cnt, ck, load, reps))
                    f.flush()
            print("%s done (reps %d)" % (label, reps), flush=True)
    return 0


# ------------------------------------------------------------- the front end
def lock_exists(p):
    return os.path.exists(p) or os.path.isdir(p)


def pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def take_timing_lock():
    lk = C.timing_lock_path()
    os.makedirs(os.path.dirname(lk), exist_ok=True)
    for _ in range(2):
        try:
            os.mkdir(lk)
            open(os.path.join(lk, "pid"), "w").write(str(os.getpid()))
            return lk
        except FileExistsError:
            try:
                pid = int(open(os.path.join(lk, "pid")).read())
            except Exception:
                pid = 0
            if pid and pid_alive(pid):
                C.die("another timing run holds %s (pid %d); two reviewers never time at once" % (lk, pid), 5)
            sys.stderr.write("stale timing lock (pid %s dead): removing %s\n" % (pid, lk))
            shutil.rmtree(lk, ignore_errors=True)
    C.die("cannot take %s" % lk, 5)


def release_timing_lock(lk):
    shutil.rmtree(lk, ignore_errors=True)


def next_run_dir(name, tag):
    base = os.path.join(C.art_dir(name), "timing")
    os.makedirs(base, exist_ok=True)
    n = len([x for x in os.listdir(base) if x[:3].isdigit()]) + 1
    d = os.path.join(base, "%03d%s" % (n, ("_" + tag) if tag else ""))
    os.makedirs(d)
    return d


def preflight(a, arms):
    meta = C.load_meta(a.name)
    base = C.art_dir(a.name)
    rows = C.ledger_rows(a.name)
    if arms[0] != "orig":
        C.die("the original must be the first arm")
    if "null" not in arms:
        C.die("the null twin rides EVERY timing run (charter 4 S1-S3): add `null` to --arms "
              "(create it with `artrev.py twin %s null --null`)" % a.name)
    revs = {}
    for arm in arms:
        d = os.path.join(base, "arms", arm)
        if not os.path.exists(os.path.join(d, "artifact.c")):
            C.die("arm %r does not exist under %s" % (arm, base))
        if arm in ("orig", "orig2") or PAD_RE.match(arm):
            continue
        rev = int(open(os.path.join(d, "rev")).read()) if os.path.exists(os.path.join(d, "rev")) else 0
        revs[arm] = rev
        sha = C.sha256_file(os.path.join(d, "artifact.c"))
        trows = [r for r in rows if r["kind"] == "twin" and r["arm"] == arm and r["status"] in ("APPLIED", "SEALED")]
        if not trows or trows[-1]["sha"] != sha:
            C.die("arm %s: artifact.c does not match its last logged twin revision (an unlogged edit?).  "
                  "Re-seal it with `twin %s %s --seal` so the revision is counted." % (arm, a.name, arm), 3)
        ok = [r for r in rows if r["kind"] == "identity" and r["arm"] == arm and r["sha"] == sha and r["status"] == "PASS"]
        if not ok:
            C.die("arm %s (rev %d): no PASSING identity run for this exact revision in the ledger; run "
                  "`artrev.py identity %s %s` first (zero differences is the bar before any timing)" % (arm, rev, a.name, arm), 3)
        if C.is_counted_arm(arm) and C.timings_of(rows, arm, rev) >= C.MAX_TIMINGS:
            C.die("BOUND: lead %s rev %d already has %d timing runs; the charter allows at most %d per revision.  "
                  "Refused." % (arm, rev, C.timings_of(rows, arm, rev), C.MAX_TIMINGS), 3)
    return meta, rows, revs


def cmd_time(a):
    arms = [x for x in a.arms.split(",") if x]
    if "orig" not in arms:
        arms = ["orig"] + arms
    elif arms[0] != "orig":
        arms.remove("orig")
        arms = ["orig"] + arms
    if "orig2" not in arms and os.path.exists(os.path.join(C.art_dir(a.name), "arms", "orig2")):
        arms.insert(1, "orig2")
    if not a.subject:
        C.die("at least one --subject LABEL=FILE (the cell's own subject first; dense/sparse variants after)")
    for s in a.subject:
        if "=" not in s or not os.path.exists(s.split("=", 1)[1]):
            C.die("bad --subject %r (LABEL=FILE, file must exist)" % s)
    pad_list = []
    if a.pads:
        pad_list = [int(x) for x in a.pads.split(",") if x]
        if len(pad_list) < 4 or any(k <= 0 or k % 16 for k in pad_list):
            C.die("--pads: at least 4 positive multiples of 16 (charter S4; k87twin_align.sh used 16..112), got %r" % a.pads)
        pad_base = [x for x in (a.pad_arms or "orig").split(",") if x]
        if "orig" not in pad_base:
            pad_base = ["orig"] + pad_base
        arms = arms + make_pad_arms(a.name, pad_base, pad_list)
    elif a.pad_arms:
        C.die("--pad-arms needs --pads")
    meta, rows, revs = preflight(a, arms)
    gate = a.load_max if a.load_max is not None else C.default_load_gate()
    overrides = []
    if a.gate_override:
        selftest_only("--gate-override")
        overrides.append("GATE-OVERRIDE")
    # --- locks and gates (refuse, never caveat)
    lockp = C.mac_suite_lock_path()
    if C.lock_exists_path(lockp) and not a.remote:
        C.die("REFUSED: %s exists (a Mac suite is running; two heavy things at once spoil both).  "
              "Wait for it to clear." % lockp, 5)
    if a.remote:
        if a.remote != "ubuntubudu":
            C.die("--remote takes `ubuntubudu` (the only timing box; host is fixed to %s)" % REMOTE_HOST)
        hour = a.hour_override if a.hour_override is not None else time.localtime().tm_hour
        if a.hour_override is not None:
            selftest_only("--hour-override")
            overrides.append("HOUR-OVERRIDE")
        if not (REMOTE_WINDOW[0] <= hour < REMOTE_WINDOW[1]):
            C.die("REFUSED: ubuntubudu is by-day-only (%02d:00-%02d:00 local; the bench owns the night); it is %02d:xx now." % (
                REMOTE_WINDOW[0], REMOTE_WINDOW[1], hour), 5)
    plan = remote_plan(a, arms, meta, gate) if a.remote else None
    if a.remote and a.dry_run:
        print("DRY RUN (nothing executed, nothing logged); local checks passed:")
        for c in plan["cmds"]:
            print("  $ " + c)
        return 0
    lk = take_timing_lock()
    rdir = next_run_dir(a.name, a.tag)
    rawp = os.path.join(rdir, "raw.tsv")
    status, rc = "FAIL", 1
    try:
        if a.remote:
            rc = run_remote(a, plan, rdir, rawp, arms)
        else:
            cmd = [os.path.join(C.tree_root(), "scripts", "watchdog"), "-s", str(a.wall), "-m", "%dk" % a.rss_kb,
                   "-S", "artrev-time", "-l", a.name, "-L", os.path.join(rdir, "watchdog.log"), "--", sys.executable, os.path.join(HERE, "artrev.py"), "_rawtime",
                   a.name, "--arms", ",".join(arms), "--rounds", str(a.rounds), "--load-max", str(gate),
                   "--max-load-wait", str(a.max_load_wait), "--out", rawp] + \
                  (["--gate-override"] if a.gate_override else []) + sum([["--subject", s] for s in a.subject], [])
            rc = subprocess.run(cmd).returncode
        if rc == 7:        # the load gate refused before any unit ran: not an attempt, not logged
            print("REFUSED by the load gate before timing started (nothing logged, nothing counted)")
            shutil.rmtree(rdir, ignore_errors=True)
            return 7
        if rc == 0:
            hdr, rrows = read_raw(rawp)
            if a.cell:
                labs = [x for x in a.cell.split(",") if x]
                have = {r["subject"] for r in rrows}
                if any(l not in have for l in labs):
                    C.die("--cell names a subject label that was not timed: %s" % [l for l in labs if l not in have])
                rrows = add_cell_rows(rrows, labs)
            summ = summarize(rrows, arms)
            if pad_list:
                apply_layout(summ, arms)
            txt = write_summary(os.path.join(rdir, "summary.tsv"), os.path.join(rdir, "summary.txt"), summ, hdr, arms)
            print(txt)
            status = "OK"
            first = list(summ.keys())[0]
            for arm in arms:
                if PAD_RE.match(arm):
                    continue
                v = " ".join("%s:%s" % (s, summ[s][arm]["verdict"]) for s in summ if arm in summ[s])
                if pad_list:
                    v += " layout=pads(%s)" % a.pads
                C.ledger_append(a.name, "time", arm, revs.get(arm, 0), C.is_counted_arm(arm), "OK",
                                C.sha256_file(os.path.join(C.art_dir(a.name), "arms", arm, "artifact.c")),
                                "run=%s rounds=%d %s %s %s" % (os.path.basename(rdir), a.rounds, "remote" if a.remote else "local",
                                                              v, ",".join(overrides)))
            print("\nrun dir:", rdir)
        else:
            for arm in arms:
                if arm not in ("orig", "orig2") and not PAD_RE.match(arm):
                    C.ledger_append(a.name, "time", arm, revs.get(arm, 0), C.is_counted_arm(arm), "FAILED(rc=%d)" % rc, "",
                                    "run=%s %s" % (os.path.basename(rdir), ",".join(overrides)))
            sys.stderr.write("timing run FAILED rc=%d (logged as an attempt; it still counts toward the bound)\n" % rc)
    finally:
        release_timing_lock(lk)
    return 0 if status == "OK" else (rc or 1)


# ------------------------------------------------------------------- remote
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15"]


def remote_plan(a, arms, meta, gate):
    stage = os.path.join(C.art_root(), "_bundle_%s" % a.name)
    bundle = stage + ".tgz"
    rrun = "%s/run_%s_%d" % (REMOTE_DIR, a.name, int(time.time()))
    rlock = "%s/.timing.lock" % REMOTE_DIR
    subj_args = []
    for s in a.subject:
        lab, p = s.split("=", 1)
        subj_args.append("--subject %s=%s" % (lab, "subjects/" + os.path.basename(p)))
    inner = ("cd ~/%s && tar xzf bundle.tgz && ARTREV_ROOT=$PWD/root ARTREV_REMOTE_CC=${ARTREV_REMOTE_CC:-gcc} "
             "gnutimeout %d scripts/watchdog -s %d -m %dk -S artrev-time -l %s -L watchdog.log -- python3 studies/artrev/artrev.py _rawtime %s "
             "--arms %s --rounds %d --load-max %s --max-load-wait %d --out raw.tsv %s" % (
                 rrun, a.wall + 60, a.wall, a.rss_kb, a.name, a.name, ",".join(arms), a.rounds, gate, a.max_load_wait,
                 " ".join(subj_args)))
    cmds = [
        "(local) bundle studies/artrev/*.{py,c,h} scripts/watchdog + %s arms {%s} + meta + subjects -> %s" % (a.name, ",".join(arms), bundle),
        " ".join(SSH) + " %s 'mkdir -p ~/%s && mkdir ~/%s || { echo REFUSED remote timing lock held; exit 5; }'" % (REMOTE_HOST, REMOTE_DIR, rlock),
        " ".join(SSH) + " %s 'mkdir -p ~/%s'" % (REMOTE_HOST, rrun),
        "scp -o BatchMode=yes %s %s:%s/bundle.tgz" % (bundle, REMOTE_HOST, rrun),
        " ".join(SSH) + " %s %s" % (REMOTE_HOST, shlex.quote(inner)),
        "scp -o BatchMode=yes %s:%s/raw.tsv <rundir>/raw.tsv" % (REMOTE_HOST, rrun),
        " ".join(SSH) + " %s 'rmdir ~/%s; rm -rf ~/%s'   # always, even after a failure" % (REMOTE_HOST, rlock, rrun),
    ]
    return {"stage": stage, "bundle": bundle, "rrun": rrun, "rlock": rlock, "inner": inner, "cmds": cmds}


def make_bundle(a, arms, plan):
    st = plan["stage"]
    shutil.rmtree(st, ignore_errors=True)
    os.makedirs(os.path.join(st, "studies", "artrev"))
    os.makedirs(os.path.join(st, "scripts"))
    for f in os.listdir(HERE):
        if f.endswith((".py", ".c", ".h")):
            shutil.copy(os.path.join(HERE, f), os.path.join(st, "studies", "artrev", f))
    shutil.copy(os.path.join(C.tree_root(), "scripts", "watchdog"), os.path.join(st, "scripts", "watchdog"))
    ad = os.path.join(st, "root", a.name)
    os.makedirs(ad)
    shutil.copy(os.path.join(C.art_dir(a.name), "meta.json"), ad)
    for arm in arms:
        dst = os.path.join(ad, "arms", arm)
        os.makedirs(dst)
        for f in ("artifact.c", "artifact.h"):
            shutil.copy(os.path.join(C.art_dir(a.name), "arms", arm, f), dst)
    os.makedirs(os.path.join(st, "subjects"))
    for s in a.subject:
        shutil.copy(s.split("=", 1)[1], os.path.join(st, "subjects"))
    env = dict(os.environ, COPYFILE_DISABLE="1")
    r = subprocess.run(["tar", "czf", plan["bundle"], "-C", st, "."], env=env, capture_output=True, text=True)
    if r.returncode:
        C.die("tar failed: " + r.stderr)


def run_remote(a, plan, rdir, rawp, arms):
    make_bundle(a, arms, plan)     # the COMPUTED arm list (orig/orig2 added, pad variants), not the raw --arms
    h = REMOTE_HOST
    r = subprocess.run(SSH + [h, "mkdir -p ~/%s && mkdir ~/%s" % (REMOTE_DIR, plan["rlock"].replace(REMOTE_DIR + "/", REMOTE_DIR + "/"))])
    if r.returncode:
        sys.stderr.write("REFUSED: the remote timing lock is held (or ssh failed)\n")
        return 5
    rc = 1
    try:
        subprocess.run(SSH + [h, "mkdir -p ~/%s" % plan["rrun"]], check=True)
        subprocess.run(["scp", "-o", "BatchMode=yes", plan["bundle"], "%s:%s/bundle.tgz" % (h, plan["rrun"])], check=True)
        rc = subprocess.run(SSH + [h, plan["inner"]]).returncode
        if rc == 0:
            rc = subprocess.run(["scp", "-o", "BatchMode=yes", "%s:%s/raw.tsv" % (h, plan["rrun"]), rawp]).returncode
    finally:
        subprocess.run(SSH + [h, "rmdir ~/%s; rm -rf ~/%s" % (plan["rlock"], plan["rrun"])])
    return rc
