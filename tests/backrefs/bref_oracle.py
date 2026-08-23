#!/usr/bin/env python3
"""tests/backrefs/bref_oracle.py — the libpcre2 side of run_backref_diff.sh
and run_dupnames_diff.sh, computed in ONE process, with the GROUP SPANS.

IT IS THE SAME ORACLE the rest of the tree uses, not a second one:
`pcre2_ctypes.py` (docs/design/eng_brep_measurements/probes/) is the project's
committed ctypes binding to the installed libpcre2-8 RUNTIME — the same
library tests/fuzz/pcre2_oracle dlopens, through the same documented function
set. It is what generated every expectation in tests/backrefs/*.rxt too.

WHY IT REPORTS GROUPS where atomic_oracle.py reports only the span: for this
module the group spans are the sharper detector. R32 E1's counterexample
family — a reference inside a RE-ENTERED group — contains subjects on which
the outer span agrees between publish-at-open and publish-at-close and the
GROUP does not, so a differential comparing `caps[0]` alone would report
agreement over exactly the population publish-at-close exists for.

libpcre2 TRUNCATES trailing unset pairs (`pcre2_match` returns the highest
captured pair plus one), so the group list is PADDED to the requested count
with `-1 -1`. That padding is oracle-side and one-directional: a pair pcrec
reports as unset and libpcre2 does not report at all is agreement, not a
divergence about shape.

SKIPS LOUDLY when libpcre2 is absent (PC-3's pattern): exit 3 with a message,
never a silent empty file the caller would read as "no cells to compare".

Usage: bref_oracle.py <patterns.tsv> <subjects-dir> <out.tsv>
  patterns.tsv : `<key>\t<ngroups>\t<pattern>` per line, where <ngroups> is
                 how many capture pairs the artifact will report (1 fewer than
                 its RX_NCAPS; 0 for a --no-captures artifact).
  out.tsv      : `<key>\t<subject-name>\t<startpos>\t<answer>`, the answer
                 spelled exactly as tests/backrefs/bref_batch.c spells it.
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
    sys.stderr.write("bref_oracle: libpcre2 unavailable: %s\n" % e)
    sys.exit(3)


def answer(rx, subj, sp, ng):
    r = rx.search(subj, sp)
    if r is None:
        return "nomatch"
    out = ["match %d %d" % (r[0][0], r[0][1])]
    groups = list(r[1])
    while len(groups) < ng:
        groups.append(None)
    for g in groups[:ng]:
        if g is None:
            out.append("-1 -1")
        else:
            out.append("%d %d" % (g[0], g[1]))
    return " ".join(out)


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
            key, ng, pat = line.split("\t", 2)
            ng = int(ng)
            try:
                rx = P.Compiled(pat)
            except Exception as e:                          # noqa: BLE001
                sys.stderr.write("bref_oracle: libpcre2 refuses %r: %s\n"
                                 % (pat, e))
                sys.exit(2)
            for sname, subj in subjects:
                for sp in range(len(subj) + 1):
                    o.write("%s\t%s\t%d\t%s\n"
                            % (key, sname, sp, answer(rx, subj, sp, ng)))
                    n += 1
    sys.stderr.write("bref_oracle: %d cells\n" % n)


if __name__ == "__main__":
    main()
