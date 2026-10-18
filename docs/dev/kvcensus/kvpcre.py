"""kvcensus: the INDEPENDENT control, libpcre2-8 (10.46 on the dev box) through
ctypes. It shares no source with pcrec's DFA reader (kvdfa.py): every claim the
machine reading makes about a site's language is re-asked of PCRE2 on concrete
strings.

  is_prefix(w, ctx)   w is a prefix of some match beginning at the origin
                      (anchored at offset len(ctx) of ctx+w, hard partial
                      matching: PARTIAL, or a complete match ending at |w|)
  match_len(w, ctx)   the anchored match length at the origin, or None

Env PCRE2_LIB overrides the library path.
"""
import ctypes, os

LIB = os.environ.get("PCRE2_LIB", "/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0")
CASELESS, UTF = 0x00000008, 0x00080000
ANCHORED, PARTIAL_HARD = 0x80000000, 0x00000020
ERROR_PARTIAL = -2

_l = ctypes.CDLL(LIB)
_l.pcre2_compile_8.restype = ctypes.c_void_p
_l.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
                               ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t),
                               ctypes.c_void_p]
_l.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
_l.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
_l.pcre2_match_8.restype = ctypes.c_int
_l.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t,
                             ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
_l.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
_l.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
_l.pcre2_code_free_8.argtypes = [ctypes.c_void_p]
_l.pcre2_match_data_free_8.argtypes = [ctypes.c_void_p]


def _missing(w):
    """continuation bytes the last UTF-8 character of w still needs"""
    for k in range(1, min(4, len(w)) + 1):
        c = w[-k]
        if c < 0x80:
            return 0
        if c >= 0xC0:
            n = 2 if c < 0xE0 else 3 if c < 0xF0 else 4
            return max(0, n - k)
    return 0


class Pat:
    def __init__(self, pat, icase=False, utf8=False):
        e, o = ctypes.c_int(), ctypes.c_size_t()
        fl = (CASELESS if icase else 0) | (UTF if utf8 else 0)
        self.code = _l.pcre2_compile_8(pat, len(pat), fl, ctypes.byref(e), ctypes.byref(o), None)
        self.utf8 = utf8
        self.md = _l.pcre2_match_data_create_from_pattern_8(self.code, None) if self.code else None

    def ok(self):
        return bool(self.code)

    def _m(self, subj, start, opts):
        rc = _l.pcre2_match_8(self.code, subj, len(subj), start, opts, self.md, None)
        if rc >= 0 or rc == ERROR_PARTIAL:
            ov = _l.pcre2_get_ovector_pointer_8(self.md)
            return rc, ov[0], ov[1]
        return rc, None, None

    def is_prefix(self, w, ctx=b""):
        """under UTF a w ending inside a character is completed byte by byte
        (PCRE2 refuses a truncated final character, -3..-5): w is a prefix iff
        one completion is"""
        need = _missing(w) if self.utf8 else 0
        if need:
            return any(self.is_prefix(w + bytes([c]), ctx) for c in range(0x80, 0xC0))
        s = ctx + w
        rc, a, b = self._m(s, len(ctx), ANCHORED | PARTIAL_HARD)
        if rc == ERROR_PARTIAL:
            return True
        return rc >= 0 and b == len(s)

    def match_len(self, w, ctx=b""):
        s = ctx + w
        rc, a, b = self._m(s, len(ctx), ANCHORED)
        return (b - a) if rc >= 0 else None

    def free(self):
        if self.md: _l.pcre2_match_data_free_8(self.md)
        if self.code: _l.pcre2_code_free_8(self.code)


def lang(P, ctxs=(b"",), cap=32, maxprod=256, budget=300000):
    """The language reading of kvdfa.lang(), derived from PCRE2 ALONE, for a
    pattern pcrec has no DFA for (backreferences, lookarounds, atomics): the
    length-j prefixes P_j are ENUMERATED (a prefix under some context in
    `ctxs`), S_j is their next-byte union, and position j is exact while
    |P_j+1| = |P_j| x |S_j|. Position j exists while no w in P_j is itself a
    complete match. Enumeration stops at `maxprod` prefixes or `budget` match
    calls: the result is then a LOWER BOUND (`capped` names where).
    -> dict(S, span, exact, cex, capped, whole)"""
    calls = 0
    Pj = [b""]
    S, exact, cex, capped = [], None, None, ""
    span = cap
    for j in range(cap):
        if any(P.match_len(w, c) is not None and P.match_len(w, c) <= len(w) for w in Pj for c in ctxs):
            span = j
            break
        nxt, per = [], {}
        for w in Pj:
            bs = []
            for b in range(256):
                calls += len(ctxs)
                if any(P.is_prefix(w + bytes([b]), c) for c in ctxs):
                    bs.append(b)
            per[w] = frozenset(bs)
            nxt += [w + bytes([b]) for b in bs]
            if calls > budget:
                break
        if calls > budget:
            capped = "budget@%d" % j
            span = j
            break
        u = frozenset().union(*per.values()) if per else frozenset()
        if not u:
            span = j
            break
        if exact is None and len(set(per.values())) > 1:
            exact = j
            ws = list(per)
            for w1 in ws:
                for w2 in ws:
                    d = per[w1] - per[w2]
                    if d and cex is None:
                        cex = (w1 + bytes([min(d)]), w2 + bytes([min(d)]))
        S.append(u)
        if len(nxt) > maxprod:
            capped = "maxprod@%d" % (j + 1)
            span = j + 1
            break
        Pj = nxt
    if exact is None:
        exact = span
    whole = 0
    if not capped and exact == span and 0 < span < cap and Pj and len(Pj[0]) == span:
        if all(P.match_len(w + b"\x00") == span for w in Pj) and \
           not any(P.is_prefix(w + bytes([b])) for w in Pj[:8] for b in range(256)):
            whole = span
    return dict(S=S, span=span, exact=exact, cex=cex, capped=capped, whole=whole)


def contexts(P):
    """the predecessor contexts the language reading ranges over: the absent
    one, plus ONE representative byte per distinct first-byte signature among
    the 256 single-byte predecessors that admit any start (a width-1 view of
    context: lookbehinds wider than one byte are under-read, a lower bound)."""
    sig = {}
    for c in range(256):
        s = frozenset(b for b in range(256) if P.is_prefix(bytes([b]), bytes([c])))
        if s:
            sig.setdefault(s, bytes([c]))
    out = [b""] + [v for k, v in sig.items()]
    return out
