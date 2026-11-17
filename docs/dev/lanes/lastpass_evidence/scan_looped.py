import re, sys, collections
import re._parser as SP
from re._constants import SUBPATTERN, MAX_REPEAT, MIN_REPEAT, POSSESSIVE_REPEAT, BRANCH, ASSERT, ASSERT_NOT, ATOMIC_GROUP
D = sys.argv[1]
lines = open(D).read().split("\n")
def looped(p):
    try: t = SP.parse(p.replace("(?<", "(?P<").replace("(?P<=", "(?<=").replace("(?P<!", "(?<!"))
    except Exception as e: return None
    names = {v: k for k, v in t.state.groupdict.items()}
    out = set()
    def walk(items, inrep):
        for op, av in items:
            if op == SUBPATTERN:
                gid, _, _, sub = av
                if gid in names and inrep: out.add(names[gid])
                walk(sub, inrep)
            elif op in (MAX_REPEAT, MIN_REPEAT, POSSESSIVE_REPEAT):
                lo, hi, sub = av
                walk(sub, inrep or hi > 1)
            elif op == BRANCH:
                for a in av[1]: walk(a, inrep)
            elif op in (ASSERT, ASSERT_NOT):
                walk(av[1], inrep)
            elif op == ATOMIC_GROUP:
                walk(av, inrep)
    walk(list(t), False)
    return out
hits = collections.defaultdict(list)
for n, l in enumerate(lines, 1):
    for m in re.finditer(r"/((?:[^/`\s]|\\/)*\(\?P?<[A-Za-z_]\w*>(?:[^/`\\]|\\.)*)/", l):
        p = m.group(1)
        lp = looped(p)
        if lp: hits[p].append(n)
for p, ns in sorted(hits.items(), key=lambda x: -len(x[1])):
    print(len(ns), repr(p), ns[:12], "..." if len(ns) > 12 else "")
