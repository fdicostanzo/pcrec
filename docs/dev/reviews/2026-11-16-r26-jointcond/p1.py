import sys; sys.path.insert(0, sys.argv[1])
from sim import *
t = PCRE(r"(?<h>\d{1,2}):(?<m>\d\d)")
H = [str(i) for i in range(10)] + ["%02d" % i for i in range(100)]
subs = [f"{h}:{m:02d}" for h in H for m in range(100)]
def run(mk, label):
    res = {}
    for rd in ("EXP", "DOM"):
        Rs = mk(rd); n = 0; acc = set()
        for s in subs:
            c = t.whole(s, ["h", "m"]); assert c
            if Rs.has((c["h"], c["m"])): acc.add(s)
        res[rd] = acc
    d = res["EXP"] ^ res["DOM"]
    print(f"{label}: EXP {len(res['EXP'])}, DOM {len(res['DOM'])}, differ {len(d)} e.g. {sorted(d)[:3]}")
    return res
run(lambda r: Dict(">=", (9, 0), r), ">= (9, 0) unpadded")
run(lambda r: between((9, 0), (17, 0), r), "between((9,0),(17,0)) unpadded")
run(lambda r: Dict(">", (9, 30), r), "> (9, 30) unpadded")
run(lambda r: padded(Dict(">=", (9, 0), r)), "padded(>= (9, 0))")
# table (O): >= (9,30) vs (>= 9, >= 30), both padded and unpadded, both readings
for pad in (False, True):
    for rd in ("EXP", "DOM"):
        A = Dict(">=", (9, 30), rd, pad)
        B = Product(cmpset(">=", 9), cmpset(">=", 30))
        if pad: B = padded(B)
        n = sum(1 for s in subs for c in [t.whole(s, ["h","m"])] if A.has((c["h"], c["m"])) != B.has((c["h"], c["m"])))
        print(f"(O) pad={pad} {rd}: differ {n} of {len(subs)}")
# non-numeric component
w = PCRE(r"(?<h>\d{1,2}):(?<m>\w\w)")
for s in ["10:ab", "9:ab", "ab:30"]:
    c = w.whole(s, ["h", "m"])
    if c is None: print(s, "not in pattern"); continue
    print(s, {rd: Dict(">=", (9, 0), rd).has((c["h"], c["m"])) for rd in ("EXP", "DOM")})
# default with a non-canonical text: ((h, m = 00): >= (9, 0)) on t2 subject `10`
t2 = PCRE(r"(?<h>\d{1,2})(?::(?<m>\d\d))?")
c = t2.whole("10", ["h", "m"]); print("t2 `10` caps", c)
for rd in ("EXP", "DOM"):
    print("((h, m = 00): >= (9, 0)) on `10`", rd, Dict(">=", (9, 0), rd).has((c["h"], "00")))
