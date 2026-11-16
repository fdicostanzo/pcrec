# fixind drill (critic round predspec20, lens fixind). Read-only; writes nothing.
# Engines: absimpact_check.py's prefix (libpcre2-8 ctypes + Python re, groups() asserts both agree), exec'd verbatim
# up to its first table. Run: timeout 300 python3 -I fixind_drill.py
import os, re, itertools, sys, ctypes
EV = "/var/tmp/pcrec-pcrec/scratch/crit-predspec20/evidence"
src = open(os.path.join(EV, "absimpact_check.py")).read()
exec(src[:src.index("def part(")], globals())


def dom(p, subjects, lab):
    """VALUES: run p over the population, collect lab's texts in matches (both engines via groups())"""
    out = set()
    for s in subjects:
        g = groups(p, s, [lab])
        if g is not None and g[lab] is not None:
            out.add(g[lab])
    return out


num = lambda v: int(v)
# ---------------------------------------------------------------------------------------------------------------
print("\n(D1) label-twice's two offered spellings, `(h?: A) & (h?: B)` vs `(h?: A & B)`, A = <5, B = >5")
for P, subj in ((r"(?<h>\d)?x", ["x"] + [d + "x" for d in D]),
                (r"(?:(?<h>\d),)*", ["".join(d + "," for d in c) for k in range(3) for c in itertools.product(D, repeat=k)])):
    pop = subj
    DOM = dom(P, pop, "h")
    A = lambda v: num(v) < 5
    B = lambda v: num(v) > 5
    nd, ex = 0, []
    for s in pop:
        # passes: list of h values per pass (None = absent); set-once: one pass
        if P.startswith("(?<h>"):
            g = groups(P, s, ["h"])
            passes = [g["h"]]
        else:
            assert whole(P, s)
            passes = [x for x in s.split(",") if x] or [None]   # zero passes: one tuple, h absent
        def marked(S):
            return all((S(v) if v is not None else any(S(d) for d in DOM)) for v in passes)
        sep = marked(A) and marked(B)
        one = marked(lambda v: A(v) and B(v))
        if sep != one:
            nd += 1; ex.append(repr(s))
    print("   %-18s DOM(h) %s: differ on %d of %d (%s): sep HOLDS, one FAILS" % (P, "".join(sorted(DOM)), nd, len(pop), ", ".join(ex)))
    # ENGINE-RUN: the set-once answers as regexes from the stated sets
    if P.startswith("(?<h>"):
        for s in pop:
            check("D1 sep", r"(?:[0-4]x|x)" if False else r"x", s, s == "x") if False else None
        for s in pop:
            g = groups(P, s, ["h"])
            want_sep = g["h"] is None or (A(g["h"]) and B(g["h"]))
            check("D1 sep engine", r"x", s, want_sep)          # sep holds: absent only (no h is <5 and >5)
            check("D1 one engine", r"(?!)", s, False)           # one: empty set, holds nowhere

# ---------------------------------------------------------------------------------------------------------------
print("\n(D2) \"every hit, possibly none\" vs `(g?: \"a\")`, occurrences(/(?<g>a)?b/), spans over {a,b} length 0-6")
SUB = ["".join(c) for k in range(7) for c in itertools.product("ab", repeat=k)]
HP = r"(?<g>a)?b"
hc = re.compile(py(HP))
def hits(s):
    # leftmost non-overlapping hits along the lazy-gap body = finditer; PCRE2 cross-check by the body's whole match
    return [m.group("g") for m in hc.finditer(s)]
DOMg = set()
for s in SUB:
    for v in hits(s):
        if v is not None:
            DOMg.add(v)
nat_vs_mark, none_vs_nat = 0, 0
for s in SUB:
    hs = hits(s)
    natural = all(v == "a" for v in hs)                         # every hit's g is "a", possibly no hit
    mark = all((v == "a") if v is not None else ("a" in DOMg) for v in hs) if hs else ("a" in DOMg)
    none_ = not any((v != "a") if v is not None else True for v in hs)     # occurs.none(!(g: "a")): unmarked ! holds on absent
    nat_vs_mark += natural != mark
    none_vs_nat += none_ != natural
    check("D2 natural", r"(?!b)(?![ab]*bb)[ab]*", s, natural)   # ENGINE-RUN: every b preceded by a
    check("D2 mark", r"[ab]*", s, mark)                        # ENGINE-RUN: always
