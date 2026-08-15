#!/usr/bin/env python3
"""R23-semantics decisive probe for S1.

One binary that maintains BOTH open-loop stack disciplines at once:

  * `cl->open`  -- entries SAVED AND RESTORED per frame (the correct stack);
                   this is the one the walk actually uses, so answers are A2-FIX's;
  * `cl->sh`    -- entries written identically but NEVER restored on frame
                   return, which is exactly prototype A/A2's discipline.

At every arrival at a `loop=1` state it scans both and counts:
  scan_diff   -- the two stacks give a DIFFERENT redirect verdict (miss or
                 false positive, or the same loop found at a different index);
  ctx_diff    -- the post-recursion `ctx = open[depth-1].ctx` restore would
                 have read a different context id under A2's discipline.

A nonzero scan_diff on a pattern is a WITNESS that A2's stack corruption
changes a semantic decision.  Zero over a large corpus is evidence (not proof)
that the corruption is latent.
"""
import subprocess
import sys

path = sys.argv[1]
PROTO = "/home/duxevents/pcrec/docs/design/k18_measurements/prototypes/proto_a2.py"
subprocess.run([sys.executable, PROTO, path], check=True)

src = open(path).read()

src = src.replace("static K18Stats k18_stats;",
                  "static K18Stats k18_stats;\n"
                  "static long k18_scan_diff, k18_ctx_diff, k18_clobber;\nstatic long k18_miss, k18_fpos;")

# shadow array in Clo
src = src.replace("    OpenEnt  *open;    /* the walk's own open-loop stack */",
                  "    OpenEnt  *open;    /* the walk's own open-loop stack */\n"
                  "    OpenEnt  *sh;      /* same writes, A2's no-restore discipline */")

# ---- frame entry: save open[] (and compare on exit) ------------------------
old = """static void clo_visit(Clo *cl, int s)
{
    int save_depth = cl->depth;
    int save_ctx = cl->ctx;"""
new = """static void clo_visit(Clo *cl, int s)
{
    int save_depth = cl->depth;
    int save_ctx = cl->ctx;
    OpenEnt *save_open = NULL;
    if (save_depth > 0) {
        save_open = malloc((size_t)save_depth * sizeof(OpenEnt));
        if (!save_open) abort();
        memcpy(save_open, cl->open, (size_t)save_depth * sizeof(OpenEnt));
    }"""
assert old in src
src = src.replace(old, new)

old = """done:
    cl->depth = save_depth;
    cl->ctx = save_ctx;
}"""
new = """done:
    cl->depth = save_depth;
    cl->ctx = save_ctx;
    if (save_open) {
        for (int i = 0; i < save_depth; i++)
            if (save_open[i].loop != cl->sh[i].loop) { k18_clobber++; break; }
        memcpy(cl->open, save_open, (size_t)save_depth * sizeof(OpenEnt));
        free(save_open);
    }
}"""
assert old in src
src = src.replace(old, new)

# ---- the redirect scan: compare both stacks --------------------------------
old = """        if (st->loop) {
            int at = -1;
            for (int i = cl->depth - 1; i >= 0; i--)
                if (cl->open[i].loop == s) { at = i; break; }
            if (at >= 0) {"""
new = """        if (st->loop) {
            int at = -1;
            for (int i = cl->depth - 1; i >= 0; i--)
                if (cl->open[i].loop == s) { at = i; break; }
            {   int at_sh = -1;
                for (int i = cl->depth - 1; i >= 0; i--)
                    if (cl->sh[i].loop == s) { at_sh = i; break; }
                if (at_sh != at) k18_scan_diff++;\n                if (at >= 0 && at_sh < 0) k18_miss++;\n                if (at < 0 && at_sh >= 0) k18_fpos++;
            }
            if (at >= 0) {"""
assert old in src
src = src.replace(old, new)

# ---- every write to open[] is mirrored into sh[] ---------------------------
src = src.replace("""                cl->depth = at;                                   /* pop L and anything above it */
                cl->ctx = at ? cl->open[at - 1].ctx : 0;""",
"""                cl->depth = at;                                   /* pop L and anything above it */
                if (at && cl->open[at - 1].ctx != cl->sh[at - 1].ctx) k18_ctx_diff++;
                cl->ctx = at ? cl->open[at - 1].ctx : 0;""")

