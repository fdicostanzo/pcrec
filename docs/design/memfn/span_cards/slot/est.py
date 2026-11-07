# span_cards/slot/est.py — THE SLOT'S ESTIMATOR: span_cards.md §3.4-§3.5 (docs/spec/measures.md §3.4-§3.5) over
# the window's cells, the gates, the NULL rule, the bimodal test, drift, the floor and the first-match outcome
# table; and the DRAFT SET writer (§3.8 step 1). Its arithmetic is drill.py's (the same text implemented
# literally; drill.py stays the design's evidence). The recompute (S2e, tests/knowledge/) is written from the
# spec and shares nothing with this file.
#   python3 -I est.py rows     RUNDIR           the rows and verdicts, one line each, and the outcome
#   python3 -I est.py draft    RUNDIR OUT.tsv   the draft set (format 2), digest by tests/knowledge/ks_ref.py;
#                                               a REFUSED outcome writes NO draft (exit 3, r9 G5/CONTRACT-6)
#   python3 -I est.py selftest SCRATCH          the input cross-checks over synthetic run directories (r9 G3)
# RUNDIR holds the FINALIZED run_record.tsv (record.py), cells.J<j>.tsv per ran timing job (format 2's cell
# columns under a `#run_id` line) and <job>/cell_text.tsv (link.py). THE RECORD IS THE INPUT (r9 G3): the plan,
# the floor and which jobs ran are its sections, never a live plan.py rebuild and never "a cells file exists";
# and so are the CARD AND POLICY VALUES ([rev1.3 r9fc-FIX-1]): the estimators, lengths, launches, rounds, units
# and gates come from the record's pinned `cards` and `policy` rows (plan.parse_cards over them), never from
# memfn/data's live tables, so a table edited after the run never moves its verdict.
# Refused inputs exit 2: a cells file of a never-ran job, a ran job missing a planned cell, a cells file of
# another run, an id whose fields disagree with its columns, a delta cell naming another base than the family
# rule's (plan.base_of), a ran job with no cell texts.
import hashlib, math, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plan  # noqa: E402

TREE = plan.TREE
K_TRIM_E6, K_MED_E6 = 1723000, 210300      # measures.md §3.4¶16, §3.5¶6
# [rev1.4 R14-3, R14-4] the NOTE thresholds: they gate nothing (a note line in the record and the draft only)
NOTE_SPLIT_E6 = 5000       # a job's control: a gap over 0.5 % between two clusters of >= 2 launches: UNMEASURED DEFAULT (D149)
NOTE_BIMODAL_E6 = 100000   # a priced delta row: a gap over 10 % of its value, likewise: UNMEASURED DEFAULT (D149)


class InputError(Exception):
    """a refused input (exit 2)"""

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

def resolution(x):
    """[rev1.4 R14-2] a delta row's RESOLUTION r (measures.md §3.5¶3a): three standard errors of the median of its
    L anchored launch values, 3 x isqrt_rn(K_MED x sp2(x)) (§3.5¶6's scale for one median), in the row's unit"""
    return 3 * isqrt_rn(rhafz(K_MED_E6 * sp2(x), 10**6))

def r_max(rec):
    """[rev1.4 r10-REV14-2] (the cap on r, its source): the record's pinned policy row r_max_e6; a record planned
    before the row existed (windows s2d-20261106 and the second, both frozen at rev 1.4) pins none, and est then
    reads the LIVE table's row and says so in a `policy` line (rows) and a `# note` line (draft), never silently"""
    pol = plan.parse_policy(rec["policy"])
    if "r_max_e6" in pol:
        return pol["r_max_e6"], "pinned by the run record"
    live = plan.parse_policy(plan.table_rows(plan.POLICY))
    if "r_max_e6" not in live:
        raise InputError("neither the record's pinned policy nor the live %s holds r_max_e6" % plan.POLICY)
    return live["r_max_e6"], "NOT pinned by the run record (planned before the row): the live %s's, sha256 %s" % (
        os.path.relpath(plan.POLICY, TREE), plan.sha256(plan.POLICY))

def split_gap(v):
    """the largest gap between two clusters of >= 2 launches in v sorted (k in 2 .. L-2, §3.5¶4's clusters)"""
    s = sorted(v)
    return max(s[k] - s[k - 1] for k in range(2, len(s) - 1))

