#!/usr/bin/env python3
"""probe_misc.py [LIBPATH] -- the point probes §B cites: caseless x UCP,
UCP WITHOUT UTF (the Latin-1 reading a (*UCP) under -e byte would owe),
the start-of-pattern verbs, and 10.43+'s per-escape ASCII restrictions.
Prints first-match span (or nomatch / compile error) per row.  Writes
nothing; runnable over ssh stdin."""
import ctypes, ctypes.util, sys
lib = ctypes.CDLL(sys.argv[1] if len(sys.argv) > 1 else
                  (ctypes.util.find_library("pcre2-8") or "libpcre2-8.so.0"))
F = {"UTF": 0x00080000, "UCP": 0x00020000, "I": 0x00000008}
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
buf = ctypes.create_string_buffer(256); lib.pcre2_config_8(11, buf)
print("#version", buf.value.decode())
ROWS = [
  # (flags, pattern bytes, subject bytes, what the row asks)
  ("UTF", "(?i)é".encode(), "É".encode(), "caseless e-acute, UTF only"),
  ("UTF|UCP", "(?i)é".encode(), "É".encode(), "caseless e-acute, UTF|UCP"),
  ("", b"(?i)\xe9", b"\xc9", "caseless 0xE9 vs 0xC9, bytes, no UCP"),
  ("UCP", b"(?i)\xe9", b"\xc9", "caseless 0xE9 vs 0xC9, bytes, UCP no UTF"),
  ("UTF", b"(?i)k", "K".encode(), "caseless k vs KELVIN SIGN, UTF only"),
  ("UTF|UCP", b"(?i)k", "K".encode(), "caseless k vs KELVIN SIGN, UTF|UCP"),
  ("UTF", b"(?i)[a-z]", "ſ".encode(), "caseless [a-z] vs LONG S, UTF only"),
  ("UTF", b"(?i)[[:lower:]]", "É".encode(), "caseless [:lower:] vs E-acute cap, UTF"),
  ("UTF|UCP", b"(?i)[[:lower:]]", "É".encode(), "caseless [:lower:] vs E-acute cap, UTF|UCP"),
  ("UTF|UCP", b"(?i)[[:lower:]]", b"A", "caseless [:lower:] vs A, UTF|UCP"),
  ("UTF", b"(?i)[[:lower:]]", b"A", "caseless [:lower:] vs A, UTF"),
  ("UTF|UCP", b"(?i)\\p{Ll}", b"A", "caseless \\p{Ll} vs A, UTF|UCP"),
  ("UTF|UCP", b"(?i)\\w", "É".encode(), "caseless \\w, UTF|UCP (control)"),
  ("", b"\\w", b"\xe9", "\\w vs byte 0xE9, no flags"),
  ("UCP", b"\\w", b"\xe9", "\\w vs byte 0xE9, UCP no UTF (Latin-1 e-acute)"),
  ("UCP", b"\\d", b"\xb2", "\\d vs byte 0xB2 superscript two, UCP no UTF"),
  ("UCP", b"\\s", b"\xa0", "\\s vs byte 0xA0 NBSP, UCP no UTF"),
  ("", b"\\s", b"\x85", "\\s vs byte 0x85 NEL, no flags"),
  ("UCP", b"\\s", b"\x85", "\\s vs byte 0x85 NEL, UCP no UTF"),
  ("UCP", b"x\\b", b"x\xe9", "\\b between x and 0xE9, UCP no UTF"),
  ("", b"x\\b", b"x\xe9", "\\b between x and 0xE9, no flags"),
  ("UTF", b"(*UCP)\\w", "é".encode(), "(*UCP) verb under UTF"),
  ("", b"(*UCP)\\w", b"\xe9", "(*UCP) verb, bytes (no UTF)"),
  ("", b"(*UTF)(*UCP)\\w", "é".encode(), "(*UTF)(*UCP) both verbs"),
  ("", b"(*UCP)(*UTF)\\w", "é".encode(), "(*UCP)(*UTF) order swapped"),
  ("UTF", b"a(*UCP)\\w", "aé".encode(), "(*UCP) not at start"),
  ("UTF", b"(?i)(*UCP)\\w", "é".encode(), "(*UCP) after an option setting"),
  ("UTF|UCP", b"(?aD)\\d", "٣".encode(), "(?aD): \\d ASCII under UCP"),
  ("UTF|UCP", b"(?aW)\\w", "é".encode(), "(?aW): \\w ASCII under UCP"),
  ("UTF|UCP", b"(?aS)\\s", " ".encode(), "(?aS): \\s ASCII under UCP"),
  ("UTF|UCP", b"(?aW)x\\b", "xé".encode(), "(?aW): does \\b follow the \\w restriction?"),
  ("UTF|UCP", b"(?aP)[[:alpha:]]", "é".encode(), "(?aP): POSIX ASCII under UCP"),
  ("UTF|UCP", b"(?aT)[[:digit:]]", "٣".encode(), "(?aT): [:digit:] ASCII, rest UCP"),
  ("UTF|UCP", b"(?a)\\w", "é".encode(), "(?a): all ASCII restrictions"),
  ("UTF", b"(?-a)\\w", "é".encode(), "(?-a) under UTF only"),
  ("UTF|UCP", b"(?i)(?r)k", "K".encode(), "(?r) caseless-restrict: k vs KELVIN"),
  ("UTF", b"(?i)(?r)k", "\u212a".encode(), "(?r) caseless-restrict, UTF only: k vs KELVIN"),
  ("UTF", b"(?r)(?i)k", "\u212a".encode(), "(?r) before (?i), UTF only"),
  ("UTF", b"(?i)(?r)s", "\u017f".encode(), "(?r) UTF only: s vs LONG S"),
  ("UTF", b"(?i)(?r)[a-z]", "\u212a".encode(), "(?r) UTF only: [a-z] vs KELVIN"),
  ("UTF", "(?i)(?r)\u212a".encode(), b"k", "(?r) UTF only: KELVIN pattern vs k"),
  ("UTF", b"(?i)(?r)\\x{e9}", "\u00c9".encode(), "(?r) UTF only: \\xe9 vs E-acute cap (non-ASCII pair survives)"),
  ("UTF|UCP", "\\bМосква\\b".encode(), " Москва ".encode(), "asr-b-cyr-ucp shape"),
  ("UTF", "\\bМосква\\b".encode(), " Москва ".encode(), "asr-b-cyr shape (no UCP)"),
  ("UTF|UCP", b"\\d{4}", "٣٤٥٦".encode(), "cls-d-ucp shape"),
  ("UTF|UCP", b"a\\sb", "a b".encode(), "cls-s-ucp shape"),
]
md = lib.pcre2_match_data_create_8(4, None)
for fl, pat, subj, what in ROWS:
    opt = 0
    for f in filter(None, fl.split("|")): opt |= F[f]
    e, eo = ctypes.c_int(), ctypes.c_size_t()
    code = lib.pcre2_compile_8(pat, len(pat), opt, ctypes.byref(e), ctypes.byref(eo), None)
    if not code:
        m = ctypes.create_string_buffer(256); lib.pcre2_get_error_message_8(e.value, m, 256)
        res = "COMPILE-ERROR %d @%d: %s" % (e.value, eo.value, m.value.decode())
    else:
        rc = lib.pcre2_match_8(code, subj, len(subj), 0, 0, md, None)
        if rc >= 0:
            ov = lib.pcre2_get_ovector_pointer_8(md); res = "match (%d,%d)" % (ov[0], ov[1])
        else: res = "nomatch" if rc == -1 else "match-error %d" % rc
    print("%-8s %-28r %-22r %-40s %s" % (fl or "-", pat, subj, what, res))
