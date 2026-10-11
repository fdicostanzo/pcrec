#!/usr/bin/env python3
"""where_to_start.md §B: a model of the REVERSE-INNER start (ENG-TACTICS (b)/(c))
tested against libpcre2 on generated cases, with a mutation table.

A pattern is generated as R = P . L . S (P, S random regex trees over a small
alphabet, L a literal). The ORACLE is libpcre2's own unanchored search
(pcre2_match from each startpos, and its find-all loop). The MODEL is the
tactic, with libpcre2 used only as its two COMPONENTS:

  starts(j)   = { s in [lo, j] : some path of P matches subject[s:j] }, the set a
                reverse DFA of P seeded at the landmark position j accepts. Computed
                by `p_ends_at` (P with its end pinned at j, run anchored at s by the
                backtracking matcher, which tries every path) over the WHOLE
                subject, so views (\\b, ^, $, lookbehind) read their real context.
                For a P with an atomic group this is the priority-restricted set,
                not the language; the gate declines such P.
  verify(s)   = pcre2_match(R, s, ANCHORED), the forward engine run from the
                candidate: the end and the captures (tactic (b)).
  end_c(j)    = pcre2_match(S, j+|L|, ANCHORED): tactic (c), the end from the
                landmark's end over S only (compared on the END only).

The tactic (b): for each occurrence j of L at or after `from`, in increasing
order: s* = min starts(j); if verify(s*) succeeds, that is the answer; else
next occurrence (j+1). A GATE decides whether the tactic applies (else the
model answers with the plain engine): G2's THREE arms, each its own conjunct
(P fixed width; P cannot consume every distinct byte of L = rust regex-automata's
`has_no_earlier_match` sufficient conditions; and D151 add. 5's FACTOR-FREE arm: no
string of P contains L as a factor AND L is border-free, decided on P's automaton --
`factor_witness`, a product of P's NFA with L's occurrence automaton), plus pcrec-side
conditions (P has no backreference, atomic group, possessive quantifier, or lookaround).
`--arms literal` switches the third arm off and reproduces the pre-arm transcripts.
Rows keyed `[factor-free]` are the splits ONLY the third arm admits.

Variants added with the arm: `floor` (the reverse walk stops at the previous hit's first
byte: the linearity argument of where_to_start.md 2.7, sound under the alphabet and
factor-free arms, not under fixed width), `floor_end` (stops at the previous hit's END:
reported, NOT sound), and four NEGATIVE CONTROLS `neg_factor*` / `neg_border*` that
admit a split the third arm refuses (P contains L; L bordered) and must be found wrong.
`--check-arm N` cross-checks the arm's decision procedure against brute-force enumeration
with python `re` and the generator's own width/alphabet bookkeeping; `--shaped N` runs the
altwide/sfx-shaped and `[a-z]+xy`-shaped cases; `--xl` adds longer and bordered literals.

Mutations are flags on the tactic; each must be DETECTED (>= 1 mismatch) for the
comparison to have teeth. `--selftest` asserts that.

Env: PCRE2_LIB (default /opt/homebrew/lib/libpcre2-8.dylib; the Linux dev box's 10.46 is /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0). Deterministic
(--seed). Usage: python3 rinner_model.py [--n 4000] [--seed 1] [--selftest]
"""
import argparse, ctypes, os, random, re, sys, collections

LIB = ctypes.CDLL(os.environ.get("PCRE2_LIB", "/opt/homebrew/lib/libpcre2-8.dylib"))
SZ = ctypes.c_size_t
LIB.pcre2_compile_8.restype = ctypes.c_void_p
LIB.pcre2_compile_8.argtypes = [ctypes.c_char_p, SZ, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(SZ), ctypes.c_void_p]
LIB.pcre2_match_data_create_8.restype = ctypes.c_void_p
LIB.pcre2_match_data_create_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
LIB.pcre2_match_8.restype = ctypes.c_int
LIB.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, SZ, SZ, ctypes.c_uint32,
                              ctypes.c_void_p, ctypes.c_void_p]
LIB.pcre2_dfa_match_8.restype = ctypes.c_int
LIB.pcre2_dfa_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, SZ, SZ, ctypes.c_uint32,
                                  ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), SZ]
LIB.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(SZ)
LIB.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
LIB.pcre2_config_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]

ANCHORED, MULTILINE, UTF = 0x80000000, 0x00000400, 0x00080000
MD = LIB.pcre2_match_data_create_8(256, None)
WS = (ctypes.c_int * 4000)()


def version():
    buf = ctypes.create_string_buffer(64)
    LIB.pcre2_config_8(11, buf)  # PCRE2_CONFIG_VERSION
    return buf.value.decode()


_cc = {}


def comp(pat, opts):
    k = (pat, opts)
    if k not in _cc:
        e, o = ctypes.c_int(), SZ()
        _cc[k] = LIB.pcre2_compile_8(pat, len(pat), opts, ctypes.byref(e), ctypes.byref(o), None)
    return _cc[k]


def match(code, subj, start, opts=0):
    rc = LIB.pcre2_match_8(code, subj, len(subj), start, opts, MD, None)
    if rc < 0:
        return None if rc == -1 else ("ERR", rc)
    ov = LIB.pcre2_get_ovector_pointer_8(MD)
    return tuple(ov[i] for i in range(2 * rc))


