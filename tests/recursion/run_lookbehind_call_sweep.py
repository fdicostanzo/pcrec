#!/usr/bin/env python3
"""[DD-14.LB] A CALL INSIDE A LOOKBEHIND, SWEPT — an ON-DEMAND differential
instrument, not part of `make test`.

    python3 tests/recursion/run_lookbehind_call_sweep.py
    SWEEP_TMP=/var/tmp/lbsweep python3 tests/recursion/run_lookbehind_call_sweep.py

WHY IT IS NOT THE CORPUS, AND WHY THE CORPUS IS NOT THIS. `inlookaround.rxt`'s
blocks are hand-shaped: each one exists to kill a specific wrong
implementation (a maxw fixpoint that runs once, a cycle test that only sees
self-recursion, a width table filled in the wrong order). That is exactly the
alphabet problem D27 names — **a test derived from what the author thought of
inherits what the author thought of.** This file enumerates a PRODUCT SPACE
instead (callee bodies x lookbehind body templates x polarity x subjects) and
asks libpcre2 about every cell, so a disagreement nobody wrote a cell for
still shows up. Neither replaces the other; the corpus is a set of aimed
questions and this is a net.

WHY IT IS ON-DEMAND. It compiles and LINKS one artifact per pattern — 900-odd
`gcc` invocations — which is `test-lookaround-identity`'s reason for being
opt-in, in the same words: an answer that cannot change unless someone edits
the width analysis is not what `make test` is for.

THE CLASSIFICATION IS THE POINT, not the pass count. Four outcomes per pattern:

    AGREE          both compile and every subject agrees on the span
    DISAGREE       both compile and a span differs — the failure this exists
                   for, and a MISCOMPILE if it ever fires
    PCREC-REFUSES  libpcre2 compiles it, pcrec does not. This is EXPECTED and
                   is not a failure: PCRE2 10.43+ ships variable-length
                   lookbehinds and `lookaround_design.md` §2.5 charters that
                   loop rather than shipping it. What the sweep CHECKS is that
                   every such refusal is the §2.5 WIDTH refusal — never a
                   crash, an internal error, a give-up, or a diagnostic naming
                   the wrong module. `bad_refusal` counts the ones that are
                   not, and it must be 0. A D26 tier-2 over-rejection is a
                   ruled limit; anything else wearing its clothes is a bug.
    BOTH-REFUSE    the recursive-callee family (libpcre2 err 125)

`pcrec_only` — pcrec compiling something libpcre2 refuses — must also be 0,
and it is the direction that would mean the width rule had gone SOFT.

MEASURED at [DD-14.LB] (2026-08-24), 908 distinct patterns x 22 subjects:
    cells 9240   agree 9240   disagree 0
    pcrec_refuses 220 (bad_refusal 0 — all 220 carry the one §2.5 sentence;
                       every refused callee is variable-width: `a?`, `a|bc`,
                       `a*`, or a body built from one)
    both_refuse 268   pcrec_only 0   cc_fail 0   give-ups 0
"""
import collections
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "docs", "design",
                                "subroutines_measurements", "probes"))
try:
    import sr_oracle as O
except Exception as e:                                      # noqa: BLE001
    sys.stderr.write("lbsweep: libpcre2 unavailable: %s\n" % e)
    sys.exit(3)
if O.SELFCHECK:
    sys.stderr.write("lbsweep: oracle self-check failed: %r\n" % (O.SELFCHECK,))
    sys.exit(3)

PCREC = os.path.join(ROOT, "build", "pcrec")
FEAT = "recursion,lookaround,named-groups,atomic-groups,assertions,backrefs"
TMP = os.environ.get("SWEEP_TMP", os.path.join(os.environ.get("TMPDIR", "/var/tmp"),
                                               "pcrec_lbsweep"))

# (name, callee body). The WIDTH CLASS of each is what the sweep is varying:
# three fixed, one fixed-through-an-alternation, one variable-by-alternation,
# one nullable, one unbounded, one recursive, one nested-lookaround.
CALLEES = [
    ("fix1", "a"), ("fix2", "ab"), ("fix3", "abc"),
    ("alt_same", "aa|bb"),          # 2 branches, SAME width -> still fixed
    ("alt_diff", "a|bc"),           # 2 branches, widths 1 and 2 -> 1..2
    ("nullable", "a?"),             # 0..1
    ("star", "a*"),                 # unbounded
    ("rec", "a(?&SELF)?b"),         # recursive -> unbounded, libpcre2 err 125
    ("cls", "[abc]"),
    ("exact", "a{3}"),
    ("nested_la", "a(?=b)"),        # width 1; the nested lookahead adds 0
]
# Lookbehind BODY templates. `{C}` calls the primary callee, `{D}` the
# secondary. The set varies what SURROUNDS the call: nothing, a literal on
# either side or both, a second call, an alternation at the body's own top
# level (with and without call-free branches), a capture, a non-capturing
# group, an atomic group, and a nested lookahead.
BODIES = [
    "{C}", "z{C}", "{C}z", "z{C}z", "{C}{D}",
    "{C}|{D}", "{C}|q", "q|{C}", "q|qq|{C}",
    "({C})", "(?:{C})", "(?>{C})", "a(?={C})b", "({C})|({D})",
]
POLS = [("pos", "(?<=", ")"), ("neg", "(?<!", ")")]
SUBJECTS = ["", "a", "b", "q", "z", "ab", "abc", "aa", "bb", "az", "za",
            "zab", "abz", "zabz", "aabb", "qq", "aq", "abcz", "aaa", "bc",
            "abab", "zaz"]

# The one refusal class a PCREC-REFUSES outcome is allowed to carry.
WIDTH_REFUSAL = re.compile(
    r"variable-length lookbehind is not implemented|this lookbehind is too long")


