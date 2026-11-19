import sys, itertools
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/simulate/wk")
sys.path.insert(1, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/rxmodel_evidence")
from ev import M, run, num
import pcre2h

def fmt(mk, r, labs):
    if r is None: return "FAILS"
    if isinstance(r, tuple):
        i, st = r; return "`%s`@%d %s" % (mk.txt[i:st.pos], i, " ".join("%s=%s" % (n, mk.lab(st, n)) for n in labs))
    return "HOLDS " + " ".join("%s=%s" % (n, mk.lab(r, n)) for n in labs)
def show(name, pat, cond, texts, labs):
    mk = M(pat)
    tw, ts, tf = texts
    w = run(mk, cond, tw)[0]; a = fmt(mk, w, labs)
    s = run(mk, cond, ts)[1]; b = fmt(mk, s, labs)
    f = run(mk, cond, tf)[2]; c = "[" + ", ".join(fmt(mk, x, labs) for x in f) + "]"
    print("%s | WHOLE %s: %s | SEARCHED %s: %s | FIND-ALL %s: %s" % (name, tw, a, ts, b, tf, c))

def L(n, f): return lambda mk, st: f(mk.lab(st, n))
lt5 = lambda v: num(v) and int(v) < 5

# R.1.7 table 1
P1 = r"(?:(?<a>\d)|(?<b>[a-z]))*xx"
for t in ("3qxx", "q3xx", "7q3xx"):
    show("S1 " + t, P1, L("a", lt5), (t, "3qxx", "3qxx q3xx 7q3xx"), ("a",))
CLOSE = r"(?:(?<h>\d+)(?::(?<m>\d\d))?,)*"
def J(eq, dm=None, canon=True):
    def f(mk, st):
        h, m = mk.lab(st, "h"), mk.lab(st, "m")
        if m is None and dm is not None: m = dm
        if h is None or m is None: return False
        if canon: return num(h) and num(m) and (int(h), int(m)) == eq
        return (h, m) == tuple(str(x) for x in eq)
    return f
for t in ("9:45,10,", "10,9:45,", "10:45,10,"):
    show("S2 " + t, CLOSE, J((10, 45)), (t, "10,9:45, 10:45,", "9:45,10, 10:45, 10,9:45,"), ("h", "m"))
    show("S3 " + t, CLOSE, J((10, 45), "00"), (t, t, t), ("h", "m"))
    show("S4canon " + t, CLOSE, J((10, 0), "00"), (t, t, t), ("h", "m"))
    show("S4str " + t, CLOSE, lambda mk, st: (mk.lab(st, "h"), mk.lab(st, "m") or "00") == ("10", "00"), (t, t, t), ("h", "m"))
# L1, R13;;
show("L1", r"(?:(?<h>\d);)*", L("h", lt5), ("7;3;", "7;3;", "7;3; 3;7;"), ("h",))
REP = r"(?:(?<h>\d)?;)*"
show("R13;;", REP, L("h", lt5), ("3;;", "3;;", "3;7; 7;; 3;"), ("h",))
show("R23;;", REP, lambda mk, st: not lt5(mk.lab(st, "h")), ("3;;", "3;;", "3;7; 7;; 3;"), ("h",))
show("R37;;", REP, lambda mk, st: (lambda v: v is not None and not lt5(v))(mk.lab(st, "h")), ("7;;", "7;;", "3;7; 7;; 3;"), ("h",))
# item inside body: /(?:(?<h>\d)?;(?C"c"))+/
show("INSIDE item", r'(?:(?<h>\d)?;(?C"c"))+', None or (lambda mk, st: True), ("3;;", "3;;", "3;;"), ("h",)) if False else None
mk = M(r'(?:(?<h>\d)?;(?C"c"))+', {"c": lambda mk, st: lt5(mk.lab(st, "h"))})
print("INSIDE item 3;;", fmt(mk, run(mk, lambda m_, s_: True, "3;;")[0], ("h",)))
# NESTED
NEST = r"(?:(?:(?<h>\d)?;)*,)*"
for t in ("3;,,", "3;;,", "3;,7;,", "7;,3;,"):
    show("NEST " + t, NEST, L("h", lt5), (t, "3;,, 7;,", "3;,, 3;;, 3;,7;,"), ("h",))
mk = M(r'(?:(?:(?<h>\d)?;(?C"c"))*,)*', {"c": lambda mk, st: lt5(mk.lab(st, "h"))})
for t in ():
    show("NEST(i) " + t, r'(?:(?:(?<h>\d)?;(?C"c"))*,)*', lambda m_, s_: True, (t, "3;,, 7;,", t), ("h",)) if False else None
def showm(name, mk, cond, texts, labs):
    tw, ts = texts
    w = run(mk, cond, tw)[0]; a = fmt(mk, w, labs)
    s = run(mk, cond, ts)[1]; b = fmt(mk, s, labs)
    print("%s | WHOLE %s: %s | SEARCHED %s: %s" % (name, tw, a, ts, b))
T = lambda mk, st: True
for t in ("3;,,", "3;;,", "3;,7;,", "7;,3;,"):
    showm("NEST(i) " + t, M(r'(?:(?:(?<h>\d)?;(?C"c"))*,)*', {"c": lambda mk, st: lt5(mk.lab(st, "h"))}), T, (t, "3;,, 7;,"), ("h",))
    showm("NEST(ii) " + t, M(r'(?:(?:(?<h>\d)?;)*(?C"c"),)*', {"c": lambda mk, st: lt5(mk.lab(st, "h"))}), T, (t, "3;,, 7;,"), ("h",))
# PART L
PL = r"(?:(?<h>\d+)(?::(?<m>\d\d))?,)*\k<m>"
for t in ("9:45,10,45", "9:45,10:45,45"):
    mk = M(PL)
    print("PART L plain", t, "WHOLE", run(mk, lambda m_, s_: True, t)[0] is not None,
          "| & (m: \"45\")", fmt(mk, run(mk, lambda m_, s_: m_.lab(s_, "m") == "45", t)[0], ("h", "m")),
          "| libpcre2 plain WHOLE", pcre2h.Pcre(PL).whole(t))
# occurrences EXPORTED: occurrences(/(?<x>(?<g>a)?b)/, min = 1) model /(?:.*?(rx))+.*/ ... one-pattern lazy gap
OCC = r"(?:[\s\S]*?(?<x>(?<g>a)?b))+[\s\S]*"
show("OCC", OCC.replace(r"[\s\S]", "."), L("g", lambda v: v == "a"), ("abb", "babb", "abb ab"), ("x", "g"))
# hits-committed optional label: occurrences(/a(?<g>x)?/) & (g: "x") on axa
show("OCC2", r"(?:.*?a(?<g>x)?)*.*", L("g", lambda v: v == "x"), ("axa", "axa", "axa"), ("g",))
