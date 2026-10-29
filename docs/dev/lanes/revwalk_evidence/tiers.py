#!/usr/bin/env python3
"""Lane revwalk (2026-10-29): the REVERSE-WALK TIER CENSUS for docs/dev/lanes/revwalk_report.md.

PARSE-ONLY: no pattern is compiled, no subject matched, no clock read; pcrec runs only as
`--list-source` (the corpus lister).  Nothing under src/ is read or touched.

For each unanchored pattern R it takes the best inner landmark L (a maximal literal run of the
flattened top-level spine with a non-empty prefix P before it; "best" = rarest scan byte under the
shipped prior tests/findings/default_ppm.tsv; ONE common L across top-level branches, D151 add. 6)
and classifies the walk back from L over P into the first-match tier table of the report:

  G1-fail   P holds a backreference, call, atomic/possessive group or lookaround (no tier)
  T1        P has FIXED byte width k (today's fixed move-back: spans at fixed offsets)
  T2        P's reverse walk automaton is a CHAIN (each state: a self-loop set, one exit, accept bit)
            with exactly ONE variable-width item (one class run, bounded or unbounded)
  T3        a chain with >= 2 variable-width items (a string of non-overlapping runs)
  T4        anything else (general reverse DFA)
plus, for T2/T3, the EXCLUSION fact (L's bytes not all in alphabet(P): the walk can never cross an
earlier occurrence) and for every tier the strong-arm composition across branches.

"Chain" is decided on the AUTOMATON (D151 add. 6 F7: never on a pattern list): P's NFA (rincensus's
build_nfa, so utf8 multibyte classes enter as their byte automata), reversed, determinised over byte
equivalence classes, minimised (Moore), and accepted iff every live state has at most one successor
other than itself and the graph has no cycle except self-loops.  A leading zero-width view in P
(`\\b`, `^` under (?m)) is admitted as start CONTEXT; a view anywhere else sends P to T4.

The reader, flatten, landmarks, NFA builder and arms are IMPORTED from
docs/design/where_to_start/rincensus.py (loaded by path).  Controls: --selftest (C1 hand rows,
positives and negatives per tier, plus a sabotage that blinds the chain test and must FAIL).

Env: PCREC (default build/pcrec), CORPUS (default .), OUT (default build/revwalk).
Usage: PCREC=build/pcrec CORPUS=. OUT=<scratch> python3 tiers.py [--selftest] [--sabotage chain]
"""
import argparse, collections, gzip, importlib.util, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.environ
E.setdefault("PCREC", "build/pcrec"); E.setdefault("CORPUS", "."); E.setdefault("OUT", "build/revwalk")
spec = importlib.util.spec_from_file_location(
    "rincensus", os.path.join(HERE, "..", "..", "..", "design", "where_to_start", "rincensus.py"))
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
G = R.G
G.PRIOR = G.prior()
ALL = R.ALL
DFA_CAP = 4000
SABOTAGE = None


class Reader(R.Reader):
    """rincensus's Reader, with ANCHORS told apart from other views: ('zw','anch') for \\A \\G and
    a non-multiline ^ ; ('zw','ctx') for \\b \\B and a multiline ^ (a context test on the byte before)."""

    def __init__(self, p, icase, utf8, mline):
        super().__init__(p, icase, utf8); self.mline = mline

    def atom(self):
        s, i = self.s, self.i
        if s.startswith("^", i):
            self.i += 1; return ("zw", "ctx", "^m") if self.mline else ("zw", "anch")
        if s.startswith(("\\A", "\\G"), i):
            self.i += 2; return ("zw", "anch")
        if s.startswith(("\\b", "\\B"), i):
            self.i += 2; return ("zw", "ctx", s[i:i + 2])
        if re.match(r"\(\?[a-zA-Z]*m[a-zA-Z]*\)", s[i:]) and "-" not in s[i:s.find(")", i)]:
            self.mline = True
        return super().atom()


def strip_one_group(tree):
    while len(tree) == 1 and len(tree[0]) == 1 and tree[0][0][0] == "grp" and not tree[0][0][2]:
        tree = tree[0][0][1]
    return tree


