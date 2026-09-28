#!/usr/bin/env python3
"""probe_k70.py [LIBPATH] -- K70's own oracle probe, extending
studies/ucp_study/probe_misc.py's rows with two things it did not cover:
(1) (?r) under BYTE (no UTF at all), across the Latin-1 range, to confirm
    the byte-mode no-op claim rather than assume it; (2) (?aD)/(?aP)/(?aS)/
    (?aT)/(?aW) under UTF ALONE (no UCP) -- pcrec has no UCP support, so
    the question is whether the sub-letter changes anything when \\d/\\w/\\s
    are already ASCII-only, not whether it matches PCRE2's own UCP-mode
    restriction. Prints first-match span (or nomatch / compile error) per
    row. Writes nothing; runnable over ssh stdin, matching probe_misc.py's
    own protocol.
"""
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

ROWS = []

# --- (1) (?r) under BYTE, no UTF at all -----------------------------------
# pcrec's byte-mode fold is the 52-ASCII-letter table (fold.c); (?r)
# restricts crossing the ASCII/non-ASCII boundary, so if the byte fold
# never crosses that boundary to begin with, (?r) has nothing to restrict.
# Sweep every ASCII letter pair (both directions) plus every byte >= 0x80
# against its would-be ASCII partner (there is none -- a byte fold never
# maps 0x80..0xFF to an ASCII letter or back), with and without (?r).
for lo, hi in [(ord('a'), ord('A')), (ord('z'), ord('Z')), (ord('m'), ord('M'))]:
    for tag, pat in (("no-r", b"(?i)"), ("r", b"(?i)(?r)")):
        ROWS.append(("", pat + bytes([lo]), bytes([hi]),
                      "byte (?%s): fold %r vs %r" % (tag, chr(lo), chr(hi))))
# Latin-1 range: 0xE9 (e-acute lower) vs 0xC9 (E-acute upper) -- these do
# NOT fold under pcrec's byte table (D23: bytes >= 0x80 have no case in the
# C locale), so (?r) should change nothing either way.
for tag, pat in (("no-r", b"(?i)"), ("r", b"(?i)(?r)")):
    ROWS.append(("", pat + b"\xe9", b"\xc9",
                  "byte (?%s): 0xE9 vs 0xC9 (Latin-1 e-acute, no UTF)" % tag))
    ROWS.append(("", pat + b"\xe9", b"\xe9",
                  "byte (?%s): 0xE9 vs 0xE9 (self, sanity)" % tag))
# A whole Latin-1 class under (?r), byte mode, no UTF.
for tag, pat in (("no-r", b"(?i)[\xc0-\xde]"), ("r", b"(?i)(?r)[\xc0-\xde]")):
    ROWS.append(("", pat, b"\xe9",
                  "byte (?%s): [0xC0-0xDE] class vs 0xE9" % tag))

# --- (2) (?aD)/(?aP)/(?aS)/(?aT)/(?aW) under UTF ALONE, no UCP ------------
# Compares WITH vs WITHOUT the sub-letter, both under UTF (no UCP), on
# subjects that would only diverge if the sub-letter's ASCII restriction
# were doing anything absent UCP.
pairs = [
    (b"\\d", "٣".encode(), "D"),   # ARABIC-INDIC DIGIT THREE
    (b"\\w", "é".encode(), "W"),
    (b"\\s", " ".encode(), "S"),   # NBSP
    (b"[[:alpha:]]", "é".encode(), "P"),
    (b"[[:digit:]]", "٣".encode(), "T"),
]
for body, subj, letter in pairs:
    ROWS.append(("UTF", body, subj, "UTF no-UCP, no (?a%s): baseline" % letter))
    ROWS.append(("UTF", b"(?a" + letter.encode() + b")" + body, subj,
                 "UTF no-UCP, (?a%s)" % letter))
ROWS.append(("UTF", b"x\\b", "xé".encode(), "UTF no-UCP, no (?aW): x\\b"))
ROWS.append(("UTF", b"(?aW)x\\b", "xé".encode(), "UTF no-UCP, (?aW): x\\b"))
ROWS.append(("UTF", b"\\w", "é".encode(), "UTF no-UCP, no (?a): baseline"))
ROWS.append(("UTF", b"(?a)\\w", "é".encode(), "UTF no-UCP, (?a): all restrictions"))

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
    print("%-8s %-28r %-22r %-48s %s" % (fl or "-", pat, subj, what, res))
