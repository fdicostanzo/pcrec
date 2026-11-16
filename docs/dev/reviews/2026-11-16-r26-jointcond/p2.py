import sys; sys.path.insert(0, sys.argv[1])
from sim import *
# nested: c outside, h outer item, k inner loop
PAT = r"(?<c>\d)(?:;(?<h>\d)(?::(?<k>\d))*)*"
P = PCRE(PAT)
def passes(s):
    # own construction: c, then outer items split on ';', inner on ':'
    assert P.whole(s, ["c"]) is not None
    c, rest = s[0], s[1:]
    outer = rest.split(";")[1:] if rest else []
    return c, [(it[0], it[1:].split(":")[1:]) for it in outer]
def tuples(s, names, reading_never_reached_inner):
    """yield the tuples per J7 + lane's pairing statement (deepest loop enclosing a named label)."""
    c, outer = passes(s)
    looped_inner = "k" in names
    looped_outer = "h" in names
    out = []
    if looped_inner:
        if not outer:   # outer loop ran zero passes: the inner loop is never reached
            if reading_never_reached_inner == "unset":
                out.append({"c": c, "h": EMPTY if looped_outer else None, "k": None})
            else:
                out.append({"c": c, "h": EMPTY, "k": EMPTY})
        for h, ks in outer:
            if not ks: out.append({"c": c, "h": h, "k": EMPTY})
            for k in ks: out.append({"c": c, "h": h, "k": k})
    elif looped_outer:
        if not outer: out.append({"c": c, "h": EMPTY})
        for h, ks in outer: out.append({"c": c, "h": h})
    return out
def evaluate(s, names, defaults, Rset, nr):
    for tp in tuples(s, names, nr):
        t = []
        for n in names:
            v = tp[n]
            if v is None:
                if n in defaults: v = defaults[n]
                else: return False          # J6: unset label fails
            t.append(v)
        if not holds_tuple(Rset, tuple(t), "product-by-spelling"):
            return False
    return True
T37 = Arity1(lambda s: s in "34567" and len(s) == 1, "3..7")
lt5 = cmpset("<", 5)
R = Product(T37, lt5)
for s in ["5", "5;9", "5;2:1", "9"]:
    for nr in ("zero(§4.2)", "unset(§4B.1 literal)"):
        a = evaluate(s, ["c", "k"], {}, R, nr.split("(")[0])
        b = evaluate(s, ["c", "k"], {"k": "9"}, R, nr.split("(")[0])
        print(f"{s!r:8} {nr:22} (c: 3..7, k: <5) -> {a};  (c: 3..7, k = 9: <5) -> {b}")