def p_ends_at(P, opts, subj, s, j):
    """Does some path of P match subject[s:j] (in the whole subject's context)?

    P is compiled with its END PINNED at j by a fixed-length lookbehind anchored at
    the subject start, `(?:P)(?<=\\A[\\s\\S]{j})`, and run ANCHORED at s by the
    backtracking matcher, which tries every path of P until one ends at j. (The
    all-paths pcre2_dfa_match was the first instrument and is WRONG here: it reports
    only the longest end for a trailing quantifier, `a*` on "aab" gives {2}, not
    {0,1,2}; recorded in where_to_start.md §B.)
    """
    if UTFMODE and (0x80 <= subj[s] < 0xC0 if s < len(subj) else False):
        return False                    # not a character start: no match begins here
    code = comp(("(?:%s)(?<=\\A[\\s\\S]{%d})" % (P, len(subj[:j].decode("utf8")) if UTFMODE else j)).encode(), opts)
    r = match(code, subj, s, ANCHORED)
    if isinstance(r, tuple) and r and r[0] == "ERR":
        raise RuntimeError("pcre2 error %d" % r[1])
    return r is not None



# ---- G2's factor-free arm (D151 add. 5): decided on P's AUTOMATON ---------
#
# arm 3 = (no string of P contains L as a factor) AND (L is border-free).
# The factor test is a product of P's NFA with L's occurrence automaton (KMP): L
# is a factor of some string of P iff the product reaches (P accepting, L fully
# matched).  Views and lookarounds are epsilon (a SUPERSET of P's language, so the
# arm errs only toward declining); atomic/possessive/lazy modifiers do not change
# the language.  It reads P's text through the generator's own grammar, never a
# pattern list.  `--check-arm` cross-checks it against brute-force enumeration.
import heapq


def _tok_set(s, i):
    """parse '[...]' at s[i] -> (set, next i); ranges a-z supported, '^' negates over ALPH+\\n."""
    j = s.index("]", i + 1)
    body, neg = s[i + 1:j], s[i + 1] == "^"
    if neg: body = body[1:]
    cs, k = set(), 0
    while k < len(body):
        if k + 2 < len(body) and body[k + 1] == "-":
            cs |= {chr(x) for x in range(ord(body[k]), ord(body[k + 2]) + 1)}; k += 3
        else:
            cs.add(body[k]); k += 1
    return ((set(ALPH) | {"\n"}) - cs if neg else cs), j + 1


def parse_p(s):
    """P text -> AST: ('set', frozenset) | ('eps',) | ('cat', [..]) | ('alt', [..]) | ('rep', n, lo, hi)."""
    def alt(i):
        parts, (n, i) = [], seq(i)
        parts.append(n)
        while i < len(s) and s[i] == "|":
            n, i = seq(i + 1); parts.append(n)
        return (parts[0] if len(parts) == 1 else ("alt", parts)), i

    def seq(i):
        items = []
        while i < len(s) and s[i] not in "|)":
            n, i = piece(i); items.append(n)
        return ("cat", items), i

    def piece(i):
        n, i = atom(i)
        if i < len(s) and s[i] in "*+?{":
            if s[i] == "{":
                j = s.index("}", i); a = s[i + 1:j].split(","); i = j + 1
                lo, hi = int(a[0]), (int(a[1]) if len(a) > 1 else int(a[0]))
            else:
                lo, hi = {"*": (0, INF), "+": (1, INF), "?": (0, 1)}[s[i]]; i += 1
            if i < len(s) and s[i] in "?+": i += 1      # lazy / possessive: same language
            n = ("rep", n, lo, hi)
        return n, i

    def atom(i):
        c = s[i]
        if c == "(":
            look = s.startswith(("(?=", "(?!", "(?<=", "(?<!"), i)
            j = i + 1
            if s.startswith(("(?:", "(?>", "(?=", "(?!"), i): j = i + 3
            elif s.startswith(("(?<=", "(?<!"), i): j = i + 4
            n, j = alt(j)
            assert s[j] == ")", (s, j)
            return (("eps",) if look else n), j + 1
        if c == "[":
            cs, j = _tok_set(s, i); return ("set", frozenset(cs)), j
        if c == ".": return ("set", frozenset(ALPH)), i + 1
        if c == "\\":
            assert s[i + 1] in "bB", s; return ("eps",), i + 2
        if c in "^$": return ("eps",), i + 1
        return ("set", frozenset(c)), i + 1

    n, i = alt(0)
    assert i == len(s), (s, i)
    return n


