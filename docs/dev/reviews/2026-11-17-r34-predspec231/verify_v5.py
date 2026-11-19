import re, itertools
# L30 edge on a repeated label: /(?:(?<h>\d)?;)*/, texts over {3,7,;} to length 5; pass rows = the loop's iterations
REP = re.compile(r"(?:(\d)?;)*")
PASS = re.compile(r"(\d)?;")
pool = [""] + ["".join(t) for n in range(1, 6) for t in itertools.product("37;", repeat=n)]
assert len(pool) == 364
def kand(xs):
    if any(x is False for x in xs): return False
    if any(x is None for x in xs): return None
    return True
def knot(x): return None if x is None else (not x)
def passes(st):
    ps = [m.group(1) for m in PASS.finditer(st)]
    return ps if ps else [None]           # zero passes: one null pass row (R.1.2 / R.1.5)
def not_lt0(st): return knot(kand([None if h is None else False for h in passes(st)]))   # NOT (h: <0)
def set_not_lt0(st): return kand([None if h is None else True for h in passes(st)])      # (h: !<0)
def whole(c, s): return REP.fullmatch(s) is not None and c(s) is True
def searched(c, s):
    for i in range(len(s) + 1):
        m = REP.match(s, i)
        ends = [m.end()] + [j for j in range(len(s), i - 1, -1) if j != m.end() and REP.fullmatch(s[i:j])]
        for j in ends:
            if c(s[i:j]) is True: return (i, j)
    return None
dw = [s for s in pool if whole(not_lt0, s) != whole(set_not_lt0, s)]
ds = [s for s in pool if (searched(not_lt0, s) is None) != (searched(set_not_lt0, s) is None)]
k = lambda x: (len(x), x)
print("L30 REP edge NOT (h: <0) vs (h: !<0): WHOLE differ", len(dw), "first", min(dw, key=k) if dw else None,
      "| SEARCHED holds differ", len(ds))
print("on '3;;': NOT", not_lt0("3;;"), "set", set_not_lt0("3;;"))
