#!/usr/bin/env python3
"""[DEC-FALLBACK] rev 2: read reach_<variant>_<arm>.jsonl (reach.py) and
  (1) count every T1/T2/T3/T4 row's reach per variant x arm, T1 per arrival
      LABEL and T2 per SCOPE (the CR the admission saw), with one witness;
  (2) check the design's tables against the probes and stamps, computed HERE
      from the rev-2 row lists, which share no code with src/:
        T2  verdict == the probed fit.prefilter on EVERY attempt, and the
            listing cell == `--emit-ir`'s prefilter value on the final one;
        T3  PFLW == the probed prefilter_lang_why on every gate;
        T1  the row the design's walk takes == the probed branch;
        attribution walk == the stamped ENGINE_SEL;
        COMPILE_MAX_ATTEMPTS: max attempts observed <= 25; no non-trial T1
        row fires twice in one compile (rev 2 §1.9).
Writes reach.tsv (the table) and prints a summary plus every mismatch.
usage: analyse.py SCRATCH OUT_DIR
"""
import collections, glob, json, os, re, sys

T1 = ["forcing", "nomem", "size-term-trial", "sel1-collapse", "sel1-drop",
      "unroll-rescue", "prefilter-collapse", "drop-anchored", "drop-premul",
      "drop-prefilter", "refuse"]
T2 = ["backref", "linked-call", "var-nullable", "nullable-exact", "nullable-collapsed",
      "overflow-drop", "forced-on", "forced-off", "var", "default-on", "default-off"]
T3 = ["rung-sizecap", "rung-sel1", "forced", "nullable", "exact", "no-rep"]
T4 = ["option", "denied", "default", "cap-rescue", "size-model", "capacity-declined",
      "size-model-declined"]
PFLW = {0: "exact", 1: "no-rep", 2: "nullable", 3: "forced", 4: "sel1", 5: "sizecap"}

def kv(s):
    return {a: int(b) for a, b in re.findall(r"(\w+)=(-?\d+)", s)}

def parse(pr):
    """-> attempts: [{hdr, adm, gate, fail, take}] in order."""
    atts, cur = [], None
    for p in pr:
        if p.startswith("att="):
            cur = {"hdr": kv(p), "adm": None, "gate": None, "fail": None, "take": None}
            atts.append(cur)
        elif cur is None:
            continue
        elif p.startswith("adm "):
            cur["adm"] = kv(p)
        elif p.startswith("gate "):
            cur["gate"] = kv(p)
        elif p.startswith("fail "):
            cur["fail"] = kv(p)
        elif p in ("forcing", "nomem", "trial"):
            cur["take"] = {"forcing": "forcing", "nomem": "nomem", "trial": "size-term-trial"}[p]
        elif p.startswith("sel1 "):
            d = kv(p)
            cur["take"] = "sel1-collapse" if d["collapse"] else "sel1-drop"
        elif p.startswith("rung="):
            cur["take"] = p[5:]
    return atts

def labels(f):
    s = []
    if f["nomem"]: s.append("nomem")
    if f["ovf"]: s.append("overflow")
    if f["scr"]: s.append("size")
    return "|".join(s) if s else "other"

def t2_row(a, fpc):
    """rev 2's T2, in order: -> (row, verdict, listing)."""
    yes = "yes-collapsed" if fpc else "yes"
    if a["bref"]: return "backref", 0, "no-backreference"
    if a["call"]: return "linked-call", 0, "no-linked-call"
    if a["cr"] == 0 and not a["dd"] and a["wp"] and a["var"] and a["nul"] and not a["fon"]:
        return "var-nullable", 0, "no-nullable-exact"
    if a["cr"] == 0 and not a["dd"] and a["wp"] and a["ea"] and not a["fon"]:
        return "nullable-exact", 0, "no-nullable-exact"
    if a["cr"] != 0 and a["ea"] and a["crep"] and not a["fon"]:
        return "nullable-collapsed", 0, "no-nullable-collapsed"
    if a["dd"] and (a["cr"] != 1 or a["foff"]):
        return "overflow-drop", 0, "no-dfa-overflow"
    if a["fon"]: return "forced-on", 1, yes
    if a["foff"]: return "forced-off", 0, "no-fno-prefilter"
    if a["var"]: return "var", 0, "no-engine-vm"
    if a["wp"]: return "default-on", 1, yes
    return "default-off", 0, "no-engine-vm"

