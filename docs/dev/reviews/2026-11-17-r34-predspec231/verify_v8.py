import re, itertools
# (h: <5) vs NOT some(NOT (h: <5)) on /(?:(?<h>\d)?;)*/ over 364 texts; pass rows = the loop's iterations
REP = re.compile(r"(?:(\d)?;)*")
PASS = re.compile(r"(\d)?;")
pool = [""] + ["".join(t) for n in range(1, 6) for t in itertools.product("37;", repeat=n)]
assert len(pool) == 364
def kand(xs):
    if any(x is False for x in xs): return False
    if any(x is None for x in xs): return None
    return True
def kor(xs):
    if any(x is True for x in xs): return True
    if any(x is None for x in xs): return None
    return False
def knot(x): return None if x is None else (not x)
def real(st): return [m.group(1) for m in PASS.finditer(st)]
def rows(st): return real(st) or [None]            # zero passes: one null pass row (R.1.2)
def c1(h): return None if h is None else int(h) < 5
def plain(st): return kand([c1(h) for h in rows(st)])                                   # pass-and
def dm_exists(st): return knot(any(knot(c1(h)) is True for h in real(st)))              # group-truth: EXISTS over REAL passes
def dm_kleene(st): return knot(kor([knot(c1(h)) for h in rows(st)]))                    # Kleene `some` over the same pass rows
def whole(c, s): return REP.fullmatch(s) is not None and c(s) is True
def searched(c, s):
    for i in range(len(s) + 1):
        m = REP.match(s, i)
        ends = [m.end()] + [j for j in range(len(s), i - 1, -1) if j != m.end() and REP.fullmatch(s[i:j])]
        for j in ends:
            if c(s[i:j]) is True: return (i, j)
    return None
k = lambda x: (len(x), x)
for nm, c in [("EXISTS (draft)", dm_exists), ("Kleene some", dm_kleene)]:
    dw = [s for s in pool if whole(plain, s) != whole(c, s)]
    ds = [s for s in pool if (searched(plain, s) is None) != (searched(c, s) is None)]
    dr = [s for s in pool if searched(plain, s) != searched(c, s)]
    print("(h: <5) vs NOT some(NOT (h: <5)) [%s]: WHOLE differ %d first %r | SEARCHED holds differ %d | reported row differ %d first %r"
          % (nm, len(dw), min(dw, key=k) if dw else None, len(ds), len(dr), min(dr, key=k) if dr else None))
for s in ["", "3;;", "7;;"]:
    print(repr(s), "plain", whole(plain, s), searched(plain, s), "| EXISTS", whole(dm_exists, s), searched(dm_exists, s))
