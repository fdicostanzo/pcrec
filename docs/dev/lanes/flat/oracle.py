#!/usr/bin/env python3
"""flat/oracle.py OUT ANSWERS GRID2_ORACLE -- leg O of check.sh: the walk's find-all answer against libpcre2.

J1 cells: libpcre2 10.46 (docs/design/eng_brep_measurements/probes/pcre2_ctypes.py, refused at another version) on
each cell's smallest subject and its smallest subject with a match, folded the way grid1/gdrv.c folds one buffer
(matches, h = h*131 + s*31 + e mod 2^64).
`-e utf8` patterns compile with PCRE2_UTF. Anchors: grid2's own oracle.tsv line (libpcre2 too). One line per cell:
`O <cell> <subject> OK|FAIL ...`; exit 1 on any FAIL.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PCRE2_UTF = 0x00080000
MASK = (1 << 64) - 1


def binding():
    p = os.path.join(ROOT, "docs/design/eng_brep_measurements/probes/pcre2_ctypes.py")
    spec = importlib.util.spec_from_file_location("pcre2_ctypes", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    out, answers, g2oracle = sys.argv[1:4]
    pc = binding()
    if pc.version().split()[0] != "10.46":
        sys.exit("oracle: libpcre2 %s, want 10.46" % pc.version())
    pats = {}
    for ln in open(os.path.join(ROOT, "docs/design/memfn/r17b_prime/e8min/j1_patterns.tsv"), encoding="utf-8"):
        f = ln.rstrip("\n").split("\t")
        if len(f) == 3:
            pats[f[0]] = (f[1], f[2])
    g2 = {}
    for ln in open(g2oracle):
        f = ln.rstrip("\n").split("\t")
        if len(f) == 4 and f[2] == "all":
            g2[(f[0], f[1])] = f[3]
    rows = [ln.rstrip("\n").split("\t") for ln in open(answers)]
    bad = 0
    for cell in sorted({r[0] for r in rows}):
        mine = [r for r in rows if r[0] == cell]
        if cell.startswith("an-"):
            for _, s, w in mine:
                want = g2.get((cell[3:], s))
                ok = want == w
                bad += not ok
                print("O %s %s %s walk='%s' grid2-oracle='%s'" % (cell, s, "OK" if ok else "FAIL", w, want))
            continue
        size = lambda r: os.path.getsize(os.path.join(out, "subj", r[1]))
        pick = [min(mine, key=size)]
        hit = [r for r in mine if not r[2].startswith("matches=0 ")]
        if hit and min(hit, key=size) is not pick[0]:
            pick.append(min(hit, key=size))
        extra, pat = pats[cell[3:]]
        rx = pc.compile(pat.encode("utf-8"), PCRE2_UTF if "utf8" in extra else 0)
        for _, s, w in pick:
            bad += one(rx, out, cell, s, w)
    sys.exit(1 if bad else 0)


def one(rx, out, cell, s, w):
    buf = open(os.path.join(out, "subj", s), "rb").read()
    k = h = p = 0
    while p <= len(buf):
        r = rx.search(buf, p)
        if r is None:
            break
        (a, e), _ = r
        k += 1
        h = (h * 131 + a * 31 + e) & MASK
        if e == a and e >= len(buf):
            break
        p = e if e > a else e + 1
    want = "matches=%d hash=%x" % (k, h)
    ok = want == w
    print("O %s %s %s walk='%s' libpcre2='%s'" % (cell, s, "OK" if ok else "FAIL", w, want))
    return not ok


if __name__ == "__main__":
    main()
