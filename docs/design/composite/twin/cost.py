#!/usr/bin/env python3
"""[COMPOSITE] design lane mscomp: counted subject loads (no clock) of a whole
find-all, today's artifact vs the hand-composed split composite, with the
survey's qdrv.c instrument (docs/dev/optloop/matchsplit/qdrv.c: every subject
load counted through kernel-address ASan hooks).

  cost.py PCREC OUTDIR      (cells are listed below; prints one TSV row per cell x k)
The composite is ONE translation unit: floor.c + q.c + the controller, the
parts' entries left exported (the twin does not need EMIT-ENTRIES)."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
QDRV = os.path.join(HERE, "../../../dev/optloop/matchsplit/qdrv.c")
GT = "/usr/bin/gnutimeout"
CFLAGS = ["-O0", "-g", "-fno-pie", "-no-pie", "-fsanitize=kernel-address", "--param",
          "asan-instrumentation-with-call-threshold=0", "--param", "asan-stack=0", "--param", "asan-globals=0",
          "-fno-builtin-memchr", "-fno-builtin-memrchr", "-fno-builtin-memcmp", "-fno-builtin-memmem",
          "-w", "-fcf-protection=none"]
SQ = open(os.path.join(HERE, "sqli_np.txt"), "rb").read() if os.path.exists(os.path.join(HERE, "sqli_np.txt")) else None
SP = open(os.path.join(HERE, "sqli_p.txt"), "rb").read() if os.path.exists(os.path.join(HERE, "sqli_p.txt")) else None

# (name, P, Q (pruned by hand = the build's kill + prune), [(pre, run, suf)])
CELLS = [
    ("trim", rb"^\s+|\s+$", rb"\s+$",
     [(b"Q", b"\t", b"Q"), (b"Q", b"\t", b""), (b"", b"\t", b""), (b"Q", b"\t", b"\n"), (b"Q", b"\t", b"Q\n")]),
    ("wrapper", rb"^\s*\{|\}\s*$", rb"\}\s*$",
     [(b"Q", b"}", b"Q"), (b"Q", b"}", b""), (b"Q", b" ", b"}")]),
    ("trim-ws-start", rb"^\s+|\s+$", rb"\s+$", [(b"", b"\t", b"Qx")]),
    ("sqli", SP, SQ, [(b"Q", b"select ", b"Q"), (b"Q", b"xxxx ", b"Q"), (b"Q", b"a", b"Q")]),
]


def run(cmd, **kw):
    return subprocess.run([GT, "300"] + cmd, capture_output=True, **kw)


def build_today(pcrec, p, wd):
    os.makedirs(wd, exist_ok=True)
    r = run([pcrec, "--features", "all", "-p", "rx", "-o", f"{wd}/rx.c", "--pattern", p])
    assert r.returncode == 0, r.stderr
    return link(wd, [f"{wd}/rx.c"])


def build_comp(pcrec, p, q, wd):
    os.makedirs(wd, exist_ok=True)
    for pre, name, text in (("rxf", "floor", b"\\G(?:" + p + b")"), ("rxq", "q", q)):
        r = run([pcrec, "--features", "all", "-p", pre, "-o", f"{wd}/{name}.c", "--pattern", text])
        assert r.returncode == 0, r.stderr
    ctrl = open(f"{HERE}/ctrl.c.in").read().replace("@HAS_G@", "0").replace('#include "plain.h"\n', "")
    ctrl = ctrl.replace("RXP_NCAPS", "RXF_NCAPS")
    hdr = ('#include "floor.h"\n#define RX_NCAPS RXF_NCAPS\n'
           'int rx_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);\n')
    open(f"{wd}/rx.h", "w").write(hdr)
    open(f"{wd}/comp.c", "w").write('#include "floor.c"\n#include "q.c"\n' + ctrl)
    return link(wd, [f"{wd}/comp.c"])


def link(wd, srcs):
    r = run(["gcc"] + CFLAGS + ["-I", wd, "-c", "-o", f"{wd}/a.o"] + srcs)
    assert r.returncode == 0, r.stderr.decode()[:2000]
    r = run(["gcc", "-O1", "-w", "-fno-pie", "-fno-builtin", "-I", wd, "-c", "-o", f"{wd}/d.o", QDRV])
    assert r.returncode == 0, r.stderr
    r = run(["gcc", "-no-pie", "-o", f"{wd}/q", f"{wd}/a.o", f"{wd}/d.o"])
    assert r.returncode == 0, r.stderr
    return f"{wd}/q"


def count(q, pre, rb, k, suf):
    r = run([q, pre.hex(), rb.hex(), str(k), suf.hex()])
    f = r.stdout.decode().split()
    return int(f[1]), int(f[2]), int(f[3])


def main():
    pcrec, out = sys.argv[1:3]
    print("cell\tsubject\tk\tcalls\tmatches\tT_today\tT_comp\tratio")
    for name, p, q, subs in CELLS:
        if p is None: continue
        t = build_today(pcrec, p, f"{out}/{name}/today")
        c = build_comp(pcrec, p, q, f"{out}/{name}/comp")
        for pre, rb, suf in subs:
            for k in (1000, 4000, 16000):
                ca, ma, ta = count(t, pre, rb, k, suf)
                cb, mb, tb = count(c, pre, rb, k, suf)
                assert (ca, ma) == (cb, mb), (name, pre, rb, suf, k, ca, ma, cb, mb)
                lab = (pre + b"." + rb + b"^k." + suf).decode("latin-1").encode("unicode_escape").decode()
                print(f"{name}\t{lab}\t{k}\t{ca}\t{ma}\t{ta}\t{tb}\t{tb / ta:.4f}", flush=True)


if __name__ == "__main__":
    main()