T2_ESEL = {"var-nullable": "declined-nullable-default", "nullable-exact": "declined-nullable-default",
           "nullable-collapsed": "declined-nullable"}

def t3_row(g, cr, fpf):
    if g["wanted"] and (fpf or not g["nul"]):
        if cr == 2: return "rung-sizecap", 5
        if cr == 1: return "rung-sel1", 4
        return "forced", 3
    if g["wanted"]: return "nullable", 2
    if g["rep"]: return "exact", 0
    return "no-rep", 1

# T1 esel cells {kept, off}; None = PASS (rev 2 §1.2/§1.7: the walk goes on
# to the previous fired attributing row). "ROLE" = overflowed-{role}.
ESEL = {"sel1-collapse": ("collapsed-prefilter", "ROLE"), "sel1-drop": ("ROLE", "ROLE"),
        "prefilter-collapse": ("size-cap-retry", None), "drop-anchored": ("size-cap-retry",) * 2,
        "drop-premul": ("size-cap-retry",) * 2, "drop-prefilter": ("size-cap-retry",) * 2}

def attribution(arm, eng, atts, final_pf, role_dfa):
    if arm in ("vm", "dfa") or eng not in ("", "auto"):
        return "forced"
    fa = atts[-1]["adm"]
    if fa is not None:
        r = t2_row(fa, 0)[0]
        if r in T2_ESEL: return T2_ESEL[r]
    for a in reversed(atts[:-1]):
        t = a["take"]
        if t in ESEL:
            c = ESEL[t][0 if final_pf else 1]
            if c is None: continue
            return ("overflowed-dfa" if role_dfa else "overflowed-prefilter") if c == "ROLE" else c
    return "selected"

