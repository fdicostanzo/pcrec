#!/usr/bin/env python3
"""[START-LANDING] rev 2: the seam's decode against Unicode Table 3-7 (STUDY).

    decode_eq.py WORKDIR

The guard (design §2.5, both forms) asks one question: does a well-formed
character start at p? A build answers it with THE SEAM'S `$_decode`
(`src/enc/enc_utf8.c` `u8_defs_decode`, length or 0), so the twins call that
text (mktwin.py). This check is the control that does not share its source:
an independent Table 3-7 spelling (lead ranges with narrowed second-byte
bounds, Unicode 16 §3.9), compared with the seam text on EVERY 4-byte window
b0 b1 b2 b3 (2^32) and EVERY end in {p+1 .. p+4} (truncation), exhaustively:
the two must agree on "decodes" and, where it does, on the length. Exit 1 on
any disagreement, printing the first few. It also counts the lengths, which
makes the run self-describing (a check that compared two constant-0
functions would print a single length).
"""
import os, re, subprocess, sys

work = sys.argv[1]
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
t = open(os.path.join(root, "src", "enc", "enc_utf8.c")).read()
i = t.index("static const char u8_defs_decode[] =")
lits = re.findall(r'^"((?:[^"\\]|\\.)*)"', t[i:t.index(";\n", i)], re.M)
seam = "".join(bytes(l, "ascii").decode("unicode_escape") for l in lits).replace("$", "seam")
C = "#include <stddef.h>\n" + seam + r'''
#include <stdio.h>
static size_t t37(const unsigned char *s, size_t end, size_t p)
{   /* Unicode Table 3-7: the well-formed byte sequences */
    unsigned c = s[p]; size_t k; unsigned lo = 0x80, hi = 0xBF;
    if (c < 0x80) return 1;
    if (c >= 0xC2 && c <= 0xDF) k = 1;
    else if (c == 0xE0) { k = 2; lo = 0xA0; }
    else if (c >= 0xE1 && c <= 0xEC) k = 2;
    else if (c == 0xED) { k = 2; hi = 0x9F; }
    else if (c >= 0xEE && c <= 0xEF) k = 2;
    else if (c == 0xF0) { k = 3; lo = 0x90; }
    else if (c >= 0xF1 && c <= 0xF3) k = 3;
    else if (c == 0xF4) { k = 3; hi = 0x8F; }
    else return 0;
    if (p + k >= end) return 0;
    if (s[p + 1] < lo || s[p + 1] > hi) return 0;
    for (size_t i = 2; i <= k; i++) if (s[p + i] < 0x80 || s[p + i] > 0xBF) return 0;
    return k + 1;
}
int main(void)
{
    unsigned char s[4]; unsigned cp; long bad = 0; unsigned long long len[5] = {0}, n = 0;
    for (unsigned long long w = 0; w < (1ull << 32); w++) {
        s[0] = w >> 24; s[1] = w >> 16; s[2] = w >> 8; s[3] = w;
        for (size_t end = 1; end <= 4; end++) {
            /* the seam's decode reads only s[p..p+len) when it returns len, and
               never past `end` (its own bound): the window is the subject */
            size_t a = seam_decode(s, end, 0, &cp), b = t37(s, end, 0);
            n++; len[a]++;
            if (a != b && bad++ < 8)
                printf("DIFF %02x %02x %02x %02x end=%zu seam=%zu t37=%zu\n", s[0], s[1], s[2], s[3], end, a, b);
        }
    }
    printf("decode_eq windows*ends=%llu len0=%llu len1=%llu len2=%llu len3=%llu len4=%llu disagreements=%ld\n",
           n, len[0], len[1], len[2], len[3], len[4], bad);
    return bad != 0;
}
'''
os.makedirs(work, exist_ok=True)
open(os.path.join(work, "decode_eq.c"), "w").write(C)
subprocess.check_call(["gcc", "-O2", "-w", "-o", os.path.join(work, "decode_eq"), os.path.join(work, "decode_eq.c")])
sys.exit(subprocess.call([os.path.join(work, "decode_eq")]))
