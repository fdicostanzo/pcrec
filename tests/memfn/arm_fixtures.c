/* tests/memfn/arm_fixtures.c — C5's fixture renderer ([MEMFN] R4c;
 * docs/design/memfn/integration.md §17.4): a FIXED set of site descriptions,
 * one or more per scalar arm shape, rendered through the kit's public entry
 * points with this file's own hooks and sink, each part written to its own
 * file for run_arm_pins.sh to digest against tests/memfn/pins/arms.tsv.
 *
 * It includes the kit's ONE public header and links build/libpcrec.a (the
 * kit's objects are in it); nothing of pcrec's. The hooks are this file's
 * stand-ins for pcrec's (a marker comment for a note, the `memcmp` spelling
 * for a run compare), so a pin moves only when an ARM's text moves, never
 * with pcrec's scaffolding (F12).
 *
 *   arm_fixtures OUTDIR [--perturb]
 *
 * writes OUTDIR/<fixture>.def and OUTDIR/<fixture>.use and prints one line
 * per fixture, `<fixture>\t<form_id>`. --perturb moves one byte of one
 * fixture's description (pre-onebyte-rest's first byte, 64 -> 65): the
 * script's witness that a pinned digest sees a change in what it pins.
 * Exit 1 on any kit refusal. */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "memfn.h"

/* ---- a growable text sink ------------------------------------------------ */

typedef struct { char *p; size_t len, cap; } Text;

static void text_put(Text *t, const char *s, size_t n)
{
    if (t->len + n + 1 > t->cap) {
        t->cap = (t->len + n + 1) * 2;
        t->p = realloc(t->p, t->cap);
        if (!t->p) { perror("realloc"); exit(2); }
    }
    memcpy(t->p + t->len, s, n);
    t->len += n;
    t->p[t->len] = 0;
}

static void s_puts(void *u, const char *s) { text_put(u, s, strlen(s)); }

static void s_vprintf(void *u, const char *fmt, va_list ap)
{
    char buf[4096];
    int n = vsnprintf(buf, sizeof buf, fmt, ap);
    if (n < 0 || (size_t)n >= sizeof buf) { fputs("fixture line too long\n", stderr); exit(2); }
    text_put(u, buf, (size_t)n);
}

static int s_cmt_open(void *u, int tier) { (void)tier; s_puts(u, "/* "); return 1; }
static void s_cmt_close(void *u) { s_puts(u, " */\n"); }

/* pcrec's legend spelling: printable ASCII quoted, else a number. */
static void s_legend(void *u, uint8_t b)
{
    char buf[16];
    if (b == '\'') snprintf(buf, sizeof buf, "'\\''");
    else if (b == '\\') snprintf(buf, sizeof buf, "'\\\\'");
    else if (b >= 0x20 && b < 0x7f) snprintf(buf, sizeof buf, "'%c'", b);
    else snprintf(buf, sizeof buf, "%d", b);
    s_puts(u, buf);
}

static mf_sink sink_of(Text *t)
{
    mf_sink s = { .u = t, .puts = s_puts, .vprintf = s_vprintf,
                  .cmt_open = s_cmt_open, .cmt_close = s_cmt_close,
                  .legend_byte = s_legend };
    return s;
}

static void *a_alloc(void *u, size_t n) { (void)u; return calloc(1, n); }

/* ---- the hooks ------------------------------------------------------------ */

typedef struct { const mf_site *site; const char *fn1; const char *indent; } Fx;

static const char *h_fn_name(void *u, uint32_t ref)
{
    return ref == 2 ? "rx_reqrun_whole" : ((Fx *)u)->fn1;
}

static const char *h_table_name(void *u, uint32_t ref)
{
    static char names[16][24];   /* test code: one name per offset */
    (void)u;
    snprintf(names[ref & 15], sizeof names[0], "rx_ofs_k%u", ref - 1);
    return names[ref & 15];
}

static void h_note(void *u, mf_sink *c, uint32_t part)
{
    Fx *fx = u;
    char buf[64];
    snprintf(buf, sizeof buf, "%s/* note %u */\n", fx->indent ? fx->indent : "", part);
    c->puts(c->u, buf);
}

static const char *h_note_tag(void *u, uint32_t part)
{
    const mf_site *s = ((Fx *)u)->site;
    return s->op == MF_OP_ALL_PRESENT && s->preds[part].fn_ref == 2
         ? "[K66]" : "[OPT-REQPOS]";
}