def build_nfa(ast):
    eps, tr = [], []

    def new():
        eps.append([]); tr.append([]); return len(eps) - 1

    def comp_(n):
        k = n[0]
        if k == "set":
            a, b = new(), new(); tr[a].append((n[1], b)); return a, b
        if k == "eps":
            a, b = new(), new(); eps[a].append(b); return a, b
        if k == "cat":
            a = b = new()
            for m in n[1]:
                s2, e2 = comp_(m); eps[b].append(s2); b = e2
            return a, b
        if k == "alt":
            a, b = new(), new()
            for m in n[1]:
                s2, e2 = comp_(m); eps[a].append(s2); eps[e2].append(b)
            return a, b
        _, m, lo, hi = n                                   # rep
        a = b = new()
        for _ in range(lo):
            s2, e2 = comp_(m); eps[b].append(s2); b = e2
        if hi >= INF:
            s2, e2 = comp_(m); loop = new()
            eps[b].append(loop); eps[loop].append(s2); eps[e2].append(loop); b = loop
        else:
            end = new()
            for _ in range(hi - lo):
                eps[b].append(end); s2, e2 = comp_(m); eps[b].append(s2); b = e2
            eps[b].append(end); b = end
        return a, b

    s, e = comp_(ast)
    return eps, tr, s, e


def border_free(L):
    return not any(L[:k] == L[-k:] for k in range(1, len(L)))


def factor_witness(P, L):
    """Length of a SHORTEST string of P containing L as a factor, or None (P has no such string).
    Product of P's NFA with L's KMP automaton; (accepting, full-match) is the target."""
    eps, tr, s0, acc = build_nfa(parse_p(P))
    n = len(L)
    fail = [0] * n
    for q in range(1, n):
        k = fail[q - 1]
        while k and L[q] != L[k]: k = fail[k - 1]
        fail[q] = k + (L[q] == L[k])

    def step(k, ch):
        if k == n: return n
        while k and L[k] != ch: k = fail[k - 1]
        return k + (L[k] == ch)

    best, pq, seen = {(s0, 0): 0}, [(0, s0, 0)], set()
    while pq:
        d, q, k = heapq.heappop(pq)
        if (q, k) in seen: continue
        seen.add((q, k))
        if q == acc and k == n: return d
        for q2 in eps[q]:
            if best.get((q2, k), 1 << 30) > d:
                best[(q2, k)] = d; heapq.heappush(pq, (d, q2, k))
        for cs, q2 in tr[q]:
            for ch in cs:
                k2 = step(k, ch)
                if best.get((q2, k2), 1 << 30) > d + 1:
                    best[(q2, k2)] = d + 1; heapq.heappush(pq, (d + 1, q2, k2))
    return None


def arm_factor_free(P, L):
    return border_free(L) and factor_witness(P, L) is None


# ---- the generator -------------------------------------------------------

ALPH = "abX"
SUBJ = "aabbXX\n"
LITS = ["X", "X", "Xa", "aa", "ab", "a", "bX"]
UTFMODE = False
INF = 10 ** 6


class G:
    def __init__(self, rnd, side, ncap0):
        self.r, self.side, self.ncap = rnd, side, ncap0
        self.f = dict(bref=0, atomic=0, look=0, view=0)

    def atom(self, d):
        r = self.r
        x = r.random()
        if x < 0.30:
            c = r.choice(ALPH); return c, (1, 1), {c}
        if x < 0.42:
            s = r.choice([("[ab]", "ab"), ("[^X]", ALPH.replace("X", "") + "\n"), ("[aX]", "aX"), (".", ALPH)])
            return s[0], (1, 1), set(s[1])
        if x < 0.52 and d < 2:
            t, w, a = self.alt(d + 1)
            if r.random() < 0.5:
                self.ncap += 1; return "(" + t + ")", w, a
            if r.random() < 0.15 and self.side == "P":
                self.f["atomic"] = 1; return "(?>" + t + ")", w, a
            return "(?:" + t + ")", w, a
        if x < 0.60:
            v = r.choice(["\\b", "\\B", "^", "$"]); self.f["view"] = 1
            return v, (0, 0), set()
        if x < 0.64 and d < 2:
            k = r.choice(["?=", "?!", "?<=", "?<!"]); self.f["look"] = 1
            c = r.choice(ALPH)
            return "(" + k + c + ")", (0, 0), set()
        if x < 0.70 and self.side == "S" and self.ncap0 > 0:
            self.f["bref"] = 1; return "\\1", (0, INF), set(ALPH)
        c = r.choice(ALPH); return c, (1, 1), {c}

    def piece(self, d):
        t, (lo, hi), a = self.atom(d)
        r = self.r
        if (lo, hi) == (0, 0) or r.random() < 0.55:
            return t, (lo, hi), a
        q, m, n = r.choice([("*", 0, INF), ("+", 1, INF), ("?", 0, 1), ("{0,2}", 0, 2), ("{1,3}", 1, 3), ("{2}", 2, 2)])
        mod = r.choice(["", "", "?", "+"]) if q != "{2}" else ""
        if mod == "+":
            if self.side == "P": self.f["atomic"] = 1
        hi2 = INF if hi >= INF or n >= INF else hi * n
        return t + q + mod, (lo * m, hi2), (a if n > 0 else set())

    def seq(self, d):
        k = self.r.choice([1, 1, 2, 2, 3])
        t, lo, hi, a = "", 0, 0, set()
        for _ in range(k):
            pt, (pl, ph), pa = self.piece(d)
            t += pt; lo += pl; hi = min(INF, hi + ph); a |= pa
        return t, (lo, hi), a

    def alt(self, d):
        n = 1 if self.r.random() < 0.7 else 2
        parts = [self.seq(d) for _ in range(n)]
        return ("|".join(p[0] for p in parts), (min(p[1][0] for p in parts), max(p[1][1] for p in parts)),
                set().union(*[p[2] for p in parts]))


