# p48: the ONE-STATE RELAXATION twin: an unbounded self-loop head needs no uniform exit.
import sys
p = sys.argv[1] + '/src/opt/scanedge.c'
t = open(p).read()
anchor = """    if (nfound == 0) {
        free(indeg);"""
add = """    /* P48 RELAX TWIN: every remaining self-loop state is an unbounded candidate,
     * whatever its exits (keyed by its self-loop set's lowest class). */
    for (int s = 0; s < n && nfound < n; s++) {
        if (!member_ok(d, &d->st[s], end_view_ok)) continue;
        int lo = -1, outside = 0;
        for (int c = 0; c < d->ncls; c++) {
            if (d->st[s].tr[c] == s) { if (lo < 0) lo = c; }
            else outside = 1;
        }
        if (lo < 0 || !outside) continue;
        if (s == d->s0 && !acc_of(d, s)) continue;
        /* (6) and (8) kept, as for today's unbounded heads (conservative; the
         * emitter's dfa_form_derive re-derives (8) and refuses loudly). */
        if (vtg[s]) continue;
        if (prefilter_reseeds && stg[s]) continue;
        bool dup = false;
        for (int k = 0; k < nfound; k++) if (found[k].head == s && found[k].span < 0) dup = true;
        if (dup) continue;
        found[nfound].head = s; found[nfound].cls = lo; found[nfound].span = -1;
        found[nfound].next = s; found[nfound].nmembers = 1; nfound++;
    }
""" + anchor
assert t.count(anchor) == 1
t = t.replace(anchor, add)
open(p, 'w').write(t)
