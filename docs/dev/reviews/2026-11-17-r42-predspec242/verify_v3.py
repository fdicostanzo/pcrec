import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/rxmodel_evidence")
import pcre2h as P
W = P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED
for pat in (r"(?J)(?:(?P<x>a)|(?P<x>b))+\k<x>", r"(?J)(?:(?P<x>a)|(?P<x>b))+"):
    rx = P.Pcre(pat)
    for s in ("abba", "abbb", "aba", "abb", "ab", "ba", "baa", "bab"):
        r = rx.match(s, 0, W)
        if r is None: print(pat, s, None); continue
        ov = P.L.pcre2_get_ovector_pointer_8(rx.md)
        g = [(None if ov[2*i] == P.UNSET else s[ov[2*i]:ov[2*i+1]]) for i in range(3)]
        print(pat, s, "WHOLE match, groups 0..2 =", g)
