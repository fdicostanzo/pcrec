#!/usr/bin/env python3
"""[SEL-SIZE] scratch census: auto-selected DFA artifacts by emitted size,
over corpus-as-written + pcrec-bench patterns (raw and (?:P)\\z), with the
forced-VM size for the large ones. Scratch only."""
import concurrent.futures, os, re, sys, json
sys.path.insert(0, os.path.join(os.environ.get("REPO", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))), "scripts"))
import emit_sweep as es, cls_identity as ci
TREE = os.environ.get("REPO", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
BIN = os.environ.get("PCREC", os.path.join(TREE, "build/pcrec"))
TO = 120
STAMP = re.compile(rb'#define RX_(ENGINE|ENGINE_SEL|DFA_SCAN|DFA_PREFILTER|VM_PREFILTER) "([^"]*)"')
def argv(pat, enc, feat, flags, eng):
    a = [BIN, "-p", "rx", "-e", enc]
    if feat: a += ["--features", feat]
    if "i" in flags: a.append("-i")
    if "u" in flags: a.append("--ucp")
    if eng: a.append("--engine=" + eng)
    return a + ["-o", "-", "--pattern", pat]
def comp(pat, enc, feat, flags, eng):
    rc, out, err = es.run(argv(pat, enc, feat, flags, eng), TO)
    if rc is None: return {"rc": "timeout"}
    if rc != 0: return {"rc": "refuse"}
    st = {k.decode(): v.decode() for k, v in STAMP.findall(out[:200000])}
    # stamps may sit late in a big file; search tail too
    if "ENGINE" not in st:
        st = {k.decode(): v.decode() for k, v in STAMP.findall(out)}
    return {"rc": "ok", "bytes": len(out), "warn": b"large artifact" in err,
            "n1": b"work budget" in err, **st}
rows = []
blocks = ci.corpus_blocks(BIN, TREE, TO)
seen = set()
for rel, pat, fl, ft, enc, eng in blocks:
    if eng: continue            # forced engine in corpus: no auto choice
    k = ("corpus", pat, enc or "byte", ft or "", ci.flag_tuple(fl))
    if k in seen: continue
    seen.add(k); rows.append(k)
for d in sorted(os.listdir(ci.BENCH_ROOT)):
    pd = os.path.join(ci.BENCH_ROOT, d, "patterns")
    if not os.path.isdir(pd): continue
    for fn in sorted(os.listdir(pd)):
        if not fn.endswith(".rx"): continue
        pat = open(os.path.join(pd, fn), "rb").read().rstrip(b"\n")
        for wrap in (pat, b"(?:" + pat + b")\\z"):
            for enc in ("byte", "utf8"):
                k = ("bench:%s/%s%s" % (d, fn, "" if wrap is pat else "\\z"), wrap, enc, "all", ())
                if k not in seen: seen.add(k); rows.append(k)
print("population", len(rows), file=sys.stderr)
def one(k):
    pop, pat, enc, ft, fl = k
    a = comp(pat, enc, ft, fl, "")
    r = {"pop": pop, "pat": pat.decode("utf-8", "surrogateescape")[:120], "enc": enc, "feat": ft, "flags": "".join(fl), "auto": a}
    if a.get("rc") == "ok" and a.get("ENGINE") == "dfa" and a["bytes"] >= 100000:
        r["vm"] = comp(pat, enc, ft, fl, "vm")
    if a.get("n1"):
        r["dfa"] = comp(pat, enc, ft, fl, "dfa")
        r["vm"] = comp(pat, enc, ft, fl, "vm")
    return r
with concurrent.futures.ThreadPoolExecutor(4) as ex:
    res = list(ex.map(one, rows))
json.dump(res, open(sys.argv[1], "w"), indent=0)
