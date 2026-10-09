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
 *   arm_fixtures OUTDIR --only FIXTURE
 *   arm_fixtures --gate [--gate-only CASE]
 *
 * writes OUTDIR/<fixture>.def and OUTDIR/<fixture>.use and prints one line
 * per fixture, `<fixture>\t<form_id>\t<libc>`. --perturb moves one byte of one
 * fixture's description (pre-onebyte-rest's first byte, 64 -> 65): the
 * script's witness that a pinned digest sees a change in what it pins.
 * The line's third column is the art's MEMFN_LIBC stamp (run_arm_pins.sh
 * checks it against a scan of the rendered text).
 * Exit 1 on any kit refusal. --only renders the one named fixture and
 * nothing else (exit 2 if no fixture has that name): run_rows.sh
 * ([MEMFN-ROWCON] N4) runs each fixture alone under an MF_TRACE kit, so the
 * trace's rows are that fixture's own.
 *
 * --gate ([MEMFN-ROWCON] N3) runs the GATE CASES instead and writes nothing:
 * sites built to be DECLINED at define (the walk moves on: the form id that
 * renders them) or REFUSED (the refusal's text), one line per case,
 * `<case>\tRENDER\t<form_id>` or `<case>\tREFUSE\t<text>`. They are what
 * shows the general gate covers the ad hoc K96 tests N3 deleted from
 * ofsskip.c (a floor or a non-`n` miss at define and at the call) and the
 * rulings N3 makes real (F1, an unstated miss, K-1's fn_ref). The EXPECTED
 * outcome of each is run_arm_pins.sh's (check 6), never this file's.
 * --gate-only CASE runs the one named case (exit 2 if none has that name):
 * rows_check.py (check E) runs each ADVANCE shape-class case alone under an
 * MF_TRACE kit and reads its hooks' classes off the trace's REACH lines.
 *
 * R4h prep: two pinned ADVANCE fixtures (adv-kit-count, adv-caller-count:
 * the counter owned by the kit and by the caller, MF_SITE_ABI 5), and gate
 * cases for the caller-owned counter's rules and for the ADVANCE hooks'
 * shape classes (CONJ `more`, POSTFIX `peek`, EXPR_STMT `step`). */
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

/* --only: render this fixture alone (NULL: every fixture); only_seen counts
 * the fixtures that matched it. */
static const char *only;
static int only_seen;

static int skip_fixture(const char *name)
{
    if (!only) return 0;
    if (strcmp(name, only)) return 1;
    only_seen++;
    return 0;
}

static int render_h(const char *dir, const char *name, const mf_site *s,
                    const char *fn1, Bounds b)
{
    if (skip_fixture(name)) return 0;
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

/* R4g's PF find (memfn/src/pffind.c): FIND / STMT / ASSIGN over one SET term,
 * with the hooks pcrec's pcrec_emit_find gives it (src/gen/emit_dfa.c,
 * find_site): the cursor is both `lo` and `result`, no declaration, no note,
 * the miss the range's end, `on_miss` only on the unbounded memchr. */
static mf_site pf_site(int bounded, int table)
{
    mf_site s = base_site();
    s.form = MF_FORM_STMT;
    s.op = MF_OP_FIND;
    s.handoff = MF_H_ASSIGN;
    s.use = MF_USE_POSITION;
    s.empty = table ? MF_EMPTY_NOP : MF_EMPTY_EXCLUDED;
    s.end_back = (uint8_t)bounded;
    s.on_miss_leaves = !table && !bounded;
    s.pred.nterm = 1;
    s.pred.plan_hint = MF_NO_PRED;
    return s;
}

/* One site through mf_emit with the caller's ONE hook set `h`; its `.def` and
 * `.use` parts written under `dir`, its form id and libc record printed. */
static int render_emit(const char *dir, const char *name, const mf_site *s,
                       const mf_hooks *hp)
{
    mf_arena a = { NULL, a_alloc };
    mf_art *art = mf_art_begin(&a, "rx", MF_P_PORTABLE_ONLY, s->denies);
    Text def = { 0 }, use = { 0 };
    mf_sink sd = sink_of(&def), su = sink_of(&use);
    mf_hooks h = *hp;
    mf_result res = { 0 };
    if (mf_emit(art, s, &h, &su, &sd, &res) || mf_art_end(art)) {
        fprintf(stderr, "%s: the kit refused: %s\n", name, mf_art_error(art));
        return 1;
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

static int render_pf(const char *dir, const char *name, const mf_site *s,
                     const char *result, const char *decl)
{
    if (skip_fixture(name)) return 0;
    Fx fx = { s, NULL, "    " };
    int table = s->pred.term[0].table_ref != 0;
    mf_hooks h = { .s = "subject", .n = "subject_length", .lo = "scan_position",
                   .result = result, .result_decl = decl,
                   .miss = s->end_back ? "subject_length - 1" : MF_MISS_N,
                   .on_miss = !table && !s->end_back ? "return 0;" : NULL,
                   .table_name = table ? h_table_name : NULL,
                   .indent = "    ", .u = &fx };
    return render_emit(dir, name, s, &h);
}

/* ---- the reads-below FIND (M4 prep, R-7: Q-R7-1/2/3) ----------------------
 *
 * `(?m)^`'s skip as pcrec's emit_attempt describes it at M4 (integration.md
 * §15.7): FIND / STMT / ASSIGN over ONE SET term one byte BELOW the
 * candidate (`\n` at -1), its range bounded by its reads (Q-R7-1: the
 * candidate reaches n), its floor lo's text, its empty range AT_N (Q-R7-2:
 * lo == n over a non-NULL subject) and its on_miss `break;` (Q-R7-3,
 * LOOP_EXIT). `empty`, `floor` and `on_miss` vary per fixture/case. */
static mf_site back_site(mf_empty empty, int byte)
{
    mf_site s = pf_site(0, 0);
    s.empty = empty;
    t_byte(&s.pred.term[0], -1, byte);
    s.pred.term[0].need = MF_REQUIRED;
    return s;
}

/* The MLINE hooks: the attempt loop's `start`, both lo and result, `floor`
 * and `on_miss` per caller, no miss stated (on_miss leaves; under Q-R7-1 the
 * range's end `n` is a HIT, so MF_MISS_N would be a false statement). */
static mf_hooks back_hooks(Fx *fx, const char *floor, const char *on_miss)
{
    mf_hooks h = { .s = "subject", .n = "subject_length", .lo = "start",
                   .floor = floor, .result = "start", .on_miss = on_miss,
                   .indent = "            ", .u = fx };
    return h;
}

/* ---- the MISMATCH (M7 prep, R-8: MF_VOCAB 3, MF_SITE_ABI 7) ---------------
 *
 * The encoding seam's span compare as pcrec's src/enc backends will describe
 * it (Q-R8-2/4/5): STMT / MISMATCH / ON_DIFF over ONE REQUIRED REF term at
 * offset 0, `empty` NOP (an empty reference is EQUAL), `on_miss_leaves` 1,
 * `fold_kind` the fold's FACT; the hooks are the residual entry's own
 * parameter names (`s`, `n`, `at`, `ref`, `reflen`), the loop index `i`
 * declared `size_t `, the sign-encoded failure as on_miss, the fold TEXT
 * with `@` for the byte. */
static const char MM_ASCII[] = "if (@ >= 'A' && @ <= 'Z') @ = (unsigned char)(@ + 32);";
static const char MM_UCP[] = "rx_span_ci_fold(@)";
static const char MM_ON_DIFF[] = "return -(ptrdiff_t)i - 1;";

static mf_site mm_site(mf_fold fk)
{
    mf_site s = base_site();
    s.form = MF_FORM_STMT;
    s.op = MF_OP_MISMATCH;
    s.handoff = MF_H_ON_DIFF;
    s.use = MF_USE_POSITION;
    s.empty = MF_EMPTY_NOP;
    s.on_miss_leaves = 1;
    s.policy |= MF_P_INLOOP;
    s.fold_kind = (uint8_t)fk;
    s.pred.nterm = 1;
    s.pred.plan_hint = MF_NO_PRED;
    s.pred.term[0].kind = MF_T_REF;
    s.pred.term[0].need = MF_REQUIRED;
    return s;
}

static mf_hooks mm_hooks(Fx *fx, const char *fold)
{
    mf_hooks h = { .s = "s", .n = "n", .lo = "at", .ref = "ref", .reflen = "reflen",
                   .result = "i", .result_decl = "size_t ", .on_miss = MM_ON_DIFF,
                   .fold = fold, .indent = "    ", .u = fx };
    return h;
}

/* ---- ADVANCE (R4h prep) ---------------------------------------------------- */

/* The in-loop skip's site (integration.md §15.7's STAY skip / scan-edge loop,
 * M3): STMT / SKIP / ADVANCE over one SET term at offset 0 (the digits),
 * `empty` NOP (the range IS `more`, Q-G2-5), `span_hi` the run's cap, and
 * `count_by_caller` the counter's owner (Q-R4h-1 (a), MF_SITE_ABI 5). */
static mf_site adv_site(int caller, uint64_t span)
{
    mf_site s = base_site();
    s.form = MF_FORM_STMT;
    s.op = MF_OP_SKIP;
    s.handoff = MF_H_ADVANCE;
    s.use = MF_USE_POSITION;
    s.empty = MF_EMPTY_NOP;
    s.span_hi = span;
    s.count_by_caller = (uint8_t)caller;
    s.pred.nterm = 1;
    s.pred.plan_hint = MF_NO_PRED;
    t_set(&s.pred.term[0], 0, "0123456789", 0);
    s.pred.term[0].need = MF_REQUIRED;
    return s;
}

/* The ADVANCE hooks, as pcrec's scan edge spells them (emit_scan_edge, the
 * forward direction): its texts, its counter, and the indent. */
typedef struct { const char *more, *peek, *step, *count; long count_start; } AdvH;

static mf_hooks adv_hooks(AdvH a, Fx *fx)
{
    mf_hooks h = { .more = a.more, .peek = a.peek, .step = a.step,
                   .count = a.count, .count_start = a.count_start,
                   .cursor = "scan_position", .indent = "    ", .u = fx };
    return h;
}

/* advtarget (the R4h frozen target): the rest of what pcrec passes at an
 * in-loop site, its own member text, cursor and indent. */
typedef struct { const char *member, *cursor, *indent; } AdvX;

/* The hooks' user pointer for a target fixture: an Fx first (every other hook
 * reads it as one), then the member text. */
typedef struct { Fx fx; const char *member; } AdvFx;

/* pcrec's member hook as R4h will pass it: its own class test, OPAQUE to the
 * kit (EDGE's `scan_test` text exists only at render, and every site's test
 * reads pcrec's own `peek`, never the byte expression offered). */
static const char *h_adv_member(void *u, uint32_t term, const char *byte_expr)
{
    (void)term;
    (void)byte_expr;
    return ((AdvFx *)u)->member;
}

static const AdvH ADV_EDGE = { "scan_position < subject_length", "subject[scan_position]",
                               "scan_position++", "scan_run_length", 1 };

static int render_adv_x(const char *dir, const char *name, const mf_site *s, AdvH ah,
                        const AdvX *x)
{
    if (skip_fixture(name)) return 0;
    mf_arena a = { NULL, a_alloc };
    mf_art *art = mf_art_begin(&a, "rx", MF_P_PORTABLE_ONLY, s->denies);
    Text def = { 0 }, use = { 0 };
    mf_sink sd = sink_of(&def), su = sink_of(&use);
    AdvFx ax = { { s, NULL, "    " }, x ? x->member : NULL };
    mf_hooks h = adv_hooks(ah, &ax.fx);
    if (x) {
        h.u = &ax;
        h.member = h_adv_member;
        h.cursor = x->cursor;
        h.indent = x->indent;
    }
    mf_result res = { 0 };
    if (mf_emit(art, s, &h, &su, &sd, &res) || mf_art_end(art)) {
        fprintf(stderr, "%s: the kit refused: %s\n", name, mf_art_error(art));
        return 1;
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

static int render_adv(const char *dir, const char *name, const mf_site *s, AdvH ah)
{
    return render_adv_x(dir, name, s, ah, NULL);
}

/* ---- the STRIDED ADVANCE (M6 prep, R-10: MF_SITE_ABI 8) ------------------- */

/* One strided shape: W positions, position i's byte set and pcrec's own
 * class test of it (NULL members: the kit's own set test, s[cursor + i]). */
typedef struct {
    const char *name;
    int         caller;              /* `it_` is the caller's counter */
    uint64_t    span;
    const char *bound;               /* `subject_length` or `lim_` */
    unsigned    w;
    const char *lit;                 /* W literal bytes, or NULL: lo/hi ranges */
    const char *lo, *hi;             /* per position, when lit is NULL */
    int         own;                 /* 1: no member hook (the kit's own test) */
} StrideFx;

/* The hooks' user pointer for a strided fixture: an Fx first, then one
 * member text per term. */
typedef struct { Fx fx; const char *member[MF_MAX_TERM]; } StrideU;

/* pcrec's member hook at a strided site: term i's own class test, opaque. */
static const char *h_stride_member(void *u, uint32_t term, const char *byte_expr)
{
    (void)byte_expr;
    return term < MF_MAX_TERM ? ((StrideU *)u)->member[term] : NULL;
}

/* The strided site: STMT / SKIP / ADVANCE over W REQUIRED SET terms, term i
 * at offset i (RULED Q-R10-2), span_hi the iteration cap (Q-R10-5). */
static mf_site stride_site(const StrideFx *x)
{
    mf_site s = adv_site(x->caller, x->span);
    s.pred.nterm = (uint8_t)x->w;
    for (unsigned i = 0; i < x->w; i++) {
        mf_term *t = &s.pred.term[i];
        if (x->lit) {
            t_byte(t, (int)i, (unsigned char)x->lit[i]);
        } else {
            t_byte(t, (int)i, (unsigned char)x->lo[i]);
            for (int b = (unsigned char)x->lo[i]; b <= (unsigned char)x->hi[i]; b++)
                t->set[b >> 3] |= (uint8_t)(1u << (b & 7));
        }
        t->need = MF_REQUIRED;
    }
    return s;
}

/* Renders strided fixture `x` with the hook texts the VM's cursor rung
 * writes at the site (vm_emit_span_scan, read off build/pcrec's output). */
static int render_stride(const char *dir, const StrideFx *x)
{
    if (skip_fixture(x->name)) return 0;
    mf_site s = stride_site(x);
    char more[96], step[64];
    snprintf(more, sizeof more, "rx_span_cursor + %u <= %s", x->w, x->bound);
    snprintf(step, sizeof step, "rx_span_cursor += %u", x->w);
    StrideU su = { { &s, NULL, "    " }, { NULL } };
    char mtext[MF_MAX_TERM][96];
    for (unsigned i = 0; i < x->w; i++) {
        if (x->lit)
            snprintf(mtext[i], sizeof mtext[i], "subject[rx_span_cursor + %u] == %d", i,
                     (unsigned char)x->lit[i]);
        else
            snprintf(mtext[i], sizeof mtext[i], "(unsigned)(subject[rx_span_cursor + %u] - %d) <= %du",
                     i, (unsigned char)x->lo[i], (unsigned char)x->hi[i] - (unsigned char)x->lo[i]);
        su.member[i] = mtext[i];
    }
    mf_arena a = { NULL, a_alloc };
    mf_art *art = mf_art_begin(&a, "rx", MF_P_PORTABLE_ONLY, s.denies);
    Text def = { 0 }, use = { 0 };
    mf_sink sd = sink_of(&def), sk = sink_of(&use);
    mf_hooks h = { .more = more, .peek = "subject[rx_span_cursor + 0]", .step = step,
                   .count = x->caller ? "it_" : NULL, .count_start = 0,
                   .cursor = "rx_span_cursor", .s = "subject",
                   .member = x->own ? NULL : h_stride_member,
                   .indent = "        ", .u = &su };
    mf_result res = { 0 };
    if (mf_emit(art, &s, &h, &sk, &sd, &res) || mf_art_end(art)) {
        fprintf(stderr, "%s: the kit refused: %s\n", x->name, mf_art_error(art));
        return 1;
    }
    char path[1024];
    snprintf(path, sizeof path, "%s/%s.def", dir, x->name);
    FILE *f = fopen(path, "w");
    if (!f) { perror(path); return 1; }
    fputs(def.p ? def.p : "", f);
    fclose(f);
    snprintf(path, sizeof path, "%s/%s.use", dir, x->name);
    f = fopen(path, "w");
    if (!f) { perror(path); return 1; }
    fputs(use.p ? use.p : "", f);
    fclose(f);
    char libc[256] = "?";
    mf_sink sl = { .u = libc, .stamp = c_stamp, .stamp_int = c_stamp_int };
    if (mf_stamps(art, &sl)) {
        fprintf(stderr, "%s: mf_stamps refused: %s\n", x->name, mf_art_error(art));
        return 1;
    }
    printf("%s\t%s\t%s\n", x->name, res.form_id, libc);
    free(def.p);
    free(use.p);
    return 0;
}

/* The strided shapes (M6 prep): the five pinned under pins/m6_target/ (the
 * VM's strided span loop today, cut from build/pcrec artifacts: the
 * possessive arm over subject_length with and without the caller's `it_`,
 * the greedy arm's MRL-folded `lim_`, utf8's W = 3, and W = 32, the
 * cursor rung's bound), a range-member body, and one the kit tests itself
 * (no member hook: its bytes are s[cursor + i], Q-R10-4). */
static const StrideFx STRIDES[] = {
    { "adv-vmstride-it",    1, 5, "subject_length", 2, "ab", NULL, NULL, 0 },
    { "adv-vmstride",       0, MF_SPAN_UNBOUNDED, "subject_length", 2, "ab", NULL, NULL, 0 },
    { "adv-vmstride-lim",   0, MF_SPAN_UNBOUNDED, "lim_", 2, "ab", NULL, NULL, 0 },
    { "adv-vmstride-u8w3",  0, MF_SPAN_UNBOUNDED, "subject_length", 3, "a\xc3\xa9", NULL, NULL, 0 },
    { "adv-vmstride-w32",   0, MF_SPAN_UNBOUNDED, "subject_length", 32,
      "abcdefghijklmnopqrstuvwxyz012345", NULL, NULL, 0 },
    { "adv-vmstride-range", 0, MF_SPAN_UNBOUNDED, "subject_length", 2, NULL, "a0", "z9", 0 },
    { "adv-vmstride-own",   1, 7, "subject_length", 3, "x\xc3y", NULL, NULL, 1 },
};

/* ---- the gate cases (--gate, N3) ----------------------------------------- */

/* One gate case: define with `hd`, then use (or call, for a FUNC site) with
 * `hu`; prints the outcome line. Never fails the driver: the outcome is the
 * script's to judge. */
static void gate_case(const char *name, const mf_site *s, const mf_hooks *hd,
                      const mf_hooks *hu)
{
    if (skip_fixture(name)) return;
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

    /* R4h prep (a), Q-R4h-1 (a), MF_SITE_ABI 5: the caller-owned counter.
       Owned by the caller, its name is a USE (a conditional `uses` entry):
       stated, it renders; unstated, it is refused naming `count`. The
       kit-owned site with no counter named stays legal (no use). The fact
       itself is 0 or 1 and ADVANCE-only (the vocabulary refuses). */
    mf_site ac = adv_site(1, 16);
    Fx af = { &ac, NULL, "    " };
    mf_hooks ah = adv_hooks(ADV_EDGE, &af);
    gate_case("adv-caller-count", &ac, &ah, &ah);
    AdvH nocount = ADV_EDGE;
    nocount.count = NULL;
    mf_hooks an = adv_hooks(nocount, &af);
    gate_case("adv-caller-count-unstated", &ac, &an, &an);
    mf_site ak = adv_site(0, 16);
    gate_case("adv-kit-count-unstated", &ak, &an, &an);
    gate_case("adv-kit-count", &ak, &ah, &ah);
    mf_site a2 = adv_site(2, 16);
    gate_case("adv-caller-count-2", &a2, &ah, &ah);
    mf_site af2 = pf_site(0, 1);
    t_set(&af2.pred.term[0], 0, "xy", 1);
    af2.pred.term[0].need = MF_REQUIRED;
    af2.count_by_caller = 1;
    gate_hooks(&fd, &fu, &hd, &hu, MF_MISS_N, NULL, NULL, MF_MISS_N, NULL, "subject");
    hu.lo = "scan_position";
    hu.result = "scan_position";
    hu.result_decl = NULL;
    hu.on_miss = NULL;
    gate_case("adv-caller-count-not-advance", &af2, &hd, &hu);

    /* (G3) the ADVANCE hooks' shape classes. Every case RENDERS through the
       generic row (it serves every class); what each text CLASSIFIES as is
       read off an MF_TRACE build by rows_check.py (check E), never here.
       The `in` cases are the texts pcrec's three M3 sites send (§15.7:
       the forward and reverse STAY skip and scan edge, the VM span scan);
       the rest are one shape each that a raw paste would break. */
    static const struct { const char *name; AdvH h; } cls[] = {
        { "adv-cls-fwd",    { "scan_position < subject_length", "subject[scan_position]", "scan_position++", NULL, 0 } },
        { "adv-cls-view",   { "scan_position + 1 < subject_length", "subject[scan_position]", "scan_position++;", NULL, 0 } },
        { "adv-cls-rev",    { "rewind_position > search_from", "subject[rewind_position - 1]", "rewind_position--", NULL, 0 } },
        { "adv-cls-vm",     { "rx_span_cursor + 1 <= lim_", "subject[rx_span_cursor + 0]", "rx_span_cursor += 1", NULL, 0 } },
        { "adv-cls-edge2",  { "a && b < n", "(p + 1)[0]", "p->k++", NULL, 0 } },
        { "adv-cls-arrow",  { "!done && p < q", "s->b[i].c", "i -= 2;", NULL, 0 } },
        { "adv-cls-or",     { "p < n || q", "s[i] + 1", "a++; b++;", NULL, 0 } },
        { "adv-cls-assign", { "p = q", "*p", "{ p++; }", NULL, 0 } },
        { "adv-cls-shift",  { "p <<= 1", "s[i++]", "p++, q++", NULL, 0 } },
        { "adv-cls-tern",   { "c ? p < n : 0", "f(i)", "return 0;", NULL, 0 } },
        { "adv-cls-call",   { "RX_MORE(p)", "s [i]", "if (c) p++", NULL, 0 } },
        { "adv-cls-comma",  { "p < n, q", "s[i]--", "c ? p++ : q++", NULL, 0 } },
        { "adv-cls-trail",  { "p < n &&", "0x41", "unsigned k = 0", NULL, 0 } },
    };
    mf_site au = adv_site(0, MF_SPAN_UNBOUNDED);
    Fx uf = { &au, NULL, "    " };
    for (size_t i = 0; i < sizeof cls / sizeof cls[0]; i++) {
        mf_hooks ch = adv_hooks(cls[i].h, &uf);
        gate_case(cls[i].name, &au, &ch, &ch);
    }

    /* M4 prep (R-7, MF_SITE_ABI 6): the reads-below FIND's three classes.
       POSITIVE: MLINE's own site (AT_N, floor == lo, `break;`) takes
       pf_memchr_back, also with `break ;` spelled loosely and with a JUMP.
       DECLINE: the row serves AT_N only (EXCLUDED would not prove s
       non-NULL on a read-bounded range), its floor must be lo's text, and a
       table set is not its, so each of those goes to the generic row.
       REFUSE: a `break;` (LOOP_EXIT, Q-R7-3) only a no-loop row may paste,
       so a site the back row declines, or an offset-0 memchr site, is
       refused naming `on_miss`; AT_N on ADVANCE has no miss to give
       (Q-R7-2: as MISS). */
    mf_site bk = back_site(MF_EMPTY_AT_N, '\n');
    Fx bf = { &bk, NULL, "            " };
    mf_hooks bh = back_hooks(&bf, "start", "break;");
    gate_case("back-at-n-break", &bk, &bh, &bh);
    bh = back_hooks(&bf, "start", "  break ;  ");
    gate_case("back-at-n-break-spaced", &bk, &bh, &bh);
    bh = back_hooks(&bf, "start", "return 0;");
    gate_case("back-at-n-return", &bk, &bh, &bh);
    mf_site bx = back_site(MF_EMPTY_EXCLUDED, '\n');
    bh = back_hooks(&bf, "start", "return 0;");
    bh.miss = "((size_t)-1)";
    gate_case("back-excluded-generic", &bx, &bh, &bh);
    bh = back_hooks(&bf, "0", "return 0;");
    bh.miss = "((size_t)-1)";
    gate_case("back-floor-not-lo-generic", &bk, &bh, &bh);
    mf_site bt = back_site(MF_EMPTY_AT_N, '\n');
    t_set(&bt.pred.term[0], -1, "\n\r", 1);
    bt.pred.term[0].need = MF_REQUIRED;
    bh = back_hooks(&bf, "start", "return 0;");
    bh.miss = "((size_t)-1)";
    bh.table_name = h_table_name;
    gate_case("back-table-generic", &bt, &bh, &bh);
    bh = back_hooks(&bf, "start", "break;");
    bh.miss = "((size_t)-1)";
    gate_case("back-excluded-break-refused", &bx, &bh, &bh);
    mf_site p0 = pf_site(0, 0);
    t_byte(&p0.pred.term[0], 0, 'x');
    mf_hooks ph = { .s = "subject", .n = "subject_length", .lo = "scan_position",
                    .result = "scan_position", .miss = MF_MISS_N, .on_miss = "break;",
                    .indent = "    ", .u = &bf };
    gate_case("pf-memchr-break-refused", &p0, &ph, &ph);
    mf_site av = adv_site(0, MF_SPAN_UNBOUNDED);
    av.empty = MF_EMPTY_AT_N;
    mf_hooks vh = adv_hooks(cls[0].h, &uf);
    gate_case("adv-at-n-refused", &av, &vh, &vh);

    /* M7 prep (R-8, MF_VOCAB 3, MF_SITE_ABI 7): the MISMATCH. POSITIVE: the
       exact and expression folds take the generic row, the in-place fold
       (a FOLD_STMT text, under ASCII or UCP) the row mismatch_inplace, which
       also takes a BRACED on_miss; a non-identifier hook is parenthesized
       by both. REFUSE: a `break;` (its own loop encloses on_miss, Q-R7-3),
       a fold stated against fold_kind NONE, a stated fold with no fold
       text (R1), a fold text with no `@`, an on_miss that may fall through,
       the vocabulary's shape rules (reverse, a non-NOP empty, a second term,
       a REF term off 0), an unstated `ref` (R1) and fold_kind on a FIND. */
    mf_site me = mm_site(MF_FOLD_NONE), mu = mm_site(MF_FOLD_UCP),
            ma = mm_site(MF_FOLD_ASCII);
    Fx mf = { &me, NULL, "    " };
    mf_hooks mh = mm_hooks(&mf, NULL);
    gate_case("mm-exact", &me, &mh, &mh);
    mh = mm_hooks(&mf, MM_UCP);
    gate_case("mm-expr", &mu, &mh, &mh);
    mh = mm_hooks(&mf, MM_ASCII);
    gate_case("mm-inplace", &ma, &mh, &mh);
    mh.on_miss = "{ return -1; }";
    gate_case("mm-inplace-braced", &ma, &mh, &mh);
    mh = mm_hooks(&mf, MM_ASCII);
    gate_case("mm-ucp-inplace", &mu, &mh, &mh);
    mh = mm_hooks(&mf, "@ | 0x20");
    mh.s = "(sp + 0)";
    mh.reflen = "len - 1";
    gate_case("mm-expr-nonident", &ma, &mh, &mh);
    mh = mm_hooks(&mf, MM_ASCII);
    mh.on_miss = "break;";
    gate_case("mm-loop-exit", &ma, &mh, &mh);
    mh = mm_hooks(&mf, MM_UCP);
    gate_case("mm-none-fold", &me, &mh, &mh);
    mh = mm_hooks(&mf, NULL);
    gate_case("mm-ascii-nofold", &ma, &mh, &mh);
    mh = mm_hooks(&mf, "fold(c)");
    gate_case("mm-fold-noat", &mu, &mh, &mh);
    mf_site ml = mm_site(MF_FOLD_NONE);
    ml.on_miss_leaves = 0;
    mh = mm_hooks(&mf, NULL);
    gate_case("mm-leaves-0", &ml, &mh, &mh);
    mf_site mr = mm_site(MF_FOLD_NONE);
    mr.reverse = 1;
    gate_case("mm-reverse", &mr, &mh, &mh);
    mf_site mm = mm_site(MF_FOLD_NONE);
    mm.empty = MF_EMPTY_MISS;
    gate_case("mm-empty-miss", &mm, &mh, &mh);
    mf_site m2 = mm_site(MF_FOLD_NONE);
    m2.pred.nterm = 2;
    t_byte(&m2.pred.term[1], 0, 'a');
    gate_case("mm-two-terms", &m2, &mh, &mh);
    mf_site m1 = mm_site(MF_FOLD_NONE);
    m1.pred.term[0].offset = 1;
    gate_case("mm-ref-off1", &m1, &mh, &mh);
    mh.ref = NULL;
    gate_case("mm-ref-unstated", &me, &mh, &mh);
    mf_site mk = pf_site(0, 0);
    t_byte(&mk.pred.term[0], 0, 'x');
    mk.fold_kind = MF_FOLD_ASCII;
    gate_case("mm-fold-kind-find", &mk, &ph, &ph);

    /* M6 prep (R-10, MF_SITE_ABI 8): the STRIDED ADVANCE. POSITIVE: W = 2
       and W = MF_MAX_TERM render (the generic row, the only ADVANCE row),
       with no member hook too (the kit's own s[cursor + i]). REFUSED, each
       naming its field: `reverse` at W > 1, a term off its position, an
       OPTIONAL term, a RUN term, a strided non-ADVANCE SKIP (Q-G2-9 holds
       there), and an unstated `s` or `cursor` (the kit's own reads need
       both at W > 1, Q-R10-4: R1 at the use). */
    Fx sf = { NULL, NULL, "    " };
    mf_hooks sh = { .more = "rx_span_cursor + 2 <= subject_length",
                    .peek = "subject[rx_span_cursor + 0]", .step = "rx_span_cursor += 2",
                    .cursor = "rx_span_cursor", .s = "subject", .indent = "        ", .u = &sf };
    mf_site sw = stride_site(&STRIDES[1]);
    sf.site = &sw;
    gate_case("stride-render", &sw, &sh, &sh);
    mf_site s32 = stride_site(&STRIDES[4]);
    gate_case("stride-w32", &s32, &sh, &sh);
    mf_site srv = sw;
    srv.reverse = 1;
    gate_case("stride-reverse", &srv, &sh, &sh);
    mf_site sgap = sw;
    sgap.pred.term[1].offset = 2;
    gate_case("stride-gap", &sgap, &sh, &sh);
    mf_site sopt = sw;
    sopt.pred.term[1].need = MF_OPTIONAL;
    gate_case("stride-optional", &sopt, &sh, &sh);
    mf_site srun = sw;
    t_run(&srun.pred.term[1], 1, "b", NULL);
    srun.pred.term[1].need = MF_REQUIRED;
    gate_case("stride-run-term", &srun, &sh, &sh);
    mf_site sna = ofs_site();
    sna.op = MF_OP_SKIP;
    sna.pred = sw.pred;
    gate_case("stride-not-advance", &sna, &hd, &hu);
    mf_hooks shs = sh;
    shs.s = NULL;
    gate_case("stride-s-unstated", &sw, &shs, &shs);
    mf_hooks shc = sh;
    shc.cursor = NULL;
    gate_case("stride-cursor-unstated", &sw, &shc, &shc);
}

int main(int argc, char **argv)
{
    if (argc < 2) { fputs("usage: arm_fixtures OUTDIR [--perturb] | --gate [--gate-only CASE]\n", stderr); return 2; }
    if (!strcmp(argv[1], "--gate")) {
        if (argc > 3 && !strcmp(argv[2], "--gate-only")) only = argv[3];
        gate_cases();
        if (only && only_seen != 1) {
            fprintf(stderr, "arm_fixtures: --gate-only %s matched %d cases\n", only, only_seen);
            return 2;
        }
        return 0;
    }
    const char *dir = argv[1];
    int perturb = argc > 2 && !strcmp(argv[2], "--perturb");
    if (argc > 3 && !strcmp(argv[2], "--only")) only = argv[3];
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

    /* pffind (R4g): the PF find's four rows, one fixture each, and the walk's
     * in-place edge (a result other than lo is the generic row's) */
    s = pf_site(0, 0);
    t_byte(&s.pred.term[0], 0, 'x');
    bad |= render_pf(dir, "pf-memchr", &s, "scan_position", NULL);
    s = pf_site(1, 0);
    t_byte(&s.pred.term[0], 0, 'x');
    bad |= render_pf(dir, "pf-memchr-bounded", &s, "scan_position", NULL);
    s = pf_site(0, 1);
    t_set(&s.pred.term[0], 0, "xy", 1);
    s.pred.term[0].need = MF_REQUIRED;
    bad |= render_pf(dir, "pf-walk", &s, "scan_position", NULL);
    s = pf_site(1, 1);
    t_set(&s.pred.term[0], 0, "xy", 1);
    s.pred.term[0].need = MF_REQUIRED;
    bad |= render_pf(dir, "pf-walk-bounded", &s, "scan_position", NULL);
    s = pf_site(0, 1);
    t_set(&s.pred.term[0], 0, "xy", 1);
    s.pred.term[0].need = MF_REQUIRED;
    bad |= render_pf(dir, "pf-decline-not-in-place", &s, "hit_position", NULL);

    /* r4gfix: the PF rows' contract audit. Fields memfn.h reads only on
     * ALL_PRESENT / DENSE (ret_pred, npred + preds) are irrelevant to a FIND
     * site: stating them leaves the PF row chosen, its bytes unmoved
     * (finding 1). A stated result_decl on a one-call mf_emit is judged at
     * SELECTION over the use hooks too, so the PF row declines to the generic
     * row, which declares and renders (finding 3). */
    s = pf_site(0, 0);
    t_byte(&s.pred.term[0], 0, 'x');
    s.ret_pred = 2;
    bad |= render_pf(dir, "pf-memchr-ret-pred", &s, "scan_position", NULL);
    {
        mf_pred pp;
        memset(&pp, 0, sizeof pp);
        p_byte(&pp, 'x');
        s = pf_site(0, 1);
        t_set(&s.pred.term[0], 0, "xy", 1);
        s.pred.term[0].need = MF_REQUIRED;
        s.npred = 1;
        s.preds = &pp;
        bad |= render_pf(dir, "pf-walk-preds", &s, "scan_position", NULL);
    }
    s = pf_site(0, 0);
    t_byte(&s.pred.term[0], 0, 'x');
    bad |= render_pf(dir, "pf-emit-result-decl", &s, "scan_position", "size_t ");

    /* M4 prep (R-7): the reads-below FIND, twice. `pf-memchr-back` is MLINE's
     * site through its own row (pf_memchr_back: the memchr, `if (!q) break;`,
     * the store + 1); `find-back-reaches-n` is a G2-style reads-below FIND the
     * row does not take (empty MISS, a stated miss), so the GENERIC row renders
     * it, its loop read-bounded (Q-R7-1). run_arm_pins.sh check 9 compiles and
     * runs both: each must answer n on "a\n" from 0. */
    if (!skip_fixture("pf-memchr-back")) {
        s = back_site(MF_EMPTY_AT_N, '\n');
        Fx fb = { &s, NULL, "            " };
        mf_hooks hb = back_hooks(&fb, "start", "break;");
        bad |= render_emit(dir, "pf-memchr-back", &s, &hb);
    }
    if (!skip_fixture("find-back-reaches-n")) {
        s = back_site(MF_EMPTY_MISS, '\n');
        s.on_miss_leaves = 0;
        Fx fg = { &s, NULL, "    " };
        mf_hooks hg = back_hooks(&fg, "start", NULL);
        hg.lo = "start";
        hg.result = "hit";
        hg.miss = "((size_t)-1)";
        hg.indent = "    ";
        bad |= render_emit(dir, "find-back-reaches-n", &s, &hg);
    }

    /* M7 prep (R-8): the MISMATCH, one fixture per shape the seam's span
     * compare has (Q-R8-9): exact and the UCP expression fold through the
     * generic row, the ASCII in-place fold through mismatch_inplace, each
     * frozen byte for byte under pins/n7_target/ (pcrec's pre-migration loop,
     * run_arm_pins.sh check 10); plus two edges the frozen shapes do not
     * reach: non-identifier hooks and a BRACED on_miss (parenthesized and
     * kept as written) and a hook text naming `y` (the in-place temps
     * renamed). Check 11 compiles all five and runs them. */
    static const struct { const char *name; mf_fold fk; const char *fold;
                          const char *s, *ref, *on_diff; } mmx[] = {
        { "mm-exact",         MF_FOLD_NONE,  NULL,     "s", "ref", MM_ON_DIFF },
        { "mm-ucp-expr",      MF_FOLD_UCP,   MM_UCP,   "s", "ref", MM_ON_DIFF },
        { "mm-ascii-inplace", MF_FOLD_ASCII, MM_ASCII, "s", "ref", MM_ON_DIFF },
        { "mm-nonident",      MF_FOLD_UCP,   "@ | 0x20", "(sp + 0)", "ref",
          "{ return -(ptrdiff_t)i - 1; }" },
        { "mm-inplace-clash", MF_FOLD_ASCII, MM_ASCII, "s", "y", MM_ON_DIFF },
    };
    for (size_t i = 0; i < sizeof mmx / sizeof mmx[0]; i++) {
        if (skip_fixture(mmx[i].name)) continue;
        s = mm_site(mmx[i].fk);
        Fx fm = { &s, NULL, "    " };
        mf_hooks hm = mm_hooks(&fm, mmx[i].fold);
        hm.s = mmx[i].s;
        hm.ref = mmx[i].ref;
        hm.on_miss = mmx[i].on_diff;
        bad |= render_emit(dir, mmx[i].name, &s, &hm);
    }

    /* R4h prep (a): the scan edge's counted loop, its counter owned by the
       kit (declared as the kit's first statement) and by the caller (never
       declared; advanced and capped). The generic row renders both today;
       run_arm_pins.sh check 7 reads the declaration's presence off each. */
    s = adv_site(0, 16);
    bad |= render_adv(dir, "adv-kit-count", &s, ADV_EDGE);
    s = adv_site(1, 16);
    bad |= render_adv(dir, "adv-caller-count", &s, ADV_EDGE);

    /* advtarget (2026-10-08): R4h's FROZEN TARGET, one fixture per in-loop
       shape, each with the hook texts pcrec's emitters write TODAY at that
       site (read off build/pcrec's output for the witness named; the
       sites: dir_fwd_skip/dir_rev_skip, emit_scan_edge, vm_emit_span_scan).
       Each one's .use is ALSO committed verbatim under pins/r4h_target/
       (run_arm_pins.sh check 8): the text pcrec's layout normalization
       must emit, character for character, before R4h migrates the sites at
       zero movers. The term's set is descriptive only: the member hook is
       pcrec's own text and the kit pastes it opaque, parenthesized. */
    static const struct { const char *name; int caller; uint64_t span;
                          const char *set_not, *set; AdvH h; AdvX x; } tgt[] = {
        /* a[^x]*: STAY forward (dir_fwd_skip) */
        { "adv-stay-fwd", 0, MF_SPAN_UNBOUNDED, "x", NULL,
          { "scan_position < subject_length", "subject[scan_position]", "scan_position++",
            NULL, 0 },
          { "rx_forward_stay1[subject[scan_position]]", "scan_position", "            " } },
        /* a[^x]*: STAY reverse (dir_rev_skip; `peek` owns the -1) */
        { "adv-stay-rev", 0, MF_SPAN_UNBOUNDED, "x", NULL,
          { "rewind_position > search_from", "subject[rewind_position - 1]", "rewind_position--",
            NULL, 0 },
          { "rx_reverse_stay0[subject[rewind_position - 1]]", "rewind_position",
            "                " } },
        /* a[^x]*x$: STAY forward with a view (`+ 1 <` in `more`) */
        { "adv-stay-view", 0, MF_SPAN_UNBOUNDED, "x", NULL,
          { "scan_position + 1 < subject_length", "subject[scan_position]", "scan_position++",
            NULL, 0 },
          { "rx_forward_stay1[subject[scan_position]]", "scan_position", "            " } },
        /* [a-z]*: EDGE unbounded (emit_scan_edge, span < 0) */
        { "adv-edge-unbounded", 0, MF_SPAN_UNBOUNDED, NULL, "abcdefghijklmnopqrstuvwxyz",
          { "scan_position < subject_length", "subject[scan_position]", "scan_position++",
            NULL, 0 },
          { "(unsigned)(subject[scan_position] - 97) <= 25u", "scan_position", "            " } },
        /* a[0-9]{3,20}x: EDGE bounded, forward (anchored machine), caller's counter */
        { "adv-edge-counted-fwd", 1, 3, NULL, "0123456789",
          { "scan_position < subject_length", "subject[scan_position]", "scan_position++",
            "scan_run_length", 1 },
          { "(unsigned)(subject[scan_position] - 48) <= 9u", "scan_position", "            " } },
        /* a[0-9]{3,20}x: EDGE bounded, reverse, caller's counter */
        { "adv-edge-counted-rev", 1, 3, NULL, "0123456789",
          { "rewind_position > search_from", "subject[rewind_position - 1]", "rewind_position--",
            "scan_run_length", 1 },
          { "(unsigned)(subject[rewind_position - 1] - 48) <= 9u", "rewind_position",
            "                " } },
        /* (a)[a-z]{2,9}x --engine=vm: VMSPAN with the caller's `it_` */
        { "adv-vmspan-it", 1, 9, NULL, "abcdefghijklmnopqrstuvwxyz",
          { "rx_span_cursor + 1 <= lim_", "subject[rx_span_cursor + 0]", "rx_span_cursor += 1",
            "it_", 0 },
          { "(unsigned)(subject[rx_span_cursor + 0] - 97) <= 25u", "rx_span_cursor", "        " } },
        /* a[a-z]*x --engine=vm: VMSPAN, no counter */
        { "adv-vmspan", 0, MF_SPAN_UNBOUNDED, NULL, "abcdefghijklmnopqrstuvwxyz",
          { "rx_span_cursor + 1 <= lim_", "subject[rx_span_cursor + 0]", "rx_span_cursor += 1",
            NULL, 0 },
          { "(unsigned)(subject[rx_span_cursor + 0] - 97) <= 25u", "rx_span_cursor", "        " } },
    };
    for (size_t i = 0; i < sizeof tgt / sizeof tgt[0]; i++) {
        s = adv_site(tgt[i].caller, tgt[i].span);
        mf_term *t = &s.pred.term[0];
        if (tgt[i].set_not) {                           /* [^c]: every byte but c */
            t_set(t, 0, tgt[i].set_not, 0);
            for (size_t k = 0; k < sizeof t->set; k++) t->set[k] = (uint8_t)~t->set[k];
        } else {
            t_set(t, 0, tgt[i].set, 0);
        }
        t->need = MF_REQUIRED;
        bad |= render_adv_x(dir, tgt[i].name, &s, tgt[i].h, &tgt[i].x);
    }

    /* M6 prep (R-10, MF_SITE_ABI 8): the strided ADVANCE shapes */
    for (size_t i = 0; i < sizeof STRIDES / sizeof STRIDES[0]; i++)
        bad |= render_stride(dir, &STRIDES[i]);

    if (only && only_seen != 1) {
        fprintf(stderr, "arm_fixtures: --only %s matched %d fixtures\n", only, only_seen);
        return 2;
    }
    return bad;
}
