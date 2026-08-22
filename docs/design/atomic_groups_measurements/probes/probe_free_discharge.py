"""probe_free_discharge.py — MEASURED, IN-PCREC on one arm and libpcre2 on the
other. The [M6.4.1] design's §5 (the engine split) FREE DISCHARGE, tested
rather than asserted.

THE RULE UNDER TEST. A user-written possessive `X{m,n}+` is a NO-OP exactly
when `src/opt/possessify.c`'s §2.2 verdict on the SAME quantifier is positive
— that verdict's whole content is "no retreat into this loop can produce a
match the preferred path does not", which is precisely "the cut deletes
nothing". If that is right, the module may DISCHARGE such a possessive (drop
the semantic mark) and the pattern stays DFA-eligible; if it is wrong, the
discharge is a silent miscompile in the DEFAULT engine.

HOW THE VERDICT IS READ WITHOUT NEW CODE, which is the point of this probe.
pcrec refuses the `+` spelling today, so the verdict cannot be asked of the
possessive pattern. It CAN be asked of the pattern's NON-POSSESSIVE TWIN:
compile it `--engine=vm` (which is what makes `run_possessify` run at all,
src/opt/select_engine.c:234) and read `RX_VM_STRATS` off the artifact —
bit 0x1 is `VM_STRAT_POSSESSIVE`, set by `vm_rung_mark` from `a->possessive`
(src/gen/emit_vm.c:252-255, :1751-1753), i.e. exactly possessify's verdict.
That is the SHIPPED analysis answering, not a model of it.

THE INDEPENDENT ARM is libpcre2: for every (pattern, subject) cell it answers
the possessive pattern AND its non-possessive twin. A cell where the verdict
is POSITIVE and libpcre2's two answers DIFFER refutes the discharge rule.

TWO POPULATIONS ARE REPORTED SEPARATELY AND THIS IS NOT COSMETIC:
 - VERDICT POSITIVE, answers differ  -> the discharge would MISCOMPILE.
 - VERDICT NEGATIVE, answers always agree -> the discharge is INCOMPLETE
   (it declines a pattern it could have rescued). Harmless, and the number
   is what says whether §2.2 is the right condition or merely a safe one.

U9 IS SUBTRACTED EXPLICITLY, not silently. docs/dev/upstream_issues.md U9
records a libpcre2 10.46 behaviour on `{m,n}+`-over-a-GROUP with a preceding
item that consumed: PCRE2 refuses to backtrack into the PRECEDING item, which
python and a hand derivation both say it should. Those cells make the
possessive and plain answers differ for a reason that is not the cut, so a
probe that lumped them in would report the discharge rule as refuted by
somebody else's bug. Every violation is classified, and the U9-shaped ones
are listed in their own bucket with the criterion printed.
"""
import itertools
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "eng_brep_measurements", "probes"))
import pcre2_ctypes as P  # noqa: E402

PCREC = os.environ.get("PCREC", "build/pcrec")

PRE    = ["", "a?", "x", "b*"]
BODIES = ["a", "[ab]", "(?:a|bc)", "(?:a|ab)", "(?:ab?)", "(?:a|b)", "(?:abc)",
          "[^\"]", "(?:a|bb)"]
QUANT  = ["*", "+", "?", "{0,3}", "{1,3}", "{2}", "{2,}"]
FOLLOW = ["", "c", "d", "a", "b", "\"", "bc"]
SUBJ   = ["", "a", "aa", "aaa", "ab", "abc", "abcd", "aab", "aabc", "bca",
          "aaab", "\"x\"", "abab", "b", "bb", "bbc"]

_verdict_cache = {}


