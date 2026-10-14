#!/usr/bin/env python3 -I
"""armread fit.py RAW_TSV : per-engine C_call / c_byte / C_match from the slot's raw EXT launches.
Reads only raw_EXT.tsv (5 launches/arm). Prints the tables used in armread_report.md."""
import sys, csv, statistics as st
raw = {}
for r in csv.DictReader(open(sys.argv[1]), delimiter="\t"):
    base = r["arm"].endswith("#b")
    raw.setdefault((r["cell"], r["arm"], r["subject"]), []).append(float(r["ns"]))
med = lambda k: st.median(raw[k])
N = {"pc_e0": 0, "pc_nm8": 8, "pc_nm64": 64, "pc_nm1k": 1024, "pc_nm64k": 65536}
M = {"pc_mw2-L8": 8192, "pc_mw2-L64": 1024, "pc_mw2-L1k": 64,
     "pc_mw5-L8": 8192, "pc_mw5-L64": 1024, "pc_mw5-L1k": 64}
def wls(x, y, w):
    sw = sum(w); mx = sum(a*b for a, b in zip(w, x))/sw; my = sum(a*b for a, b in zip(w, y))/sw
    sxx = sum(a*(b-mx)**2 for a, b in zip(w, x)); sxy = sum(a*(b-mx)*(c-my) for a, b, c in zip(w, x, y))
    s = sxy/sxx; return my - s*mx, s
cells = [("p1", "dfa"), ("p1", "vm"), ("p2", "hyb"), ("p2", "dfa"), ("p2", "vm"), ("p3", "dfa"), ("p3", "vm")]
subs_all = {"p1": "pc_mw2-L", "p2": "pc_mw2-L", "p3": "pc_mw5-L"}
out = {}
for p, arm in cells:
    fk = lambda s, i=0: (p+"-first", arm, s)
    ys = [med(fk(s)) for s in N]; xs = list(N.values())
    print(f"\n=== {p} {arm}  first-mode medians (ns): " + " ".join(f"n={x}:{y:.2f}" for x, y in zip(xs, ys)))
    fits = {}
    fits["W5 (w=1/y^2, 5 pts)"] = wls(xs, ys, [1/y**2 for y in ys])
    fits["U5 (unweighted, 5 pts)"] = wls(xs, ys, [1]*5)
    fits["U4 (n<=1024, 4 pts)"] = wls(xs[:4], ys[:4], [1]*4)
    fits["W4 (n>=8, rel-w, 4 pts)"] = wls(xs[1:], ys[1:], [1/y**2 for y in ys[1:]])
    for nm, (a, b) in fits.items():
        res = [y-(a+b*x) for x, y in zip(xs, ys)]
        print(f"  {nm:26s} C={a:7.3f} c={b:.5f}  resid(ns) " + " ".join(f"{r:+.2f}" for r in res))
    # per-launch (5 launches) of W5
    pl = []
    for i in range(5):
        yy = [raw[fk(s)][i] for s in N]
        pl.append(wls(xs, yy, [1/y**2 for y in yy]))
    print(f"  W5 per-launch C {min(a for a,b in pl):.3f}..{max(a for a,b in pl):.3f}  c {min(b for a,b in pl):.5f}..{max(b for a,b in pl):.5f}")
    # A/A for base arm
    if (p+"-first", arm+"#b", "pc_nm64k") in raw:
        aa = [abs(med((p+"-first", arm+"#b", s))-med(fk(s))) for s in N]
        print("  A/A |#b-base| first (ns) " + " ".join(f"{a:.2f}" for a in aa))
    C0 = ys[0]; c = (ys[4]-ys[3])/(65536-1024)  # local slope 1Ki->64Ki
    ceff = (ys[4]-C0)/65536
    out[(p, arm)] = dict(C_e0=C0, C_fit=fits["W5 (w=1/y^2, 5 pts)"][0], C_w4=fits["W4 (n>=8, rel-w, 4 pts)"][0],
                         c_fit=fits["W5 (w=1/y^2, 5 pts)"][1], c_hi=c, ceff=ceff, t64k=ys[4])
    # find-all
    mk = [(s, m) for s, m in M.items() if s.startswith(subs_all[p])]
    mk.sort(key=lambda t: t[1])
    ms = [m for s, m in mk]; ts = [med((p+"-all", arm, s)) for s, m in mk]
    print(f"  find-all medians (ns/pass): " + " ".join(f"m={m}:{t:.1f}" for m, t in zip(ms, ts)))
    s_lo = (ts[1]-ts[0])/(ms[1]-ms[0]); s_hi = (ts[2]-ts[1])/(ms[2]-ms[1])
    print(f"  all-row slope per match (ns/match, = C_call+C_match): m64->1024 {s_lo:.3f}  m1024->8192 {s_hi:.3f}; intercept(m=64,1024 line) {ts[0]-ms[0]*s_lo:.1f} vs first nm64k {ys[4]:.1f}")
    # difference method: C_match = (T_all - T_nm64k)/m - C_call
    for Cname in ("C_e0", "C_fit"):
        Cc = out[(p, arm)][Cname]
        vals = [(t-ys[4])/m - Cc for t, m in zip(ts, ms)]
        # per-launch spread
        lo, hi = [], []
        for (s, m) in mk:
            L = [(raw[(p+"-all", arm, s)][i]-raw[fk("pc_nm64k")][i])/m for i in range(5)]
            lo.append(min(L)-Cc); hi.append(max(L)-Cc)
        print(f"  C_match via {Cname}={Cc:.2f}: " + " ".join(f"m={m}:{v:.3f}[{a:.3f}..{b:.3f}]" for m, v, a, b in zip(ms, vals, lo, hi)))
    out[(p, arm)]["cm"] = {m: (t-ys[4])/m - out[(p, arm)]["C_e0"] for t, m in zip(ts, ms)}
    out[(p, arm)]["slope"] = {m: (t-ys[4])/m for t, m in zip(ts, ms)}
    # all-mode A/A
    if (p+"-all", arm+"#b", mk[0][0]) in raw:
        print("  A/A |#b-base| all (ns/pass) " + " ".join(f"{abs(med((p+'-all', arm+'#b', s))-med((p+'-all', arm, s))):.2f}" for s, m in mk))
print("\n=== crossovers (C_e0 / ceff):")
for k, v in out.items():
    print(k, f"L*(C_e0/ceff)={v['C_e0']/v['ceff']:.1f}B  L*(C_fit/c_fit)={v['C_fit']/v['c_fit']:.1f}B  ceff={v['ceff']:.5f}",
          "g*=" + " ".join(f"{m}:{c/v['ceff']:.1f}B" for m, c in v["cm"].items()))
print("\n=== e0-anchored line  T(n)=C_e0+ceff*n, ceff=(T64k-C_e0)/65536 ; residual measured-line at n=8,64,1024; local slopes")
for (p, arm), v in out.items():
    ys = [med((p+"-first", arm, s)) for s in N]
    r = [ys[i]-(v["C_e0"]+v["ceff"]*x) for i, x in ((1, 8), (2, 64), (3, 1024))]
    sl = [(ys[i+1]-ys[i])/(x1-x0) for i, (x0, x1) in enumerate(zip(list(N.values())[:-1], list(N.values())[1:]))]
    print(p, arm, f"C_e0={v['C_e0']:.2f} ceff={v['ceff']:.5f} resid8/64/1k=" + "/".join(f"{x:+.2f}" for x in r),
          "segment slopes 0-8,8-64,64-1k,1k-64k=" + " ".join(f"{s:.4f}" for s in sl))
