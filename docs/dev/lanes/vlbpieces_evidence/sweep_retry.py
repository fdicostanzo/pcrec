#!/usr/bin/env python3
"""vlbpieces retry-order sweep: NON-ATOMIC lookbehinds whose single variable
piece sits beside a fixed piece with equal-width alternatives (distinct
groups), followed by back-reference follows that accept only some of the
lookbehind's successes. The piece walk tries the fixed piece's choices as
OUTER loops (it is walked first); PCRE2 tries them as INNER ones.

Usage: sweep_retry.py PROBE_BINARY OUT.tsv
"""
import itertools, subprocess, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import model

BODIES = [
    "(a|aa)(?:(b)|(b))", "(?:(b)|(b))(a|aa)", "(a{1,2})(?:(a)|(a))",
    "(?:(a)|(a))(a{0,2})", "(a|ab)(?:(b)|(a))", "(?:(a)|(b))(b?)",
]
FOLLOWS = ["\\1", "\\2", "\\3", "\\1\\2", "(?:\\2|\\1\\1)", "(?:\\3|\\1b)",
           "(?:\\3\\1|\\2b)", "(?:\\2\\1a|\\3)"]
SUBJECTS = ["".join(t) for n in range(8) for t in itertools.product("ab", repeat=n)]

def main():
    probe, outp = sys.argv[1], sys.argv[2]
    cells = []
    for body in BODIES:
        P = model.Parser(body); P.alt(); ng = P.ng
        for fol in FOLLOWS:
            if any(int(d) > ng for d in fol if d.isdigit()): continue
            for form, pat in (("nonatomic", "(?<*%s)%s" % (body, fol)),
                              ("pos", "(?<=%s)%s" % (body, fol))):
                for s in SUBJECTS:
                    cells.append((body, form, pat, s))
    text = "".join("%s\t%s\n" % (c[2], c[3]) for c in cells)
    pc = subprocess.run([probe, "m"], input=text, capture_output=True, text=True).stdout.splitlines()
    assert len(pc) == len(cells)
    with open(outp, "w") as f:
        f.write("body\tform\tpattern\tsubject\tpcre2\trange\tpieces\ttrim\n")
        for c, line in zip(cells, pc):
            ref = line.split("\t")[2]
            f.write("\t".join(c) + "\t%s\t%s\t%s\t%s\n" % (ref, model.run("range", c[2], c[3]),
                                                          model.run("pieces", c[2], c[3]),
                                                          model.run("trim", c[2], c[3])))

if __name__ == "__main__":
    main()
