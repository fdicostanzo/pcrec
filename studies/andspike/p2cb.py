"""p2cb.py -- a minimal ctypes binding to libpcre2-8 WITH callouts.

Built only from the installed pcre2.h and the pcre2api/pcre2callout man pages
(D181: PCRE2 source is off-limits). Default library: the 10.49 oracle build
under $PCREC_TMPDIR/oracle/pcre2-10.49/install; override with ANDSPIKE_PCRE2.
"""
import ctypes as C
import os

_TMP = os.environ.get("PCREC_TMPDIR", "/var/tmp/pcrec-" + os.environ.get("USER", "pcrec"))
LIBPATH = os.environ.get("ANDSPIKE_PCRE2",
                         os.path.join(_TMP, "oracle", "pcre2-10.49", "install", "lib", "libpcre2-8.so"))
_lib = C.CDLL(LIBPATH)

# pcre2.h constants (installed header).
ANCHORED = 0x80000000
CASELESS = 0x00000008
DOTALL = 0x00000020
NO_AUTO_POSSESS = 0x00004000
NO_DOTSTAR_ANCHOR = 0x00008000
NO_START_OPTIMIZE = 0x00010000
UTF = 0x00080000
ERROR_NOMATCH = -1
ERROR_CALLOUT = -37
ERROR_MATCHLIMIT = -47
ERROR_DEPTHLIMIT = -53
ERROR_HEAPLIMIT = -63
UNSET = (1 << 64) - 1
CALLOUT_STARTMATCH = 1
CALLOUT_BACKTRACK = 2

# pcre2callout "Missing callouts": every optimization that can skip a callout.
NO_OPT = NO_AUTO_POSSESS | NO_START_OPTIMIZE | NO_DOTSTAR_ANCHOR

SIZE = C.c_size_t
SPTR = C.c_char_p


class CalloutBlock(C.Structure):
    # Field order is the installed header's, not the man page's list.
    _fields_ = [
        ("version", C.c_uint32),
        ("callout_number", C.c_uint32),
        ("capture_top", C.c_uint32),
        ("capture_last", C.c_uint32),
        ("offset_vector", C.POINTER(SIZE)),
        ("mark", C.c_void_p),
        ("subject", C.c_void_p),
        ("subject_length", SIZE),
        ("start_match", SIZE),
        ("current_position", SIZE),
        ("pattern_position", SIZE),
        ("next_item_length", SIZE),
        ("callout_string_offset", SIZE),
        ("callout_string_length", SIZE),
        ("callout_string", C.c_void_p),
        ("callout_flags", C.c_uint32),
    ]


CALLOUT_FN = C.CFUNCTYPE(C.c_int, C.POINTER(CalloutBlock), C.c_void_p)

_lib.pcre2_compile_8.restype = C.c_void_p
_lib.pcre2_compile_8.argtypes = [C.c_char_p, SIZE, C.c_uint32, C.POINTER(C.c_int),
                                 C.POINTER(SIZE), C.c_void_p]
_lib.pcre2_code_free_8.argtypes = [C.c_void_p]
_lib.pcre2_match_data_create_from_pattern_8.restype = C.c_void_p
_lib.pcre2_match_data_create_from_pattern_8.argtypes = [C.c_void_p, C.c_void_p]
_lib.pcre2_match_data_free_8.argtypes = [C.c_void_p]
_lib.pcre2_match_8.restype = C.c_int
_lib.pcre2_match_8.argtypes = [C.c_void_p, C.c_char_p, SIZE, SIZE, C.c_uint32,
                               C.c_void_p, C.c_void_p]
