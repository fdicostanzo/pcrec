# wcfix (window_contract rev 3.1, panel r4 B1): count today's <PREFIX>_FINDINGS
# outcome over emit_sweep's corpus argv stream, crossed by the ANALYSIS axis
# (none / weblog / log / an -I user bundle / an underivable `l1none`-shaped
# bundle) and by every deny arm where `""` exists today. The population that
# matters to B1 is the compiles that SUCCEED today with `""` under an
# underivable bundle: each one refuses when asked, so an offer that raised on
# every attempt would refuse it.
#
# usage: python3 -I analysiscount.py TREE PCREC SCRATCH [JOBS]
import sys, os, re, collections
from concurrent.futures import ThreadPoolExecutor
tree, pcrec, scr = sys.argv[1], sys.argv[2], sys.argv[3]
jobs = int(sys.argv[4]) if len(sys.argv) > 4 else 6
sys.path.insert(0, tree + "/scripts")
import emit_sweep as es

os.makedirs(scr + "/I", exist_ok=True)
# l1none: tests/findings/run_findings_tests.sh's own fixture, verbatim.
open(scr + "/I/l1none.rxt", "w").write("""analysis l1none
    cpfreq
        question q
        reader r
        analyzer authored
        encoding utf8
        serves byte-rate when utf8 via encode-latin1
        row U+20AC 7
        provenance
            source authored
            retrieved 2026-09-28
""")
# mine: a measured-shaped user freq bundle (byte), answering at link 0 (stop -I).
open(scr + "/I/mine.rxt", "w").write("""analysis mine
    freq
        question q
        reader r
        analyzer authored
        encoding bytes
        serves byte-rate when byte via unigram
        row 61 50
        row 62 30
        row 63 20
        provenance
            source exemplar-x
            retrieved 2026-10-16
            bytes 100
            sha256 0000000000000000000000000000000000000000000000000000000000000000
""")
I = ["-I", scr + "/I"]
cells = [("none", []), ("weblog", ["--analysis", "weblog"]), ("log", ["--analysis", "log"]),
         ("mine-I", I + ["--analysis", "mine"])]
deny = [("noreqbyte", ["-fno-req-byte"]),
        ("noreq-pf", ["-fno-req-byte", "-fno-req-run", "-fno-prefilter"]),
        ("noreq-vm", ["--engine=vm", "-fno-req-byte", "-fno-req-run"])]
arms = []
for dn, d in deny:
    for cn, c in cells:
        arms.append((dn + "/byte/" + cn, d + c))
    for cn, c in cells[:3] + [("l1none-I", I + ["--analysis", "l1none"])]:
        arms.append((dn + "/utf8/" + cn, ["-e", "utf8"] + d + c))
# the default arms under l1none: every compile asks, so every one refuses
arms.append(("default/utf8/l1none-I", ["-e", "utf8"] + I + ["--analysis", "l1none"]))
arms.append(("vm/utf8/l1none-I", ["-e", "utf8", "--engine=vm"] + I + ["--analysis", "l1none"]))

pats = es.enumerate_corpus(pcrec, tree, 60)
if os.environ.get("LIMIT"): pats = pats[:int(os.environ["LIMIT"])]
RE = re.compile(rb'^#define RX_FINDINGS "(.*)"$', re.M)
def one(item):
    arm, extra, (f, k, p) = item
    ok, out, err = es.compile_stream_c(pcrec, p, 60, extra=extra, want_err=True)
    if not ok:
        e = err.decode("utf-8", "replace") if isinstance(err, bytes) else (err or "")
        return (arm, "REFUSED-underivable" if "counts nothing via" in e else "REFUSED-other")
    m = RE.findall(out)
    if len(m) != 1: return (arm, "NSTAMP=%d" % len(m))
    v = m[0].decode()
    return (arm, '""' if v == "" else ("none" if v.endswith("=none") else v.split(":")[0]))
items = [(a, e, x) for a, e in arms for x in pats]
c = collections.Counter()
with ThreadPoolExecutor(jobs) as ex:
    for r in ex.map(one, items): c[r] += 1
print("patterns", len(pats))
for (a, v), n in sorted(c.items()): print(a, v, n, sep="\t")
