import sys, itertools; sys.path.insert(0, sys.argv[1])
from sim import *
P = PCRE(r"(?<k>\d)(?:;(?<h>\d))*")
subs = [str(k) + "".join(";" + str(h) for h in hs) for k in range(10) for n in range(3) for hs in itertools.product(range(10), repeat=n)]
def split(s):
    assert P.whole(s, ["k"]) is not None
    p = s.split(";"); return p[0], p[1:]
R = Dict(">=", (5, 3), "DOM")
def joint(s):
    k, hs = split(s)
    if not hs: return holds_tuple(R, (EMPTY, k), "product-by-spelling", [str(i) for i in range(10)])
    return all(R.has((h, k)) for h in hs)
def expansion(s):   # LEVEL / item 7: "the union is §4.1's | of records": (h: >5) | (h: 5, k: >=3), each record by the sequence rule
    k, hs = split(s)
    a1 = all(int(h) > 5 for h in hs)
    a2 = all(h == "5" for h in hs) and int(k) >= 3
    return a1 or a2
d = [s for s in subs if joint(s) != expansion(s)]
print("joint vs |-of-records: subjects", len(subs), "differ", len(d), "zero-pass differ", sum(1 for s in d if ";" not in s), "e.g.", d[:4])
# k = 3, two outside labels a, b, one looped h; non-product R = (1, 1, 0) | (2, 2, 0)
P3 = PCRE(r"(?<a>\d)(?<b>\d)(?:;(?<h>\d))*")
R3 = Union(Product(lit("1"), lit("1"), lit("0")), Product(lit("2"), lit("2"), lit("0")))
c = P3.whole("12", ["a", "b", "h"])
joint3 = holds_tuple(R3, (c["a"], c["b"], EMPTY), "x", [str(i) for i in range(10)])
sep3 = any(R3.has((c["a"], x, y)) for x in map(str, range(10)) for y in map(str, range(10))) and \
       any(R3.has((x, c["b"], y)) for x in map(str, range(10)) for y in map(str, range(10)))
hand = any(p.parts[0].has(c["a"]) and p.parts[1].has(c["b"]) for p in R3.xs)
print("k=3 `12` zero passes: joint projection", joint3, "| each outside label separately", sep3, "| hand |-of-records", hand)
