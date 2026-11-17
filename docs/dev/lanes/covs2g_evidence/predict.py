r"""[COVER-CAP] stage 2 (lane covs2g; cover_cap.md §11.1 "The prediction"; review r45chk P2,
r45read W20): the mover PREDICTION against the emit sweep's OBSERVED movers, re-pointed to
compute the kit's POSSIBLE-MOVER predicate (N1) from pcrec's own `MFWSTMT` trace records. A COPY
of lane covs2a's docs/dev/lanes/covs2a_evidence/predict.py (which stays as committed) with one
added prediction class, FORM, and its input:

  FORM(P, h*)  = some encoding's trace compile of P (a -DPCREC_CAND_TRACE build of the
                 candidate, `--trace-bin`, env PCREC_MF_ROUTE_TRACE=1) prints an `MFWSTMT`
                 alternative (one (site, kind, owner, alt) group: the site's own alternatives
                 and each pre-check part's) holding a RUN: two or more CONSECUTIVE stated
                 offsets o .. o + n - 1 whose positions carry ONE byte-identical set under
                 either meet (the AND of the sets every span states at that offset, over every
                 span, and over the verify-YES spans only), that set has two or more members,
                 and the run's LAST offset is at or past h* (`--hstar`). Span boundaries do not
                 end a run: a cover's after side at k (and its before side at -1) joins the
                 0 .. k - 1 run when its set is the same.

The predictor reads pcrec's STATEMENTS only, never the kit's reply or plan (r45chk P2; R6
line 703-705): it is pcrec's independent control of the forms. Its red is a moved pattern
outside INTO | OUT | FORM; a predicted pattern that does not move is listed, never red. With
no `--hstar` the FORM class is empty (h* = 64, the predicted tie: no site moves, cover_cap.md
§11.1) and the run is covs2a's.

`--selftest` checks the predicate itself on named witnesses through `--trace-bin` (no sweep,
no corpus): `\w{32}\B` (its after side continues \w to offset 32: a possible mover at every
h* <= 32, not at 33), `[0-9a-f]{24}` (last offset 23: a mover at h* <= 23, not at 24), `a{32}`
(a run of one-member sets: never), plus two plants that must flip a verdict (the
two-member clause dropped; span boundaries ending a run).

The rest of covs2a's text, unchanged:

Over the sweep's own population (every corpus pattern, `enumerate_corpus`),
both encodings, the BASELINE listing (REF_PCREC, main before stage 2) and the
CANDIDATE listing (TREE/build/pcrec) each give the cover decision's `why` and
`k` (the `cover` section, facts_listing.md §4.5: columns why, k). The
baseline's `statement-fits` and the candidate's `width-limit` are the same
conjunct C15 (renamed at stage 2, A4). D is the candidate's width default
(`--list-limits` PCREC_DEFAULT_WINDOW_SEARCH_WIDTH, read fail-loud; `--width D`
overrides it for a -D build).

  INTO(P)      = some encoding's BASELINE why is `statement-fits` and its k
                 <= D (an UPPER bound: C9-C14 never ran on it).
  OUT(P)       = some encoding's BASELINE why is `cover` with k > D: expected
                 to move, to the candidate's `width-limit`.
  LOST(P)      = some encoding's baseline why is `cover` and the candidate's
                 is not, outside OUT
  UNEXPLAINED  = a sweep mover (any artifact stream) whose pattern is in
                 none of INTO, OUT, FORM (G2: predicted must contain observed)

NOT handled here (cover_cap.md §11.1, PER SWEEP VARIANT): a lowered-cap
variant's `size-cap-retry` artifacts; the listings are the default build's.

usage: python3 -I predict.py TREE REF_PCREC MOVERS.tsv OUT.tsv [--width D] [-j N]
                             [--trace-bin TRB --hstar H]
       python3 -I predict.py --selftest TREE --trace-bin TRB
"""
import collections, concurrent.futures, os, subprocess, sys, tempfile

