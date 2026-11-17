import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/modeclosure/work")
from mk import *
seen=[]
class X(P.Pcre):
    def _callout(self, b, _):
        seen.append(b.contents.mark.decode() if b.contents.mark else None); return super()._callout(b, _)
rx = X(r'(?:(*MARK:P)(?:(?<h>\d)(*MARK:Hh))?;)*(?C"e")', {"e": lambda c: True})
print(rx.match("3;", 0, P.PCRE2_ANCHORED|P.PCRE2_ENDANCHORED), seen)
