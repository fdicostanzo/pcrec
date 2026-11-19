#!/usr/bin/env python3
# Lane predspec28 (2026-11-18): the evidence of docs/design/predicates_draft.md REVISION 28 (the fold of the owner's
# rulings of the evening of 2026-11-18).  DESIGN EVIDENCE ONLY; rules nothing.  Standalone: the helpers are COPIED
# from predspec271_model.py (not imported; predspec271_evidence/ stays as committed).
#
# PARTS (the record entry each re-runs, COND-FAMILY 2026-11-18 evening):
#   PW  padded: his wrap `padded($y + 1)` (runs A, B, C) under both domains, EXACT (a callout model; the manager's
#       scratch padwrap.py used a lookahead approximation for `& /\d{n}/`); `padded(rx, n)`'s two-case macro against
#       "zero-filled to at least n" (minimum); the hole program; the three bounds; the withdrawn EXACT leaning shown.
#   NW  number-domain m1: does numeral-width's WIDTH KEPT part from CANONICAL on canonical operands? (`+ 1`, `- 1`)
#   FL  hole-flags / flags-propagate: i, m, s, x; the override; a trailing-flag binding; PART J's move; the read.
#   AC  any_case(rx) := /(?i:${rx})/ under propagation: plain arguments and a filter-role argument (two readings).
#   UN  unset-in-hole: the never-matching rx `(?!)`; R.1.15 (5) under the ruled reading.
#   CN  construction-line: the enumerate line as RULE-AS-CODE (a small enumerator; its SETS checked against python
#       `re` by brute force, its ORDER is the rule); the manager's hand-worked table RUN; lift-order by consequence.
#   HR  hole-reads-capture: the label vs `\k<y>` (BL1 re-run); the label-only group's spellings in libpcre2.
#   SN  same-name-twice: libpcre2 with and without `(?J)`; the numbered form.
#   DW  dollar-warning: `/(?<x>\d+)-/ & ($x & <5)` never holds; `(x: <5)` does.
#   TT  the TYPE TABLE of rev 28 as RULE-AS-CODE (the changed rows T8, T9, T10, T13, T20 and the composition).
#
# CONTROLS: libpcre2-8 through ../rxmodel_evidence/pcre2h.py (run, never read: D181); python `re`; direct python
# semantic functions.  The label is predspec261's marker model.
#
# Run (W = the worktree; from $PCREC_TMPDIR/scratch/predspec28; one process, seconds):
#   timeout 900 python3 -I -B W/docs/dev/lanes/predspec28_evidence/predspec28_model.py > fwd.out
#   PREDSPEC28_SABOTAGE=s1,.. : deliberately wrong rules; each must fail its check (ONE sabotage per check):
#     s1  PW: the canonical domain admits padded reads (`0099` read as 99);
#     s2  PW: the macro's second case without its length bound (`rx` alone: a short value matched unpadded too);
#     s3  PW: the hole program under EXACT (the withdrawn leaning) instead of MINIMUM;
#     s4  PW: `<=9999` on the padded text judged on the parsed integer (not §2.4's canonical numerals);
#     s5  NW: WIDTH KEPT modelled as canonical for `-` (the difference hidden);
#     s6  FL: no propagation (a hole keeps its own flags: the reversed NO INHERITED FLAGS);
#     s7  AC: the plain-argument body under no propagation;
#     s8  UN: the never-matching constant spelled `(?:)` (the EMPTY string: the naming trap);
#     s9  CN: `\d` enumerated in descending order (enumerate's order not codepoint order);
#     s10 CN: enumerate accepts an infinite rx by truncating it (no refusal);
#     s11 HR: the hole reads the capture (not the label);
#     s12 SN: under `(?J)` the backreference modelled as the LAST set group;
#     s13 DW: `$x & <5` as an `&` operand modelled as the condition `(x: <5)`;
#     s14 TT: a single-value function on a FINITE rx classed UNDER CONSTRUCTION (rev 27.1's line, before the ruling).
import os, sys, re, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rxmodel_evidence"))
import pcre2h as P                                           # noqa: E402

_sv = os.environ.get("PREDSPEC28_SABOTAGE", "")
SABS = set("s%d" % i for i in range(1, 15)) if _sv == "1" else set(x for x in _sv.split(",") if x)
def sab(k): return k in SABS

CHECKS = []
def check(name, ok):
    CHECKS.append((name, bool(ok)))
    return "OK" if ok else "FAILED"

NOTEMPTY_ATSTART = 0x00000008


def pool(alpha, n=5):
    out = [""]
    for k in range(1, n + 1):
        out += ["".join(t) for t in itertools.product(alpha, repeat=k)]
    return out


def W(rx, s): return rx.match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)
def S(rx, s): return rx.match(s, 0)


def F(rx, s):
    """PCRE2's global loop (R.1.2)"""
    out, pos, ne = [], 0, False
    while pos <= len(s):
        r = rx.match(s, pos, (NOTEMPTY_ATSTART | P.PCRE2_ANCHORED) if ne else 0)
        if r is None:
            if ne:
                ne = False
                pos += 1
                continue
            break
        out.append(r)
        ne = r[1] == r[0]
        pos = r[1]
    return out


def fW(rx, s): return "FAILS" if W(rx, s) is None else "HOLDS"
def fS(rx, s):
    r = S(rx, s)
    return "FAILS" if r is None else "`%s`@%d" % (s[r[0]:r[1]], r[0])
def fF(rx, s): return "[" + ", ".join("`%s`@%d" % (s[a:b], a) for a, b, _ in F(rx, s)) + "]"


