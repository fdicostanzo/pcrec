#!/usr/bin/env python3
"""check.py CASE [--cc gcc-16] -- correctness: every arm of CASE against
libpcre2 and against each other over out/subjects.bin x out/cases.tsv.

  arms: bb (today's default artifact), bd (raised-cap, when present),
        bv (forced VM), ia/ib/ic (island twin with kit4 / page3w / bitmap1)
Writes out/<case>/check.tsv (one summary row per arm) and mismatch samples to
out/<case>/mismatch_<arm>.txt.
"""
import collections
import os
import subprocess
import sys

import oracle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# case -> (pattern for libpcre2, flags)
PATTERNS = {
    "c1": (r"[\x{100}-\x{2000}]+", "UTF|MIU"),
    "nd": (r"\p{Nd}+", "UTF|MIU"),
    "l": (r"\p{L}+", "UTF|MIU"),
    "xwd": (r"\p{Xwd}+", "UTF|MIU"),
    "x1": (r"(?<=[\x{100}-\x{2000}])x", "UTF|MIU"),
    "x2": (r"(?<![\w\x{C0}-\x{24F}\x{370}-\x{52F}])[\w\x{C0}-\x{24F}\x{370}-\x{52F}]+(?![\w\x{C0}-\x{24F}\x{370}-\x{52F}])", "UTF|MIU"),
    "x3": (r"\b\w+\b", "UTF|UCP|MIU"),
    "x3b": (r"\b\p{Xwd}+\b", "UTF|UCP|MIU"),
}

ARMFILES = [("bb", "base.c"), ("bd", "bigcap.c"), ("bv", "vm.c"),
            ("ia", "tw_kit4.c"), ("ib", "tw_page3w.c"), ("ic", "tw_bitmap1.c")]


def arms_for(case):
    d = os.path.join(OUT, case)
    return [(a, os.path.join(d, f)) for a, f in ARMFILES if os.path.exists(os.path.join(d, f))]


def build(case, cc, arms, exe, extra=()):
    d = os.path.join(OUT, case)
    hdr = ["#include <stddef.h>", "typedef int (*sfn)(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);"]
    for a, _ in arms:
        hdr.append("int %s_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);" % a)
    hdr.append("#define NARMS %d" % len(arms))
    hdr.append("static const struct { const char *name; sfn fn; } arms[] = { %s };" %
               ", ".join('{"%s", %s_search}' % (a, a) for a, _ in arms))
    open(os.path.join(d, "arms_gen.h"), "w").write("\n".join(hdr) + "\n")
    cmd = [cc, "-O2", "-std=gnu11", "-w", "-I" + d, os.path.join(HERE, "driver.c")] + [p for _, p in arms] + ["-o", exe] + list(extra)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit("build failed")


def main(case, cc="gcc-16", pattern=None, flags=None):
    d = os.path.join(OUT, case)
    pat, fl = PATTERNS[case]
    if pattern:
        pat, fl = pattern, flags
    arms = arms_for(case)
    exe = os.path.join(d, "check_exe")
    build(case, cc, arms, exe)
    subs = oracle.read_subjects(os.path.join(OUT, "subjects.bin"))
    cases = oracle.read_cases(os.path.join(OUT, "cases.tsv"))
    lib = oracle.load()
    ora = {(i, f): (rc, s, e) for i, f, rc, s, e in oracle.answers(lib, pat.encode(), fl, subs, cases)}
    r = subprocess.run([exe, os.path.join(OUT, "subjects.bin"), os.path.join(OUT, "cases.tsv")],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("driver failed rc=%d\n%s" % (r.returncode, r.stderr[-2000:]))
    got = collections.defaultdict(dict)
    for line in r.stdout.splitlines():
        a, i, f, rc, s, e = line.split("\t")
        got[a][(int(i), int(f))] = (rc, s, e)
    nmatch = sum(1 for v in ora.values() if v[0] == "1")
    rows = []
    print("case %s: %d cases, oracle libpcre2 %s: %d matches, %d errors" %
          (case, len(cases), oracle.version(lib), nmatch, sum(1 for v in ora.values() if v[0].startswith("E"))))
    names = [a for a, _ in arms]
    for a in names:
        bad = [k for k in ora if got[a][k] != (ora[k][0], str(ora[k][1]), str(ora[k][2]))]
        rows.append((case, a, len(cases), len(bad), "vs libpcre2"))
        print("  %-3s vs libpcre2: %d / %d differ" % (a, len(bad), len(cases)))
        if bad:
            with open(os.path.join(d, "mismatch_%s.txt" % a), "w") as f:
                for k in bad[:200]:
                    s = subs[k[0]]
                    f.write("subject=%s from=%d got=%s oracle=%s\n" % (s.hex(), k[1], got[a][k], ora[k]))
    for a in names:
        for b in names:
            if a < b:
                bad = [k for k in ora if got[a][k] != got[b][k]]
                rows.append((case, a + "==" + b, len(cases), len(bad), "arm vs arm"))
                print("  %s vs %s: %d differ" % (a, b, len(bad)))
    with open(os.path.join(d, "check.tsv"), "w") as f:
        f.write("case\tcomparison\tcases\tdiffering\tkind\n")
        for r_ in rows:
            f.write("\t".join(map(str, r_)) + "\n")
    return rows


if __name__ == "__main__":
    main(sys.argv[1])