def gen_case(rnd):
    g = G(rnd, "P", 0); g.ncap0 = 0
    P, pw, pa = g.alt(0)
    pf = dict(g.f)
    L = rnd.choice(LITS)
    h = G(rnd, "S", g.ncap); h.ncap0 = g.ncap
    S, _sw, _sa = h.alt(0)
    sf = dict(h.f)
    multi = rnd.random() < 0.2
    # P is wrapped so L binds to the whole of P and the whole of S.
    R = "(?:%s)%s(?:%s)" % (P, L, S)
    return dict(P=P, L=L, S=S, R=R, pw=pw, palph=pa, pf=pf, sf=sf, multi=multi,
                nofactor=factor_witness(P, L) is None, bfree=border_free(L))


ARM3 = True      # --arms literal switches the factor-free arm off (reproduces the committed pre-arm transcripts)


def arms(c):
    """the three G2 arms for a case, each its own conjunct: {name: bool}"""
    return {"fixed-width": c["pw"][0] == c["pw"][1],
            "cannot-contain-L": not set(c["L"]) <= c["palph"],
            "factor-free": c["nofactor"] and c["bfree"]}


def gate(c):
    """(applies, reason). rust's sufficient conditions + pcrec's + D151 add. 5's factor-free arm."""
    pf, a = c["pf"], arms(c)
    amb = not (a["fixed-width"] or a["cannot-contain-L"] or (a["factor-free"] and ARM3))
    sfx = "+split-ambiguous" if amb else "+split-clean"
    if pf["atomic"]: return False, "P-atomic" + sfx
    if pf["look"]: return False, "P-lookaround" + sfx
    if a["fixed-width"]: return True, "P-fixed-width"
    if a["cannot-contain-L"]: return True, "P-cannot-contain-L"
    if a["factor-free"] and ARM3: return True, "P-factor-free"
    return False, "split-ambiguous"


def subjects(rnd, k):
    out = set()
    while len(out) < k:
        n = rnd.randint(0, 9)
        out.add("".join(rnd.choice(SUBJ) for _ in range(n)).encode())
    return sorted(out)


# ---- the tactic, with its mutation flags --------------------------------

def tactic_first(c, subj, frm, mut, opts, stats):
    cR = comp(c["R"].encode(), opts)
    cP = comp(("(?:%s)" % c["P"]).encode(), opts)
    L = c["L"].encode()
    base = subj
    off = 0
    if "slice" in mut:                  # M: the walk starts at the startpos as if it were 0
        base, off, frm = subj[frm:], frm, 0
        cR = comp(c["R"].encode(), opts)
    lo = 0 if "lo0" in mut else frm
    j = frm
    walked = 0
    min_match_start = 0
    prev_j = None
    while True:
        j = base.find(L, j)
        if j < 0:
            return None
        lo_j = lo
        if prev_j is not None:
            if "floor" in mut:          # the walk STOPS at the previous hit: no start at or before its first byte
                lo_j = max(lo, prev_j + 1)
            if "floor_end" in mut:      # ... or at the previous hit's END (the harsher reading)
                lo_j = max(lo, prev_j + len(L))
        Pw = c["P"]
        if "erase" in mut:              # the reverse machine a DFA builds: atomicity ERASED
            Pw = re.sub(r"([*+?}])\+", r"\1", Pw.replace("(?>", "(?:"))
        st = [s for s in range(lo_j, j + 1) if p_ends_at(Pw, opts, base, s, j)]
        walked += j - (min(st) if st else j)
        if "rust_guard" in mut and st and min(st) < min_match_start:
            # rust's try_search_half_rev_limited: the reverse walk would cross the previous
            # literal's end; RetryError::Quadratic, the core engine answers from the startpos.
            stats["rust_guard_fallback"] += 1
            return match(cR, base, frm)
        if "fallback" in mut and st and min_match_start > 0:
            # the candidate loop's GIVE-UP (rust's guard tripping, or a failed-verify budget):
            # hand the CURRENT candidate's s* to the ordinary unanchored scan as its startpos.
            # Exact iff s* is a lower bound on every remaining match start.
            return match(cR, base, min(st))
        if "lowerbound" in mut and st:
            # the HANDOFF form: s* is a lower bound on every match start, so the ordinary
            # unanchored search from s* answers exactly (no candidate loop at all).
            return match(cR, base, min(st))
        if st:
            s = max(st) if "max_start" in mut else min(st)
            r = match(cR, base, s, ANCHORED)
            if r is None and "noverify" in mut:
                r = (s, j + len(L))
            if r is not None:
                stats["walk"] += walked
                if off:
                    r = tuple(x + off if x != (1 << 64) - 1 else x for x in r)
                return r
        min_match_start = j + len(L)
        prev_j = j
        j += len(L) if "skipL" in mut else 1


