#!/usr/bin/env python3
"""vlbpieces sweep: bodies x forms x every {a,b} subject up to length 6.
Each cell runs through libpcre2 10.46 (probe, the oracle) and both model
evaluators (model.py). Writes one TSV row per cell with the body's
compile-time features, so a candidate admission rule can be tested
against the whole population.

Usage: sweep.py PROBE_BINARY OUT.tsv
"""
import itertools, subprocess, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
import model

BODIES = [
    # fixed only (the one-length row's class)
    "ab", "(a)b", "(?:(a)|(b))a",
    # one variable piece
    "a{1,3}", "ba{0,2}", "a{0,2}b", "(a){1,3}", "(a{1,2})b", "b(a{1,2})",
    "(?:a|ab)", "(?:(a)|(ab))", "(?:(ab)|(a))b", "(?:(a)|(b)|(ab))",
    "((?:a|b){1,3})", "(?:(a)|(b)){1,3}", "(b)(?:a|ba)", "(?>a|ab)b",
    "(?>a|ab)", "a{1,2}+", "(?>(a)|(ab))", "(?:a|b)?(b)", "(a|ab)",
    "((?:ab)?)b", "(a{0,2}?)", "(?:(a)|(a)){1,2}", "(?:(a)|(a))(a?)",
    # a group that CROSSES from the variable piece into the trailing fixed run
    "(a{1,2}b)", "(a?(b))a", "(b{0,1}a)a", "((?:a|ab)b)", "(?:(a)|(ab))(b)a",
    # one variable piece whose inside varies (nested)
    "(?:a{1,2}b){1,2}", "(?:(a{1,2})b){1,2}", "(?:ab?){1,3}",
    "((?:a|ab){1,2})", "(?:(a)|(ab)){1,2}", "((?:a|ab)b?)",
    # two or more variable pieces
    "a{1,2}b{1,2}", "(a{1,2})(a{1,2})", "(a{1,2})(b{1,2})", "a{0,2}(a)a{0,2}",
    "(a{0,2})b?", "a?(b?)a?", "(a?)(b?)", "(?:a|ab)(b?)", "(a|ab)(b|bb)",
    "(?>a|ab)(b?)", "(a{1,2})b(a{0,1})", "a{1,2}(b)(?:a|ab)",
    "((?:ab)?)(b?)", "(a{1,2}?)(a{1,2})", "a{1,2}?b{0,1}", "(a?)a(a?)",
    "(?:a|b)?(?:b|ab)?", "a{0,2}b{0,2}", "(?:(a)|(ab))(?:(b)|(bb))",
    # two or more variable pieces, every group right of the last one
    "a{1,2}b{0,1}(a)", "(?:a|ab)b?(b)", "a?b?(ab)", "a{0,2}a{0,2}(a)",
    # assertions and nested lookaround
    "\\ba{1,2}", "^a{0,2}(b?)", "a{1,2}(?=b)", "(?<=b)a{1,2}", "(?<=(b))a{0,2}",
    "(?!a)(?:a|b){1,2}", "(?<=(a|bb))(a?)(b?)",
    # atomic or possessive with another variable piece
    "(?>a{1,2})(b{0,1})", "(a{1,2}+)(a?)", "(?>(a|ab))(b?)", "(a?+)(a{0,2})",
]

SUBJECTS = ["".join(t) for n in range(7) for t in itertools.product("ab", repeat=n)]


def features(body):
    P = model.Parser("(?:" + body + ")")
    root = P.alt()
    brs = root[1] if root[0] == "alt" else [root]
    nvar_max, exposed, ncap = 0, False, P.ng
    for b in brs:
        items = model.flatten(b)
        var = [i for i, it in enumerate(items)
               if it[0] not in ("open", "close") and model.width(it)[0] != model.width(it)[1]]
        nvar_max = max(nvar_max, len(var))
        last = var[-1] if var else -1
        for i, it in enumerate(items):
            # a group inside an item, or an open marker, at or left of the last
            # variable item has offsets that depend on the walk's choices
            has_cap = it[0] == "open" or (it[0] not in ("close",) and "'cap'" in repr(it))
            if has_cap and i <= last:
                exposed = True
    return nvar_max, exposed, ncap


def forms(body, ncap):
    out = [("pos", "(?<=%s)" % body), ("neg", "(?<!%s)" % body)]
    if ncap:
        out.append(("nonatomic", "(?<*%s)\\1" % body))
        if ncap >= 2:
            out.append(("nonatomic", "(?<*%s)\\2" % body))
    else:
        out.append(("nonatomic", "(?<*%s)b" % body))
    return out


def main():
    probe, outp = sys.argv[1], sys.argv[2]
    cells = []
    for body in BODIES:
        nvar, exposed, ncap = features(body)
        for form, pat in forms(body, ncap):
            for s in SUBJECTS:
                cells.append((body, form, nvar, exposed, ncap, pat, s))
    text = "".join("%s\t%s\n" % (c[5], c[6]) for c in cells)
    pc = subprocess.run([probe, "m"], input=text, capture_output=True, text=True).stdout.splitlines()
    assert len(pc) == len(cells), (len(pc), len(cells))
    with open(outp, "w") as f:
        f.write("body\tform\tnvar\texposed\tncap\tpattern\tsubject\tpcre2\trange\tpieces\ttrim\n")
        for c, line in zip(cells, pc):
            ref = line.split("\t")[2]
            r = model.run("range", c[5], c[6])
            p = model.run("pieces", c[5], c[6])
            tr = model.run("trim", c[5], c[6])
            f.write("\t".join(map(str, c)) + "\t%s\t%s\t%s\t%s\n" % (ref, r, p, tr))


if __name__ == "__main__":
    main()
