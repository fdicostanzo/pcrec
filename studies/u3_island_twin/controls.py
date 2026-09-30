#!/usr/bin/env python3
"""controls.py -- FAILING-DIRECTION controls for check.py.  Each control
plants one defect into a copy of a twin's C source; check.py must then report
a nonzero difference against libpcre2.  A check that stays green under its
control is a check that cannot see the defect.

  overlong    the decoder stops rejecting overlong forms
  surrogate   the decoder stops rejecting U+D800..DFFF
  bot-in-set  an ill-formed byte is read as a member of the set
  back-len    the repaired back_step's length test removed (s3.5 control)
  edge        the set predicate's upper bound off by one
  seed        the forward seed from the char before `from` ignored
  h7          the accept-before-a-non-member (H7) column zeroed
"""
import os
import re
import shutil
import sys

import check

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def mut_overlong(s):
    return s.replace("if (v < floor || v > 0x10FFFFu", "if (v > 0x10FFFFu")


def mut_surrogate(s):
    return s.replace(" || (v >= 0xD800u && v <= 0xDFFFu)) return 0;", ") return 0;")


def mut_bot(s):
    return re.sub(r": (\d)u\)", lambda m: ": 1u)" if m.group(1) == "2" else m.group(0), s)


def mut_back(s):
    return s.replace("if (len && q + len == e) return len;", "if (len) return len;")


def mut_edge(s):
    return s.replace("7936u) return 0", "7935u) return 0")


def mut_seed(s):
    return re.sub(r"st = (\w+)_seed_isl\[v\];", "st = 0;", s)


def mut_h7(s):
    def zero(m):
        return m.group(1) + ", ".join("0" for _ in m.group(2).split(",")) + m.group(3)
    return re.sub(r"(static const unsigned char \w+_f_acci\[\d+\] = \{\s*)([^}]*?)(,?\s*\};)", zero, s)


CONTROLS = [
    ("overlong", "c1", mut_overlong), ("surrogate", "c3", mut_surrogate),
    ("bot-in-set", "c1", mut_bot), ("back-len", "c1", mut_back), ("edge", "c1", mut_edge),
    ("overlong", "x2", mut_overlong), ("overlong", "x1", mut_overlong), ("bot-in-set", "x2", mut_bot), ("back-len", "x2", mut_back),
    ("seed", "x1", mut_seed), ("seed", "x2", mut_seed), ("h7", "x2", mut_h7),
    ("back-len", "x1", mut_back),
]


def main():
    rows = []
    for name, case, mut in CONTROLS:
        d = os.path.join(OUT, "ctl_%s_%s" % (case, name))
        os.makedirs(d, exist_ok=True)
        src = open(os.path.join(OUT, case, "tw_kit4.c")).read()
        new = mut(src)
        assert new != src, "control %s/%s did not change the source" % (case, name)
        open(os.path.join(d, "tw_kit4.c"), "w").write(new)
        pat, fl = check.PATTERNS[case]
        sys.stdout.flush()
        res = check.main("ctl_%s_%s" % (case, name), pattern=pat, flags=fl)
        differing = [r for r in res if r[4] == "vs libpcre2"][0][3]
        rows.append((case, name, differing, "DETECTED" if differing else "NOT DETECTED"))
    with open(os.path.join(HERE, "results", "controls.tsv"), "w") as f:
        f.write("case\tcontrol\tcases_differing_from_libpcre2\tverdict\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    print()
    for r in rows:
        print(*r, sep="\t")


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    main()
