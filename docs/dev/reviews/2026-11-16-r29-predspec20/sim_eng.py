# simulate lens: a small two-engine harness (libpcre2-8 via ctypes + Python re). Whole-value and searched matching.
import ctypes, re, sys
L = ctypes.CDLL("libpcre2-8.so.0")
L.pcre2_compile_8.restype = ctypes.c_void_p
L.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int),
                              ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
L.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
L.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint32,
                            ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_match_data_free_8.argtypes = [ctypes.c_void_p]
L.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
L.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
L.pcre2_substring_number_from_name_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
L.pcre2_config_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
ANCH, ENDANCH = 0x80000000, 0x20000000
UNSET = ctypes.c_size_t(-1).value
_vb = ctypes.create_string_buffer(64)
L.pcre2_config_8(11, _vb)
VER = "libpcre2-8 %s | Python %s" % (_vb.value.decode(), sys.version.split()[0])
_c = {}
DIS = [0]
PROBES = [0]


def code(p):
    if p not in _c:
        e, o = ctypes.c_int(), ctypes.c_size_t()
        c = L.pcre2_compile_8(p.encode(), len(p.encode()), 0, ctypes.byref(e), ctypes.byref(o), None)
        assert c, (p, e.value)
        _c[p] = c
    return _c[p]


def py(p):
    return p.replace("(?<", "(?P<").replace("(?P<=", "(?<=").replace("(?P<!", "(?<!")


def pc(p, t, names, start=0, whole=True, pyok=True):
    """PCRE2 match of p on t (whole: anchored both ends at start..len(t)); returns None or (span, {name: text|None})."""
    c = code(p)
    md = L.pcre2_match_data_create_from_pattern_8(c, None)
    b = t.encode()
    rc = L.pcre2_match_8(c, b, len(b), start, (ANCH | ENDANCH) if whole else 0, md, None)
    out = None
    if rc >= 0:
        ov = L.pcre2_get_ovector_pointer_8(md)
        g = {}
        for nm in names:
            n = L.pcre2_substring_number_from_name_8(c, nm.encode())
            g[nm] = None if ov[2 * n] == UNSET else b[ov[2 * n]:ov[2 * n + 1]].decode()
        out = ((ov[0], ov[1]), g)
    L.pcre2_match_data_free_8(md)
    PROBES[0] += 1
    if pyok:
        m = re.fullmatch(py(p), t) if whole else re.compile(py(p)).search(t, start)
        po = None if m is None else (m.span(), {nm: m.group(nm) for nm in names})
        if po != out:
            DIS[0] += 1
            print("  ENGINE DISAGREEMENT", repr(p), repr(t), out, po)
    return out


def groups(p, t, names, pyok=True):
    r = pc(p, t, names, whole=True, pyok=pyok)
    return None if r is None else r[1]