def row(rx, s, mode):
    if mode == "W":
        return W(rx, s) is not None
    if mode == "S":
        r = S(rx, s)
        return None if r is None else (r[0], r[1])
    return tuple((a, b) for a, b, _ in F(rx, s))


def diff3(r1, r2, texts):
    out, first = [], None
    for m in "WSF":
        n = 0
        for s in texts:
            if row(r1, s, m) != row(r2, s, m):
                n += 1
                first = first or (m, s)
        out.append(n)
    return out, first


def show(rx, w, s_, f_):
    return "WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % (w.replace("\n", "\\n"), fW(rx, w), s_, fS(rx, s_), f_, fF(rx, f_))


def canon(v):
    return v is not None and re.fullmatch(r"0|[1-9]\d*", v) is not None


def plus(y, k, dom="canonical"):
    """`$y + k` on one string: dom canonical = THE NUMBER DOMAIN (RULED number-domain: canonical); parsed = any digit
    string read as an integer (the candidate not taken).  None = yields nothing."""
    if y is None:
        return None
    if dom == "canonical" and not sab("s1"):
        ok = canon(y)
    else:
        ok = re.fullmatch(r"\d+", y) is not None
    if not ok:
        return None
    r = int(y) + k
    return str(r) if r >= 0 else None


VQ = r'(?<v>[\s\S]*?)(?C"eq")'      # a value hole: a lazy capture accepted only when the predicate holds on it


def hole(pre, pred, post=''):
    """pred(c, v) -> True when the hole's set holds v (the label read where the hole stands)"""
    return P.Pcre(pre + VQ + post, {"eq": lambda c: pred(c, c.get("v")) is True})


def zfill_min(v, n):
    """padded-width RULED minimum: zeros reach out to n characters; a value n or longer is matched unpadded"""
    return "0" * max(0, n - len(v)) + v


print("predspec28 evidence; libpcre2-8 %s%s" % (P.version(), " ; SABOTAGE %s" % ",".join(sorted(SABS, key=lambda x: int(x[1:]))) if SABS else ""))
for line, ok in P.selfcheck():
    print("selfcheck: %s ; %s" % (line, check("selfcheck " + line[:30], ok)))

# =====================================================================================================================
print("\n== PART PW: padded (number-domain, padded-width entries): EXACT models (no lookahead approximation)")
def padset(L, v):                     # `padded(L)` = /0*${L}/ (RULED 2026-11-15): v in 0* L
    return L is not None and v is not None and re.fullmatch(r"0*" + re.escape(L), v) is not None
progA = {d: hole(r'(?<y>\d{4})-', lambda c, v, d=d: padset(plus(c.get("y"), 1, d), v)) for d in ("canonical", "parsed")}
progB = {d: hole(r'(?<y>\d{4})-', lambda c, v, d=d: padset(plus(c.get("y"), 1, d), v) and re.fullmatch(r"\d{4}", v) is not None) for d in ("canonical", "parsed")}
progC = {d: hole(r'0*(?<y>[1-9]\d*)-', lambda c, v, d=d: padset(plus(c.get("y"), 1, d), v) and re.fullmatch(r"\d\d", v) is not None) for d in ("canonical", "parsed")}
resA, resB, resC = {}, {}, {}
for d in ("canonical", "parsed"):
    resA[d] = [fW(progA[d], t) for t in ("2025-2026", "2025-02026", "0099-0100", "0099-100")]
    print("PW A `/(?<y>\\d{4})-${padded($y + 1)}/` [%s] WHOLE 2025-2026 %s, 2025-02026 %s, 0099-0100 %s, 0099-100 %s ; SEARCHED `0099-0100 2025-2026` %s ; FIND-ALL `0099-0100 2025-2026 0100-0101` %s"
          % ((d,) + tuple(resA[d]) + (fS(progA[d], "0099-0100 2025-2026"), fF(progA[d], "0099-0100 2025-2026 0100-0101"))))
    resB[d] = [fW(progB[d], t) for t in ("2025-2026", "2025-02026", "0099-0100", "0099-100", "9999-10000")]
    print("PW B `/(?<y>\\d{4})-${padded($y + 1) & /\\d{4}/}/` [%s] WHOLE 2025-2026 %s, 2025-02026 %s, 0099-0100 %s, 0099-100 %s, 9999-10000 %s ; SEARCHED `0099-0100 2025-2026` %s ; FIND-ALL `0099-0100 2025-2026 0100-0101` %s"
          % ((d,) + tuple(resB[d]) + (fS(progB[d], "0099-0100 2025-2026"), fF(progB[d], "0099-0100 2025-2026 0100-0101"))))
    resC[d] = [fW(progC[d], t) for t in ("05-06", "09-10", "05-6", "99-100")]
    print("PW C `/0*(?<y>[1-9]\\d*)-${padded($y + 1) & /\\d\\d/}/` [%s] WHOLE 05-06 %s, 09-10 %s, 05-6 %s, 99-100 %s ; SEARCHED `12-14 05-06` %s ; FIND-ALL `05-06 09-10 11-13 01-02` %s"
          % ((d,) + tuple(resC[d]) + (fS(progC[d], "12-14 05-06"), fF(progC[d], "05-06 09-10 11-13 01-02"))))
dCC, _ = diff3(progC["canonical"], progC["parsed"], pool("0159-", 5))
print("PW C canonical vs parsed over %d texts (`0159-`, length <= 5): %d / %d / %d" % (len(pool("0159-", 5)), dCC[0], dCC[1], dCC[2]))
print("PW the record's runs (A, B, C) %s" % check("PW A B C as recorded, both domains",
      resA["canonical"] == ["HOLDS", "HOLDS", "FAILS", "FAILS"] and resA["parsed"] == ["HOLDS"] * 4
      and resB["canonical"] == ["HOLDS", "FAILS", "FAILS", "FAILS", "FAILS"] and resB["parsed"] == ["HOLDS", "FAILS", "HOLDS", "FAILS", "FAILS"]
      and resC["canonical"] == resC["parsed"] == ["HOLDS", "HOLDS", "FAILS", "FAILS"] and dCC == [0, 0, 0]))