def anchored(tree):
    """every top-level branch opens (after flags) on a start anchor"""
    for alt in tree:
        sp = R.flatten(alt, True)
        k = 0
        while k < len(sp) and sp[k][:2] == ("zw", "flag"):
            k += 1
        if not (k < len(sp) and sp[k][:2] == ("zw", "anch")):
            return False
    return True


# ---- the reverse walk automaton -------------------------------------------------------------

def eclose(eps, qs):
    st = list(qs); out = set(qs)
    while st:
        q = st.pop()
        for q2 in eps[q]:
            if q2 not in out:
                out.add(q2); st.append(q2)
    return frozenset(out)


def reverse_dfa(items, utf8):
    """-> (states, trans, accept, start) of the MINIMAL DFA of reverse(L(items)), dead state removed;
    raises R.Cap on size."""
    eps, tr, s0, e0 = R.build_nfa(items, utf8)
    n = len(eps)
    reps = [[] for _ in range(n)]; rtr = [[] for _ in range(n)]
    for q in range(n):
        for q2 in eps[q]:
            reps[q2].append(q)
        for cs, q2 in tr[q]:
            rtr[q2].append((cs, q))
    # byte equivalence classes over every transition set
    sig = [0] * 256
    sets = {cs for q in range(n) for cs, _ in rtr[q]}
    for k, cs in enumerate(sets):
        for b in cs:
            sig[b] |= 1 << k
    cls = {}
    for b in range(256):
        cls.setdefault(sig[b], []).append(b)
    classes = [frozenset(v) for v in cls.values()]
    rep = [min(c) for c in classes]
    start = eclose(reps, {e0})
    idx = {start: 0}; order = [start]; trans = []
    while len(trans) < len(order):
        S = order[len(trans)]
        row = []
        for ci, b in enumerate(rep):
            T = set()
            for q in S:
                for cs, q2 in rtr[q]:
                    if b in cs:
                        T.add(q2)
            T = eclose(reps, T) if T else frozenset()
            if T not in idx:
                if len(order) >= DFA_CAP:
                    raise R.Cap("dfa")
                idx[T] = len(order); order.append(T)
            row.append(idx[T])
        trans.append(row)
    acc = [s0 in S for S in order]
    dead = [len(S) == 0 for S in order]
    # Moore minimisation
    part = [(1 if acc[i] else 0) if not dead[i] else 2 for i in range(len(order))]
    while True:
        keys = {}
        newp = []
        for i in range(len(order)):
            k = (part[i],) + tuple(part[t] for t in trans[i])
            newp.append(keys.setdefault(k, len(keys)))
        if len(keys) == len(set(part)):
            part = newp; break
        part = newp
    m = max(part) + 1
    mtrans = [None] * m; macc = [False] * m; mdead = [False] * m
    for i in range(len(order)):
        p = part[i]
        mtrans[p] = [part[t] for t in trans[i]]; macc[p] = acc[i]; mdead[p] = dead[i] or mdead[p]
    # a merged class is dead iff it cannot reach an accepting state
    live = set(p for p in range(m) if macc[p])
    changed = True
    while changed:
        changed = False
        for p in range(m):
            if p not in live and any(t in live for t in mtrans[p]):
                live.add(p); changed = True
    return mtrans, macc, live, part[0], classes


def chain_shape(items, utf8):
    """-> ('chain', nloop) | ('nochain', why).  A CHAIN: from the start, every live state has at most
    one live successor other than itself, and no cycle except self-loops."""
    if SABOTAGE == "chain":
        return ("chain", 1)
    try:
        mtrans, macc, live, st, classes = reverse_dfa(items, utf8)
    except R.Cap as e:
        return ("nochain", "cap")
    seen = set(); q = st; nloop = 0
    while True:
        if q in seen:
            return ("nochain", "cycle")
        seen.add(q)
        succ = {t for t in mtrans[q] if t in live}
        if q in succ:
            nloop += 1; succ.discard(q)
        if len(succ) > 1:
            return ("nochain", "branch")
        if not succ:
            return ("chain", nloop)
        q = succ.pop()


