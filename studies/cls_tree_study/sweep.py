#!/usr/bin/env python3
"""sweep.py — build, EXHAUSTIVELY VERIFY, and SIZE one kit matcher per
(population, set, lam) cell.

Three things happen per cell and they are deliberately separate:

  SIZE      the matcher alone, compiled to its own `.o` with external
            linkage, measured with `size` — so `.text` and `.rodata` are the
            matcher's and nothing else's.
  VERIFY    the same matcher linked against a REFERENCE built by a different
            construction (a flat binary search over the whole interval list,
            emit.reference) and compared on EVERY code point 0..0x10FFFF.
            Not a sample.  1,114,112 cells per matcher.
  RECORD    one TSV row.

The verification is the study's own control and it is the strong form: a
disagreement anywhere in the code-point space fails the cell.  It is what
lets the memo say the representations are answer-identical rather than
believed to be.
"""

import argparse
import os
import re
import subprocess
import sys
import time

import clsets
import emit
import section

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
CC = os.environ.get("CC", "gcc-16")
CFLAGS = ["-O2", "-std=gnu11", "-Wall", "-Wextra"]

LAMS = [0.0, 4.0, 16.0, 64.0, 256.0, 1e9]
LAMNAME = {0.0: "size", 4.0: "n1size", 16.0: "mid", 64.0: "n1speed",
           256.0: "speed", 1e9: "maxspeed"}

VERIFY_MAIN = r"""
#include <stdio.h>
int cls_kit(unsigned cp);
static int cls_ref(unsigned cp);
int main(void)
{
    unsigned long bad = 0, mem = 0;
    for (unsigned cp = 0; cp <= 0x10FFFFu; cp++) {
        int a = cls_kit(cp) ? 1 : 0, b = cls_ref(cp) ? 1 : 0;
        mem += (unsigned long)b;
        if (a != b) { if (bad < 4) fprintf(stderr, "MISMATCH cp=U+%04X kit=%d ref=%d\n", cp, a, b); bad++; }
    }
    printf("%lu %lu\n", bad, mem);
    return bad ? 1 : 0;
}
"""


def sanitize(name):
    return "".join(c if c.isalnum() else "_" for c in name)


def build_cell(outdir, tag, iv, lam, dp="c"):
    P = section.partition_c if dp == "c" else section.partition
    secs, ro_model, ops, forms = P(iv, lam)
    src, ro = emit.emit("cls_kit", iv, secs, forms, static=False)
    mpath = os.path.join(outdir, tag + "_m.c")
    with open(mpath, "w") as f:
        f.write(emit.PRELUDE + src)
    opath = os.path.join(outdir, tag + "_m.o")
    r = subprocess.run([CC] + CFLAGS + ["-c", mpath, "-o", opath],
                       capture_output=True, text=True)
    if r.returncode:
        return None, "compile: " + r.stderr.strip().splitlines()[0]

    text, rodata, data, bss = obj_sizes(opath)

    vpath = os.path.join(outdir, tag + "_v.c")
    with open(vpath, "w") as f:
        f.write(emit.PRELUDE + emit.reference("cls_ref", iv) + VERIFY_MAIN)
    bpath = os.path.join(outdir, tag + "_v")
    r = subprocess.run([CC, "-O1", "-std=gnu11", vpath, opath, "-o", bpath],
                       capture_output=True, text=True)
    if r.returncode:
        return None, "link: " + r.stderr.strip().splitlines()[0]
    r = subprocess.run([bpath], capture_output=True, text=True)
    verdict = "PASS" if r.returncode == 0 else "FAIL"
    bad = r.stdout.split()[0] if r.stdout.split() else "?"

    return dict(sections=len(secs), forms=forms, text=text, rodata=rodata,
                ro_model=ro, ops=ops, verify=verdict, mismatches=bad), None


