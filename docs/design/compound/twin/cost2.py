#!/usr/bin/env python3
"""[COMPOUND] design lane mscomp2: counted subject loads (no clock) of a whole
find-all, today's artifact vs the revision-2 split compound, PIN-ONLY cells
(chk B1: the first build admits only an end-pinned or never Q, so a subject
has at most a floor match plus the end matches; the many-match term of an
unanchored Q is out of scope by admission).

Differences from cost.py (revision 1): Q is DERIVED by twin2.derive (not
pruned by hand), F is P's own attempt (P compiled, its _match_caps at the
floor), the controller is ctrl2.c.in, and the cells add MATCHING subjects
(a floor match and an end match in one find-all; the final-newline tie).

  cost2.py PCREC OUTDIR      (prints one TSV row per cell x k)"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import twin2                                   # noqa: E402
from cost import CFLAGS, QDRV, GT, count       # noqa: E402

# (name, P, [(prefix, run, suffix-or-callable(k))])
CELLS = [
    ("trim", rb"^\s+|\s+$", [
        (b"Q", b"\t", b"Q"),                         # K106 internal run, no match
        (b"", b"\t", b"Q"),                          # floor match only
        (b"Q", b"\t", b""),                          # end match only
        (b"", b"\t", lambda k: b"Q" + b"\t" * min(k, 4000)),    # floor match + end match (qdrv's suffix cap)
        (b"Q", b"\t", b"\n"),                        # end match before a final newline (B3)
        (b"", b"\t", lambda k: b"Q" + b"\t" * min(k, 4000) + b"\n"),
    ]),
    ("wrapper", rb"^\s*\{|\}\s*$", [
        (b"{", b" ", b"}"),                          # floor match + end match
        (b"Q", b"}", b"Q"),                          # n+3 attempt entries today
        (b"{", b" ", b"}\n"),
    ]),
    ("tie", rb"^q|a$|a\n$", [
        (b"q", b"x", b"a\n"),                        # floor + the two-seed tie
        (b"x", b"x", b"a\n"),
    ]),
    ("lazytie", rb"^q|\s*?$", [
        (b"q", b" ", b"\n"),
    ]),
    ("floor-only", rb"a{0,4}\A", [
        (b"", b"a", b""),
        (b"x", b"a", b""),
    ]),
]


def run(cmd, **kw):
    return subprocess.run([GT, "300"] + cmd, capture_output=True, **kw)


def link(wd, srcs, defs=()):
    r = run(["gcc"] + CFLAGS + list(defs) + ["-I", wd, "-x", "c", "-c", "-o", f"{wd}/a.o"] + srcs)
    assert r.returncode == 0, r.stderr.decode()[:2000]
    r = run(["gcc", "-O1", "-w", "-fno-pie", "-fno-builtin", "-I", wd, "-c", "-o", f"{wd}/d.o", QDRV])
    assert r.returncode == 0, r.stderr
    r = run(["gcc", "-no-pie", "-o", f"{wd}/q", f"{wd}/a.o", f"{wd}/d.o"])
    assert r.returncode == 0, r.stderr
    return f"{wd}/q"


def build_today(pcrec, p, wd):
    os.makedirs(wd, exist_ok=True)
    r = run([pcrec, "--features", "all", "-p", "rx", "-o", f"{wd}/rx.c", "--pattern", p])
    assert r.returncode == 0, r.stderr
    return link(wd, [f"{wd}/rx.c"])


def build_comp(pcrec, p, wd):
    os.makedirs(wd, exist_ok=True)
    q, has_g, why = twin2.derive(p, "byte")
    assert why.startswith("ok"), why
    for pre, name, text in (("rxf", "floor", p),) + ((("rxq", "q", q),) if q is not None else ()):
        r = run([pcrec, "--features", "all", "-p", pre, "-o", f"{wd}/{name}.c", "--pattern", text])
        assert r.returncode == 0, r.stderr
    fmode = twin2.bound_floor(f"{wd}/floor.c")
    open(f"{wd}/plain.h", "w").write("#define RXP_NCAPS RXF_NCAPS\n")
    open(f"{wd}/rx.h", "w").write('#include "floor.h"\n#define RX_NCAPS RXF_NCAPS\n'
                                  'int rx_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);\n')
    inc = '#include "floor.c"\n' + ('#include "q.c"\n' if q is not None else "")
    open(f"{wd}/comp.c", "w").write(inc + open(f"{HERE}/ctrl2.c.in").read())
    defs = ["-DUTF=0", "-DGUARD=0", "-DUCHECK=0", f"-DHAS_G={1 if has_g else 0}", f"-DQNEVER={1 if q is None else 0}", f"-DFMODE={fmode}"]
    return link(wd, [f"{wd}/comp.c"], defs), q


def main():
    pcrec, out = sys.argv[1:3]
    print("cell\tQ\tsubject\tk\tcalls\tmatches\tT_today\tT_comp\tratio")
    for name, p, subs in CELLS:
        t = build_today(pcrec, p, f"{out}/{name}/today")
        c, q = build_comp(pcrec, p, f"{out}/{name}/comp")
        for pre, rb, suf in subs:
            for k in (1000, 4000, 16000):
                s = suf(k) if callable(suf) else suf
                ca, ma, ta = count(t, pre, rb, k, s)
                cb, mb, tb = count(c, pre, rb, k, s)
                assert (ca, ma) == (cb, mb), (name, pre, rb, k, ca, ma, cb, mb)
                sl = s if not callable(suf) else s.replace(b"\t" * min(k, 4000), b"\t^min(k,4000)")
                lab = (pre + b"." + rb + b"^k." + sl).decode("latin-1").encode("unicode_escape").decode()
                qs = "never" if q is None else q.decode("latin-1").encode("unicode_escape").decode()
                print(f"{name}\t{qs}\t{lab}\t{k}\t{ca}\t{ma}\t{ta}\t{tb}\t{tb / max(ta, 1):.4f}", flush=True)


if __name__ == "__main__":
    main()
