#!/usr/bin/env python3
"""MRL over-pruning hunt with pcrec's OWN DFA ENGINE as the oracle.

PROVENANCE: written by the LANDING PANEL's soundness critic, not by the build
lane, and adopted here verbatim in mechanism (paths generalised, its companion
driver inlined so the file stands alone). It is the instrument behind that
lens's ~285,000-cell verdict, and it is kept because an instrument built by
someone attacking the change is worth more than one built by the person who
wrote it — the build lane's own differential compares two pcrec builds that
share every line of the analysis, and this one does not.

NOT BATTERY-WIRED, deliberately (D35's ages-freely shape): it generates random
patterns and builds three artifacts each, so it costs minutes and its
population is a seed rather than a fixture. The properties that must keep
holding live in tests/mrl/. Re-run this when the analysis changes.

    Arm A: the default hybrid build (VM + MRL, prefilter-window ceiling).
    Arm B: --no-captures, which selects the pure DFA engine -- table-driven,
           linear-time, MRL never touches it, and it always terminates. It
           answers the match SPAN, which is exactly the quantity an over-large
           minimum-remaining-length would delete.
    Arm C: --engine=vm (subject-end ceiling) -- separates the WINDOW ceiling
           from the bound itself.

A `nomatch` from A where B reports a match is a deleted match: BLOCKER.
Give-ups on A are reported and NOT counted as divergences (a budget fact, not
a soundness fact); B never gives up.

The same idea now runs inside the committed differential as its referee arm
(tests/mrl/run_mrldiff.sh, panel F2) for the EXCUSED cells specifically. This
file is the broader, randomized form.

Usage: dfadiff.py [SEED] [NPATTERNS] [WORKDIR]
Env:   PCREC (default: the tree's build/pcrec)
"""
import itertools, os, random, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    "..", "..", "..", ".."))
PC = os.environ.get("PCREC", os.path.join(ROOT, "build", "pcrec"))
WORK = (sys.argv[3] if len(sys.argv) > 3
        else tempfile.mkdtemp(prefix="dfadiff."))
os.makedirs(WORK, exist_ok=True)

# The companion driver, INLINED so this file needs nothing beside it. It was a
# separate scratchpad file in the panel's copy; a probe that depends on an
# uncommitted sibling is a probe that stops running.
DRIVER = r"""/* independent critic driver.
 * argv mode:  run <subject> [startpos]
 * batch mode: run -   ... reads one subject per line from stdin (empty line = "")
 *             and prints one result line each. */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "art.h"

static void one(const unsigned char *s, size_t n, size_t startpos)
{
    ptrdiff_t caps[RX_NCAPS][2];
    int rc, k;
    for (k = 0; k < RX_NCAPS; k++) { caps[k][0] = -1; caps[k][1] = -1; }
    rc = rx_search(s, n, startpos, caps);
    if (rc == 1) {
        printf("match");
        for (k = 0; k < RX_NCAPS; k++) printf(" %td:%td", caps[k][0], caps[k][1]);
        printf("\n");
    } else if (rc == 0) {
        printf("nomatch\n");
    } else {
        printf("giveup %d\n", rc);
    }
}

int main(int argc, char **argv)
{
    if (argc < 2) { fprintf(stderr, "usage: %s <subject>|-\n", argv[0]); return 2; }
    if (!strcmp(argv[1], "-")) {
        char buf[65536];
        while (fgets(buf, sizeof buf, stdin)) {
            size_t n = strlen(buf);
            while (n && (buf[n - 1] == '\n' || buf[n - 1] == '\r')) buf[--n] = 0;
            one((const unsigned char *)buf, n, 0);
        }
        return 0;
    }
    {
        size_t startpos = (argc >= 3) ? (size_t)strtoul(argv[2], NULL, 10) : 0;
        one((const unsigned char *)argv[1], strlen(argv[1]), startpos);
    }
    return 0;
}
"""

with open(os.path.join(WORK, "drv.c"), "w") as _f:
    _f.write(DRIVER)

ARMS = [("A_hy", ["--step-budget=20000000"]),
        ("B_dfa", ["--no-captures"]),
        ("C_vm", ["--engine=vm", "--step-budget=20000000"])]

