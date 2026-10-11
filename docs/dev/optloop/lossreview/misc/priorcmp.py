#!/usr/bin/env python3
"""lossreview/misc: today vs prior-variant counted work, priced by fit.py's
coefficients (the bench box's, implied by pcrec's own counted work).

    priorcmp.py FITOUT.txt RES_today.tsv RES_variant.tsv [RES_variant2.tsv ...]   (RES = run_pop_mc.py output)

Prints per utf8 throughput cell: modelled ns today and under each variant,
the ratio, and the variant's scan stamps (REQ_BYTE, REQ_RUN, OFFSETS)."""
import csv, sys, re, collections
coef = {}
for l in open(sys.argv[1]):
    m = re.match(r"\s+(\w+)\s+([0-9.]+) ns", l)
    if m: coef[m.group(1)] = float(m.group(2))
def load(path):
    a = collections.OrderedDict(); st = {}
    for r in csv.DictReader(open(path), delimiter="\t"):
        if r["config"] != "default" or r["regime"] != "throughput" or not r.get("n"): continue
        k = r["pid"]; c = a.setdefault(k, collections.Counter())
        for x in ["calls", "mc", "mcmp", "T_scan", "T_fwd", "T_rev", "T_vm", "T_anc", "T_pre", "T_skip", "T_endw", "T_misc", "T_unk"]: c[x] += int(r.get(x) or 0)
        st[k] = (r["REQ_BYTE"], r["REQ_RUN"], r.get("DFA_PREFILTER", ""), r.get("DFA_PREFILTER_OFFSETS", "") if "DFA_PREFILTER_OFFSETS" in r else "")
    return a, st
def price(c):
    step = c["T_fwd"] + c["T_rev"] + c["T_vm"] + c["T_anc"]
    skip = max(0, c["T_pre"] + c["T_skip"] + c["T_endw"] + c["T_misc"] + c["T_unk"] - c["T_scan"])
    return (coef["calls"] * c["calls"] + coef["memchr"] * c["mc"] + coef["memcmp"] * c["mcmp"] + coef["scan_B"] * c["T_scan"]
            + coef["step_B"] * step + coef["skip_B"] * skip)
base, bst = load(sys.argv[2])
vars_ = [(p, load(p)) for p in sys.argv[3:]]
print("cell\ttoday_us\t" + "\t".join("%s_us\tx" % p.split("_")[-1].split(".")[0] for p, _ in vars_) + "\tstamps_today\t" + "\t".join("stamps_" + p.split("_")[-1].split(".")[0] for p, _ in vars_))
for k, c in base.items():
    t = price(c)
    row = [k, "%.0f" % (t / 1000)]
    for p, (a, st) in vars_:
        v = price(a[k]); row += ["%.0f" % (v / 1000), "%.2f" % (v / t if t else 0)]
    row.append("/".join(bst[k][:2]) + " " + bst[k][2])
    for p, (a, st) in vars_: row.append("/".join(st[k][:2]) + " " + st[k][2])
    print("\t".join(row))
