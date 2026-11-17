#!/usr/bin/env python3
# Lane rxmodel (2026-11-17): a small ctypes harness on the INSTALLED libpcre2-8 (the library is RUN, never read: the
# D181 wall). It compiles a pattern, runs it in three modes (WHOLE value, SEARCHED first match, FIND-ALL) and serves
# STRING CALLOUTS `(?C"name")` from Python functions: a callout's function sees the captures set at that point
# (by group name), the match's start and the current position, and returns True (continue: callout result 0) or
# False / None (result 1: "fail here", PCRE backtracks to its next choice). A callout may also stand as the condition
# of a conditional group, `(?(?C"name")yes|no)`: result 0 takes `yes`, nonzero takes `no`.
#
# Compile options used for every model: PCRE2_NO_AUTO_POSSESS and PCRE2_NO_START_OPTIMIZE (and NO_DOTSTAR_ANCHOR), so
# no optimization removes a path a callout would see (the pcre2callout documentation names these as the options that
# make callouts see every attempt). selfcheck() verifies the option values BEHAVIOURALLY (callout counts), not from a
# header.
import ctypes, re

L = ctypes.CDLL("libpcre2-8.so.0")
SIZE = ctypes.c_size_t
UNSET = ctypes.c_size_t(-1).value

PCRE2_MATCH_UNSET_BACKREF = 0x00000200
PCRE2_NO_AUTO_POSSESS = 0x00004000
PCRE2_NO_DOTSTAR_ANCHOR = 0x00008000
PCRE2_NO_START_OPTIMIZE = 0x00010000
PCRE2_ANCHORED = 0x80000000
PCRE2_ENDANCHORED = 0x20000000
BASE_OPTS = PCRE2_NO_AUTO_POSSESS | PCRE2_NO_START_OPTIMIZE | PCRE2_NO_DOTSTAR_ANCHOR


class CalloutBlock(ctypes.Structure):          # pcre2callout(3), the documented callout block, versions 0-2
    _fields_ = [("version", ctypes.c_uint32), ("callout_number", ctypes.c_uint32),
                ("capture_top", ctypes.c_uint32), ("capture_last", ctypes.c_uint32),
                ("offset_vector", ctypes.POINTER(SIZE)), ("mark", ctypes.c_char_p),
                ("subject", ctypes.POINTER(ctypes.c_char)), ("subject_length", SIZE),
                ("start_match", SIZE), ("current_position", SIZE), ("pattern_position", SIZE),
                ("next_item_length", SIZE), ("callout_string_offset", SIZE), ("callout_string_length", SIZE),
                ("callout_string", ctypes.POINTER(ctypes.c_char)), ("callout_flags", ctypes.c_uint32)]


CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(CalloutBlock), ctypes.c_void_p)
L.pcre2_compile_8.restype = ctypes.c_void_p
L.pcre2_compile_8.argtypes = [ctypes.c_char_p, SIZE, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(SIZE), ctypes.c_void_p]
L.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
L.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_match_context_create_8.restype = ctypes.c_void_p
L.pcre2_match_context_create_8.argtypes = [ctypes.c_void_p]
L.pcre2_set_callout_8.argtypes = [ctypes.c_void_p, CB, ctypes.c_void_p]
L.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, SIZE, SIZE, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(SIZE)
L.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
L.pcre2_substring_number_from_name_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
L.pcre2_get_error_message_8.argtypes = [ctypes.c_int, ctypes.c_char_p, SIZE]


def version():
    b = ctypes.create_string_buffer(64)
    L.pcre2_config_8(11, b)                     # PCRE2_CONFIG_VERSION
    return b.value.decode()


def errmsg(code):
    b = ctypes.create_string_buffer(256)
    L.pcre2_get_error_message_8(code, b, 256)
    return b.value.decode()


class Ctx:
    """What a callout's Python function sees."""
    def __init__(self, rx, blk):
        self.rx, self.start, self.pos = rx, blk.start_match, blk.current_position
        self.subject = rx._subj
        ov, top = blk.offset_vector, blk.capture_top
        self._caps = {}
        for nm, g in rx.names.items():
            if g < top and ov[2 * g] != UNSET:
                self._caps[nm] = (ov[2 * g], ov[2 * g + 1])
    def get(self, name):
        sp = self._caps.get(name)
        return None if sp is None else self.subject[sp[0]:sp[1]]
    def span(self, name): return self._caps.get(name)
    def stretch(self): return self.subject[self.start:self.pos]