def slope(pts):
    n = len(pts)
    sx = sum(x for x, _ in pts); sy = sum(y for _, y in pts)
    S = n * sum(x * y for x, y in pts) - sx * sy
    D = n * sum(x * x for x, _ in pts) - sx * sx
    return rhafz(S, D)

CELL_COLS = ["cell", "group", "arm", "length", "launch", "round", "events", "ns_e6"]

def cell_row(a, length, l, ns_e6):
    """one cell line for arm a (a plan.Arm) at (length, launch l): the id's fifth field is a delta arm's base
    (§3.4¶5), events the arm's (`-` on a slope arm and on ctl)"""
    base = a.base if a.base and not a.name.startswith("base.") else None
    cid = "%s/%s/%d/%d" % (a.group, a.name, length, l) + ("/" + base if base else "")
    ev = "-" if a.events is None else str(a.events)
    return "\t".join([cid, a.group, a.name, str(length), str(l), "med", ev, str(ns_e6)])

def cells_text(run_id, rows):
    return "#run_id\t%s\n#%s\n%s\n" % (run_id, "\t".join(CELL_COLS), "\n".join(rows))

def read_cells(rundir, rec):
    """the cells of every RAN timing job, cross-checked against the record (r9 G3)"""
    ran = {j for j, (s, _c) in rec["jobs"].items() if s == "ran"}
    cells = []
    for f in sorted(os.listdir(rundir)):
        m = re.fullmatch(r"cells\.(J\w+)\.tsv", f)
        if not m:
            continue
        j = m.group(1)
        if j not in ran:
            raise InputError("%s holds cells of job %s, which the record says %s" % (f, j, rec["jobs"].get(j, ("unplanned",))[0]))
        lines = open(os.path.join(rundir, f)).read().splitlines()
        if not lines or lines[0] != "#run_id\t%s" % rec["run"]["run_id"]:
            raise InputError("%s's first line %r is not `#run_id<TAB>%s`: a cells file of another run" % (f, lines[:1], rec["run"]["run_id"]))
        for ln in lines[1:]:
            if ln.startswith("#") or not ln.strip():
                continue
            c = dict(zip(CELL_COLS, ln.split("\t")))
            try:
                c["length"], c["launch"], c["ns_e6"] = int(c["length"]), int(c["launch"]), int(c["ns_e6"])
            except (KeyError, ValueError):
                raise InputError("%s: a malformed cell line %r" % (f, ln))
            idf = c["cell"].split("/")
            if idf[:4] != [c["group"], c["arm"], str(c["length"]), str(c["launch"])] or c["group"].split(".")[0] != j:
                raise InputError("%s: cell id %s disagrees with its columns (%s %s %d %d) or its job" % (f, c["cell"], c["group"], c["arm"], c["length"], c["launch"]))
            key = c["arm"][:-2] if c["arm"].endswith("#b") else c["arm"]
            want = plan.base_of(key) if key.startswith("kit.") else None
            if (idf[4] if len(idf) == 5 else None) != want or len(idf) > 5:
                raise InputError("%s: cell %s names base %s, the family rule's is %s" % (f, c["cell"], idf[4:] or "none", want))
            c["job"] = j
            cells.append(c)
    return cells

