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
T6  generic form of T2 for ANY DFA artifact whose forward skip is the `can_begin_match` bitmap
    loop and whose start set is <= 6 bytes: the set is read from the artifact's own table,
    folded into one-bit cubes, and skipped 8 bytes per step by an OR of haszero terms.
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
elif t == "T6":
    # generic: the artifact's own can_begin_match table -> cubes -> SWAR terms
    import re
    m = re.search(r"static const unsigned char %s_can_begin_match\[256\] = \{(.*?)\};" % pfx, s, re.S)
    assert m
    vals = [int(x) for x in re.findall(r"\d+", m.group(1))]
    assert len(vals) == 256
    S = sorted(i for i, v in enumerate(vals) if v)
    assert 1 <= len(S) <= 6, "set too large for a few-term SWAR twin: %d" % len(S)
    terms, left = [], list(S)
    while left:
        b = left.pop(0)
        for c in left:
            d = b ^ c
            if d & (d - 1) == 0:                       # differ in exactly one bit: a one-cube
                terms.append((0xFF & ~d, b & ~d)); left.remove(c); break
        else:
            terms.append((0xFF, b))
    if plant:
        terms = [(m_, v_ ^ 0x10) for m_, v_ in terms]
    old = "            while (scan_position < subject_length && !%s_can_begin_match[subject[scan_position]]) scan_position++;\n" % pfx
    assert s.count(old) == 1
    rep = lambda x: "0x%02X%s" % (x, "") 
    zs = []
    for i, (mk, vl) in enumerate(terms):
        rep8 = "0x" + ("%02X" % mk) * 8 + "ull"; val8 = "0x" + ("%02X" % vl) * 8 + "ull"
        zs.append("(((w & %s) ^ %s) - 0x0101010101010101ull) & ~((w & %s) ^ %s)" % (rep8, val8, rep8, val8))
    new = ("            /* TWIN T6: the start set %s = %d cube term(s) (mask:value %s): 8 bytes per step */\n"
           "            while (scan_position + 8 <= subject_length) {\n"
           "                unsigned long long w; memcpy(&w, subject + scan_position, 8);\n"
           "                unsigned long long z = ((%s)) & 0x8080808080808080ull;\n"
           "                if (z) { scan_position += (size_t)(__builtin_ctzll(z) >> 3); break; }\n"
           "                scan_position += 8;\n"
           "            }\n") % (",".join("%02x" % b for b in S), len(terms), " ".join("%02x:%02x" % t_ for t_ in terms), ") | (".join(zs)) + old
    s = s.replace(old, new, 1)
else:
    sys.exit("T1|T2|T6")
open(dst, "w").write(s)
