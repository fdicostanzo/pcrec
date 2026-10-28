#!/usr/bin/env python3
"""docs/dev/lanes/reqvm1/movers.py -- lane reqvm1's mover census ([REQRUN-VM]),
adapted from docs/dev/lanes/ic1b/movers.py (same population and cells).

Every `pattern`/`pattern-esc` line under tests/ (read by `pcrec --list-source`,
ids FILE:LINE), and every line of each --patterns-file, is compiled by a
REFERENCE pcrec (the lane's base) and a WORKING pcrec (the lane built with the
reference's abi number, so the digits do not move every artifact), in five
cells: byte and utf8 at the default engine, byte and utf8 at --engine=vm, and
byte --no-captures; all under --features all, `-o -`.

A cell is IDENTICAL, MOVED (both compile, texts differ), GAINED (only the
working side compiles), LOST (only the reference compiles) or REFUSED by both.
EXPECTED: nothing is gained or lost, and a MOVED cell is an ADMITTED site of
the lane: the working artifact is a VM with no DFA scan (`_VM_PREFILTER
"none"`) carrying a number in `_REQ_HANDOFF` where the reference read "none"
(the attempt loop's rows, class `vm-attempts`), or a VM hybrid whose working
`_DFA_PREFILTER` reads "handoff" where the reference's did not (the
prefilter's re-entry, class `hybrid-reentry`). Anything else is UNEXPECTED
and printed.

Usage: movers.py REF_PCREC WORK_PCREC TREE [--patterns-file F]... [--jobs N]
Trailer: `movers: DONE cells=... unexpected=N`."""
import argparse
import concurrent.futures as cf
import os
import subprocess

CELLS = [("byte-auto", []), ("utf8-auto", ["-e", "utf8"]),
         ("byte-vm", ["--engine=vm"]), ("utf8-vm", ["-e", "utf8", "--engine=vm"]),
         ("byte-nocap", ["--no-captures"])]


def run(argv):
    try:
        r = subprocess.run(argv, capture_output=True, timeout=120)
        return r.returncode, r.stdout
    except subprocess.TimeoutExpired:
        return 124, b""


def decode_escape(s):
    out = bytearray()
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            n = s[i + 1]
            m = {"t": b"\t", "n": b"\n", "r": b"\r", "\\": b"\\"}
            if n in m:
                out += m[n]
                i += 2
                continue
            if n == "x":
                out.append(int(s[i + 2:i + 4], 16))
                i += 4
                continue
        out += c.encode("utf-8", "surrogateescape")
        i += 1
    return bytes(out)


def corpus(pcrec, tree):
    rows = []
    for d, _, fs in os.walk(os.path.join(tree, "tests")):
        for fn in sorted(fs):
            if not fn.endswith(".rxt"):
                continue
            f = os.path.join(d, fn)
            rc, out = run([pcrec, "--list-source", f])
            if rc:
                continue
            for line in out.decode("utf-8", "surrogateescape").splitlines():
                v = line.split("\t")
                if line.startswith("#") or len(v) < 5 or v[0] not in ("pattern", "pattern-esc"):
                    continue
                rows.append(("%s:%s" % (os.path.relpath(f, tree), v[1]), decode_escape(v[4])))
    return rows


def stamp(text, name):
    for line in text.splitlines():
        if line.startswith(b"#define RX_" + name + b" "):
            return line.split(b" ", 2)[2].strip()
    return None


def site(ro, wo):
    """The admitted site class a moved cell must be, or None."""
    if stamp(wo, b"VM_PREFILTER") == b'"none"' and stamp(wo, b"ENGINE") == b'"vm"':
        if stamp(wo, b"REQ_HANDOFF") not in (None, b'"none"') and stamp(ro, b"REQ_HANDOFF") == b'"none"':
            return "vm-attempts"
    if stamp(wo, b"VM_PREFILTER") == b'"hybrid"':
        if stamp(wo, b"DFA_PREFILTER") == b'"handoff"' and stamp(ro, b"DFA_PREFILTER") != b'"handoff"':
            return "hybrid-reentry"
    return None


def one(ref, work, key, pat, cell, flags):
    p = pat.decode("utf-8", "surrogateescape")
    base = ["-p", "rx", "--features", "all"] + flags + ["-o", "-", "--pattern", p]
    rr, ro = run([ref] + base)
    wr, wo = run([work] + base)
    if rr == 0 and wr == 0:
        cls = "IDENTICAL" if ro == wo else (site(ro, wo) or "MOVED")
    elif rr != 0 and wr != 0:
        cls = "REFUSED"
    elif wr == 0:
        cls = "GAINED"
    else:
        cls = "LOST"
    ok = cls in ("IDENTICAL", "REFUSED", "vm-attempts", "hybrid-reentry")
    return key, cell, cls, ok, p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref")
    ap.add_argument("work")
    ap.add_argument("tree")
    ap.add_argument("--patterns-file", action="append", default=[])
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    rows = corpus(a.work, a.tree)
    for pf in a.patterns_file:
        with open(pf, "rb") as f:
            for i, line in enumerate(f, 1):
                line = line.rstrip(b"\n")
                if line:
                    rows.append(("%s:%d" % (os.path.basename(pf), i), line))
    counts = {}
    unexpected = []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(one, a.ref, a.work, k, p, c, fl) for k, p in rows for c, fl in CELLS]
        for fu in cf.as_completed(futs):
            key, cell, cls, ok, p = fu.result()
            counts[cls] = counts.get(cls, 0) + 1
            if not ok:
                unexpected.append((key, cell, cls, p))
    for key, cell, cls, p in sorted(unexpected)[:200]:
        print("UNEXPECTED %s %s %s %r" % (cls, key, cell, p))
    print("movers: patterns=%d %s" % (len(rows), " ".join(
        "%s=%d" % (k.lower(), v) for k, v in sorted(counts.items()))))
    print("movers: DONE cells=%d unexpected=%d" % (sum(counts.values()), len(unexpected)))
    return 1 if unexpected else 0


if __name__ == "__main__":
    raise SystemExit(main())