# the two-case macro `padded(rx, n) := (/0*${rx}/ & /(?s:.){${n}}/) | (rx & /(?s:.){${n},}/)` against the definition
def macro(members, n, t):
    alt = "(?:" + "|".join(re.escape(m) for m in members) + ")"
    a = re.fullmatch(r"0*" + alt, t) is not None and re.fullmatch(r"(?s:.){%d}" % n, t) is not None
    b = re.fullmatch(alt, t) is not None and (sab("s2") or re.fullmatch(r"(?s:.){%d,}" % n, t) is not None)
    return a or b
def defn(members, n, t):
    return any(t == zfill_min(m, n) for m in members)
def cands(v, n):
    z = zfill_min(v, n)
    return {v, z, "0" + z, v.zfill(n + 1), z[1:], "00" + v}
nchk = ndiff = 0
vals = [str(i) for i in range(12000)] + ["99999", "100000", "123456"]
for v in vals:
    for t in cands(v, 4):
        nchk += 1
        ndiff += macro([v], 4, t) != defn([v], 4, t)
print("PW macro vs \"zero-filled to at least 4\": %d values (0..11,999, 99999, 100000, 123456), up to six candidate texts each (v, filled, one zero more, filled to 5, one char less, `00` + v): %d checks, %d differ"
      % (len(vals), nchk, ndiff))
multi = [["7", "123", "12345"], ["007", "5"], ["0", "00"], ["123456", "42"], ["abc", "x"]]
mp = pool("0123457", 6)
md = {}
for ms in multi:
    md[tuple(ms)] = sum(1 for t in mp if macro(ms, 4, t) != defn(ms, 4, t))
print("PW macro vs definition, an rx of SEVERAL strings, over %d texts (`0123457`, length <= 6) + the members' own fills: %s"
      % (len(mp), " ; ".join("%s %d" % ("|".join(k), n) for k, n in md.items())))
for ms in multi:
    extra = [zfill_min(m, 4) for m in ms] + ms + ["0" + zfill_min(m, 4) for m in ms]
    md[tuple(ms)] += sum(1 for t in extra if macro(ms, 4, t) != defn(ms, 4, t))
print("PW %s" % check("PW two-case macro = minimum", ndiff == 0 and all(n == 0 for n in md.values())))
print("PW what each member gives at n = 4: %s" % " ; ".join("%s -> %s" % ("|".join(ms), "|".join(sorted({zfill_min(m, 4) for m in ms}))) for ms in multi))

# the hole program `/(?<y>\d+)-${padded($y + 1, 4)}/` under MINIMUM (RULED) and EXACT (the withdrawn leaning)
def pw_min(c, v):
    L = plus(c.get("y"), 1)
    return L is not None and v is not None and (macro([L], 4, v) if not sab("s3") else (len(L) <= 4 and v == L.zfill(4)))
def pw_exact(c, v):
    L = plus(c.get("y"), 1)
    return L is not None and v is not None and len(L) <= 4 and v == L.zfill(4)
hmin = hole(r'(?<y>\d+)-', pw_min); hexa = hole(r'(?<y>\d+)-', pw_exact)
cases = ("42-0043", "42-43", "9999-10000", "2025-2026")
rmin = [fW(hmin, t) for t in cases]; rexa = [fW(hexa, t) for t in cases]
print("PW `/(?<y>\\d+)-${padded($y + 1, 4)}/` MINIMUM (RULED): %s ; SEARCHED `9999-10000 42-0043` %s ; FIND-ALL `9999-10000 42-0043 7-0008` %s"
      % (", ".join("%s %s" % x for x in zip(cases, rmin)), fS(hmin, "9999-10000 42-0043"), fF(hmin, "9999-10000 42-0043 7-0008")))
print("PW the same, EXACT (the manager's withdrawn leaning): %s ; SEARCHED %s ; FIND-ALL %s"
      % (", ".join("%s %s" % x for x in zip(cases, rexa)), fS(hexa, "9999-10000 42-0043"), fF(hexa, "9999-10000 42-0043 7-0008")))
print("PW %s" % check("PW minimum hole program", rmin == ["HOLDS", "FAILS", "HOLDS", "HOLDS"] and rexa == ["HOLDS", "FAILS", "FAILS", "HOLDS"]))

# the three bounds on a minimum-width result (his observations; none ruled)
def le9999(t):                         # `<=9999` under THE NUMBER DOMAIN (RULED canonical): a canonical numeral <= 9999
    if sab("s4"):
        return re.fullmatch(r"\d+", t) is not None and int(t) <= 9999
    return canon(t) and int(t) <= 9999
bnd = []
for val in ("43", "2026", "10000"):
    p = zfill_min(val, 4)
    img = p[-4:]                                                    # right(padded(v, 4), 4): the IMAGE
    flt = p if re.fullmatch(r"\d{4}", p) else None                  # padded(v, 4) & /\d{4}/: the FILTER
    pre = zfill_min(val, 4) if le9999(val) else None                # padded(v & <=9999, 4): on the value
    post = p if le9999(p) else None                                 # padded(v, 4) & <=9999: on the padded text
    bnd.append((val, img, flt, pre, post))
    print("PW bounds on value %s: rightmost-4 image `%s` ; `& /\\d{4}/` %s ; `<=9999` on the value %s ; `<=9999` on the padded text %s"
          % (val, img, flt or "nothing", pre or "nothing", post or "nothing"))