print("   DOM(g) = %s; natural vs (g?: \"a\"): %d of %d differ (e.g. 'b', 'abb'); occurs.none(!(g: \"a\")) vs natural: %d"
      % (sorted(DOMg), nat_vs_mark, len(SUB), none_vs_nat))

# ---------------------------------------------------------------------------------------------------------------
print("\n(D3) DOM over the rx text vs over the narrowed operand; t2m := t2 & (m?: padded(<60)) vs t2x (minutes [0-5]\\d)")
T2 = r"(?<h>\d{1,2})(?::(?<m>\d\d))?"
T2X = r"(?<h>\d{1,2})(?::(?<m>[0-5]\d))?"
SUBT = [h + ("" if m is None else ":" + m) for h in [str(i) for i in range(10)] + ["%02d" % i for i in range(100)]
        for m in [None] + ["%02d" % i for i in range(100)]]
padded_lt60 = lambda v: re.fullmatch(r"0*(?:[0-9]|[1-5][0-9])", v) is not None   # /0*${<60}/
padded_ge60 = lambda v: re.fullmatch(r"0*(?:[6-9][0-9]|[1-9][0-9]{2,})", v) is not None
DOMraw = dom(T2, SUBT, "m")
same, n2m, n2x = 0, 0, 0
t2m_set = {}
for s in SUBT:
    g = groups(T2, s, ["h", "m"])
    m_ok = g is not None and (g["m"] is None or padded_lt60(g["m"]))   # (m?: <60): absent -> some DOM value <60 (yes)
    t2m_set[s] = g if m_ok else None
    gx = groups(T2X, s, ["h", "m"])
    same += (t2m_set[s] == gx)
DOMnarrow = {g["m"] for g in t2m_set.values() if g and g["m"] is not None}
DOMx = dom(T2X, SUBT, "m")
print("   t2m and t2x: same match and labels on %d of %d subjects; DOM(m): t2 text %d values, t2m narrowed %d, t2x %d"
      % (same, len(SUBT), len(DOMraw), len(DOMnarrow), len(DOMx)))
diff = 0
for s in SUBT:
    g = t2m_set[s]
    if g is None:
        continue
    a = padded_ge60(g["m"]) if g["m"] is not None else any(padded_ge60(d) for d in DOMraw)    # DOM read before narrowing
    b = padded_ge60(g["m"]) if g["m"] is not None else any(padded_ge60(d) for d in DOMx)      # t2x's DOM
    diff += a != b
print("   (m?: padded(>=60)): t2m (DOM from t2's rx) vs t2x: %d of %d matching subjects differ (every minute-less one: `9` HOLDS vs FAILS)"
      % (diff, sum(1 for v in t2m_set.values() if v)))

# ---------------------------------------------------------------------------------------------------------------
print("\n(D4) a mark written for a beside `$a` on the value side: /(?<a>\\d)?-(?<b>\\d)/")
PA = r"(?<a>\d)?-(?<b>\d)"
SUBA = ["%s-%s" % (a, b) for a in [""] + D for b in D]
DOMa = dom(PA, SUBA, "a")
for name, Sa in (("(a?: <3, b: >$a)", lambda v: num(v) < 3), ("(a?: >7, b: >$a)", lambda v: num(v) > 7)):
    res = {"no-reach": 0, "shared": 0, "independent": 0}
    split = []
    for s in SUBA:
        g = groups(PA, s, ["a", "b"])
        b = num(g["b"])
        if g["a"] is not None:
            v = num(g["a"]); r = (Sa(g["a"]), Sa(g["a"]) and b > v, Sa(g["a"]) and b > v)
            r = (Sa(g["a"]) and b > v,) * 3
        else:
            r = (False,                                                     # $a empty (e2), entry a? holds
                 any(Sa(d) and b > num(d) for d in DOMa),                   # one witness for a and $a
                 any(Sa(d) for d in DOMa) and any(b > num(d) for d in DOMa))  # a witness each
        for k, x in zip(("no-reach", "shared", "independent"), r):
            res[k] += x
        if len(set(r)) > 1:
            split.append("%s:%s" % (s, "/".join("H" if x else "F" for x in r)))
    print("   %-18s holds: no-reach %d, shared witness %d, independent %d of %d; the readings split on %d: %s"
          % (name, res["no-reach"], res["shared"], res["independent"], len(SUBA), len(split), " ".join(split[:4])))