def read_record(rundir):
    """the finalized run record: run (dict), jobs {job: (state, cause)}, plan [(key, group, job)], floor, the
    pinned card and policy rows, and from them `card` ({quantity: card}) and `facts` (plan.card_facts)"""
    rec, sec = {"run": {}, "jobs": {}, "plan": [], "floor": [], "cards": [], "policy": []}, None
    p = os.path.join(rundir, "run_record.tsv")
    if not os.path.exists(p):
        raise InputError("%s is absent (record.py finalize writes it)" % p)
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
        elif sec in ("plan", "floor"):
            rec[sec].append(tuple(f))
        elif sec in ("cards", "policy"):
            rec[sec].append(f)
    if not rec["run"].get("run_id") or not rec["jobs"] or not rec["plan"] or not rec["floor"]:
        raise InputError("%s is not finalized (run_id, jobs, plan and floor are all required)" % p)
    for k in ("cards", "policy"):
        if not rec[k] or not re.fullmatch(r"[0-9a-f]{64}", rec["run"].get(k + "_sha256", "")):
            raise InputError("%s pins no %s values or no %s_sha256 (r9fc FIX-1: the verdict reads the values the "
                             "run was planned under, never the live tables)" % (p, k, k))
    try:
        rec["card"] = plan.parse_cards(rec["cards"], plan.parse_policy(rec["policy"]))
        rec["facts"] = plan.card_facts(rec["card"])
    except (SystemExit, KeyError, ValueError) as e:
        raise InputError("%s's pinned cards or policy do not parse: %s" % (p, e))
    if len(rec["card"]) != len(rec["cards"]):
        raise InputError("%s pins %d card rows, %d of them ver-%s cards" % (p, len(rec["cards"]), len(rec["card"]), plan.METHOD_VER))
    if rec["run"].get("rules") != "kit-grid@" + plan.METHOD_VER:
        raise InputError("the record's rules owner %r is not this producer's kit-grid@%s (measures.md §3.5¶8a)"
                         % (rec["run"].get("rules"), plan.METHOD_VER))
    return rec

