#!/usr/bin/env python3
"""Dump the NFA and trace one epsilon closure, on the UNMODIFIED closure.

MEASUREMENT ARTIFACT. The design note has to show K18's walk state by state,
and a trace copied out of docs/dev/known_issues.md would be a citation, not a
verification. PCREC_K18_DUMP=1 prints the NFA; PCREC_K18_TRACE=1 prints every
clo_visit step with its verdict.
"""
import sys

path = sys.argv[1]
src = open(path).read()

src = src.replace('#include <stdlib.h>\n#include <string.h>',
                  '#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>')

src = src.replace("static void clo_visit(Clo *cl, int s)\n{\n    for (;;) {",
                  """static int k18_trace = -1;
static const char *k18_kind(NKind k)
{
    switch (k) {
    case N_CLASS: return "CLASS"; case N_SPLIT: return "SPLIT";
    case N_EPS: return "EPS"; case N_BOT: return "BOT";
    case N_EOL: return "EOL"; case N_ACCEPT: return "ACCEPT";
    }
    return "?";
}

static void clo_visit(Clo *cl, int s)
{
    for (;;) {""")

src = src.replace("""        if (cl->seen[s] == cl->gen) {""",
"""        if (k18_trace > 0 && s >= 0)
            fprintf(stderr, "  visit %2d %-6s t1=%-3d t2=%-3d loop=%d %s\\n",
                    s, k18_kind(cl->nfa->st[s].k), cl->nfa->st[s].t1,
                    cl->nfa->st[s].t2, cl->nfa->st[s].loop,
                    cl->seen[s] == cl->gen ? "<-- ALREADY SEEN" : "");
        if (cl->seen[s] == cl->gen) {""")

src = src.replace("""            const NState *ls = &cl->nfa->st[s];
            if (ls->loop) {""",
"""            const NState *ls = &cl->nfa->st[s];
            if (!ls->loop && k18_trace > 0)
                fprintf(stderr, "      DEAD: seen, not a loop entry -- "
                        "the walk stops one hop short\\n");
            if (ls->loop) {""")

src = src.replace("""        case N_CLASS:  cl->out[cl->nout++] = s; return;
        case N_ACCEPT: cl->accept = true; return;""",
"""        case N_CLASS:  if (k18_trace > 0) fprintf(stderr, "      EMIT thread %d\\n", s);
                       cl->out[cl->nout++] = s; return;
        case N_ACCEPT: if (k18_trace > 0) fprintf(stderr, "      ACCEPT\\n");
                       cl->accept = true; return;""")

src = src.replace("""    marks_next(mk);
    Clo cl = { nfa, mk->mark, mk->gen,""",
"""    marks_next(mk);
    if (k18_trace < 0) k18_trace = getenv("PCREC_K18_TRACE") ? 1 : 0;
    if (k18_trace > 0) {
        fprintf(stderr, "closure pre-set {");
        for (int i = 0; i < npre; i++) fprintf(stderr, "%s%d", i ? "," : "", pre[i]);
        fprintf(stderr, "} bot=%d eol=%d prune=%d\\n", bot_ok, eol_ok, prune);
    }
    Clo cl = { nfa, mk->mark, mk->gen,""")

src = src.replace("""    eqclasses(nfa, d);""",
"""    if (getenv("PCREC_K18_DUMP")) {
        fprintf(stderr, "NFA start=%d n=%d\\n", nfa->start, nfa->n);
        for (int i = 0; i < nfa->n; i++) {
            const NState *st = &nfa->st[i];
            const char *kn;
            switch (st->k) {
            case N_CLASS: kn = "CLASS"; break; case N_SPLIT: kn = "SPLIT"; break;
            case N_EPS: kn = "EPS"; break; case N_BOT: kn = "BOT"; break;
            case N_EOL: kn = "EOL"; break; default: kn = "ACCEPT"; break;
            }
            fprintf(stderr, "  %2d %-6s t1=%-3d t2=%-3d loop=%d exit_is_t2=%d",
                    i, kn, st->t1, st->t2, st->loop, st->exit_is_t2);
            if (st->k == N_CLASS) {
                fprintf(stderr, "  cls=");
                for (int c = 32; c < 127; c++)
                    if (cls_has(st->cls, (unsigned)c)) fputc(c, stderr);
            }
            fputc('\\n', stderr);
        }
    }
    eqclasses(nfa, d);""")

open(path, "w").write(src)
print("proto dump applied to", path)
