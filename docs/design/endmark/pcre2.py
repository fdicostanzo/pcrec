"""Minimal ctypes binding to libpcre2-8 (the reference oracle, 10.46 on the
Linux dev box). compile(pattern, utf) -> Code; Code.match(subject, start) ->
None or a list of (start, end) pairs (-1, -1 for an unset group)."""
import ctypes, ctypes.util

_lib = ctypes.CDLL(ctypes.util.find_library("pcre2-8") or "libpcre2-8.so.0")
_lib.pcre2_compile_8.restype = ctypes.c_void_p
_lib.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
                                 ctypes.POINTER(ctypes.c_int),
                                 ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
_lib.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
_lib.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
_lib.pcre2_match_8.restype = ctypes.c_int
_lib.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t,
                               ctypes.c_size_t, ctypes.c_uint32, ctypes.c_void_p,
                               ctypes.c_void_p]
_lib.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
_lib.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
_lib.pcre2_get_ovector_count_8.restype = ctypes.c_uint32
_lib.pcre2_get_ovector_count_8.argtypes = [ctypes.c_void_p]
_lib.pcre2_config_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]

UTF = 0x00080000
MULTILINE = 0x00000400
NO_START_OPTIMIZE = 0x00010000   # keep lookahead/\K oddities from start-opt shortcuts
UNSET = (1 << 64) - 1


def version():
    buf = ctypes.create_string_buffer(64)
    _lib.pcre2_config_8(11, buf)   # PCRE2_CONFIG_VERSION
    return buf.value.decode()


class Code:
    def __init__(self, pattern, utf=False, extra=0):
        if isinstance(pattern, str):
            pattern = pattern.encode()
        err = ctypes.c_int(); off = ctypes.c_size_t()
        opts = (UTF if utf else 0) | extra
        self.code = _lib.pcre2_compile_8(pattern, len(pattern), opts,
                                         ctypes.byref(err), ctypes.byref(off), None)
        if not self.code:
            raise ValueError("pcre2 compile failed (%d at %d): %r" % (err.value, off.value, pattern))
        self.md = _lib.pcre2_match_data_create_from_pattern_8(self.code, None)
        self.pattern = pattern

    def match(self, subject, start):
        rc = _lib.pcre2_match_8(self.code, subject, len(subject), start, 0, self.md, None)
        if rc == -1:
            return None
        if rc < 0:
            raise RuntimeError("pcre2 match error %d on %r" % (rc, self.pattern))
        ov = _lib.pcre2_get_ovector_pointer_8(self.md)
        n = _lib.pcre2_get_ovector_count_8(self.md)
        out = []
        for i in range(n):
            a, b = ov[2 * i], ov[2 * i + 1]
            out.append((-1, -1) if a == UNSET else (a, b))
        return out
