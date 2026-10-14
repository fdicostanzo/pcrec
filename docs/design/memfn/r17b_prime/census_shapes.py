# r17bp: how many R17-b movers would R0 (>= 2 RANGE terms in the cover) return
# to the walk, and how many stateful FIND sites per artifact. Compile-only.
import re, sys, subprocess
from concurrent.futures import ThreadPoolExecutor
W = sys.argv[1]; sys.path.insert(0, W + "/scripts")
import emit_sweep as es
PC = W + "/build/pcrec"
pats = es.distinct_patterns(es.enumerate_corpus(PC, W, 30), every=1)
pats = [(p[2] if isinstance(p, tuple) else p) for p in pats]
ARMS = [("byte", []), ("byte-vm", ["--engine=vm"])]
MASK = re.compile(rb"static inline unsigned long long (\w+)__mask\(const unsigned char \*p\)\n\{\n    pcrec_mfk_w8_vector v = pcrec_mfk_w8_load_vector\(p\);\n    return (.*);\n\}")
def task(item):
    p, (arm, extra) = item
    try:
        r = subprocess.run([PC, "-p", "rx", "--features", "all"] + extra + ["-o", "-", "--pattern", p], capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        return (arm, p, None)
    if r.returncode: return (arm, p, None)
    sites = []
    for m in MASK.finditer(r.stdout):
        e = m.group(2)
        sites.append((m.group(1).decode(), e.count(b"_range("), e.count(b"_eq("), e.count(b"_cube(")))
    return (arm, p, sites)
items = [(p, a) for p in pats for a in ARMS]
with ThreadPoolExecutor(8) as ex: res = list(ex.map(task, items))
from collections import Counter
for arm, _ in ARMS:
    rs = [x for x in res if x[0] == arm and x[2] is not None]
    movers = [x for x in rs if x[2]]
    nsites = Counter(len(x[2]) for x in movers)
    shapes = Counter((s[1], s[2], s[3]) for x in movers for s in x[2])
    r0 = sum(1 for x in movers if all(s[1] >= 2 for s in x[2]))
    r0any = sum(1 for x in movers if any(s[1] >= 2 for s in x[2]))
    print(f"ARM {arm}: compiled {len(rs)} movers {len(movers)}  sites/artifact {dict(nsites)}")
    print(f"   R0 (every site >=2 RANGE): {r0}; any site >=2 RANGE: {r0any}")
    print("   shapes (range,eq,cube):count", dict(sorted(shapes.items(), key=lambda kv: -kv[1])))
