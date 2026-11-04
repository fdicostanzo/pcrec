#!/usr/bin/env python3
r"""docs/dev/lanes/trailgc2/movers.py -- lane trailgc2's mover census ([K134]),
adapted from docs/dev/lanes/reqvm1/movers.py (same population and cells).

Every `pattern`/`pattern-esc` line under tests/ (read by `pcrec --list-source`,
ids FILE:LINE), and every line of each --patterns-file, is compiled by a
REFERENCE pcrec (the lane's base, abi 91) and a WORKING pcrec (the lane, abi
93), in five cells: byte and utf8 at the default engine, byte and utf8 at
--engine=vm, and byte --no-captures; all under --features all, `-o -`.

The abi number is masked on both sides (the provenance line, the
`PCREC_RX_ABI_H` guard, `.abi = N`), so it does not move every artifact, and so
is the `<PREFIX>_VM_PROGRAM_BYTES` value, which measures the program text the
checkpoints add to.

A cell is IDENTICAL, MOVED (both compile, texts differ), GAINED (only the
working side compiles), LOST (only the reference compiles) or REFUSED by both.
EXPECTED: nothing is gained or lost, and a MOVED cell is an ADMITTED site of
the lane, class `checkpoints`: removing from the working text the trail floor
function, the compaction function and the `<PREFIX>_TRAIL_CHECK` macro (one
block), every `<PREFIX>_TRAIL_CHECK();` line, the matcher's
`<prefix>_trail_gc_at` declaration, and rewriting each guarded jump
`{ <PREFIX>_TRAIL_CHECK(); goto L; }` back to `goto L;`, gives the reference
text exactly. Anything else is UNEXPECTED and printed.

Usage: movers.py REF_PCREC WORK_PCREC TREE [--patterns-file F]... [--jobs N]
Trailer: `movers: DONE cells=... unexpected=N`."""
import argparse
import concurrent.futures as cf
import os
import re
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


ABI_LINE = re.compile(rb"(abi |PCREC_RX_ABI_H|\.abi = )")
# the VM program's own size stamp measures the text the checkpoints add to
PROGRAM_BYTES = re.compile(rb"^(#define \w+_VM_PROGRAM_BYTES )\d+ULL$")
GUARDED = re.compile(rb"\{ \w+_TRAIL_CHECK\(\); (goto \w+;) \}")


def mask_abi(text):
    return b"\n".join(re.sub(rb"\b(91|93)\b", b"N", l) if ABI_LINE.search(l)
                      else PROGRAM_BYTES.sub(rb"\1N", l) for l in text.split(b"\n"))


def strip_checkpoints(text):
    """The working text with the lane's admitted additions taken out."""
    out = []
    skip = False
    for l in text.split(b"\n"):
        if re.match(rb"^static .*size_t \w+_trail_gc_floor\(size_t cap\)$", l):
            skip = True
        if skip == "blank":
            skip = False
            if l == b"":
                continue
        if skip:
            if l.startswith(b"    } while (0)"):
                skip = "blank"
            continue
        if re.match(rb"^\s*\w+_TRAIL_CHECK\(\);\s*$", l):
            continue
        if re.match(rb"^\s*size_t \w+_trail_gc_at = \w+_trail_gc_floor\(run->trail_cap\);$", l):
            continue
        out.append(GUARDED.sub(rb"\1", l))
    return b"\n".join(out)


def site(ro, wo):
    """The admitted site class a moved cell must be, or None."""
    if strip_checkpoints(wo) == ro:
        return "checkpoints"
    return None


def one(ref, work, key, pat, cell, flags):
    p = pat.decode("utf-8", "surrogateescape")
    base = ["-p", "rx", "--features", "all"] + flags + ["-o", "-", "--pattern", p]
    rr, ro = run([ref] + base)
    wr, wo = run([work] + base)
    if rr == 0 and wr == 0:
        ro, wo = mask_abi(ro), mask_abi(wo)
        cls = "IDENTICAL" if ro == wo else (site(ro, wo) or "MOVED")
    elif rr != 0 and wr != 0:
        cls = "REFUSED"
    elif wr == 0:
        cls = "GAINED"
    else:
        cls = "LOST"
    ok = cls in ("IDENTICAL", "REFUSED", "checkpoints")
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