def scanedge_cover(items, utf8):
    """R1 (scan edges, src/opt/scanedge.c precondition (1)): on P's minimal reverse DFA, is EVERY self-loop
    state SCAN-SHAPED today, i.e. every byte outside its loop set leaves to ONE target (dead counted as one)?
    -> 'all' | 'some' | 'none' | 'noloop' | 'nochain'"""
    try:
        mtrans, macc, live, st, classes = reverse_dfa(items, utf8)
    except R.Cap:
        return "nochain"
    if chain_shape(items, utf8)[0] != "chain":
        return "nochain"
    loops = shaped = 0
    for q in live:
        row = mtrans[q]
        if q not in row:
            continue
        loops += 1
        exits = {(t if t in live else -1) for t in row if t != q}
        shaped += len(exits) == 1
    if not loops:
        return "noloop"
    return "all" if shaped == loops else ("some" if shaped else "none")


def is_var(it):
    lo, hi, _a, _f = R.props(it)
    return hi is None or lo != hi


def last_of(it):
    """the bytes that can END a non-empty string of `it`"""
    k = it[0]
    if k == "set":
        return set(it[1])
    if k == "zw":
        return set()
    if k == "rep":
        return set() if it[3] == 0 else last_of(it[1])
    if k == "grp":
        out = set()
        for a in it[1]:
            out |= last_seq(a)
        return out
    return set(ALL)


def last_seq(items):
    out = set()
    for it in reversed(items):
        out |= last_of(it)
        if R.props(it)[0] > 0:
            break
    return out


def plain(seg):
    """L(seg) = B^[m,M] for ONE byte set B, decided on the automaton: seg's minimal reverse DFA is a chain
    and every live state sends all of B, and only B, to one live successor (itself or the next)"""
    try:
        mtrans, macc, live, st, classes = reverse_dfa(seg, False)
    except R.Cap:
        return False
    B = None; q = st; seen = set()
    while q not in seen:
        seen.add(q)
        outs = {}
        for ci, t in enumerate(mtrans[q]):
            if t in live:
                outs.setdefault(t, set()).update(classes[ci])
        if not outs:
            return B is not None
        if len(outs) != 1:
            return False
        (t, bs), = outs.items()
        if B is None:
            B = bs
        elif bs != B:
            return False
        if t == q:
            return True
        q = t
    return False


def exact_chain(seg, utf8):
    return chain_shape(seg, utf8)[0] == "chain"


def segments(body):
    """the FINEST segmentation from the right: a cut before item i iff LAST(body[:i]) is disjoint from the
    alphabet of the segment being built.  -> list of segments (forward order), each a list of items"""
    segs, cur, B = [], [], set()
    for i in range(len(body) - 1, -1, -1):
        cur.insert(0, body[i]); B |= R.props(body[i])[2]
        if i > 0 and not (last_seq(body[:i]) & B):
            segs.insert(0, cur); cur, B = [], set()
    if cur:
        segs.insert(0, cur)
    return segs


def ascii_only(seg):
    _lo, _hi, al, _f = R.seq_props(seg)
    return all(b < 0x80 for b in al)


def seg_kind(seg, utf8=False):
    """plain under utf8 only where every byte is ASCII (a byte-EXACT run, D161 add. 10)"""
    lo, hi, _a, _f = R.seq_props(seg)
    if (not utf8 or ascii_only(seg)) and plain(seg):
        return "plain"
    if hi is not None and lo == hi:
        return "fixed"
    return "chain" if exact_chain(seg, utf8) else "other"


def seg_tier(body, utf8=False):
    """-> (tier, why, segs).  A segment that may host the match start (every earlier one nullable) must be
    walked EXACTLY: plain, fixed (the first only: nothing precedes it) or a chain automaton; any other
    segment is back-scanned over its alphabet (a SUPERSET, its content left to the verify).
    T2: one variable segment, plain; T3: the rest of the admitted."""
    segs = segments(body)
    kinds = [seg_kind(q, utf8) for q in segs]
    sup = False
    for k, q in enumerate(segs):
        po = all(R.seq_props(segs[t])[0] == 0 for t in range(k))
        if po:
            if not (kinds[k] in ("plain", "chain") or (k == 0 and kinds[k] == "fixed")):
                return "outer", "start may lie in segment %d/%d (%s)" % (k + 1, len(segs), kinds[k]), segs
        elif kinds[k] == "other" or (utf8 and kinds[k] != "fixed" and not ascii_only(q)):
            sup = True
    var = [k for k, q in enumerate(segs) if any(is_var(x) for x in q)]
    if len(var) == 1 and kinds[var[0]] == "plain" and not sup:
        return "T2", "segs=%d" % len(segs), segs
    return "T3", "segs=%d var=%d%s" % (len(segs), len(var), " superset" if sup else ""), segs


