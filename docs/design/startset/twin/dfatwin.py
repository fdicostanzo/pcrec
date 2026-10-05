#!/usr/bin/env python3
"""[START-SET] the DFA hat's hand twins (docs/design/startset.md §4.1), on a
SEEDED forward machine with a byte-class skip:
  tw  can_begin_match narrowed to T = S_ast & E, NO re-seed (M3 as ratified)
  rs  the same narrowing PLUS pf_emit_ofs_reseed's expression on skip exit
Same patch text as docs/dev/optloop/c2/firstset_witness.sh; T, not S, is the
set (never wider than today's).  ANSWERS ONLY.
    dfatwin.py <tw.c> <rs.c> <S_hex64>
"""
import re, sys
S = bytes.fromhex(sys.argv[3])
def narrow(path, pfx):
    src = open(path).read()
    m = re.search(r"(static const unsigned char %s_can_begin_match\[256\] = \{)(.*?)(\};)" % pfx, src, re.S)
    assert m, "no can_begin_match"
    old = [v != "0" for v in re.findall(r"\d+", m.group(2))][:256]
    new = [old[i] and bool(S[i >> 3] >> (i & 7) & 1) for i in range(256)]
    assert sum(new) < sum(old), "T == E: nothing narrows (not in the DFA hat's reach)"
    vals = ", ".join("1" if x else "0" for x in new)
    open(path, "w").write(src[:m.start()] + m.group(1) + "\n        " + vals + "\n    " + m.group(3) + src[m.end():])
    return sum(old), sum(new)
def reseed(path, pfx):
    src = open(path).read()
    old = ("        if (forward_state == 0 && last_accept_position == (size_t)-1) {\n"
           "            while (scan_position + 1 < subject_length && !%s_can_begin_match[subject[scan_position]]) scan_position++;\n"
           "        }\n") % pfx
    assert src.count(old) == 1, "skip-loop block count %d" % src.count(old)
    new = ("        if (forward_state == 0 && last_accept_position == (size_t)-1) {\n"
           "            size_t entry_position = scan_position;\n"
           "            while (scan_position + 1 < subject_length && !%s_can_begin_match[subject[scan_position]]) scan_position++;\n"
           "            if (scan_position > entry_position)\n"
           "                forward_state = %s_forward_seed_state[%s_forward_byte_class[subject[scan_position - 1]]];\n"
           "        }\n") % (pfx, pfx, pfx)
    open(path, "w").write(src.replace(old, new, 1))
e, t = narrow(sys.argv[1], "tw"); narrow(sys.argv[2], "rs"); reseed(sys.argv[2], "rs")
print("|E|=%d |T|=%d" % (e, t))
