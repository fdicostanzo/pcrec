#!/usr/bin/env python3
"""The router S1 TWIN: the artifact S1 is designed to emit for
`/user|/users`, made by hand from the base compiler's `-fno-req-run` artifact
(which is program-identical to 25b1984f's, the pre-check dominated away) by
replacing its one-byte memchr prefilter with the run-pinned offset-set skip
of docs/design/litscan_s1.md §2. With --count, both memchr and the forward
step are wrapped in counters (a COUNT instrument; no timing is read here).
Usage: mk_twin.py BASE.c OUT.c [--count]"""
import sys
src = open(sys.argv[1]).read()
count = "--count" in sys.argv
OLD_PF = """            if (scan_position >= subject_length) return 0;
            const void *q = memchr(subject + scan_position, 47, subject_length - scan_position);
            if (!q) return 0;
            scan_position = (size_t)((const unsigned char *)q - subject);
"""
NEW_PF = """            size_t cand = rx_ofsskip(subject, subject_length, scan_position);
            if (cand >= subject_length) return 0;
            scan_position = cand;
"""
SKIP = """static inline size_t rx_ofsskip(const unsigned char *subject, size_t n, size_t pos)
{
    while (pos + 4 < n) {
        size_t cand;
        const void *q = memchr(subject + pos, 47, n - pos);
        if (!q) return n;
        cand = (size_t)((const unsigned char *)q - subject);
        if (cand + 4 >= n) return n;
        if (!memcmp(subject + cand, "/user", 5)) return cand;
        pos = cand + 1;
    }
    return n;
}

"""
HOOK = "#ifndef __has_attribute\n"
assert src.count(OLD_PF) == 1 and src.count(HOOK) == 1
if "--twin" in sys.argv:
    src = src.replace(OLD_PF, NEW_PF).replace(HOOK, SKIP + HOOK)
if count:
    pre = ("long g_mc, g_st;\n#define memchr(a, b, c) (g_mc++, memchr(a, b, c))\n")
    src = src.replace(SKIP if "--twin" in sys.argv else HOOK,
                      pre + (SKIP if "--twin" in sys.argv else HOOK), 1)
    src = src.replace("forward_state = rx_forward_step(", "g_st++, forward_state = rx_forward_step(")
open(sys.argv[2], "w").write(src)
