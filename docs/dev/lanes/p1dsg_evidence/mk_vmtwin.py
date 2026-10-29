"""Splice a landmark-seeded reverse-walk candidate loop into a pcrec VM artifact's
rx_search_run (scratch twin, NOT pcrec code). argv: artifact.c rw.inc LANDMARK LEN_L out.c"""
import sys
a = open(sys.argv[1]).read(); rw = open(sys.argv[2]).read()
L = int(sys.argv[3]); lenL = int(sys.argv[4])
anchor = '    attempt_position = search_from;\n    window_end = subject_length;\n'
assert a.count(anchor) == 1
loop = f'''    /* p1dsg TWIN: candidates from the landmark byte {L}; P's reverse DFA seeded at the
     * landmark, floored at search_from; ONE anchored VM attempt at the smallest accepting
     * start (exact here: the context item makes starts(j) a singleton). */
    window_end = subject_length;
    rx_run_state_init(run);
    ctx.subject = subject; ctx.len = subject_length; ctx.ncap = 0;
    ctx.caps = NULL; ctx.user = NULL;
    {{
        size_t p = search_from;
        while (p < subject_length) {{
            const unsigned char *q = memchr(subject + p, {L}, subject_length - p);
            if (!q) return 0;
            size_t at = (size_t)(q - subject);
            size_t st = rw_walk(subject, at + {lenL}, search_from);
            if (st != (size_t)-1) {{
                ctx.pos = attempt_position = st;
                result = rx_match_anchored(&ctx, run, window_end);
                if (result == RX_R_STEPS)   return PCREC_ERR_STEPS;
                if (result == RX_R_FRAMES)  return PCREC_ERR_FRAMES;
                if (result == RX_R_WORK)    return PCREC_ERR_WORK;
                if (result == RX_R_RECURSE) return PCREC_ERR_RECURSE;
                if (result == RX_R_INTERNAL) return PCREC_ERR_INTERNAL;
                if (result >= 0) {{
                    if (capture_spans) rx_report_captures(run, capture_spans, attempt_position, result);
                    return 1;
                }}
                rx_reset_for_next_attempt(run);
            }}
            p = at + 1;
        }}
        return 0;
    }}
'''
a = a.replace(anchor, loop + anchor, 1)
fn = 'static int rx_search_run('
a = a.replace(fn, rw + '\n' + fn, 1)
open(sys.argv[5], 'w').write(a)
