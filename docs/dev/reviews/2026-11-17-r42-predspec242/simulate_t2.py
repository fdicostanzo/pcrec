import sys
sys.path.insert(1, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/rxmodel_evidence")
import pcre2h
def trace(pat, s):
    log = []
    def t(c): log.append((c.pos, dict(c._caps))); return True
    r = pcre2h.Pcre(pat, {"t": t, "e": lambda c: (log.append(("END", c.pos, dict(c._caps))) or True)})
    print(pat, repr(s), r.match(s, 0, pcre2h.PCRE2_ANCHORED | pcre2h.PCRE2_ENDANCHORED), log)
trace(r'(?:(?<ps>)(?C"t")(?<h>\d)?,?)*(?C"e")', "3")
trace(r'(?:(?<ps>)(?C"t")(?<h>\d)?,?)*(?C"e")', "3,")
trace(r'(?:(?<ps>)(?C"t")(?<h>\d)?)*(?C"e")', "3")
trace(r'(?:(?<ps>)(?C"t")(?<h>\d)|(?<e>))*(?C"e")', "3")
trace(r'(?J)(?:(?<x>a)|(?<x>b))+\k<x>', "aba")
trace(r'(?J)(?:(?<x>a)|(?<x>b))+\k<x>', "abb")