ATOMS = ["a", "b", "[ab]", "(a)", "(?:ab)", "(?:a|b)", "(a|bb)", "(?:abc)",
         "(?:ab|a)", "(a?)", "(?:aa)", "(a)(b)", "(?:a|aa)", "(?:aa|a)",
         "a{1,3}", "(a{1,2})", "(?:ab|ba)"]
QUANTS = ["", "*", "+", "?", "*?", "+?", "??", "{2}", "{1,3}", "{2,4}", "{0,3}",
          "{1,3}?", "{2,4}?", "{3,}", "{2,}?", "{4,7}", "{5}", "{9}", "{12}",
          "{10,20}", "{9,}?", "{20}", "{8,12}"]


def gen(rng):
    parts = []
    for _ in range(rng.randint(2, 4)):
        at = rng.choice(ATOMS)
        q = rng.choice(QUANTS)
        if at in ("(a?)", "(?:a|b)") and q in ("{3,}", "*", "+", "*?", "+?", "{2,}?", "{9,}?"):
            q = "{1,3}"
        parts.append(at + q)
    p = "".join(parts)
    if rng.random() < 0.15:
        p = "^" + p
    if rng.random() < 0.15:
        p = p + "$"
    return p


def build(pat, tag, flags):
    out = os.path.join(WORK, tag)
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    try:
        r = subprocess.run([PC, "-p", "rx", "-o", out + "/art.c"] + flags +
                           ["--", pat], capture_output=True, timeout=90)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    shutil.copy(os.path.join(WORK, "drv.c"), out + "/drv.c")
    try:
        r = subprocess.run(["gcc", "-O1", "-I", out, "-o", out + "/run",
                            out + "/art.c", out + "/drv.c"],
                           capture_output=True, timeout=600)
    except subprocess.TimeoutExpired:
        return None
    return out + "/run" if r.returncode == 0 else None


def span(line):
    """match span only, so arms with different NCAPS are comparable"""
    if line.startswith("match"):
        return line.split()[1]
    if line.startswith("nomatch"):
        return "nomatch"
    return "giveup"


SUBJ = [""]
for L in range(1, 9):
    SUBJ += ["".join(t) for t in itertools.product("ab", repeat=L)]
for L in range(0, 120):
    SUBJ += ["a" * L, "a" * L + "b", "b" + "a" * L, "ab" * L, "a" * L + "ba",
             ("ab" * L) + "a", "b" * L + "a" * L]
SUBJ = list(dict.fromkeys(SUBJ))
STDIN = "\n".join(SUBJ) + "\n"

rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
N = int(sys.argv[2]) if len(sys.argv) > 2 else 80
ndiv = ngive = ntested = 0
for it in range(N):
    pat = gen(rng)
    exes, ok = {}, True
    for tag, flags in ARMS:
        e = build(pat, tag, flags)
        if e is None:
            ok = False
            break
        exes[tag] = e
    if not ok:
        print("skip  %r" % pat, flush=True)
        continue
    outs = {}
    for tag in exes:
        try:
            r = subprocess.run([exes[tag], "-"], input=STDIN.encode(),
                               capture_output=True, timeout=900)
            outs[tag] = r.stdout.decode().splitlines()
        except subprocess.TimeoutExpired:
            outs[tag] = None
    if any(v is None or len(v) != len(SUBJ) for v in outs.values()):
        print("skip(timeout) %r" % pat, flush=True)
        continue
    ntested += 1
    bad = giv = 0
    for i, subj in enumerate(SUBJ):
        a, b, c = (span(outs["A_hy"][i]), span(outs["B_dfa"][i]),
                   span(outs["C_vm"][i]))
        if a == "giveup" or c == "giveup":
            giv += 1
            continue
        if a != b or c != b:
            print("  ** %r subj=%r(len %d) A=%s B_dfa=%s C_vm=%s"
                  % (pat, subj[:40], len(subj), a, b, c), flush=True)
            bad += 1
            ndiv += 1
            if bad > 4:
                break
    ngive += giv
    print("done  %-46r %d subjects, %d give-ups%s"
          % (pat, len(SUBJ), giv, "  DIVERGED" if bad else ""), flush=True)

print("==== tested %d patterns, %d span divergences, %d give-up cells ===="
      % (ntested, ndiv, ngive), flush=True)
