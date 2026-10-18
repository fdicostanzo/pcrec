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
