#!/usr/bin/env python3
"""vlbrev3 sweep: vlbpieces' two sweeps (the same bodies, forms and
subjects, imported from ../vlbpieces_evidence) re-run through the `cursor`
evaluator (rev 3 §5.1) and the `range` control, against libpcre2 10.46.

Usage: sweep_cursor.py PROBE_BINARY OUT.tsv
Prints one summary line per sweep: cells, cursor diffs, range diffs.
"""
import os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import model                                   # this lane's copy (has `cursor`)
sys.path.insert(1, os.path.join(here, "..", "vlbpieces_evidence"))
import sweep, sweep_retry                      # their BODIES/forms/SUBJECTS


def cells_main():
    out = []
    for body in sweep.BODIES:
        nvar, exposed, ncap = sweep.features(body)
        for form, pat in sweep.forms(body, ncap):
            for s in sweep.SUBJECTS:
                out.append(("main", form, pat, s))
    return out


def cells_retry():
    out = []
    for body in sweep_retry.BODIES:
        P = model.Parser(body); P.alt(); ng = P.ng
        for fol in sweep_retry.FOLLOWS:
            if any(int(d) > ng for d in fol if d.isdigit()): continue
            for form, pat in (("nonatomic", "(?<*%s)%s" % (body, fol)),
                              ("pos", "(?<=%s)%s" % (body, fol))):
                for s in sweep_retry.SUBJECTS:
                    out.append(("retry", form, pat, s))
    return out


def main():
    probe, outp = sys.argv[1], sys.argv[2]
    cells = cells_main() + cells_retry()
    text = "".join("%s\t%s\n" % (c[2], c[3]) for c in cells)
    pc = subprocess.run([probe, "m"], input=text, capture_output=True, text=True).stdout.splitlines()
    assert len(pc) == len(cells), (len(pc), len(cells))
    tally = {}
    with open(outp, "w") as f:
        f.write("sweep\tform\tpattern\tsubject\tpcre2\tcursor\trange\n")
        for c, line in zip(cells, pc):
            ref = line.split("\t")[2]
            cu, rg = model.run("cursor", c[2], c[3]), model.run("range", c[2], c[3])
            t = tally.setdefault(c[0], [0, 0, 0])
            t[0] += 1; t[1] += cu != ref; t[2] += rg != ref
            f.write("\t".join(c) + "\t%s\t%s\t%s\n" % (ref, cu, rg))
    for k, (n, dc, dr) in sorted(tally.items()):
        print("%s sweep: %d cells; cursor differs from libpcre2 on %d; range (control) on %d"
              % (k, n, dc, dr))


if __name__ == "__main__":
    main()
