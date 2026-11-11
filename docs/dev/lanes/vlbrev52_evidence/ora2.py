#!/usr/bin/env python3
"""vlbrev51 oracle: libpcre2 10.46 via the repo's ctypes binding; prints code AND offset.
Input: PATTERN<TAB>subj... ; output: pattern ACCEPT lb=N [subj=match] | REJECT code@offset"""
import ctypes, re, sys
sys.path.insert(0, sys.argv[1])
import pcre2_ctypes as P
L = P._lib
L.pcre2_pattern_info_8.restype = ctypes.c_int
L.pcre2_pattern_info_8.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
print("libpcre2", P.version())
for line in open(sys.argv[2], encoding="utf-8"):
    line = line.rstrip("\n")
    if not line or line.startswith("#"):
        continue
    f = line.split("\t"); pat, subs = f[0], f[1:]
    try:
        c = P.compile(pat, 0)
    except P.Pcre2Error as e:
        m = re.search(r"offset (\d+)", str(e))
        print("%s\tREJECT %s@%s" % (pat, e.code, m.group(1) if m else "?")); continue
    v = ctypes.c_uint32(0)
    L.pcre2_pattern_info_8(c._code, 15, ctypes.byref(v))
    print("%s\tACCEPT lb=%d %s" % (pat, v.value, " ".join("%s=%s" % (s, c.search(s, 0)) for s in subs)))
