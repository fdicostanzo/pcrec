#!/usr/bin/env python3
r"""docs/dev/lanes/ic3/movers.py -- lane ic3's mover census ([INLINE-C] stage 3),
adapted from docs/dev/lanes/reqvm1/movers.py (same pattern population).

Two populations, each compiled by a REFERENCE pcrec (main 89831df9a) and a
WORKING pcrec (lane/ic3; both abi 91, so no rewrite is needed):

  1. every `pattern`/`pattern-esc` line under tests/ (read by the working
     pcrec's `--list-source`, ids FILE:LINE) plus each --patterns-file line,
     `--pattern` text under `--features all -o -`, in six cells: byte and
     utf8 at the default engine, byte and utf8 at --engine=vm, byte
     --no-captures, and byte --allow-code=c (stage 3 touches the code
     emitter, so a granted cell is measured too);
  2. every `.rxt`/`.rxtin` file under tests/ and examples/ that declares a
     `target` (44 at the lane's base), compiled as a
     FILE operand with --allow-code=c into a fresh directory, every written
     file compared byte for byte (the composer and the code-header path
     changed).

A cell is IDENTICAL, MOVED (both compile, texts differ), GAINED (only the
working side compiles), LOST (only the reference compiles) or REFUSED by both.
EXPECTED: IDENTICAL or REFUSED, plus the GAINED files of EXPECTED_GAINED
(a local definition holding a site, which stage 3 admits: match_api
§11.1¶1b; the D27 row `file.local_def_delivering_admitted`). Stage 3's new behaviour (pinned reached
code, a site in a composed definition) is reachable only from fixtures the
reference cannot read (`sha256` pins) or does not have, and those are
measured by the code suite, not here. Anything else is UNEXPECTED and
printed.

Usage: movers.py REF_PCREC WORK_PCREC TREE SCRATCH [--patterns-file F]... [--jobs N]
Trailer: `movers: DONE cells=... unexpected=N`."""
import argparse
import concurrent.futures as cf
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reqvm1"))
from movers import run, corpus  # noqa: E402  (the shared population reader)

EXPECTED_GAINED = {("tests/code/d27/rxt/deliver_local.rxtin", "file")}

CELLS = [("byte-auto", []), ("utf8-auto", ["-e", "utf8"]),
         ("byte-vm", ["--engine=vm"]), ("utf8-vm", ["-e", "utf8", "--engine=vm"]),
         ("byte-nocap", ["--no-captures"]), ("byte-code", ["--allow-code=c"])]


def classify(rr, ro, wr, wo):
    if rr == 0 and wr == 0:
        return "IDENTICAL" if ro == wo else "MOVED"
    if rr != 0 and wr != 0:
        return "REFUSED"
    return "GAINED" if wr == 0 else "LOST"


def one(ref, work, key, pat, cell, flags):
    p = pat.decode("utf-8", "surrogateescape")
    base = ["-p", "rx", "--features", "all"] + flags + ["-o", "-", "--pattern", p]
    rr, ro = run([ref] + base)
    wr, wo = run([work] + base)
    return key, cell, classify(rr, ro, wr, wo), p


def slurp(d):
    out = {}
    for fn in sorted(os.listdir(d)):
        with open(os.path.join(d, fn), "rb") as f:
            out[fn] = f.read()
    return out


def one_file(ref, work, tree, scratch, i, f):
    rd, wd = os.path.join(scratch, "r%d" % i), os.path.join(scratch, "w%d" % i)
    os.makedirs(rd)
    os.makedirs(wd)
    # The working tree's file, compiled by each binary from its own directory
    # (relative lib/include paths resolve the same for both).
    rr, _ = run([ref, "--allow-code=c", "-o", rd, f])
    wr, _ = run([work, "--allow-code=c", "-o", wd, f])
    ro = slurp(rd) if rr == 0 else None
    wo = slurp(wd) if wr == 0 else None
    return os.path.relpath(f, tree), "file", classify(rr, ro, wr, wo), ""


def target_files(tree):
    out = []
    for d, _, fs in [w for top in ("tests", "examples")
                     for w in os.walk(os.path.join(tree, top))]:
        for fn in sorted(fs):
            if fn.endswith((".rxt", ".rxtin")):
                f = os.path.join(d, fn)
                with open(f, "rb") as h:
                    if any(l.startswith(b"target ") for l in h.read().splitlines()):
                        out.append(f)
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref")
    ap.add_argument("work")
    ap.add_argument("tree")
    ap.add_argument("scratch")
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
    files = target_files(a.tree)
    counts = {}
    unexpected = []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(one, a.ref, a.work, k, p, c, fl) for k, p in rows for c, fl in CELLS]
        futs += [ex.submit(one_file, a.ref, a.work, a.tree, a.scratch, i, f)
                 for i, f in enumerate(files)]
        for fu in cf.as_completed(futs):
            key, cell, cls, p = fu.result()
            counts[cls] = counts.get(cls, 0) + 1
            if cls not in ("IDENTICAL", "REFUSED") and not (
                    cls == "GAINED" and (key, cell) in EXPECTED_GAINED):
                unexpected.append((key, cell, cls, p))
    for key, cell, cls, p in sorted(unexpected)[:200]:
        print("UNEXPECTED %s %s %s %r" % (cls, key, cell, p))
    print("movers: patterns=%d files=%d %s" % (len(rows), len(files), " ".join(
        "%s=%d" % (k.lower(), v) for k, v in sorted(counts.items()))))
    print("movers: DONE cells=%d unexpected=%d" % (sum(counts.values()), len(unexpected)))
    return 1 if unexpected else 0


if __name__ == "__main__":
    sys.exit(main())
