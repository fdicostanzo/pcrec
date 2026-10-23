#!/usr/bin/env python3
# docs/design/findall_iter/twin/i4_verdict.py -- the I4 timing cell's VERDICT
# ([FINDALL-NEXT] I4, lane i2build; docs/design/findall_iter_i2.md §4). parity_verdict.py
# calls main() on a results.tsv whose arms include Fb; the rules are that file's header.
from collections import defaultdict

GATE2 = ("c1-", "c3-", "c4", "c6")
GATE3 = (("c3-4k", "R2"), ("c3-1m", "R2"))
GATE4 = ("c7", "c8")
LOAD_MAX, SIB_MAX = 1.0, 25.0   # the re-queue rule's UNMEASURED DEFAULTS
ARMS = ["I_i1", "I_i1b", "I", "F", "Fb", "I_info", "N4", "N64"]


def median(v):
    v = sorted(v)
    m = len(v) // 2
    return v[m] if len(v) % 2 else (v[m - 1] + v[m]) / 2


def quantile(v, q):
    v = sorted(v)
    if len(v) == 1:
        return v[0]
    x = q * (len(v) - 1)
    i = int(x)
    f = x - i
    return v[i] if i + 1 >= len(v) else v[i] * (1 - f) + v[i + 1] * f


def floor_of(xs, ys):
    """The A/A floor over the launches: max(|median(X/X') - 1|, IQR(X/X') / median)."""
    r = [x / y for x, y in zip(xs, ys)]
    m = median(r)
    return max(abs(m - 1), (quantile(r, 0.75) - quantile(r, 0.25)) / m)


def main(rows):
    hdr, rows = rows[0], rows[1:]
    col = {h: i for i, h in enumerate(hdr)}
    ns = defaultdict(dict)          # (cell, regime, arm) -> {launch: ns}
    count = {}
    cells, ld, sb = [], defaultdict(list), defaultdict(list)
    for r in rows:
        c, g, a, l = r[col["cell"]], r[col["regime"]], r[col["arm"]], r[col["launch"]]
        ns[(c, g, a)][l] = float(r[col["ns"]])
        count[(c, a)] = int(r[col["count"]])
        if c not in cells:
            cells.append(c)
        ld[l].append(float(r[col["load1"]]))
        sb[l].append(float(r[col["sib_busy_pct"]]))
    launches = sorted(ld, key=int)
    quiet = all(median(ld[l]) <= LOAD_MAX and max(sb[l]) <= SIB_MAX for l in launches)
    print(f"== I4 TABLE: {len(launches)} launches, {len(rows)} rows; ns per whole find-all, "
          f"median over launches [IQR %]; ratio = arm / I")
    for l in launches:
        print(f"   launch {l}: load1 median {median(ld[l]):.2f}, sibling busy max {max(sb[l]):.1f}%")
    print(f"QUIET {'yes' if quiet else 'no'} (every launch: load1 median <= {LOAD_MAX}, "
          f"sibling <= {SIB_MAX}% busy)")
    nverd = nfind = 0
    for c in cells:
        for g in ("R1", "R2"):
            d = {a: ns[(c, g, a)] for a in ARMS if (c, g, a) in ns}
            if set(d) != set(ARMS):
                print(f"   {c} {g}: MISSING arms {sorted(set(ARMS) - set(d))}")
                continue
            ls_ = sorted(set.intersection(*(set(v) for v in d.values())), key=int)
            med = {a: median([d[a][l] for l in ls_]) for a in ARMS}
            f_i = floor_of([d["I_i1"][l] for l in ls_], [d["I_i1b"][l] for l in ls_])
            f_f = floor_of([d["F"][l] for l in ls_], [d["Fb"][l] for l in ls_])
            print(f"-- {c} {g}  floor_I {f_i * 100:.2f}%  floor_F {f_f * 100:.2f}%")
            for a in ARMS:
                v = [d[a][l] for l in ls_]
                iqr = (quantile(v, .75) - quantile(v, .25)) / med[a] * 100
                print(f"   {a:<7}{med[a]:>14.2f} ns  [{iqr:5.2f}%]  ratio {med[a] / med['I']:.4f}")
            out = []
            r1 = med["I"] / med["I_i1"]
            ok = r1 <= 1 + f_i
            out.append(f"G1 {'PASS' if ok else 'FINDING'} I/I_i1 {r1:.4f}")
            nfind += not ok
            rf = med["F"] / med["I"]
            if c.startswith(GATE2):
                ok = rf <= 1 + f_f
                out.append(f"G2 {'PASS' if ok else 'FINDING'} F/I {rf:.4f}")
                nfind += not ok
            if (c, g) in GATE3:
                ok = rf < 1 - f_f
                out.append(f"G3 {'PASS' if ok else 'FINDING'} F/I {rf:.4f} (< {1 - f_f:.4f})")
                nfind += not ok
            if c.startswith(GATE4):
                ok = rf <= 1 + f_f
                out.append(f"G4 {'PASS' if ok else 'FINDING'} F/I {rf:.4f}")
                nfind += not ok
            out.append(f"report F/I {rf:.4f} N4/I {med['N4'] / med['I']:.4f} "
                       f"N64/I {med['N64'] / med['I']:.4f} I_info/I {med['I_info'] / med['I']:.4f}")
            if c == "c1-4k" and count.get((c, "F")):
                out.append(f"(I_info-F)/match {(med['I_info'] - med['F']) / count[(c, 'F')]:.3f} ns")
            print(f"VERDICT {c} {g} floor_I {f_i * 100:.2f}% floor_F {f_f * 100:.2f}%: " + "; ".join(out))
            nverd += 1
    print(f"I4 GATES: {nfind} FINDING(s)")
    print("parity: DONE rc=0")
    print(f"== parity COMPLETE {nverd} verdict rows")
    return 0
