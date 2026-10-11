#!/usr/bin/env python3
"""lossreview/misc twins: the hand edits of an EMITTED artifact (no src/ change).

    twin_edit.py T1|T2 PFX IN.c OUT.c [plant]

T1  capability `tail-dotstar-txt` (`.*\\.txt$`, nocaps, rev-end route): a
    necessary-LAST-BYTE test ahead of the reverse walk -- any match ends at n
    (last byte `t`) or, when the subject ends in a newline, at n-1 (last byte
    `\\n`); every other last byte returns 0 without entering the walk.
T2  utf8 `ci-sigma` (`(?i)σ`, nocaps): the start set {0xCE, 0xCF} is one cube
    ((b & 0xFE) == 0xCE); the byte-class skip loop is preceded by an 8-byte
    SWAR skip on that cube (haszero over (word & 0xFE..) ^ 0xCE..).
`plant` writes a deliberately wrong twin (T1: drop the \\n allowance; T2: cube
value 0xCF) -- the identity driver must report differences for it.
Both edits assert the anchor text they replace, so a drifted emitter fails
loudly instead of producing an unedited 'twin'."""
import sys
t, pfx, src, dst = sys.argv[1:5]; plant = len(sys.argv) > 5
s = open(src).read()
if t == "T1":
    key = "int %s_search(const unsigned char *subject, size_t subject_length, size_t search_from, ptrdiff_t (*capture_spans)[2])\n{\n    if (search_from > subject_length) return 0;\n" % pfx
    assert key in s
    cond = "subject[subject_length - 1] != 't'" if plant else "subject[subject_length - 1] != 't' && subject[subject_length - 1] != '\\n'"
    s = s.replace(key, key + "    /* TWIN T1: the necessary last byte of a match of .*\\.txt$ is t, or \\n when the match ends before a final \\n */\n    if (subject_length == 0 || (%s)) return 0;\n" % cond, 1)
elif t == "T2":
    old = "            while (scan_position < subject_length && !%s_can_begin_match[subject[scan_position]]) scan_position++;\n" % pfx
    assert old in s
    val = "0xCFCFCFCFCFCFCFCFull" if plant else "0xCECECECECECECECEull"
    new = ("            /* TWIN T2: the start set {0xCE,0xCF} is one cube ((b & 0xFE) == 0xCE): 8 bytes per step */\n"
           "            while (scan_position + 8 <= subject_length) {\n"
           "                unsigned long long w; memcpy(&w, subject + scan_position, 8);\n"
           "                unsigned long long t = (w & 0xFEFEFEFEFEFEFEFEull) ^ %s;\n"
           "                unsigned long long z = (t - 0x0101010101010101ull) & ~t & 0x8080808080808080ull;\n"
           "                if (z) { scan_position += (size_t)(__builtin_ctzll(z) >> 3); break; }\n"
           "                scan_position += 8;\n"
           "            }\n") % val + old
    s = s.replace(old, new, 1)
else:
    sys.exit("T1|T2")
open(dst, "w").write(s)