print("PW %s" % check("PW bounds", bnd == [("43", "0043", "0043", "0043", None), ("2026", "2026", "2026", "2026", "2026"), ("10000", "0000", None, None, None)]))

# =====================================================================================================================
print("\n== PART NW: number-domain m1: numeral-width's two candidates on CANONICAL operands")
def width_kept(y, k):
    r = plus(y, k)
    if r is None:
        return None
    if sab("s5") and k < 0:
        return r
    return r.zfill(len(y))
nd = {}
for k in (1, -1):
    ys = [str(i) for i in range(0 if k > 0 else 1, 10000)]
    dif = [y for y in ys if plus(y, k) != width_kept(y, k)]
    nd[k] = dif
    print("NW `$y %s 1` over canonical y %s..9999: canonical vs WIDTH KEPT differ on %d (first %s)" % ("+" if k > 0 else "-", ys[0], len(dif), dif[:3]))
hc = hole(r'(?<y>\d+)-', lambda c, v: v == plus(c.get("y"), -1)); hw = hole(r'(?<y>\d+)-', lambda c, v: v == width_kept(c.get("y"), -1))
print("NW `/(?<y>\\d+)-${$y - 1}/` CANONICAL: WHOLE 10-9 %s, 10-09 %s ; SEARCHED `10-09 10-9` %s ; FIND-ALL `10-9 100-99 100-099` %s"
      % (fW(hc, "10-9"), fW(hc, "10-09"), fS(hc, "10-09 10-9"), fF(hc, "10-9 100-99 100-099")))
print("NW the same, WIDTH KEPT: WHOLE 10-9 %s, 10-09 %s ; SEARCHED `10-09 10-9` %s ; FIND-ALL `10-9 100-99 100-099` %s"
      % (fW(hw, "10-9"), fW(hw, "10-09"), fS(hw, "10-09 10-9"), fF(hw, "10-9 100-99 100-099")))
print("NW %s" % check("NW the candidates part on canonical operands under `-`", nd[1] == [] and len(nd[-1]) > 0))

# =====================================================================================================================
print("\n== PART FL: hole-flags + flags-propagate (RULED): what is inserted STARTS with the flags at the hole; its own written flags win")
def ins(x):                            # a hole: the inserted rx in a non-capturing group (hole-reading)
    return "(?:%s)" % x if not sab("s6") else "(?^:%s)" % x   # s6: (?^) resets to no flags: no propagation
def ins_own(x, flags):                 # a binding with flags written by a trailing modifier, `/x/i` = `(?i:x)`
    return ins("(?%s:%s)" % (flags, x))
fl = []
pi = P.Pcre(r'(?i)id-' + ins("blah")); pn = P.Pcre(r'(?i)id-(?-i:blah)')
print("FL i  PROPAGATE `/(?i)id-${/blah/}/`: %s" % show(pi, "id-BLAH", "x ID-BLAH", "id-blah ID-BLAH Id-blah"))
print("FL i  (no propagation, the reversed rule, for the record): %s" % show(pn, "id-BLAH", "x ID-BLAH", "id-blah ID-BLAH Id-blah"))
fl.append(W(pi, "id-BLAH") is not None)
for desc, rx in (('`/(?i)${"blah"}/`', r'(?i)' + ins("blah")), ('`/(?i)${/blah/}/`', r'(?i)' + ins("blah"))):
    p = P.Pcre(rx)
    print("FL i  %s: %s" % (desc, show(p, "BLAH", "x BLAH", "blah BLAH Blah")))
    fl.append(W(p, "BLAH") is not None)
po = P.Pcre(r'(?i)' + ins("(?-i)blah"))
print("FL override `/(?i)${/(?-i)blah/}/` (the record's hand-worked case, RUN): %s" % show(po, "BLAH", "BLAH blah", "blah BLAH Blah blah"))
fl += [W(po, "BLAH") is None, W(po, "blah") is not None]
pt = P.Pcre(r'x' + ins_own("blah", "i"))
print("FL a binding `q := /blah/i` in a CASEFUL hole `/x${q}/`: %s" % show(pt, "xBLAH", "XBLAH xBlah", "xblah XBLAH xBLAH"))
fl += [W(pt, "xBLAH") is not None, W(pt, "XBLAH") is None]
pm = P.Pcre(r'(?m)a\n' + ins("^x")); pmn = P.Pcre(r'(?m)a\n(?-m:^x)')
print("FL m  `/(?m)a\\n${/^x/}/`: propagate WHOLE `a\\nx` %s ; no propagation %s" % (fW(pm, "a\nx"), fW(pmn, "a\nx")))
ps = P.Pcre(r'(?s)a' + ins(".") + 'b'); psn = P.Pcre(r'(?s)a(?-s:.)b')
print("FL s  `/(?s)a${/./}b/`: propagate WHOLE `a\\nb` %s ; no propagation %s" % (fW(ps, "a\nb"), fW(psn, "a\nb")))
px = P.Pcre(r'(?x)' + ins("a b")); pxn = P.Pcre(r'(?x)(?-x:a b)')
print("FL x  `/(?x)${/a b/}/`: propagate WHOLE `ab` %s, `a b` %s ; no propagation `ab` %s, `a b` %s" % (fW(px, "ab"), fW(px, "a b"), fW(pxn, "ab"), fW(pxn, "a b")))
fl += [W(pm, "a\nx") is not None, W(pmn, "a\nx") is None, W(ps, "a\nb") is not None, W(psn, "a\nb") is None,
       W(px, "ab") is not None, W(px, "a b") is None, W(pxn, "a b") is not None]
