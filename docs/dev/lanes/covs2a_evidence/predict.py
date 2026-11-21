"""[COVER-CAP] stage 2 (lane covs2a; cover_cap.md §11.1 "The prediction", A6):
the mover PREDICTION against the emit sweep's OBSERVED movers, plus the
decision census. A COPY of lane covs1's docs/dev/lanes/covs1_evidence/predict.py
(which stays as committed) with three edits (A6): (1) the INTO predicate,
(2) the expected-OUT set beside the LOST rule, (3) both sides read from the
two `--emit-facts` listings' `cover` sections, not from trace builds.

Over the sweep's own population (every corpus pattern, `enumerate_corpus`),
both encodings, the BASELINE listing (REF_PCREC, main before stage 2) and the
CANDIDATE listing (TREE/build/pcrec) each give the cover decision's `why` and
`k` (the `cover` section, facts_listing.md §4.5: columns why, k). The
baseline's `statement-fits` and the candidate's `width-limit` are the same
conjunct C15 (renamed at stage 2, A4). D is the candidate's width default
(`--list-limits` PCREC_DEFAULT_WINDOW_SEARCH_WIDTH, read fail-loud; `--width D`
overrides it for a -D build).

  INTO(P)      = some encoding's BASELINE why is `statement-fits` and its k
                 <= D (an UPPER bound: C9-C14 never ran on it). At D = 32 the
                 set is empty by construction: stage 1 admits every k <= 32.
  OUT(P)       = some encoding's BASELINE why is `cover` with k > D (empty
                 while D >= 32): expected to move, to the candidate's
                 `width-limit`.
  LOST(P)      = some encoding's baseline why is `cover` and the candidate's
                 is not, outside OUT (0 current covers lost)
  UNEXPLAINED  = a sweep mover (any artifact stream) whose pattern is in
                 neither INTO nor OUT (G2: predicted must contain observed)

Every predicted-but-unmoved pattern is listed with the candidate's why. The
decision census (baseline why -> candidate why, both encodings) and the
candidate's C4 `erased`/`island` counts are printed over the whole
population (K35). Exit 0 iff LOST = 0 and UNEXPLAINED = 0.

NOT handled here (cover_cap.md §11.1, PER SWEEP VARIANT): a lowered-cap
variant's `size-cap-retry` artifacts; the listings are the default build's.

usage: python3 -I predict.py TREE REF_PCREC MOVERS.tsv OUT.tsv [--width D] [-j N]
"""
import collections, concurrent.futures, os, subprocess, sys

TREE, REF_BIN, MOVERS, OUT = sys.argv[1:5]
NEWBIN = os.path.join(TREE, "build", "pcrec")
J = int(sys.argv[sys.argv.index("-j") + 1]) if "-j" in sys.argv else 8
C15 = ("statement-fits", "width-limit")   # one conjunct, its stage-1 and stage-2 names


def width_default():
    """D: --width D, else the candidate's --list-limits row; fail loud."""
    if "--width" in sys.argv:
        return int(sys.argv[sys.argv.index("--width") + 1])
    p = subprocess.run([NEWBIN, "--list-limits"], capture_output=True, timeout=60)
    for ln in p.stdout.decode().splitlines():
        f = ln.split("\t")
        if f[0] == "PCREC_DEFAULT_WINDOW_SEARCH_WIDTH" and len(f) > 1 and f[1].isdigit():
            return int(f[1])
    sys.exit("predict: FAIL: no decimal PCREC_DEFAULT_WINDOW_SEARCH_WIDTH row in %s --list-limits" % NEWBIN)


D = width_default()
sys.path.insert(0, os.path.join(TREE, "scripts"))
import emit_sweep as es  # noqa: E402

ENCS = (("byte", []), ("utf8", ["-e", "utf8"]))

