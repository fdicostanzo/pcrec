import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/verify")
from vlib import *
co = {"h<5": Tc("h", lt(5)), "l<20": Tc("l", lt(20))}
N1 = lambda: W(OCC(Pat(r"(?:(?P<h>\d);)+"), 1), C("h", lt(5)))
pN1 = pc(r'(?:[\s\S]*?(?:(?<h>\d);)+)+[\s\S]*(?C"h<5")', co, ("h",))
with rules("24"):
    o = OCC(Pat(r"(?:(?P<h>\d);)+"), 1)
    print("set_once_labels(Pat inner-looped h):", set_once_labels(Pat(r"(?:(?P<h>\d);)+")), "; Occ.labs:", o.labs)
    print("set_once_labels(Atom(...)):", set_once_labels(Atom(alt_BA())), "; Rep:", set_once_labels(Rep(Pat(r"(?P<h>\d);"), 1)))
print("N1 on '3;': engine", eng(N1, ("h",))("WHOLE", "3;"), "; PCRE2", pN1("WHOLE", "3;"))
print("N1 engine vs PCRE2:", cmp(eng(N1, ("h",)), pN1, strings("37;x", 5)))
Q8 = lambda: W(OCC(Atom(alt_BA()), 1), lab_l(lt(20)))
pQ8 = pc(r'(?:[\s\S]*?(?>(?|(?<l>\d\d)|(?<l>\d)\d)))+[\s\S]*(?C"l<20")', co, ("l",))
print("Q8 on '11': engine", eng(Q8, ("l",))("WHOLE", "11"), "; PCRE2", pQ8("WHOLE", "11"))
print("Q8 engine vs PCRE2:", cmp(eng(Q8, ("l",)), pQ8, DSP))
