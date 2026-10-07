/* tests/memfn/arm_fixtures.c — C5's fixture renderer ([MEMFN] R4c;
 * docs/design/memfn/integration.md §17.4): a FIXED set of site descriptions,
 * one or more per scalar arm shape, rendered through the kit's public entry
 * points with this file's own hooks and sink, each part written to its own
 * file for run_arm_pins.sh to digest against tests/memfn/pins/arms.tsv.
 *
 * It includes the kit's ONE public header and links build/libpcrec.a (the
 * kit's objects are in it); nothing of pcrec's. The hooks are this file's
 * stand-ins for pcrec's (a marker comment for a note; the sink's string
 * escaper spelled as pcrec_sb_cstr's), so a pin moves only when an ARM's
 * text moves, never with pcrec's scaffolding (F12). Since M1b the run
 * compare is the kit's own (no `run_cmp` hook), and each fixture's art
 * flushes its pending word-load helpers into the `def` part after the use,
 * so the helpers' text is pinned too. Two DECLINE fixtures (lane m1bfix)
 * pin an arm's edge from the other side: an offset-skip site whose miss is
 * not `n`, or that states a floor, must render through `generic`. Every
 * fixture STATES its `miss` (MF_MISS_N unless the fixture says otherwise):
 * since [MEMFN-ROWCON] N3 a row that uses an unstated `miss` declines (R1).
 *
 *   arm_fixtures OUTDIR [--perturb]
 *   arm_fixtures --gate
 *
 * writes OUTDIR/<fixture>.def and OUTDIR/<fixture>.use and prints one line
 * per fixture, `<fixture>\t<form_id>\t<libc>`. --perturb moves one byte of one
 * fixture's description (pre-onebyte-rest's first byte, 64 -> 65): the
 * script's witness that a pinned digest sees a change in what it pins.
 * The line's third column is the art's MEMFN_LIBC stamp (run_arm_pins.sh
 * checks it against a scan of the rendered text).
 * Exit 1 on any kit refusal.
 *
 * --gate ([MEMFN-ROWCON] N3) runs the GATE CASES instead and writes nothing:
 * sites built to be DECLINED at define (the walk moves on: the form id that
 * renders them) or REFUSED (the refusal's text), one line per case,
 * `<case>\tRENDER\t<form_id>` or `<case>\tREFUSE\t<text>`. They are what
 * shows the general gate covers the ad hoc K96 tests N3 deleted from
 * ofsskip.c (a floor or a non-`n` miss at define and at the call) and the
 * rulings N3 makes real (F1, an unstated miss, K-1's fn_ref). The EXPECTED
 * outcome of each is run_arm_pins.sh's (check 6), never this file's. */
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

/* A string literal's body, escaped as pcrec_sb_cstr escapes it. */
static void s_cstr(void *u, const uint8_t *b, size_t n)
{
    char buf[8];
    for (size_t i = 0; i < n; i++) {
        if (b[i] == '"' || b[i] == '\\' || b[i] == '?') snprintf(buf, sizeof buf, "\\%c", b[i]);
        else if (b[i] >= 32 && b[i] < 127) snprintf(buf, sizeof buf, "%c", b[i]);
        else snprintf(buf, sizeof buf, "\\%03o", b[i]);
        s_puts(u, buf);
    }
}

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

/* A sink that keeps only the MEMFN_LIBC stamp (the libc record, libcnote). */
static void c_stamp(void *u, const char *name, const char *value)
{
    if (!strcmp(name, "MEMFN_LIBC")) snprintf(u, 256, "%s", value);
}

static void c_stamp_int(void *u, const char *name, long long value)
{
    (void)u; (void)name; (void)value;
}

