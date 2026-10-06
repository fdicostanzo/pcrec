#!/usr/bin/env python3
"""tests/startset/compile_fuzz.py -- [START-SET] stage 3's COMPILE-ONLY arm:
"the deny arm compiles => the default compiles" over a GENERATED population
of seeded patterns (D148; the ss3 D6 panel's BLOCKER sound-F1 and its lesson,
docs/dev/reviews/2026-10-06-r-ss3-panel.md).

WHY THIS ARM EXISTS. The DFA hat once carried a build assertion (`T == S` over
`T = S & E*`) whose premise was false: a byte of `S` can leave every seed state
where it is (`(?<=\\w) *a`: a space keeps the non-word context and keeps the
word-context thread in ` *`), so valid patterns REFUSED with an internal error
at default flags while `-fno-start-set` compiled them. Every answer check in
this directory compares two COMPILED artifacts, so a pattern that no longer
compiles reaches none of them; the corpus held no such shape. A compile-only
fuzz found it (4 hits in 9,000). This arm is that fuzz, made deterministic,
floored and permanent.

THE CHECK. For each generated (pattern, flags): compile with `-fno-start-set`
(the deny arm, today's emitter without either hat). If it compiles, the
default build MUST compile too, inside the same budget; an "internal error"
on EITHER arm is a failure whatever the other did. A default refusal or
timeout where the deny arm compiled is the F1 shape exactly.

POPULATION. A seeded grammar (`\\b`, `\\B`, lookbehinds, lookaheads over small
loops and alternations, the critic's `/tmp/sscrit/fz.py` alphabet) plus a
TEMPLATE family biased at F1's mechanism: a context assertion, then a
starred/lazy loop over a byte the assertion's context does not change, then a
tail. Flags are drawn per pattern from {none, -i, --no-captures,
-fprefilter-collapse, -e utf8, --ucp}. Seeded with a fixed seed, so a run is
reproducible and a failing line can be re-run by hand.

FLOORS (K35): the population that the deny arm compiled, and the number of
those whose default artifact reached a DFA hat (`RX_DFA_PREFILTER "first-`),
each at half the landing figure -- a grammar edit that stopped reaching the
hat must fail, not read clean.

FAILING DIRECTION (measured at landing, lane ssfix3): on the pre-fix compiler
(`T = S & E*` + the assertion) this arm reads the F1 refusals (report
docs/dev/lanes/ssbuild3_report.md, "Panel fixes (ssfix3)").

Env: PCREC, JOBS, SEED, N (population size), TEMPLATE (the template's share,
default 0.3; 0 is the critic's untemplated grammar), FLOOR_OK, FLOOR_HAT.
Prints PASS:/FAIL: and the trailers.
"""
import concurrent.futures as cf, os, random, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", ".."))
PCREC = os.environ.get("PCREC", os.path.join(TREE, "build", "pcrec"))
JOBS = int(os.environ.get("JOBS", "8"))
SEED = int(os.environ.get("SEED", "20261006"))
N = int(os.environ.get("N", "9000"))
TEMPLATE = float(os.environ.get("TEMPLATE", "0.3"))   # share drawn from the F1 template
TMO = 60
# K35 floors: half the landing figures (lane ssfix3, N=9000, SEED=20261006).
FLOOR_OK = int(os.environ.get("FLOOR_OK", "4500"))
FLOOR_HAT = int(os.environ.get("FLOOR_HAT", "340"))

ATOMS = ["a", "b", "-", " ", "x", "[ab]", "[^a]", "\\w", "\\W", "\\s", "\\d", ".",
         "(?:ab|b)", "[a-]", "\\n"]
CTX = ["\\b", "\\B", "(?<=a)", "(?<!a)", "(?<=\\w)", "(?<!\\W)", "(?<=-)",
       "(?<![a-])", "(?<=[ab])", "(?<!b)", "(?<!\\s)", "(?<=\\s)", "(?=a)", "(?!-)"]
QUANT = ["*", "+", "?", "{1,2}", "*?", "+?"]
FLAGS = [[], ["-i"], ["--no-captures"], ["-fprefilter-collapse"], ["-e", "utf8"], ["--ucp"]]


