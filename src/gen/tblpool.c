/* [UCP] U3 THE ARTIFACT'S TABLE POOL (review r4 ucpu3 EMIT-1; internal.h's
 * `pcrec_tbl_ref`). One mechanism for "an identical table is emitted once
 * and shared by every machine that reads it": a table is named by its
 * CONTENT (element type, length, values), and the first emitter to ask for a
 * content names it. Its first reader is the character-stepped DFA, whose
 * forward, reverse and retry machines read identical class, seed, segment and
 * ill-formed-byte tables (until the pool, each machine emitted its own copy:
 * ~50% of `(*UCP)\b\w+\b`'s .rodata, ~66% of `(*UCP)\b\w*`'s).
 *
 * WHY FILE SCOPE: a table that two functions read cannot live inside either.
 * `pcrec_tbl_emit` writes the pending tables where the emitter calls it,
 * ahead of the first function that reads them; a later ask for a content
 * that was already emitted resolves to it. A content first asked for after
 * the last emit would name a table no one defines: `pcrec_tbl_done` refuses
 * the artifact then.
 *
 * A linear scan per ask: a pool holds tens of tables, each compared once per
 * machine (D77: no index until a measurement asks for one). */
#include <string.h>

#include "core/internal.h"

struct PcrecTbl {
    struct PcrecTbl *next;
    const char      *name, *type;
    const int       *v;
    int              n;
    int              seq;      /* ask order: emitted iff seq < Job.tbl_out */
};

/* The smallest C type for `v[0..n)` (internal.h). */
const char *pcrec_tbl_type(const int *v, int n)
{
    int lo = 0, hi = 0;
    for (int i = 0; i < n; i++) {
        if (v[i] < lo) lo = v[i];
        if (v[i] > hi) hi = v[i];
    }
    if (lo >= 0 && hi <= 255) return "unsigned char";
    if (lo >= -32768 && hi <= 32767) return "short";
    return "int";
}

/* The pool's name for table `type`/`v`/`n`, pooling it under `name` when
 * the content is new (internal.h). `v` is copied: callers reuse scratch. */
const char *pcrec_tbl_ref(Ctx *cx, const char *name, const char *type,
                          const int *v, int n)
{
    Job *job = cx->job;
    for (const struct PcrecTbl *t = job->tbl_head; t; t = t->next)
        if (t->n == n && strcmp(t->type, type) == 0 &&
            memcmp(t->v, v, (size_t)n * sizeof *v) == 0)
            return t->name;
    struct PcrecTbl *t = pcrec_arena_alloc(&cx->arena, sizeof *t);
    int *cp = pcrec_arena_alloc(&cx->arena, (size_t)(n > 0 ? n : 1) * sizeof *cp);
    if (n > 0) memcpy(cp, v, (size_t)n * sizeof *v);
    *t = (struct PcrecTbl){ job->tbl_head, name, type, cp, n, job->tbl_n++ };
    job->tbl_head = t;
    return name;
}

/* Writes one pooled table at file scope, sixteen values to the line. */
static void tbl_write(StrBuf *c, const struct PcrecTbl *t)
{
    pcrec_sb_printf(c, "static const %s %s[%d] = {", t->type, t->name,
                    t->n > 0 ? t->n : 1);
    for (int i = 0; i < t->n; i++) {
        if (i % 16 == 0) pcrec_sb_puts(c, "\n   ");
        pcrec_sb_printf(c, " %d,", t->v[i]);
    }
    if (t->n == 0) pcrec_sb_puts(c, " 0");
    pcrec_sb_puts(c, "\n};\n");
}

/* Writes every table pooled since the last call, in ask order (internal.h). */
void pcrec_tbl_emit(Ctx *cx, StrBuf *c)
{
    Job *job = cx->job;
    for (int seq = job->tbl_out; seq < job->tbl_n; seq++)
        for (const struct PcrecTbl *t = job->tbl_head; t; t = t->next)
            if (t->seq == seq) tbl_write(c, t);
    job->tbl_out = job->tbl_n;
}

/* Refuses an artifact that pooled a table it never emitted (internal.h). */
void pcrec_tbl_done(Ctx *cx)
{
    if (cx->job->tbl_out != cx->job->tbl_n)
        pcrec_ctx_fail(cx, 0, "internal error: %d pooled table(s) were never "
                       "emitted, so nothing defines them",
                       cx->job->tbl_n - cx->job->tbl_out);
}