print("\n(D5) 'the empty list passes, an item without minutes fails, every item in R', lists of /(?:(?<h>\\d+)(?::(?<m>\\d\\d))?,)*/")
POP = r"(?:(?<h>\d+)(?::(?<m>\d\d))?,)*"
ITEMS = [(h, m) for h in ("3", "12") for m in (None, "15", "45", "05", "99")]
SUBO = ["".join("%s%s," % (h, "" if m is None else ":" + m) for h, m in its) for k in range(4) for its in itertools.product(ITEMS, repeat=k)]
DOMm = set()
for s in SUBO:
    assert whole(POP, s)
for h, m in ITEMS:
    if m is not None:
        DOMm.add(m)
DOMm = {"%02d" % i for i in range(100)}     # m's VALUES over the pattern (any two digits can be a minute in some list)
for rname, Rm in (("R = (<10, <30)", lambda v: num(v) < 30), ("R' = (<10, padded(<100))", lambda v: num(v) < 100)):
    c = {"marked": 0, "plain-not": 0}
    ex = []
    for s in SUBO:
        its = [x for x in s.split(",") if x]
        ps = [(x.split(":")[0], x.split(":")[1] if ":" in x else None) for x in its]
        inR = lambda h, m: num(h) < 10 and Rm(m)
        want = all(m is not None and inR(h, m) for h, m in ps)
        marked = not any((not inR(h, m)) if m is not None else any(not inR(h, d) for d in DOMm) for h, m in ps)
        plainnot = not any((m is None) or not inR(h, m) for h, m in ps)
        c["marked"] += marked != want; c["plain-not"] += plainnot != want
        if marked != want and len(ex) < 3: ex.append(repr(s))
    print("   %-26s vs the wanted answers over %d lists: occurs.none(((h, m?): !R)) differs on %d (%s); occurs.none(!((h, m): R)) on %d"
          % (rname, len(SUBO), c["marked"], ", ".join(ex), c["plain-not"]))

print("\n(D6) an array alternative lacking the label: [x = /\\d/, y = /[a-z]/] & (x?: /[0-5]/) read as the rx /(?<x>\\d)|(?<y>[a-z])/")
PX = r"(?<x>\d)|(?<y>[a-z])"
SUBX = D + [chr(c) for c in range(97, 123)]
DOMx6 = dom(PX, SUBX, "x")
keep = drop = unm = 0
for s in SUBX:
    g = groups(PX, s, ["x", "y"])
    v = g["x"]
    inS = lambda t: re.fullmatch("[0-5]", t) is not None
    unm += (v is not None and inS(v))
    keep += (inS(v) if v is not None else any(inS(d) for d in DOMx6))       # absent (an alternative not taken), marked
    drop += (v is not None and inS(v))                                      # the y entry DROPPED structurally (l.1897)
    check("D6 rx marked", r"[0-5a-z]", s, (inS(v) if v is not None else any(inS(d) for d in DOMx6)))
print("   of %d subjects: unmarked holds on %d; marked, as the rx's absent label: %d; marked, with the entry DROPPED: %d"
      % (len(SUBX), unm, keep, drop))

print("\nTOTAL engine-run cases %d, differ %d, probes %d, engine disagreements %d" % (TOT["cases"], TOT["differ"], TOT["probes"], DIS[0]))
