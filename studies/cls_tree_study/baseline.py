#!/usr/bin/env python3
"""baseline.py — WHAT PCREC EMITS TODAY for the same sets, so the kit has
something real to be compared against.

For each distinct set in the uprops population this picks one `\\p` spelling
that denotes it and compiles that pattern with the WORKTREE's own
`build/pcrec` under `--features unicode-props -e utf8`, recording the emitted
byte count and the compiler's own code/total split from its large-artifact
accounting.  Nothing is hand-computed: the number is what the shipped
compiler writes to disk today.

`-e utf8` is not optional to the comparison.  Under `byte` every one of these
sets is clamped to Latin-1 and tiny — which is exactly the trap
[K53-SELRETRY] §4 recorded when a codegen census compiled `\\p` corpus lines
with no encoding and concluded the `\\p` family was not the population.
"""

import os
import re
import subprocess
import sys
import time

import clsets

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
PCREC = os.path.join(REPO, "build", "pcrec")
RES = os.path.join(HERE, "results")

NSPREFIX = {1: "", 2: "sc=", 4: "scx="}


def set_to_name():
    """Distinct set -> one `\\p{...}` body that denotes it.  Prefers the bare
    namespace; falls back to `sc=`/`scx=`."""
    ivs, rows = clsets._parse_inc()
    out = {}
    for name, ns, off, n, cio, cin in rows:
        key = clsets._slice(ivs, off, n)
        if not key or key in out:
            continue
        for bit in (1, 2, 4):
            if ns & bit:
                out[key] = NSPREFIX[bit] + name
                break
    return out


def main():
    if not os.path.exists(PCREC):
        sys.exit("baseline: %s missing — run `make -j4 CC=gcc-16` in the "
                 "worktree first" % PCREC)
    tmp = os.path.join(HERE, "build", "baseline")
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(RES, exist_ok=True)
    names = set_to_name()

    only = set(sys.argv[1:]) or None
    path = os.path.join(RES, "baseline.tsv")
    with open(path, "w") as out:
        out.write("# pcrec=%s flags=--features unicode-props -e utf8 date=%s\n"
                  % (PCREC, time.strftime("%Y-%m-%dT%H:%M:%S")))
        out.write("set\tbody\tintervals\tmembers\temit_bytes\tcode_bytes\t"
                  "obj_text\tobj_rodata\tobj_total\tpcrec_s\tstatus\n")
        for name, iv in clsets.uprops():
            if only and name not in only:
                continue
            body = names.get(tuple(iv))
            if body is None:
                out.write("%s\t-\t%d\t%d\t\t\t\t\t\t\tNONAME\n"
                          % (name, len(iv),
                             sum(h - l + 1 for l, h in iv)))
                continue
            cpath = os.path.join(tmp, "b.c")
            t0 = time.perf_counter()
            r = subprocess.run(
                ["timeout", "120", PCREC, "--features", "unicode-props",
                 "-e", "utf8", "-p", "rx", "--warn-emit-bytes=100000000",
                 "-o", cpath, "\\p{%s}" % body],
                capture_output=True, text=True)
            el = time.perf_counter() - t0
            if r.returncode != 0:
                msg = (r.stderr.strip().splitlines() or ["?"])[-1][:90]
                out.write("%s\t%s\t%d\t%d\t\t\t\t\t\t%.3f\tREFUSED: %s\n"
                          % (name, body, len(iv),
                             sum(h - l + 1 for l, h in iv), el, msg))
                out.flush()
                continue
            nbytes = os.path.getsize(cpath)
            # APPLES TO APPLES: the kit is measured as OBJECT bytes
            # (.text+.rodata of its own `.o`), so the baseline must be too —
            # comparing an emitted-SOURCE byte count against an object byte
            # count would flatter the kit by whatever the comments weigh.
            import sweep
            oo = os.path.join(tmp, "b.o")
            rc = subprocess.run(["timeout", "300", os.environ.get("CC", "gcc-16"),
                                 "-O2", "-std=gnu11", "-c", cpath, "-o", oo],
                                capture_output=True, text=True)
            if rc.returncode == 0:
                otext, orod, _, _ = sweep.obj_sizes(oo)
            else:
                otext = orod = -1
            # the compiler's own code/total split, asked for directly
            r2 = subprocess.run(
                ["timeout", "120", PCREC, "--features", "unicode-props",
                 "-e", "utf8", "-p", "rx", "--warn-emit-bytes=1",
                 "-o", cpath, "\\p{%s}" % body],
                capture_output=True, text=True)
            m = re.search(r"\((\d+) of code\)", r2.stderr)
            code = m.group(1) if m else ""
            out.write("%s\t%s\t%d\t%d\t%d\t%s\t%d\t%d\t%d\t%.3f\tOK\n"
                      % (name, body, len(iv), sum(h - l + 1 for l, h in iv),
                         nbytes, code, otext, orod, otext + orod, el))
            out.flush()
    print("wrote", path)


if __name__ == "__main__":
    main()
