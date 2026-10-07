#!/usr/bin/env python3
"""Arm A family, rev 2 (B-B2 / B-B3).  Superset of ../gen_a.py:

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
          ("+?", 1, False)]
FOLLOWS = [("\\b", True, None), ("\\b\\w", True, None), ("\\b.", True, None), ("\\bx", True, None),
           ("\\b$", True, None), ("(?:\\b|x)", True, "x"), ("(?:\\b|\\.)", True, "\\."),
           ("(?:x?\\b)", True, "x"), ("\\B", "B", None)]
WRAPS = [("{Q}{F}", True), ("({Q}){F}", True), ("x{Q}{F}", True), ("(?:{Q}{F}x)+", False),
         ("(?:{Q})+{F}", False)]

def predicate(F, L, W, A, extra, gated, greedy, mn, wrap_ok, drop=""):
    """The rev-2 A1 predicate for these shapes; `drop` names one ablation."""
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
        for (b, fc, lc), (q, mn, greedy), (f, gated, extra), (w, wrap_ok) in itertools.product(BODIES, QUANTS, FOLLOWS, WRAPS):
            F, L = mem(fc, m), mem(lc, m)
            X = mem(extra, m) if extra else None
            claim = predicate(F, L, W, A, X, gated, greedy, mn, wrap_ok)
            abl = [] if claim else [d for d in ("m0", "lazy", "firstpol", "mixed", "encl")
                                    if predicate(F, L, W, A, X, gated, greedy, mn, wrap_ok, d)]
            hi = "utf" in m and bool(mem(fc, m, HIGH))
            if greedy:
                ps = "{X}" + q + "+"
            else:      # lazy: the possessified loop lands at the MAXIMAL exit
                ps = "(?>{X}%s)" % q[:-1]
            g = w.replace("{Q}", b + q).replace("{F}", f)
            p = w.replace("{Q}", ps.replace("{X}", b)).replace("{F}", f)
            mods = ",".join(x for x in [m, "no_auto_possess"] if x)
            n += 1
            print("A%05d\t%s\t%s\t%s\t%s\t%r\t%s\t%d" % (n, mods, g, p, "yes" if claim else "no",
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
        print("H%04d\t%s\t%s\t%s\tno\t%r\tencl\t0" % (k + 1, mods, g, p, HA))
main()
