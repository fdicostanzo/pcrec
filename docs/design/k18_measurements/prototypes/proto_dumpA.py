#!/usr/bin/env python3
"""proto A + the same closure trace proto_dump.py adds to the shipped closure.

MEASUREMENT ARTIFACT. Its whole point is that the BEFORE and AFTER traces in
the design note are both printed by a compiler, not reconstructed by hand.
"""
import subprocess
import sys

path = sys.argv[1]
subprocess.run([sys.executable,
                __file__.replace("proto_dumpA.py", "proto_a.py"), path], check=True)

src = open(path).read()

src = src.replace("""typedef struct { int loop; int ctx; } OpenEnt;""",
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

typedef struct { int loop; int ctx; } OpenEnt;""")

src = src.replace("""        const NState *st = &cl->nfa->st[s];

        /* --- the empty-iteration rule""",
"""        const NState *st = &cl->nfa->st[s];
        if (k18_trace > 0) {
            fprintf(stderr, "  visit %2d %-6s t1=%-3d t2=%-3d loop=%d  open={",
                    s, k18_kind(st->k), st->t1, st->t2, st->loop);
            for (int i = 0; i < cl->depth; i++)
                fprintf(stderr, "%s%d", i ? "," : "", cl->open[i].loop);
            fprintf(stderr, "} ctx=%d\\n", cl->ctx);
        }

        /* --- the empty-iteration rule""")

src = src.replace("""            if (at >= 0) {
                if (k18_stats_on) {""",
"""            if (at >= 0) {
                if (k18_trace > 0)
                    fprintf(stderr, "      REDIRECT: loop %d is OPEN on this "
                            "path -> empty iteration ends the loop\\n", s);
                if (k18_stats_on) {""")

src = src.replace("""        if (!pmemo_add(cl->memo, s, cl->ctx)) break;""",
"""        if (!pmemo_add(cl->memo, s, cl->ctx)) {
            if (k18_trace > 0)
                fprintf(stderr, "      dedup: (state %d, ctx %d) already "
                        "expanded THIS context\\n", s, cl->ctx);
            break;
        }""")

src = src.replace("""            if (cl->emit[s] != cl->gen) { cl->emit[s] = cl->gen; cl->out[cl->nout++] = s; }
            goto done;""",
"""            if (cl->emit[s] != cl->gen) {
                if (k18_trace > 0) fprintf(stderr, "      EMIT thread %d\\n", s);
                cl->emit[s] = cl->gen; cl->out[cl->nout++] = s;
            }
            goto done;""")

src = src.replace("""        case N_ACCEPT: cl->accept = true; goto done;""",
"""        case N_ACCEPT: if (k18_trace > 0) fprintf(stderr, "      ACCEPT\\n");
                       cl->accept = true; goto done;""")

src = src.replace("""    marks_next(mk);
    pmemo_next(memo);""",
"""    marks_next(mk);
    pmemo_next(memo);
    if (k18_trace < 0) k18_trace = getenv("PCREC_K18_TRACE") ? 1 : 0;
    if (k18_trace > 0) {
        fprintf(stderr, "closure pre-set {");
        for (int i = 0; i < npre; i++) fprintf(stderr, "%s%d", i ? "," : "", pre[i]);
        fprintf(stderr, "} bot=%d eol=%d prune=%d\\n", bot_ok, eol_ok, prune);
    }""")

open(path, "w").write(src)
print("proto dumpA applied to", path)
