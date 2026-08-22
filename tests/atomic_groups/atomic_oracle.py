#!/usr/bin/env python3
"""tests/atomic_groups/atomic_oracle.py — the libpcre2 side of
run_atomic_diff.sh, computed in ONE process.

WHY NOT tests/fuzz/pcre2_oracle, which every other differential in this tree
uses. That binary answers ONE (pattern, subject, startpos) per invocation, and
this differential asks about ~120,000 cells; at one process per cell the sweep
took MEASURED 44 cells per minute, i.e. about eleven hours. This computes every
cell the sweep needs in one pass and writes them to a TSV the shell reads.

IT IS THE SAME ORACLE, not a second one. `pcre2_ctypes.py`
(docs/design/eng_brep_measurements/probes/) is the project's committed ctypes
binding to the installed libpcre2-8 RUNTIME — the same library
tests/fuzz/pcre2_oracle dlopens, through the same documented function set
(compile / match / ovector / free). Appendix B.2 of the atomic-groups design
names it as the oracle of record for this module, and it is what generated
every expectation in tests/atomic_groups/*.rxt.

SKIPS LOUDLY when libpcre2 is absent (PC-3's pattern): exit 3 with a message,
never a silent empty file that the caller would read as "no cells to compare".

Usage: atomic_oracle.py <patterns-file> <subjects-dir> <out.tsv>
  patterns-file : one `<class>\t<pattern>` per line
  out.tsv       : `<pattern>\t<subject-name>\t<startpos>\t<answer>` where the
                  answer is spelled exactly as tests/fuzz/pcre2_oracle spells
                  it ("match S E" / "nomatch"), so the shell compares strings.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "docs", "design",
                                "eng_brep_measurements", "probes"))

try:
    import pcre2_ctypes as P
except Exception as e:                                     # noqa: BLE001
    sys.stderr.write("atomic_oracle: libpcre2 unavailable: %s\n" % e)
    sys.exit(3)


def answer(rx, subj, sp):
    r = rx.search(subj, sp)
    if r is None:
        return "nomatch"
    return "match %d %d" % (r[0][0], r[0][1])


def main():
    patfile, subjdir, out = sys.argv[1], sys.argv[2], sys.argv[3]

    subjects = []
    for name in sorted(os.listdir(subjdir)):
        with open(os.path.join(subjdir, name), "rb") as f:
            subjects.append((name, f.read().decode("latin-1")))

    n = 0
    with open(out, "w") as o:
        for line in open(patfile):
            line = line.rstrip("\n")
            if not line:
                continue
            cls, pat = line.split("\t", 1)
            try:
                rx = P.compile(pat)
            except Exception as e:                         # noqa: BLE001
                # A pattern libpcre2 REFUSES is a defect in the sweep's own
                # list, not a cell: every pattern here is meant to be legal
                # PCRE2. Reported loudly so it cannot become a silently
                # smaller denominator.
                sys.stderr.write("atomic_oracle: libpcre2 refused %r: %s\n"
                                 % (pat, e))
                return 2
            for name, subj in subjects:
                for sp in range(0, len(subj) + 1):
                    o.write("%s\t%s\t%d\t%s\n"
                            % (pat, name, sp, answer(rx, subj, sp)))
                    n += 1
    sys.stderr.write("atomic_oracle: %d cells\n" % n)
    return 0


sys.exit(main())