def classify_p(pit, run, utf8, icase):
    """-> dict(tier, why, excl, strong, fixed, nvar, unb, ctx, chain)"""
    a = R.arms_for(pit, run, utf8, icase)
    o = dict(excl=bool(a.get("disj")), strong=bool(a.get("disj") or a.get("ffree")),
             fixed=bool(a.get("fixed")), pmin=a["pmin"], pmax=a["pmax"], g1why=a.get("g1_why", ""))
    if a["empty"]:
        o.update(tier="T0", why="P empty"); return o
    if not a["g1"]:
        o.update(tier="G1", why=a["g1_why"]); return o
    if a["fixed"]:
        o.update(tier="T1", why="fixed width %d" % a["pmin"]); return o
    body = list(pit); ctx = False
    while body and body[0][0] == "zw":
        ctx = ctx or body[0][1] == "ctx"; body = body[1:]
    if any(R.props(x)[3] or x[0] == "zw" or (x[0] in ("grp", "rep") and has_zw(x)) for x in body):
        o.update(tier="T4", why="view inside P"); return o
    o.update(nvar=sum(1 for x in body if is_var(x)), unb=sum(1 for x in body if R.props(x)[1] is None), ctx=ctx)
    o["chain"] = chain_shape(body, utf8)[0]
    o["sedge"] = scanedge_cover(body, utf8)
    if SABOTAGE == "chain":
        o.update(tier="T2", why="sabotaged"); return o
    t, why, segs = seg_tier(body, utf8)
    o["nseg"] = len(segs)
    if t == "outer":
        o.update(tier="T4", why="outer"); o["t3x"] = True; return o
    o.update(tier=t, why=why)
    return o


def has_zw(it):
    if it[0] == "zw":
        return True
    if it[0] == "grp":
        return any(has_zw(x) for a in it[1] for x in a)
    if it[0] == "rep":
        return has_zw(it[1])
    return False


TIER_RANK = {"T0": 0, "T1": 1, "T2": 2, "T3": 3, "T4": 4, "G1": 5}


def decide(tree, utf8, icase):
    tree = strip_one_group(tree)
    branches = [R.flatten(a, True) for a in tree]
    per = [R.cands_of(sp, "max") for sp in branches]
    if not any(per):
        return dict(stage="no-landmark")
    common = set(per[0])
    for d in per[1:]:
        common &= set(d)
    if not common:
        return dict(stage="no-common-L")
    first = set()
    for sp in branches:
        try:
            eps, tr, s0, _e = R.build_nfa(sp, utf8)
            for q in eclose(eps, {s0}):
                for cs, _ in tr[q]:
                    first |= cs
        except R.Cap:
            first = set(ALL)
    key_ppm = R.ppm(first) if first else R.ppm(ALL)
    best = None
    for key in common:
        run = list(key)
        scan = min(R.ppm(r) for r in run)
        res = []
        for bi, sp in enumerate(branches):
            ch = None
            for start, _r in per[bi][key]:
                c = classify_p(sp[:start], run, utf8, icase)
                c["S_refs"] = refs_back(sp[start + len(run):])
                c["_pit"] = sp[:start]
                if ch is None or (c["tier"] != "T0" and (ch["tier"] == "T0" or TIER_RANK[c["tier"]] < TIER_RANK[ch["tier"]])):
                    ch = c
            res.append(ch)
        if all(c["tier"] == "T0" for c in res):
            continue
        tier = max((c["tier"] for c in res if c["tier"] != "T0"), key=lambda t: TIER_RANK[t])
        strong = all(c["tier"] == "T0" or c["strong"] for c in res)
        excl = all(c["tier"] == "T0" or c["excl"] for c in res)
        widths = {c["pmin"] for c in res if c["tier"] == "T1"}
        comp = len(res) == 1 or strong or (all(c["tier"] == "T1" for c in res) and len(widths) == 1)
        cand = dict(stage="landmark", tier=tier, strong=strong, excl=excl, comp=comp, ratio=key_ppm / max(1, scan),
                    L="".join(chr(min(r)) if 32 <= min(r) < 127 else "\\x%02x" % min(r) for r in run),
                    nbr=len(res), why=";".join(c["why"] for c in res), unb=max(c.get("unb", 0) for c in res),
                    ctx=any(c.get("ctx") for c in res), srefs=any(c["S_refs"] for c in res),
                    chain=",".join(c.get("chain", "") for c in res), t3x=any(c.get("t3x") for c in res),
                    sedge=",".join(c.get("sedge", "") for c in res),
                    _pit=res[0]["_pit"] if len(res) == 1 else None, _run=run)
        # prefer: an admissible tier (T1..T3 composing; T2/T3 also excluding), then rarer
        adm = admissible(cand)
        rk = (adm, cand["ratio"], -TIER_RANK[tier])
        if best is None or rk > best[0]:
            best = (rk, cand)
    if best is None:
        return dict(stage="P-empty")
    return best[1]