_lib.pcre2_get_ovector_pointer_8.restype = C.POINTER(SIZE)
_lib.pcre2_get_ovector_pointer_8.argtypes = [C.c_void_p]
_lib.pcre2_get_ovector_count_8.restype = C.c_uint32
_lib.pcre2_get_ovector_count_8.argtypes = [C.c_void_p]
_lib.pcre2_match_context_create_8.restype = C.c_void_p
_lib.pcre2_match_context_create_8.argtypes = [C.c_void_p]
_lib.pcre2_match_context_free_8.argtypes = [C.c_void_p]
_lib.pcre2_set_callout_8.restype = C.c_int
_lib.pcre2_set_callout_8.argtypes = [C.c_void_p, CALLOUT_FN, C.c_void_p]
_lib.pcre2_set_match_limit_8.argtypes = [C.c_void_p, C.c_uint32]
_lib.pcre2_set_depth_limit_8.argtypes = [C.c_void_p, C.c_uint32]
_lib.pcre2_get_error_message_8.restype = C.c_int
_lib.pcre2_get_error_message_8.argtypes = [C.c_int, C.c_char_p, SIZE]


class Pcre2Error(Exception):
    pass


def errmsg(code):
    buf = C.create_string_buffer(256)
    _lib.pcre2_get_error_message_8(code, buf, 256)
    return buf.value.decode("latin-1")


def version():
    _lib.pcre2_config_8.restype = C.c_int
    buf = C.create_string_buffer(64)
    _lib.pcre2_config_8(11, buf)  # PCRE2_CONFIG_VERSION
    return buf.value.decode()


class Code:
    """A compiled pattern. `pat` is bytes (UTF-8 when opts has UTF)."""

    def __init__(self, pat, opts=0):
        if isinstance(pat, str):
            pat = pat.encode("utf-8" if opts & UTF else "latin-1")
        err = C.c_int(0)
        off = SIZE(0)
        self.ptr = _lib.pcre2_compile_8(pat, len(pat), opts, C.byref(err), C.byref(off), None)
        if not self.ptr:
            raise Pcre2Error("compile error %d at %d: %s (%r)" % (err.value, off.value, errmsg(err.value), pat))
        self.pat = pat

    def __del__(self):
        if getattr(self, "ptr", None):
            _lib.pcre2_code_free_8(self.ptr)
            self.ptr = None

    def match(self, subj, start=0, opts=0, callout=None, match_limit=None, depth_limit=None):
        """Run pcre2_match. callout(block) -> int (0 continue, >0 fail here,
        <0 abandon). Returns (rc, ovector-as-list-of-pairs or None)."""
        md = _lib.pcre2_match_data_create_from_pattern_8(self.ptr, None)
        mc = _lib.pcre2_match_context_create_8(None)
        keep = None
        try:
            if callout is not None:
                def _cb(blk, _data):
                    try:
                        return int(callout(blk.contents))
                    except Exception as e:  # never let an exception look like "continue"
                        _cb.exc = e
                        return ERROR_CALLOUT
                _cb.exc = None
                keep = CALLOUT_FN(_cb)
                _lib.pcre2_set_callout_8(mc, keep, None)
            if match_limit is not None:
                _lib.pcre2_set_match_limit_8(mc, match_limit)
            if depth_limit is not None:
                _lib.pcre2_set_depth_limit_8(mc, depth_limit)
            rc = _lib.pcre2_match_8(self.ptr, subj, len(subj), start, opts, md, mc)
            if callout is not None and _cb.exc is not None:
                raise _cb.exc
            ov = None
            if rc > 0:
                p = _lib.pcre2_get_ovector_pointer_8(md)
                n = _lib.pcre2_get_ovector_count_8(md)
                ov = [(None if p[2 * k] == UNSET else p[2 * k],
                       None if p[2 * k + 1] == UNSET else p[2 * k + 1]) for k in range(n)]
            return rc, ov
        finally:
            _lib.pcre2_match_context_free_8(mc)
            _lib.pcre2_match_data_free_8(md)


def caps_of(blk):
    """Capture pairs visible at a callout: groups 1..capture_top-1."""
    ov = blk.offset_vector
    out = []
    for k in range(1, blk.capture_top):
        a, b = ov[2 * k], ov[2 * k + 1]
        out.append(None if a == UNSET else (a, b))
    return out
