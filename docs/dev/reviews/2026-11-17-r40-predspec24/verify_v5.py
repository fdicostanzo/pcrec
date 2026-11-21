import sys, re as _re; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/verify")
from vlib import *
A = lambda: Pat(r"\d")
with rules("24"):
    for B in (r"\d$", r"\d(?=\d)", r"\d\b"):
        x = AND(A(), Pat(B)); z = ZERO(A(), Pat(B)); dd = D(A(), Pat(B))
        # the text's reading: B matched WHOLE on the stretch's own text
        txt = None
        for i in range(0, 3):
            for e in range(i, 3):
                s = "12"
                if _re.fullmatch(r"\d", s[i:e]) and _re.fullmatch(B, s[i:e]):
                    txt = txt or (s[i:e], i)
        print("B=%-10s on '12' SEARCHED: engine A&B %s ; engine A&(0:B) %s ; engine A&!B %s ; text (B whole on stretch) A&B %s" % (
            B, aS(x, "12"), aS(z, "12"), aS(dd, "12"), txt))
    print("A&B vs A&(0:B), B=/\\d$/, over DSP:", cmp(strip(eng(lambda: AND(A(), Pat(r"\d$")))), strip(eng(lambda: ZERO(A(), Pat(r"\d$")))), DSP))
# V19 construction with B = \d$ : (*napla:A(?<T>...))B(?=\k<T>\z)
REST, TIE = r"(?<T>[\s\S]*+)", r"(?=\k<T>\z)"
m19 = pc(r'(*napla:\d' + REST + r')\d$' + TIE, {}, ())
print("V19-construction model of A & /\\d$/ on '12' SEARCHED:", m19("SEARCHED", "12"))
EAT = r"(?:(?!\k<T>\z)[\s\S])*+"
m11 = pc(r'(*napla:\d' + REST + r')(?!\d$\k<T>\z)' + EAT, {}, ())
print("V11-construction model of A & !/\\d$/ on '12' SEARCHED:", m11("SEARCHED", "12"))
# MODECLOSURE-7: 0: as PCRE group 0 inside occurrences
def z0(c):  # B = /1\d*/ whole on start_match..pos
    return _re.fullmatch(r"1\d*", c.subject[c.start:c.pos]) is not None
g0 = P.Pcre(r'(?:[\s\S]*?\d+(?C"z"))+[\s\S]*', {"z": z0})
with rules("24"):
    oc = OCC(AND(Pat(r"\d+"), Pat(r"1\d*")), 1)
    print("MC-7 on ' 1': engine occurrences(/\\d+/ & /1\\d*/) WHOLE", aW(oc, " 1"), "; group-0 reading WHOLE", g0.whole(" 1"))
