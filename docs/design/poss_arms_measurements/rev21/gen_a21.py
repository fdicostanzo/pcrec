#!/usr/bin/env python3
"""Arm A family, rev 2.1 (possarms21), FROZEN at the sha in poss_arms.md §8.3a.
Adds, over rev 2 (gen_a2.py):
  - N2: follows with an empty BYPASS around the gate, `(?:\\b|)` and
    `(?:\\B|)`, and the bounded lazy quantifiers `{1,3}?` and `{2,}?`. The
    `lazy` ablation is what PROTO_SAB_LAZY does: A1 admitted for a lazy loop
    with row 2's may_end ignored. Rev 2 had no nullable follow, which is why
    its lazy ablation read 0 diverging.
  - the R block: a gate INSIDE A REFERENCED GROUP (`({F}){Q}\\1`,
    `({F}){Q}\\1k`): Q's follow is the reference, whose FIRST is the TEXT the
    group captured, where every gate is zero-width (N1). Claimed by today's
    ladder over that text model; tag `textpos` = the position reading
    (an A0-narrowed gate non-nullable) would claim it.
  - the N2 hand witnesses, and column 9 `src` (computed | hand), R-3(b).
Rev 2 docstring follows.

Arm A family, rev 2 (B-B2 / B-B3).  Superset of ../gen_a.py:

  - models `\B` as a gate too (it admits the left character's OWN wordness);
    rev 1's gen_a.py never claimed a `\B` row, and CLAIM-vs-MARK found the
    prototype soundly marking `(?:a\.)+\B` (LAST `.`, FIRST `a`), a shape
    the rev-1 predicate could not express;
  - adds the MIXED-LAST multi-character body (?:a[a.]) (S562's witness
    shape, B-B2);
  - adds column 7 `abl`: the comma list of ABLATED predicates that would
    CLAIM a row the full predicate does not (B-B3's ablation table):
        m0       drop m >= 1
        lazy     drop greedy-only
        firstpol read the polarity from FIRST(X) instead of LAST(X)
        mixed    collapse a mixed LAST to one polarity ("word" if any member is)
        encl     ignore an enclosing loop (claim the wrapped shape as if bare)
  - adds column 8 `hi`: 1 when FIRST(X) has a member above U+00FF (probed
    with U+0100 U+0131 U+017F U+0660 U+212A U+4E00 under the utf modes).
    pcrec's FIRST sets are code points <= 0xFF and widen to all bytes past
    that (possessify.c's A_CLASS arm), so a `hi` claim is one pcrec DECLINES
    BY REPRESENTATION; CLAIM-vs-MARK reads `claim && !hi` as the expectation.

The CLAIM column is computed from class membership asked of libpcre2 itself
(`^(?:C)$` per character per mode), never from pcrec.  Output rows feed
../eqcheck.py (columns 1-6) and r2_claimmark.py (all columns)."""
import subprocess, itertools, sys
MODES = ["", "i", "ucp", "utf", "utf,ucp", "utf,i"]
BASE = ["a", "k", "K", "x", "1", "_", " ", ".", "é"]
HIGH = ["Ā", "ı", "ſ", "٠", "K", "一"]
def alpha(m): return BASE + (["K"] if "utf" in m else [])

def member(cls, mods, chars):
    lines = []
    for ch in chars:
        lines.append('"^(?:%s)$"%s' % (cls, mods))
        lines.append("\\x{%x}" % ord(ch)); lines.append("")
    out = subprocess.run(["pcre2test", "-q"], input="\n".join(lines).encode(),
                         stdout=subprocess.PIPE).stdout.decode("latin-1").split("\n")
    res = []
    for ln in out:
        if ln.startswith(" 0:"): res.append(True)
        elif ln.startswith("No match"): res.append(False)
    assert len(res) == len(chars), (cls, mods, res)
    return {ch for ch, r in zip(chars, res) if r}

BODIES = [("\\w", "\\w", "\\w"), ("[a-c]", "[a-c]", "[a-c]"), ("[a-z_0-9]", "[a-z_0-9]", "[a-z_0-9]"),
          ("\\d", "\\d", "\\d"), ("k", "k", "k"), ("[j-l]", "[j-l]", "[j-l]"),
          ("\\W", "\\W", "\\W"), ("[ .]", "[ .]", "[ .]"), ("[a .]", "[a .]", "[a .]"),
          (".", ".", "."), ("[^x]", "[^x]", "[^x]"),
          ("(?:ak)", "a", "k"), ("(?:a\\.)", "a", "\\."), ("(?:\\.a)", "\\.", "a"),
          ("(?:a[a.])", "a", "[a.]")]