pj = P.Pcre(r'(?i)(?<y>a)-' + ins("a")); pjo = P.Pcre(r'(?i)(?<y>a)-(?-i:a)')
print("FL PART J MOVES `/(?i)(?<y>a)-${q}/`, q := /a/ (rev 28): %s" % show(pj, "a-A", "x a-A", "a-A a-a A-a"))
print("FL PART J as rev 27.1 printed it (own flags):         %s" % show(pjo, "a-A", "x a-A", "a-A a-a A-a"))
hm = hole(r'(?i)(?<y>a)-', lambda c, v: c.get("y") is not None and v.casefold() == c.get("y").casefold())
kref = P.Pcre(r'(?i)(?<y>a)-\k<y>')
dj, _ = diff3(hm, kref, pool("aA-x", 5)); dqj, _ = diff3(pj, hm, pool("aA-x", 5))
print("FL the read `${$y}` at the same hole (nothing written: the options at the hole) vs `\\k<y>` %d / %d / %d ; vs the binding `${q}` %d / %d / %d of %d (`aA-x`)"
      % (dj[0], dj[1], dj[2], dqj[0], dqj[1], dqj[2], len(pool("aA-x", 5))))
okpy = re.fullmatch(r'(?i)id-(?:blah)', "id-BLAH") is not None and re.fullmatch(r'(?i)(?:(?-i:blah))', "BLAH") is None
print("FL python `re` agrees on the i cases (propagate HOLDS, override FAILS on BLAH): %s" % okpy)
fl += [W(pj, "a-A") is not None, W(pjo, "a-A") is None, dj == [0, 0, 0], dqj == [0, 0, 0], okpy]
print("FL %s" % check("FL propagation with override, every flag", all(fl)))

# =====================================================================================================================
print("\n== PART AC: any_case(rx) := /(?i:${rx})/ under flags-propagate, against the primitive (a member up to letter case)")
def variants(t):
    return {"".join(p) for p in itertools.product(*[(ch.lower(), ch.upper()) if ch.isalpha() else (ch,) for ch in t])}
def prim(Srx, t):                       # the primitive's definition (§2.7): t equals some member of S up to letter case
    return any(re.fullmatch(Srx, u) is not None for u in variants(t))
AP = pool("hHoO1", 4)
acd = {}
for Srx in ("ho", "h[o1]+", "(?:ho|1h)"):
    body = r"(?i:(?:%s))" % Srx if not sab("s7") else r"(?i:(?-i:%s))" % Srx
    nobody = r"(?i:(?-i:%s))" % Srx
    acd[Srx] = sum(1 for t in AP if (re.fullmatch(body, t) is not None) != prim(Srx, t))
    nn = sum(1 for t in AP if (re.fullmatch(nobody, t) is not None) != prim(Srx, t))
    print("AC plain argument `/%s/`: the body vs the primitive %d of %d differ (under the reversed rule: %d)" % (Srx, acd[Srx], len(AP), nn))
QP = pool('hHoO"', 4)
Sq = r'"(?=ho")[^"]*"'                  # quoted("ho") = /"${"ho" & /[^"]*/}"/, the `&` spelt as a whole-stretch lookahead
fr_a = r'(?i:"(?=(?-i:ho)")[^"]*")'     # reading (a), m2: an `&` operand is not a hole: keeps its own (caseful) flags
fr_b = r'(?i:"(?=ho")[^"]*")'           # reading (b): propagation reaches the `&` operand too (NOT ruled)
da = [t for t in QP if (re.fullmatch(fr_a, t) is not None) != prim(Sq, t)]
db = [t for t in QP if (re.fullmatch(fr_b, t) is not None) != prim(Sq, t)]
print("AC a FILTER-ROLE argument `any_case(quoted(\"ho\"))` over %d texts (`hHoO\"`, length <= 4): (a) an `&` operand keeps its own flags (the manager's m2): %d differ %s ; (b) propagation into the `&` operand too: %d differ"
      % (len(QP), len(da), da[:3], len(db)))
print("AC %s" % check("AC plain arguments pass, filter role fails under (a)", all(n == 0 for n in acd.values()) and len(da) > 0 and len(db) == 0))

# =====================================================================================================================
print("\n== PART UN: unset-in-hole (RULED: no string, a regex that matches nothing)")
NEVER = r"(?!)" if not sab("s8") else r"(?:)"
py = [re.search(NEVER, "abc") is None, re.fullmatch(r"(?:%s|x)" % NEVER, "x") is not None, re.fullmatch(r"a(?:%s)?" % NEVER, "a") is not None,
      re.fullmatch(NEVER, "") is None]
pc_ = [S(P.Pcre(NEVER), "abc") is None, W(P.Pcre(r"(?:%s|x)" % NEVER), "x") is not None, W(P.Pcre(r"a(?:%s)?" % NEVER), "a") is not None,
       W(P.Pcre(NEVER), "") is None]
print("UN the never-matching rx `%s`: finds nothing in `abc` (and not the empty string) / `(?:%s|x)` holds on `x` / `a(?:%s)?` holds on `a`: python %s ; libpcre2 %s"
      % (NEVER, NEVER, NEVER, py, pc_))
