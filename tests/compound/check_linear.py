#!/usr/bin/env python3
"""tests/compound/check_linear.py -- [COMPOUND] G3, COUNTED WORK
(docs/design/compound.md §E.3 G3, §B.5; the twin's cost2.py promoted).

  check_linear.py PCREC PCREC_HARNESS WORKDIR

Counts the subject-byte LOADS of a whole find-all (no clock: loads_drv.c's
kernel-address hooks) on the named pin-only shapes, k = 1,000 and 4,000:
the compound (the default build), the lever (today's plain artifact, the
harness build under `--harness=no-compound`) and, for the final-newline
cells, Q's tree compiled ALONE as a plain artifact. Calls and matches must
agree between the compound and the lever. The bounds, derived from the
measured excess (one seed byte per Q call), not chosen:
  - every cell:            T_compound <= T_lever + calls
    except the two final-newline cells (`\\s+$`, `\\s*?$`: Q's rev-end double
    walk, B3's to remove), gated at TODAY's rev-end cost:
                           T_compound <= T_Qalone + calls
  - linearity, every cell: T_compound(4k) <= 4 * T_compound(k) + calls(4k)
    (any k, 4k pair separates 4x from 16x).
Each compound artifact must stamp `"split"` (the cell measures the
compound, not a declined row). Exit 1 on a violated bound.
"""
import os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CFLAGS = ["-O0", "-g", "-fno-pie", "-no-pie", "-fsanitize=kernel-address", "--param",
          "asan-instrumentation-with-call-threshold=0", "--param", "asan-stack=0",
          "--param", "asan-globals=0", "-fno-builtin-memchr", "-fno-builtin-memrchr",
          "-fno-builtin-memcmp", "-fno-builtin-memmem", "-w", "-fcf-protection=none"]

# (name, P, Q alone or None, [(prefix, run, suffix, final_newline)])
CELLS = [
    ("trim", rb"^\s+|\s+$", rb"\s+$", [
        (b"Q", b"\t", b"Q", False),        # K106's internal run, no match
        (b"", b"\t", b"Q", False),         # a floor match only
        (b"Q", b"\t", b"", False),         # an end match only
        (b"", b"\t", b"Q" + b"\t" * 400, False),  # a floor match and an end match
        (b"Q", b"\t", b"\n", True),        # an end match before a final newline
    ]),
    ("wrapper", rb"^\s*\{|\}\s*$", rb"\}\s*$", [
        (b"{", b" ", b"}", False),         # a floor match and an end match
        (b"Q", b"}", b"Q", False),         # n+3 attempt entries today
        (b"{", b" ", b"}\n", False),
    ]),
    ("tie", rb"^q|a$|a\n$", rb"a$|a\n$", [
        (b"q", b"x", b"a\n", False),
        (b"x", b"x", b"a\n", False),
    ]),
    ("lazytie", rb"^q|\s*?$", rb"\s*?$", [
        (b"q", b" ", b"\n", True),
    ]),
    ("floor-only", rb"a{0,4}\A", None, [
        (b"", b"a", b"", False),
        (b"x", b"a", b"", False),
    ]),
]
KS = (1000, 4000)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, timeout=600, **kw)


def build(cmd, pat, wd):
    os.makedirs(wd, exist_ok=True)
    r = run(cmd + ["--features", "all", "-p", "rx", "-o", os.path.join(wd, "rx.c"), "--pattern", pat])
    if r.returncode:
        sys.exit("FAIL: %s refused %r: %s" % (cmd[0], pat, r.stderr.decode()[:200]))
    st = re.search(rb'#define RX_COMPOUND "([^"]*)"', open(os.path.join(wd, "rx.c"), "rb").read())
    for args in (CFLAGS + ["-I", wd, "-c", "-o", os.path.join(wd, "a.o"), os.path.join(wd, "rx.c")],
                 ["-O1", "-w", "-fno-pie", "-fno-builtin", "-I", wd, "-c", "-o",
                  os.path.join(wd, "d.o"), os.path.join(HERE, "loads_drv.c")],
                 ["-no-pie", "-o", os.path.join(wd, "q"), os.path.join(wd, "a.o"), os.path.join(wd, "d.o")]):
        r = run([os.environ.get("CC", "gcc")] + args)
        if r.returncode:
            sys.exit("FAIL: the counted build failed: %s" % r.stderr.decode()[:400])
    return os.path.join(wd, "q"), st.group(1).decode() if st else "MISSING"


def count(q, pre, rb, k, suf):
    f = run([q, pre.hex(), rb.hex(), str(k), suf.hex()]).stdout.decode().split()
    return int(f[1]), int(f[2]), int(f[3])


def main():
    pcrec, harness, wd = sys.argv[1:4]
    fails, rows = [], 0
    for name, p, qalone, subs in CELLS:
        comp, st = build([pcrec], p, os.path.join(wd, name, "comp"))
        lev, _ = build([harness, "--harness=no-compound"], p, os.path.join(wd, name, "lever"))
        qa = build([pcrec], qalone, os.path.join(wd, name, "qalone"))[0] if qalone else None
        if st != "split":
            fails.append("%s: the compound build stamps %r, not \"split\"" % (name, st))
            continue
        for pre, rb, suf, fnl in subs:
            tc = {}
            for k in KS:
                cc, mc, tcomp = count(comp, pre, rb, k, suf)
                cl, ml, tlev = count(lev, pre, rb, k, suf)
                rows += 1
                tc[k] = (tcomp, cc)
                lab = "%s %r.%r^%d.%r" % (name, pre, rb, k, suf[:8])
                if (cc, mc) != (cl, ml):
                    fails.append("%s: calls/matches %d/%d, lever %d/%d" % (lab, cc, mc, cl, ml))
                if fnl:
                    _, _, tq = count(qa, pre, rb, k, suf)
                    if tcomp > tq + cc:
                        fails.append("%s: T_compound %d > T_Qalone %d + calls %d" % (lab, tcomp, tq, cc))
                    print("%-12s %-34s k=%-5d calls=%-4d T_lever=%-10d T_Qalone=%-8d T_compound=%d"
                          % (name, repr(pre + b"." + rb + b"^k." + suf[:6]), k, cc, tlev, tq, tcomp))
                else:
                    if tcomp > tlev + cc:
                        fails.append("%s: T_compound %d > T_lever %d + calls %d" % (lab, tcomp, tlev, cc))
                    print("%-12s %-34s k=%-5d calls=%-4d T_lever=%-10d T_compound=%d"
                          % (name, repr(pre + b"." + rb + b"^k." + suf[:6]), k, cc, tlev, tcomp))
            (t1, _), (t4, c4) = tc[KS[0]], tc[KS[1]]
            if t4 > 4 * t1 + c4:
                fails.append("%s %r: not linear, T(4k) %d > 4*T(k) %d + calls %d" % (name, pre + rb + suf[:8], t4, 4 * t1, c4))
    shutil.rmtree(wd, ignore_errors=True)
    for f in fails:
        print("FAIL: " + f)
    ok = not fails and rows >= 24
    print("%s: G3 counted work: %d cell-k rows over %d shapes; %d violations" %
          ("PASS" if ok else "FAIL", rows, len(CELLS), len(fails)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