def admissible(c):
    if c["tier"] == "T1":
        return c["comp"]
    if c["tier"] in ("T2", "T3"):
        return c["comp"] and c["strong"]
    return False


def refs_back(items):
    return any(R.props(x)[3] & {"bref", "call"} for x in items)


# ---- populations --------------------------------------------------------------------------

def corpus_pop():
    rows, seen = [], set()
    files = []
    for root, _d, fs in os.walk(os.path.join(E["CORPUS"], "tests")):
        files += [os.path.join(root, f) for f in fs if f.endswith(".rxt")]
    for f in sorted(files):
        r = subprocess.run([E["PCREC"], "--list-source", f], capture_output=True, timeout=120)
        if r.returncode != 0:
            continue
        rel = os.path.relpath(f, E["CORPUS"])
        for ln in r.stdout.split(b"\n"):
            if ln.startswith(b"#section"):
                break
            if not ln or ln.startswith(b"#"):
                continue
            fl = ln.split(b"\t")
            if len(fl) < 9 or fl[0] not in (b"pattern", b"pattern-esc"):
                continue
            pat = G.dec_field(fl[4])
            if not pat or b"\x00" in pat:
                continue
            enc = "utf8" if fl[8].decode() == "utf8" else "byte"
            fla = fl[5].decode()
            key = (pat, enc, fla)
            if key in seen:
                continue
            seen.add(key)
            rows.append(dict(pop="corpus", id="%s:%s" % (rel, fl[1].decode()), enc=enc,
                             icase="i" in fla, mline="m" in fla, pat=pat))
    return rows


def bench_pop():
    """the bench snapshot the repo holds: docs/design/startset/census.tsv's bench rows (pat_hex), plus
    the subtri witnesses (docs/dev/lanes/subtri_evidence/*.tmpl name them; 5b is added by hand)."""
    rows = []
    f = os.path.join(E["CORPUS"], "docs", "design", "startset", "census.tsv")
    hdr = None
    for ln in open(f, encoding="utf-8"):
        if ln.startswith("#"):
            continue
        fl = ln.rstrip("\n").split("\t")
        if hdr is None:
            hdr = fl; continue
        d = dict(zip(hdr, fl))
        if d["kind"] != "bench":
            continue
        rows.append(dict(pop="bench", id="%s/%s" % (d["set"], d["name"]), enc="utf8" if d["set"] == "utf8" else "byte",
                         icase=False, mline=False, pat=bytes.fromhex(d["pat_hex"])))
    # the 5b witness: subtri_report.md "Case 5b" gives the prefix class and the landmark `@`; the suffix
    # here is an APPROXIMATION (the bench file is not in this repo); the tier reads only P and L
    rows.append(dict(pop="bench", id="subtri/5b-mask-email~", enc="byte", icase=False, mline=False,
                     pat=rb"[%+\-.0-9A-Za-z_]+@[0-9A-Za-z\-]+(?:\.[0-9A-Za-z\-]+)*\.[A-Za-z]{2,}"))
    return rows