src = src.replace("""                    cl->open[cl->depth].loop = s;
                    cl->ctx = lctx_intern(cl->ctxs, cl->ctx, s);
                    cl->open[cl->depth].ctx = cl->ctx;
                    cl->depth++;""",
"""                    cl->open[cl->depth].loop = s;
                    cl->ctx = lctx_intern(cl->ctxs, cl->ctx, s);
                    cl->open[cl->depth].ctx = cl->ctx;
                    cl->sh[cl->depth] = cl->open[cl->depth];
                    cl->depth++;""")

src = src.replace("""                    clo_visit(cl, st->t1);
                    cl->depth--;
                    cl->ctx = cl->depth ? cl->open[cl->depth - 1].ctx : 0;""",
"""                    clo_visit(cl, st->t1);
                    cl->depth--;
                    if (cl->depth && cl->open[cl->depth - 1].ctx != cl->sh[cl->depth - 1].ctx)
                        k18_ctx_diff++;
                    cl->ctx = cl->depth ? cl->open[cl->depth - 1].ctx : 0;""")

src = src.replace("""                clo_visit(cl, st->t1);              /* t1 = exit (lazy) */
                cl->open[cl->depth].loop = s;
                cl->ctx = lctx_intern(cl->ctxs, cl->ctx, s);
                cl->open[cl->depth].ctx = cl->ctx;
                cl->depth++;""",
"""                clo_visit(cl, st->t1);              /* t1 = exit (lazy) */
                cl->open[cl->depth].loop = s;
                cl->ctx = lctx_intern(cl->ctxs, cl->ctx, s);
                cl->open[cl->depth].ctx = cl->ctx;
                cl->sh[cl->depth] = cl->open[cl->depth];
                cl->depth++;""")

# ---- allocate sh[] and thread it -------------------------------------------
src = src.replace("""    OpenEnt *openst = arena_alloc(&cx->arena, (size_t)(nfa->n + 2) * sizeof(OpenEnt));""",
"""    OpenEnt *openst = arena_alloc(&cx->arena, (size_t)(nfa->n + 2) * sizeof(OpenEnt));
    OpenEnt *shadowst = arena_alloc(&cx->arena, (size_t)(nfa->n + 2) * sizeof(OpenEnt));""")

old = """                    LCtxTab *ctxs, OpenEnt *openst,
                    int *out, int *nout, bool *accept)"""
assert old in src, "closure sig anchor drift"
src = src.replace(old, """                    LCtxTab *ctxs, OpenEnt *openst, OpenEnt *shadowst,
                    int *out, int *nout, bool *accept)""")
src = src.replace("""    Clo cl = { nfa, memo, ctxs, mk->mark, mk0->mark, mk->gen, openst, 0, 0,
               out, 0, false, eol_ok, bot_ok, prune };""",
"""    Clo cl = { nfa, memo, ctxs, mk->mark, mk0->mark, mk->gen, openst, shadowst, 0, 0,
               out, 0, false, eol_ok, bot_ok, prune };""")
old = """                      Marks *mk0, PMemo *memo, LCtxTab *ctxs, OpenEnt *openst)"""
assert old in src, "make_state sig anchor drift"
src = src.replace(old, """                      Marks *mk0, PMemo *memo, LCtxTab *ctxs, OpenEnt *openst,
                      OpenEnt *shadowst)""")
src = src.replace("openst, scratch, &nout, &accept);", "openst, shadowst, scratch, &nout, &accept);")
src = src.replace("openst, scratch2, &nout2, &accept2);", "openst, shadowst, scratch2, &nout2, &accept2);")
src = src.replace("&marks, scratch, &marks0, &memo, &ctxs, openst",
                  "&marks, scratch, &marks0, &memo, &ctxs, openst, shadowst")

src = src.replace('"K18STATS nfa=%d dfa=%d closures=%ld visits=%ld expansions=%ld "',
                  '"K18STATS miss=%ld fpos=%ld scandiff=%ld ctxdiff=%ld clobber=%ld nfa=%d dfa=%d closures=%ld visits=%ld expansions=%ld "')
src = src.replace("nfa->n, d->n, k18_stats.closures,",
                  "k18_miss, k18_fpos, k18_scan_diff, k18_ctx_diff, k18_clobber, nfa->n, d->n, k18_stats.closures,")

open(path, "w").write(src)
print("proto A2-SHADOW applied to", path)