# Facts rows that may differ between the baseline and the candidate for a
# pattern that GAINS a cover (cover_cap.md 3.1/3.3/5.2). DECLARED here, not read
# from the candidate: the first two are the declared-gone / declared-new items;
# the rest are the rows that DESCRIBE the scan route, its prefilter, its start
# and the windows/requirement landmarks the route consumes -- a pattern that now
# compiles to a cover no longer takes that route, so those rows change or vanish.
# Any other row (classes, states, accepts, anchoring, captures, features...)
# moving on a mover is UNEXPLAINED.
DECLARED_ROWS = {"span_facts", "cover"}
ROUTE_ROWS = {"RX_DFA_SCAN", "RX_DFA_SCAN_EDGE", "RX_DFA_PREFILTER", "RX_DFA_PREFILTER_OFFSETS",
              "RX_DFA_START", "RX_DFA_UNIFORM_FOLDS", "RX_REQ_WHY", "RX_REQ_HANDOFF",
              "end_window", "land_char", "width", "req_set", "req_landmark_maxoff",
              "run_pin"}
# every name above is column 2 of a facts/decisions row of a real `--emit-facts` listing (checked against
# a built listing, review r11 ADQ-4). "finisher-dfa" was dropped: it is a conjunct name (known.c, lmwalk.c),
# never a row, so it could never match a moved row.


def run(argv, env=None):
    try:
        return subprocess.run(argv, capture_output=True, env=env, timeout=120)
    except subprocess.TimeoutExpired:
        return None


def decisions(binary, pat):
    """{enc: (why, k)} from the listing's `cover` section (k an int, or None for `-`)."""
    p = run([binary, "--features", "all", "--emit-facts=byte,utf8", "--pattern", pat])
    if p is None:
        return {e: ("timeout", None) for e, _ in ENCS}
    if p.returncode:
        return {e: ("rc!=0", None) for e, _ in ENCS}
    out, sect = {}, ""
    for ln in p.stdout.decode("latin-1").splitlines():
        if ln.startswith("#section "):
            sect = ln.split(None, 1)[1]
            continue
        f = ln.split("\t")
        if sect == "cover" and not ln.startswith("#") and len(f) > 2:
            out[f[0]] = (f[1], int(f[2]) if f[2].isdigit() else None)
    return {e: out.get(e, ("no-row", None)) for e, _ in ENCS}


def facts_rows(binary, pat):
    p = run([binary, "--features", "all", "--emit-facts=byte,utf8", "--pattern", pat])
    if p is None or p.returncode:
        return None
    rows = collections.Counter()
    sect = ""
    for ln in p.stdout.decode("latin-1").splitlines():
        if ln.startswith("#section "):
            sect = ln.split(None, 1)[1]
            continue
        f = ln.split("\t")
        if len(f) > 1 and not ln.startswith("#"):
            # every row of the DECLARED-NEW `cover` section is the one declared item
            rows[(f[0], "cover" if sect == "cover" else f[1], ln)] += 1
    return rows


def moved_rows(pat):
    """{(enc, row-name)} whose lines differ, baseline vs candidate."""
    a, b = facts_rows(REF_BIN, pat), facts_rows(NEWBIN, pat)
    if a is None or b is None:
        return None
    return {(e, n) for (e, n, _) in set((a - b).keys()) | set((b - a).keys())}


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
    a, b = decisions(REF_BIN, pat), decisions(NEWBIN, pat)
    rows = []
    for enc, _ in ENCS:
        # (enc, baseline why, candidate why, wmin, baseline k)
        rows.append((enc, a[enc][0], b[enc][0], wm.get(enc), a[enc][1]))
    return pat, rows


