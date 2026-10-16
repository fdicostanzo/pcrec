# wcrev3: count today's <PREFIX>_FINDINGS stamp values over the corpus argv stream
import sys, os, re, collections, subprocess
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, sys.argv[1] + "/scripts")
import emit_sweep as es
tree, pcrec = sys.argv[1], sys.argv[2]
pats = es.enumerate_corpus(pcrec, tree, 60)
arms = [("noreqbyte", ["-fno-req-byte"]), ("noreqbyte-run", ["-fno-req-byte","-fno-req-run"]), ("noreq-pf", ["-fno-req-byte","-fno-req-run","-fno-prefilter"]), ("noreq-pf-utf8", ["-e","utf8","-fno-req-byte","-fno-req-run","-fno-prefilter"]), ("noreq-vm", ["--engine=vm","-fno-req-byte","-fno-req-run"])]
RE = re.compile(rb'^#define RX_FINDINGS "(.*)"$', re.M)
def one(item):
    arm, extra, (f, k, p) = item
    ok, out, _ = es.compile_stream_c(pcrec, p, 60, extra=extra)
    if not ok: return (arm, "REFUSED")
    m = RE.findall(out)
    if len(m) != 1: return (arm, "NSTAMP=%d" % len(m))
    v = m[0].decode()
    return (arm, "EMPTY" if v == "" else ("none" if v.endswith("=none") else v.split(":")[0]))
items = [(a, e, x) for a, e in arms for x in pats]
c = collections.Counter()
with ThreadPoolExecutor(14) as ex:
    for r in ex.map(one, items): c[r] += 1
print("patterns", len(pats))
for (a, v), n in sorted(c.items()): print(a, v, n, sep="\t")