def row_of(r, keep=False):
    o = dict(pop=r["pop"], id=r["id"], enc=r["enc"])
    try:
        rd = Reader(r["pat"], r["icase"], r["enc"] == "utf8", r["mline"])
        tree = rd.parse()
    except (R.Unparsed, IndexError, ValueError, RecursionError) as e:
        o["stage"] = "unparsed"; o["why"] = str(e) or type(e).__name__; return o
    if anchored(strip_one_group(tree)):
        o["stage"] = "anchored"; return o
    if rd.approx:
        o["stage"] = "approx"; o["why"] = "an item the reader approximates (\\X \\p \\C ...)"; return o
    try:
        d = decide(tree, r["enc"] == "utf8", r["icase"])
        if not keep:
            d = {k: v for k, v in d.items() if not k.startswith("_")}
        o.update(d)
    except (R.Cap, RecursionError) as e:
        o["stage"] = "cap"
    # the whole-pattern reverse walk (today's reverse pass from a match END): its tier with P = R
    t2 = strip_one_group(tree)
    if len(t2) == 1:
        body = R.flatten(t2[0], True)
        while body and body[0][0] == "zw" and body[0][1] in ("flag", "ctx"):
            body = body[1:]
        while body and body[-1][0] == "zw" and body[-1][1] in ("flag", "ctx"):
            body = body[:-1]
        lo, hi, _a, fl = R.seq_props(body)
        if not body or fl or any(has_zw(x) for x in body):
            o["whole"] = "views/G1"
        elif hi is not None and lo == hi:
            o["whole"] = "T1"
        else:
            t = seg_tier(body, r["enc"] == "utf8")[0]
            o["whole"] = "T4" if t == "outer" else t
    else:
        o["whole"] = "alt"
    return o


# ---- control C1 ---------------------------------------------------------------------------

C1 = [  # (pattern, flags, expected tier of the chosen landmark or a stage, expected strong)
    (rb"[%+\-.0-9A-Za-z_]+@[a-z]+\.com", "", "T2", True),
    (rb"\w+@example\.com", "", "T2", True),
    (rb"[a-z]{1,8}@example\.com", "", "T2", True),
    (rb"ab[0-9]@x", "", "T1", True),
    (rb"\d+[-.]\d+@", "", "T3", True),
    (rb"\b[a-z]+[.,][a-z]+\(", "", "T3", True),
    (rb"[a-z]+[0-9]+[a-z]*@", "", "T3", True),
    (rb"[a-c][a-z]+@", "", "T4", True),
    (rb"=[a-c][a-z]+@", "", "T3", True),
    (rb"(?:ab)+@", "", "T4", True),
    (rb"[a-z]+xy", "", "T2", False),
    (rb"(a+)\1@", "", "G1", None),
    (rb"(?>a+)@", "", "G1", True),
    (rb"^\w+@", "", "anchored", None),
    (rb"\w+@", "m", "T2", True),
    (rb"\b\w+@", "", "T2", True),
    (rb"\w+\b-x", "", "T4", True),
    (rb"\bat (?:[A-Za-z_$][A-Za-z0-9_$]*\.){2,}[A-Za-z_$][A-Za-z0-9_$]*\(", "", "T3", True),
    (rb"x*[A-Z][A-Z0-9]*@", "", "T4", True),
    (rb"a*\d+@", "", "T3", True),
]


def selftest():
    bad = 0
    for pat, fl, want, strong in C1:
        o = row_of(dict(pop="c1", id=pat.decode(), enc="byte", icase="i" in fl, mline="m" in fl, pat=pat))
        got = o.get("tier", o.get("stage"))
        ok = got == want and (strong is None or o.get("strong") == strong)
        bad += not ok
        print("%s %-40s want %-8s got %-8s strong=%s why=%s" % ("ok " if ok else "BAD", pat.decode(), want, got,
                                                               o.get("strong"), o.get("why", "")))
    print("C1: %d/%d %s" % (len(C1) - bad, len(C1), "PASS" if not bad else "FAIL"))
    return bad == 0


# ---- summary ------------------------------------------------------------------------------