def find_all(fn, subj):
    out, frm = [], 0
    while frm <= len(subj):
        r = fn(frm)
        if r is None or isinstance(r[0], str):
            break
        out.append(r)
        frm = r[1] if r[1] > r[0] else r[0] + 1
        if len(out) > 4 * len(subj) + 8:
            break                       # a WRONG variant whose answers do not advance: stop (a sound one yields <= len+1)
    return out


VARIANTS = ["tactic", "gate_off", "lowerbound", "lowerbound_gate_off", "rust_guard", "rust_guard_gate_off",
            "fallback", "fallback_gate_off", "erase_atomic",
            "max_start", "lo0", "slice", "noverify", "skipL", "restart_s1", "c_end", "c_end_gate_off",
            "floor", "floor_end", "neg_factor", "neg_factor_floor", "neg_border", "neg_border_floor"]
# variants that are NOT mutations of a sound tactic (their mismatch count is a finding, not a teeth check)
UNGATED = {"erase_atomic", "gate_off", "lowerbound_gate_off", "rust_guard_gate_off", "fallback_gate_off", "c_end_gate_off"}
# the gated tactic and its sound forms (asserted 0 mismatches); each also keyed "[factor-free]" for the splits ONLY arm 3 admits.
# `floor` = the walk stops at the previous hit's first byte (D151 add. 5's linearity argument); applies where P is not
# fixed width (a fixed-width P's one start may lie before the previous hit, and its walk is already <= w).
SOUND = ("tactic", "lowerbound", "rust_guard", "fallback", "c_end", "floor")
# NEGATIVE CONTROLS: admit a split the arm refuses. Each must be wrong somewhere or the check cannot fail.
#   neg_factor*: G1 ok, not admitted, L border-free but P CONTAINS L as a factor  (arm 3's factor conjunct removed)
#   neg_border*: G1 ok, not admitted, P factor-free but L has a border            (arm 3's border conjunct removed)
NEG = {"neg_factor": ("factor", ()), "neg_factor_floor": ("factor", ("floor",)),
       "neg_border": ("border", ()), "neg_border_floor": ("border", ("floor",))}
INFO = {"floor_end"}                         # reported, not asserted


def run(n, seed, show):
    rnd = random.Random(seed)
    tot = collections.Counter()
    bad = collections.Counter()
    wit = {}
    reasons = collections.Counter()
    stats = collections.Counter()
    for _ in range(n):
        c = gen_case(rnd)
        opts = (MULTILINE if c["multi"] else 0) | (UTF if UTFMODE else 0)
        cR = comp(c["R"].encode(), opts)
        if not cR or not comp(("(?:%s)" % c["P"]).encode(), opts) or not comp(("(?:%s)" % c["S"]).encode(), opts):
            tot["uncompilable"] += 1
            continue
        ok, why = gate(c)
        reasons[why] += 1
        tot["cases"] += 1
        tot["gated"] += ok
        sfx = "[factor-free]" if why == "P-factor-free" else ""
        a3 = arms(c)
        g1 = not (c["pf"]["atomic"] or c["pf"]["look"])
        if g1:
            for nm, val in a3.items():
                tot["armcase:" + nm] += val
            tot["armcase:any(literal)"] += a3["fixed-width"] or a3["cannot-contain-L"]
            tot["armcase:factor-free-only"] += why == "P-factor-free"
        cS = comp(("(?:%s)" % c["S"]).encode(), opts)
        for subj in subjects(rnd, 12):
            orc = lambda f: match(cR, subj, f)
            truth_all = find_all(orc, subj)
            for v in VARIANTS:
                if v in ("c_end", "c_end_gate_off"):
                    if v == "c_end" and (not ok or c["sf"]["bref"]):
                        continue
                    if v == "c_end_gate_off" and (ok or c["sf"]["bref"]):
                        continue
                    # tactic (c): the END from the landmark's end over S only.
                    for frm in range(len(subj) + 1):
                        if UTFMODE and frm < len(subj) and 0x80 <= subj[frm] < 0xC0:
                            continue
                        t = orc(frm)
                        if t is None: continue
                        # (c) is tested in isolation: given the TRUE start t0 (which (b) recovers), the
                        # landmark is the first L at/after t0 that a P-path from t0 reaches.
                        j = subj.find(c["L"].encode(), t[0])
                        while j >= 0 and not p_ends_at(c["P"], opts, subj, t[0], j):
                            j = subj.find(c["L"].encode(), j + 1)
                        e = match(cS, subj, j + len(c["L"].encode()), ANCHORED) if j >= 0 else None
                        tot[v + sfx] += 1
                        if e is None or e[1] != t[1]:
                            bad[v + sfx] += 1
                            wit.setdefault(v + sfx, (c["R"], subj, frm, t[:2], e))
                    continue
                key = v
                if v == "erase_atomic":
                    # an atomic/possessive P whose split is clean, walked by the ERASED language
                    if why != "P-atomic+split-clean": continue
                    mut = ("erase",)
                elif v in UNGATED:
                    if ok: continue
                    mut = () if v == "gate_off" else (v[:-len("_gate_off")],)
                    key = "%s[%s]" % (v, why)
                elif v == "tactic":
                    if not ok: continue
                    mut = ()
                    key = v + sfx
                elif v in NEG:
                    kind, mut = NEG[v]
                    if ok or not g1: continue
                    if kind == "factor" and not (c["bfree"] and not c["nofactor"]): continue
                    if kind == "border" and not (c["nofactor"] and not c["bfree"]): continue
                elif v in ("floor", "floor_end"):
                    if not ok or a3["fixed-width"]: continue
                    mut = (v,)
                    key = v + sfx if v == "floor" else v + (sfx or "[literal]")
                else:
                    if not ok: continue
                    mut = (v,)
                    if v in SOUND: key = v + sfx
                fn = lambda f: tactic_first(c, subj, f, mut, opts, stats)
                # single searches from every startpos
                for frm in range(len(subj) + 1):
                    if UTFMODE and frm < len(subj) and 0x80 <= subj[frm] < 0xC0:
                        continue
                    t, m = orc(frm), fn(frm)
                    tot[key] += 1
                    if v == "tactic":
                        for nm, val in a3.items():
                            tot["arm:" + nm] += val
                        tot["arm:factor-free-only"] += why == "P-factor-free"
                    if t != m:
                        bad[key] += 1
                        wit.setdefault(key, (c["R"], subj, frm, t, m))
                # find-all
                if v == "restart_s1":
                    got, frm = [], 0
                    while frm <= len(subj):
                        r = fn(frm)
                        if r is None: break
                        got.append(r); frm = r[0] + 1
                else:
                    got = find_all(fn, subj)
                tot[key + "/findall"] += 1
                if got != truth_all:
                    bad[key + "/findall"] += 1
                    wit.setdefault(key + "/findall", (c["R"], subj, 0, truth_all, got))
    return tot, bad, wit, reasons, stats


