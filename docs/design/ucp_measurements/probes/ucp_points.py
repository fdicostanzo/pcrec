#!/usr/bin/env python3
"""ucp_points.py [LIBPATH] -- POINT PROBES and BOUNDARY STREAMS for the
[UCP] design: caseless x UCP cells the sets probe cannot express, UCP
WITHOUT UTF (the byte tier), (?aW)'s scope over \\b, and \\b/\\B at
ILL-FORMED bytes under PCRE2_MATCH_INVALID_UTF (pcrec's ruled ill-formed
semantics, utf8_design.md s2.6).  A STREAM row runs one ANCHORED
pcre2_match per offset of a zero-width pattern and marks '|' where it
holds.  Writes nothing; runs
over ssh stdin like ucp_sets.py."""
import ctypes, ctypes.util, sys
lib = ctypes.CDLL(sys.argv[1] if len(sys.argv) > 1 else
                  (ctypes.util.find_library("pcre2-8") or "libpcre2-8.so.0"))
F = {"UTF": 0x00080000, "UCP": 0x00020000, "MIU": 0x04000000}
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
lib.pcre2_substitute_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t,
    ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t,
    ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t)]
buf = ctypes.create_string_buffer(64); lib.pcre2_config_8(11, buf)
print("#version", buf.value.decode())
md = lib.pcre2_match_data_create_8(4, None)
def comp(pat, fl):
    opt = 0
    for f in filter(None, fl.split("|")): opt |= F[f]
    e, eo = ctypes.c_int(), ctypes.c_size_t()
    code = lib.pcre2_compile_8(pat, len(pat), opt, ctypes.byref(e), ctypes.byref(eo), None)
    if not code:
        m = ctypes.create_string_buffer(256); lib.pcre2_get_error_message_8(e.value, m, 256)
        return None, "COMPILE-ERROR %d: %s" % (e.value, m.value.decode())
    return code, None
def point(fl, pat, subj, start=0):
    code, err = comp(pat, fl)
    if err: return err
    rc = lib.pcre2_match_8(code, subj, len(subj), start, 0, md, None)
    if rc >= 0:
        ov = lib.pcre2_get_ovector_pointer_8(md); return "match (%d,%d)" % (ov[0], ov[1])
    return "nomatch" if rc == -1 else "match-error %d" % rc
def stream(fl, pat, subj):
    """Per-offset ANCHORED probe of a zero-width pattern: '|' at every
    offset s where a match (s,s) is returned; '?' where the engine returned
    a match NOT at (s,s) (MIU re-positioning); an error code is printed
    inline.  (The first version used one global pcre2_substitute; its
    empty-match advance under MATCH_INVALID_UTF skipped offsets, so it
    under-marked -- recorded in out/CLAUDE.md.)"""
    code, err = comp(pat, fl)
    if err: return err
    r = b""
    for s in range(len(subj) + 1):
        rc = lib.pcre2_match_8(code, subj, len(subj), s, 0x80000000, md, None)
        if rc >= 0:
            ov = lib.pcre2_get_ovector_pointer_8(md)
            r += b"|" if (ov[0], ov[1]) == (s, s) else b"?"
        elif rc != -1: r += ("<%d>" % rc).encode()
        if s < len(subj): r += subj[s:s+1]
    return repr(r)
# vacuity guard for the MIU bit: `a` on 61 FF must MATCH under MIU and ERROR under UTF alone
print("#guard MIU bit:", point("UTF|MIU", b"a", b"a\xff"), "| UTF alone:", point("UTF", b"a", b"a\xff"))
U = lambda s: s.encode()
POINTS = [
 ("UTF|UCP", b"(?i)[[:lower:]]", U("K"), "(?i)[:lower:] vs KELVIN under UCP (parse.c:652's claim)"),
 ("UTF|UCP", b"(?i)[[:upper:]]", U("ſ"), "(?i)[:upper:] vs LONG S under UCP"),
 ("UTF|UCP", b"(?i)\\w", U("K"), "(?i)\\w vs KELVIN under UCP (K is in Xwd anyway)"),
 ("UTF",     b"(?i)\\w", U("K"), "(?i)\\w vs KELVIN, UTF only"),
 ("UTF",     b"(?i)[[:lower:]]", U("K"), "(?i)[:lower:] vs KELVIN, UTF only"),
 ("UTF|UCP", b"(?aW:x\\b)", U("xé"), "(?aW:) scopes \\b: ASCII \\b inside"),
 ("UTF|UCP", b"x\\b", U("xé"), "same without (?aW): UCP \\b"),
 ("UTF|UCP", b"(?aW)x\\B", U("xé"), "(?aW) \\B"),
 # UCP without UTF: the byte tier
 ("UCP", b"(?i)(?r)\xe9", b"\xc9", "byte tier: (?r) keeps the Latin-1 pair"),
 ("UCP", b"(?i)[[:lower:]]", b"A", "byte tier: (?i)[:lower:] inert"),
 ("UCP", b"[[:lower:]]", b"\xe9", "byte tier: [:lower:] has 0xE9"),
 ("UCP", b"[[:alpha:]]", b"\xaa", "byte tier: [:alpha:] has 0xAA (Lo)"),
 ("UCP", b"(?aW)\\w", b"\xe9", "byte tier: (?aW)"),
 ("UCP", b"\\w", b"\xb2", "byte tier: \\w has 0xB2 (No)"),
 ("UCP", b"[[:punct:]]", b"\xa7", "byte tier: [:punct:] has 0xA7 (Po)"),
 ("UCP", b"[[:punct:]]", b"\xa2", "byte tier: [:punct:] lacks 0xA2 (Sc, non-ASCII)"),
 ("UCP", b"(?i)\xb5", U("μ"), "byte tier: MICRO SIGN vs mu (not representable: 2 bytes)"),
 ("UCP", b"(?i)\xff", b"\xff", "byte tier: y-diaeresis self"),
 # MIU mid-character start
 ("UTF|UCP|MIU", b"\\B", U("éa"), "MIU: \\B from start=1 (mid-character)", 1),
 ("UTF|UCP|MIU", b"\\b", U("éé"), "MIU: \\b from start=1 (mid-character)", 1),
]
for row in POINTS:
    fl, pat, subj, what = row[:4]; start = row[4] if len(row) > 4 else 0
    print("POINT %-12s %-22r %-18r s=%d %-58s %s" % (fl, pat, subj, start, what, point(fl, pat, subj, start)))
SUBJECTS = [U("é\xff") [:-1] + b"\xff", b"\xff" + U("é"), U("é") + b"\xffa", b"a\xff" + U("é"),
            b"a\x80b", U("é") + b"\xc3", b"\xc3" + U("é"), U("日") + b"\xe6\x97a",
            b"x\xed\xa0\x80y", b"x\xc0\x80y", U("‿") + b"\xff", b"\xff" + U("́x"),
            U("á é"), U("٣é-x")]
for pat in (b"\\b", b"\\B", b"(?<=\\w)", b"(?!\\w)"):
    for fl in ("UTF|MIU", "UTF|UCP|MIU"):
        for s in SUBJECTS:
            print("STREAM %-12s %-8r %-28r %s" % (fl, pat, s, stream(fl, pat, s)))
