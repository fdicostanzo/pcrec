import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/R/tree/docs/dev/lanes/rxmodel_evidence")
import pcre2h
print(pcre2h.version())
seen = []
def j(c):
    seen.append((c.get("h"), c.get("m")))
    return c.get("h") == "10" and c.get("m") == "45"
p = pcre2h.Pcre(r'(?:(?<h>\d+)(?::(?<m>\d\d))?,)*(?C"j")', {"j": j})
for s in ["9:45,10,", "10:45,", "10,9:45,"]:
    seen.clear()
    print(repr(s), "WHOLE", p.whole(s), "SEARCHED", p.search(s), "tuples seen at the condition (first 3):", seen[:3])