def ast_info(n):
    """(min width, max width, alphabet) of a parsed P: an independent derivation of what the generator tracks."""
    k = n[0]
    if k == "set": return 1, 1, set(n[1])
    if k == "eps": return 0, 0, set()
    if k == "cat":
        lo = hi = 0; al = set()
        for m in n[1]:
            a, b, c_ = ast_info(m); lo += a; hi = min(INF, hi + b); al |= c_
        return lo, hi, al
    if k == "alt":
        r = [ast_info(m) for m in n[1]]
        return min(x[0] for x in r), max(x[1] for x in r), set().union(*[x[2] for x in r])
    a, b, c_ = ast_info(n[1])
    return a * n[2], (INF if b and n[3] >= INF else min(INF, b * n[3])), (c_ if n[3] > 0 else set())


def check_arm(n, seed):
    """the arm's decision procedure against two independent controls: (1) brute-force enumeration with python `re`
    (view/lookaround/atomic-free P; every string over the alphabet up to length 6), (2) the generator's own width
    and alphabet bookkeeping against the parsed AST's."""
    import itertools
    rnd = random.Random(seed)
    chars = sorted(set(ALPH) | {"\n"})
    allw = ["".join(t) for k in range(0, 7) for t in itertools.product(chars, repeat=k)]
    st = collections.Counter()
    for _ in range(n):
        c = gen_case(rnd)
        lo, hi, al = ast_info(parse_p(c["P"]))
        st["bookkeeping"] += 1
        if (lo, hi) != tuple(c["pw"]) or al != set(c["palph"]):
            st["bookkeeping-MISMATCH"] += 1
            print("bookkeeping mismatch", c["P"], (lo, hi, al), c["pw"], c["palph"])
        pf = c["pf"]
        if pf["view"] or pf["look"] or pf["atomic"]:
            continue
        wlen = factor_witness(c["P"], c["L"])
        rx = re.compile(c["P"])
        try:
            found = next((w for w in allw if c["L"] in w and rx.fullmatch(w)), None)
        except re.error:
            continue
        st["brute"] += 1
        st["factor-present"] += wlen is not None
        if found is not None and wlen is None:
            st["UNSOUND (brute found a factor string, automaton says none)"] += 1
            print("UNSOUND", c["P"], c["L"], found)
        if wlen is not None and wlen <= 6 and found is None:
            st["INCOMPLETE (automaton witness <=6, brute found none)"] += 1
            print("INCOMPLETE", c["P"], c["L"], wlen)
        if found is not None and wlen is not None and wlen > len(found):
            st["witness-not-shortest"] += 1
    return st


