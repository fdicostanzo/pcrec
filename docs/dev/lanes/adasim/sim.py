"""adasim/sim.py -- count-only simulation of an adaptive per-64-byte-stretch WALK/M64 choice, priced from fit.py's model.
The real member mask of every stretch (feat.py) drives the rule; a mode's cost is the model's delta to the walk
(fit.py); ADAPTIVE = walk_measured + sum over M-mode stretches of delta + S*switches + bk*W-stretches (+ probe cost).
Rule (3 thresholds a, b, h; decision for stretch s from stretch s-1's transitions t): enter/stay M when t <= a
(sparse or empty) or t >= b (random-dense); leave M for W only when a+h < t < b-h (the regular-dense band);
W stays W otherwise. A call (rx_search) starts cold in W unless CARRY. usage: sim.py MODEL.json OUTDIR"""
import sys, json, itertools, os
sys.path.insert(0, "/home/pcrec/projects/pcrec/worktrees/flat/docs/dev/lanes/adasim")
from common import *
from multiprocessing import Pool

MODEL = None
OB = 2.0                       # ns per NON-EMPTY M-mode stretch to read the rule's inputs (popcount of m^(m>>1) / of m; an empty stretch is the loop test, free); varied 0..6
S_DEF, BK_DEF = 3.0, 0.3     # ns per mode switch (varied 0..10), ns per W-mode stretch of stop-counter bookkeeping


def delta(k, q):
    b, c, d = MODEL["M64"]
    return b * (k == 0) + c * k + d * q


