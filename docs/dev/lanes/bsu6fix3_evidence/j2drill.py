#!/usr/bin/env python3
"""bsu6fix3: call cards.py's selftest_j2 directly. usage: j2drill.py CARDS [--plant-stale-stub]
--plant-stale-stub rewrites (in memory) the drill's prepare_cell stub back to 9986aca43's 3-argument lambda: must FAIL."""
import importlib.util, sys
CARDS = sys.argv[1]
plant = "--plant-stale-stub" in sys.argv[2:]
src = open(CARDS).read()
if plant:
    a = 'globals()["prepare_cell"] = lambda _rd, c, _n, _retime=0: list(c)'
    assert src.count(a) == 1, "plant site not found"
    src = src.replace(a, 'globals()["prepare_cell"] = lambda _rd, c, _n: list(c)')
spec = importlib.util.spec_from_file_location("cards", CARDS)
m = importlib.util.module_from_spec(spec)
sys.argv = ["x"]
exec(compile(src, CARDS, "exec"), m.__dict__)
bad = []


def check(name, ok, line):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, line))
    if not ok:
        bad.append(name)


m.selftest_j2(check)
print("j2drill%s: %d failed" % (" (planted stale stub)" if plant else "", len(bad)))
sys.exit(1 if bad else 0)
