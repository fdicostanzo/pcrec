"""
Minimal ctypes binding onto the system libpcre2-8 (8-bit) runtime, for use as
the D27 oracle for pcrec's `assertions` module. No pcre2.h is available on
this box (no libpcre2-dev), so this binds the exported symbols directly by
name/signature rather than going through the C header. Only the handful of
entry points needed for compile + match are declared; opaque pointers
(pcre2_code*, pcre2_match_data*) are carried as plain c_void_p and never
dereferenced from Python.

options is always 0 for both compile and match, per the project brief
(pinned: no compile or match options), EXCEPT PCRE2_CASELESS when a test
block's `flags i` directive is honoured (kept for parity with the existing
corpus convention even though the assertions corpus does not lean on it).
"""
import ctypes
import ctypes.util

_LIBPATH = "/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0"
_lib = ctypes.CDLL(_LIBPATH)

PCRE2_ZERO_TERMINATED = ctypes.c_size_t(-1)
PCRE2_UNSET = (1 << 64) - 1  # (PCRE2_SIZE)-1, all-bits-set on a 64-bit size_t
PCRE2_CASELESS = 0x00000008
PCRE2_ERROR_NOMATCH = -1

_lib.pcre2_compile_8.restype = ctypes.c_void_p
_lib.pcre2_compile_8.argtypes = [
    ctypes.c_char_p,               # pattern
    ctypes.c_size_t,               # length
    ctypes.c_uint32,               # options
    ctypes.POINTER(ctypes.c_int),  # errorcode out
    ctypes.POINTER(ctypes.c_size_t),  # erroroffset out
    ctypes.c_void_p,               # compile context (NULL)
]

_lib.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
_lib.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

_lib.pcre2_match_8.restype = ctypes.c_int
_lib.pcre2_match_8.argtypes = [
    ctypes.c_void_p,   # code
    ctypes.c_char_p,   # subject
    ctypes.c_size_t,   # length
    ctypes.c_size_t,   # startoffset
    ctypes.c_uint32,   # options
    ctypes.c_void_p,   # match_data
    ctypes.c_void_p,   # match context (NULL)
]

_lib.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
_lib.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]

_lib.pcre2_get_ovector_count_8.restype = ctypes.c_uint32
_lib.pcre2_get_ovector_count_8.argtypes = [ctypes.c_void_p]

_lib.pcre2_code_free_8.restype = None
_lib.pcre2_code_free_8.argtypes = [ctypes.c_void_p]

_lib.pcre2_match_data_free_8.restype = None
_lib.pcre2_match_data_free_8.argtypes = [ctypes.c_void_p]

_lib.pcre2_get_error_message_8.restype = ctypes.c_int
_lib.pcre2_get_error_message_8.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_size_t]


class Pcre2CompileError(Exception):
    def __init__(self, errorcode, erroroffset, message):
        self.errorcode = errorcode
        self.erroroffset = erroroffset
        self.message = message
        super().__init__(f"PCRE2 compile error {errorcode} at offset {erroroffset}: {message}")


def _error_message(code):
    buf = ctypes.create_string_buffer(256)
    _lib.pcre2_get_error_message_8(code, buf, 256)
    return buf.value.decode("latin-1", errors="replace")


def compiles(pattern: bytes, caseless: bool = False):
    """Return True iff libpcre2 accepts `pattern` at options=0 (or CASELESS)."""
    options = PCRE2_CASELESS if caseless else 0
    errcode = ctypes.c_int(0)
    erroff = ctypes.c_size_t(0)
    code = _lib.pcre2_compile_8(pattern, len(pattern), options,
                                 ctypes.byref(errcode), ctypes.byref(erroff), None)
    if code:
        _lib.pcre2_code_free_8(code)
        return True
    return False


def compile_error(pattern: bytes, caseless: bool = False):
    """Return (errorcode, erroroffset, message) if pattern is REJECTED, else None."""
    options = PCRE2_CASELESS if caseless else 0
    errcode = ctypes.c_int(0)
    erroff = ctypes.c_size_t(0)
    code = _lib.pcre2_compile_8(pattern, len(pattern), options,
                                 ctypes.byref(errcode), ctypes.byref(erroff), None)
    if code:
        _lib.pcre2_code_free_8(code)
        return None
    return (errcode.value, erroff.value, _error_message(errcode.value))


def match(pattern: bytes, subject: bytes, startpos: int = 0, caseless: bool = False):
    """
    Compile `pattern` and match against `subject[startpos:]` (PCRE2 semantics:
    startoffset, not a sliced subject -- ^ and \\A/\\G etc. see the whole
    subject and the real startoffset, exactly like pcrec's startpos).

    Returns None on no-match, or a list of (start, end) tuples (or None for
    an unset group) indexed by capture slot, slot 0 = whole match, on match.
    Raises Pcre2CompileError if the pattern itself is rejected -- callers
    doing perr-style checks should catch this instead of calling match().
    """
    options = PCRE2_CASELESS if caseless else 0
    errcode = ctypes.c_int(0)
    erroff = ctypes.c_size_t(0)
    code = _lib.pcre2_compile_8(pattern, len(pattern), options,
                                 ctypes.byref(errcode), ctypes.byref(erroff), None)
    if not code:
        raise Pcre2CompileError(errcode.value, erroff.value, _error_message(errcode.value))
    try:
        md = _lib.pcre2_match_data_create_from_pattern_8(code, None)
        if not md:
            raise RuntimeError("pcre2_match_data_create_from_pattern_8 failed")
        try:
            rc = _lib.pcre2_match_8(code, subject, len(subject), startpos, 0, md, None)
            if rc == PCRE2_ERROR_NOMATCH:
                return None
            if rc < 0:
                raise RuntimeError(f"pcre2_match_8 error {rc}: {_error_message(rc)}")
            ovec = _lib.pcre2_get_ovector_pointer_8(md)
            ovcount = _lib.pcre2_get_ovector_count_8(md)
            # rc == 0 means the ovector was too small to hold all captured
            # substrings; ovcount pairs were still written. We size to
            # ovcount either way (match_data_create_from_pattern sizes the
            # ovector to the pattern's own group count + 1, so rc == 0
            # should not arise here, but handle it rather than assume).
            npairs = ovcount
            out = []
            for i in range(npairs):
                s = ovec[2 * i]
                e = ovec[2 * i + 1]
                if s == PCRE2_UNSET or e == PCRE2_UNSET:
                    out.append(None)
                else:
                    out.append((s, e))
            return out
        finally:
            _lib.pcre2_match_data_free_8(md)
    finally:
        _lib.pcre2_code_free_8(code)


def group_count(pattern: bytes, caseless: bool = False) -> int:
    """Number of capturing groups PCRE2 sees in `pattern` (0 if none)."""
    options = PCRE2_CASELESS if caseless else 0
    errcode = ctypes.c_int(0)
    erroff = ctypes.c_size_t(0)
    code = _lib.pcre2_compile_8(pattern, len(pattern), options,
                                 ctypes.byref(errcode), ctypes.byref(erroff), None)
    if not code:
        raise Pcre2CompileError(errcode.value, erroff.value, _error_message(errcode.value))
    try:
        md = _lib.pcre2_match_data_create_from_pattern_8(code, None)
        try:
            return _lib.pcre2_get_ovector_count_8(md) - 1
        finally:
            _lib.pcre2_match_data_free_8(md)
    finally:
        _lib.pcre2_code_free_8(code)