def shaped(seed, nsubj):
    """hand-shaped cases (the bench's altwide/sfx and the [a-z]+xy floor example); the arm is DECIDED on the
    automaton for each, never labelled by hand."""
    global ALPH, UTFMODE
    ALPH, UTFMODE = "abcdefghijklmnopqrstuvwxyz", False
    rnd = random.Random(seed)
    lc = ALPH

    def stems(k, avoid, letters=lc):
        out = []
        while len(out) < k:
            w = "".join(rnd.choice(letters) for _ in range(rnd.randint(3, 9)))
            if avoid not in w and w not in out: out.append(w)
        return out

    sfx64, sfx256 = stems(64, "ing"), stems(256, "ing")
    # stems for the BORDERED-L control: eight end in "ni", so that "...ni" + "nin" overlaps a previous "nin" by one byte
    nin = stems(56, "nin") + ["kani", "bgni", "zeni", "opni", "qrni", "stuni", "vwxni", "hjni"]
    S7 = "[0-9]"
    st64 = lambda x: "(?:%s)" % "|".join(x)
    # (name, P, L, S, subject token pool, hot): a "hot" pool is small and built around the case's own hazard, so that the
    # hazardous subjects (overlaps, the stem-plus-L shapes) are common rather than rare
    cases = [
        ("sfx-64-shaped", st64(sfx64), "ing", S7, sfx64 + ["ing", "in", "g"]),
        ("sfx-64-shaped-hot", st64(sfx64), "ing", S7, sfx64[:4] + ["ing", "ing", "in", "g", "i", "ng", "n"]),
        ("sfx-256-shaped", st64(sfx256), "ing", S7, sfx256 + ["ing", "in", "g"]),
        ("sfx-256-shaped-hot", st64(sfx256), "ing", S7, sfx256[:4] + ["ing", "ing", "in", "g", "i", "ng", "n"]),
        ("sfx-64-NEG-stem-has-ing", st64(sfx64[:-1] + ["sing"]), "ing", S7, sfx64[:3] + ["sing", "ing", "ing"]),
        ("sfx-64-NEG-bordered-L", st64(nin), "nin", S7, ["kani", "kani", "nin", "nin", "in"]),
        ("[a-z]+xy", "[a-z]+", "xy", S7, ["xy", "xy", "a", "y"]),
        ("[a-z]+xy-NEG-S-empty", "[a-z]+", "xy", "", ["xy", "xy", "a", "y"]),
        ("[a-wz]+xy", "[a-wz]+", "xy", S7, ["xy", "xy", "a", "y", "x"]),
        ("[a-w]+xy-ing-S", "[a-w]+", "xy", S7, ["xy", "xy", "a", "y", "x"]),
        ("[a-z]{3}xy", "[a-z]{3}", "xy", S7, ["xy", "xy", "abc", "y", "x"]),
    ]
    res = []
    for name, P, L, S, pool in cases:
        lo, hi, al = ast_info(parse_p(P))
        w = factor_witness(P, L)
        c = dict(P=P, L=L, S=S, R="(?:%s)%s(?:%s)" % (P, L, S), pw=(lo, hi), palph=al)
        fixed, cannot = lo == hi, not set(L) <= al
        arm3 = w is None and border_free(L)
        lits_admit = fixed or cannot
        admitted_only_by_3 = arm3 and not lits_admit
        opts = 0
        cR = comp(c["R"].encode(), opts)
        assert cR, name
        print("== %s: P width (%s,%s), |alphabet(P)|=%d; fixed-width=%s, cannot-contain-L=%s; shortest P-string containing L: %s; "
              "L border-free=%s -> factor-free arm=%s; admitted by literal arms=%s, ONLY by arm 3=%s"
              % (name, lo, "inf" if hi >= INF else hi, len(al), fixed, cannot,
                 "none" if w is None else "%d bytes" % w, border_free(L), arm3, lits_admit, admitted_only_by_3))
        subs = set()
        while len(subs) < nsubj:
            t = "".join(rnd.choice(pool + ["7", "7", "3"]) if rnd.random() < 0.9 else rnd.choice(lc + "0123456789")
                        for _ in range(rnd.randint(1, 6)))
            if len(t) <= 60: subs.add(t.encode())
        subs = sorted(subs)
        for variant, mut in (("plain", ()), ("floor", ("floor",)), ("floor_end", ("floor_end",)), ("lowerbound", ("lowerbound",))):
            if variant in ("floor", "floor_end") and fixed: continue
            chk = bad_ = fa = fabad = 0; wit = None
            for subj in subs:
                orc = lambda f: match(cR, subj, f)
                fn = lambda f: tactic_first(c, subj, f, mut, opts, collections.Counter())
                for frm in range(len(subj) + 1):
                    t, m = orc(frm), fn(frm); chk += 1
                    if t != m:
                        bad_ += 1; wit = wit or (subj, frm, t, m)
                fa += 1
                if find_all(fn, subj) != find_all(orc, subj): fabad += 1
            print("   %-10s single %6d mismatch %4d | findall %5d mismatch %4d%s"
                  % (variant, chk, bad_, fa, fabad, ("  first: %r from %d truth %r got %r" % wit) if bad_ else ""))
            res.append((name, variant, arm3, lits_admit, bad_ + fabad))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--utf8", action="store_true", help="UTF mode: alphabet gains U+00E9, L may be it")
    ap.add_argument("--arms", choices=["all", "literal"], default="all",
                    help="'literal' switches the factor-free arm off (reproduces the pre-arm transcripts)")
    ap.add_argument("--xl", action="store_true", help="supplement population: longer and BORDERED literals added to LITS")
    ap.add_argument("--check-arm", type=int, metavar="N", help="cross-check the arm's decision procedure on N cases and exit")
    ap.add_argument("--shaped", type=int, metavar="NSUBJ", help="run the hand-shaped altwide/sfx and [a-z]+xy cases and exit")
    a = ap.parse_args()
    global ALPH, SUBJ, LITS, UTFMODE, ARM3
    ARM3 = a.arms == "all"
    if a.utf8:
        ALPH, SUBJ, UTFMODE = "abXé", "aabXXéé\n", True
        LITS = ["X", "é", "Xé", "éa", "aa", "a"]
        if a.xl: LITS += ["Xab", "aéb", "éé", "aXa", "bXb", "XX"]
    elif a.xl:
        LITS += ["Xab", "abX", "bb", "aXa", "bXb", "XX", "aba"]
    if a.check_arm:
        st = check_arm(a.check_arm, a.seed)
        print("# check_arm: libpcre2 not used; python re %s; seed %d, %d cases%s" % (sys.version.split()[0], a.seed, a.check_arm,
              ", UTF alphabet" if a.utf8 else ""))
        for k in sorted(st): print("%-70s %d" % (k, st[k]))
        bad_ = [k for k in st if k.isupper() or "MISMATCH" in k or k.startswith(("UNSOUND", "INCOMPLETE"))]
        print("check_arm: " + ("FAIL" if bad_ else "PASS"))
        sys.exit(1 if bad_ else 0)
    if a.shaped:
        print("# rinner_model.py --shaped: libpcre2 %s, seed %d, %d subjects per case" % (version(), a.seed, a.shaped))
        res = shaped(a.seed, a.shaped)
        fails = []
        for name, variant, arm3, lits, nbad in res:
            if arm3 and variant in ("plain", "floor", "lowerbound") and nbad:
                fails.append("%s/%s: arm-3-admitted split is WRONG (%d)" % (name, variant, nbad))
            if "NEG" in name or name.startswith("[a-z]+xy"):
                if not arm3 and variant == "floor" and nbad == 0:
                    fails.append("%s/floor: the negative control found nothing" % name)
        print("shaped: " + ("PASS" if not fails else "FAIL: " + "; ".join(fails)))
        sys.exit(1 if fails else 0)
    tot, bad, wit, reasons, stats = run(a.n, a.seed, True)
    print("# rinner_model.py: libpcre2 %s%s, seed %d, "
          "%d generated R = P.L.S%s%s%s" % (version(), "" if version().startswith("10.46") else " (NOT the 10.46 reference)",
          a.seed, a.n, ", UTF mode" if a.utf8 else "",
          ", XL literals" if a.xl else "", "" if ARM3 else ", LITERAL ARMS ONLY"))
    print("cases compiled %d (uncompilable %d); gate applies %d" % (tot["cases"], tot["uncompilable"], tot["gated"]))
    print("gate reasons: " + ", ".join("%s %d" % kv for kv in sorted(reasons.items())))
    print("G2 arms among G1-passing cases (cases / single-search checks; arms overlap):")
    for nm in ("fixed-width", "cannot-contain-L", "factor-free"):
        print("  %-22s %6d cases %9d checks" % (nm, tot["armcase:" + nm], tot["arm:" + nm]))
    print("  %-22s %6d cases" % ("either literal arm", tot["armcase:any(literal)"]))
    print("  %-22s %6d cases %9d checks   <- splits admitted by the factor-free arm and by NEITHER literal arm"
          % ("factor-free ONLY", tot["armcase:factor-free-only"], tot["arm:factor-free-only"]))
    print("%-30s %10s %10s  %s" % ("variant", "checks", "mismatch", "first witness (R, subject, startpos, truth, model)"))
    keys = []
    for v in VARIANTS:
        keys += sorted(k for k in tot if k == v or k.startswith(v + "[") or k == v + "/findall")
    for k in dict.fromkeys(keys):
            if tot[k] == 0: continue
            w = wit.get(k, "")
            print("%-30s %10d %10d  %s" % (k, tot[k], bad[k], w if bad[k] else ""))
    print("reverse-walk bytes over accepted candidates (tactic+mutants): %d; rust-guard fallbacks: %d"
          % (stats["walk"], stats["rust_guard_fallback"]))
    if a.selftest:
        fails = []
        for v in SOUND:
            for sf in ("", "[factor-free]"):
                for fa in ("", "/findall"):
                    if bad[v + sf + fa]:
                        fails.append("the gated %s%s%s disagrees with libpcre2" % (v, sf, fa))
        for v in VARIANTS:
            if v in UNGATED or v in SOUND or v in NEG or v in INFO: continue
            if bad[v] + bad[v + "/findall"] == 0:
                fails.append("mutation %s NOT detected" % v)
        if sum(n for k, n in bad.items() if k.startswith("gate_off[")) == 0:
            fails.append("the ungated tactic was never wrong: the gate is not shown necessary")
        if ARM3:
            if tot["tactic[factor-free]"] == 0:
                fails.append("the factor-free arm admitted no split: nothing was tested")
            nf = sum(bad[k] for k in ("neg_factor", "neg_factor/findall", "neg_factor_floor", "neg_factor_floor/findall"))
            if nf == 0: fails.append("negative control neg_factor (factor present) was never wrong")
            if a.xl:
                nb = sum(bad[k] for k in ("neg_border", "neg_border/findall", "neg_border_floor", "neg_border_floor/findall"))
                if nb == 0: fails.append("negative control neg_border (bordered L) was never wrong")
        print("selftest: " + ("PASS" if not fails else "FAIL: " + "; ".join(fails)))
        sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
