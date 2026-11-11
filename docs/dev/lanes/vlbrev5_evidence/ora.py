#!/usr/bin/env python3
"""vlbrev5 oracle cells: libpcre2 10.46 via the repo's ctypes binding.
Input lines: PATTERN<TAB>subj1<TAB>subj2...  ('u:' prefix on the pattern = PCRE2_UTF)
Output: pattern  ACCEPT lb=N [answers] | REJECT code"""
import ctypes
import sys

sys.path.insert(0, sys.argv[1])
import pcre2_ctypes as P  # noqa: E402

L = P._lib
L.pcre2_pattern_info_8.restype = ctypes.c_int
L.pcre2_pattern_info_8.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
INFO_MAXLOOKBEHIND = 15

print("libpcre2", P.version())
for line in open(sys.argv[2], encoding="utf-8"):
    line = line.rstrip("\n")
    if not line or line.startswith("#"):
        continue
    f = line.split("\t")
    pat, subs = f[0], f[1:]
    opts = 0
    if pat.startswith("u:"):
        opts, pat = P.PCRE2_UTF, pat[2:]
    try:
        c = P.compile(pat.encode("utf-8") if opts else pat, opts)
    except P.Pcre2Error as e:
        print("%s\tREJECT %s" % (line, e.code))
        continue
    v = ctypes.c_uint32(0)
    L.pcre2_pattern_info_8(c._code, INFO_MAXLOOKBEHIND, ctypes.byref(v))
    out = []
    for s in subs:
        m = c.search(s.encode("utf-8") if opts else s, 0)
        out.append("%s=%s" % (s, m))
    print("%s\tACCEPT lb=%d %s" % (pat, v.value, " ".join(out)))
