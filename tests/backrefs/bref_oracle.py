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
                 [VLOOKBEHIND] (vlookbehind.md §6 gate 1) an optional MODE
                 column, `<key>\t<ngroups>\t<mode>\t<pattern>`, one of:
                   byte          libpcre2 options 0 (the default, absent column)
                   utf8          PCRE2_UTF; every subject must be valid UTF-8
                                 (an invalid one is a harness failure, exit 2)
                   utf8-invalid  PCRE2_UTF | PCRE2_MATCH_INVALID_UTF, pcrec's
                                 own reading of an ill-formed subject
                   utf8-clip     options 0 for a pcrec `-e utf8` artifact on
                                 ASCII subjects: D142 item 3's stated rule
                                 (match_api.md §9.4¶8, pcrec gives the byte
                                 answer where libpcre2 UTF clips)
                 In the three utf8 modes the startpos sweep covers character
                 boundaries only (no continuation byte), the rule the pcrec
                 side's cell list uses; a mid-character start is K50's domain.
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


MODES = {
    "byte": 0,
    "utf8": P.PCRE2_UTF,
    "utf8-invalid": P.PCRE2_UTF | P.PCRE2_MATCH_INVALID_UTF,
    "utf8-clip": 0,
}


def starts(subj, mode):
    """The startpos sweep: every offset, or character boundaries only."""
    if mode == "byte":
        return range(len(subj) + 1)
    return [i for i in range(len(subj) + 1)
            if i == len(subj) or (subj[i] & 0xC0) != 0x80]


def main():
    patfile, subjdir, out = sys.argv[1], sys.argv[2], sys.argv[3]

    subjects = []
    for name in sorted(os.listdir(subjdir)):
        with open(os.path.join(subjdir, name), "rb") as f:
            subjects.append((name, f.read()))

    n = 0
    with open(out, "w") as o:
        for line in open(patfile):
            line = line.rstrip("\n")
            if not line:
                continue
            f = line.split("\t", 3)
            if len(f) == 4 and f[2] in MODES:
                key, ng, mode, pat = f
            else:
                key, ng, pat = line.split("\t", 2)
                mode = "byte"
            ng = int(ng)
            try:
                rx = P.Compiled(pat if mode == "byte" else pat.encode("utf-8"),
                                MODES[mode])
            except Exception as e:                          # noqa: BLE001
                sys.stderr.write("bref_oracle: libpcre2 refuses %r: %s\n"
                                 % (pat, e))
                sys.exit(2)
            for sname, subj in subjects:
                if mode == "utf8":
                    try:
                        subj.decode("utf-8")
                    except UnicodeDecodeError:
                        sys.stderr.write("bref_oracle: subject %s is not "
                                         "valid UTF-8 in mode utf8\n" % sname)
                        sys.exit(2)
                if mode == "utf8-clip" and any(b >= 0x80 for b in subj):
                    sys.stderr.write("bref_oracle: subject %s is not ASCII "
                                     "in mode utf8-clip\n" % sname)
                    sys.exit(2)
                for sp in starts(subj, mode):
                    o.write("%s\t%s\t%d\t%s\n"
                            % (key, sname, sp, answer(rx, subj, sp, ng)))
                    n += 1
    sys.stderr.write("bref_oracle: %d cells\n" % n)


if __name__ == "__main__":
    main()
