# span_cards/slot/j1_rule.py — J1's pre-registered rule (span_cards.md §3.6, m 0.5, k 5): the slot's own
# derivation of J1's verdict from J1's cells. The recompute (S2e) re-derives it independently (MEAS-7).
#   python3 -I j1_rule.py CELLS.tsv   prints `j1_verdict X` and `j1_widths W;W|-`, then one line per (cell, w)
# CELLS: columns `cell pattern subject regime width launch ns_e6` (the run record's j1_cells section), width
# `128#b` the twin. A J1 cell c is (pattern, subject, regime).
import math, sys

M_NUM, M_DEN, K = 1, 2, 5            # the margin m = 0.5 and k = 5 of 8 cells (§3.6, j1_drill.py Part 2)
WIDTHS = (32, 64, 256, 512)

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

def sp2(x):
    m = med(x)
    k = max(range(len(x)), key=lambda i: (abs(x[i] - m), i))
    w = [x[i] for i in range(len(x)) if i != k]
    n = len(w)
    return rhafz(1723000 * (n * sum(t * t for t in w) - sum(w) ** 2), 10**6 * n * (n - 1))

def verdict(rows):
    t = {}
    for r in rows:
        t.setdefault((r["pattern"], r["subject"], r["regime"]), {}).setdefault(r["width"], {})[int(r["launch"])] = int(r["ns_e6"])
    cells = sorted(t)
    beats = {w: 0 for w in WIDTHS}
    loses = {w: 0 for w in WIDTHS}
    lines = []
    for c in cells:
        base, twin = t[c]["128"], t[c]["128#b"]
        ls = sorted(base)
        aa = med([rhafz(abs(twin[l] - base[l]) * 10**6, base[l]) for l in ls])
        for w in WIDTHS:
            r = [rhafz((t[c][str(w)][l] - base[l]) * 10**6, base[l]) for l in ls]
            thr = isqrt_rn(aa * aa + sp2(r))
            big = abs(med(r)) * M_DEN > thr * M_NUM   # |med(r)| > m x thr, i.e. 2 x |med(r)| > thr
            b = all(x < 0 for x in r) and big
            lo = all(x > 0 for x in r) and big
            beats[w] += b
            loses[w] += lo
            lines.append("%s\t%d\t%s\tmed_r %d\tthr %d" % ("/".join(c), w, "beats" if b else "loses" if lo else "-",
                                                         med(r), thr))
    win = [w for w in WIDTHS if beats[w] >= K and loses[w] == 0]
    if win:
        v = "b"
    elif not any(beats.values()):
        v = "a"
    else:
        v = "c"
    return v, win, lines, len(cells)

def main():
    cols = ["cell", "pattern", "subject", "regime", "width", "launch", "ns_e6"]
    rows = [dict(zip(cols, ln.rstrip("\n").split("\t"))) for ln in open(sys.argv[1])
            if ln.strip() and not ln.startswith("#")]
    v, win, lines, n = verdict(rows)
    print("j1_verdict\t%s" % v)
    print("j1_widths\t%s" % (";".join(str(w) for w in win) or "-"))
    print("j1_cells_read\t%d" % n)
    for ln in lines:
        print(ln)

if __name__ == "__main__":
    main()