def possessify_verdict(pat):
    """True iff pcrec's shipped possessify pass marks EVERY quantifier in
    `pat`. Returns None if pcrec refuses the pattern (then the cell is not
    this probe's business and is dropped, counted, and reported)."""
    if pat in _verdict_cache:
        return _verdict_cache[pat]
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "o.c")
        r = subprocess.run([PCREC, "-p", "rx", "--engine=vm", "--no-captures",
                            "-o", out, pat],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            v = None
        else:
            m = re.search(r"^#define RX_VM_STRATS (0x[0-9a-fA-F]+)u",
                          open(out).read(), re.M)
            # 0x1 = VM_STRAT_POSSESSIVE only. A pattern with several
            # quantifiers ORs the bits, so "0x1 alone" is "ALL of them were
            # marked" -- the conservative reading, and the right one here.
            v = (m is not None and int(m.group(1), 16) == 0x1)
    _verdict_cache[pat] = v
    return v


def pcrun(rx, subj):
    r = rx.search(subj, 0)
    return None if r is None else r[0]


def u9_shaped(pre, body, quant):
    """U9's measured trigger, stated as a predicate over this probe's own
    generator rather than inferred from a pattern string: a BOUNDED brace
    possessive of a GROUP, with a preceding item that can consume and then
    give back. See docs/dev/upstream_issues.md U9 for the isolation that
    established all three conjuncts."""
    return (quant.startswith("{") and quant.endswith("}") and "," in quant
            and body.startswith("(?:")
            and pre not in ("", "x"))


CONTROLS = [
    # (possessive pattern, plain twin, subject, what this row proves)
    ("a*+a",  "a*a",  "aaa",
     "the canonical cut: verdict MUST be negative and the answers MUST differ"),
    ("(?:a|ab){1,3}+c", "(?:a|ab){1,3}c", "abc",
     "possessify's own §2.4 117-counterexample family"),
    ("[^\"]*+\"", "[^\"]*\"", 'say \"hi\"',
     "the canonical possessive IDIOM: verdict positive, answers identical"),
    ("a?(?:b){0,4}+a", "a?(?:b){0,4}a", "a",
     "U9's own witness (libpcre2 quirk, not the cut)"),
]


def controls():
    """THE PROBE'S OWN POSITIVE AND NEGATIVE CONTROLS. A run that reports
    "0 violations" is worth nothing unless the instrument could have reported
    one, and this project's record is full of checks that could not (see
    docs/design/assertions_measurements/CLAUDE.md). These four rows are
    printed every run: two where the possessive MUST change the answer and
    the verdict MUST be negative, one where it must not and the verdict must
    be positive, and U9's witness."""
    print("=== CONTROLS (printed every run; the instrument proving it can fire) ===")
    ok = True
    for poss, plain, subj, why in CONTROLS:
        v = possessify_verdict(plain)
        try:
            a = pcrun(P.compile(poss), subj)
            b = pcrun(P.compile(plain), subj)
        except P.Pcre2Error as e:
            a = b = "ERR:%s" % e
        print("  %-22s vs %-20s subj %-9s verdict=%-7s poss=%-8s plain=%-8s %s"
              % (poss, plain, repr(subj), v, a, b,
                 "DIFFER" if a != b else "same"))
        print("      %s" % why)
        if v is True and a != b and "U9" not in why:
            print("      *** CONTROL FAILED: positive verdict on a differing cell")
            ok = False
    print("  controls consistent: %s" % ("yes" if ok else "NO"))
    print()
    return ok


def main():
    print("libpcre2:", P.version(), "  pcrec:", PCREC)
    print()
    controls()
    cells = 0
    refused = 0
    pos_verdict_pats = 0
    neg_verdict_pats = 0
    viol = []
    u9_viol = []
    incomplete = []      # verdict negative but never differs
    rescued = []         # verdict positive: the discharge's population
    npats = 0
    pos_u9_shaped = [0]
    for pre, body, quant, follow in itertools.product(PRE, BODIES, QUANT, FOLLOW):
        plain = pre + body + quant + follow
        poss = pre + body + quant + "+" + follow
        v = possessify_verdict(plain)
        if v is None:
            refused += 1
            continue
        npats += 1
        try:
            rp = P.compile(poss)
            rq = P.compile(plain)
        except P.Pcre2Error:
            refused += 1
            continue
        if v:
            pos_verdict_pats += 1
            rescued.append(poss)
            if u9_shaped(pre, body, quant):
                pos_u9_shaped[0] += 1
        else:
            neg_verdict_pats += 1
        differs_anywhere = False
        for s in SUBJ:
            cells += 1
            a = pcrun(rp, s)
            b = pcrun(rq, s)
            if a != b:
                differs_anywhere = True
                if v:
                    (u9_viol if u9_shaped(pre, body, quant) else viol).append(
                        (poss, plain, s, a, b))
        if not v and not differs_anywhere:
            incomplete.append((poss, plain))

    print("patterns generated and compilable by BOTH pcrec and libpcre2: %d"
          % npats)
    print("  (dropped: %d pattern/compile refusals -- reported, not hidden)" % refused)
    print("cells (pattern x subject): %d" % cells)
    print()
    print("possessify §2.2 verdict POSITIVE on every quantifier : %d patterns"
          % pos_verdict_pats)
    print("possessify §2.2 verdict NEGATIVE                     : %d patterns"
          % neg_verdict_pats)
    print()
    print("=== THE DISCHARGE RULE ===")
    print("REFUTING CONDITION: a POSITIVE verdict on a pattern whose possessive")
    print("and non-possessive spellings give libpcre2 DIFFERENT answers.")
    print("violations (U9 excluded): %d" % len(viol))
    for r in viol[:12]:
        print("   poss %-26s plain %-26s subj %-7s poss=%s plain=%s" % r)
    if len(viol) > 12:
        print("   ... %d more" % (len(viol) - 12))
    print()
    print("positive-verdict patterns that are U9-SHAPED at all: %d --" % pos_u9_shaped[0])
    print("if this is 0 the subtraction below had NOTHING to subtract, which is")
    print("a fact about the generator, not evidence that U9 is absent.")
    print()
    print("U9-SHAPED cells subtracted (bounded {m,n}+ of a GROUP with a")
    print("preceding backtrackable item -- libpcre2's own recorded quirk): %d"
          % len(u9_viol))
    for r in u9_viol[:8]:
        print("   poss %-26s plain %-26s subj %-7s poss=%s plain=%s" % r)
    if len(u9_viol) > 8:
        print("   ... %d more" % (len(u9_viol) - 8))
    print()
    print("=== HOW COMPLETE IS §2.2 AS A DISCHARGE CONDITION ===")
    print("patterns with a NEGATIVE verdict whose possessive spelling never")
    print("changed the answer on ANY subject in this set: %d of %d"
          % (len(incomplete), neg_verdict_pats))
    print("  (these are rescues the discharge DECLINES. Not a defect -- §2.2")
    print("   is a sufficient condition and declining is always safe -- but it")
    print("   is the size of the gap, and a subject set this small OVERSTATES")
    print("   it: 'never differed on 16 subjects' is not 'is a no-op'.)")
    for p, q in incomplete[:10]:
        print("     %-28s (twin %s)" % (p, q))
    if len(incomplete) > 10:
        print("     ... %d more" % (len(incomplete) - 10))
    print()
    print("=== THE RESCUED POPULATION (what the discharge buys) ===")
    print("possessive patterns the discharge turns back into DFA-eligible")
    print("ones, assuming nothing ELSE forces the VM: %d of %d (%.1f%%)"
          % (pos_verdict_pats, npats, 100.0 * pos_verdict_pats / max(npats, 1)))
    for p in rescued[:14]:
        print("     %s" % p)
    if len(rescued) > 14:
        print("     ... %d more" % (len(rescued) - 14))


main()