/* The run compare as runcmp.c's two fallback rows spell it. */
static void h_run_cmp(void *u, mf_sink *c, const char *base, int32_t off,
                      uint32_t term)
{
    const mf_site *s = ((Fx *)u)->site;
    const mf_pred *p = s->op == MF_OP_ALL_PRESENT ? &s->preds[term / MF_MAX_TERM] : &s->pred;
    const mf_term *t = &p->term[term % MF_MAX_TERM];
    char buf[512];
    if (!t->mask) {
        size_t n = (size_t)snprintf(buf, sizeof buf, "!memcmp(%s", base);
        if (off) n += (size_t)snprintf(buf + n, sizeof buf - n, " + %d", off);
        n += (size_t)snprintf(buf + n, sizeof buf - n, ", \"%.*s\", %u)",
                              (int)t->run_len, (const char *)t->run, t->run_len);
        c->puts(c->u, buf);
        return;
    }
    for (uint32_t i = 0; i < t->run_len; i++) {
        snprintf(buf, sizeof buf, "%s((%s)[%d] & %d) == %d", i ? " && " : "", base,
                 off + (int)i, t->mask[i], t->run[i]);
        c->puts(c->u, buf);
    }
}

/* ---- building the fixtures ------------------------------------------------ */

static void t_byte(mf_term *t, int off, int b)
{
    memset(t, 0, sizeof *t);
    t->kind = MF_T_SET;
    t->offset = off;
    t->set[b >> 3] = (uint8_t)(1u << (b & 7));
    t->ppm_hi = MF_PPM_FULL;
}

static void t_set(mf_term *t, int off, const char *members, uint32_t ref)
{
    t_byte(t, off, (unsigned char)members[0]);
    for (const char *m = members; *m; m++)
        t->set[(unsigned char)*m >> 3] |= (uint8_t)(1u << (*m & 7));
    t->table_ref = ref;
    t->need = MF_OPTIONAL;
}

static void t_run(mf_term *t, int off, const char *run, const uint8_t *mask)
{
    memset(t, 0, sizeof *t);
    t->kind = MF_T_RUN;
    t->offset = off;
    t->run = (const uint8_t *)run;
    t->mask = mask;
    t->run_len = (uint32_t)strlen(run);
    t->ppm_hi = MF_PPM_FULL;
}

static mf_site base_site(void)
{
    mf_site s;
    memset(&s, 0, sizeof s);
    s.abi = MF_SITE_ABI;
    s.ret_pred = MF_NO_PRED;
    s.span_hi = MF_SPAN_UNBOUNDED;
    s.cand_ppm_hi = MF_PPM_FULL;
    s.empty = MF_EMPTY_MISS;
    s.consumer = MF_C_ENGINE;
    s.policy = MF_P_PORTABLE_ONLY;
    return s;
}

static mf_site ofs_site(void)
{
    mf_site s = base_site();
    s.form = MF_FORM_FUNC;
    s.op = MF_OP_FIND;
    s.handoff = MF_H_RETURN;
    s.use = MF_USE_POSITION;
    s.pred.fn_ref = 1;
    return s;
}

static mf_site pre_site(mf_pred *p, int n, int ret)
{
    mf_site s = base_site();
    s.form = MF_FORM_STMT;
    s.op = MF_OP_ALL_PRESENT;
    s.handoff = ret >= 0 ? MF_H_ASSIGN : MF_H_ON_MISS;
    s.use = ret >= 0 ? MF_USE_POSITION : MF_USE_DISCARD;
    s.ret_pred = ret >= 0 ? (uint8_t)ret : MF_NO_PRED;
    s.npred = (uint16_t)n;
    s.preds = p;
    return s;
}

static void p_byte(mf_pred *p, int b)
{
    memset(p, 0, sizeof *p);
    p->nterm = 1;
    t_byte(&p->term[0], 0, b);
}

static void p_run(mf_pred *p, const char *run, const uint8_t *mask, int pos,
                  uint32_t fn_ref)
{
    memset(p, 0, sizeof *p);
    p->nterm = 1;
    t_run(&p->term[0], 0, run, mask);
    p->plan_pos = (uint16_t)pos;
    p->fn_ref = fn_ref;
}

/* ---- rendering ------------------------------------------------------------ */

