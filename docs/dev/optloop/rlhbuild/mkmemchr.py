#!/usr/bin/env python3
"""docs/dev/optloop/rlhbuild/mkmemchr.py -- SCRATCH, NOT the lane's text:
the built artifact with every rendering of the byte gate's kit loop (the
`generic` row's statement expression over one byte, R-15's site) replaced by
a libc memchr returning the same position (the hit, or subject_length). Used
for the R-15 delta: today's generic loop vs a memchr ASSIGN, at the entry
AND the re-entry. An artifact with no such loop is copied unchanged.

    mkmemchr.py IN.c OUT.c"""
import re, sys

src, dst = sys.argv[1:3]
s = open(src).read()
pat = re.compile(r'(size_t )?(\w+) = \(\{ const unsigned char \*rx_mf1_s = \(const unsigned char \*\)\(subject\); '
                 r'size_t rx_mf1_n = subject_length; size_t rx_mf1_lo = (\w+);.*?\(rx_mf1_s\[rx_mf1_c0\] == (\d+)\)\).*?\}\);')
def rep(m):
    decl, res, lo, b = m.group(1) or "", m.group(2), m.group(3), m.group(4)
    return ("%s%s = ({ const unsigned char *rlb_q = subject_length > %s ? "
            "memchr(subject + %s, %s, subject_length - %s) : NULL; "
            "rlb_q ? (size_t)(rlb_q - subject) : subject_length; });"
            % (decl, res, lo, lo, b, lo))
s, n = pat.subn(rep, s)
if n and "#include <string.h>" not in s:
    s = "#include <string.h>\n" + s
open(dst, "w").write(s)
print("mkmemchr: %d site(s) rewritten" % n, file=sys.stderr)