def summarize(rows):
    out = []
    for pop in ("corpus", "bench"):
        rs = [r for r in rows if r["pop"] == pop]
        c = collections.Counter(r["stage"] for r in rs)
        out.append("## %s: %d patterns; stages %s" % (pop, len(rs), dict(sorted(c.items()))))
        lm = [r for r in rs if r["stage"] == "landmark"]
        un = sum(1 for r in rs if r["stage"] not in ("unparsed", "anchored"))
        out.append("unanchored parsed (approximated items excluded): %d; with an inner landmark (non-empty P): %d"
                   % (sum(1 for r in rs if r["stage"] not in ("unparsed", "anchored", "approx")), len(lm)))
        out.append("")
        out.append("| tier | all | composes | + exclusion (T2/T3) / strong arm (T1, T4) | admitted at F=2 | of those, unbounded run | G4: S refers back |")
        out.append("|---|---|---|---|---|---|---|")
        for t in ("T1", "T2", "T3", "T4", "G1"):
            ts = [r for r in lm if r["tier"] == t]
            comp = [r for r in ts if r["comp"]]
            ex = [r for r in comp if (r["excl"] if t in ("T2", "T3") else r["strong"])]
            f2 = [r for r in ex if r["ratio"] >= 2]
            unb = [r for r in f2 if r["unb"]]
            sr = [r for r in f2 if r["srefs"]]
            out.append("| %s | %d | %d | %d | %d | %d | %d |" % (t, len(ts), len(comp), len(ex), len(f2), len(unb), len(sr)))
        st = [r for r in lm if r["tier"] in ("T2", "T3") and r["comp"] and not r["excl"] and r["strong"]]
        out.append("")
        out.append("T2/T3 admitted by the factor-free arm only (exclusion fails): %d" % len(st))
        ne = [r for r in lm if r["tier"] in ("T2", "T3") and not r["strong"]]
        out.append("T2/T3 chain but NO strong arm (falls to T4's gates / handoff): %d" % len(ne))
        why4 = collections.Counter(r["why"].split(";")[0] for r in lm if r["tier"] == "T4")
        out.append("T4 by first reason: %s" % dict(why4.most_common()))
        bad = [r["id"] for r in lm if r.get("chain") == "chain" and r["tier"] not in ("T2", "T3")]
        out.append("C2 cross-check (P's minimal reverse DFA is a chain => a T2/T3 segment tier): %d chain rows, %d violations %s"
                   % (sum(1 for r in lm if r.get("chain") == "chain"), len(bad), bad[:5]))
        for t in ("T2", "T3"):
            ad = [r for r in lm if r["tier"] == t and r["comp"] and r["excl"] and r["ratio"] >= 2]
            out.append("R1 scan edges, %s admitted at F=2 (%d): every loop state of P's reverse DFA scan-shaped today %s"
                       % (t, len(ad), dict(collections.Counter(r.get("sedge") for r in ad))))
        t3x = [r for r in lm if r.get("t3x")]
        out.append("T4 because the start may lie in a non-plain segment ('outer'): %d" % len(t3x))
        wc = collections.Counter(r.get("whole") for r in rs if r["stage"] not in ("unparsed", "anchored", "approx"))
        out.append("whole pattern's reverse walk (from a match END), unanchored parsed: %s" % dict(wc))
        out.append("")
        for t in ("T1", "T2", "T3", "T4"):
            ex = [r for r in lm if r["tier"] == t and r["comp"] and (r["excl"] if t in ("T2", "T3") else r["strong"]) and r["ratio"] >= 2]
            out.append("examples %s (admitted, F>=2): %s" % (t, "; ".join("%s L=%s" % (r["id"], r["L"]) for r in ex[:12])))
        out.append("")
    return "\n".join(out)


def main():
    global SABOTAGE
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sabotage", choices=["chain"])
    a = ap.parse_args()
    SABOTAGE = a.sabotage
    if a.sabotage:
        ok = selftest()
        print("sabotage %s: the selftest %s (it must FAIL)" % (a.sabotage, "PASSED: SABOTAGE UNDETECTED" if ok else "failed: detected"))
        sys.exit(1 if ok else 0)
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    os.makedirs(E["OUT"], exist_ok=True)
    pop = corpus_pop() + bench_pop()
    rows = [row_of(r) for r in pop]
    for r, p in zip(rows, pop):
        r["pat"] = p["pat"].decode("latin-1")
    cols = ["pop", "id", "enc", "stage", "tier", "why", "L", "nbr", "comp", "strong", "excl", "ratio", "unb", "ctx",
            "srefs", "chain", "sedge", "whole", "pat"]
    with gzip.open(os.path.join(E["OUT"], "rows.tsv.gz"), "wt") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(c, "")).replace("\t", " ").replace("\n", " ") for c in cols) + "\n")
    s = summarize(rows)
    open(os.path.join(E["OUT"], "summary.txt"), "w").write(s + "\n")
    print(s)


if __name__ == "__main__":
    main()
