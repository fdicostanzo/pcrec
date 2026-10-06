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
model answers with the plain engine): rust regex-automata's
`has_no_earlier_match` sufficient conditions (P fixed width, or P cannot
consume every distinct byte of L), plus pcrec-side conditions (P has no
backreference, atomic group, possessive quantifier, or lookaround).

Mutations are flags on the tactic; each must be DETECTED (>= 1 mismatch) for the
comparison to have teeth. `--selftest` asserts that.

Env: PCRE2_LIB (default /opt/homebrew/lib/libpcre2-8.dylib). Deterministic
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
    return dict(P=P, L=L, S=S, R=R, pw=pw, palph=pa, pf=pf, sf=sf, multi=multi)


def gate(c):
    """(applies, reason). rust's sufficient conditions + pcrec's."""
    pf = c["pf"]
    amb = c["pw"][0] != c["pw"][1] and set(c["L"]) <= c["palph"]
    sfx = "+split-ambiguous" if amb else "+split-clean"
    if pf["atomic"]: return False, "P-atomic" + sfx
    if pf["look"]: return False, "P-lookaround" + sfx
    if c["pw"][0] == c["pw"][1]: return True, "P-fixed-width"
    if not set(c["L"]) <= c["palph"]: return True, "P-cannot-contain-L"
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
    while True:
        j = base.find(L, j)
        if j < 0:
            return None
        Pw = c["P"]
        if "erase" in mut:              # the reverse machine a DFA builds: atomicity ERASED
            Pw = re.sub(r"([*+?}])\+", r"\1", Pw.replace("(?>", "(?:"))
        st = [s for s in range(lo, j + 1) if p_ends_at(Pw, opts, base, s, j)]
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
        j += len(L) if "skipL" in mut else 1


def find_all(fn, subj):
    out, frm = [], 0
    while frm <= len(subj):
        r = fn(frm)
        if r is None or isinstance(r[0], str):
            break
        out.append(r)
        frm = r[1] if r[1] > r[0] else r[0] + 1
    return out


VARIANTS = ["tactic", "gate_off", "lowerbound", "lowerbound_gate_off", "rust_guard", "rust_guard_gate_off",
            "fallback", "fallback_gate_off", "erase_atomic",
            "max_start", "lo0", "slice", "noverify", "skipL", "restart_s1", "c_end", "c_end_gate_off"]
# variants that are NOT mutations of a sound tactic (their mismatch count is a finding, not a teeth check)
UNGATED = {"erase_atomic", "gate_off", "lowerbound_gate_off", "rust_guard_gate_off", "fallback_gate_off", "c_end_gate_off"}


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
                        tot[v] += 1
                        if e is None or e[1] != t[1]:
                            bad[v] += 1
                            wit.setdefault(v, (c["R"], subj, frm, t[:2], e))
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
                else:
                    if not ok: continue
                    mut = (v,)
                fn = lambda f: tactic_first(c, subj, f, mut, opts, stats)
                # single searches from every startpos
                for frm in range(len(subj) + 1):
                    if UTFMODE and frm < len(subj) and 0x80 <= subj[frm] < 0xC0:
                        continue
                    t, m = orc(frm), fn(frm)
                    tot[key] += 1
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--utf8", action="store_true", help="UTF mode: alphabet gains U+00E9, L may be it")
    a = ap.parse_args()
    global ALPH, SUBJ, LITS, UTFMODE
    if a.utf8:
        ALPH, SUBJ, UTFMODE = "abX\u00e9", "aabXX\u00e9\u00e9\n", True
        LITS = ["X", "\u00e9", "X\u00e9", "\u00e9a", "aa", "a"]
    tot, bad, wit, reasons, stats = run(a.n, a.seed, True)
    print("# rinner_model.py: libpcre2 %s (Homebrew, the Mac's local; NOT the 10.46 reference), seed %d, "
          "%d generated R = P.L.S%s" % (version(), a.seed, a.n, ", UTF mode" if a.utf8 else ""))
    print("cases compiled %d (uncompilable %d); gate applies %d" % (tot["cases"], tot["uncompilable"], tot["gated"]))
    print("gate reasons: " + ", ".join("%s %d" % kv for kv in sorted(reasons.items())))
    print("%-22s %10s %10s  %s" % ("variant", "checks", "mismatch", "first witness (R, subject, startpos, truth, model)"))
    keys = []
    for v in VARIANTS:
        keys += sorted(k for k in tot if k == v or k.startswith(v + "[") or k == v + "/findall")
    for k in dict.fromkeys(keys):
            if tot[k] == 0: continue
            w = wit.get(k, "")
            print("%-22s %10d %10d  %s" % (k, tot[k], bad[k], w if bad[k] else ""))
    print("reverse-walk bytes over accepted candidates (tactic+mutants): %d; rust-guard fallbacks: %d"
          % (stats["walk"], stats["rust_guard_fallback"]))
    if a.selftest:
        fails = []
        for v in ("tactic", "lowerbound", "rust_guard", "fallback", "c_end"):
            if bad[v] or bad[v + "/findall"]:
                fails.append("the gated %s disagrees with libpcre2" % v)
        for v in VARIANTS:
            if v in UNGATED or v in ("tactic", "lowerbound", "rust_guard", "fallback", "c_end"): continue
            if bad[v] + bad[v + "/findall"] == 0:
                fails.append("mutation %s NOT detected" % v)
        if sum(n for k, n in bad.items() if k.startswith("gate_off[")) == 0:
            fails.append("the ungated tactic was never wrong: the gate is not shown necessary")
        print("selftest: " + ("PASS" if not fails else "FAIL: " + "; ".join(fails)))
        sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
