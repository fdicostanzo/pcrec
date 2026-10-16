#!/usr/bin/env python3
"""grid2: the wall estimate of the FULL zen4-grid2 slot from a DRY run's own per-launch costs.

  python3 -I estimate.py DRYOUT        reads DRYOUT/{slot.status,time/raw_*.tsv,build.log,check.out,
                                       subjects.tsv,f2.log}, designs the FULL slot into
                                       DRYOUT/full_design/ (design2.py design, no build) and prints
                                       the estimate table; the LAST line is the one-line verdict.

What is measured and what is assumed (each row says which):
  - TIMING phases (F1, F3, OB, TRIG): seconds per LAUNCH measured from the dry raw files'
    nanosecond timestamps (the gap to the next launch of the same group), by subject class
    (tiny n <= 128 B, mid <= 128 KiB, big larger) and phase; the full slot's launches are
    groups x (arms + 2 base copies) x (LAUNCHES + RERUN_EXTRA x RERUN_SHARE), RERUN_SHARE = 0.2
    (EP69, an estimate: the dry run times 1 launch and cannot measure it);
  - BUILD: the dry run's measured build wall + the generator's measured seconds per MiB
    scaled to the full subject bytes;
  - CHECK: the dry run's measured check wall scaled by (arms x subject bytes) of the full
    design over the dry's (an assumption: R, L, C each load the subject once per arm);
  - PERF (items 6-7): the dry run's measured seconds per perf row scaled to the full row count;
    when the dry run skipped perf, items 6-7 use the spec's ~5 + 1 min and say so.
Quiet-gate waits are not estimated (they are the box's).
"""
import collections, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAUNCHES, EXTRA, SHARE = 3, 2, 0.2

def klass(n):
    return "tiny" if n <= 128 else ("mid" if n <= 131072 else "big")

def read_tsv(p):
    L = open(p).read().splitlines()
    h = L[0].split("\t")
    return [dict(zip(h, l.split("\t"))) for l in L[1:] if l]

def spec_phase(cell, item):
    if str(item) in ("34", "3"): return "OB"
    if str(item) == "8": return "TRIG"
    return "F3" if cell.startswith("f3-") else "F1"

