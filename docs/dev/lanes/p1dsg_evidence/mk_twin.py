"""Splice a landmark-seeded reverse-walk candidate loop into a pcrec DFA artifact's
rx_search (scratch twin, NOT pcrec code). argv: artifact.c rw.inc LANDMARK_BYTE LEN_L"""
import sys
a = open(sys.argv[1]).read(); rw = open(sys.argv[2]).read()
L = int(sys.argv[3]); lenL = int(sys.argv[4])
proto = 'int rx_search(const unsigned char *subject, size_t subject_length, size_t search_from, ptrdiff_t (*capture_spans)[2])\n{'
assert proto in a
loop = f'''
    /* p1dsg TWIN: candidates from the landmark byte {L}; P's reverse DFA seeded at the
     * landmark (here: P.L's reverse machine seeded at the landmark's end), floored at
     * search_from; one anchored forward match at the smallest accepting start. */
    {{
        size_t p = search_from;
        while (p < subject_length) {{
            const unsigned char *q = memchr(subject + p, {L}, subject_length - p);
            if (!q) return 0;
            size_t at = (size_t)(q - subject);
            size_t st = rw_walk(subject, at + {lenL}, search_from);
            if (st != (size_t)-1) {{
                rx_ctx c; c.subject = subject; c.len = subject_length; c.pos = st;
                ptrdiff_t m = rx_match(&c);
                if (m >= 0) {{
                    if (capture_spans) {{ capture_spans[0][0] = (ptrdiff_t)st; capture_spans[0][1] = (ptrdiff_t)(st + (size_t)m); }}
                    return 1;
                }}
            }}
            p = at + 1;
        }}
        return 0;
    }}
'''
a = a.replace(proto, rw + '\nptrdiff_t rx_match(const rx_ctx *ctx);\n' + proto + loop, 1)
open(sys.argv[5], 'w').write(a)