alg = hole(r'(?<y>\d)?-', lambda c, v: v in ([c.get("y")] if c.get("y") is not None else []) + ["x"])
pco = P.Pcre(r'(?<y>\d)?-(?:\k<y>|x)')
du, _ = diff3(alg, pco, pool("37x-", 5))
print("UN `/(?<y>\\d)?-${$y | \"x\"}/` (the unset read = the rx of no strings): %s ; vs PCRE `(?:\\k<y>|x)` %d / %d / %d of %d"
      % (show(alg, "-x", "-x", "3-3 -x"), du[0], du[1], du[2], len(pool("37x-", 5))))
def F2(rx, s, after):
    out, pos, ne = [], 0, False
    while pos <= len(s):
        r = rx.match(s, pos, (NOTEMPTY_ATSTART | P.PCRE2_ANCHORED) if ne else 0)
        if r is None:
            if ne:
                ne = False
                pos += 1
                continue
            break
        out.append(r)
        after(r)
        ne = r[1] == r[0]
        pos = r[1]
    return out
def carry(pre, post, t):
    st = {"prev": None}
    rx = P.Pcre(pre + VQ + post, {"eq": lambda c: st["prev"] is not None and c.get("v") == plus(st["prev"], 1)})
    return F2(rx, t, lambda r: st.__setitem__("prev", r[2].get("y")))
r5 = {t: carry('', r'-(?<y>\d{4})', t) for t in ("-2025 2026-2030", "-2025 2027-2030")}
r5b = {t: carry(r'(?:', r'-)?(?<y>\d{4})', t) for t in ("2025 2026-2030", "2025 2027-2030")}
for t, hs in list(r5.items()) + list(r5b.items()):
    print("UN R.1.15 (5) hit list on `%s`: %s" % (t, "[" + ", ".join("`%s`@%d" % (t[a:b], a) for a, b, _ in hs) + "]"))
print("UN %s" % check("UN never-matching rx, ALGEBRA, (5) vacuous first form",
      all(py) and all(pc_) and du == [0, 0, 0] and all(len(h) == 0 for h in r5.values())
      and [(a, b) for a, b, _ in r5b["2025 2026-2030"]] == [(0, 4), (5, 14)]))

# =====================================================================================================================
print("\n== PART CN: construction-line (RULED: enumerate) as RULE-AS-CODE; lift-order by consequence")
BUDGET = 10000
class Refused(Exception):
    pass
def enum(n):
    """§5.5 enumerate: a FINITE rx's strings in PCRE priority order (class members in codepoint order, the LEAN);
    an infinite or over-budget rx, or an edge assertion, refused"""
    k = n[0]
    if k == "lit":
        return [n[1]]
    if k == "alt":
        return [s for c in n[1] for s in enum(c)]
    if k == "cls":
        return sorted(n[1], reverse=sab("s9"))
    if k == "cat":
        out = [""]
        for c in n[1]:
            out = [a + b for a in out for b in enum(c)]          # first operand slowest
            if len(out) > BUDGET:
                raise Refused("over budget")
        return out
    if k == "rep":
        _, c, lo, hi = n
        if hi is None:
            if not sab("s10"):
                raise Refused("infinite")
            hi = 3
        out = []
        for m in range(hi, lo - 1, -1):                          # greedy: more copies first
            out += enum(("cat", [c] * m)) if m else [""]
        if len(out) > BUDGET:
            raise Refused("over budget")
        return out
    if k == "look":
        raise Refused("an assertion looking outside")
    raise ValueError(k)
D = ("cls", "0123456789")
def lift(f, node):
    return [f(s) for s in enum(node)]
def alt_rx(strs):
    return P.Pcre("(?:" + "|".join(re.escape(s) for s in strs) + ")")
left2 = lambda s: s[:2]
table = [("left(\"foobar\", 2)", lambda: lift(left2, ("lit", "foobar")), r"foobar"),
         ("left(/foobar|bazqux/, 2)", lambda: lift(left2, ("alt", [("lit", "foobar"), ("lit", "bazqux")])), r"foobar|bazqux"),
         ("left(\"foobar\" | \"bazqux\", 2)", lambda: lift(left2, ("alt", [("lit", "foobar"), ("lit", "bazqux")])), r"foobar|bazqux"),
         ("\\d + 1", lambda: lift(lambda s: plus(s, 1), D), r"\d"),
         ("left(/\\d+/, 2)", lambda: lift(left2, ("rep", D, 1, None)), r"\d+"),
         ("left(/(?<=x)ab/, 1)", lambda: lift(lambda s: s[:1], ("cat", [("look", "(?<=x)"), ("lit", "ab")])), r"(?<=x)ab"),
         ("[1, 2] + [10, 20]", lambda: [plus(a, int(b)) for a in enum(("alt", [("lit", "1"), ("lit", "2")])) for b in enum(("alt", [("lit", "10"), ("lit", "20")]))], None)]
cn = {}
for name, fn, src in table:
    try:
        out = fn()
        cn[name] = out
        extra = ""
        if src is not None and "(?<=" not in src:
            bf = sorted(s for s in pool("0123456789abfoqruxz", 1) + ["foobar", "bazqux"] if re.fullmatch(src, s))
            setok = sorted(enum({"foobar": ("lit", "foobar"), r"foobar|bazqux": ("alt", [("lit", "foobar"), ("lit", "bazqux")]), r"\d": D, r"\d+": ("rep", D, 1, None)}[src])) == bf
            extra = " ; enumerate's SET = python `re`'s on a brute-force pool: %s" % setok
            cn[name + " set"] = setok
        print("CN %-28s = %s%s" % (name, " | ".join(out), extra))
    except Refused as e:
        cn[name] = "REFUSED (%s)" % e
        print("CN %-28s : COMPILE ERROR, UNDER CONSTRUCTION (enumerate refuses: %s)" % (name, e))
