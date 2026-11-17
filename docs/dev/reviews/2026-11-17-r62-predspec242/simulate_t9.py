import sys
sys.path.insert(1, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/rxmodel_evidence")
import pcre2h, re
def num(v): return v is not None and re.fullmatch(r"0|[1-9]\d*", v) is not None
def late(h, m): return num(h) and num(m) and (int(h), int(m)) >= (9, 30)
for hh in (r"\d{1,2}", r"\d"):
    T2V = r"(?<h>" + hh + r")(?::(?<m>\d\d))?"
    for nm, pat in (("plain", T2V + '(?C"t")'), ("atomic", "(?>" + T2V + ')(?C"t")'), ("PRUNE", T2V + '(*PRUNE)(?C"t")'), ("SKIP", T2V + '(*SKIP)(?C"t")'), ("COMMIT", T2V + '(*COMMIT)(?C"t")')):
        p = pcre2h.Pcre(pat, {"t": lambda c: not late(c.get("h"), c.get("m"))})
        print(hh, nm, [(t, [t[a:b] + "@%d" % a for a, b, _ in p.findall(t)]) for t in ("9:30", "9:30 8:15", "8:15 9:30 7:00", "10:00")])