def main(out):
    full = os.path.join(out, "full_design")
    os.makedirs(full, exist_ok=True)
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "design2.py"), "design", full], check=True, capture_output=True)
    # ---- measured seconds per launch, by (phase, class)
    dsub = {r["name"]: int(r["n"]) for r in read_tsv(os.path.join(out, "subjects.tsv"))}
    secs = collections.defaultdict(list)
    for f in sorted(os.listdir(os.path.join(out, "time"))) if os.path.isdir(os.path.join(out, "time")) else []:
        if not f.startswith("raw_"): continue
        rows = [l.split("\t") for l in open(os.path.join(out, "time", f)).read().splitlines()[1:]]
        for a, b in zip(rows, rows[1:]):
            if a[1:4] != b[1:4]: continue          # a group boundary: not a launch gap
            nm = a[2].split("@")[0]
            ph = {"raw_F1.tsv": "F1", "raw_F3.tsv": "F3", "raw_OB.tsv": "OB", "raw_TRIG.tsv": "TRIG"}.get(f, "F1")
            secs[(ph, klass(dsub.get(nm, 65536)))].append(float(b[10]) - float(a[10]))
    mean = lambda v: sum(v) / len(v)
    allsecs = [x for v in secs.values() for x in v]
    glob = mean(allsecs) if allsecs else 0.75
    def per(ph, k):
        if secs.get((ph, k)): return mean(secs[(ph, k)]), "measured n=%d" % len(secs[(ph, k)])
        kk = [x for (p, c), v in secs.items() if c == k for x in v]
        if kk: return mean(kk), "class mean n=%d" % len(kk)
        return glob, "global mean (class unseen in the dry run)"
    # ---- the full design's launches
    fsub = {r["name"]: (int(r["n"]), int(r["nbuf"])) for r in read_tsv(os.path.join(full, "subjects.tsv"))}
    tab = collections.OrderedDict()
    for g in read_tsv(os.path.join(full, "groups2.tsv")):
        ph = spec_phase(g["cell"], g["item"])
        nm = g["subject"].split("@")[0]
        n = fsub[nm][0]
        arms = [a for a in g["arms"].split(",")]
        per_round = len(arms) + 2
        s, why = per(ph, klass(n))
        launches = per_round * (LAUNCHES + EXTRA * SHARE)
        t = tab.setdefault(ph, [0, 0.0, 0.0, collections.Counter()])
        t[0] += 1; t[1] += launches; t[2] += launches * s; t[3][why.split(" n=")[0]] += 1
    # ---- build, check, gen
    bt = re.findall(r"^gen: wall=(\d+)s bytes=(\d+)", open(os.path.join(out, "build.log")).read(), re.M)
    dry_gen_s, dry_gen_b = (int(bt[0][0]), int(bt[0][1])) if bt else (0, 1)
    st = open(os.path.join(out, "slot.status")).read()
    def stamp(name):
        m = re.search(r"^%s_(?:START|END)\b.*?(\d{4}-\d\d-\d\dT[\d:]+)" % name, st, re.M)
        return m.group(1) if m else None
    from datetime import datetime
    def span(name):
        a = re.search(r"^%s_START (\S+)" % name, st, re.M); b = re.search(r"^%s_END \S+ (\S+)" % name, st, re.M)
        if not (a and b): return None
        f = lambda x: datetime.fromisoformat(x)
        return (f(b.group(1)) - f(a.group(1))).total_seconds()
    dry_build = span("BUILD") or 0.0
    dry_check = span("CHECK") or 0.0
    fbytes = sum(n * nb for n, nb in fsub.values())
    gen_full = (dry_gen_s / max(1, dry_gen_b)) * fbytes
    def arm_bytes(groups_tsv, sub):
        t = 0
        for g in read_tsv(groups_tsv):
            n, nb = sub[g["subject"].split("@")[0]]
            t += (len(g["arms"].split(",")) + 0) * n * nb
        return t
    ratio = arm_bytes(os.path.join(full, "groups2.tsv"), fsub) / max(1, arm_bytes(os.path.join(out, "groups2.tsv"), {r["name"]: (int(r["n"]), int(r["nbuf"])) for r in read_tsv(os.path.join(out, "subjects.tsv"))}))
    check_full = dry_check * ratio
    # ---- perf
    f2log = os.path.join(out, "f2.log")
    perf_rows = 0; perf_note = "spec's ~5 + 1 min (the dry run skipped perf)"
    f2_full = 6 * 60.0
    if os.path.exists(f2log) and "SKIPPED" not in open(f2log).read():
        m = re.search(r"^F2_DONE item=\S+ rows=(\d+)", st, re.M); w = span("F2")
        if m and w:
            rows_dry = int(m.group(1)); frows = 0
            for r in read_tsv(os.path.join(full, "arms_f2.tsv")) if False else []: pass
            # full f2 rows = arms_f2 lines' subjects x arms
            fl = [l.split("\t") for l in open(os.path.join(full, "arms_f2.tsv")).read().splitlines() if l and not l.startswith("#")]
            frows = sum(len(l[3].split(",")) for l in fl)
            f2_full = w / max(1, rows_dry) * frows; perf_note = "measured %.1f s/row x %d rows" % (w / max(1, rows_dry), frows)
    # ---- the table
    spec = {"F1": ("items 1+2 (F1 part)", 56.1 + 5.2 * 0.6), "F3": ("items 1+2 (F3 part)", 0), "OB": ("items 3+4", 13.5 + 2.4), "TRIG": ("item 8 (optional)", 2.0)}
    print(f"{'phase':6} {'groups':>6} {'launches':>9} {'est min':>8}  basis")
    req = 0.0; opt = 0.0
    for ph in ("F1", "F3", "OB", "TRIG"):
        if ph not in tab: continue
        g, l, s, why = tab[ph]
        print(f"{ph:6} {g:6d} {l:9.0f} {s / 60:8.1f}  {dict(why)}")
        if ph == "TRIG": opt += s
        else: req += s
    print(f"{'BUILD':6} {'':6} {'':9} {(dry_build + max(0, gen_full - dry_gen_s)) / 60:8.1f}  dry build {dry_build:.0f} s + generator {gen_full:.0f} s ({fbytes / 2**20:.0f} MiB at {dry_gen_s}s/{dry_gen_b / 2**20:.1f} MiB)")
    req += dry_build + max(0, gen_full - dry_gen_s)
    print(f"{'CHECK':6} {'':6} {'':9} {check_full / 60:8.1f}  dry check {dry_check:.0f} s x {ratio:.1f} (arms x bytes ratio, an assumption)")
    req += check_full
    print(f"{'PERF':6} {'':6} {'':9} {f2_full / 60:8.1f}  {perf_note}")
    opt += f2_full
    print(f"spec: required 88 min, with optional 96 min")
    print(f"ESTIMATE required={req / 60:.0f} min with-optional={(req + opt) / 60:.0f} min (+ quiet-gate waits; spec 88 / 96)")

if __name__ == "__main__":
    main(sys.argv[1])