def main():
    newbin = NEWBIN
    pop = es.enumerate_corpus(newbin, TREE, 60)
    pats = sorted({p for _, _, p in pop})
    print("population: %d corpus rows, %d distinct patterns" % (len(pop), len(pats)), flush=True)
    res = {}
    with concurrent.futures.ThreadPoolExecutor(J) as ex:
        for pat, rows in ex.map(one, pats, chunksize=8):
            res[pat] = rows
    pred, out_set, lost = set(), set(), []
    census = collections.Counter()
    c4 = collections.Counter()
    print("width default D = %d" % D, flush=True)
    for pat, rows in res.items():
        for enc, rw, nw, wmin, k in rows:
            census[(enc, rw, nw)] += 1
            if nw.startswith("anchored-A/"):
                c4[(enc, nw)] += 1
            if rw in C15 and k is not None and k <= D:            # (1) INTO
                pred.add(pat)
            if rw == "cover" and k is not None and k > D:         # (2) expected OUT
                out_set.add(pat)
                if nw not in C15:
                    lost.append((pat, enc, rw, nw))   # OUT, but not to C15: still LOST
            elif rw == "cover" and nw != "cover":
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
    unexplained = sorted(p for p in observed if p not in pred and p not in out_set)
    # each mover must be a GAINED cover or an expected-OUT one, and move only
    # declared/route rows (in an encoding whose cover changed)
    wrong = []   # (pattern, why-text)
    for p in sorted(observed):
        rows = dict((enc, (rw, nw)) for enc, rw, nw, _, _ in res[p])
        gained = [e for e, (rw, nw) in rows.items() if rw != "cover" and nw == "cover"]
        dropped = [e for e, (rw, nw) in rows.items() if rw == "cover" and nw in C15 and p in out_set]
        mv = moved_rows(p)
        if mv is None:
            wrong.append((p, "facts listing failed on a side"))
            continue
        if not gained and not dropped:
            wrong.append((p, "mover but no encoding gains or (expected) drops a cover: " + repr(rows)))
        for enc, name in sorted(mv):
            if name in DECLARED_ROWS:
                continue
            if name not in ROUTE_ROWS:
                wrong.append((p, "row outside the declared route rows moved: %s %s" % (enc, name)))
            elif enc not in gained and enc not in dropped:
                wrong.append((p, "route row %s moved in %s where the cover did not change (%s -> %s)" % (name, enc, rows[enc][0], rows[enc][1])))
    unmoved = sorted(p for p in (pred | out_set) if p not in observed)
    with open(OUT, "w") as fh:
        fh.write("#class\tpattern\tencoding\tbaseline_why\tcandidate_why\twmin\tbaseline_k\tstreams\n")
        for p in sorted(res):
            cls = ("LOST" if any(x[0] == p for x in lost) else
                   "UNEXPLAINED" if p in unexplained else
                   "predicted-moved" if (p in pred or p in out_set) and p in observed else
                   "predicted-unmoved" if p in pred or p in out_set else "-")
            for enc, rw, nw, wmin, k in res[p]:
                fh.write("%s\t%r\t%s\t%s\t%s\t%s\t%s\t%s\n" % (cls, p, enc, rw, nw, wmin, k,
                                                           ",".join(sorted(observed.get(p, ())))))
    print("## decision census (encoding, baseline why -> candidate why), K35 over %d patterns x 2" % len(res))
    for (enc, rw, nw), n in sorted(census.items(), key=lambda kv: (kv[0][0], -kv[1])):
        if rw != nw:
            print("moved\t%s\t%s -> %s\t%d" % (enc, rw, nw, n))
    print("unchanged decisions: %d" % sum(n for (e, a, b), n in census.items() if a == b))
    print("## C4 guards on the candidate: " + (", ".join("%s %s %d" % (k[0], k[1], v) for k, v in sorted(c4.items())) or "none"))
    print("predicted INTO=%d OUT=%d observed=%d predicted-moved=%d predicted-unmoved=%d" % (
        len(pred), len(out_set), len(observed), len((pred | out_set) & set(observed)), len(unmoved)))
    for p in unmoved:
        print("predicted-unmoved\t%r\t%s" % (p[:80], " ".join("%s:%s" % (r[0], r[2]) for r in res[p])))
    for p in unexplained:
        print("UNEXPLAINED\t%r\t%s\t%s" % (p[:80], ",".join(sorted(observed[p])),
                                          " ".join("%s:%s>%s" % (r[0], r[1], r[2]) for r in res[p])))
    for p, why in wrong:
        print("UNEXPLAINED-ROWS\t%r\t%s" % (p[:80], why))
    for x in lost:
        print("LOST\t%r\t%s\t%s -> %s" % (x[0][:80], x[1], x[2], x[3]))
    for x in unkeyed[:20]:
        print("UNKEYED\t%s\t%s\t%s" % x)
    bad = bool(lost or unexplained or unkeyed or wrong)
    print("predict: lost=%d unexplained=%d unexplained-rows=%d unkeyed=%d gained-movers=%d" % (len(lost), len(unexplained), len(wrong), len(unkeyed), len(observed) - len({p for p, _ in wrong})))
    print("predict: DONE rc=%d" % (1 if bad else 0))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
