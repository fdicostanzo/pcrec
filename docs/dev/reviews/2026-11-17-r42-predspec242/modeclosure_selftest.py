import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/modeclosure/work")
from mk import *
def marks(pat, s, opts=P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED):
    seen = []
    class X(P.Pcre):
        def _callout(self, b, _):
            seen.append((b.contents.mark.decode() if b.contents.mark else None, b.contents.current_position)); return super()._callout(b, _)
    rx = X(pat + '(?C"e")', {"e": lambda c: True})
    r = rx.match(s, 0, opts)
    return r, seen
print("version", P.version())
print(marks(r'(?:a(*MARK:A)b|a(*MARK:B))c', "ac"))
print(marks(r'x(?=(*MARK:L)y)y', "xy"))
print(marks(r'x(?<=(*MARK:B)x)y', "xy"))
print(marks(r'(?>(*MARK:A)x)y', "xy"))
print(marks(r'(?!(*MARK:N)z)x', "x"))
rx = P.Pcre(r'(?:(?<p>)(?<h>\d)?)*(?C"e")', {"e": lambda c: (print("  callout p", c.span("p"), "h", c.span("h")) or True)})
print("empty-iter", rx.match("3", 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED))
rx = P.Pcre(r'(?:a|(?<e>))*(?C"e")', {"e": lambda c: (print("  callout e", c.span("e")) or True)})
print("empty-iter2", rx.match("a", 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED))
