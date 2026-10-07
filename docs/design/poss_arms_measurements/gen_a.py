#!/usr/bin/env python3
"""Arm A family: PRE + C{q} + F (+ wrappers), greedy vs possessive spelling.
CLAIM column = what the PROPOSED predicate (context-sharpened FIRST at the
\b gate, m>=1, greedy, unique-iteration body, FIRST/LAST C-pure wrt W) says.
Class membership and \w are taken from libpcre2 itself, per mode."""
import subprocess, itertools
MODES = {"": 1, "i": 1, "ucp": 1, "utf": 1, "utf,ucp": 1, "utf,i": 1}
BASE = ["a", "k", "K", "x", "1", "_", " ", ".", "é"]
def alpha(m): return BASE + (["K"] if "utf" in m else [])

def member(cls, mods):
    lines = []
    for ch in alpha(mods):
        lines.append('"^(?:%s)$"%s' % (cls, mods))
        lines.append("\\x{%x}" % ord(ch)); lines.append("")
    out = subprocess.run(["pcre2test", "-q"], input="\n".join(lines).encode(),
                         stdout=subprocess.PIPE).stdout.decode("latin-1").split("\n")
    res = []; i = 0
    for ln in out:
        if ln.startswith(" 0:"): res.append(True)
        elif ln.startswith("No match"): res.append(False)
    assert len(res) == len(alpha(mods)), (cls, mods, res)
    return {ch for ch, r in zip(alpha(mods), res) if r}

# body: (spelling, first-class, last-class) -- single class bodies have first=last
BODIES = [("\\w", "\\w", "\\w"), ("[a-c]", "[a-c]", "[a-c]"), ("[a-z_0-9]", "[a-z_0-9]", "[a-z_0-9]"),
          ("\\d", "\\d", "\\d"), ("k", "k", "k"), ("[j-l]", "[j-l]", "[j-l]"),
          ("\\W", "\\W", "\\W"), ("[ .]", "[ .]", "[ .]"), ("[a .]", "[a .]", "[a .]"),
          (".", ".", "."), ("[^x]", "[^x]", "[^x]"),
          ("(?:ak)", "a", "k"), ("(?:a\\.)", "a", "\\."), ("(?:\\.a)", "\\.", "a")]
QUANTS = [("+", 1, True), ("{1,3}", 1, True), ("{2,}", 2, True), ("*", 0, True), ("?", 0, True),
          ("+?", 1, False)]
# follow: spelling, gate-at-head?, extra bytes that bypass the gate (as class spelling or None)
FOLLOWS = [("\\b", True, None), ("\\b\\w", True, None), ("\\b.", True, None), ("\\bx", True, None), ("\\b$", True, None), ("(?:\\b|x)", True, "x"), ("(?:\\b|\\.)", True, "\\."), ("(?:x?\\b)", True, "x"),
           ("\\B", False, None)]
WRAPS = [("{Q}{F}", True), ("({Q}){F}", True), ("x{Q}{F}", True), ("(?:{Q}{F}x)+", False), ("(?:{Q})+{F}", False)]

def main():
    import sys
    modes = sys.argv[1].split(";") if len(sys.argv) > 1 else list(MODES)
    cache = {}
    def mem(c, m):
        if (c, m) not in cache: cache[(c, m)] = member(c, m)
        return cache[(c, m)]
    n = 0
    for m in modes:
        W = mem("\\w", m)
        A = set(alpha(m))
        for (b, fc, lc), (q, mn, greedy), (f, gated, extra), (w, wrap_ok) in itertools.product(BODIES, QUANTS, FOLLOWS, WRAPS):
            F, L = mem(fc, m), mem(lc, m)
            Fpure = F <= W or not (F & W)
            Lpure = L <= W or not (L & W)
            claim = "no"
            if gated and greedy and mn >= 1 and wrap_ok and Fpure and Lpure:
                lword = L <= W
                gate_ok = {c for c in A if (c in W) != lword}   # \b given left polarity
                eff = set(gate_ok) | (mem(extra, m) if extra else set())
                if not (F & eff):
                    claim = "yes"
            pq = q + "+" if greedy else None
            if pq is None:   # lazy: possessive spelling is (?>X{q}) -- min exit; compare max-exit atomic instead
                base = q[:-1]
                ps = "(?>{X}%s)" % base
            else:
                ps = "{X}" + pq
            Xg = b + q
            Xp = ps.replace("{X}", b)
            g = w.replace("{Q}", Xg).replace("{F}", f)
            p = w.replace("{Q}", Xp).replace("{F}", f)
            mods = ",".join(x for x in [m, "no_auto_possess"] if x)
            n += 1
            print("A%05d\t%s\t%s\t%s\t%s\t%r" % (n, mods, g, p, claim, alpha(m)))
main()