def main():
    scratch, outdir = sys.argv[1:3]
    reach = collections.Counter()
    wit = {}
    mism = collections.Counter(); mism_ex = {}
    maxatt = 0; twice = collections.Counter()
    sequences = collections.Counter()
    variants = set()
    inv = collections.Counter()           # rev 2 §1.9's run-time invariants
    waste = collections.Counter()         # [DEC-COLLAPSE-WASTE]'s three-way split
    for path in sorted(glob.glob(os.path.join(scratch, "reach_*_*.jsonl"))):
        v, arm = os.path.basename(path)[6:-6].split("_", 1)
        variants.add((v, arm))
        for ln in open(path):
            r = json.loads(ln)
            if r["status"] == "TIMEOUT":
                mism["TIMEOUT"] += 1; continue
            atts = parse(r["pr"])
            if not atts:
                continue
            maxatt = max(maxatt, len(atts))
            fpf = arm == "pf"
            role_dfa = None
            fired = collections.Counter()
            seq = []
            def hit(table, row, scope, c=1):
                k = (table, row, scope, v, arm)
                reach[k] += c
                if k not in wit:
                    wit[k] = (r["src"], r["key"][0][:90], r["key"][1], r["key"][3])
            def miss(kind, detail):
                mism[kind] += 1
                mism_ex.setdefault(kind, (v, arm, r["src"], r["key"][0][:80], detail))
            for i, a in enumerate(atts):
                if a["adm"] is not None and a["adm"]["var"]:
                    inv["has_var admissions"] += 1
                    inv["has_var with CR!=NONE or dd (must be 0)"] += bool(a["adm"]["cr"] or a["adm"]["dd"])
                cr = a["hdr"]["cr"]
                if cr and a["adm"] is not None and a["adm"]["dn"] and arm == "base":
                    waste[(v, {1: "SEL1", 2: "SIZECAP"}[cr], "(iii) empty_admits: designed decline")] += 1
                if cr and a["gate"] is not None and a["adm"] is not None and a["adm"]["pf"] and arm == "base":
                    g = a["gate"]
                    cls = ("(i) no collapsible repeat" if not g["rep"] else
                           "(ii) nullable, not empty_admits" if (g["wanted"] and g["nul"] and not g["collapse"]) else
                           "collapsed")
                    waste[(v, {1: "SEL1", 2: "SIZECAP"}[cr], cls)] += 1
                if a["adm"] is not None:
                    gcol = a["gate"]["collapse"] if a["gate"] else 0
                    row, verdict, lst = t2_row(a["adm"], gcol)
                    scope = {0: "NONE", 1: "SEL1", 2: "SIZECAP"}[a["adm"]["cr"]]
                    hit("T2", row, scope)
                    if verdict != a["adm"]["pf"]:
                        miss("T2-verdict", (row, a["adm"]))
                    if i == len(atts) - 1 and "ir_pf" in r and not r["ir_pf"].startswith("<"):
                        if lst != r["ir_pf"]:
                            miss("T2-listing", (row, lst, r["ir_pf"]))
                if a["gate"] is not None:
                    trow, tv = t3_row(a["gate"], a["hdr"]["cr"], fpf)
                    hit("T3", trow, "-")
                    if tv != a["gate"]["pflw"]:
                        miss("T3-pflw", (trow, a["gate"]))
                f = a["fail"]
                if f is not None:
                    lab = labels(f)
                    take = a["take"] or "refuse?"
                    if take in ("sel1-collapse", "sel1-drop") and role_dfa is None:
                        role_dfa = f["chosen"] == 1
                    hit("T1", take, lab)
                    seq.append(take)
                    if take not in ("size-term-trial", "forcing", "refuse"):
                        fired[take] += 1
                    # the design's walk, from the labels and state alone
                    want = None
                    if f["forcing"]: want = "forcing"
                    elif f["nomem"]: want = "nomem"
                    elif f["stph"] == 1: want = "size-term-trial"
                    if want and want != take:
                        miss("T1-walk", (want, take, f))
            sel = [k for k, t in enumerate(seq) if t in ("sel1-collapse", "sel1-drop")]
            if sel:
                around = seq[:sel[0]] + seq[sel[-1] + 1:]
                inv["compiles with a [SEL-1] row"] += 1
                inv["... with a size row before/after it (must be 0 off F-B3)"] += any(
                    t not in ("refuse", "size-term-trial") for t in around)
            if r["status"] == "ok" and seq and seq[-1] == "sel1-drop":
                inv["compiles ending on sel1-drop"] += 1
                inv["... whose final prefilter survived (must be 0)"] += r["st"].get("VM_PREFILTER") == "hybrid"
            for t, n in fired.items():
                if n > 1:
                    twice[t] += 1
            sequences[(v, arm, " > ".join(seq) or "-", r["status"])] += 1
            if r["status"] == "ok":
                if r["st"].get("UNROLL_K_WHY"):
                    hit("T4", r["st"]["UNROLL_K_WHY"], "-")
                es = r["st"].get("ENGINE_SEL")
                fpfin = r["st"].get("VM_PREFILTER") == "hybrid"
                if es:
                    got = attribution(arm, r["key"][4], atts, fpfin, bool(role_dfa))
                    if got != es:
                        miss("attribution", (got, es, seq))
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "reach.tsv"), "w") as o:
        o.write("table\trow\tscope\tvariant\tarm\tn\twitness_src\twitness_pattern\tflags\tencoding\n")
        for k in sorted(reach):
            w = wit[k]
            o.write("\t".join([k[0], k[1], k[2], k[3], k[4], str(reach[k]), w[0], w[1], w[2], w[3]]) + "\n")
    with open(os.path.join(outdir, "sequences.tsv"), "w") as o:
        o.write("variant\tarm\tsequence\tstatus\tn\n")
        for k in sorted(sequences):
            if k[2] != "-":
                o.write("\t".join(k) + "\t%d\n" % sequences[k])
    print("variant x arm files:", len(variants))
    print("max attempts observed:", maxatt, "(COMPILE_MAX_ATTEMPTS 25)")
    print("non-trial T1 rows fired twice in one compile:", dict(twice) or "none")
    print("mismatches:", dict(mism) or "none")
    print("run-time invariants (rev 2 §1.9):")
    for k in ("has_var admissions", "has_var with CR!=NONE or dd (must be 0)", "compiles ending on sel1-drop",
              "... whose final prefilter survived (must be 0)", "compiles with a [SEL-1] row",
              "... with a size row before/after it (must be 0 off F-B3)"):
        print("  %-58s %d" % (k, inv[k]))
    print("[DEC-COLLAPSE-WASTE] rung attempts by class, base arm (rung attempt that kept a prefilter, or the designed decline):")
    for k in sorted(waste):
        print("  %-8s %-8s %-40s %d" % (k[0], k[1], k[2], waste[k]))
    for k, e in mism_ex.items():
        print("  first", k, e)
    # rows with zero reach anywhere
    allrows = [("T1", r) for r in T1] + [("T2", r) for r in T2] + [("T3", r) for r in T3] + [("T4", r) for r in T4]
    tot = collections.Counter()
    for k, n in reach.items():
        tot[(k[0], k[1])] += n
    print("rows never reached in any variant x arm:", [r for r in allrows if tot[r] == 0])

main()
