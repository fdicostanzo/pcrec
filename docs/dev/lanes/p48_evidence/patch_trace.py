# p48: add a P48_TRACE stderr line per machine (skip + edge states) to a scratch tree's emit_dfa.c
import sys
p = sys.argv[1] + '/src/gen/emit_dfa.c'
t = open(p).read()
anchor = """    for (int i = 0; i < d->n && f->nscan < PCREC_MAX_SCAN_EDGES; i++)
        if (dfa_edge_taken(dfa_edge_of(cx, d, i))) f->scan[f->nscan++] = i;
"""
add = anchor + """    if (getenv("P48_TRACE")) {   /* P48 TWIN TRACE (scratch only) */
        for (int k = 0; k < f->nskip + f->nscan; k++) {
            int st = k < f->nskip ? f->skip[k] : f->scan[k - f->nskip];
            uint8_t m[256];
            if (k < f->nskip) stay_set(d, st, m);
            else for (int b = 0; b < 256; b++) m[b] = pcrec_scan_has(&d->st[st], d->clsmap[b]);
            fprintf(stderr, "P48\\t%s\\t%s\\t%d\\t%d\\t%d\\t", dir->c.name, k < f->nskip ? "skip" : "edge",
                    st, k < f->nskip ? 0 : d->st[st].scan_span, d->st[st].up[UPC_PLAIN].accept ? 1 : 0);
            for (int b = 0; b < 256; b += 4)
                fprintf(stderr, "%x", (m[b] ? 1 : 0) | (m[b+1] ? 2 : 0) | (m[b+2] ? 4 : 0) | (m[b+3] ? 8 : 0));
            fprintf(stderr, "\\t%d\\t%d\\n", st == d->s0, f->nscan);
        }
        fprintf(stderr, "P48M\\t%s\\tseedhead=%d\\tn=%d\\n", dir->c.name,
                f->nscan > 0 && dfa_seed_can_be_scan_head(d), d->n);
    }
"""
assert t.count(anchor) == 1
t = t.replace(anchor, add)
if '#include <stdio.h>' not in t:
    t = '#include <stdio.h>\n' + t
if '#include <stdlib.h>' not in t:
    t = '#include <stdlib.h>\n' + t
# dfa_seed_can_be_scan_head is defined later in the file: forward-declare it at the top
t = t.replace('#include <stdlib.h>\n', '#include <stdlib.h>\n', 1)
open(p, 'w').write(t)
