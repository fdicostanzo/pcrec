"""libpcre2-8 reference for the differential cases (ctypes, no build step).

ref(pattern, flags, template, subject, limit, unset, gaps=True) ->
    dict(kind='ok', out=bytes, n=int)            substitution succeeded
    dict(kind='err', code=int, where=str)        compile or substitute error

limit: 'all' | int.  0 is pcrec-only (copies the subject).  1 is the
non-global call; N>1 is GLOBAL with a substitute callout that rejects the
(N+1)th match with a negative return (pcre2api "Substitution callouts":
the rest of the input is copied and the call returns the count so far).
gaps=False maps to PCRE2_SUBSTITUTE_REPLACEMENT_ONLY.
"""
import ctypes as C
import os

# D98: the library tests/lib/resolve_pcre2.sh resolved (run_d27.sh sources it
# and it exports PCREC_PCRE2_PATH), so this binding and the C drivers read one
# copy; the bare SONAME only where the resolver had no libdir to name.
L = C.CDLL(os.environ.get('PCREC_PCRE2_PATH') or 'libpcre2-8.so.0')
UTF, UCP, CASELESS, MIU, DUPNAMES = 0x80000, 0x20000, 0x8, 0x04000000, 0x40
S_GLOBAL, S_UNSET_EMPTY, S_OVF, S_REPONLY = 0x100, 0x400, 0x1000, 0x20000
SZ = C.c_size_t
L.pcre2_compile_8.restype = C.c_void_p
L.pcre2_compile_8.argtypes = [C.c_char_p, SZ, C.c_uint32, C.POINTER(C.c_int), C.POINTER(SZ), C.c_void_p]
L.pcre2_match_data_create_from_pattern_8.restype = C.c_void_p
L.pcre2_match_data_create_from_pattern_8.argtypes = [C.c_void_p, C.c_void_p]
L.pcre2_match_context_create_8.restype = C.c_void_p
L.pcre2_match_context_create_8.argtypes = [C.c_void_p]
L.pcre2_substitute_8.restype = C.c_int
L.pcre2_substitute_8.argtypes = [C.c_void_p, C.c_char_p, SZ, SZ, C.c_uint32, C.c_void_p, C.c_void_p,
                                 C.c_char_p, SZ, C.c_char_p, C.POINTER(SZ)]
CB = C.CFUNCTYPE(C.c_int, C.c_void_p, C.c_void_p)
L.pcre2_set_substitute_callout_8.argtypes = [C.c_void_p, CB, C.c_void_p]
L.pcre2_code_free_8.argtypes = [C.c_void_p]
L.pcre2_match_data_free_8.argtypes = [C.c_void_p]
L.pcre2_match_context_free_8.argtypes = [C.c_void_p]


class _Blk(C.Structure):
    _fields_ = [('version', C.c_uint32), ('input', C.c_void_p), ('output', C.c_void_p),
                ('output_offsets', C.c_size_t * 2), ('ovector', C.c_void_p), ('oveccount', C.c_uint32),
                ('subscount', C.c_uint32)]


def copts(flags: str) -> int:
    o = 0
    f = flags.split()
    if '-e' in f and f[f.index('-e') + 1] == 'utf8' or '--encoding=utf8' in f:
        o |= UTF | MIU   # -e utf8 alone reads \\w as ASCII (cli.md §1.9¶2)
    if '-i' in f:
        o |= CASELESS
    if '--ucp' in f:
        o |= UCP
    return o


def ref(pattern: bytes, flags: str, template: bytes, subject: bytes, limit, unset: str, gaps=True):
    err, off = C.c_int(), SZ()
    code = L.pcre2_compile_8(pattern, len(pattern), copts(flags), C.byref(err), C.byref(off), None)
    if not code:
        return dict(kind='err', code=err.value, where='compile')
    md = L.pcre2_match_data_create_from_pattern_8(code, None)
    mc = L.pcre2_match_context_create_8(None)
    o = S_OVF | (S_UNSET_EMPTY if unset == 'empty' else 0) | (0 if gaps else S_REPONLY)
    keep = None
    if limit == 'all' or (isinstance(limit, int) and limit > 1):
        o |= S_GLOBAL
    if isinstance(limit, int) and limit > 1:
        lim = limit

        def cb(blk, data):
            return 0 if C.cast(blk, C.POINTER(_Blk)).contents.subscount <= lim else -1
        keep = CB(cb)
        L.pcre2_set_substitute_callout_8(mc, keep, None)
    cap = 1 << 16
    for _ in range(2):
        buf = C.create_string_buffer(cap)
        ol = SZ(cap)
        rc = L.pcre2_substitute_8(code, subject, len(subject), 0, o, md, mc, template, len(template), buf, C.byref(ol))
        if rc == -48 and ol.value > cap:
            cap = ol.value
            continue
        break
    L.pcre2_match_context_free_8(mc)
    L.pcre2_match_data_free_8(md)
    L.pcre2_code_free_8(code)
    if rc < 0:
        return dict(kind='err', code=rc, where='substitute')
    if isinstance(limit, int) and limit > 1:
        rc = min(rc, limit)   # the rejected (limit+1)th match is counted in the return
    return dict(kind='ok', out=buf.raw[:ol.value], n=rc)
