#!/usr/bin/env python3
"""oracle.py -- libpcre2 answers for (pattern, options) x cases.tsv, written
as `idx from rc start end` rows.  ctypes on the local libpcre2-8 (the design's
probes established 10.46 == 10.48 on every relation used here; a 10.46
confirmation run over ssh is a separate, light step -- see run_oracle_remote).

rc: 1 match, 0 no match, otherwise `E<code>`.  Options: UTF|MIU always
(pcrec's ruled ill-formed semantics is MATCH_INVALID_UTF's), UCP on request.
"""
import ctypes
import ctypes.util
import os
import struct
import sys

F = {"UTF": 0x00080000, "UCP": 0x00020000, "MIU": 0x04000000}


def load(path=None):
    cands = [path] if path else ["/opt/homebrew/lib/libpcre2-8.dylib", ctypes.util.find_library("pcre2-8"), "libpcre2-8.so.0"]
    for c in cands:
        if c and (os.path.exists(c) or not c.startswith("/")):
            try:
                return ctypes.CDLL(c)
            except OSError:
                pass
    raise SystemExit("no libpcre2-8")


def setup(lib):
    lib.pcre2_compile_8.restype = ctypes.c_void_p
    lib.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
    lib.pcre2_match_data_create_8.restype = ctypes.c_void_p
    lib.pcre2_match_data_create_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
    lib.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t,
                                  ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
    lib.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
    lib.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
    lib.pcre2_get_error_message_8.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_size_t]


def version(lib):
    buf = ctypes.create_string_buffer(64)
    lib.pcre2_config_8(11, buf)
    return buf.value.decode()


def read_subjects(path):
    b = open(path, "rb").read()
    n = struct.unpack_from("<I", b, 0)[0]
    p = 4
    subs = []
    for _ in range(n):
        L = struct.unpack_from("<I", b, p)[0]
        p += 4
        subs.append(b[p:p + L])
        p += L
    return subs


def answers(lib, pattern, flags, subs, cases):
    setup(lib)
    opt = 0
    for f in flags.split("|"):
        opt |= F[f]
    e, eo = ctypes.c_int(), ctypes.c_size_t()
    code = lib.pcre2_compile_8(pattern, len(pattern), opt, ctypes.byref(e), ctypes.byref(eo), None)
    if not code:
        m = ctypes.create_string_buffer(256)
        lib.pcre2_get_error_message_8(e.value, m, 256)
        raise SystemExit("compile error %d at %d: %s" % (e.value, eo.value, m.value.decode()))
    md = lib.pcre2_match_data_create_8(4, None)
    out = []
    for (i, fr) in cases:
        s = subs[i]
        rc = lib.pcre2_match_8(code, s, len(s), fr, 0, md, None)
        if rc >= 0:
            ov = lib.pcre2_get_ovector_pointer_8(md)
            out.append((i, fr, "1", ov[0], ov[1]))
        elif rc == -1:
            out.append((i, fr, "0", -1, -1))
        else:
            out.append((i, fr, "E%d" % rc, -1, -1))
    return out


def read_cases(path):
    return [tuple(map(int, l.split("\t"))) for l in open(path)]


if __name__ == "__main__":
    pat, flags, subj, cases = sys.argv[1:5]
    lib = load()
    print("#libpcre2", version(lib), file=sys.stderr)
    for r in answers(lib, pat.encode(), flags, read_subjects(subj), read_cases(cases)):
        print("\t".join(map(str, r)))
