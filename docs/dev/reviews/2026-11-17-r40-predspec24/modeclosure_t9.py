import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/modeclosure")
from mc_lib import *
W, Pat, C, OCC, lt, NOT, ORC, Atom, ALT, Rep, D, eq = (g(k) for k in ("W", "Pat", "C", "OCC", "lt", "NOT", "ORC", "Atom", "ALT", "Rep", "D", "eq"))
strings = g("strings")
OP = strings("12 x", 5)
DSP = strings("129 ", 5)
CO = {"n<100": Tc("n", lt(100)), "n<10": Tc("n", lt(10)), "l<20": Tc("l", lt(20)), "h<5": Tc("h", lt(5)), "a=1": Tc("a", eq("1"))}
N = r"(?P<n>\d+)"
rows = [
 ("Q1 NOT inside occurrences", lambda: OCC(W(Pat(N), NOT(C("n", lt(100)))), 1), r'(?:[\s\S]*?(?<n>\d+)(?!(?C"n<100")))+[\s\S]*', ("n",), OP),
 ("Q2 `NOT c | d` inside occurrences", lambda: OCC(W(Pat(N), ORC(NOT(C("n", lt(10))), C("n", lt(100)))), 1), r'(?:[\s\S]*?(?<n>\d+)(?:(?!(?C"n<10"))|(?C"n<100")))+[\s\S]*', ("n",), OP),
 ("Q3 atomic inside occurrences", lambda: OCC(W(Atom(ALT(Pat(r"(?P<l>\d\d)"), Pat(r"(?P<l>\d)\d"))), C("l", lt(20))), 1), r'(?:[\s\S]*?(?>(?|(?<l>\d\d)|(?<l>\d)\d))(?C"l<20"))+[\s\S]*', ("l",), DSP),
 ("Q4 condition inside atomic inside occurrences", lambda: OCC(Atom(W(ALT(Pat(r"(?P<l>\d\d)"), Pat(r"(?P<l>\d)\d")), C("l", lt(20)))), 1), r'(?:[\s\S]*?(?>(?|(?<l>\d\d)|(?<l>\d)\d)(?C"l<20")))+[\s\S]*', ("l",), DSP),
 ("Q5 occurrences then a bare outer condition (last hit), FIND-ALL included", lambda: W(OCC(Pat(N), 1), C("n", lt(100))), r'(?:[\s\S]*?(?<n>\d+))+[\s\S]*(?C"n<100")', ("n",), OP),
 ("Q6 NOT after occurrences", lambda: W(OCC(Pat(N), 1), NOT(C("n", lt(10)))), r'(?:[\s\S]*?(?<n>\d+))+[\s\S]*(?!(?C"n<10"))', ("n",), OP),
 ("Q7 a loop over a conditioned item, NOT inside", lambda: Rep(W(Pat(r"(?P<h>\d);"), NOT(C("h", lt(5)))), 1), r'(?:(?<h>\d)(?!(?C"h<5"));)+', ("h",), strings("37;", 5)),
]
for nm, mk, pat, labs, pool in rows:
    print(nm + ":", cmp(enkey(mk, labs), rxkey(pat, CO, labs), pool))
