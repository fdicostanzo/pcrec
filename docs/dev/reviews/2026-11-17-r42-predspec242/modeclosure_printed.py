import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/modeclosure/work")
from um import URx, P
lt5 = lambda v: v is not None and v.isdigit() and int(v) < 5
b  = lambda n: ("(?<h>\\d)?;" if n else "(?:\\d)?;")
U  = "(?:(?:%s)*%s)?" % (b(0), b(1)); U0 = "(?:(?:%s)*%s)?" % (b(0), b(0))
N = URx("(?:(?:%s,)*%s,)?(?C\"t\")" % (U0, U), {"t": lambda v: lt5(v["h"])}, ("h",))
print("NEST WHOLE", [(t, N.key("WHOLE", t)) for t in ("3;,,", "3;;,", "3;,7;,", "7;,3;,")])
print("NEST SEARCHED `3;,, 7;,`", N.key("SEARCHED", "3;,, 7;,"), "FIND-ALL `3;,, 3;;, 3;,7;,`", N.key("FIND-ALL", "3;,, 3;;, 3;,7;,"))
R = URx(U + '(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",))
print("R13;; WHOLE `3;;`", R.key("WHOLE", "3;;"), "SEARCHED", R.key("SEARCHED", "3;;"), "FIND-ALL `3;7; 7;; 3;`", R.key("FIND-ALL", "3;7; 7;; 3;"))
Rn = URx(U + '(?!(?C"t"))', {"t": lambda v: lt5(v["h"])}, ("h",))
print("R23;; WHOLE `3;;`", Rn.key("WHOLE", "3;;"), "SEARCHED", Rn.key("SEARCHED", "3;;"), "FIND-ALL", Rn.key("FIND-ALL", "3;7; 7;; 3;"))
O = URx("(?:(?:[\\s\\S]*?(?:a)?b)*[\\s\\S]*?(?<x>(?<g>a)?b))[\\s\\S]*(?C\"t\")", {"t": lambda v: v["g"] == "a"}, ("x", "g"))
print("EXPORTED occurrences(/(?<x>(?<g>a)?b)/, min = 1) & (g: a): WHOLE `abb`", O.key("WHOLE", "abb"), "SEARCHED `babb`", O.key("SEARCHED", "babb"), "FIND-ALL `abb ab`", O.key("FIND-ALL", "abb ab"))