def population():
    """Every pattern, deduplicated, in a deterministic order."""
    out, seen = [], set()
    for cn, cb in CALLEES:
        for dn, db in CALLEES:
            # The secondary only varies for templates that USE it; otherwise
            # it is pinned so the same pattern is not generated eleven times.
            if cn == dn and cn != "fix1":
                continue
            cbody = cb.replace("(?&SELF)", "(?&g)")
            dbody = db.replace("(?&SELF)", "(?&h)")
            for tmpl in BODIES:
                if "{D}" not in tmpl and dn != "fix1":
                    continue
                for _pn, open_, close in POLS:
                    body = tmpl.format(C="(?&g)", D="(?&h)")
                    # The `{0}`-callee idiom, not `(?(DEFINE)`: DEFINE is
                    # module `conditionals`' construct until [DD-14] wave F
                    # (design §2.5/§4.4c, and inlookaround.rxt's own header).
                    pat = ("^(?:(?<g>%s)){0}(?:(?<h>%s)){0}%s%s%s$"
                           % (cbody, dbody, open_, body, close))
                    if pat in seen:
                        continue
                    seen.add(pat)
                    out.append((pat, cn, dn, tmpl))
    return out


def pcrec_compile(pat, out):
    r = subprocess.run([PCREC, "--features", FEAT, "-p", "rx", "--emit-main",
                        "-o", out, "--", pat], capture_output=True, text=True)
    return r.returncode, (r.stderr.strip() or r.stdout.strip())


def build_and_run(cpath, exe):
    r = subprocess.run([os.environ.get("CC", "gcc"), "-O1", "-o", exe, cpath],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None, "CC: " + r.stderr.strip()[:200]
    got = {}
    for s in SUBJECTS:
        p = subprocess.run([exe, s], capture_output=True, text=True, timeout=30)
        t = p.stdout.strip()
        if t.startswith("match"):
            _, a, b = t.split()
            got[s] = (int(a), int(b))
        elif t == "nomatch":
            got[s] = None
        else:
            # A give-up code. Not a span, and never silently scored as one.
            got[s] = ("OTHER", t)
    return got, None


def oracle(pat):
    try:
        c = O.compile(pat)
    except Exception as e:                                  # noqa: BLE001
        return None, str(e)
    got = {}
    for s in SUBJECTS:
        try:
            r = c.search(s, 0)
        except Exception as e:                              # noqa: BLE001
            got[s] = ("OTHER", str(e))
            continue
        got[s] = None if r is None else (r[0][0], r[0][1])
    return got, None


def main():
    if not os.path.exists(PCREC):
        sys.stderr.write("lbsweep: %s not built (run `make`)\n" % PCREC)
        return 3
    os.makedirs(TMP, exist_ok=True)
    cpath, exe = os.path.join(TMP, "s.c"), os.path.join(TMP, "s")
    pats = population()
    print("population: %d distinct patterns x %d subjects = %d cells"
          % (len(pats), len(SUBJECTS), len(pats) * len(SUBJECTS)))

    t = collections.Counter()
    findings = []
    for i, (pat, _cn, _dn, _tm) in enumerate(pats):
        orc, oerr = oracle(pat)
        rc, msg = pcrec_compile(pat, cpath)
        if rc != 0 and orc is None:
            t["both_refuse"] += 1
            continue
        if rc != 0:
            t["pcrec_refuses"] += 1
            if not WIDTH_REFUSAL.search(msg):
                t["bad_refusal"] += 1
                findings.append(("REFUSAL-NOT-A-WIDTH-LIMIT", pat, msg))
            continue
        if orc is None:
            t["pcrec_only"] += 1
            findings.append(("PCREC-COMPILES-LIBPCRE2-DOES-NOT", pat, oerr))
            continue
        got, err = build_and_run(cpath, exe)
        if got is None:
            t["cc_fail"] += 1
            findings.append(("CC-FAILED", pat, err))
            continue
        for s in SUBJECTS:
            t["cells"] += 1
            a, b = got[s], orc[s]
            if isinstance(a, tuple) and a and a[0] == "OTHER":
                t["giveup"] += 1
                findings.append(("PCREC-GIVEUP", "%s | %r" % (pat, s), str(a)))
                continue
            if isinstance(b, tuple) and b and b[0] == "OTHER":
                t["oracle_giveup"] += 1
                continue
            if a == b:
                t["agree"] += 1
            else:
                t["disagree"] += 1
                findings.append(("DISAGREE", "%s | %r" % (pat, s),
                                 "pcrec=%r libpcre2=%r" % (a, b)))
        if (i + 1) % 200 == 0:
            print("  ... %d/%d patterns, %d cells, %d disagree"
                  % (i + 1, len(pats), t["cells"], t["disagree"]), flush=True)

    print()
    for k in ("cells", "agree", "disagree", "pcrec_refuses", "bad_refusal",
              "both_refuse", "pcrec_only", "cc_fail", "giveup",
              "oracle_giveup"):
        print("  %-16s %d" % (k, t[k]))
    for k, p, m in findings[:40]:
        print("  %-32s %s\n      %s" % (k, p, m))
    if len(findings) > 40:
        print("  (%d findings total)" % len(findings))
    # A DISAGREEMENT, a give-up, a bad refusal, a build failure, or pcrec
    # compiling what libpcre2 refuses each fails this instrument. An ordinary
    # PCREC-REFUSES does NOT: it is the ruled §2.5 limit.
    bad = (t["disagree"] + t["bad_refusal"] + t["pcrec_only"] + t["cc_fail"]
           + t["giveup"])
    print("\nlbsweep: %s (%d disqualifying findings)"
          % ("OK" if bad == 0 else "FAILED", bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
