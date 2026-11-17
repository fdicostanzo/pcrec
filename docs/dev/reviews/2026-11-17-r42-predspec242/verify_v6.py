import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/verify/w")
from eng import *
J = lambda: C(("h", "k"), lambda h, k: num(h) and num(k) and int(h) > int(k))
for nm, pat, texts in (("two depths", r"(?:(?P<k>\d)(?:(?P<h>\d);)*,)*", ("37;,", "73;,", "37;,51;,")),
                       ("siblings", r"(?:(?P<k>\d);)*(?:(?P<h>\d),)*", ("3;7,", "7;3,", "3;9;7,"))):
    for fn, mk in (("bare J", lambda pat=pat: W(Pat(pat), J())), ("some(J)", lambda pat=pat: W(Pat(pat), SOME(J()))),
                   ("occurs.none(NOT J)", lambda pat=pat: W(Pat(pat), NONE(NOT(J()))))):
        f = ekey(mk, ("h", "k"))
        for s in texts:
            for mode in ("WHOLE", "SEARCHED", "FIND-ALL"):
                try: r = f(mode, s)
                except Exception as e: r = "EXC %s: %s" % (type(e).__name__, e)
                print("%s %s `%s` %s: %s" % (nm, fn, s, mode, r))
