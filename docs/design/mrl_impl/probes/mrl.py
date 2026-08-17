#!/usr/bin/env python3
"""[M4.6d] the MRL build lane's instrument: a THREE-WAY differential and a
step meter over the same emitted artifacts.

The three arms are pcrec WITH MRL pruning, pcrec with `-fno-length-prune`
(byte-identical to what pcrec emitted before MRL existed, so it is the ground
truth `eng_brep_design.md` §5.1 established for this territory), and python
`re`.  It compares the FULL CAPTURE VECTOR, never the span: the soundness
claim is about where the groups land, and a span-only instrument would miss
exactly the class of error the clamp exists not to introduce
(k23_design.md §7.1's own instrument rule, inherited).

LC_ALL=C is set for every subprocess (R24 M-F1's collation defect).

Steps are measured by DOUBLING the emitted step budget until the artifact
stops returning ERR_STEPS, which reports the smallest power of two above the
true count -- a bound, and labelled as one.  There is no step counter to read
out of a shipped artifact, and adding one would measure a different binary.

Usage:
    mrl.py diff CASES.tsv          three-way differential over a case file
    mrl.py steps PATTERN SUBJECT   step bound for both arms, side by side
    mrl.py sizes PATTERN           emitted-C size for both arms
"""
import os, re, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
PCREC = os.path.join(ROOT, "build", "pcrec")
ENV = dict(os.environ, LC_ALL="C")
BIG = 10 ** 12          # "no budget in practice" for the differential arms

DRIVER = r"""
#include <stdio.h>
#include <string.h>
#include "gen.h"
int main(int argc, char **argv)
{
    ptrdiff_t caps[RX_NCAPS][2];
    const char *s = argc > 1 ? argv[1] : "";
    int r = rx_search((const unsigned char *)s, strlen(s), 0, caps);
    int k;
    if (r != 1) { printf("r=%d\n", r); return r == 0 ? 1 : 3; }
    for (k = 0; k < RX_NCAPS; k++)
        printf("%s%td,%td", k ? " " : "", caps[k][0], caps[k][1]);
    printf("\n");
    return 0;
}
"""


class Arm:
    """One compiled artifact, kept alive so a sweep pays the build cost once."""

    def __init__(self, d, pat, flags, budget=BIG):
        self.dir = d
        self.exe = os.path.join(d, "a.out")
        self.c = os.path.join(d, "gen.c")
        drv = os.path.join(d, "drv.c")
        with open(drv, "w") as f:
            f.write(DRIVER)
        cmd = [PCREC, "-p", "rx", "--step-budget=%d" % budget,
               "-o", self.c] + flags + ["--", pat]
        r = subprocess.run(cmd, env=ENV, capture_output=True)
        if r.returncode:
            raise RuntimeError("pcrec: " + r.stderr.decode()[:200])
        r = subprocess.run(["gcc", "-O1", "-I", d, "-o", self.exe, drv, self.c],
                           env=ENV, capture_output=True)
        if r.returncode:
            raise RuntimeError("gcc: " + r.stderr.decode()[:400])
        self.size = os.path.getsize(self.c)

    def run(self, subj):
        r = subprocess.run([self.exe, subj], env=ENV, capture_output=True,
                           timeout=600)
        out = r.stdout.decode().strip()
        if r.returncode == 3:
            return "giveup:" + out
        if r.returncode == 1:
            return "nomatch"
        return out


def py_expect(pat, subj):
    try:
        m = re.search(pat, subj)
    except re.error as e:
        return "py-error:" + str(e)
    if not m:
        return "nomatch"
    out = []
    for k in range(m.re.groups + 1):
        sp = m.span(k)
        out.append("%d,%d" % sp if sp != (-1, -1) else "-1,-1")
    return " ".join(out)


def subjects(spec):
    """`spec` is a comma-separated list of python string expressions."""
    return [eval(s, {"__builtins__": {}}, {}) for s in spec.split("|")]


def cmd_diff(path):
    agree = differ = skipped = 0
    nshape = 0
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        pat, spec = line.split("\t", 1)
        nshape += 1
        with tempfile.TemporaryDirectory() as d:
            try:
                on = Arm(os.path.join(d), pat, [])
                os.makedirs(os.path.join(d, "off"))
                off = Arm(os.path.join(d, "off"), pat, ["-fno-length-prune"])
            except RuntimeError as e:
                print("SKIP %-34s %s" % (pat, e))
                skipped += 1
                continue
            for subj in subjects(spec):
                a, b = on.run(subj), off.run(subj)
                c = py_expect(pat, subj)
                tag = "n=%d" % len(subj)
                if a == b == c:
                    agree += 1
                else:
                    differ += 1
                    print("DIFFER %-30s %-10s pruned=%-28s unpruned=%-28s py=%s"
                          % (pat, tag, a, b, c))
    print("shapes %d  cells AGREE %d  DIFFER %d  skipped-shapes %d"
          % (nshape, agree, differ, skipped))
    return 1 if differ else 0


def step_bound(pat, subj, flags):
    b = 1
    while b <= 2 * 10 ** 9:
        with tempfile.TemporaryDirectory() as d:
            arm = Arm(d, pat, flags, budget=b)
            out = arm.run(subj)
        if not out.startswith("giveup"):
            return b, out
        b *= 2
    return None, "giveup"


def cmd_steps(pat, spec):
    for subj in subjects(spec):
        on = step_bound(pat, subj, [])
        off = step_bound(pat, subj, ["-fno-length-prune"])
        print("%-30s n=%-6d pruned<=%-12s unpruned<=%-14s %s | %s"
              % (pat, len(subj), on[0], off[0], on[1], off[1]))
    return 0


def cmd_sizes(pat):
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "off"))
        on = Arm(d, pat, [])
        off = Arm(os.path.join(d, "off"), pat, ["-fno-length-prune"])
    print("%-34s pruned %7d B   unpruned %7d B   %+.1f%%"
          % (pat, on.size, off.size, 100.0 * (on.size - off.size) / off.size))
    return 0


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "diff":
        sys.exit(cmd_diff(sys.argv[2]))
    if what == "steps":
        sys.exit(cmd_steps(sys.argv[2], sys.argv[3]))
    if what == "sizes":
        sys.exit(cmd_sizes(sys.argv[2]))
    sys.exit("unknown subcommand " + what)
