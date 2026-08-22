"""probe_possessify_under_cut.py — MEASURED, both arms, and it tests a claim
nobody in this tree has tested.

[M6.4.1] §6.4. `src/opt/possessify.c` runs on the tree AFTER the module lands,
so it will be analysing quantifiers that sit INSIDE, AROUND or BEFORE an atomic
group. Its §2.2 verdict was validated ([ENG-BREP], R24) on a corpus with NO
cuts in it, because pcrec could not compile one. The design's claim is that the
verdict stays sound anyway, on a subset argument: a cut only REMOVES paths, and
"the winner is never a retreat-into-Q path" is inherited by a subset.

THE ARGUMENT HAS A VISIBLE HOLE and that is why this probe exists. The verdict
is about the UNCUT pattern's winner W. In the cut pattern the winner is the
best SURVIVING path W'. If the cut deletes W, nothing in the verdict says W' is
not a retreat-into-Q path — and possessifying Q would then delete W' too.

METHOD. Generate patterns with EXACTLY ONE quantifier and at least one atomic
group. For each:
  - VERDICT: compile the pattern's atomicity-ERASED twin `--engine=vm
    --no-captures` and read `RX_VM_STRATS` (0x1 = possessify marked it). With
    one quantifier in the pattern the bit is unambiguous. Erasure is the right
    model because possessify will see A_ATOMIC as transparent for FIRST/FOLLOW
    (§6.4's proposed rule) -- if the module instead made A_ATOMIC opaque, this
    probe measures the wrong thing and says so here rather than silently.
  - TRUTH: libpcre2's answer for the atomic pattern, and for the atomic pattern
    with that one quantifier written POSSESSIVE. Possessifying is exactly what
    a positive verdict licenses.
  - VIOLATION: verdict POSITIVE and the two answers DIFFER. That is a
    miscompile the module would ship, in the default engine.

The generator puts the quantifier in all three positions relative to the cut
(inside the atomic body, wrapping the atomic group, and before/after it),
because the hole in the argument is position-dependent and a generator that
only produced one position would answer a narrower question than it claims.
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

QBODY = ["a", "[ab]", "(?:a|bc)", "(?:a|ab)", "(?:ab?)"]
QUANT = ["*", "+", "?", "{0,3}", "{1,3}", "{2}"]
ATOM  = ["(?>a|ab)", "(?>ab|a)", "(?>a*)", "(?>[ab]|abc)", "(?>a|b)"]
TAIL  = ["", "c", "b", "a", "bc"]
SUBJ  = ["", "a", "aa", "ab", "aab", "abc", "abcd", "aabc", "abab", "ba",
         "aaab", "b", "bc", "bca", "aaa", "abb"]

_vc = {}


def verdict(erased):
    if erased in _vc:
        return _vc[erased]
    with tempfile.TemporaryDirectory() as td:
        o = os.path.join(td, "o.c")
        r = subprocess.run([PCREC, "-p", "rx", "--engine=vm", "--no-captures",
                            "-o", o, erased], capture_output=True, text=True,
                           timeout=60)
        if r.returncode != 0:
            v = None
        else:
            m = re.search(r"^#define RX_VM_STRATS (0x[0-9a-fA-F]+)u",
                          open(o).read(), re.M)
            v = (m is not None and int(m.group(1), 16) == 0x1)
    _vc[erased] = v
    return v


def ans(pat, s):
    try:
        rx = P.compile(pat)
    except P.Pcre2Error:
        return "ERR"
    r = rx.search(s, 0)
    return None if r is None else r[0]


def shapes(qb, q, at, tail):
    """The three positions of the quantifier relative to the cut. Each entry is
    (plain, possessive) as a PAIR of pattern strings differing in one byte."""
    return [
        ("Q inside the atomic body",
         "(?>%s%s|xy)%s" % (qb, q, tail), "(?>%s%s+|xy)%s" % (qb, q, tail)),
        ("Q wrapping the atomic group",
         "(?:%s)%s%s" % (at, q, tail), "(?:%s)%s+%s" % (at, q, tail)),
        ("Q before the atomic group",
         "%s%s%s%s" % (qb, q, at, tail), "%s%s+%s%s" % (qb, q, at, tail)),
        ("Q after the atomic group",
         "%s%s%s%s" % (at, qb, q, tail), "%s%s%s+%s" % (at, qb, q, tail)),
    ]


def erase(pat):
    return pat.replace("(?>", "(?:")


def main():
    print("libpcre2:", P.version(), "  pcrec:", PCREC)
    print()
    per_shape = {}
    viol = []
    cells = 0
    skipped = 0
    for qb, q, at, tail in itertools.product(QBODY, QUANT, ATOM, TAIL):
        for name, plain, poss in shapes(qb, q, at, tail):
            v = verdict(erase(plain))
            st = per_shape.setdefault(name, {"pos": 0, "neg": 0, "skip": 0,
                                             "viol": 0})
            if v is None:
                st["skip"] += 1
                skipped += 1
                continue
            st["pos" if v else "neg"] += 1
            for s in SUBJ:
                cells += 1
                a = ans(plain, s)
                b = ans(poss, s)
                if a == "ERR" or b == "ERR":
                    continue
                if v and a != b:
                    st["viol"] += 1
                    viol.append((name, plain, poss, s, a, b))

    print("cells (pattern x subject): %d    patterns pcrec refused: %d"
          % (cells, skipped))
    print()
    print("%-30s %8s %8s %8s %10s" % ("QUANTIFIER POSITION", "verdict+",
                                      "verdict-", "refused", "VIOLATIONS"))
    for name, st in per_shape.items():
        print("%-30s %8d %8d %8d %10d"
              % (name, st["pos"], st["neg"], st["skip"], st["viol"]))
    print()
    print("REFUTING CONDITION: a POSITIVE possessify verdict on a quantifier")
    print("whose possessive spelling changes libpcre2's answer for the")
    print("ATOMIC pattern. Total: %d" % len(viol))
    for r in viol[:20]:
        print("  [%s]" % r[0])
        print("    plain %-30s poss %-30s subj %-8s -> %s vs %s"
              % (r[1], r[2], repr(r[3]), r[4], r[5]))
    if len(viol) > 20:
        print("  ... %d more" % (len(viol) - 20))
    print()
    if not viol:
        print("VERDICT: possessify's §2.2 verdict survives the cut on this")
        print("family, in all four quantifier positions. This is EVIDENCE,")
        print("NOT A PROOF -- the subset argument's hole (§6.4) is closed by")
        print("measurement over a generated family, not by a theorem.")
    else:
        print("VERDICT: REFUTED. possessify must be gated in the presence of")
        print("an atomic node; see the violating positions above.")
    # THE NON-VACUITY COUNTER. A run where the possessive spelling never
    # changed the answer ANYWHERE would report zero violations for a reason
    # that has nothing to do with the cut.
    nv = 0
    for qb, q, at, tail in itertools.product(QBODY[:2], QUANT, ATOM[:2], TAIL[:2]):
        for name, plain, poss in shapes(qb, q, at, tail):
            for s in SUBJ:
                if ans(plain, s) != ans(poss, s):
                    nv += 1
    print()
    print("NON-VACUITY (a subsample): cells where the possessive spelling DOES")
    print("change libpcre2's answer, verdict ignored: %d. If this were 0 the" % nv)
    print("zero above would mean nothing.")


main()