def compute(rundir):
    rec = read_record(rundir)
    cells = read_cells(rundir, rec)
    floor = rec["floor"]
    R_MAX = r_max(rec)[0]
    card = rec["card"]                         # the PINNED cards (r9fc FIX-1), never plan.CARD
    LENGTHS, _LEN, L, _R, GU = rec["facts"]
    if any(k.split(".")[1] not in card for k, _g, _j in rec["plan"]):
        raise InputError("a planned key's quantity has no pinned card (%s)" % sorted({k.split(".")[1] for k, _g, _j in rec["plan"]} - set(card)))
    rows = [(k, g, j, card[k.split(".")[1]]["est"], plan.base_of(k)) for k, g, j in rec["plan"]]
    c = {}
    for x in cells:
        c[(x["job"], x["arm"], x["length"], x["launch"])] = x
    ran = {j for j, (s, _c) in rec["jobs"].items() if s == "ran" and j != "J1"}
    def need(j, arm, length, l):
        if (j, arm, length, l) not in c:
            raise InputError("job %s ran, but its cell (%s, %d, launch %d) is absent" % (j, arm, length, l))
        return c[(j, arm, length, l)]
    def cell(j, arm, length, l):
        return need(j, arm, length, l)["ns_e6"]
    u = {}
    for j in sorted(ran):
        if not any(r[2] == j for r in rows):
            continue
        u[j] = [slope([(x, cell(j, "ctl", x, l)) for x in LENGTHS]) for l in range(1, L + 1)]
        if min(u[j]) <= 0:
            raise InputError("job %s's control slopes %s: every u_l must be positive (measures.md §3.4¶14a)" % (j, u[j]))
    out = {}
    W = None
    for key, group, j, est, base in rows:
        if j not in ran:
            out[key] = {"absent": "never-ran:%s" % j}
            continue
        kind, xs = plan._est_parse(est)
        def per_launch(arm):
            if kind == "slope":
                return [slope([(x, cell(j, arm, x, l)) for x in xs]) for l in range(1, L + 1)], None
            ev = {need(j, a2, xs[0], l)["events"] for a2 in (key, key + "#b") for l in range(1, L + 1)}
            if len(ev) != 1 or not next(iter(ev)).isdigit() or int(next(iter(ev))) <= 0:
                raise InputError("%s's cells state events %s: one positive E is required (§3.4¶11)" % (key, sorted(ev)))
            E = int(ev.pop())
            D = [cell(j, arm, xs[0], l) - cell(j, base, xs[0], l) for l in range(1, L + 1)]
            return [rhafz(d, E) for d in D], D
        a, D = per_launch(key)
        ab, Db = per_launch(key + "#b")
        v = [rhafz(a[i] * 10**6, u[j][i]) for i in range(L)]
        vb = [rhafz(ab[i] * 10**6, u[j][i]) for i in range(L)]
        out[key] = {"group": group, "job": j, "est": est, "v": v, "vb": vb, "abs": med(a), "D": D, "Db": Db}
        if key == plan.UNIT_KEY:
            W = med(v)
    for key, r in out.items():
        if "absent" in r:
            continue
        if W is None or W <= 0:
            break
        x = [rhafz(t * 10**6, W) for t in r["v"]]
        xb = [rhafz(t * 10**6, W) for t in r["vb"]]
        aa = med([abs(xb[i] - x[i]) for i in range(L)])
        r.update(x=x, value=med(x), aa=aa, noise=isqrt_rn(aa * aa + sp2(x)))
        if r["D"] is not None:
            aaD = med([abs(r["Db"][i] - r["D"][i]) for i in range(L)])
            r["null"] = not (all(d > 0 for d in trim(r["D"])) and med(r["D"]) > aaD)
            # [rev1.4 r10-REV14-2] r is the row's resolution capped at the policy's r_max_e6
            res = min(resolution(x), R_MAX)
            if r["null"] and all(d < 0 for d in trim(r["D"])):
                # [rev1.4 r10-REV14-1] negative on all six trimmed launches: a DEFECT, whatever r is
                r["why"] = "null: negative per-event cost on all six trimmed launches (a fixture defect, whatever r)"
            elif r["null"] and abs(r["value"]) <= res and r["aa"] <= res:
                # [rev1.4 R14-2] SUB-RESOLUTION: signs mixed, consistent with zero within r, its paired A/A within
                # r too: a MEASURED row, the clamped estimate, its noise r or the measured noise if larger
                # (measures.md §3.5¶3a)
                r.update(null=False, sub=res, value=max(0, r["value"]), noise=max(res, r["noise"]),
                         why="sub-resolution: consistent with zero within r %d" % res)
            elif r["null"] and abs(r["value"]) <= res:
                r["why"] = "null: within its resolution r %d but its paired A/A %d is above r" % (res, r["aa"])
            elif r["null"]:
                r["why"] = "null: below its paired A/A or signs mixed, at a size above its resolution r %d" % res
        else:
            # §3.5¶2: the card's gate; the unit's is HALF, compared doubled (exact for an odd gate, r9 G7)
            G = card[key.split(".")[1]]["gate"]
            half = 2 if key == plan.UNIT_KEY else 1
            r["gate"] = r["value"] > 0 and half * r["noise"] * 10**6 <= G * r["value"]
    unit = out.get(plan.UNIT_KEY, {})
    unit_bad = None
    if "absent" in unit or not unit or W is None or W <= 0:
        unit_bad = "unit absent"                  # measures.md §3.5¶12 row 1: no unit, no set (r9 CONTRACT-4)
    else:
        s = sorted(unit["x"])
        if not unit["gate"]:
            unit_bad = "unit over its half gate"
        elif any(2 * (s[k] - s[k - 1]) > GU for k in range(2, L - 1)):
            unit_bad = "unit bimodal"
    drift = {}
    uj = next((j for k, _g, j, _e, _b in rows if k == plan.UNIT_KEY), None)
    if uj in u:
        CU = med(u[uj])
        rel = lambda v: [rhafz(t * 10**6, med(v)) for t in v]
        for j in sorted(u):
            d = rhafz(abs(med(u[j]) - CU) * 10**6, CU)
            T3 = 3 * isqrt_rn(rhafz(K_MED_E6 * (sp2(rel(u[uj])) + sp2(rel(u[j]))), 10**6))
            drift[j] = (d, T3, 2 * d > GU and d > T3)    # §3.5¶6: both the size floor G/2 and 3 SE
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
        if when not in ("always", "unless-j1-b"):
            raise InputError("floor clause %s: unknown condition token %r" % (cl, when))
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