static mf_sink sink_of(Text *t)
{
    mf_sink s = { .u = t, .puts = s_puts, .vprintf = s_vprintf,
                  .cmt_open = s_cmt_open, .cmt_close = s_cmt_close,
                  .cstr = s_cstr, .legend_byte = s_legend };
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

/* The run compare's own site: one RUN term behind the caller's guard. */
static mf_site run_site(const char *run, const uint8_t *mask, int off,
                        uint64_t denies)
{
    mf_site s = base_site();
    s.form = MF_FORM_EXPR;
    s.op = MF_OP_VERIFY;
    s.handoff = MF_H_BOOL;
    s.empty = MF_EMPTY_EXCLUDED;
    s.guard_by_caller = 1;
    s.use = MF_USE_DISCARD;
    s.policy |= MF_P_INLOOP;
    s.denies = denies;
    s.pred.nterm = 1;
    s.pred.plan_hint = MF_NO_PRED;
    memset(&s.pred.term[0], 0, sizeof s.pred.term[0]);
    s.pred.term[0].kind = MF_T_RUN;
    s.pred.term[0].offset = off;
    s.pred.term[0].run = (const uint8_t *)run;
    s.pred.term[0].mask = mask;
    s.pred.term[0].run_len = (uint32_t)strlen(run);
    s.pred.term[0].ppm_hi = MF_PPM_FULL;
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
    s.on_miss_leaves = 1;           /* the hooks' on_miss is "return 0;" */
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

/* render_h's `n`, `miss` and `floor` for both hook sets: NULL in every
 * fixture but the decline fixtures (lane m1bfix) */
typedef struct { const char *n, *miss, *floor; } Bounds;

static int render_h(const char *dir, const char *name, const mf_site *s,
                    const char *fn1, Bounds b)
{
    mf_arena a = { NULL, a_alloc };
    mf_art *art = mf_art_begin(&a, "rx", MF_P_PORTABLE_ONLY, s->denies);
    Text def = { 0 }, use = { 0 };
    mf_sink sd = sink_of(&def), su = sink_of(&use);
    Fx fd = { s, fn1, NULL }, fu = { s, fn1, "    " };
    mf_hooks hd = { .fn_name = h_fn_name, .table_name = h_table_name,
                    .note = h_note, .note_tag = h_note_tag, .u = &fd,
                    .n = b.n, .miss = b.miss, .floor = b.floor };
    mf_hooks hu = { .s = "subject", .n = "subject_length", .lo = "search_from",
                    .miss = b.miss, .floor = b.floor,
                    .indent = "    ", .on_miss = "return 0;",
                    .result = "handoff_position", .result_decl = "size_t ",
                    .table_name = h_table_name, .note = h_note, .u = &fu };
    mf_result res = { 0 };
    uint32_t h = 0;
    int rc = mf_define(art, s, &hd, &sd, &h) ||
             (s->form == MF_FORM_FUNC ? mf_call(art, h, &hu, &su)
                                      : mf_use(art, h, &hu, &su, &res)) ||
             mf_flush_helpers(art, &sd) ||
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
    /* the libc record the art holds once its sites are rendered: the kit
     * records it as it renders (libcnote), with no pcrec scan in this driver */
    char libc[256] = "?";
    mf_sink sk = { .u = libc, .stamp = c_stamp, .stamp_int = c_stamp_int };
    if (mf_stamps(art, &sk)) {
        fprintf(stderr, "%s: mf_stamps refused: %s\n", name, mf_art_error(art));
        return 1;
    }
    printf("%s\t%s\t%s\n", name, res.form_id, libc);
    free(def.p);
    free(use.p);
    return 0;
}

static int render(const char *dir, const char *name, const mf_site *s,
                  const char *fn1)
{
    return render_h(dir, name, s, fn1, (Bounds){ NULL, MF_MISS_N, NULL });
}

/* ---- the gate cases (--gate, N3) ----------------------------------------- */

/* One gate case: define with `hd`, then use (or call, for a FUNC site) with
 * `hu`; prints the outcome line. Never fails the driver: the outcome is the
 * script's to judge. */
static void gate_case(const char *name, const mf_site *s, const mf_hooks *hd,
                      const mf_hooks *hu)
{
    mf_arena a = { NULL, a_alloc };
    mf_art *art = mf_art_begin(&a, "rx", MF_P_PORTABLE_ONLY, s->denies);
    Text def = { 0 }, use = { 0 };
    mf_sink sd = sink_of(&def), su = sink_of(&use);
    mf_result res = { 0 };
    uint32_t h = 0;
    int rc = mf_define(art, s, hd, &sd, &h) || mf_use(art, h, hu, &su, &res);
    if (rc) printf("%s\tREFUSE\t%s\n", name, mf_art_error(art) ? mf_art_error(art) : "");
    else    printf("%s\tRENDER\t%s\n", name, res.form_id);
    free(def.p);
    free(use.p);
}

/* The define and use hooks render_h passes, with `miss`, `floor` and `s`
 * given per side (NULL: unstated). */
static void gate_hooks(Fx *fd, Fx *fu, mf_hooks *hd, mf_hooks *hu,
                       const char *dmiss, const char *dfloor, const char *ds,
                       const char *umiss, const char *ufloor, const char *us)
{
    mf_hooks d = { .fn_name = h_fn_name, .table_name = h_table_name,
                   .note_tag = h_note_tag, .u = fd,
                   .s = ds, .miss = dmiss, .floor = dfloor };
    mf_hooks u = { .s = us, .n = "subject_length", .lo = "search_from",
                   .miss = umiss, .floor = ufloor,
                   .indent = "    ", .on_miss = "return 0;",
                   .result = "handoff_position", .result_decl = "size_t ",
                   .table_name = h_table_name, .u = fu };
    *hd = d;
    *hu = u;
}

static void gate_cases(void)
{
    static const char NONID[] = "(subject + 0)";   /* not an identifier (F1) */
    mf_hooks hd, hu;
    mf_site s = ofs_site();
    s.pred.nterm = 2;
    t_byte(&s.pred.term[0], 0, 'n');
    t_byte(&s.pred.term[1], 1, 'e');
    s.pred.plan_hint = 0;
    Fx fd = { &s, "rx_ofsskip", NULL }, fu = { &s, "rx_ofsskip", "    " };

    /* ofsskip, K96's deleted call-time tests: a floor, a non-n miss */
    gate_hooks(&fd, &fu, &hd, &hu, MF_MISS_N, NULL, NULL, MF_MISS_N, "search_floor", "subject");
    gate_case("ofs-call-floor", &s, &hd, &hu);
    gate_hooks(&fd, &fu, &hd, &hu, MF_MISS_N, NULL, NULL, "((size_t)-1)", NULL, "subject");
    gate_case("ofs-call-miss-other", &s, &hd, &hu);
    /* ruling (b): an unstated miss, at the call and at the define */
    gate_hooks(&fd, &fu, &hd, &hu, MF_MISS_N, NULL, NULL, NULL, NULL, "subject");
    gate_case("ofs-call-miss-unstated", &s, &hd, &hu);
    gate_hooks(&fd, &fu, &hd, &hu, NULL, NULL, NULL, MF_MISS_N, NULL, "subject");
    gate_case("ofs-define-miss-unstated", &s, &hd, &hu);
    /* K96's deleted define-time tests: a floor, a non-n miss */
    gate_hooks(&fd, &fu, &hd, &hu, MF_MISS_N, "search_floor", NULL, MF_MISS_N, "search_floor", "subject");
    gate_case("ofs-define-floor", &s, &hd, &hu);
    gate_hooks(&fd, &fu, &hd, &hu, "((size_t)-1)", NULL, NULL, "((size_t)-1)", NULL, "subject");
    gate_case("ofs-define-miss-other", &s, &hd, &hu);
    /* ruling (a), F1: a non-identifier s at define reaches generic; one
       stated only at the call is refused */
    gate_hooks(&fd, &fu, &hd, &hu, MF_MISS_N, NULL, NONID, MF_MISS_N, NULL, NONID);
    gate_case("ofs-define-nonident", &s, &hd, &hu);
    gate_hooks(&fd, &fu, &hd, &hu, MF_MISS_N, NULL, NULL, MF_MISS_N, NULL, NONID);
    gate_case("ofs-call-nonident", &s, &hd, &hu);
    /* ruling (c), K-1: a FUNC site stating fn_ref 0 states no name */
    mf_site z = s;
    z.pred.fn_ref = 0;
    gate_hooks(&fd, &fu, &hd, &hu, MF_MISS_N, NULL, NULL, MF_MISS_N, NULL, "subject");
    gate_case("ofs-fn_ref-0", &z, &hd, &hu);

    /* an ALL_PRESENT FUNC site (generic's): its name is site.pred.fn_ref */
    mf_pred ap[1];
    p_byte(&ap[0], 'a');
    mf_site g = base_site();
    g.form = MF_FORM_FUNC;
    g.op = MF_OP_ALL_PRESENT;
    g.handoff = MF_H_BOOL;
    g.empty = MF_EMPTY_MISS;
    g.npred = 1;
    g.preds = ap;
    g.pred.fn_ref = 0;
    Fx gd = { &g, "rx_allp", NULL }, gu = { &g, "rx_allp", "    " };
    gate_hooks(&gd, &gu, &hd, &hu, MF_MISS_N, NULL, NULL, MF_MISS_N, NULL, "subject");
    gate_case("allp-func-fn_ref-0", &g, &hd, &hu);
    g.pred.fn_ref = 7;
    gate_case("allp-func-fn_ref-7", &g, &hd, &hu);

    /* precheck: the split by handoff, and K96's floor at its run calls */
    mf_pred q[2];
    p_byte(&q[0], 109);
    q[0].need = q[0].term[0].need = MF_OPTIONAL;
    p_run(&q[1], "userpass", NULL, 3, 1);
    mf_site pa = pre_site(q, 2, 1);
    Fx pd = { &pa, "rx_reqrun", NULL }, pu = { &pa, "rx_reqrun", "    " };
    gate_hooks(&pd, &pu, &hd, &hu, NULL, NULL, NULL, NULL, NULL, "subject");
    gate_case("pre-assign-miss-unstated", &pa, &hd, &hu);
    gate_hooks(&pd, &pu, &hd, &hu, NULL, NULL, NULL, MF_MISS_N, NULL, "subject");
    gate_case("pre-assign-miss-token", &pa, &hd, &hu);
    gate_hooks(&pd, &pu, &hd, &hu, "((size_t)-1)", NULL, NULL, "((size_t)-1)", NULL, "subject");
    gate_case("pre-assign-miss-other", &pa, &hd, &hu);
    mf_site po = pre_site(q, 2, -1);
    Fx od = { &po, "rx_reqrun", NULL }, ou = { &po, "rx_reqrun", "    " };
    gate_hooks(&od, &ou, &hd, &hu, "((size_t)-1)", NULL, NULL, "((size_t)-1)", NULL, "subject");
    gate_case("pre-onmiss-miss-other", &po, &hd, &hu);
    gate_hooks(&od, &ou, &hd, &hu, NULL, NULL, NULL, NULL, "search_floor", "subject");
    gate_case("pre-use-floor", &po, &hd, &hu);
    gate_hooks(&od, &ou, &hd, &hu, NULL, "search_floor", NULL, NULL, "search_floor", "subject");
    gate_case("pre-define-floor", &po, &hd, &hu);
    gate_hooks(&od, &ou, &hd, &hu, NULL, NULL, NONID, NULL, NULL, NONID);
    gate_case("pre-define-nonident", &po, &hd, &hu);
    gate_hooks(&od, &ou, &hd, &hu, NULL, NULL, NULL, NULL, NULL, NONID);
    gate_case("pre-use-nonident", &po, &hd, &hu);

    /* runcmp: F1 through mf_emit's one hook set */
    mf_site r = run_site("abcdefgh", NULL, 0, 0);
    Fx rd = { &r, NULL, NULL }, ru = { &r, NULL, "    " };
    gate_hooks(&rd, &ru, &hd, &hu, NULL, NULL, NONID, NULL, NULL, NONID);
    hd.lo = hu.lo;
    gate_case("run-nonident", &r, &hd, &hu);
}

int main(int argc, char **argv)
{
    if (argc < 2) { fputs("usage: arm_fixtures OUTDIR [--perturb] | --gate\n", stderr); return 2; }
    if (!strcmp(argv[1], "--gate")) {
        gate_cases();
        return 0;
    }
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

    /* ofsskip's edge (lane m1bfix): its function returns `n` on a miss and
     * reads from `pos` up, so a site whose miss is another value, or that
     * states a floor, is the generic row's. The first stays ofsskip: a
     * miss stated as the `n` hook's own text. */
    s = ofs_site();
    s.pred.nterm = 2;
    t_set(&s.pred.term[0], 0, "ab", 1);
    t_run(&s.pred.term[1], 1, "/user", NULL);
    s.pred.plan_hint = 1;
    s.pred.plan_pos = 2;
    bad |= render_h(dir, "ofs-miss-n", &s, "rx_ofsskip",
                    (Bounds){ "subject_length", "subject_length", NULL });
    /* the same site, the miss stated by the MF_MISS_N token (lane missn):
     * the same arm, and the same bytes as ofs-miss-n */
    bad |= render_h(dir, "ofs-miss-token", &s, "rx_ofsskip",
                    (Bounds){ "subject_length", MF_MISS_N, NULL });
    bad |= render_h(dir, "ofs-decline-miss", &s, "rx_ofsskip",
                    (Bounds){ "subject_length", "((size_t)-1)", NULL });
    bad |= render_h(dir, "ofs-decline-floor", &s, "rx_ofsskip",
                    (Bounds){ "subject_length", "subject_length", "search_floor" });

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
    /* the same ASSIGN site with `miss` stated by the token (lane missn) */
    bad |= render_h(dir, "pre-lead-handoff-miss-token", &s, "rx_reqrun",
                    (Bounds){ "subject_length", MF_MISS_N, NULL });

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

    /* runcmp (M1b): the four rows and the deny, one fixture each */
    static const uint8_t ci4[] = { 0xDF, 0xFF, 0xDF, 0x00 };      /* cube, exact, cube, don't-care */
    s = run_site("abc", NULL, 0, 0);                              /* L 3: overlap */
    bad |= render(dir, "run-overlap3", &s, NULL);
    s = run_site("ab\"?\\cdefghij", NULL, 2, 0);                  /* L 13: overlap at w8, escapes */
    bad |= render(dir, "run-overlap13", &s, NULL);
    s = run_site("abcdefgh", NULL, 0, 0);                         /* L 8: memcmp */
    bad |= render(dir, "run-memcmp8", &s, NULL);
    s = run_site("A-C\x00", ci4, 1, 0);                           /* masked: words */
    s.pred.term[0].run_len = 4;
    bad |= render(dir, "run-masked-words", &s, NULL);
    s = run_site("A-C\x00", ci4, 1, MF_D_RUN_OVERLAP);            /* masked, denied: bytes */
    s.pred.term[0].run_len = 4;
    bad |= render(dir, "run-masked-deny", &s, NULL);
    s = run_site("abc", NULL, 0, MF_D_RUN_OVERLAP);               /* exact, denied: memcmp */
    bad |= render(dir, "run-exact-deny", &s, NULL);

    return bad;
}
