#!/usr/bin/env python3
"""[M6.2 wave B] THE COMPOSED STATE BUDGET, on the BUILT COMPILER.

assertions_design.md §3.5.1 is the finding this probe exists to settle, and it
is the one the design is least comfortable with:

    worst corpus state count   8,002  on ((a)|ab){4000}c        (§3.4's corpus)
    worst measured \\b ratio     4.75x on (?:ab){1,8}c            (§3.5)
    composed                  38,009
    PCREC_MAX_DFA_STATES_TABLE 32,000

    "38,009 > 32,000: the composed worst case EXCEEDS the state cap."

Both inputs to that product are PROTOTYPE or single-arm numbers — §3.5's ratio
came from probes/probe_wordctx_states.py, a Moore-minimising model with TWO
disclosed fidelity gaps in OPPOSITE directions, and the two worst values come
from different patterns, so the composition is a BOUND and not an observation.
§10 therefore makes it a Wave B landing condition to be measured HERE, on
pcrec, with the refusal boundary LOCATED rather than predicted.

WHAT IT MEASURES, all four on the real compiler:

  1. THE RATIO, per pattern: states and ncls for PAT against \\bPAT\\b, read off
     each artifact's own emitted tables. Same arm-vs-arm shape §3.5 used, with
     pcrec on both arms instead of a model on both.
  2. THE ALPHABET DELTA, per pattern: §3.4 predicted 0/+1/+2 over the corpus by
     SIMULATING the refinement on an unrefined class map. pcrec now performs
     it, so this is the prediction meeting the thing it predicted.
  3. THE REFUSAL BOUNDARY, located by bisection on a repeat count, against BOTH
     caps: PCREC_MAX_DFA_STATES_TABLE (32,000, ENG_UNANCH) and
     PCREC_MAX_DFA_STATES_GOTO (10,000, ENG_ATTEMPT — 3.2x tighter, and §3.4.1
     discloses that the whole corpus measurement was blind to that engine).
     Reported as the largest N that compiles with and without the assertion.
  4. THAT THE REFUSAL IS CLEAN. A capability regression is acceptable and was
     forecast; a MISCOMPILE at the boundary is not. Every refusal found is
     checked to be the states-cap diagnostic and nothing else.

Reading the state count. ENG_UNANCH emits `<prefix>_facc[N]`, so N is the
forward machine's state count. ENG_ATTEMPT emits no accept array at all — it
bakes acceptance into computed-goto label bodies — so the count there is the
number of `<prefix>_t<i>[]` transition tables, one per state. §3.4.1 is
explicit that the design's own corpus numbers came only from the first of
those, which is why this probe reads both.

Usage: probe_wordctx_budget.py PCREC_BIN [PATTERN_FILE]
"""
import re
import subprocess
import sys

CAP_TABLE = 32000    # PCREC_MAX_DFA_STATES_TABLE, src/core/limits.h
CAP_GOTO = 10000     # PCREC_MAX_DFA_STATES_GOTO