def notes(rundir, out=None):
    """[rev1.4 R14-3, R14-4] the run's NOTE lines (the record's `run` keys note_box_state and note_bimodal, the
    draft's `# note` lines): a launch-level fast/slow split in a job's control (NOTE_SPLIT_E6), and the priced
    delta rows whose launches fall in two clusters (NOTE_BIMODAL_E6). They gate nothing."""
    if out is None:
        out = compute(rundir)[0]
    rec = read_record(rundir)
    LENGTHS, L = rec["facts"][0], rec["facts"][2]
    c = {(x["job"], x["arm"], x["length"], x["launch"]): x["ns_e6"] for x in read_cells(rundir, rec)}
    split = []
    for j in sorted({j for j, _a, _x, _l in c}):
        if (j, "ctl", LENGTHS[0], 1) not in c:
            continue
        u = [slope([(x, c[(j, "ctl", x, l)]) for x in LENGTHS]) for l in range(1, L + 1)]
        g = split_gap([rhafz(t * 10**6, med(u)) for t in u])
        if g > NOTE_SPLIT_E6:
            split.append("%s %d.%02d %%" % (j, g // 10000, g % 10000 // 100))
    bim = sorted(k for k, r in out.items() if "absent" not in r and r.get("D") is not None and not r.get("null")
                 and not r.get("sub") and split_gap(r["x"]) * 10**6 > NOTE_BIMODAL_E6 * r["value"])
    return [("note_box_state", "a launch-level fast/slow split in the control of %s (a gap over %d ppm between two "
             "clusters of >= 2 launches): the box changed state within those jobs" % (", ".join(split), NOTE_SPLIT_E6)
             if split else "no launch-level fast/slow split in any job's control"),
            ("note_bimodal", "bimodal delta rows (a gap over %d ppm of the value between two clusters of >= 2 "
             "launches; priced with their spread as noise): %s" % (NOTE_BIMODAL_E6, ", ".join(bim) or "none"))]

def cell_texts(rundir, rec):
    """{row key: (form, fold hash, tags)} from every ran job's cell_text.tsv (link.py's, the texts it TIMED and
    checked, r9 G5); a form whose fold differs between jobs REFUSES (the kit moved inside the window)"""
    out, fold = {}, {}
    for j, (s, _c) in sorted(rec["jobs"].items()):
        if s != "ran" or j == "J1":
            continue
        p = os.path.join(rundir, j, "cell_text.tsv")
        if not os.path.exists(p):
            raise InputError("job %s ran but %s is absent" % (j, p))
        for ln in open(p):
            if ln.startswith("#") or not ln.strip():
                continue
            arm, form, _cls, _inst, fh, tags = ln.rstrip("\n").split("\t")
            if fold.setdefault(form, fh) != fh:
                raise InputError("form %s's fold hash is %s in one job and %s in %s" % (form, fold[form], fh, j))
            if not arm.endswith("#b") and arm.startswith("kit."):
                out[arm] = (form, fh, tags)
    return out

def main():
    cmd, rundir = sys.argv[1], sys.argv[2]
    if cmd == "selftest":
        return selftest(rundir)
    try:
        out, drift, unit_bad, outcome, W = compute(rundir)
    except InputError as e:
        print("est: REFUSED input: %s" % e)
        return 2
    if cmd == "rows":
        print("policy\tr_max_e6\t%d\t%s" % r_max(read_record(rundir)))
        for k in sorted(out):
            r = out[k]
            if "absent" in r:
                print("row\t%s\tABSENT\t%s" % (k, r["absent"]))
            else:
                # [rev1.4 R14-4] a delta row has no gate (measures.md §3.5¶3): `ungated`, never a gate verdict
                print("row\t%s\tvalue %s\tnoise %s\t%s" % (k, "-" if r.get("null") else r["value"],
                      "-" if r.get("null") else r["noise"],
                      r.get("why") or ("ungated" if r["D"] is not None else
                                       "gate %s" % ("pass" if r.get("gate", True) else "FAIL"))))
        for j, (d, T, bad) in sorted(drift.items()):
            print("drift\t%s\t%d\t%d\t%s" % (j, d, T, "REFUSED" if bad else "kept"))
        for k, v in notes(rundir, out):
            print("note\t%s\t%s" % (k, v))
        print("== s2 OUTCOME %s exit %d %s" % (outcome[0], outcome[1], "; ".join(outcome[2])))
        return outcome[1]
    if cmd == "draft":
        if outcome[0] == "REFUSED":
            print("== s2 OUTCOME REFUSED: no draft written (%s)" % "; ".join(outcome[2]))
            return outcome[1]
        try:
            return write_draft(rundir, sys.argv[3], out, drift, outcome)
        except InputError as e:
            print("est: REFUSED input: %s" % e)
            return 2

def write_draft(rundir, path, out, drift, outcome):
    rec = read_record(rundir)
    for k in ("box", "isa", "libc", "gcc", "code_commit"):
        if not rec["run"].get(k):
            raise InputError("the record's run section has no %s (record.py window writes it)" % k)
    texts = cell_texts(rundir, rec)
    rsha = hashlib.sha256(open(os.path.join(rundir, "run_record.tsv"), "rb").read()).hexdigest()
    # the ver-3 cards as the record pins them, VERBATIM: each states its declared gate_e6 (`-`), so check C's
    # set-vs-card-table equality holds; the value a `-` took is the record's pinned policy ([rev1.3 r9fc-FIX-8])
    cards = ["\t".join(f) for f in rec["cards"]]
    n = str(rec["facts"][2] * rec["facts"][3])
    rows = []
    for k in sorted(out):
        r = out[k]
        if "absent" in r or r.get("gate") is False or drift.get(r["job"], (0, 0, False))[2]:
            continue
        q = k.split(".")
        unit = rec["card"][q[1]]["unit"]
        deps, tags = "-", "-"
        if q[1] != "enter":
            if k not in texts:
                raise InputError("row %s has no cell text in its job's cell_text.tsv" % k)
            form, fh, tags = texts[k]
            if form != q[2]:
                raise InputError("row %s's cell text is form %s's" % (k, form))
            deps = "kit:form.%s=%s" % (form, fh)
        if r.get("null"):
            rows.append([k, unit, "", str(r["abs"]), "-", n, "null", "-", "-",
                         deps, tags, r["why"]])
        else:
            rows.append([k, unit, str(r["value"]), str(r["abs"]), str(r["noise"]), n, "measured", "-", "-", deps,
                         tags, "slot %s%s" % (r["job"], " sub-resolution r %d" % r["sub"] if r.get("sub") else "")])
    hdr = [("format", "2"), ("id", "zen4-grid3"), ("rev", "1"), ("class", "x86_64/zen4"),
           ("isa", rec["run"]["isa"]), ("tier", "scratch"), ("composite", "0"), ("members", ""),
           ("unit_key", plan.UNIT_KEY), ("method", "kit-grid@%s" % plan.METHOD_VER),
           ("run", "%s record:%s" % (rec["run"]["run_id"], rsha)),
           ("box", rec["run"]["box"]), ("compiler", "gcc %s -O2 -march=x86-64 -mtune=generic" % rec["run"]["gcc"]),
           ("libc", rec["run"]["libc"]), ("code_commit", rec["run"]["code_commit"]),
           ("counters", "skipped:not-taken"), ("partial", "1" if outcome[0] == "PARTIAL" else "0"),
           ("rows", str(len(rows))), ("values_digest", "0000000000000000")]
    cells = ["\t".join([c[k] if isinstance(c[k], str) else str(c[k]) for k in CELL_COLS]) for c in read_cells(rundir, rec)]
    def text(h):
        t = ["# pcrec measurement set (spec: docs/spec/measures.md)"]
        t += ["# note %s: %s" % kv for kv in notes(rundir, out)]       # [rev1.4 R14-3, R14-4]
        t += ["# note r_max_e6: %d, %s" % r_max(rec)]                   # [rev1.4 r10-REV14-2]
        t += ["#section header", "#key\tvalue"]
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

# ---- the self-test (r9 G3): the cross-checks above, each case a refusal or an outcome ---------------------------
def _synth(d, run_id="selftest"):
    """a synthetic finalized run directory: the live plan frozen, every timing job ran, linear cells (a slope
    arm's per-byte cost and a delta arm's per-event cost by its key's hash, so rows differ), no clock"""
    import record
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    open(os.path.join(d, "plan.tsv"), "w").write(plan.frozen_text())
    fr = plan.read_frozen(os.path.join(d, "plan.tsv"))
    jobs, _rows, _f, _u = plan.build()
    rec = {name: [] for name, _ in record.SECTIONS}
    rec["run"] = [["set", record.SET], ["rules", record.RULES], ["run_id", run_id], ["code_commit", "0000000"],
                  ["j1_verdict", "a"]]
    rec["jobs"] = [[j, "ran", "-"] for j in record.JOBS]
    record.pin(rec, fr)
    record.write(os.path.join(d, "run_record.tsv"), rec)
    for j, arms in jobs.items():
        if j == "J1":
            continue
        lines = []
        for a in arms:
            h = int(hashlib.sha256(a.name.rstrip("#b").encode()).hexdigest()[:4], 16)
            for l in range(1, plan.L_LAUNCHES + 1):
                for x in a.lengths:
                    jit = (l * 7919 + (a.name.endswith("#b")) * 13) % 97
                    if a.kind == "ctl" or plan._est_parse(plan.CARD.get(a.name.split(".")[1], {"est": "slope 1,2,3"})["est"])[0] == "slope" and not a.name.startswith("base."):
                        ns = x * (1000 + h % 500) + 5000 + jit
                    else:
                        ns = 9000000 + (a.events or 0) * (2000 + h % 900) + jit
                    lines.append(cell_row(a, x, l, ns * 1000))
        open(os.path.join(d, "cells.%s.tsv" % j), "w").write(cells_text(run_id, lines))
    return d

def selftest(scratch):
    """each case: (name, the plant on a fresh synthetic directory, the expected result: 'ok' or 'refused')"""
    def edit(p, f):
        new = f(open(p).read())
        open(p, "w").write(new)
    def drop_line(t):
        ls = t.split("\n")
        k = next(i for i, ln in enumerate(ls) if "/kit.find_hit." in ln and "/4/" in ln)
        return "\n".join(ls[:k] + ls[k + 1:])
    def set_never(d):
        edit(os.path.join(d, "run_record.tsv"), lambda t: t.replace("J3\tran\t-", "J3\tnever-ran\tfailed"))
    def base_swap(t):
        return re.sub(r"(/kit\.find_hit\.libc\.[^\t]*/)base\.libc\t", r"\1base.walk\t", t, count=1)
    def unpin(d):
        edit(os.path.join(d, "run_record.tsv"), lambda t: re.sub(r"(#section policy\n#[^\n]*\n)[^#]*", r"\1", t))
    def unit_twin_skew(d):     # 4 of the unit twin's 7 launches x1.004 at every length (fixcheck FIX-1's repro)
        def f(t):
            out = []
            for ln in t.split("\n"):
                c = ln.split("\t")
                if len(c) == 8 and c[2] == plan.UNIT_KEY + "#b" and int(c[4]) <= 4:
                    c[7] = str(int(c[7]) * 1004 // 1000)
                out.append("\t".join(c))
            return "\n".join(out)
        edit(os.path.join(d, "cells.J2.tsv"), f)
    def live_edit(d):          # the live tables move after the run: est must not read them (r9fc FIX-1)
        unit_twin_skew(d)
        for c in plan.CARD.values():
            c["gate"] = 300
        plan.CARD["find_byte"]["est"] = "slope 1,2,3"
    def set_delta(d, key, ds, twin=3):
        """[rev1.4 R14-2] KEY's (and its twin's) cells in J4 = its base's cell + ds[l-1] x E per launch l (the twin
        `twin` x E above): a per-event cost of ds[l-1] in the cells' own units"""
        p = os.path.join(d, "cells.J4.tsv")
        ls = open(p).read().split("\n")
        base = {}
        for ln in ls:
            c = ln.split("\t")
            if len(c) == 8 and c[2].startswith("base.null."):
                base[(c[2], c[3], c[4])] = int(c[7])
        out = []
        for ln in ls:
            c = ln.split("\t")
            if len(c) == 8 and c[2] in (key, key + "#b"):
                E, l = int(c[6]), int(c[4])
                c[7] = str(base[(c[0].split("/")[4], c[3], c[4])] + (ds[l - 1] + (twin if c[2] != key else 0)) * E)
            out.append("\t".join(c))
        open(p, "w").write("\n".join(out))
    VK = "kit.verify_cmp.settest.c1.p0"
    def row(pred):
        return lambda out: pred(out[VK])
    sub = row(lambda r: bool(r.get("sub")) and not r["null"] and r["value"] >= 0 and r["noise"] >= r["sub"])
    cases = [
        ("complete", lambda d: None, "ok"),
        ("[R14-2] a verify row at zero, signs mixed: sub-resolution, measured",
         lambda d: set_delta(d, VK, [40, -30, 10, -50, 20, -10, 30]), sub),
        ("[R14-2] consistently negative within r: measured, its value clamped to 0",
         lambda d: set_delta(d, VK, [-20, -60, -10, -40, -30, -90, -25]), row(lambda r: bool(r.get("sub")) and r["value"] == 0)),
        ("[R14-2] consistently negative above r: null (a fixture artifact)",
         lambda d: set_delta(d, VK, [-1000, -1010, -990, -1005, -995, -1020, -1000]),
         row(lambda r: r["null"] and not r.get("sub") and "negative" in r["why"])),
        ("[R14-2] signs mixed at a size above r: null",
         lambda d: set_delta(d, VK, [1000, 1000, 1000, 1000, -50, -600, 1000]),
         row(lambda r: r["null"] and not r.get("sub") and "signs mixed" in r["why"])),
        ("[R14-2] a priced verify row keeps the NULL rule's value (no clamp, no r)",
         lambda d: set_delta(d, VK, [1000, 1010, 990, 1005, 995, 1020, 1000]),
         row(lambda r: not r["null"] and not r.get("sub") and r["value"] > 0)),
        ("[R14-4] a delta row in two clusters is named by the bimodal note",
         lambda d: set_delta(d, VK, [1000, 1000, 1000, 1500, 1500, 1500, 1000]),
         lambda out: VK in dict(notes(d_now[0], out))["note_bimodal"]),
        ("leftover cells of a never-ran job", set_never, "refused"),
        ("a planned cell missing", lambda d: edit(os.path.join(d, "cells.J3.tsv"), drop_line), "refused"),
        ("a cells file of another run", lambda d: edit(os.path.join(d, "cells.J4.tsv"),
                                                       lambda t: t.replace("#run_id\tselftest", "#run_id\tother", 1)), "refused"),
        ("a delta cell naming another base", lambda d: edit(os.path.join(d, "cells.J3.tsv"), base_swap), "refused"),
        ("an id disagreeing with its launch column", lambda d: edit(os.path.join(d, "cells.J2.tsv"),
            lambda t: re.sub(r"(J2\.unit/kit\.find_byte\.walk/65536/)4(\t)", r"\g<1>5\2", t, count=1)), "refused"),
        ("a record pinning no policy values", unpin, "refused"),
        ("a unit twin skewed (the baseline of the next case)", unit_twin_skew, "ok"),
        ("live card/policy edit after the run", live_edit, "same"),
    ]
    # `same`: the record and cells equal the previous case's byte for byte, only the LIVE tables differ (the
    # plant edits plan.CARD in memory, restored after), and the outcome must be the previous case's
    bad, prev = 0, None
    live = {q: dict(c) for q, c in plan.CARD.items()}
    d_now = [None]
    for name, plant, want in cases:
        d = d_now[0] = _synth(os.path.join(scratch, "est_selftest"))
        before = open(os.path.join(d, "run_record.tsv")).read() + "".join(
            open(os.path.join(d, f)).read() for f in sorted(os.listdir(d)) if f.startswith("cells."))
        plant(d)
        after = open(os.path.join(d, "run_record.tsv")).read() + "".join(
            open(os.path.join(d, f)).read() for f in sorted(os.listdir(d)) if f.startswith("cells."))
        if want not in ("ok", "same", "refused"):       # a row predicate over compute()'s rows (rev 1.4)
            try:
                ok = bool(want(compute(d)[0]))
            except (InputError, KeyError) as e:
                ok = False
                print("selftest\t%s\t(%s)" % (name, e))
            bad += not ok
            print("selftest\t%s\t%s" % (name, "ok" if ok else "WRONG"))
            continue
        if want != "ok" and before == after and plan.CARD == live:
            print("selftest\t%s\tPLANT DID NOT APPLY" % name)
            bad += 1
            continue
        try:
            outcome = compute(d)[3]
            got = "ok"
            why = "%s exit %d" % outcome[:2]
        except InputError as e:
            outcome, got, why = None, "refused", str(e)
        finally:
            for q, c in live.items():
                plan.CARD[q].clear()
                plan.CARD[q].update(c)
        if want == "same":
            got = "same" if outcome is not None and prev is not None and outcome[:2] == prev[:2] and after == prev_after else "moved"
            why += " (the previous case's: %s)" % ("%s exit %d" % prev[:2] if prev else "none")
        prev, prev_after = outcome, after
        ok = got == want
        bad += not ok
        print("selftest\t%s\t%s\t%s (%s)" % (name, "ok" if ok else "WRONG", got, why[:150]))
    print("== est SELFTEST %s: %d cases, %d wrong" % ("ok" if not bad else "FAILED", len(cases), bad))
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