def call_starts(nst, ncalls):
    if ncalls >= nst:
        return np.arange(nst)
    return np.unique((np.arange(ncalls) * nst) // ncalls)


def modes(t, a, b, h, starts, carry):
    """bool array: True = M for stretch s, from stretch s-1's t. Vectorised (exact t seen in either mode)."""
    n = len(t)
    sig = np.zeros(n, np.int8)
    tp = t[:-1]
    sig[1:] = np.where((tp <= a) | (tp >= b), 1, np.where((tp > a + h) & (tp < b - h), -1, 0))
    sig[0] = -1
    if not carry:
        sig[starts] = -1
    idx = np.where(sig != 0, np.arange(n), -1)
    idx = np.maximum.accumulate(idx)
    return sig[idx] > 0


def modes_sig(enter, leave, starts, carry):
    """mode array from per-stretch ENTER/LEAVE signals computed on the previous stretch (forward-fill the last signal)."""
    n = len(enter)
    sig = np.zeros(n, np.int8)
    sig[1:] = np.where(enter[:-1], 1, np.where(leave[:-1], -1, 0))
    sig[0] = -1
    if not carry:
        sig[starts] = -1
    idx = np.maximum.accumulate(np.where(sig != 0, np.arange(n), -1))
    return sig[idx] > 0


def modes_r2(k, t, kc, b, h, starts, carry):
    """R2 (dense-aware variant, observes k in both modes): M when the previous stretch had <= kc members or t >= b;
    back to W only when it had > kc+h members AND t < b-h."""
    return modes_sig((k <= kc) | (t >= b), (k > kc + h) & (t < b - h), starts, carry)


def modes_loop(t, a, b, h, starts, carry, rho=1.0, N=0):
    """the same rule with the walk-mode observation degraded: in W the walk sees only its stop count
    (stops = ceil(rho * runs), runs = (t+1)//2, so t_est = 2*stops) and, every N-th stretch, an exact mask sample.
    Returns (mode array, number of samples taken)."""
    n = len(t); out = np.zeros(n, bool); st = False; ns = 0
    cs = set(starts.tolist()); tl = t.tolist(); prev = None
    for s in range(n):
        if s == 0 or (not carry and s in cs):
            st = False; prev = None
        elif prev is not None:
            sample = (not st) and N > 0 and s % N == 0
            if sample:
                ns += 1
            tv = prev if (st or sample or rho >= 1.0) else 2 * int(np.ceil(rho * ((prev + 1) // 2)))
            if tv <= a or tv >= b:
                st = True
            elif a + h < tv < b - h:
                st = False
        out[s] = st; prev = tl[s]
    return out, ns


def price(dl, md, S, bk, probes=0, probe_ns=0.0, ne=None):
    sw = int((md[1:] != md[:-1]).sum())
    return float(dl[md].sum()) + S * sw + bk * float((~md).sum()) + OB * float((md & ne).sum() if ne is not None else md.sum()) + probe_ns * probes, sw, int(md.sum())


def load_cells():
    """[(cell, subj, walk_ns, floor_ns, meas dict, ncalls, nst, role)] -- role fit | hold | anchor | skip."""
    have = subjects(); ft = flat_table(); e8 = e8_table(); fl = {c for c, _ in ft if not c.startswith("an-")}
    out = []
    for (c, s), d in ft.items():
        if c.startswith("an-"):
            continue
        sub = resolve(have, c, s)
        out.append(dict(cell=c, subj=sub, walk=d["walk"], floor=d["walk"] * d["floor"] / 100, meas={"V1": d["V1"], "M64": d["M64"]},
                        calls=e8[(c, sub)]["matches"] + 1, role="fit"))
    for (c, s), v in e8.items():
        if c in fl:
            continue
        sub = resolve(have, c, s)
        out.append(dict(cell=c, subj=sub, walk=v["walk"], floor=v["floor"], meas={"V1": v["V1"]}, calls=v["matches"] + 1, role="hold"))
    for d in out:
        k, t, q = feats(d["cell"], d["subj"]); d.update(k=k, t=t, q=q, nst=len(k), dl=delta(k, q))
        d["raw_dl"] = d["dl"]
        if d["role"] == "fit":     # CALIBRATED: spread the model's miss on measured ALWAYS-M64 evenly over the stretches
            d["dl"] = d["dl"] + ((d["meas"]["M64"] - d["walk"]) - d["dl"].sum()) / d["nst"]
        if d["role"] == "hold" and d["walk"] / d["nst"] < 4.0:
            d["role"] = "skip"
        if d["role"] in ("hold", "fit"):     # V1-CALIBRATED: shift M64's per-stretch delta by V1's measured miss (V1 stands in for M64)
            v1raw = MODEL["V1"][0] * (d["k"] == 0) + MODEL["V1"][1] * d["k"] + MODEL["V1"][2] * d["q"]
            d["raw_v1"] = v1raw
            d["dl_v1cal"] = d["raw_dl"] + ((d["meas"]["V1"] - d["walk"]) - v1raw.sum()) / d["nst"]
    return out


def evaluate(cells, a, b, h, S=S_DEF, bk=BK_DEF, carry=False, loop=None):
    res = []
    for d in cells:
        st = call_starts(d["nst"], d["calls"])
        if loop:
            md, ns = modes_loop(d["t"], a, b, h, st, carry, **loop); pr = (ns, loop.get("pns", 0.0))
        else:
            md = modes(d["t"], a, b, h, st, carry); pr = (0, 0.0)
        cost, sw, nm = price(d["dl"], md, S, bk, *pr, ne=d["k"] > 0)
        res.append((cost, sw, nm))
    return res


def _fitjob(args):
    cells, a, b, h = args
    r = evaluate(cells, a, b, h, carry=True)
    x = np.array([c / d["walk"] for (c, _, _), d in zip(r, cells)])
    return (a, b, h, float(x.mean() + np.maximum(x, 0).mean()), float(x.max()))   # losses count twice


CLASS = {"L": "logs", "P": "prose", "C": "code", "N": "non-English", "B": "binary", "S": "structured", "a": "anchors"}
THR = (1, 31, 8)     # a, b, h: the middle of the grid's near-ties (see report); verified against the grid in main()


def add_anchors(cells):
    G = flat_table()
    spec = {"an-dig": ("g2-dig-n64k-g8-L1k-reg-S", 1024), "an-dfa-hat": ("g2-dfa-hat-n64k-ginf-L32-S", 32)}
    for c, (sub, L) in spec.items():
        d0 = G[(c, sub)]
        k, t, q = feats(c, sub)
        sc = len(k) / 1024.0          # the table's ns is ns/pass = ONE 64 KiB buffer (1024 stretches); features cover 64 buffers
        d = dict(cell=c, subj=sub, walk=d0["walk"] * sc, floor=d0["walk"] * d0["floor"] / 100 * sc, meas={"V1": d0["V1"] * sc, "M64": d0["M64"] * sc},
                 calls=(len(k) * 64) // L, role="anchor", k=k, t=t, q=q, nst=len(k))
        d["raw_dl"] = delta(k, q)
        d["dl"] = d["raw_dl"] + ((d["meas"]["M64"] - d["walk"]) - d["raw_dl"].sum()) / d["nst"]
        cells.append(d)


def row(d, thr, S, bk, carry, key="dl", rule=1):
    a, b, h = thr
    st = call_starts(d["nst"], d["calls"])
    md = modes(d["t"], a, b, h, st, carry) if rule == 1 else modes_r2(d["k"], d["t"], a, b, h, st, carry)
    dl = d[key]
    cost, sw, nm = price(dl, md, S, bk, ne=d["k"] > 0)
    orc = float(np.minimum(dl, 0).sum())
    return dict(adapt=d["walk"] + cost, sw=sw, mshare=nm / d["nst"], oracle=d["walk"] + orc, m64=d["walk"] + float(dl.sum()))


def summarize(cells, rows):
    """aggregate over a list of cells: dict of the report's headline numbers."""
    w = np.array([d["walk"] for d in cells]); fl = np.array([d["floor"] for d in cells])
    ad = np.array([r["adapt"] for r in rows]); m6 = np.array([r["m64"] for r in rows]); orc = np.array([r["oracle"] for r in rows])
    loss = ad - w > fl; m6loss = m6 - w > fl
    win = (w - m6) > fl
    kept = float(np.maximum(w - ad, 0)[win].sum() / (w - m6)[win].sum()) if win.any() else float("nan")
    ora = float((w - ad).sum() / (w - orc).sum()) if (w - orc).sum() > 1e-6 * w.sum() else float('nan')
    rel = (ad - w) / w; worst = int(np.argmax(rel))
    return dict(n=len(cells), tot_adapt=100 * (ad.sum() / w.sum() - 1), tot_m64=100 * (m6.sum() / w.sum() - 1), tot_orc=100 * (orc.sum() / w.sum() - 1),
                mean_adapt=100 * float(rel.mean()), mean_m64=100 * float(((m6 - w) / w).mean()), mean_orc=100 * float(((orc - w) / w).mean()),
                loss=int(loss.sum()), m64loss=int(m6loss.sum()), l1=int(((ad - w) / w > 0.01).sum()), l5=int(((ad - w) / w > 0.05).sum()),
                m1=int(((m6 - w) / w > 0.01).sum()), m5=int(((m6 - w) / w > 0.05).sum()), kept=kept, oracle_share=ora,
                worst=100 * float(rel[worst]), worst_cell=cells[worst]["cell"] + " " + cells[worst]["subj"][-24:],
                worst_pct_over_floor=100 * float(np.max((ad - w - fl) / w)))


def fmt(sm):
    return ("n=%(n)d | total vs walk: ADAPT %(tot_adapt)+.1f%%  M64 %(tot_m64)+.1f%%  ORACLE %(tot_orc)+.1f%% | mean per cell: ADAPT %(mean_adapt)+.1f%%"
            "  M64 %(mean_m64)+.1f%%  ORACLE %(mean_orc)+.1f%% | losses>floor ADAPT %(loss)d, M64 %(m64loss)d; >1%% ADAPT %(l1)d, M64 %(m1)d; >5%% ADAPT %(l5)d, M64 %(m5)d | M64 wins kept %(kept).2f"
            " | oracle share %(oracle_share).2f | worst cell %(worst)+.1f%% (%(worst_cell)s)") % sm


def main():
    global MODEL
    mj = json.load(open(sys.argv[1])); od = sys.argv[2]; os.makedirs(od, exist_ok=True)
    MODEL = {arm: mj["forms"][f"{arm} A:[e,k,q]"]["coef"][1:] for arm in ("M64", "V1")}
    cells = load_cells(); add_anchors(cells)
    fitc = [d for d in cells if d["role"] in ("fit", "anchor")]
    j1fit = [d for d in cells if d["role"] == "fit"]
    hold = [d for d in cells if d["role"] == "hold"]
    skip = [d for d in cells if d["role"] == "skip"]
    # 1. threshold fit on flat's J1 cells (CARRY, calibrated costs, S=3, bk=0.3), losses counted twice
    grid = [(a, b, h) for a in range(0, 11) for b in range(16, 34) for h in range(0, 13) if a + h < b - h]
    with Pool(4) as p:
        r = p.map(_fitjob, [(j1fit, a, b, h) for a, b, h in grid], chunksize=8)
    r.sort(key=lambda z: z[3]); best = r[0][3]
    near = [z for z in r if z[3] < best + 0.003]
    print("grid: %d configs, best obj %.4f at a=%d b=%d h=%d; %d within 0.003: a in %s, b in %s, h in %s, leave-band lo in %s hi in %s" % (
        len(r), best, *r[0][:3], len(near), sorted({z[0] for z in near}), sorted({z[1] for z in near}), sorted({z[2] for z in near}),
        sorted({z[0] + z[2] for z in near}), sorted({z[1] - z[2] for z in near})))
    me = [z for z in r if z[:3] == THR][0]
    print("chosen %s: obj %.4f (rank %d of %d), worst fit-cell d/walk %+.3f" % (THR, me[3], r.index(me) + 1, len(r), me[4]))
    # 2. main tables
    def run(cs, thr=THR, S=S_DEF, bk=BK_DEF, carry=True, key="dl", rule=1):
        rows = [row(d, thr, S, bk, carry, key, rule) for d in cs]
        return rows, summarize(cs, rows)
    out = {}
    for name, cs in (("flat J1 (fit, calibrated)", j1fit), ("flat anchors", [d for d in cells if d["role"] == "anchor"]),
                     ("e8-only (hold-out, raw model)", hold)):
        for carry in (True, False):
            rows, sm = run(cs, carry=carry)
            print(("CARRY" if carry else "COLD ") + " " + name + ": " + fmt(sm)); out[(name, carry)] = rows
    for carry in (True, False):
        rows, sm = run(hold, carry=carry, key="dl_v1cal")
        print(("CARRY" if carry else "COLD ") + " e8-only (hold-out, V1-calibrated): " + fmt(sm)); out[("e8-only v1cal", carry)] = rows
    rows, sm = run(j1fit, carry=True, key="dl_v1cal")
    print("CARRY flat J1 with the V1-calibrated costs instead of the M64-calibrated: " + fmt(sm))
    err = np.array([abs(row(d, THR, 0, 0, True, "dl_v1cal")["m64"] - d["meas"]["M64"]) / d["walk"] for d in j1fit])
    print("V1-calibrated M64 total vs measured M64 on the 41 flat cells: |err| median %.3f p90 %.3f max %.3f (fraction of walk)" % (np.median(err), np.percentile(err, 90), err.max()))
    errr = np.array([abs(d["raw_dl"].sum() - (d["meas"]["M64"] - d["walk"])) / d["walk"] for d in j1fit])
    print("raw-model M64 total vs measured M64 on the 41 flat cells (in-sample): |err| median %.3f p90 %.3f max %.3f" % (np.median(errr), np.percentile(errr, 90), errr.max()))
    rows = out[("flat J1 (fit, calibrated)", True)]
    for d, rw in zip(j1fit, rows):
        print("  %-7s %-26s walk %10.0f M64 %+6.1f%% ADAPT %+6.1f%% ORACLE %+6.1f%% Mshare %.2f sw %5d floor %.2f%%" % (d["cell"], d["subj"][-26:], d["walk"], 100 * (rw["m64"] / d["walk"] - 1), 100 * (rw["adapt"] / d["walk"] - 1), 100 * (rw["oracle"] / d["walk"] - 1), rw["mshare"], rw["sw"], 100 * d["floor"] / d["walk"]))
    rows = out[("e8-only v1cal", True)]
    print("e8-only (V1-calibrated, CARRY) worst ADAPT cells (V1 measured, V1 model, ADAPT, M64-proxy as % of walk):")
    for d, rw in sorted(zip(hold, rows), key=lambda z: -(z[1]["adapt"] / z[0]["walk"]))[:8]:
        print("  %-7s %-26s V1meas %+6.1f%% ADAPT %+6.1f%% M64proxy %+6.1f%% Mshare %.2f e=%.2f k=%.1f t=%.1f" % (d["cell"], d["subj"][-26:], 100 * (d["meas"]["V1"] / d["walk"] - 1),
              100 * (rw["adapt"] / d["walk"] - 1), 100 * (rw["m64"] / d["walk"] - 1), rw["mshare"], (d["k"] == 0).mean(), d["k"].mean(), d["t"].mean()))
    # R2: the dense-aware variant -- fit (kc, b, h) on the same cells, same objective, then the hold-out
    best2 = None
    for kc in range(0, 33, 2):
        for b in (27, 29, 31, 33):
            for h in (2, 4, 8, 12):
                rows = [row(d, (kc, b, h), S_DEF, BK_DEF, True, "dl", 2) for d in j1fit]
                x = np.array([(r["adapt"] - d["walk"]) / d["walk"] for r, d in zip(rows, j1fit)]); ob = float(x.mean() + np.maximum(x, 0).mean())
                if best2 is None or ob < best2[0]:
                    best2 = (ob, (kc, b, h))
    thr2 = best2[1]
    print("R2 grid best (kc, b, h) =", thr2, "obj %.4f (R1 chosen obj %.4f)" % (best2[0], me[3]))
    for name, cs, key in (("flat J1", j1fit, "dl"), ("e8-only V1-cal", hold, "dl_v1cal"), ("flat anchors", [d for d in cells if d["role"] == "anchor"], "dl")):
        for carry in (True, False):
            print(("CARRY" if carry else "COLD ") + " R2 " + name + ": " + fmt(run(cs, thr=thr2, carry=carry, key=key, rule=2)[1]))
    rows = run(hold, thr=thr2, key="dl_v1cal", rule=2)[0]
    print("R2 e8-only worst cells:", [(d["cell"], d["subj"][-14:], round(100 * (rw["adapt"] / d["walk"] - 1), 1)) for d, rw in sorted(zip(hold, rows), key=lambda z: -(z[1]["adapt"] / z[0]["walk"]))[:6]])
    cl = {}
    for d, rw in zip(j1fit, run(j1fit, thr=thr2, rule=2)[0]):
        c = CLASS[d["cell"][3]]; v = cl.setdefault(c, [0, 0.0]); v[0] += rw["sw"]; v[1] += d["nst"] * 64 / 2 ** 20
    print("R2 switches/MiB (flat J1):", "; ".join("%s %.1f" % (c, v[0] / v[1]) for c, v in sorted(cl.items())))
    global OB
    for ob in (0.0, 6.0):
        OB = ob
        print("ob=%.0f R1 fit: %s" % (ob, fmt(run(j1fit)[1])[:210]))
        print("       R1 hold: %s" % fmt(run(hold, key="dl_v1cal")[1])[:210])
        print("       R2 fit: %s" % fmt(run(j1fit, thr=thr2, rule=2)[1])[:210])
        print("       R2 hold: %s" % fmt(run(hold, thr=thr2, key="dl_v1cal", rule=2)[1])[:210])
    OB = 2.0
    for thr in [(0, 33, 12), (4, 33, 12), (8, 33, 12), (2, 33, 4), (2, 29, 12), (2, 33, 0)]:
        print("R2 thr=%s fit: %s" % (thr, fmt(run(j1fit, thr=thr, rule=2)[1])[:210]))
        print("             hold: %s" % fmt(run(hold, thr=thr, key="dl_v1cal", rule=2)[1])[:210])
    # measured best arm per cell (walk, V1, M64 where measured) vs ADAPT
    for name, cs in (("flat J1", j1fit), ("flat anchors", [d for d in cells if d["role"] == "anchor"]), ("e8-only", hold)):
        rows = out[({"flat J1": "flat J1 (fit, calibrated)", "e8-only": "e8-only v1cal"}.get(name, name), True)]
        rel = []; lose = 0
        for d, rw in zip(cs, rows):
            bestm = min([d["walk"]] + list(d["meas"].values())); rel.append(rw["adapt"] / bestm - 1); lose += rw["adapt"] / bestm - 1 > d["floor"] / d["walk"]
        rel = np.array(rel)
        print("CARRY %s: ADAPT vs measured-best-arm per cell: mean %+.1f%% median %+.1f%% worst %+.1f%%; cells >floor above best-arm: %d of %d" % (
            name, 100 * rel.mean(), 100 * np.median(rel), 100 * rel.max(), lose, len(cs)))
    # V1 / M64 measured loss counts (verdict-like: delta > A/A floor)
    for name, cs in (("flat J1", j1fit), ("flat anchors", [d for d in cells if d["role"] == "anchor"]), ("e8-only", hold)):
        for arm in ("V1", "M64"):
            ms = [d for d in cs if arm in d["meas"]]
            if ms:
                print("measured %s on %s: loses (> floor) in %d of %d cells; >1%% in %d; >5%% in %d" % (arm, name, sum(d["meas"][arm] - d["walk"] > d["floor"] for d in ms), len(ms),
                      sum((d["meas"][arm] - d["walk"]) / d["walk"] > 0.01 for d in ms), sum((d["meas"][arm] - d["walk"]) / d["walk"] > 0.05 for d in ms)))
    # 3. per-class switches per MiB and M share (CARRY and COLD)
    for carry in (True, False):
        cl = {}
        for cs_, key in ((j1fit, "flat J1"), (hold, "e8-only"), ([d for d in cells if d["role"] == "anchor"], "anchors")):
            for d, rw in zip(cs_, out[({"flat J1": "flat J1 (fit, calibrated)", "e8-only": "e8-only v1cal", "anchors": "flat anchors"}[key], carry)]):
                c = CLASS[d["cell"][3] if d["cell"].startswith("j1-") else "a"] + ("" if d["cell"].startswith("j1-") else " " + d["cell"])
                v = cl.setdefault(c, [0, 0.0, 0.0]); v[0] += rw["sw"]; v[1] += d["nst"] * 64 / 2 ** 20; v[2] += rw["mshare"] * d["nst"] * 64 / 2 ** 20
        print(("CARRY" if carry else "COLD ") + " switches/MiB (and M-mode share of bytes) by class: " + "; ".join(
            "%s %.1f (%.0f%%)" % (c, v[0] / v[1], 100 * v[2] / v[1]) for c, v in sorted(cl.items())))
    # 4. sensitivity (CARRY unless noted), J1 fit set + e8-only
    for S in (0, 1, 3, 5, 10):
        print("S=%-2d fit: %s" % (S, fmt(run(j1fit, S=S)[1])[:170]))
        print("      hold: %s" % fmt(run(hold, S=S, key="dl_v1cal")[1])[:170])
    for bk in (0.0, 1.0):
        print("bk=%.1f fit: %s" % (bk, fmt(run(j1fit, bk=bk)[1])[:170]))
    for thr in [(0, 31, 8), (2, 31, 8), (3, 31, 8), (1, 27, 8), (1, 33, 8), (1, 31, 5), (1, 31, 11), (1, 31, 3), (4, 28, 4), (6, 30, 6)]:
        print("thr=%s fit: %s" % (thr, fmt(run(j1fit, thr=thr)[1])[:190]))
        print("            hold: %s" % fmt(run(hold, thr=thr, key="dl_v1cal")[1])[:190])
    # 5. the same rule with the WALK-mode observation degraded (stop counts only, every Nth stretch a mask sample)
    ref = [d for d in j1fit if d["nst"] <= 120000]       # python loop: keep to the smaller subjects
    ok = True
    for d in ref[:6]:
        st = call_starts(d["nst"], d["calls"])
        ok &= bool((modes(d["t"], *THR, st, True) == modes_loop(d["t"], *THR, st, True)[0]).all())
    print("loop == vectorised on 6 cells:", ok)
    for lp in (dict(rho=1.0, N=0), dict(rho=0.5, N=0), dict(rho=0.5, N=16, pns=4.0), dict(rho=0.25, N=16, pns=4.0)):
        rows = []
        for d in ref:
            md, ns = modes_loop(d["t"], *THR, call_starts(d["nst"], d["calls"]), True, **{k: v for k, v in lp.items() if k != "pns"})
            cost, sw, nm = price(d["dl"], md, S_DEF, BK_DEF, ns, lp.get("pns", 0.0), ne=d["k"] > 0)
            rows.append(dict(adapt=d["walk"] + cost, m64=d["walk"] + float(d["dl"].sum()), oracle=d["walk"] + float(np.minimum(d["dl"], 0).sum()), sw=sw, mshare=nm / d["nst"]))
        print("walk-obs %s on %d cells (<=120k stretches): %s" % (lp, len(ref), fmt(summarize(ref, rows))[:200]))
    # 6. per-cell table
    with open(od + "/cells.tsv", "w") as f:
        f.write("role\tcell\tsubject\tstretches\twalk_ns\tfloor_ns\tV1_meas\tM64_meas\tM64_pred\tADAPT_carry\tADAPT_cold\tORACLE\tsw_per_MiB_carry\tM_share_carry\tR2_ADAPT_carry\tR2_ADAPT_cold\n")
        for d in cells:
            if d["role"] == "skip":
                continue
            key = "dl_v1cal" if d["role"] == "hold" else "dl"      # hold-out rows: costs calibrated on V1's measured miss
            rc, rk = row(d, THR, S_DEF, BK_DEF, True, key), row(d, THR, S_DEF, BK_DEF, False, key)
            r2c, r2k = row(d, thr2, S_DEF, BK_DEF, True, key, 2), row(d, thr2, S_DEF, BK_DEF, False, key, 2)
            f.write("\t".join(str(x) for x in (d["role"], d["cell"], d["subj"], d["nst"], "%.0f" % d["walk"], "%.0f" % d["floor"],
                    "%.0f" % d["meas"]["V1"], ("%.0f" % d["meas"]["M64"]) if "M64" in d["meas"] else "-", "%.0f" % rc["m64"], "%.0f" % rc["adapt"],
                    "%.0f" % rk["adapt"], "%.0f" % rc["oracle"], "%.1f" % (rc["sw"] / (d["nst"] * 64 / 2 ** 20)), "%.2f" % rc["mshare"],
                    "%.0f" % r2c["adapt"], "%.0f" % r2k["adapt"])) + "\n")
    print("early-exit cells excluded (not priceable):", [d["cell"] + " " + d["subj"] for d in skip])


if __name__ == "__main__":
    main()