def opt(name, conv=str, default=None):
    return conv(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


SELFTEST = "--selftest" in sys.argv
if SELFTEST:
    TREE, REF_BIN, MOVERS, OUT = sys.argv[sys.argv.index("--selftest") + 1], None, None, None
else:
    TREE, REF_BIN, MOVERS, OUT = sys.argv[1:5]
NEWBIN = os.path.join(TREE, "build", "pcrec")
TRBIN = opt("--trace-bin")
HSTAR = opt("--hstar", int)
if (HSTAR is not None or SELFTEST) and not (TRBIN and os.access(TRBIN, os.X_OK)):
    sys.exit("predict: FAIL: --hstar/--selftest need --trace-bin, an executable -DPCREC_CAND_TRACE pcrec")
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


D = None if SELFTEST else width_default()
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


def stmt_records(pat):
    """{enc: [MFWSTMT fields]} from the trace build's compile of P (deduplicated: a site
    stated twice in one compile prints twice); None for an encoding whose compile failed."""
    env = dict(os.environ, PCREC_MF_ROUTE_TRACE="1")
    out = {}
    for enc, fl in ENCS:
        with tempfile.TemporaryDirectory() as td:   # the compile writes a.c and a.h
            p = run([TRBIN, "--features", "all", "-p", "rx", "-o", os.path.join(td, "a.c")] + fl +
                    ["--pattern", pat], env=env)
        if p is None or p.returncode:
            out[enc] = None
            continue
        recs = []
        for ln in dict.fromkeys(p.stderr.decode("latin-1").splitlines()):
            f = ln.split("\t")
            if f[0] == "MFWSTMT" and len(f) == 14:
                recs.append(f[1:])
        out[enc] = recs
    return out


def alt_groups(recs):
    """{(site, kind, owner, alt): [(start, verify, [set bytes per position])]} per alternative."""
    g = collections.defaultdict(list)
    for site, kind, owner, alt, _entry, _rs, _span, start, ln, verify, _clo, _clen, sets in recs:
        ps = [bytes.fromhex(x) for x in sets.split(",")] if int(ln) else []
        if len(ps) != int(ln) or any(len(x) != 32 for x in ps):
            raise ValueError("MFWSTMT span with %s positions but sets %r" % (ln, sets[:80]))
        g[(site, kind, owner, alt)].append((int(start), int(verify), ps))
    return g


VERIFY_YES = 1   # memfn.h: MF_VERIFY_UNSTATED 0, MF_VERIFY_YES 1, MF_VERIFY_NO 2


def runs(spans, yes_only, boundaries_end=False):
    """The maximal runs of one alternative under one meet: [(first, last, set)]. The meet at an
    offset is the AND of every (verify-YES, with yes_only) span's set there. `boundaries_end`
    is the PLANT the selftest uses (a run broken where one span ends and the next begins)."""
    meet, owner = {}, {}
    for i, (start, verify, ps) in enumerate(spans):
        if yes_only and verify != VERIFY_YES:
            continue
        for j, st in enumerate(ps):
            o = start + j
            meet[o] = bytes(a & b for a, b in zip(meet[o], st)) if o in meet else st
            owner.setdefault(o, i)
    out, cur = [], None
    for o in sorted(meet):
        if (cur and o == cur[1] + 1 and meet[o] == cur[2] and
                not (boundaries_end and owner[o] != owner[cur[1]])):
            cur[1] = o
        else:
            if cur:
                out.append(tuple(cur))
            cur = [o, o, meet[o]]
    if cur:
        out.append(tuple(cur))
    return out


def popcount(st):
    return sum(bin(b).count("1") for b in st)


def possible_movers(recs, h, min_members=2, boundaries_end=False):
    """N1 (cover_cap.md §11.1, r45chk P2): the alternatives that are possible movers at h*."""
    hits = []
    for key, spans in alt_groups(recs).items():
        for yes_only in (False, True):
            for first, last, st in runs(spans, yes_only, boundaries_end):
                if last - first + 1 >= 2 and popcount(st) >= min_members and last >= h:
                    hits.append((key, "yes" if yes_only else "all", first, last))
    return hits


def one(pat):
    wm = wmins(pat)
    a, b = decisions(REF_BIN, pat), decisions(NEWBIN, pat)
    rows = []
    for enc, _ in ENCS:
        # (enc, baseline why, candidate why, wmin, baseline k)
        rows.append((enc, a[enc][0], b[enc][0], wm.get(enc), a[enc][1]))
    form = None
    if HSTAR is not None:
        st = stmt_records(pat)
        form = {enc: (None if r is None else (len(alt_groups(r)), possible_movers(r, HSTAR)))
                for enc, r in st.items()}
    return pat, rows, form


def selftest():
    """The predicate's own witnesses and plants (no sweep, no corpus): each line a verdict."""
    fails = 0
    cases = [("\\w{32}\\B", 32, True), ("\\w{32}\\B", 33, False), ("[0-9a-f]{24}", 23, True),
             ("[0-9a-f]{24}", 24, False), ("a{32}", 0, False)]
    recs = {}
    for pat, h, want in cases:
        if pat not in recs:
            recs[pat] = stmt_records(pat)["byte"]
        r = recs[pat]
        if not r:
            print("selftest FAIL: %r: no MFWSTMT record (the trace build states nothing)" % pat)
            fails += 1
            continue
        got = bool(possible_movers(r, h))
        print("selftest %s: %r at h*=%d: possible mover %s (expected %s; %d alternative(s), %d record(s))"
              % ("ok" if got == want else "FAIL", pat, h, got, want, len(alt_groups(r)), len(r)))
        fails += got != want
    # PLANTS: each must flip a verdict above, or the clause it drops is untested
    lit = recs["a{32}"]
    w32 = recs["\\w{32}\\B"]
    if not lit or not w32:   # a plant over no records flips nothing and proves nothing
        print("predict selftest: DONE rc=1")
        return 1
    flip1 = bool(possible_movers(lit, 0, min_members=1))
    print("selftest %s: plant (the two-member clause dropped) flips the literal to a mover" % ("ok" if flip1 else "FAIL"))
    flip2 = not possible_movers(w32, 32, boundaries_end=True)
    print("selftest %s: plant (span boundaries end a run) drops \\w{32}\\B at h*=32" % ("ok" if flip2 else "FAIL"))
    fails += (not flip1) + (not flip2)
    print("predict selftest: DONE rc=%d" % (1 if fails else 0))
    return 1 if fails else 0


def main():
    newbin = NEWBIN
    pop = es.enumerate_corpus(newbin, TREE, 60)
    pats = sorted({p for _, _, p in pop})
    print("population: %d corpus rows, %d distinct patterns" % (len(pop), len(pats)), flush=True)
    res, formres = {}, {}
    with concurrent.futures.ThreadPoolExecutor(J) as ex:
        for pat, rows, fm in ex.map(one, pats, chunksize=8):
            res[pat] = rows
            formres[pat] = fm
    pred, out_set, lost = set(), set(), []
    # (3) FORM: N1 from pcrec's MFWSTMT statements at h* (r45chk P2); K35 counts below
    form, form_failed, nalt = set(), [], 0
    for pat, fm in formres.items():
        if fm is None:
            continue
        for enc, v in fm.items():
            if v is None:
                form_failed.append((pat, enc))
                continue
            nalt += v[0]
            if v[1]:
                form.add(pat)
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
    unexplained = sorted(p for p in observed if p not in pred and p not in out_set and p not in form)
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
        if not gained and not dropped and p in form:
            # a FORM mover moves emitted text only: its cover decision stays, so no facts row may move
            for enc, name in sorted(mv):
                wrong.append((p, "form mover moved a facts row: %s %s" % (enc, name)))
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
    unmoved = sorted(p for p in (pred | out_set | form) if p not in observed)
    with open(OUT, "w") as fh:
        fh.write("#class\tpattern\tencoding\tbaseline_why\tcandidate_why\twmin\tbaseline_k\tstreams\n")
        for p in sorted(res):
            cls = ("LOST" if any(x[0] == p for x in lost) else
                   "UNEXPLAINED" if p in unexplained else
                   "predicted-moved" if (p in pred or p in out_set or p in form) and p in observed else
                   "predicted-unmoved" if p in pred or p in out_set or p in form else "-")
            for enc, rw, nw, wmin, k in res[p]:
                fh.write("%s\t%r\t%s\t%s\t%s\t%s\t%s\t%s\n" % (cls, p, enc, rw, nw, wmin, k,
                                                           ",".join(sorted(observed.get(p, ())))))
    print("## decision census (encoding, baseline why -> candidate why), K35 over %d patterns x 2" % len(res))
    for (enc, rw, nw), n in sorted(census.items(), key=lambda kv: (kv[0][0], -kv[1])):
        if rw != nw:
            print("moved\t%s\t%s -> %s\t%d" % (enc, rw, nw, n))
    print("unchanged decisions: %d" % sum(n for (e, a, b), n in census.items() if a == b))
    print("## C4 guards on the candidate: " + (", ".join("%s %s %d" % (k[0], k[1], v) for k, v in sorted(c4.items())) or "none"))
    print("FORM at h*=%s: %d pattern(s) over %d statement alternative(s); %d trace compile(s) failed" % (
        HSTAR if HSTAR is not None else "64 (none given: the tie, empty)", len(form), nalt, len(form_failed)))
    if HSTAR is not None and nalt == 0:
        lost.append(("(population)", "-", "MFWSTMT", "0 alternatives read: the trace pass stated nothing (K35)"))
    print("predicted INTO=%d OUT=%d FORM=%d observed=%d predicted-moved=%d predicted-unmoved=%d" % (
        len(pred), len(out_set), len(form), len(observed), len((pred | out_set | form) & set(observed)), len(unmoved)))
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
    sys.exit(selftest() if SELFTEST else main())