QUANTS = [("+", 1, True), ("{1,3}", 1, True), ("{2,}", 2, True), ("*", 0, True), ("?", 0, True),
          ("+?", 1, False), ("{1,3}?", 1, False), ("{2,}?", 2, False)]
FOLLOWS = [("\\b", True, None), ("\\b\\w", True, None), ("\\b.", True, None), ("\\bx", True, None),
           ("\\b$", True, None), ("(?:\\b|x)", True, "x"), ("(?:\\b|\\.)", True, "\\."),
           ("(?:x?\\b)", True, "x"), ("\\B", "B", None),
           ("(?:\\b|)", True, None, True), ("(?:\\B|)", "B", None, True)]
FOLLOWS = [f if len(f) == 4 else f + (False,) for f in FOLLOWS]
# the TEXT model of each follow, for the R block: (class expr of its first
# characters or None, nullable) -- a gate is zero-width in a text
FTEXT = {"\\b": (None, True), "\\b\\w": ("\\w", False), "\\b.": (".", False),
         "\\bx": ("x", False), "\\b$": (None, True), "(?:\\b|x)": ("x", True),
         "(?:\\b|\\.)": ("\\.", True), "(?:x?\\b)": ("x", True), "\\B": (None, True),
         "(?:\\b|)": (None, True), "(?:\\B|)": (None, True)}
WRAPS = [("{Q}{F}", True), ("({Q}){F}", True), ("x{Q}{F}", True), ("(?:{Q}{F}x)+", False),
         ("(?:{Q})+{F}", False)]

def predicate(F, L, W, A, extra, gated, greedy, mn, wrap_ok, drop="", bypass=False):
    """The rev-2.1 A1 predicate for these shapes; `drop` names one ablation.
    `bypass` (an empty branch around the gate) changes nothing for a GREEDY
    loop -- row 3 does not read may_end -- and the `lazy` ablation ignores
    may_end too, which is exactly the defect N2 measured."""
    if not gated: return False
    if not greedy and drop != "lazy": return False
    if mn < 1 and drop != "m0": return False
    if not wrap_ok and drop != "encl": return False
    if drop == "firstpol":
        if not (F <= W or not (F & W)): return False
        lword = F <= W
    elif drop == "mixed":
        lword = bool(L & W)
    else:
        if not (L <= W or not (L & W)): return False
        lword = L <= W
    if gated == "B":   # \B admits the SAME wordness as the left character
        gate_ok = {c for c in A if (c in W) == lword}
    else:              # \b admits the OTHER wordness
        gate_ok = {c for c in A if (c in W) != lword}
    eff = gate_ok | (extra or set())
    return not (F & eff)