static int render(const char *dir, const char *name, const mf_site *s,
                  const char *fn1)
{
    mf_arena a = { NULL, a_alloc };
    mf_art *art = mf_art_begin(&a, "rx", MF_P_PORTABLE_ONLY, 0);
    Text def = { 0 }, use = { 0 };
    mf_sink sd = sink_of(&def), su = sink_of(&use);
    Fx fd = { s, fn1, NULL }, fu = { s, fn1, "    " };
    mf_hooks hd = { .fn_name = h_fn_name, .table_name = h_table_name,
                    .note = h_note, .note_tag = h_note_tag,
                    .run_cmp = h_run_cmp, .on_miss = "return 0;", .u = &fd };
    mf_hooks hu = { .s = "subject", .n = "subject_length", .lo = "search_from",
                    .indent = "    ", .on_miss = "return 0;",
                    .result = "handoff_position", .result_decl = "size_t ",
                    .table_name = h_table_name, .note = h_note, .u = &fu };
    mf_result res = { 0 };
    uint32_t h = 0;
    int rc = mf_define(art, s, &hd, &sd, &h) ||
             (s->form == MF_FORM_FUNC ? mf_call(art, h, &hu, &su)
                                      : mf_use(art, h, &hu, &su, &res)) ||
             mf_art_end(art);
    if (rc) {
        fprintf(stderr, "%s: the kit refused: %s\n", name, mf_art_error(art));
        return 1;
    }
    if (s->form == MF_FORM_FUNC) {
        /* a FUNC site's form id: render its call once more through mf_use */
        Text scratch = { 0 };
        mf_sink sc = sink_of(&scratch);
        mf_use(art, h, &hu, &sc, &res);
        free(scratch.p);
    }
    char path[1024];
    snprintf(path, sizeof path, "%s/%s.def", dir, name);
    FILE *f = fopen(path, "w");
    if (!f) { perror(path); return 1; }
    fputs(def.p ? def.p : "", f);
    fclose(f);
    snprintf(path, sizeof path, "%s/%s.use", dir, name);
    f = fopen(path, "w");
    if (!f) { perror(path); return 1; }
    fputs(use.p ? use.p : "", f);
    fclose(f);
    printf("%s\t%s\n", name, res.form_id);
    free(def.p);
    free(use.p);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc < 2) { fputs("usage: arm_fixtures OUTDIR [--perturb]\n", stderr); return 2; }
    const char *dir = argv[1];
    int perturb = argc > 2 && !strcmp(argv[2], "--perturb");
    static const uint8_t ci3[] = { 0xDF, 0xDF, 0xDF };           /* caseless letters */
    static const uint8_t ci3b[] = { 0xFF, 0xDF, 0xFF };          /* one cube, mid   */
    int bad = 0;

    /* ofsskip: an offset-set row: a table at 0, a byte at 1, the scan at 3 */
    mf_site s = ofs_site();
    s.pred.nterm = 3;
    t_set(&s.pred.term[0], 0, "0123456789", 1);
    t_byte(&s.pred.term[1], 1, 'x');
    s.pred.term[1].need = MF_OPTIONAL;
    t_byte(&s.pred.term[2], 3, 'q');
    s.pred.term[2].need = MF_OPTIONAL;
    s.pred.plan_hint = 2;
    bad |= render(dir, "ofs-set-scan3", &s, "rx_ofsskip");

    /* ofsskip: a run-pinned row: a table at 0, the run /user at 1, scanned on 's' */
    s = ofs_site();
    s.pred.nterm = 2;
    t_set(&s.pred.term[0], 0, "ab", 1);
    t_run(&s.pred.term[1], 1, "/user", NULL);
    s.pred.plan_hint = 1;
    s.pred.plan_pos = 2;
    bad |= render(dir, "ofs-run-pinned", &s, "rx_ofsskip");

    /* ofsskip: the scan at offset 0 (no `+ 0` spelling) */
    s = ofs_site();
    s.pred.nterm = 2;
    t_byte(&s.pred.term[0], 0, 'n');
    t_byte(&s.pred.term[1], 1, 'e');
    s.pred.plan_hint = 0;
    bad |= render(dir, "ofs-scan0", &s, "rx_ofsskip");

    /* ofsskip: a masked run scanned on a two-member cube: the pair leapfrog */
    s = ofs_site();
    s.pred.nterm = 1;
    t_run(&s.pred.term[0], 0, "\x41\x42\x43", ci3);   /* A B C under 0xDF */
    s.pred.plan_hint = 0;
    s.pred.plan_pos = 1;
    bad |= render(dir, "ofs-pair", &s, "rx_ofsskip");

    /* precheck: the one-byte gate and the set rest */
    mf_pred p[4];
    p_byte(&p[0], perturb ? 65 : 64);
    p_byte(&p[1], 65);
    p_byte(&p[2], 66);
    s = pre_site(p, 3, -1);
    bad |= render(dir, "pre-onebyte-rest", &s, "rx_reqrun");

    /* precheck: the leading pick, then the window kept by the handoff */
    mf_pred q[2];
    p_byte(&q[0], 109);
    q[0].need = q[0].term[0].need = MF_OPTIONAL;
    p_run(&q[1], "userpass", NULL, 3, 1);
    s = pre_site(q, 2, 1);
    bad |= render(dir, "pre-lead-handoff", &s, "rx_reqrun");

    /* precheck: a masked window (the pair arm), the whole run, the set rest */
    mf_pred r[4];
    p_run(&r[0], "\x41\x42\x43", ci3b, 1, 1);
    p_run(&r[1], "xyABCz", NULL, 3, 2);
    p_byte(&r[2], 90);
    p_byte(&r[3], 91);
    s = pre_site(r, 4, -1);
    bad |= render(dir, "pre-masked-whole-rest", &s, "rx_reqrun");

    /* precheck: the window alone, kept by the handoff (no lead) */
    mf_pred w[1];
    p_run(&w[0], "dog", NULL, 2, 1);
    s = pre_site(w, 1, 0);
    bad |= render(dir, "pre-window-handoff", &s, "rx_reqrun");

    return bad;
}
