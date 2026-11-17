import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/simulate/wk")
sys.path.insert(1, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/rxmodel_evidence")
from ev import M, run, num
import pcre2h
def show(tag, mk, cond, t, labs=()):
    w, s, f = run(mk, cond, t)
    fs = lambda r: "`%s`@%d %s" % (t[r[0]:r[1].pos], r[0], " ".join("%s=%s" % (n, mk.lab(r[1], n)) for n in labs))
    print(tag, repr(t), "WHOLE", "FAILS" if w is None else "HOLDS " + " ".join("%s=%s" % (n, mk.lab(w, n)) for n in labs),
          "| SEARCHED", "FAILS" if s is None else fs(s), "| FIND-ALL", [fs(x) for x in f if x[1].pos > x[0]])
T = lambda m, st: True
# H1 occurrences(/(?<n>\d+)/ & (n: <100)) on 1234: one-pattern model, condition inside each hit
lt100 = lambda v: num(v) and int(v) < 100
show("H1", M(r'(?:.*?(?<n>\d+)(?C"c"))*.*', {"c": lambda m, st: lt100(m.lab(st, "n"))}), T, "1234", ("n",))
show("H2", M(r'(?:.*?(?<hit>\d+))*.*'), lambda m, st: lt100(m.lab(st, "hit")), "1234", ("hit",))
# KIND: t := /(?<h>\d{1,2}):(?<m>\d\d)/ & (h: >= 10); loop /(?:${t},)*/
ge10 = lambda v: num(v) and int(v) >= 10
K = M(r'(?:(?<h>\d{1,2}):(?<m>\d\d)(?C"c"),)*', {"c": lambda m, st: ge10(m.lab(st, "h"))})
show("KIND loop", K, T, "10:00,11:00,9:00,12:00,", ("h", "m"))
show("KIND hits", M(r'(?<h>\d{1,2}):(?<m>\d\d)'), lambda m, st: ge10(m.lab(st, "h")), "10:00,11:00,9:00,12:00,", ("h", "m"))
def jge(m, st, lo):
    h, mm = m.lab(st, "h"), m.lab(st, "m")
    return num(h) and num(mm) and (int(h), int(mm)) >= lo
K2 = M(r'(?:(?<h>\d{1,2}):(?<m>\d\d)(?C"c"),)*', {"c": lambda m, st: jge(m, st, (10, 0))})
show("KIND joint loop", K2, T, "10:00,11:00,9:00,12:00,", ("h", "m"))
show("KIND joint hits", M(r'(?<h>\d{1,2}):(?<m>\d\d)'), lambda m, st: jge(m, st, (10, 0)), "10:00,11:00,9:00,12:00,", ("h", "m"))
# libpcre2 for the loop (callout)
lib = pcre2h.Pcre(r'(?:(?<h>\d{1,2}):(?<m>\d\d)(?C"c"),)*', {"c": lambda c: ge10(c.get("h"))})
print("libpcre2 KIND loop FIND-ALL", [(a, b) for a, b, _ in lib.findall("10:00,11:00,9:00,12:00,") if b > a], "WHOLE", lib.whole("10:00,11:00,9:00,12:00,"))
# late item STOP line and unpadded
time = r'(?<h>\d{1,2})(?::(?<m>\d\d))?'
LT = M(r'(?:' + time + r'(?C"c"),)*', {"c": lambda m, st: jge(m, st, (9, 30))})
for t in ("10:00,9:00,11:00,", "10:15,9:00,11:15,", "9:45,10:15,", "9:45,10,"):
    show("late item", LT, T, t, ("h", "m"))