def gen(rng):
    def atom(d):
        r = rng.random()
        if r < 0.4:
            return rng.choice(ATOMS)
        if r < 0.7:
            return rng.choice(CTX)
        if r < 0.85 and d < 2:
            return "(?:" + "|".join(seq(d + 1) for _ in range(rng.randint(2, 3))) + ")"
        return rng.choice(ATOMS) + rng.choice(QUANT)

    def seq(d=0):
        return "".join(atom(d) for _ in range(rng.randint(1, 4)))

    if rng.random() < TEMPLATE:   # the F1 template: context, a loop the context ignores, a tail
        tail = rng.choice(ATOMS) + (rng.choice(QUANT) if rng.random() < 0.3 else "")
        return (rng.choice(CTX) + rng.choice(ATOMS) + rng.choice(["*", "*?", "+", "?"])
                + tail + (rng.choice(CTX) if rng.random() < 0.2 else ""))
    return seq()


def compile_(pat, flags, deny):
    cmd = [PCREC, "--features", "all", "-o", "-", "--pattern", pat] + flags
    if deny:
        cmd.append("-fno-start-set")
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=TMO)
    except subprocess.TimeoutExpired:
        return "timeout", b"", ""
    err = r.stderr.decode("utf-8", "replace")
    return r.returncode, r.stdout, err


def one(item):
    pat, flags = item
    drc, _, derr = compile_(pat, flags, True)
    if "internal error" in derr:
        return ("fail", pat, flags, "deny arm internal error: " + derr.strip()[:200])
    if drc != 0:
        return ("deny-refused", pat, flags, "")
    rc, out, err = compile_(pat, flags, False)
    if rc != 0 or "internal error" in err:
        return ("fail", pat, flags, "default rc=%s while -fno-start-set compiled: %s" % (rc, err.strip()[:200]))
    hat = b'_DFA_PREFILTER "first-' in out
    return ("hat" if hat else "ok", pat, flags, "")


def main():
    rng = random.Random(SEED)
    pop = []
    for _ in range(N):
        pop.append((gen(rng), rng.choice(FLAGS)))
    counts = {"ok": 0, "hat": 0, "deny-refused": 0, "fail": 0}
    fails = []
    with cf.ThreadPoolExecutor(JOBS) as ex:
        for kind, pat, flags, why in ex.map(one, pop, chunksize=16):
            counts[kind] += 1
            if kind == "fail":
                fails.append((pat, flags, why))
    p = f = 0
    compiled = counts["ok"] + counts["hat"]
    print("REACH: [cf-pop] %d generated (seed %d): %d compile on the deny arm (%d reach a DFA hat), "
          "%d refused by the deny arm" % (N, SEED, compiled, counts["hat"], counts["deny-refused"]))
    if fails:
        f += 1
        print("FAIL: [cf-deny-implies-default] %d pattern(s) the deny arm compiles and the default refuses "
              "(or an internal error):" % len(fails))
        for pat, flags, why in fails[:20]:
            print("    %r %s: %s" % (pat, " ".join(flags) or "(no flags)", why))
    else:
        p += 1
        print("PASS: [cf-deny-implies-default] every one of %d deny-compiling patterns compiles at default" % compiled)
    if compiled >= FLOOR_OK:
        p += 1
        print("PASS: [cf-floor] %d deny-compiling patterns (floor %d)" % (compiled, FLOOR_OK))
    else:
        f += 1
        print("FAIL: [cf-floor] %d deny-compiling patterns, below the floor %d" % (compiled, FLOOR_OK))
    if counts["hat"] >= FLOOR_HAT:
        p += 1
        print("PASS: [cf-hat-floor] %d reach a DFA hat (floor %d)" % (counts["hat"], FLOOR_HAT))
    else:
        f += 1
        print("FAIL: [cf-hat-floor] %d reach a DFA hat, below the floor %d" % (counts["hat"], FLOOR_HAT))
    print("checks passed: %d" % p)
    print("checks failed: %d" % f)
    return 0 if f == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
