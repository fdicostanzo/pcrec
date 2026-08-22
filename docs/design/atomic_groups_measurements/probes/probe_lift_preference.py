"""probe_lift_preference.py — MEASURED, both arms.

[M6.4.1] REVISION 2 (R31 re-check N1). The possessive-rung LIFT (§3.2 RULE 3)
gained a NULLABILITY carve-out in revision 1 and had NO PREFERENCE carve-out.
It needed both, and for the identical reason: **the possessive rungs are
GREEDY-ONLY, and their right to ignore preference is a CONSEQUENCE of §2.2's
verdict — an antecedent a user-written atomic group deletes.**

`src/gen/emit_vm.c:2053-2062` argues the collapse in as many words:

    "The PREFERENCE disappears when the quantifier is possessified, and that
     is the analysis's conclusion rather than a shortcut. ... On the
     disjointness arm a greedy loop tops out by preference, and a LAZY one is
     FORCED to the same top: at any non-maximal exit the body could iterate
     again, so that byte is in FIRST(X), so by disjointness the follow cannot
     begin there — and the lazy conjunct (non-nullable remainder) is what
     rules out the match simply ENDING there instead. Both preferences
     therefore land on the maximal exit, which is what makes ONE EMITTED SHAPE
     CORRECT FOR BOTH."

Every clause of that is §2.2. `(?>a*?)b` has no §2.2 verdict, its lazy exit is
NOT the maximal one, and the one emitted shape is wrong for it.

The signatures corroborate: `vm_opt_chain` takes `bool greedy`
(`emit_vm.c:2358`); `vm_poss_chain` (`:2437`), `vm_poss_star` (`:2494`) and
`vm_counter_poss_opt` (`:3247`) do not take it and do not read it.

TWO HALVES, and the second is the one that makes this a HIGH:

  PART A (in-pcrec) — lazy quantifiers ARE possessified today, on EVERY one of
  `vm_rep`'s dispatch paths. So the collapse is relied on across the whole
  ladder, not only on the cursor rung the re-check measured.

  PART B (both oracles) — what the lift would ANSWER. The lift emits the
  GREEDY possessive shape, so its answer is readable off libpcre2 directly by
  compiling the greedy possessive spelling. Any row where that differs from
  the atomic-lazy pattern's own answer is a MISCOMPILE the lift would ship.

The CONTROL row is `(?>a*?b)c`, whose `A_ATOMIC` child is an `A_CAT` and not an
`A_REP`, so the lift does not apply and the answer must AGREE. A run where
every row miscompiles has lost its control and is measuring the wrong thing.
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "eng_brep_measurements", "probes"))
import pcre2_ctypes as P  # noqa: E402

PCREC = os.environ.get("PCREC", "build/pcrec")

RUNG = {"0x1": "CURSOR", "0x2": "FRAMES_BOUNDED", "0x4": "FRAMES_UNBOUNDED",
        "0x8": "REVDET", "0x10": "COUNTER"}

# (pattern, which dispatch path it is the witness for)
PART_A = [
    ("a*?b",              "CURSOR"),
    ("(?:ab|b){1,3}?c",   "FRAMES_BOUNDED"),
    ("(?:ab|b)*?c",       "FRAMES_UNBOUNDED"),
    ("(?:a|bc)*?d",       "REVDET"),
    ("(?:ab|b){8,12}?c",  "COUNTER, bounded"),
    ("(?:ab|b){8,}?c",    "COUNTER, unbounded"),
]

# (atomic-lazy pattern, the GREEDY possessive shape the lift would emit, subject)
PART_B = [
    ("(?>a*?)b",           "a*+b",            "aaab"),
    ("(?>a*?)a",           "a*+a",            "aaa"),
    ("(?>a+?)b",           "a++b",            "aaab"),
    ("(?>a{1,3}?)b",       "a{1,3}+b",        "aaab"),
    ("(?>[ab]*?)b",        "[ab]*+b",         "abab"),
    ("(?>a*?)",            "a*+",             "aaa"),
    ("(?>(?:a|bc)*?)d",    "(?:a|bc)*+d",     "abcd"),
    ("(?>a*?)c|ab",        "a*+c|ab",         "aab"),
    # THE CONTROL: the A_ATOMIC's child is an A_CAT, so the lift never applies
    # and this row MUST agree. A suite where every row is red has lost it.
    ("(?>a*?b)c",          "(?>a*b)c",        "aabc"),
]


def stamps(pat):
    with tempfile.TemporaryDirectory() as td:
        o = os.path.join(td, "o.c")
        r = subprocess.run([PCREC, "-p", "rx", "--engine=vm", "--no-captures",
                            "-o", o, pat], capture_output=True, text=True,
                           timeout=60)
        if r.returncode != 0:
            return None
        t = open(o).read()
        g = lambda k: (re.search(r"#define RX_VM_%s (0x[0-9a-f]+)" % k, t) or
                       [None, "?"])[1]
        return (g("STRATS"), g("RUNGS"),
                len(re.findall(r"^ *RX_CUT\(", t, re.M)),
                len(re.findall(r"run->resume_depth = rx_.*_frame_mark;", t)))


def pc(pat, s):
    try:
        rx = P.compile(pat)
    except P.Pcre2Error:
        return "ERR"
    r = rx.search(s, 0)
    return None if r is None else r[0]


def py(pat, s):
    try:
        rx = re.compile(pat)
    except re.error:
        return "ERR"
    m = rx.search(s, 0)
    return None if m is None else m.span()


def main():
    print("libpcre2:", P.version(), "  pcrec:", PCREC)
    print()
    print("=== PART A — lazy quantifiers ARE possessified today, on every path ===")
    print("%-20s %-19s %-8s %-8s %s" % ("PATTERN", "path", "STRATS", "cuts",
                                        "2nd-spelling"))
    print("-" * 68)
    allposs = True
    for pat, want in PART_A:
        st = stamps(pat)
        if st is None:
            print("%-20s REFUSED" % pat)
            allposs = False
            continue
        strats, rungs, calls, second = st
        got = RUNG.get(rungs, rungs)
        if strats != "0x1":
            allposs = False
        print("%-20s %-19s %-8s %-8d %d%s" % (pat, got, strats, calls, second,
              "" if got == want or want.startswith(got) else "  (expected %s)" % want))
    print()
    print("  STRATS 0x1 is VM_STRAT_POSSESSIVE. %s"
          % ("Every path possessifies a lazy body."
             if allposs else "**Some path did NOT** — re-read the table."))
    print()
    print("=== PART B — what the LIFT would answer ===")
    print("The lift emits the GREEDY possessive shape, so its answer is the")
    print("greedy possessive spelling's answer, read off libpcre2 directly.")
    print()
    print("%-18s %-14s %-8s %-9s %-9s %-11s %s"
          % ("ATOMIC-LAZY", "LIFT EMITS", "SUBJ", "pcre2", "python",
             "lift gives", "VERDICT"))
    print("-" * 92)
    bad = 0
    ctrl_ok = None
    for lazy, lift, s in PART_B:
        a, b, c = pc(lazy, s), py(lazy, s), pc(lift, s)
        is_ctrl = (lazy == "(?>a*?b)c")
        ok = (a == c)
        if is_ctrl:
            ctrl_ok = ok
        elif not ok:
            bad += 1
        print("%-18s %-14s %-8s %-9s %-9s %-11s %s"
              % (lazy, lift, repr(s), a, b, c,
                 ("CONTROL ok" if ok else "**CONTROL FAILED**") if is_ctrl
                 else ("agrees" if ok else "**MISCOMPILE**")))
    print()
    print("oracle agreement on the atomic-lazy column: %s"
          % ("libpcre2 and python agree on every row"
             if all(pc(l, s) == py(l, s) for l, _, s in PART_B)
             else "**they disagree somewhere — check before citing**"))
    print()
    if ctrl_ok is None or not ctrl_ok:
        print("VERDICT: THE CONTROL FAILED. `(?>a*?b)c`'s child is an A_CAT, the")
        print("lift does not apply, and it must agree. This run measures nothing.")
        return 1
    if bad == 0:
        print("VERDICT: no row miscompiles — which would REFUTE N1. Check that")
        print("the lift column really is the greedy possessive spelling.")
        return 1
    print("VERDICT: %d of %d lift-eligible rows MISCOMPILE, with the control"
          % (bad, len(PART_B) - 1))
    print("holding. A LAZY body under A_ATOMIC must take the general §3.3 shape,")
    print("never the lift — the same deleted-antecedent shape as nullability.")
    return 0


sys.exit(main())
