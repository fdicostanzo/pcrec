"""[COVER-CAP] stage 1 (lane covs1): the mover PREDICTION (cover_cap.md §5.2)
against the emit sweep's OBSERVED movers, plus the decision census.

Over the sweep's own population (every corpus pattern, `enumerate_corpus`),
both encodings, the BASELINE trace build and the CANDIDATE trace build each
record the cover decision (`PCREC_KIT_PROOF_TRACE=1`, the compile's own last
KITPROOF record of role `-`); the baseline listing's `width` fact gives wmin.

  predicted(P) = some encoding's BASELINE why is exact/producer-short or
                 exact/producer-unstated, or fixed-width with wmin <= 32
  LOST(P)      = some encoding's baseline why is `cover` and the candidate's
                 is not (cover_cap.md: 0 current covers lost)
  UNEXPLAINED  = a sweep mover (any artifact stream) whose pattern is not
                 predicted (G2: predicted must contain observed)

Every predicted-but-unmoved pattern is listed with the candidate's why. The
decision census (baseline why -> candidate why, both encodings) and the
candidate's C4 `erased`/`island` counts are printed over the whole
population (K35). Exit 0 iff LOST = 0 and UNEXPLAINED = 0.

usage: python3 -I predict.py TREE REF_PCREC REF_TRACE NEW_TRACE MOVERS.tsv OUT.tsv [-j N]
"""
import collections, concurrent.futures, os, subprocess, sys

TREE, REF_BIN, REF_TRACE, NEW_TRACE, MOVERS, OUT = sys.argv[1:7]
J = int(sys.argv[sys.argv.index("-j") + 1]) if "-j" in sys.argv else 8
sys.path.insert(0, os.path.join(TREE, "scripts"))
import emit_sweep as es  # noqa: E402

ENCS = (("byte", []), ("utf8", ["-e", "utf8"]))


def run(argv, env=None):
    try:
        return subprocess.run(argv, capture_output=True, env=env, timeout=120)
    except subprocess.TimeoutExpired:
        return None


def decision(binary, pat, encargs):
    env = dict(os.environ, PCREC_KIT_PROOF_TRACE="1")
    p = run([binary, "--harness=kit-proof", "-p", "rx", "--features", "all"] + encargs +
            ["-o", "-", "--pattern", pat], env)
    if p is None:
        return "timeout"
    if p.returncode:
        return "rc!=0"
    own = None
    for ln in p.stderr.decode("latin-1").splitlines():
        f = ln.split("\t")
        if f[0] == "KITPROOF" and (len(f) < 5 or f[4] == "-"):
            own = f[1]
    return own or "not-asked"


def wmins(pat):
    p = run([REF_BIN, "--features", "all", "--emit-facts=byte,utf8", "--pattern", pat])
    out = {}
    if p is None or p.returncode:
        return out
    for ln in p.stdout.decode("latin-1").splitlines():
        f = ln.split("\t")
        if len(f) > 6 and f[1] == "width" and f[6].startswith("["):
            try:
                out[f[0]] = int(f[6][1:].split(",")[0])
            except ValueError:
                pass
    return out


def one(pat):
    wm = wmins(pat)
    rows = []
    for enc, ea in ENCS:
        rows.append((enc, decision(REF_TRACE, pat, ea), decision(NEW_TRACE, pat, ea), wm.get(enc)))
    return pat, rows


def main():
    newbin = os.path.join(TREE, "build", "pcrec")
    pop = es.enumerate_corpus(newbin, TREE, 60)
    pats = sorted({p for _, _, p in pop})
    print("population: %d corpus rows, %d distinct patterns" % (len(pop), len(pats)), flush=True)
    res = {}
    with concurrent.futures.ThreadPoolExecutor(J) as ex:
        for pat, rows in ex.map(one, pats, chunksize=8):
            res[pat] = rows
    pred, lost = set(), []
    census = collections.Counter()
    c4 = collections.Counter()
    for pat, rows in res.items():
        for enc, rw, nw, wmin in rows:
            census[(enc, rw, nw)] += 1
            if nw.startswith("anchored-A/"):
                c4[(enc, nw)] += 1
            if rw in ("exact/producer-short", "exact/producer-unstated") or \
               (rw.startswith("fixed-width") and wmin is not None and wmin <= 32):
                pred.add(pat)
            if rw == "cover" and nw != "cover":
                lost.append((pat, enc, rw, nw))
    # observed: the sweep's movers keyed f"{file}:{kind}:{pat[:60]!r}"
    bykey = collections.defaultdict(set)
    for f, k, p in pop:
        bykey["%s:%s:%r" % (f, k, p[:60])].add(p)
    observed = collections.defaultdict(set)   # pat -> streams
    unkeyed = []
    for ln in open(MOVERS):
        if ln.startswith("#") or not ln.strip():
            continue
        stream, cls, key = ln.rstrip("\n").split("\t", 2)
        if stream in ("dumps",):
            continue
        ps = bykey.get(key)
        if not ps:
            unkeyed.append((stream, cls, key))
            continue
        for p in ps:
            observed[p].add(stream)
    unexplained = sorted(p for p in observed if p not in pred)
    unmoved = sorted(p for p in pred if p not in observed)
    with open(OUT, "w") as fh:
        fh.write("#class\tpattern\tencoding\tbaseline_why\tcandidate_why\twmin\tstreams\n")
        for p in sorted(res):
            cls = ("LOST" if any(x[0] == p for x in lost) else
                   "UNEXPLAINED" if p in unexplained else
                   "predicted-moved" if p in pred and p in observed else
                   "predicted-unmoved" if p in pred else "-")
            for enc, rw, nw, wmin in res[p]:
                fh.write("%s\t%r\t%s\t%s\t%s\t%s\t%s\n" % (cls, p, enc, rw, nw, wmin,
                                                           ",".join(sorted(observed.get(p, ())))))
    print("## decision census (encoding, baseline why -> candidate why), K35 over %d patterns x 2" % len(res))
    for (enc, rw, nw), n in sorted(census.items(), key=lambda kv: (kv[0][0], -kv[1])):
        if rw != nw:
            print("moved\t%s\t%s -> %s\t%d" % (enc, rw, nw, n))
    print("unchanged decisions: %d" % sum(n for (e, a, b), n in census.items() if a == b))
    print("## C4 guards on the candidate: " + (", ".join("%s %s %d" % (k[0], k[1], v) for k, v in sorted(c4.items())) or "none"))
    print("predicted=%d observed=%d predicted-moved=%d predicted-unmoved=%d" % (
        len(pred), len(observed), len(pred & set(observed)), len(unmoved)))
    for p in unmoved:
        print("predicted-unmoved\t%r\t%s" % (p[:80], " ".join("%s:%s" % (r[0], r[2]) for r in res[p])))
    for p in unexplained:
        print("UNEXPLAINED\t%r\t%s\t%s" % (p[:80], ",".join(sorted(observed[p])),
                                          " ".join("%s:%s>%s" % (r[0], r[1], r[2]) for r in res[p])))
    for x in lost:
        print("LOST\t%r\t%s\t%s -> %s" % (x[0][:80], x[1], x[2], x[3]))
    for x in unkeyed[:20]:
        print("UNKEYED\t%s\t%s\t%s" % x)
    bad = bool(lost or unexplained or unkeyed)
    print("predict: lost=%d unexplained=%d unkeyed=%d" % (len(lost), len(unexplained), len(unkeyed)))
    print("predict: DONE rc=%d" % (1 if bad else 0))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
