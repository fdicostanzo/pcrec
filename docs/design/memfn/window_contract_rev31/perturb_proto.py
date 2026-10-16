# wcfix X1: a PROTOTYPE of the perturbation check, run on today's binary.
# For every corpus pattern (emit_sweep's argv stream) and every arm, compile
# twice under the SAME analysis name and stop (`-I DIR --analysis default`):
#   base = a verbatim copy of the store's default.rxt (whole-file identical to
#          a bare compile: the null control, checked per artifact here too)
#   pert = the same file with the byte-rate PERTURBED: the 256 freq rows'
#          values reversed by rank (rarest <-> commonest), plus one cpfreq
#          block serving utf8 (so under -e utf8 pcrec's prior-none becomes a
#          table: data added, not perturbed).
# Verdict per artifact, reading ONLY emitted bytes and the stamp text (never
# the consumption record, never a trace, never the kit's report):
#   FAIL-moved   the bytes outside the two stamp lines differ while the base
#                stamp omits byte-rate
#   FAIL-refusal one side refuses and the other compiles while the base stamp
#                omits byte-rate (or base refuses)
#   FAIL-stamp   base stamp omits byte-rate and pert's lists it
#   NULL-BAD     base differs from a bare compile anywhere (the null control)
#   ok-consulted-moved / -same, ok-quiet   the legal cells; -moved is the
#                check's POWER (what a dropped stamp item would turn red)
# usage: python3 -I perturb_proto.py TREE PCREC SCRATCH [JOBS]  (LIMIT= env)
import sys, os, re, collections
from concurrent.futures import ThreadPoolExecutor
tree, pcrec, scr = sys.argv[1], sys.argv[2], sys.argv[3]
jobs = int(sys.argv[4]) if len(sys.argv) > 4 else 6
sys.path.insert(0, tree + "/scripts")
import emit_sweep as es
B, Pd = scr + "/base", scr + "/pert"
os.makedirs(B, exist_ok=True); os.makedirs(Pd, exist_ok=True)
src = open(tree + "/src/findings/default.rxt").read()
open(B + "/default.rxt", "w").write(src)
lines = src.split("\n")
rows = [(i, l) for i, l in enumerate(lines) if re.match(r"\s+row [0-9a-f]{2} \d+$", l)]
vals = sorted(int(l.split()[2]) for _, l in rows)
for (i, l), v in zip(sorted(rows, key=lambda r: int(r[1].split()[2])), reversed(vals)):
    lines[i] = l[:len(l) - len(l.lstrip())] + "row %s %d" % (l.split()[1], v)
pert = "\n".join(lines).rstrip("\n") + """
    cpfreq
        question q
        reader r
        analyzer authored
        encoding utf8
        serves byte-rate when utf8 via encode-utf8
        row U+0061 50
        row U+0078 1
        row U+00E9 30
        row U+4E2D 20
        provenance
            source authored
            retrieved 2026-10-16
"""
open(Pd + "/default.rxt", "w").write(pert)
arms = [("default", []), ("noreqbyte", ["-fno-req-byte"]),
        ("noreq-pf", ["-fno-req-byte", "-fno-req-run", "-fno-prefilter"]),
        ("noreq-vm", ["--engine=vm", "-fno-req-byte", "-fno-req-run"])]
arms = [(n + "/" + e, (["-e", "utf8"] if e == "utf8" else []) + a)
        for n, a in arms for e in ("byte", "utf8")]
pats = es.enumerate_corpus(pcrec, tree, 60)
if os.environ.get("LIMIT"): pats = pats[:int(os.environ["LIMIT"])]
ST = re.compile(rb'^#define RX_FINDINGS "(.*)"$', re.M)
MASK = re.compile(rb'^(#define RX_FINDINGS .*|    \.findings = .*)$', re.M)
def one(item):
    arm, extra, (f, k, p) = item
    okn, on, _ = es.compile_stream_c(pcrec, p, 60, extra=extra)
    okb, ob, _ = es.compile_stream_c(pcrec, p, 60, extra=extra + ["-I", B, "--analysis", "default"])
    okp, op, _ = es.compile_stream_c(pcrec, p, 60, extra=extra + ["-I", Pd, "--analysis", "default"])
    if okn != okb or (okn and on != ob): return (arm, "NULL-BAD", f, p)
    sb = ST.findall(ob)[0] if okb else None
    quiet = okb and sb == b""
    if not okb: return (arm, "refused-both" if not okp else "FAIL-refusal", f, p)
    if not okp: return (arm, "FAIL-refusal" if quiet else "ok-consulted-refusal", f, p)
    if not quiet:   # POWER: a consulted artifact the perturbation moves is one
                    # an unreported read (a dropped stamp item) would turn red
        same = MASK.sub(b"", ob) == MASK.sub(b"", op)
        return (arm, "ok-consulted-same" if same else "ok-consulted-moved", f, p)
    if ST.findall(op)[0] != b"": return (arm, "FAIL-stamp", f, p)
    if MASK.sub(b"", ob) != MASK.sub(b"", op): return (arm, "FAIL-moved", f, p)
    return (arm, "ok-quiet", f, p)
items = [(a, e, x) for a, e in arms for x in pats]
c = collections.Counter(); fails = []
with ThreadPoolExecutor(jobs) as ex:
    for arm, v, f, p in ex.map(one, items):
        c[(arm, v)] += 1
        if v.startswith(("FAIL", "NULL")): fails.append((arm, v, f, p))
print("patterns", len(pats))
for (a, v), n in sorted(c.items()): print(a, v, n, sep="\t")
for x in fails: print("#", *x, sep="\t")