def main():
    modes = sys.argv[1].split(";") if len(sys.argv) > 1 else MODES
    cache = {}
    def mem(c, m, chars=None):
        key = (c, m, chars is not None)
        if key not in cache: cache[key] = member(c, m, chars if chars is not None else alpha(m))
        return cache[key]
    n = 0
    for m in modes:
        W = mem("\\w", m)
        A = set(alpha(m))
        for (b, fc, lc), (q, mn, greedy), (f, gated, extra, byp), (w, wrap_ok) in itertools.product(BODIES, QUANTS, FOLLOWS, WRAPS):
            F, L = mem(fc, m), mem(lc, m)
            X = mem(extra, m) if extra else None
            claim = predicate(F, L, W, A, X, gated, greedy, mn, wrap_ok, bypass=byp)
            abl = [] if claim else [d for d in ("m0", "lazy", "firstpol", "mixed", "encl")
                                    if predicate(F, L, W, A, X, gated, greedy, mn, wrap_ok, d, bypass=byp)]
            hi = "utf" in m and bool(mem(fc, m, HIGH))
            if greedy:
                ps = "{X}" + q + "+"
            else:      # lazy: the possessified loop lands at the MAXIMAL exit
                ps = "(?>{X}%s)" % q[:-1]
            g = w.replace("{Q}", b + q).replace("{F}", f)
            p = w.replace("{Q}", ps.replace("{X}", b)).replace("{F}", f)
            mods = ",".join(x for x in [m, "no_auto_possess"] if x)
            n += 1
            print("A%05d\t%s\t%s\t%s\t%s\t%r\t%s\t%d\tcomputed" % (n, mods, g, p, "yes" if claim else "no",
                                                         alpha(m), ",".join(abl), hi))
        # the R block: the follow F inside a REFERENCED group before Q
        for (b, fc, lc), (q, mn, greedy), (f, gated, extra, byp), (rw, tail) in itertools.product(
                BODIES, QUANTS, FOLLOWS, [("({F}){Q}\\1", None), ("({F}){Q}\\1k", "k")]):
            F = mem(fc, m)
            tc, tn = FTEXT[f]
            T = mem(tc, m) if tc else set()
            # POST-FREEZE EDIT 1 (poss_arms.md §8.3a): pcrec declines by
            # representation only when the follow is NON-EMPTY and some set
            # in the comparison widens: FIRST(X) or a follow class has a
            # member above U+00FF (libpcre2's fold: `(?i)k` under utf), or
            # pcrec's parse-time fold puts U+212A/U+017F into a caseless
            # class with k/s in it (cls_casefold folds `\w` too; libpcre2
            # does not).  Trigger rows: 225 hi-but-marked, 520 tail-`k` /
            # `(\b\w)` declines (A35437.., A52978.., A54035..).
            def phi(c):
                if c is None: return False
                hi_ = "utf" in m and bool(mem(c, m, HIGH))
                fold_ = "utf" in m.split(",") and "i" in m.split(",") and bool(mem(c, m) & {"k", "K", "s", "S"})
                return hi_ or fold_
            thi = phi(tc) or bool(tail and tn and phi(tail))
            follow = T | (mem(tail, m) if (tail and tn) else set())
            may_end = tn and not tail
            claim = not (F & follow) and (greedy or not may_end)
            # position reading: a \b/\B gate is A0-unnarrowable -> all, non-nullable
            abl = []
            hi = int(bool(follow) and (("utf" in m and bool(mem(fc, m, HIGH))) or thi))
            g = rw.replace("{F}", f).replace("{Q}", b + q)
            ps = (b + q + "+") if greedy else "(?>%s%s)" % (b, q[:-1])
            p = rw.replace("{F}", f).replace("{Q}", ps)
            mods = ",".join(x for x in [m, "no_auto_possess"] if x)
            n += 1
            print("A%05d\t%s\t%s\t%s\t%s\t%r\t%s\t%d\tcomputed" % (n, mods, g, p, "yes" if claim else "no",
                                                         alpha(m), ",".join(abl), hi))
    # ENCL's control (B-B3).  The family's wrapped rows put the gate at the
    # HEAD of the in-body continuation, so a restart can only happen behind
    # it and dropping ENCL loses nothing there (0 of 2,196 diverge).  A gate
    # with an empty BYPASS reaches the enclosing loop's end, and the loop's
    # restart is what rescues the match: these rows are claimed only when
    # ENCL is dropped, and they diverge.
    HA = ["a", "b", "c", " ", "."]
    for k, (g, p) in enumerate([
            ("(?:a+(?:\\b|)|ab)+c", "(?:a++(?:\\b|)|ab)+c"),
            ("(?:a{1,3}(?:\\b|)|ab)+c", "(?:a{1,3}+(?:\\b|)|ab)+c"),
            ("(?:[ab]+(?:\\b|)|ba)+c", "(?:[ab]++(?:\\b|)|ba)+c"),
            ("(?:a+(?:\\b|)|ab)+c", "(?:a++(?:\\b|)|ab)+c")]):
        mods = "no_auto_possess" if k < 3 else "i,no_auto_possess"
        print("H%04d\t%s\t%s\t%s\tno\t%r\tencl\t0\thand" % (k + 1, mods, g, p, HA))
    # N2's 10.46 witness (re-check critic R) and its relatives: a LAZY loop
    # whose continuation reaches the match end through an empty bypass,
    # never testing the gate.  Declined by greedy-only; claimed by the plant.
    NA = ["a", "b", " ", "."]
    for k, (g, p) in enumerate([
            ("(\\w+?(?:\\b|))", "(\\w++(?:\\b|))"),
            ("\\w+?(?:\\b|)", "\\w++(?:\\b|)"),
            ("(\\w{1,3}?(?:\\b|))", "(\\w{1,3}+(?:\\b|))"),
            ("[a-c]+?(?:\\B|)", "[a-c]++(?:\\B|)")]):
        print("N%04d\tno_auto_possess\t%s\t%s\tno\t%r\tlazy\t0\thand" % (k + 1, g, p, NA))
main()