def emit(pcrec, pat, timeout=600):
    """(source, None) on success, (None, diagnostic) on refusal."""
    try:
        r = subprocess.run([pcrec, "--features", "all", "-p", "rx",
                            "--no-captures", "-o", "-", "--", pat],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT after %ds" % timeout
    if r.returncode != 0:
        return None, (r.stderr or r.stdout).strip().splitlines()[0] \
            if (r.stderr or r.stdout).strip() else "refused, no diagnostic"
    return r.stdout, None


def shape(src):
    """(nstates, ncls, engine) read off the artifact's own tables."""
    m = re.search(r"static const unsigned char rx_fcls\[256\]", src)
    if m:                                             # ENG_UNANCH
        a = re.search(r"static const unsigned char rx_facc\[(\d+)\]", src)
        t = re.search(r"static const short rx_ftr\[(\d+)\]", src)
        if not a or not t:
            return None
        n = int(a.group(1))
        return n, int(t.group(1)) // n, "unanch"
    if re.search(r"static const unsigned char rx_cls\[256\]", src):   # ATTEMPT
        ts = re.findall(r"static const void \*const rx_t(\d+)\[(\d+)\]", src)
        if not ts:
            return None
        return len(ts), int(ts[0][1]), "attempt"
    return None


def measure(pcrec, pat):
    src, err = emit(pcrec, pat)
    if src is None:
        return None, err
    sh = shape(src)
    if sh is None:
        return None, "compiled to a non-DFA artifact (VM)"
    return sh, None


def arm_report(pcrec, pats):
    """§3.4 and §3.5's two deltas, per pattern, both arms on pcrec."""
    rows, ratios, dcls = [], [], []
    skipped = 0
    for p in pats:
        base, e1 = measure(pcrec, p)
        wrap, e2 = measure(pcrec, r"\b" + p + r"\b")
        if base is None or wrap is None:
            skipped += 1
            rows.append((p, None, None, e1 or e2))
            continue
        bs, bc, be = base
        ws, wc, we = wrap
        rows.append((p, (bs, bc, be), (ws, wc, we), None))
        ratios.append(ws / bs)
        dcls.append(wc - bc)
    return rows, ratios, dcls, skipped


def bisect_max(pcrec, mkpat, lo, hi):
    """Largest N in [lo, hi] for which mkpat(N) compiles. hi must FAIL and lo
    must SUCCEED; returns (N, first_failing_diagnostic)."""
    okd, _ = emit(pcrec, mkpat(lo))
    if okd is None:
        return None, "the low end %d already refuses" % lo
    bad, diag = emit(pcrec, mkpat(hi))
    if bad is not None:
        return None, "the high end %d still compiles — widen the search" % hi
    last_diag = diag
    while hi - lo > 1:
        mid = (lo + hi) // 2
        src, d = emit(pcrec, mkpat(mid))
        if src is None:
            hi, last_diag = mid, d
        else:
            lo = mid
    return lo, last_diag


def pct(v):
    return "%.1f%%" % v


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pcrec = sys.argv[1]
    patfile = sys.argv[2] if len(sys.argv) > 2 else None

    print("== 1+2. THE RATIO AND THE ALPHABET DELTA, both arms on pcrec ==")
    print()
    if patfile:
        pats = [l.rstrip("\n") for l in open(patfile) if l.strip()]
    else:
        # §3.5's own representative rows, so the two tables can be read
        # against each other line for line.
        pats = ["[0-9a-f]{64}", r"\d{4}-\d{2}-\d{2}", r"\w{3,16}",
                "(?:ab){1,8}c", "[a-z][a-z0-9_]{2,31}", '"[^"]*"',
                "[aeiou]{2,3}[^aeiou]{1,2}", "[A-Z]{4,8} [0-9]{3}",
                r"\d{1,3}(?:,\d{3})+", "(?:[A-Za-z]+ ){2,4}[A-Za-z]+",
                "https?://[a-zA-Z0-9.-]+/[a-zA-Z0-9/_-]*",
                "((a)|ab){40}c", "((a)|ab){400}c", "(a|ab){100}c",
                "[01]*1[01]{8}", "a(b|c)+d", "foo|bar|baz"]
    rows, ratios, dcls, skipped = arm_report(pcrec, pats)
    print("%-42s %7s %5s %8s %7s %5s %8s %7s"
          % ("pattern (wrapped as \\bPAT\\b)", "base", "ncls", "engine",
             "wordctx", "ncls", "engine", "ratio"))
    for p, b, w, err in rows:
        if b is None:
            print("%-42s  -- skipped: %s" % (p[:42], err))
            continue
        print("%-42s %7d %5d %8s %7d %5d %8s %6.2fx"
              % (p[:42], b[0], b[1], b[2], w[0], w[1], w[2], w[0] / b[0]))
    print()
    if ratios:
        rs = sorted(ratios)
        print("STATE RATIO   n=%d  min/median/max = %.2fx / %.2fx / %.2fx"
              % (len(rs), rs[0], rs[len(rs) // 2], rs[-1]))
        ds = sorted(dcls)
        print("ALPHABET      n=%d  min/median/max = %+d / %+d / %+d   "
              "(§3.4 predicted 0 / +1 / +2 over the .rxt corpus)"
              % (len(ds), ds[0], ds[len(ds) // 2], ds[-1]))
        print("skipped (either arm refused or went to the VM): %d" % skipped)
    print()

    print("== 3+4. THE REFUSAL BOUNDARY, LOCATED ==")
    print()
    print("The family is §3.5.1's own worst-state-count shape. Each row is the")
    print("largest repeat count that COMPILES; the row below it is the first")
    print("that refuses, with the diagnostic it refused with.")
    print()
    fams = [
        ("((a)|ab){N}c        ENG_UNANCH, cap %d" % CAP_TABLE,
         lambda n: "((a)|ab){%d}c" % n, 1, 20000),
        ("\\b((a)|ab){N}c\\b    ENG_UNANCH, cap %d" % CAP_TABLE,
         lambda n: r"\b((a)|ab){%d}c\b" % n, 1, 20000),
        ("^((a)|ab){N}c       ENG_ATTEMPT, cap %d" % CAP_GOTO,
         lambda n: "^((a)|ab){%d}c" % n, 1, 20000),
        ("^\\b((a)|ab){N}c     ENG_ATTEMPT, cap %d" % CAP_GOTO,
         lambda n: r"^\b((a)|ab){%d}c" % n, 1, 20000),
        ("(?:ab){1,N}c        ENG_UNANCH, §3.5's 4.75x shape",
         lambda n: "(?:ab){1,%d}c" % n, 1, 20000),
        ("\\b(?:ab){1,N}c\\b    ENG_UNANCH, §3.5's 4.75x shape",
         lambda n: r"\b(?:ab){1,%d}c\b" % n, 1, 20000),
        # THE FAMILY THAT ACTUALLY REGRESSES, and it took looking for.
        # The families above are bounded by PCREC_MAX_SUBSET_ELEMS on their
        # BARE arm — the unanchored self-loop keeps every offset's threads
        # alive, so the state SETS are what run out, not the state COUNT — and
        # a leading `\b` PRUNES most start positions, which makes the wrapped
        # arm cheaper rather than dearer. A capability regression needs a
        # family whose bare arm is bound by the STATE COUNT, and a linear
        # chain is one: `[a-z]{1,N}` is exactly N+1 states, wrapped is N+2, so
        # the ceiling moves by ONE repeat count. That is the whole measured
        # regression, against a composed bound of 4.75x.
        ("[a-z]{1,N}          ENG_UNANCH, a LINEAR CHAIN (states-bound)",
         lambda n: "[a-z]{1,%d}" % n, 1, 40000),
        ("\\b[a-z]{1,N}\\b      ENG_UNANCH, a LINEAR CHAIN (states-bound)",
         lambda n: r"\b[a-z]{1,%d}\b" % n, 1, 40000),
    ]
    for label, mk, lo, hi in fams:
        n, diag = bisect_max(pcrec, mk, lo, hi)
        if n is None:
            print("%-52s  NOT LOCATED: %s" % (label, diag))
            continue
        okshape, _ = measure(pcrec, mk(n))
        st = "%d states, ncls %d, %s" % okshape if okshape else "shape unread"
        clean = "states-cap refusal" if "too complex for the DFA engine" in \
            (diag or "") else "*** NOT THE STATES-CAP REFUSAL ***"
        print("%-52s  largest compiling N = %-6d (%s)" % (label, n, st))
        print("%-52s  N = %-6d refuses: %s  [%s]"
              % ("", n + 1, (diag or "")[:90], clean))
    print()
    print("A refusal is a CAPABILITY regression and was forecast (§3.5.1")
    print("qualification 2). What must NOT happen is a wrong answer at the")
    print("boundary, which is why every row above names the diagnostic.")


if __name__ == "__main__":
    main()