la = alt_rx(cn["left(/foobar|bazqux/, 2)"])
print("CN `/${left(/foobar|bazqux/, 2)}/` as a pattern: %s" % show(la, "fo", "xba fo", "fo ba fofo"))
d1 = alt_rx(cn["\\d + 1"])
print("CN `/${\\d + 1}/` (ten strings, enumerate's order): %s" % show(d1, "10", "x10", "10 3 11"))
# lift-order by consequence: a variable-width finite operand, `\d{1,2}`: enumerate's order = PCRE's path order
yfin = ("rep", D, 1, 2)
cps = alt_rx([y + plus(y, 1) for y in enum(yfin) if plus(y, 1) is not None])
rt = hole(r'(?<y>\d{1,2})', lambda c, v: v == plus(c.get("y"), 1))
dl, fl_ = diff3(rt, cps, pool("0123", 5))
print("CN `/(?<y>\\d{1,2})${$y + 1}/` run time vs its compile-time copies in ENUMERATE's order: %d / %d / %d of %d (`0123`, length <= 5)"
      % (dl[0], dl[1], dl[2], len(pool("0123", 5))))
lr = hole(r'(?<y>\w+)-', lambda c, v: c.get("y") is not None and v == str(len(c.get("y"))))
print("CN `length` on a read, `/(?<y>\\w+)-${length($y)}/` (a canonical numeral): %s" % show(lr, "abc-3", "ab-3 abc-3", "a-1 ab-3 abcdefghij-10"))
print("CN %s" % check("CN enumerate line, the hand-worked table, lift-order",
      cn["left(\"foobar\", 2)"] == ["fo"] and cn["left(/foobar|bazqux/, 2)"] == ["fo", "ba"] == cn["left(\"foobar\" | \"bazqux\", 2)"]
      and cn["\\d + 1"] == [str(i) for i in range(1, 11)] and str(cn["left(/\\d+/, 2)"]).startswith("REFUSED")
      and str(cn["left(/(?<=x)ab/, 1)"]).startswith("REFUSED") and cn["[1, 2] + [10, 20]"] == ["11", "21", "12", "22"]
      and all(v for k, v in cn.items() if k.endswith(" set")) and dl == [0, 0, 0]
      and fS(d1, "x10") == "`1`@1" and W(lr, "abc-3") is not None))

# =====================================================================================================================
print("\n== PART HR: hole-reads-capture (RULED: the label); the capture way in rx text; the label-only group's spelling")
def label_of(c, g):
    if sab("s11"):
        return c.get(g)
    sp, ps = c.span(g), c.span("ps")
    return c.get(g) if (sp is not None and ps is not None and sp[0] >= ps[0]) else None
lab = P.Pcre(r'(?:(?<ps>)(?<y>\d)?-' + VQ + ';)*', {"eq": lambda c: label_of(c, "y") is not None and c.get("v") == label_of(c, "y")})
cap = P.Pcre(r'(?:(?<y>\d)?-\k<y>;)*')
print("HR LABEL `/(?:(?<y>\\d)?-${$y};)*/`: %s" % show(lab, "3-3;-3;", "3-3;-3;", "3-3;-3; 7-7;"))
print("HR CAPTURE `/(?:(?<y>\\d)?-\\k<y>;)*/`: %s" % show(cap, "3-3;-3;", "3-3;-3;", "3-3;-3; 7-7;"))
dh, _ = diff3(lab, cap, pool("37-;", 7))
print("HR label vs capture over %d texts (`37-;`, length <= 7): %d / %d / %d" % (len(pool("37-;", 7)), dh[0], dh[1], dh[2]))
spl = []
for sp_ in (r"(?<:x>foo)", r"(?':x'foo)", r"(<:x>foo)"):
    try:
        p = P.Pcre(sp_)
        spl.append("COMPILES")
        print("HR libpcre2 `%s`: COMPILES ; WHOLE `<:x>foo` %s" % (sp_, fW(p, "<:x>foo")))
    except ValueError as e:
        spl.append("REJECTED")
        print("HR libpcre2 `%s`: REJECTED (%s)" % (sp_, str(e).split(": ", 1)[-1]))
print("HR %s" % check("HR label differs from capture; the spellings", W(lab, "3-3;-3;") is None and W(cap, "3-3;-3;") is not None
      and dh[0] == 2 and spl == ["REJECTED", "REJECTED", "COMPILES"]))

# =====================================================================================================================
print("\n== PART SN: same-name-twice (RULED: an error at the backreference unless `(?J)`, then PCRE's first set group)")
sn = []
try:
    P.Pcre(r"(?'h'\d)(?'h'\d)-\k<h>")
    sn.append("COMPILES"); print("SN libpcre2 without `(?J)`: COMPILES")
except ValueError as e:
    sn.append("REJECTED"); print("SN libpcre2 `(?<h>\\d)(?<h>\\d)-\\k<h>` without `(?J)`: REJECTED (%s)" % str(e).split(": ", 1)[-1])
