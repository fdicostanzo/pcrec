"""f1.py -- build the island twin of an ALL-BYTE pcrec DFA artifact.

The base artifact must be generated with the DFA's optional machinery off so
its tables are the complete byte automaton (no scan-edge stub states, no
premultiplied cells):

    pcrec -e utf8 -p bb -fno-scan-edge -fno-premul-table -fno-anchored-dfa \
          -fno-prefilter --pattern PAT

The twin's machine is COMPUTED from those tables, not re-derived from the
pattern: for every reachable character-boundary state q and every
non-ASCII character c, delta(q, c) is the byte machine run over c's UTF-8
bytes (grouped by byte-class sequence, so 1.1M code points cost a few dozen
runs); characters whose columns agree over all reachable states are one
ATOM.  An ill-formed byte is BOT, its column the machine's own delta on the
never-valid byte 0xFF.
"""
import re

_ARR = re.compile(r"static const (?:unsigned )?(\w+) (\w+)\[(\d+)\] = \{(.*?)\};", re.S)


def parse_base(path, prefix="bb"):
    txt = open(path).read()
    arrs = {}
    for m in _ARR.finditer(txt):
        arrs[m.group(2)] = [int(x) for x in re.findall(r"-?\d+", m.group(4))]
    mul = {}
    for tag in ("forward", "reverse"):
        mm = re.search(r"%s_%s_step\(.*?return transitions\[s \* (\d+) \+ cl\];" % (prefix, tag), txt, re.S)
        assert mm, "not an indexed (non-premultiplied) table: " + tag
        mul[tag] = int(mm.group(1))
    return arrs, mul


def utf8_groups(cls, reverse):
    """Group all non-ASCII scalar values by their byte-class sequence.
    Returns list of (key, rep_bytes, cps list)."""
    groups = {}
    for lo, hi, n in ((0x80, 0x7FF, 2), (0x800, 0xFFFF, 3), (0x10000, 0x10FFFF, 4)):
        for cp in range(lo, hi + 1):
            if n == 3 and 0xD800 <= cp <= 0xDFFF:
                continue
            if n == 2:
                bs = (0xC0 | (cp >> 6), 0x80 | (cp & 63))
            elif n == 3:
                bs = (0xE0 | (cp >> 12), 0x80 | ((cp >> 6) & 63), 0x80 | (cp & 63))
            else:
                bs = (0xF0 | (cp >> 18), 0x80 | ((cp >> 12) & 63), 0x80 | ((cp >> 6) & 63), 0x80 | (cp & 63))
            seq = bs[::-1] if reverse else bs
            key = (n,) + tuple(cls[b] for b in seq)
            g = groups.get(key)
            if g is None:
                groups[key] = (list(seq), [cp])
            else:
                g[1].append(cp)
    return [(k, v[0], v[1]) for k, v in groups.items()]


def build_dir(arrs, mul, tag, prefix="bb"):
    """One direction.  Returns dict with states, ascii classes, columns."""
    cls = arrs["%s_%s_byte_class" % (prefix, tag)]
    nxt = arrs["%s_%s_next_state" % (prefix, tag)]
    acc = arrs["%s_%s_is_accepting" % (prefix, tag)]
    K = mul[tag]
    reverse = tag == "reverse"
    groups = utf8_groups(cls, reverse)

    def step(q, b):
        return nxt[q * K + cls[b]]

    def run(q, rep):
        for b in rep:
            if q < 0:
                return -1
            q = step(q, b)
        return q

    R = [0]
    seen = {0}
    i = 0
    while i < len(R):
        q = R[i]; i += 1
        cand = [step(q, b) for b in range(128)] + [step(q, 0xFF)]
        cand += [run(q, rep) for (_, rep, _) in groups]
        for t in cand:
            if t >= 0 and t not in seen:
                seen.add(t); R.append(t)
    idx = {q: i for i, q in enumerate(R)}
    return dict(cls=cls, nxt=nxt, acc=acc, K=K, R=R, idx=idx, groups=groups,
                step=step, run=run, reverse=reverse)


def machine(d, keep_in=None):
    """-> (CM args).  keep_in: which atom is 'in' decided by comparing to BOT."""
    from cm import CM
    R, idx, step, run = d["R"], d["idx"], d["step"], d["run"]
    cls = d["cls"]
    # ascii classes, renumbered
    asc_cls = sorted(set(cls[b] for b in range(128)))
    remap = {c: i for i, c in enumerate(asc_cls)}
    nasc = len(asc_cls)
    cls256 = [remap[cls[b]] if b < 128 else nasc for b in range(256)]
    rep_of = {}
    for b in range(128):
        rep_of.setdefault(cls[b], b)
    m = lambda t: (idx[t] if t >= 0 else -1)
    nxt = []
    for q in R:
        row = [m(step(q, rep_of[c])) for c in asc_cls] + ['I']
        nxt.append(row)
    # atoms
    cols = {}
    for (k, rep, cps) in d["groups"]:
        col = tuple(m(run(q, rep)) for q in R)
        cols.setdefault(col, []).append(cps)
    bot = tuple(m(step(q, 0xFF)) for q in R)
    return nxt, cols, bot, asc_cls, cls256


def intervals(cps):
    cps = sorted(cps)
    out = []
    for c in cps:
        if out and out[-1][1] + 1 == c:
            out[-1] = (out[-1][0], c)
        else:
            out.append((c, c))
    return out


def build_twin(basepath, prefix="bb"):
    """-> (fwd CM, rev CM, in_intervals, info)"""
    from cm import CM
    arrs, mul = parse_base(basepath, prefix)
    F = build_dir(arrs, mul, "forward", prefix)
    Rv = build_dir(arrs, mul, "reverse", prefix)
    res = {}
    for name, D in (("f", F), ("r", Rv)):
        nxt, cols, bot, asc_cls, cls256 = machine(D)
        nonbot = [c for c in cols if c != bot]
        botcols = [c for c in cols if c == bot]
        if len(nonbot) != 1 or len(cols) > 2:
            raise SystemExit("unsupported atom structure in %s: %d columns" % (name, len(cols)))
        incol = nonbot[0]
        res[name] = dict(D=D, nxt=nxt, incol=incol, bot=bot, asc_cls=asc_cls, cls256=cls256,
                         in_cps=cols[incol], has_out=bool(botcols))
    ivF = intervals([c for g in res["f"]["in_cps"] for c in g])
    ivR = intervals([c for g in res["r"]["in_cps"] for c in g])
    assert ivF == ivR, "forward and reverse machines disagree on the set"
    def mk(name, tag):
        r = res[name]; D = r["D"]
        nst = len(D["R"])
        tgt = [[r["bot"][i], r["incol"][i], r["bot"][i]] for i in range(nst)]
        # v: 0 = out (== BOT column), 1 = in, 2 = BOT
        acc = [D["acc"][q] for q in D["R"]]
        cb = None
        if name == "f":
            cb = arrs["%s_can_begin_match" % prefix] if ("%s_can_begin_match" % prefix) in arrs else None
        return CM(tag, nst, r["cls256"], len(r["asc_cls"]), r["nxt"], tgt, acc=acc,
                  can_begin=cb)
    info = dict(fwd_states=len(res["f"]["D"]["R"]), rev_states=len(res["r"]["D"]["R"]),
                base_fwd_states=len(arrs["bb_forward_is_accepting"]),
                base_rev_states=len(arrs["bb_reverse_is_accepting"]),
                nintervals=len(ivF), has_out=res["f"]["has_out"])
    return mk("f", "fwd"), mk("r", "rev"), ivF, info
