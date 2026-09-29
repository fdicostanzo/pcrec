#!/usr/bin/env python3
"""verify_whole.py — EXHAUSTIVE check of wholeset.py's two forms against
emit.py's independent reference on all 1,114,112 code points, per set, and
their rodata (the design note's §1.3 size column).  Same rule as sweep.py:
every matcher is verified exhaustively, never sampled.

    python3 verify_whole.py [population]      (default k53)
"""
import os
import subprocess
import sys

import clsets
import emit
import sweep
import wholeset

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.environ.get("CC", "gcc-16")

DRIVER = r"""
#include <stdio.h>
int main(void)
{
    unsigned long bad2 = 0, bad3 = 0;
    for (unsigned cp = 0; cp < 0x110000u; cp++) {
        int r = ref(cp);
        bad2 += (unsigned long)(pw2(cp) != r);
        bad3 += (unsigned long)(pw3(cp) != r);
    }
    printf("%lu %lu\n", bad2, bad3);
    return 0;
}
"""


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "k53"
    out = os.path.join(HERE, "build", "whole")
    os.makedirs(out, exist_ok=True)
    print("set\tintervals\tpage2w_rodata\tpage3w_rodata\tpage2w_obj\tpage3w_obj"
          "\tmismatch2\tmismatch3")
    fails = 0
    for name, iv in clsets.population(which):
        tag = "".join(c if c.isalnum() else "_" for c in name)
        w2, w3 = wholeset.PageW2(iv), wholeset.PageW3(iv)
        src = (emit.PRELUDE + emit.reference("ref", iv)
               + w2.c("pw2") + w3.c("pw3") + DRIVER)
        c = os.path.join(out, tag + ".c")
        b = os.path.join(out, tag)
        open(c, "w").write(src)
        subprocess.run([CC, "-O2", "-std=gnu11", "-w", c, "-o", b], check=True)
        m2, m3 = subprocess.run([b], capture_output=True, text=True,
                                check=True).stdout.split()
        fails += int(m2) + int(m3)
        # OBJECT bytes (.text + .rodata) of each form ALONE, the unit every
        # other size in the study is quoted in (sweep.obj_sizes).
        objs = []
        for fn, w in (("pw2", w2), ("pw3", w3)):
            oc, oo = os.path.join(out, tag + fn + ".c"), \
                os.path.join(out, tag + fn + ".o")
            open(oc, "w").write(w.c(fn))
            subprocess.run([CC, "-O2", "-std=gnu11", "-w", "-c", oc, "-o", oo],
                           check=True)
            t, ro, _, _ = sweep.obj_sizes(oo)
            objs.append(t + ro)
        print("%s\t%d\t%d\t%d\t%d\t%d\t%s\t%s"
              % (name, len(iv), w2.rodata(), w3.rodata(), objs[0], objs[1],
                 m2, m3))
    print("TOTAL mismatches: %d" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
