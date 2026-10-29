# p48: the BOUNDED-ONLY ENTRY twin (emit_dfa.c): the loop-entry dispatch onto a
# scan-edge head is emitted only for a BOUNDED head (scan_span > 0); an
# unbounded head keeps its self-loop cells, so the ordinary step reaches it.
import sys
p = sys.argv[1] + '/src/gen/emit_dfa.c'
t = open(p).read()
reps = [("return d->s0 >= 0 && d->s0 < d->n && d->st[d->s0].scan_span != 0;",
         "return d->s0 >= 0 && d->s0 < d->n && d->st[d->s0].scan_span > 0;"),
        ("if (a >= 0 && a < d->n && d->st[a].scan_span != 0) return true;",
         "if (a >= 0 && a < d->n && d->st[a].scan_span > 0) return true;"),
        ("if (b >= 0 && b < d->n && d->st[b].scan_span != 0) return true;",
         "if (b >= 0 && b < d->n && d->st[b].scan_span > 0) return true;"),
        ("rev->entry_head = (sn >= 0 && d->st[sn].scan_span != 0) ||\n                      (snl >= 0 && d->st[snl].scan_span != 0);",
         "rev->entry_head = (sn >= 0 && d->st[sn].scan_span > 0) ||\n                      (snl >= 0 && d->st[snl].scan_span > 0);"),
        ("rev->entry_head = sn >= 0 && d->st[sn].scan_span != 0;",
         "rev->entry_head = sn >= 0 && d->st[sn].scan_span > 0;")]
for a, b in reps:
    assert t.count(a) == 1, a
    t = t.replace(a, b)
open(p, 'w').write(t)