class Pcre:
    """One compiled pattern with its callout functions {name: f(ctx) -> True / False / None}."""
    def __init__(self, pattern, callouts=None, opts=0):
        self.pattern, self.callouts = pattern, dict(callouts or {})
        err, off = ctypes.c_int(0), SIZE(0)
        pb = pattern.encode()
        self.code = L.pcre2_compile_8(pb, len(pb), BASE_OPTS | opts, ctypes.byref(err), ctypes.byref(off), None)
        if not self.code:
            raise ValueError("compile %r at %d: %s" % (pattern, off.value, errmsg(err.value)))
        self.md = L.pcre2_match_data_create_from_pattern_8(self.code, None)
        self.mctx = L.pcre2_match_context_create_8(None)
        self._cb = CB(self._callout)
        L.pcre2_set_callout_8(self.mctx, self._cb, None)
        self.names = {}
        for nm in dict.fromkeys(re.findall(r"\(\?<([A-Za-z_]\w*)>", pattern)):
            g = L.pcre2_substring_number_from_name_8(self.code, nm.encode())
            if g < 0: raise ValueError("name %s: %s" % (nm, errmsg(g)))
            self.names[nm] = g
        self.calls, self._exc = 0, None
    def _callout(self, blkp, _):
        try:
            blk = blkp.contents
            nm = ctypes.string_at(blk.callout_string, blk.callout_string_length).decode() if blk.callout_string else str(blk.callout_number)
            self.calls += 1
            f = self.callouts[nm]
            return 0 if f(Ctx(self, blk)) is True else 1
        except Exception as e:                  # never let a Python error read as "continue"
            self._exc = e
            return -1
    def match(self, s, start=0, opts=0):
        """(start, end, labels) of the match PCRE reports from `start`, or None."""
        self._subj, self._exc = s, None
        sb = s.encode()
        rc = L.pcre2_match_8(self.code, sb, len(sb), start, opts, self.md, self.mctx)
        if self._exc is not None: raise self._exc
        if rc == -1: return None
        if rc < 0: raise RuntimeError("match %r on %r: %s" % (self.pattern, s, errmsg(rc)))
        ov = L.pcre2_get_ovector_pointer_8(self.md)
        labs = {nm: (None if ov[2 * g] == UNSET else s[ov[2 * g]:ov[2 * g + 1]]) for nm, g in self.names.items()}
        return ov[0], ov[1], labs
    def whole(self, s):                         # WHOLE value: anchored at both ends, PCRE backtracks to reach the end
        return self.match(s, 0, PCRE2_ANCHORED | PCRE2_ENDANCHORED) is not None
    def search(self, s, pos=0): return self.match(s, pos)
    def findall(self, s):                       # as the predicate engines do: again from the end; an empty match advances one
        out, pos = [], 0
        while pos <= len(s):
            r = self.match(s, pos)
            if r is None: break
            out.append(r)
            pos = r[1] if r[1] > r[0] else r[1] + 1
        return out


def selfcheck():
    """The option values and the callout mechanism, checked by behaviour."""
    out = []
    c = Pcre(r'a+(?C"t")b', {"t": lambda x: True})
    c.match("aaac"); n_noposs = c.calls
    c2 = Pcre.__new__(Pcre)
    # the same pattern WITHOUT NO_AUTO_POSSESS: a+ before b is made possessive, the callout runs once per start
    err, off = ctypes.c_int(0), SIZE(0); pb = rb'a+(?C"t")b'
    c2.pattern, c2.callouts = pb.decode(), {"t": lambda x: True}
    c2.code = L.pcre2_compile_8(pb, len(pb), PCRE2_NO_START_OPTIMIZE, ctypes.byref(err), ctypes.byref(off), None)
    c2.md = L.pcre2_match_data_create_from_pattern_8(c2.code, None); c2.mctx = L.pcre2_match_context_create_8(None)
    c2._cb = CB(c2._callout); L.pcre2_set_callout_8(c2.mctx, c2._cb, None); c2.names, c2.calls, c2._exc = {}, 0, None
    c2.match("aaac")
    out.append(("NO_AUTO_POSSESS (0x4000): `a+(?C)b` on `aaac` callouts with the option %d, without %d (expect 6 and 3)" % (n_noposs, c2.calls), n_noposs == 6 and c2.calls == 3))
    d = Pcre(r'(?C"t")abc', {"t": lambda x: True}); d.match("xxabd")
    out.append(("NO_START_OPTIMIZE (0x10000): `(?C)abc` on `xxabd` callouts %d (expect 6: every start tried)" % d.calls, d.calls == 6))
    u0 = Pcre(r"(?:(?<a>a)|x)\k<a>b"); u1 = Pcre(r"(?:(?<a>a)|x)\k<a>b", opts=PCRE2_MATCH_UNSET_BACKREF)
    out.append(("MATCH_UNSET_BACKREF (0x200): `(?:(?<a>a)|x)\\k<a>b` on `xb` default %s, with the option %s (expect None, a match)" % (u0.search("xb"), u1.search("xb")), u0.search("xb") is None and u1.search("xb") is not None))
    w = Pcre(r"\d+")
    out.append(("ANCHORED|ENDANCHORED (WHOLE): `\\d+` whole on `12` %s, on `12x` %s, on `x12` %s" % (w.whole("12"), w.whole("12x"), w.whole("x12")), (w.whole("12"), w.whole("12x"), w.whole("x12")) == (True, False, False)))
    return out