def obj_sizes(opath):
    """Section bytes of a .o.  Uses `size -m` on darwin (Mach-O) and falls
    back to `size -A` elsewhere; both are parsed rather than assumed."""
    r = subprocess.run(["size", "-m", opath], capture_output=True, text=True)
    if r.returncode == 0 and "__TEXT" in r.stdout:
        # darwin/Mach-O: `Section (__SEG, __sect): N`.  Read-only data lands
        # in __TEXT,__const or __DATA_CONST,__const depending on relocation,
        # so both are summed; __eh_frame is excluded (it is not the matcher).
        vals = {}
        for seg, sect, n in re.findall(
                r"Section \((__\w+), (__\w+)\):\s+(\d+)", r.stdout):
            vals[(seg, sect)] = int(n)
        text = sum(v for (s, c), v in vals.items() if c == "__text")
        ro = sum(v for (s, c), v in vals.items()
                 if c in ("__const", "__cstring", "__literal8"))
        data = sum(v for (s, c), v in vals.items() if c == "__data")
        bss = sum(v for (s, c), v in vals.items() if c == "__bss")
        return text, ro, data, bss
    r = subprocess.run(["size", "-A", opath], capture_output=True, text=True)
    vals = {}
    for line in r.stdout.splitlines():
        p = line.split()
        if len(p) >= 2 and p[0].startswith("."):
            try:
                vals[p[0]] = int(p[1])
            except ValueError:
                pass
    return (vals.get(".text", 0), vals.get(".rodata", 0),
            vals.get(".data", 0), vals.get(".bss", 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("population", choices=["uprops", "k53", "byteclasses"])
    ap.add_argument("--out", default=None)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--lams", default=None)
    ap.add_argument("--dp", choices=["py", "c"], default="c",
                    help="which implementation of the sectioning "
                         "DP runs (crosscheck.py compares them)")
    args = ap.parse_args()

    lams = LAMS if not args.lams else [float(x) for x in args.lams.split(",")]
    pop = clsets.population(args.population)
    if args.limit:
        pop = pop[:args.limit]
    outdir = args.out or os.path.join(HERE, "build", args.population)
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(RES, exist_ok=True)

    tsv = os.path.join(RES, "sweep_%s.tsv" % args.population)
    with open(tsv, "w") as out:
        out.write("# population=%s cc=%s cflags=%s dp=%s date=%s\n"
                  % (args.population, CC, " ".join(CFLAGS), args.dp,
                     time.strftime("%Y-%m-%dT%H:%M:%S")))
        out.write("set\tintervals\tmembers\tspan\tlam\tpolicy\tsections\t"
                  "text\trodata\ttotal\tmodel_ro\tmodel_ops\tverify\t"
                  "mismatches\tdiscovery_s\tforms\n")
        for name, iv in pop:
            tg = sanitize(name)
            members = sum(h - l + 1 for l, h in iv)
            sp = iv[-1][1] - iv[0][0] + 1
            for lam in lams:
                P = section.partition_c if args.dp == "c" \
                    else section.partition
                t0 = time.perf_counter()
                P(iv, lam)
                disc = time.perf_counter() - t0
                tag = "%s_l%s" % (tg, LAMNAME.get(lam, str(lam)))
                row, err = build_cell(outdir, tag, iv, lam, args.dp)
                if row is None:
                    sys.stderr.write("CELL FAIL %s lam=%s: %s\n"
                                     % (name, lam, err))
                    continue
                hist = {}
                for f in row["forms"]:
                    hist[f] = hist.get(f, 0) + 1
                out.write("%s\t%d\t%d\t%d\t%g\t%s\t%d\t%d\t%d\t%d\t%d\t%.1f\t"
                          "%s\t%s\t%.6f\t%s\n"
                          % (name, len(iv), members, sp, lam,
                             LAMNAME.get(lam, str(lam)), row["sections"],
                             row["text"], row["rodata"],
                             row["text"] + row["rodata"],
                             row["ro_model"], row["ops"], row["verify"],
                             row["mismatches"], disc,
                             ",".join("%s:%d" % kv for kv in
                                      sorted(hist.items()))))
                out.flush()
    print("wrote", tsv)


if __name__ == "__main__":
    main()
