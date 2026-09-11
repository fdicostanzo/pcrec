#!/usr/bin/env python3
"""calibrate_direct.py — per-form `.text` measured DIRECTLY, as a slope.

`calibrate.py` recovers the same constants by regression over the real sweep
rows.  That fit is excellent (R2 = 0.9996) but it can only identify a form
the population actually USES, and the code-point populations choose `CUBES`
zero times — so its regression coefficient is not a measurement, it is an
unidentified column that OLS happened to return 0 for.

This file measures each form on its own terms.  For form F it builds a
synthetic set of N groups each shaped so F fits, forces the sectioning to be
N sections of F, compiles, and sizes.  The per-section cost is taken as a
SLOPE between two values of N, which cancels the function's fixed overhead
and the dispatch tree's own growth is absorbed into the same slope — exactly
the quantity the DP needs, since the DP charges per section.

Two independent routes to one set of constants, and they are compared.  A
form whose two estimates disagree materially is reported, not averaged.
"""

import os
import subprocess
import sys

import emit
import kit

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.environ.get("CC", "gcc-16")
FORMS = ["ALL", "RANGES", "CUBES", "MASK64", "BITMAP", "PAGE64", "BSEARCH"]


def make_set(form, n):
    """A set of `n` groups, each a section the named form fits — and, where it
    matters, a section that form is the RIGHT answer for.  Groups are spaced
    far apart so the sectioning is unambiguous."""
    iv, secs, stride = [], [], 1 << 16
    for g in range(n):
        b = 0x1000 + g * stride
        start = len(iv)
        if form == "ALL":
            iv.append((b, b + 40))
        elif form == "RANGES":
            iv += [(b, b + 3), (b + 8, b + 11), (b + 16, b + 19)]
        elif form == "CUBES":
            # {x, x^0x20} over four bases: one cube, care = ~0x20.
            for q in range(4):
                x = b + q * 0x40
                iv += [(x, x), (x + 0x20, x + 0x20)]
        elif form == "MASK64":
            iv += [(b, b), (b + 7, b + 9), (b + 20, b + 22), (b + 40, b + 62)]
        elif form == "BITMAP":
            for q in range(0, 900, 60):
                iv.append((b + q, b + q + 7))
        elif form == "PAGE64":
            for q in range(0, 4000, 64):
                iv.append((b + q, b + q + 5))
        elif form == "BSEARCH":
            for q in range(0, 600, 40):
                iv.append((b + q, b + q + 3))
        secs.append((start, len(iv) - 1))
    return iv, secs, [form] * n


def text_of(iv, secs, forms, tag, outdir):
    src, _ro = emit.emit("cls_kit", iv, secs, forms, static=False)
    cpath = os.path.join(outdir, tag + ".c")
    with open(cpath, "w") as f:
        f.write(emit.PRELUDE + src)
    opath = os.path.join(outdir, tag + ".o")
    r = subprocess.run([CC, "-O2", "-std=gnu11", "-w", "-c", cpath,
                        "-o", opath], capture_output=True, text=True)
    if r.returncode:
        return None, None, (r.stderr.strip().splitlines() or [""])[0]
    import sweep
    text, rodata, _, _ = sweep.obj_sizes(opath)
    return text, rodata, None


def main():
    outdir = os.path.join(HERE, "build", "calib")
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)

    reg = {}
    cpath = os.path.join(HERE, "results", "calibration.tsv")
    if os.path.exists(cpath):
        for line in open(cpath):
            p = line.rstrip("\n").split("\t")
            if len(p) == 2 and p[0] in FORMS:
                reg[p[0]] = float(p[1])

    n1, n2 = 8, 32
    out = open(os.path.join(HERE, "results", "calibration_direct.tsv"), "w")
    out.write("# per-form .text measured as a SLOPE between N=%d and N=%d\n"
              % (n1, n2))
    out.write("# cc=%s\n" % CC)
    out.write("form\ttext_n%d\ttext_n%d\trodata_n%d\ttext_per_section\t"
              "ols_per_section\tdelta\tnote\n" % (n1, n2, n2))
    print("%-8s %8s %8s %10s %10s %8s" %
          ("form", "slope", "OLS", "delta", "rodata/sec", "note"))
    for form in FORMS:
        r = {}
        bad = None
        for n in (n1, n2):
            iv, secs, forms = make_set(form, n)
            t, ro, err = text_of(iv, secs, forms, "%s_%d" % (form, n), outdir)
            if err:
                bad = err
                break
            r[n] = (t, ro)
        if bad:
            out.write("%s\t\t\t\t\t\t\tBUILD FAIL: %s\n" % (form, bad))
            print("%-8s BUILD FAIL: %s" % (form, bad[:60]))
            continue
        slope = (r[n2][0] - r[n1][0]) / float(n2 - n1)
        rops = (r[n2][1] - r[n1][1]) / float(n2 - n1)
        ols = reg.get(form)
        note = ""
        if ols is None:
            note = "no OLS term"
        elif form == "CUBES":
            note = "OLS UNIDENTIFIED (0 sections in the population)"
        elif abs(slope - ols) > max(12.0, 0.25 * max(slope, 1)):
            note = "DISAGREE with OLS"
        out.write("%s\t%d\t%d\t%d\t%.1f\t%s\t%s\t%s\n"
                  % (form, r[n1][0], r[n2][0], r[n2][1], slope,
                     ("%.1f" % ols) if ols is not None else "",
                     ("%+.1f" % (slope - ols)) if ols is not None else "",
                     note))
        print("%-8s %8.1f %8s %10s %10.1f  %s"
              % (form, slope, ("%.0f" % ols) if ols is not None else "-",
                 ("%+.0f" % (slope - ols)) if ols is not None else "-",
                 rops, note))
    out.close()
    print("\nwrote", os.path.join(HERE, "results",
                                  "calibration_direct.tsv"))


if __name__ == "__main__":
    main()
