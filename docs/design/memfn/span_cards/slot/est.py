# span_cards/slot/est.py — THE SLOT'S ESTIMATOR: span_cards.md §3.4-§3.5 (docs/spec/measures.md §3.4-§3.5) over
# the window's cells, the gates, the NULL rule, the bimodal test, drift, the floor and the first-match outcome
# table; and the DRAFT SET writer (§3.8 step 1). Its arithmetic is drill.py's (the same text implemented
# literally; drill.py stays the design's evidence). The recompute (S2e, tests/knowledge/) is written from the
# spec and shares nothing with this file.
#   python3 -I est.py rows   RUNDIR             the rows and verdicts, one line each, and the outcome
#   python3 -I est.py draft  RUNDIR OUT.tsv     the draft set (format 2), digest by tests/knowledge/ks_ref.py
# RUNDIR holds cells.J<j>.tsv (format 2's cell columns, one file per ran job) and run_record.tsv.
import hashlib, math, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plan  # noqa: E402

TREE = plan.TREE
K_TRIM_E6, K_MED_E6 = 1723000, 210300

def rhafz(n, d):
    s = -1 if (n < 0) != (d < 0) else 1
    n, d = abs(n), abs(d)
    return s * ((n + d // 2) // d)

def isqrt_rn(N):
    r = math.isqrt(N)
    return r + 1 if N - r * r > r else r

def med(v):
    s = sorted(v)
    return s[(len(s) - 1) // 2]

def trim(x):
    m = med(x)
    k = max(range(len(x)), key=lambda i: (abs(x[i] - m), i))
    return [x[i] for i in range(len(x)) if i != k]

def sp2(x):
    w = trim(x)
    n = len(w)
    return rhafz(K_TRIM_E6 * (n * sum(t * t for t in w) - sum(w) ** 2), 10**6 * n * (n - 1))

def slope(pts):
    n = len(pts)
    sx = sum(x for x, _ in pts); sy = sum(y for _, y in pts)
    S = n * sum(x * y for x, y in pts) - sx * sy
    D = n * sum(x * x for x, _ in pts) - sx * sx
    return rhafz(S, D)

CELL_COLS = ["cell", "group", "arm", "length", "launch", "round", "events", "ns_e6"]

def read_cells(rundir):
    cells = []
    for f in sorted(os.listdir(rundir)):
        if f.startswith("cells.J") and f.endswith(".tsv"):
            for ln in open(os.path.join(rundir, f)):
                if ln.startswith("#") or not ln.strip():
                    continue
                c = dict(zip(CELL_COLS, ln.rstrip("\n").split("\t")))
                c["length"], c["launch"], c["ns_e6"] = int(c["length"]), int(c["launch"]), int(c["ns_e6"])
                cells.append(c)
    return cells

def read_record(rundir):
    rec, sec = {"run": {}, "jobs": {}}, None
    p = os.path.join(rundir, "run_record.tsv")
    if not os.path.exists(p):
        return rec
    for ln in open(p):
        ln = ln.rstrip("\n")
        if ln.startswith("#section "):
            sec = ln.split()[1]
            continue
        if ln.startswith("#") or not ln:
            continue
        f = ln.split("\t")
        if sec == "run":
            rec["run"][f[0]] = f[1]
        elif sec == "jobs":
            rec["jobs"][f[0]] = (f[1], f[2])
    return rec

def compute(rundir):
    jobs, rows, floor, _un = plan.build()
    cells = read_cells(rundir)
    rec = read_record(rundir)
    L = plan.L_LAUNCHES
    c = {}
    for x in cells:
        c[(x["group"].split(".")[0], x["arm"], x["length"], x["launch"])] = x
    ran = {x["group"].split(".")[0] for x in cells}
    def cell(j, arm, length, l):
        return c[(j, arm, length, l)]["ns_e6"]
    u = {}
    for j in ran:
        u[j] = [slope([(x, cell(j, "ctl", x, l)) for x in plan.LENGTHS]) for l in range(1, L + 1)]
    out = {}
    W = None
    for key, group, j, est, base in rows:
        if j not in ran:
            out[key] = {"absent": "never-ran:%s" % j}
            continue
        def per_launch(arm):
            if est.startswith("slope"):
                return [slope([(x, cell(j, arm, x, l)) for x in plan.LENGTHS]) for l in range(1, L + 1)], None
            E = int(c[(j, arm, plan.LEN, 1)]["events"])
            D = [cell(j, arm, plan.LEN, l) - cell(j, base, plan.LEN, l) for l in range(1, L + 1)]
            return [rhafz(d, E) for d in D], D
        a, D = per_launch(key)
        ab, Db = per_launch(key + "#b")
        v = [rhafz(a[i] * 10**6, u[j][i]) for i in range(L)]
        vb = [rhafz(ab[i] * 10**6, u[j][i]) for i in range(L)]
        out[key] = {"group": group, "job": j, "est": est, "v": v, "vb": vb, "abs": med(a), "D": D, "Db": Db}
        if key == "kit.find_byte.walk":
            W = med(v)
    for key, r in out.items():
        if "absent" in r:
            continue
        x = [rhafz(t * 10**6, W) for t in r["v"]]
        xb = [rhafz(t * 10**6, W) for t in r["vb"]]
        aa = med([abs(xb[i] - x[i]) for i in range(L)])
        r.update(x=x, value=med(x), aa=aa, noise=isqrt_rn(aa * aa + sp2(x)))
        if r["D"] is not None:
            aaD = med([abs(r["Db"][i] - r["D"][i]) for i in range(L)])
            r["null"] = not (all(d > 0 for d in trim(r["D"])) and med(r["D"]) > aaD)
            if r["null"] and med(r["D"]) < 0:
                r["why"] = "null: negative per-event cost (a fixture artifact)"
            elif r["null"]:
                r["why"] = "null: below its paired A/A or signs mixed over the trimmed six"
        else:
            g = plan.GATE_E6 // 2 if key == "kit.find_byte.walk" else plan.GATE_E6
            r["gate"] = r["value"] > 0 and r["noise"] * 10**6 <= g * r["value"]
    unit = out.get("kit.find_byte.walk", {})
    unit_bad = None
    if "absent" in unit or not unit:
        unit_bad = "unit absent"
    else:
        s = sorted(unit["x"])
        if not unit["gate"]:
            unit_bad = "unit over its half gate"
        elif any(s[k] - s[k - 1] > plan.GATE_E6 // 2 for k in range(2, 6)):
            unit_bad = "unit bimodal"
    drift = {}
    if "J2" in u:
        C2 = med(u["J2"])
        rel = lambda v: [rhafz(t * 10**6, med(v)) for t in v]
        for j in sorted(u):
            d = rhafz(abs(med(u[j]) - C2) * 10**6, C2)
            T = max(plan.GATE_E6 // 2, 3 * isqrt_rn(rhafz(K_MED_E6 * (sp2(rel(u["J2"])) + sp2(rel(u[j]))), 10**6)))
            drift[j] = (d, T, d > T)
    def unpriced(key):
        r = out[key]
        if "absent" in r:
            return r["absent"]
        if drift.get(r["job"], (0, 0, False))[2]:
            return "drift:%s" % r["job"]
        if r.get("null") or r.get("gate") is False:
            return "text"
        return None
    j1b = rec["run"].get("j1_verdict") == "b"
    clauses = {}
    for cl, key, when in floor:
        if j1b and when == "unless-j1-b":
            continue
        clauses.setdefault(cl, []).append(key)
    failed = [cl for cl, ks in sorted(clauses.items()) if all(unpriced(k) for k in ks)]
    absent = [k for k in out if "absent" in out[k] or drift.get(out[k]["job"], (0, 0, False))[2]
              or out[k].get("gate") is False]
    if unit_bad:
        outcome = ("REFUSED", 3, ["unit"])
    elif failed:
        outcome = ("REFUSED", 3, ["floor:%s (%s)" % (cl, ",".join(sorted({unpriced(k) for k in clauses[cl]})))
                                  for cl in failed])
    elif absent:
        outcome = ("PARTIAL", 4, sorted(absent))
    else:
        outcome = ("FULL", 0, [])
    return out, drift, unit_bad, outcome, W

def form_hash(form):
    fx = os.path.join(TREE, "build", "arm_fixtures")
    r = subprocess.run([fx, "--hash"], capture_output=True, text=True)
    for ln in r.stdout.splitlines():
        f = ln.split("\t")
        if f[0] == "FORM" and f[1] == form and f[2] == "0":
            return f[3]
    raise SystemExit("est: no form hash for %s (build/arm_fixtures --hash)" % form)

def main():
    cmd, rundir = sys.argv[1], sys.argv[2]
    out, drift, unit_bad, outcome, W = compute(rundir)
    if cmd == "rows":
        for k in sorted(out):
            r = out[k]
            if "absent" in r:
                print("row\t%s\tABSENT\t%s" % (k, r["absent"]))
            else:
                print("row\t%s\tvalue %s\tnoise %s\t%s" % (k, "-" if r.get("null") else r["value"],
                      "-" if r.get("null") else r["noise"],
                      r.get("why") or ("gate %s" % ("pass" if r.get("gate", True) else "FAIL"))))
        for j, (d, T, bad) in sorted(drift.items()):
            print("drift\t%s\t%d\t%d\t%s" % (j, d, T, "REFUSED" if bad else "kept"))
        print("== s2 OUTCOME %s exit %d %s" % (outcome[0], outcome[1], "; ".join(outcome[2])))
        return outcome[1]
    if cmd == "draft":
        return write_draft(rundir, sys.argv[3], out, drift, outcome)

def write_draft(rundir, path, out, drift, outcome):
    rec = read_record(rundir)
    rsha = hashlib.sha256(open(os.path.join(rundir, "run_record.tsv"), "rb").read()).hexdigest()
    cards = [ln.rstrip("\n") for ln in open(os.path.join(TREE, "memfn", "data", "cards", "kit-grid.tsv"))
             if not ln.startswith("#") and ln.split("\t")[2:3] == ["3"]]
    rows = []
    hashes = {}
    for k in sorted(out):
        r = out[k]
        if "absent" in r or r.get("gate") is False or drift.get(r["job"], (0, 0, False))[2]:
            continue
        q = k.split(".")
        unit = "ratio" if q[1] == "find_byte" else "walkbytes"
        deps = "-"
        if q[1] != "enter":
            hashes.setdefault(q[2], form_hash(q[2]))
            deps = "kit:form.%s=%s" % (q[2], hashes[q[2]])
        if r.get("null"):
            rows.append([k, unit, "", str(r["abs"]), "-", str(plan.L_LAUNCHES * plan.R_ROUNDS), "null", "-", "-",
                         deps, "-", r["why"]])
        else:
            rows.append([k, unit, str(r["value"]), str(r["abs"]), str(r["noise"]),
                         str(plan.L_LAUNCHES * plan.R_ROUNDS), "measured", "-", "-", deps, "-", "slot " + r["job"]])
    hdr = [("format", "2"), ("id", "zen4-grid3"), ("rev", "1"), ("class", "x86_64/zen4"),
           ("isa", rec["run"].get("isa", "")), ("tier", "scratch"), ("composite", "0"), ("members", ""),
           ("unit_key", "kit.find_byte.walk"), ("method", "kit-grid@3"),
           ("run", "%s record:%s" % (rec["run"].get("run_id", ""), rsha)),
           ("box", rec["run"].get("box", "")), ("compiler", "gcc 15.2.0 -O2 -march=x86-64 -mtune=generic"),
           ("libc", rec["run"].get("libc", "")), ("code_commit", rec["run"].get("code_commit", "")),
           ("counters", "skipped:not-taken"), ("partial", "1" if outcome[0] == "PARTIAL" else "0"),
           ("rows", str(len(rows))), ("values_digest", "0000000000000000")]
    cells = []
    for f in sorted(os.listdir(rundir)):
        if f.startswith("cells.J") and f.endswith(".tsv"):
            cells += [ln.rstrip("\n") for ln in open(os.path.join(rundir, f)) if ln.strip() and not ln.startswith("#")]
    def text(h):
        t = ["# pcrec measurement set (spec: docs/spec/measures.md)", "#section header", "#key\tvalue"]
        t += ["%s\t%s" % kv for kv in h]
        t += ["#section cards", "#" + "\t".join(["owner", "quantity", "ver", "dims", "unit", "subject", "lengths",
              "launches", "rounds", "aa_rule", "gate_e6", "env", "deps"])] + cards
        t += ["#section rows", "#" + "\t".join(["key", "unit", "value_e6", "abs_ns_e6", "noise_e6", "n", "status",
              "derivation", "inputs", "deps", "tags", "source"])] + ["\t".join(r) for r in rows]
        t += ["#section members", "#member\tunit_key\tunit_abs_ns_e6\tbox"]
        t += ["#section cells", "#" + "\t".join(CELL_COLS)] + cells
        return "\n".join(t) + "\n"
    open(path, "w").write(text(hdr))
    d = subprocess.run([sys.executable, "-I", os.path.join(TREE, "tests", "knowledge", "ks_ref.py"), "digest", path],
                       capture_output=True, text=True, check=True).stdout.strip()
    hdr[-1] = ("values_digest", d)
    open(path, "w").write(text(hdr))
    print("draft %s: %d rows, %d cells, digest %s, outcome %s" % (path, len(rows), len(cells), d, outcome[0]))
    return outcome[1]

if __name__ == "__main__":
    sys.exit(main())
