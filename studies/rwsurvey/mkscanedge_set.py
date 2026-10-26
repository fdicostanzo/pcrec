#!/usr/bin/env python3
"""rwsurvey: derive build/probe/scanedge_set.c from src/opt/scanedge.c with the
class-SET rule in place of the one-class rule (probe only: the emitted artifact of the
set variant is NOT valid, it exists so the REAL pass's other preconditions and the
slot cap decide how many chains the set rule would find).

  shaped():     S = every class whose target equals tr[cls]'s (cls must be the smallest class
                of S, so each set is found once); every class outside S shares one exit != tr[cls]
  same_shape(): additionally the two states' sets {c : tr[c] != exit} are equal
Usage: mkscanedge_set.py IN OUT
"""
import re, sys

src = open(sys.argv[1]).read()


def replace_fn(text, head, new):
    i = text.index(head)
    j = text.index("\n}\n", i) + 3
    return text[:i] + new + text[j:]


shaped = '''static bool shaped(const Dfa *d, int s, int cls, int *exit)
{
    const int *tr = d->st[s].tr;
    int v0 = tr[cls], e = -2, seen = 0;
    for (int c = 0; c < d->ncls; c++) {
        if (tr[c] == v0) { if (c < cls) return false; continue; }   /* cls = min class of S */
        if (!seen) { e = tr[c]; seen = 1; }
        else if (tr[c] != e) return false;                          /* the exit is not uniform */
    }
    if (!seen) return false;
    *exit = e;
    return true;
}
'''
same = '''static bool same_set(const Dfa *d, const int *exitv, int s, int t)
{
    for (int c = 0; c < d->ncls; c++)
        if ((d->st[s].tr[c] != exitv[s]) != (d->st[t].tr[c] != exitv[t])) return false;
    return true;
}

static bool same_shape(const Dfa *d, const bool *ok, const int *exitv, int s, int t)
{
    return ok[t] && exitv[t] == exitv[s] && acc_of(d, t) == acc_of(d, s)
        && end_acc_of(d, t) == end_acc_of(d, s) && same_set(d, exitv, s, t);
}
'''
src = replace_fn(src, "static bool shaped(const Dfa *d, int s, int cls, int *exit)", shaped)
src = replace_fn(src, "static bool same_shape(const Dfa *d, const bool *ok, const int *exitv, int s, int t)", same)
open(sys.argv[2], "w").write(src)