pj2 = P.Pcre(r"(?J)(?'h'\d)(?'h'\d)-\k<h>")
first = lambda s: re.fullmatch(r"(\d)(\d)-(\d)", s) is not None and s[-1] == (s[1] if sab("s12") else s[0])
print("SN `(?J)(?<h>\\d)(?<h>\\d)-\\k<h>`: %s" % show(pj2, "12-1", "x12-2 34-3", "12-1 34-4 56-5"))
mod = sum(1 for t in pool("12-", 4) if (W(pj2, t) is not None) != first(t))
print("SN libpcre2 under `(?J)` vs \"the FIRST group's text\" WHOLE over %d texts (`12-`, length <= 4): %d differ" % (len(pool("12-", 4)), mod))
pn2 = P.Pcre(r"(?J)(?'h'\d)(?'h'\d)-\2")
print("SN the numbered form `(?J)(?<h>\\d)(?<h>\\d)-\\2` (the second group): %s" % show(pn2, "12-2", "x12-1 34-4", "12-2 34-3 56-6"))
pbl = P.Pcre(r"(?J)(?'h'\d);(?:(?'h'\d)|x)\k<h>")
print("SN rev 27's PART BL m3 witness under `(?J)` `/(?<h>\\d);(?:(?<h>\\d)|x)\\k<h>/`: %s" % show(pbl, "3;x3", "3;x3 3;77", "3;x3 3;77 3;73"))
print("SN %s" % check("SN error without J, first set with J, numbered form", sn == ["REJECTED"] and mod == 0 and W(pj2, "12-2") is None
      and W(pn2, "12-2") is not None and fF(pbl, "3;x3 3;77 3;73") == "[`3;x3`@0, `3;73`@10]"))

# =====================================================================================================================
print("\n== PART DW: dollar-warning (the manager's call: the dedicated warning WITHDRAWN): what the program does")
def dw(c):
    x = c.get("x")
    if sab("s13"):
        return canon(x) and int(x) < 5
    return c.stretch() == x and canon(x) and int(x) < 5          # `$x & <5` as an `&` operand filters the STRETCH
pdw = P.Pcre(r'(?<x>\d+)-(?C"f")', {"f": dw})
pcond = P.Pcre(r'(?<x>\d+)-(?C"f")', {"f": lambda c: canon(c.get("x")) and int(c.get("x")) < 5})
DP = pool("37-", 5)
nh = [sum(1 for t in DP if row(pdw, t, m) not in (False, None, ())) for m in "WSF"]
nc = [sum(1 for t in DP if row(pcond, t, m) not in (False, None, ())) for m in "WSF"]
print("DW `/(?<x>\\d+)-/ & ($x & <5)`: %s ; texts with a hit over %d (`37-`, length <= 5): %d / %d / %d" % (show(pdw, "3-", "7-3-", "3- 7- 3-"), len(DP), nh[0], nh[1], nh[2]))
print("DW `/(?<x>\\d+)-/ & (x: <5)`: %s ; texts with a hit: %d / %d / %d" % (show(pcond, "3-", "7-3-", "3- 7- 3-"), nc[0], nc[1], nc[2]))
print("DW %s" % check("DW the `$` form never holds, the condition does", nh == [0, 0, 0] and nc[0] > 0))

# =====================================================================================================================
print("\n== PART TT: the TYPE TABLE of rev 28 as RULE-AS-CODE (the rows the rulings move; unstated -> NOT-MODELLED)")
KINDS = ("const", "read", "readfin", "array", "finite", "rx", "matchonly")
SINGLE_FNS = {"+", "-", "*", "%", "left", "length", "upperStart", "."}
def status(op, kind):
    if op in SINGLE_FNS:
        if kind == "matchonly":
            return "ERROR"
        if op == "." :
            return "OPEN" if kind in ("const", "read", "readfin") else "NOT-MODELLED"
        if kind in ("const", "read", "readfin", "array"):
            return "BUILT"
        if kind == "finite":
            return "UNDER CONSTRUCTION" if sab("s14") else "BUILT"
        return "UNDER CONSTRUCTION"
    if op == "count-hole":
        return {"const": "BUILT", "array": "BUILT", "finite": "BUILT", "readfin": "OPEN", "read": "UNDER CONSTRUCTION"}.get(kind, "NOT-MODELLED")
    if op == "read-unset":
        return "BUILT" if kind in ("read", "readfin") else "NOT-MODELLED"
    return "NOT-MODELLED"
RANK = {"BUILT": 0, "OPEN": 1, "NOT-MODELLED": 1, "UNDER CONSTRUCTION": 2, "ERROR": 3}
def compose(op, kind, pos, rkind):
    a, b = status(op, kind), status(pos, rkind)
    return a if RANK[a] >= RANK[b] else b
TT = {}
for op in ("+", "-", "*", "%", "left", "length", "upperStart"):
    for k in KINDS:
        TT[(op, k)] = {"const": "BUILT", "read": "BUILT", "readfin": "BUILT", "array": "BUILT", "finite": "BUILT",
                       "rx": "UNDER CONSTRUCTION", "matchonly": "ERROR"}[k]
for k in KINDS:
    TT[(".", k)] = {"const": "OPEN", "read": "OPEN", "readfin": "OPEN", "matchonly": "ERROR"}.get(k, "NOT-MODELLED")
    TT[("count-hole", k)] = {"const": "BUILT", "array": "BUILT", "finite": "BUILT", "readfin": "OPEN", "read": "UNDER CONSTRUCTION"}.get(k, "NOT-MODELLED")
okt = all(status(o, k) == e for (o, k), e in TT.items())
for op in ("+", "left", ".", "count-hole"):
    print("TT %-10s %s" % (op, " ; ".join("%s %s" % (k, status(op, k)) for k in KINDS)))
cmp = compose("+", "array", "count-hole", "array")
print("TT composition `\\d{${n + 1}}`, n := [2, 4]: T8 on an array %s, T13 on its finite result %s -> %s" % (status("+", "array"), status("count-hole", "array"), cmp))
print("TT %d cells ; %s" % (len(TT), check("TT rev 28's changed rows", okt and cmp == "BUILT")))

print("\n== CHECKS: %d of %d OK" % (sum(ok for _, ok in CHECKS), len(CHECKS)))
for n, ok in CHECKS:
    if not ok:
        print("FAILED CHECK: %s" % n)
