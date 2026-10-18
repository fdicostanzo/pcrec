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

/* MF_SITE_ABI 11 (R17-a, setfind.md §2.2): a FORWARD FIND STATES its window,
 * and today's window IS its candidate: window_stated 1, move_back the least
 * term offset (d_min), overshoot 0, as pcrec's builders state it. Applied at
 * the kit call, so every fixture keeps its description; a site with no
 * terms, or that states a window itself, is passed unchanged. The window
 * cases (seq_case) call the kit on the site as written. */
static mf_site fx_win(const mf_site *s)
{
    mf_site w = *s;
    if (w.op == MF_OP_FIND && !w.reverse && !w.pred.window_stated && w.pred.nterm) {
        int32_t d = w.pred.term[0].offset;
        for (unsigned i = 1; i < w.pred.nterm && i < MF_MAX_TERM; i++)
            if (w.pred.term[i].offset < d) d = w.pred.term[i].offset;
        w.pred.window_stated = 1;
        w.pred.move_back = d;
        w.pred.overshoot = 0;
    }
    return w;
}
#define FXW(s) (&(struct { mf_site v; }){ fx_win(s) }.v)

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
    t->need = MF_REQUIRED;      /* MF_SITE_ABI 13: a need is stated, 0 refused */
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
    t->need = MF_REQUIRED;      /* MF_SITE_ABI 13: a need is stated, 0 refused */
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
    s.pred.need = MF_REQUIRED;  /* MF_SITE_ABI 13: stated (0 is refused where read) */
    s.body = MF_BODY_ONESHOT;   /* MF_SITE_ABI 14: stated (0 is refused where read) */
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
    s.pred.term[0].need = MF_REQUIRED;
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
    p->need = MF_REQUIRED;
    t_byte(&p->term[0], 0, b);
}

static void p_run(mf_pred *p, const char *run, const uint8_t *mask, int pos,
                  uint32_t fn_ref)
{
    memset(p, 0, sizeof *p);
    p->nterm = 1;
    p->need = MF_REQUIRED;
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

/* ---- R17-b' B1 THE QUERY FAMILY (--query; r17b_prime.md §4.5 rule 2, §8.2)
 *
 * With --query every fixture is ASKED (mf_ask, the define hooks) before it
 * is defined, and the class is held three ways: to the define's own class
 * (mf_defined), to an INDEPENDENT reading of the site and of the rendered
 * text (proven0: the intersection of the offset-0 terms, computed here from
 * the description; libc_free: the rendered text calls no `memchr(`/
 * `memcmp(`; exists: a FIND renders text), and to the art: the same fixture
 * rendered with and without the preceding ask gives the same bytes (the
 * query is pure). One `QUERY<TAB>fixture<TAB>verdict` line per fixture on
 * stderr; run_finder.sh reads them. A class that cannot be asked prints its
 * own verdict. */
static int query_mode;

/* proven0 as this file reads the site: the offset-0 terms' intersection on a
 * FIND, all ones elsewhere (never through the kit). */
static void q_proven0(const mf_site *s, uint8_t out[32])
{
    memset(out, 0xFF, 32);
    if (s->op != MF_OP_FIND) return;
    for (unsigned t = 0; t < s->pred.nterm; t++) {
        const mf_term *tm = &s->pred.term[t];
        uint8_t b[32] = { 0 };
        if (tm->offset != 0) continue;
        if (tm->kind == MF_T_SET) memcpy(b, tm->set, 32);
        else if (tm->kind == MF_T_RUN) {
            for (unsigned x = 0; x < 256; x++)
                if ((x & (tm->mask ? tm->mask[0] : 0xFFu)) == tm->run[0])
                    b[x >> 3] |= (uint8_t)(1u << (x & 7));
        } else continue;
        for (int i = 0; i < 32; i++) out[i] &= b[i];
    }
}

/* `full`: the fixture was DEFINED (mf_define), so the query's class equals
 * the define's in every field. 0: it was rendered in one call (mf_emit),
 * which selects over its use hooks as well, while the query answers the
 * define phase (memfn.h mf_ask): the two may part on `libc_free` and
 * `includes` (fdb1_report.md F-B1-4: pf-emit-result-decl, the r4gfix
 * fixture whose stated result_decl declines the PF row at the use), never on
 * what every FIND row proves, `exists` and `proven0`, which is what B2's
 * readers read. */
static void q_check(const char *name, const mf_site *s, int ask_rc, const mf_class *qa,
                    const mf_art *art, uint32_t handle, const char *text, int full)
{
    mf_result dr;
    uint8_t p0[32];
    const char *why = NULL;
    if (ask_rc) why = "ASK-REFUSED";
    else if (mf_defined(art, handle, &dr)) why = "DEFINED-REFUSED";
    else if (full ? memcmp(qa, &dr.cls, sizeof *qa) != 0
                  : qa->exists != dr.cls.exists || memcmp(qa->proven0, dr.cls.proven0, 32))
        why = "ASK!=DEFINE";
    else {
        q_proven0(s, p0);
        int calls = text && (strstr(text, "memchr(") || strstr(text, "memcmp("));
        if (qa->v != MF_CLASS_V) why = "VERSION";
        else if (memcmp(qa->proven0, p0, 32)) why = "PROVEN0";
        else if (!qa->exists) why = "EXISTS";
        else if (qa->libc_free && calls) why = "LIBC_FREE";
        else if (qa->npres) why = "NPRES";
    }
    fprintf(stderr, "QUERY\t%s\t%s\n", name, why ? why : "agree");
}

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
    mf_art *art = mf_art_begin(&a, "rx", MF_P_PORTABLE_ONLY, s->denies, NULL, NULL);
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
    mf_class qa;
    int qrc = query_mode ? mf_ask(art, FXW(s), &hd, &qa) : 0;
    int rc = mf_define(art, FXW(s), &hd, &sd, &h) ||
             (s->form == MF_FORM_FUNC ? mf_call(art, h, &hu, &su)
                                      : mf_use(art, h, &hu, &su, &res)) ||
             mf_flush_helpers(art, &sd) ||
             mf_art_end(art, NULL);
    if (rc) {
        fprintf(stderr, "%s: the kit refused: %s\n", name, mf_art_error(art));
        return 1;
    }
    if (query_mode) {
        Text all = { 0 };
        if (def.p) text_put(&all, def.p, def.len);
        if (use.p) text_put(&all, use.p, use.len);
        q_check(name, s, qrc, &qa, art, h, all.p, 1);
        free(all.p);
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
    mf_art *art = mf_art_begin(&a, "rx", MF_P_PORTABLE_ONLY, s->denies, NULL, NULL);
    Text def = { 0 }, use = { 0 };
    mf_sink sd = sink_of(&def), su = sink_of(&use);
    mf_hooks h = *hp;
    mf_result res = { 0 };
    mf_class qa;
    int qrc = query_mode ? mf_ask(art, FXW(s), &h, &qa) : 0;
    if (mf_emit(art, FXW(s), &h, &su, &sd, &res) || mf_art_end(art, NULL)) {
        fprintf(stderr, "%s: the kit refused: %s\n", name, mf_art_error(art));
        return 1;
    }
    if (query_mode) {
        /* mf_emit selects over its use hooks too; the query answers the
           define phase: the two agree on every fixture or the line says so */
        Text all = { 0 };
        if (def.p) text_put(&all, def.p, def.len);
        if (use.p) text_put(&all, use.p, use.len);
        q_check(name, s, qrc, &qa, art, res.handle, all.p, 0);
        free(all.p);
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
    mf_art *art = mf_art_begin(&a, "rx", MF_P_PORTABLE_ONLY, s->denies, NULL, NULL);
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
    if (mf_emit(art, FXW(s), &h, &su, &sd, &res) || mf_art_end(art, NULL)) {
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
    mf_art *art = mf_art_begin(&a, "rx", MF_P_PORTABLE_ONLY, s.denies, NULL, NULL);
    Text def = { 0 }, use = { 0 };
    mf_sink sd = sink_of(&def), sk = sink_of(&use);
    mf_hooks h = { .more = more, .peek = "subject[rx_span_cursor + 0]", .step = step,
                   .count = x->caller ? "it_" : NULL, .count_start = 0,
                   .cursor = "rx_span_cursor", .s = "subject",
                   .member = x->own ? NULL : h_stride_member,
                   .indent = "        ", .u = &su };
    mf_result res = { 0 };
    if (mf_emit(art, FXW(&s), &h, &sk, &sd, &res) || mf_art_end(art, NULL)) {
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
    mf_art *art = mf_art_begin(&a, "rx", MF_P_PORTABLE_ONLY, s->denies, NULL, NULL);
    Text def = { 0 }, use = { 0 };
    mf_sink sd = sink_of(&def), su = sink_of(&use);
    mf_result res = { 0 };
    uint32_t h = 0;
    int rc = mf_define(art, FXW(s), hd, &sd, &h) || mf_use(art, h, hu, &su, &res);
    if (rc) printf("%s\tREFUSE\t%s\n", name, mf_art_error(art) ? mf_art_error(art) : "");
    else    printf("%s\tRENDER\t%s\n", name, res.form_id);
    free(def.p);
    free(use.p);
}

/* R17-a (MF_SITE_ABI 11): one case of the storage point's protocol and the
 * window fields' rules, the site as WRITTEN (no fx_win). `ops` is the call
 * sequence after mf_define with `hd`: `L` mf_locals with `hl`, `U` mf_use
 * with `hu`, `E` mf_art_end. Prints the outcome line as gate_case does: the
 * first refusal, or RENDER and the form id once every call passed. */
static void seq_case(const char *name, const mf_site *s, const mf_hooks *hd,
                     const mf_hooks *hl, const mf_hooks *hu, const char *ops)
{
    if (skip_fixture(name)) return;
    mf_arena a = { NULL, a_alloc };
    mf_art *art = mf_art_begin(&a, "rx", MF_P_PORTABLE_ONLY, s->denies, NULL, NULL);
    Text def = { 0 }, use = { 0 };
    mf_sink sd = sink_of(&def), su = sink_of(&use);
    mf_result res = { 0 };
    uint32_t h = 0;
    int rc = mf_define(art, s, hd, &sd, &h);
    for (const char *o = ops; !rc && *o; o++)
        rc = *o == 'L' ? mf_locals(art, h, hl, &su)
           : *o == 'U' ? mf_use(art, h, hu, &su, &res)
           : mf_art_end(art, NULL);
    if (rc) printf("%s\tREFUSE\t%s\n", name, mf_art_error(art) ? mf_art_error(art) : "");
    else    printf("%s\tRENDER\t%s\n", name, res.form_id);
    free(def.p);
    free(use.p);
}

/* The R17-a cases: the PF walk site as pcrec's set rows define it (a table
 * FIND offering its declaration point, W4, with a stem, W5), through the
 * protocol define -> locals -> use(s) -> end, then each refusal; and the
 * window rules over FIND, SKIP and reverse sites. */
static void seq_cases(void)
{
    mf_site w = pf_site(0, 1);
    t_set(&w.pred.term[0], 0, "xyz", 1);
    w.pred.term[0].need = MF_REQUIRED;
    w.pred.window_stated = 1;
    w.decl_point = 1;
    w.pred.fn_ref = 1;
    Fx f = { &w, "rx_search_pf", "    " };
    mf_hooks h = { .s = "subject", .n = "subject_length", .lo = "scan_position",
                   .result = "scan_position", .miss = MF_MISS_N,
                   .table_name = h_table_name, .fn_name = h_fn_name,
                   .indent = "    ", .u = &f };
    mf_hooks hn = h, hs = h;
    hn.n = "len";
    hs.s = "subj";
    seq_case("locals-protocol", &w, &h, &h, &h, "LUUE");
    seq_case("locals-n-differs", &w, &h, &hn, &h, "LUE");             /* S846 */
    seq_case("locals-s-differs", &w, &h, &hs, &h, "LUE");
    seq_case("locals-twice", &w, &h, &h, &h, "LLUE");                 /* S847 */
    seq_case("locals-unread", &w, &h, &h, &h, "LE");                  /* S848 */
    seq_case("locals-never-placed", &w, &h, &h, &h, "E");
    seq_case("locals-use-first", &w, &h, &h, &h, "ULE");
    mf_site nd = w;
    nd.decl_point = 0;
    seq_case("locals-no-point", &nd, &h, &h, &h, "LUE");
    seq_case("locals-none-offered", &nd, &h, &h, &h, "UE");
    mf_site d2 = w;
    d2.decl_point = 2;
    seq_case("decl-point-2", &d2, &h, &h, &h, "LUE");
    mf_site w0 = nd;
    w0.pred.window_stated = 0;
    seq_case("window-unstated", &w0, &h, &h, &h, "UE");               /* S849 */
    mf_site wb = nd;
    wb.pred.move_back = -1;
    seq_case("window-back-negative", &wb, &h, &h, &h, "UE");
    mf_site wp = nd;
    wp.pred.move_back = 1;
    seq_case("window-back-positive", &wp, &h, &h, &h, "UE");
    mf_site wu = nd;
    wu.pred.move_back = MF_MOVE_UNBOUNDED;
    seq_case("window-back-unbounded", &wu, &h, &h, &h, "UE");
    mf_site wo = nd;
    wo.pred.overshoot = 1;
    seq_case("window-overshoot", &wo, &h, &h, &h, "UE");
    mf_site w2 = nd;
    w2.pred.window_stated = 2;
    seq_case("window-stated-2", &w2, &h, &h, &h, "UE");
    mf_site wr = nd;
    wr.reverse = 1;
    seq_case("window-reverse", &wr, &h, &h, &h, "UE");
    mf_site ws = adv_site(0, MF_SPAN_UNBOUNDED);
    ws.pred.window_stated = 1;
    mf_hooks vh = adv_hooks((AdvH){ "pos < n", "subject[pos]", "pos++;", NULL, 0 }, &f);
    seq_case("window-on-skip", &ws, &vh, &vh, &vh, "UE");
    mf_site wz = adv_site(0, MF_SPAN_UNBOUNDED);
    wz.pred.move_back = 3;
    seq_case("window-unstated-move-back", &wz, &vh, &vh, &vh, "UE");
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
    /* precheck_assign_byte (R-15): the kept byte's row shares the ASSIGN
       row's declarations: a miss stated as n renders it, another miss, a
       stated floor or a non-identifier s at define leave the site to
       generic, an unstated miss is refused */
    mf_pred lb[1];
    p_byte(&lb[0], 46);
    mf_site pl = pre_site(lb, 1, 0);
    Fx ld = { &pl, "rx_reqrun", NULL }, lu = { &pl, "rx_reqrun", "    " };
    gate_hooks(&ld, &lu, &hd, &hu, NULL, NULL, NULL, MF_MISS_N, NULL, "subject");
    gate_case("pre-landmark-miss-token", &pl, &hd, &hu);
    gate_hooks(&ld, &lu, &hd, &hu, NULL, NULL, NULL, NULL, NULL, "subject");
    gate_case("pre-landmark-miss-unstated", &pl, &hd, &hu);
    gate_hooks(&ld, &lu, &hd, &hu, "((size_t)-1)", NULL, NULL, "((size_t)-1)", NULL, "subject");
    gate_case("pre-landmark-miss-other", &pl, &hd, &hu);
    gate_hooks(&ld, &lu, &hd, &hu, NULL, "search_floor", NULL, MF_MISS_N, "search_floor", "subject");
    gate_case("pre-landmark-define-floor", &pl, &hd, &hu);
    gate_hooks(&ld, &lu, &hd, &hu, NULL, NULL, NONID, MF_MISS_N, NULL, NONID);
    gate_case("pre-landmark-define-nonident", &pl, &hd, &hu);

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

/* ---- R17-b' B1: the finder table's fixtures and the kit's B1 entries -----
 *
 * (r17b_prime.md rev 3 §1, §4.5, §4.7; lane fdb1.) No finder row is ROUTED at
 * B1, so a finder decision renders nothing: it is the MF_TRACE build's
 * SHADOW (memfn/src/finder.c `fd_shadow`), whose `MFTRACE FD` records are
 * what these fixtures produce. They render only when named:
 *
 *   arm_fixtures OUTDIR --only fd-<name>   one shadow witness (rows.tsv's
 *       table `fd`): a site rendered under a fixture set; its .def/.use are
 *       the pre-table form's text, its FD records the shadow's decision
 *   arm_fixtures --fd-site SITE [--fd-set FILE] [--opts STR] [--fd-an FID]
 *       one site under a set FILE and a `--memfn=` string, and (R-24) with an
 *       analysis object whose kinds all state `mf_prov.fidelity` FID
 *       (measure_sets §1.2's section TSV, its `rows` section read here, with
 *       no pcrec code), printing `CONSULTED<TAB>0|1` (R-MS2): the R-MS1/R-MS4
 *       loops of tests/memfn/finder_check.py
 *   arm_fixtures --finder-rows     mf_finder_rows as TSV (R-MS4's listing)
 *   arm_fixtures --hash            R-MS3's fixtures (mf_form_hash)
 *   arm_fixtures --pay-grid        the pay rule over stdin's operand lines
 *
 * Every expectation is finder_check.py's, never this file's. */

/* A fixture's own sets, written here (they share no source with the kit). */
static const mf_measure FDS_R0_ROWS[] = {
    { "kit.saving.V1.WALK.r2", 0, "ratio", "fixture" },
    { "kit.saving.V1.WALK.r2e0c0", 0, "ratio", "fixture" },
    { "kit.eps.streamed.slope", 10000, "ratio", "fixture" },
};
static const mf_measure FDS_R7_ROWS[] = {
    { "kit.saving.V1.WALK.r1e0c0", 500000, "ratio", "fixture" },
    { "kit.saving.V1.WALK.r2e0c0", 500000, "ratio", "fixture" },
    { "kit.saving.V1.WALK.r2", 500000, "ratio", "fixture" },
    { "kit.eps.streamed.slope", 10000, "ratio", "fixture" },
};
static const mf_measures FDS_R0 = { "fixture-r0", 1, "0000000000000000", "-", "synthetic", 0,
                                    3, FDS_R0_ROWS };
static const mf_measures FDS_R7 = { "fixture-r7", 1, "0000000000000000", "-", "synthetic", 0,
                                    4, FDS_R7_ROWS };

/* The finder fixtures' sites: the PF shape pcrec's find_site states (one
 * term, the window the candidate, `body` ONESHOT, a storage point on a
 * table site), the pre-check composite, and a RUN landmark. */
static mf_site fd_pf_site(const char *members, int table, int body)
{
    mf_site s = pf_site(0, table);
    if (table) {
        t_set(&s.pred.term[0], 0, members, 1);
        s.pred.term[0].need = MF_REQUIRED;
        s.decl_point = 1;
        s.pred.fn_ref = 1;
    } else {
        t_byte(&s.pred.term[0], 0, (unsigned char)members[0]);
    }
    s.pred.need = MF_REQUIRED;
    s.body = (uint8_t)body;
    return s;
}

/* One site's define, storage point (where it offers one) and use, in an art
 * begun with `ms`; `CONSULTED` from its end. */
static int fd_render(const char *dir, const char *name, const mf_site *s,
                     const mf_measures *ms, const mf_analysis *an)
{
    mf_arena a = { NULL, a_alloc };
    mf_art *art = mf_art_begin(&a, "rx", s->policy, s->denies, ms, an);
    Text def = { 0 }, use = { 0 };
    mf_sink sd = sink_of(&def), su = sink_of(&use);
    Fx fx = { s, "rx_pf", "    " };
    int table = s->op == MF_OP_FIND && s->pred.term[0].kind == MF_T_SET &&
                s->pred.term[0].table_ref;
    int pre = s->op == MF_OP_ALL_PRESENT;
    /* B2's PF shape (MF_SITE_ABI 13): an unbounded site whose empty range
       runs the miss states the leaving on_miss; a bounded one its `n - 1`
       miss and, on the DFA hat, its moved statement; MLINE's context stop
       (a term below the candidate) its floor and `break;` */
    int back = s->op == MF_OP_FIND && s->pred.term[0].offset < 0;
    int miss_runs = pre || (!table && !s->end_back) ||
                    (s->empty == MF_EMPTY_MISS && !s->end_back);
    mf_hooks h = { .s = "subject", .n = "subject_length", .lo = pre ? "search_from" : "scan_position",
                   .result = pre ? "handoff_position" : "scan_position",
                   .miss = s->end_back ? "subject_length - 1" : MF_MISS_N,
                   .on_miss = back ? "break;" : miss_runs ? "return 0;" : NULL,
                   .floor = back ? "scan_position" : NULL,
                   .table_name = h_table_name, .fn_name = h_fn_name,
                   .note = pre ? h_note : NULL, .note_tag = pre ? h_note_tag : NULL,
                   .indent = "    ", .u = &fx, .start = "search_from",
                   .moved = s->site_kind == MF_SK_DFA_HAT ? "state = 1;" : NULL };
    uint8_t consulted = 9;
    uint32_t hd = 0;
    mf_result res;
    memset(&res, 0, sizeof res);
    int rc = mf_define(art, FXW(s), &h, &sd, &hd) ||
             (s->decl_point && mf_locals(art, hd, &h, &su)) ||
             mf_use(art, hd, &h, &su, &res) ||
             mf_flush_helpers(art, &sd) ||
             mf_art_end(art, &consulted);
    if (rc) {
        fprintf(stderr, "%s: the kit refused: %s\n", name, mf_art_error(art));
        printf("REFUSED\t%s\n", mf_art_error(art) ? mf_art_error(art) : "-");
        return 1;
    }
    if (dir) {
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
    }
    printf("CONSULTED\t%u\n", (unsigned)consulted);
    printf("ROUTED\t%s\n", res.row[0] ? res.row : "-");
    printf("TEXT\t");
    for (const char *c = use.p ? use.p : ""; *c; c++) putchar(*c == '\n' ? '|' : *c);
    printf("\n");
    free(def.p);
    free(use.p);
    return 0;
}

/* R17-b' B3b: a presence site with no part yet (every span P2 drops is
 * never defined) is ASKED: its links, `LINK<TAB>i<TAB>v p m o`, one per span
 * (the traced kit records them too, `MFTRACE FD ... phase=ask`). */
static int fd_ask_links(const char *name, const mf_site *s)
{
    mf_arena a = { NULL, a_alloc };
    mf_art *art = mf_art_begin(&a, "rx", s->policy, s->denies, NULL, NULL);
    mf_hooks h = { .start = "search_from" };
    mf_class c;
    if (mf_ask(art, FXW(s), &h, &c)) {
        fprintf(stderr, "%s: the kit refused the ask\n", name);
        printf("REFUSED\t-\n");
        return 1;
    }
    for (unsigned i = 0; i < c.npres; i++)
        printf("LINK\t%u\tv%dp%dm%do%d\n", i, c.pres[i].verify, c.pres[i].proven_by,
               c.pres[i].member, c.pres[i].order);
    return 0;
}

/* The named site (fd fixtures and --fd-site). */
static int fd_site_of(const char *name, mf_site *s, mf_pred *p)
{
    if (!strcmp(name, "set10"))            *s = fd_pf_site("0123456789", 1, MF_BODY_ONESHOT);
    else if (!strcmp(name, "set10-nobody")) *s = fd_pf_site("0123456789", 1, MF_BODY_UNSTATED);
    else if (!strcmp(name, "set10-param"))  *s = fd_pf_site("0123456789", 1, MF_BODY_PARAM);
    else if (!strcmp(name, "set10-bodyoor")) *s = fd_pf_site("0123456789", 1, 9);
    else if (!strcmp(name, "set2r"))        *s = fd_pf_site("0123456789abcdefghijklmnopqrstuvwxyz", 1, MF_BODY_ONESHOT);
    else if (!strcmp(name, "byte1"))        *s = fd_pf_site("x", 0, MF_BODY_ONESHOT);
    /* R17-b' B2: the one-byte sites as pcrec states them since MF_SITE_ABI 13
       (the set at every count with its table OFFERED, the consumer kind, the
       miss and moved behaviour as facts): rows D1, D1w, D1c route them */
    else if (!strcmp(name, "byte1t") || !strcmp(name, "byte1vm") ||
             !strcmp(name, "hat1")) {
        int hat = !strcmp(name, "hat1");
        *s = fd_pf_site("x", 1, MF_BODY_ONESHOT);
        s->empty = hat ? MF_EMPTY_NOP : MF_EMPTY_MISS;
        s->end_back = (uint8_t)hat;
        s->on_miss_leaves = !hat;
        s->site_kind = !strcmp(name, "byte1vm") ? MF_SK_VM_ATTEMPT
                     : hat ? MF_SK_DFA_HAT : MF_SK_DFA_SCAN;
    } else if (!strcmp(name, "mline")) {
        *s = pf_site(0, 0);
        t_byte(&s->pred.term[0], -1, '\n');
        s->empty = MF_EMPTY_AT_N;
        s->on_miss_leaves = 1;
        s->body = MF_BODY_ONESHOT;
        s->site_kind = MF_SK_DFA_ATTEMPT;
    }
    else if (!strcmp(name, "run3")) {
        *s = pf_site(0, 0);
        t_run(&s->pred.term[0], 0, "abc", NULL);
        s->pred.term[0].need = MF_REQUIRED;
        s->pred.need = MF_REQUIRED;
        s->empty = MF_EMPTY_MISS;
        s->on_miss_leaves = 1;
        s->body = MF_BODY_ONESHOT;
    } else if (!strncmp(name, "pre-", 4)) {
        /* R17-b' B3b: the presence sites as pcrec states them since
           MF_SITE_ABI 17 (B3a's spans, the start search's proof), each with
           the parts its routed PRES links lay out (compose.c
           pres_layout_check): `pre-req` one REQUIRED member (P0: verified,
           at the head); `pre-opt` one OPTIONAL member (P3: the pick,
           verified); `pre-lead` an OPTIONAL member `q` and a caseless run
           "ABC" whose every position is a two-member cube, so under no rate
           the member is strictly rarer and LEADS (P4, then P3's window);
           `pre-dom` the OPTIONAL member the start search proves (identity:
           P2 drops every span, so it has no part and is only ASKED) */
        static mf_pred sp[2];
        static const uint8_t cube[3] = { 0xDF, 0xDF, 0xDF };
        int noproof = !strcmp(name, "pre-noproof");   /* pre-opt, its proof UNSTATED */
        int omin = !strcmp(name, "pre-omin");          /* pre-opt, omin below the start */
        if (noproof || omin) name = "pre-opt";
        int req = !strcmp(name, "pre-req");
        int norun_part = !strcmp(name, "pre-lead-run");   /* P4 denied: no lead part */
        int lead = !strcmp(name, "pre-lead") || norun_part;
        mf_need need = req ? MF_REQUIRED : MF_OPTIONAL;
        if (strcmp(name, "pre-req") && strcmp(name, "pre-opt") && !lead &&
            strcmp(name, "pre-dom"))
            return -1;
        memset(sp, 0, sizeof sp);
        t_byte(&sp[0].term[0], 0, 'q');
        sp[0].term[0].need = need;
        sp[0].member_order = 1;
        if (lead) {
            t_run(&sp[1].term[0], 0, "ABC", cube);
            sp[1].term[0].need = need;
        }
        for (int i = 0; i < 1 + lead; i++) {
            sp[i].nterm = 1;
            sp[i].need = need;
            sp[i].plan_hint = MF_NO_PRED;
            sp[i].span_class = MF_SPAN_PRESENCE;
        }
        if (omin) sp[0].omin = -1;
        int nparts = 0;
        if (!strcmp(name, "pre-dom")) {
            *s = pre_site(p, 0, -1);
            s->preds = NULL;
        } else {
            if (!norun_part) {
                p_byte(&p[nparts], 'q');
                p[nparts].need = lead ? MF_OPTIONAL : MF_REQUIRED;
                p[nparts++].term[0].need = lead ? MF_OPTIONAL : MF_REQUIRED;
            }
            if (lead) {
                p_run(&p[nparts], "ABC", cube, 2, 1);
                p[nparts++].plan_hint = 0;
            }
            *s = pre_site(p, nparts, -1);
        }
        s->body = MF_BODY_ONESHOT;
        s->site_kind = req ? MF_SK_VM_ATTEMPT : MF_SK_DFA_SCAN;
        s->pspans = sp;
        s->npspan = (uint16_t)(1 + lead);
        s->pres_proof = (mf_pres_proof){ .byte = -1, .stated = 1 };
        if (noproof) s->pres_proof = (mf_pres_proof){ 0 };
        if (!strcmp(name, "pre-dom"))
            s->pres_proof = (mf_pres_proof){ .byte = 'q', .stop = 1, .stated = 1 };
    } else {
        return -1;
    }
    return 0;
}

/* --only fd-<row>: the shadow witnesses and their controls. */
static int fd_fixture(const char *dir, const char *name)
{
    static const struct { const char *name, *site; const mf_measures *ms; const char *opts; } fx[] = {
        { "fd-R0",      "set2r",  &FDS_R0, NULL },    /* r2 cover, saving inside eps: R0 */
        { "fd-R7-r2",   "set2r",  &FDS_R7, NULL },    /* the same cover, saving > eps: R7 */
        { "fd-R7",      "set10",  &FDS_R7, NULL },    /* r1 cover, saving > eps: R7     */
        { "fd-R7w",     "set10",  NULL, NULL },       /* no set: R7w                    */
        { "fd-D2",      "run3",   NULL, NULL },       /* a RUN landmark: D2 (routed: the walk) */
        { "fd-P0",      "pre-req", NULL, NULL },      /* a REQUIRED presence span: P0   */
        { "fd-P3",      "pre-opt", NULL, NULL },      /* an OPTIONAL one: P3, the pick  */
        { "fd-P9",      "pre-opt", NULL, "no-fd-pres-pick" }, /* the pick denied: P9 */
        { "fd-P4",      "pre-lead", NULL, NULL },     /* a member rarer than the run: P4 */
        { "fd-P4-den",  "pre-lead-run", NULL, "no-pres-set-lead" }, /* P4 denied: the run alone */
        { "fd-P2",      "pre-dom", NULL, NULL },      /* the proof stands: P2 (asked) */
        { "fd-P2-den",  "pre-dom", NULL, "no-fd-pres-g1" }, /* P2 denied: P3 (asked) */
        { "fd-nobody",  "set10-nobody", &FDS_R7, NULL }, /* body UNSTATED: refused (R-23, S1089's witness) */
    };
    for (size_t i = 0; i < sizeof fx / sizeof fx[0]; i++) {
        if (strcmp(name, fx[i].name)) continue;
        mf_site s;
        mf_pred p[2];
        only_seen++;
        if (fd_site_of(fx[i].site, &s, p)) return 2;
        s.opts = fx[i].opts;
        if (s.op == MF_OP_ALL_PRESENT && s.npspan && !s.npred)
            return fd_ask_links(name, &s) ? 1 : 0;
        return fd_render(dir, name, &s, fx[i].ms, NULL) ? 1 : 0;
    }
    return 2;
}

/* A set FILE's `rows` section (key, unit, value_e6 by header name). */
static int fd_load_set(const char *path, mf_measures *ms)
{
    static mf_measure rows[2048];
    static char keys[2048][128];
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); return -1; }
    char line[4096];
    int sect = 0, ck = -1, cv = -1;
    memset(ms, 0, sizeof *ms);
    ms->id = path;
    ms->rows = rows;
    while (fgets(line, sizeof line, f)) {
        line[strcspn(line, "\r\n")] = 0;
        if (!strncmp(line, "#section ", 9)) { sect = !strcmp(line + 9, "rows"); continue; }
        if (line[0] == '#') {
            if (!sect) continue;
            int c = 0;
            for (char *t = strtok(line + 1, "\t"); t; t = strtok(NULL, "\t"), c++) {
                if (!strcmp(t, "key")) ck = c;
                if (!strcmp(t, "value_e6")) cv = c;
            }
            continue;
        }
        if (!sect || !line[0] || ck < 0 || cv < 0 || ms->nrows >= 2048) continue;
        char *cell[32];
        int n = 0;
        for (char *t = line; n < 32; n++) {
            cell[n] = t;
            char *e = strchr(t, '\t');
            if (!e) { n++; break; }
            *e = 0;
            t = e + 1;
        }
        if (ck >= n || cv >= n || !cell[cv][0]) continue;
        snprintf(keys[ms->nrows], sizeof keys[0], "%s", cell[ck]);
        rows[ms->nrows] = (mf_measure){ keys[ms->nrows], strtoll(cell[cv], NULL, 10), "-", "-" };
        ms->nrows++;
    }
    fclose(f);
    return 0;
}

/* R-24 (MF_SITE_ABI 15): an analysis object every one of whose kinds states
 * the provenance fidelity `fid` and a byte count, handed to mf_art_begin so a
 * kit that READ either field before B3a would show it (finder_check.py L:
 * the same site renders identically with and without it). `fid` is stated as
 * given, an out-of-enum value included: nothing reads it, so nothing refuses
 * it. Each kind is PRESENT, MEASURED, with the payload the invariant asks. */
static const uint32_t an_rates[256] = { 1000000 };
static mf_akind an_kinds[2];
static mf_analysis an_obj;

static const mf_analysis *fd_an_make(int fid)
{
    static const char *const tags[2] = { "byte-rate", "run-rarity" };
    for (int i = 0; i < 2; i++) {
        memset(&an_kinds[i], 0, sizeof an_kinds[i]);
        an_kinds[i].tag = tags[i];
        an_kinds[i].version = 1;
        an_kinds[i].present = MF_KIND_PRESENT;
        an_kinds[i].prov.source = MF_PROV_MEASURED;
        an_kinds[i].prov.bundle = "weblog";
        an_kinds[i].prov.digest = 0x1234;
        an_kinds[i].prov.bytes = 999960;
        an_kinds[i].prov.fidelity = (uint8_t)fid;
        an_kinds[i].payload = an_rates;
    }
    an_obj.list_v = MF_ANALYSIS_LIST_V;
    an_obj.nkinds = 2;
    an_obj.kinds = an_kinds;
    return &an_obj;
}

static int fd_site_mode(const char *site, const char *setpath, const char *opts,
                        int fid)
{
    mf_site s;
    mf_pred p[2];
    mf_measures ms;
    if (fd_site_of(site, &s, p)) { fprintf(stderr, "no fd site %s\n", site); return 2; }
    s.opts = opts;
    if (setpath && fd_load_set(setpath, &ms)) return 2;
    if (s.op == MF_OP_ALL_PRESENT && s.npspan && !s.npred)
        return fd_ask_links(site, &s) ? 1 : 0;
    return fd_render(NULL, site, &s, setpath ? &ms : NULL,
                     fid >= 0 ? fd_an_make(fid) : NULL) ? 1 : 0;
}

static int finder_rows_mode(void)
{
    static mf_finder_listing l;
    mf_finder_rows(&l);
    size_t n = l.n;
    const mf_finder_row *r = l.rows;
    printf("#id\tslot\tneeds\tpick\tunpaid\tdeny\tbasis\trouted\tlocked\tstep\tkeys\n");
    for (size_t i = 0; i < n; i++) {
        printf("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%u\t%u\t%s\t", r[i].id, r[i].slot, r[i].needs,
               r[i].pick, r[i].unpaid, r[i].deny, r[i].basis, r[i].routed, r[i].locked,
               r[i].step);
        for (unsigned k = 0; k < r[i].nkeys; k++)
            printf("%s%s", k ? ";" : "", r[i].keys[k].key);
        printf("%s\n", r[i].nkeys ? "" : "-");
    }
    size_t no;
    const mf_option *o = mf_options(&no);
    for (size_t i = 0; i < no; i++) printf("OPTION\t%s\n", o[i].name);
    return 0;
}

/* R-MS3's fixtures: the forms that render resolve, others are refused; the
 * text hash ignores a rename, a comment and layout, and moves on a one-
 * operator edit. */
static int hash_mode(void)
{
    static const char *const ids[] = { "walk", "libc", "V1", "W64", "NONE", "dispatch-twin", NULL };
    for (unsigned i = 0; ids[i]; i++) {
        char h[17] = "-";
        int rc = mf_form_hash(ids[i], h);
        printf("FORM\t%s\t%d\t%s\n", ids[i], rc, rc ? "-" : h);
    }
    static const struct { const char *name, *text; } tx[] = {
        { "base",    "    while (pos < n && !mf_tbl[subject[pos]]) pos++;\n" },
        { "rename",  "    while (cursor < len && !my_table[s[cursor]]) cursor++;\n" },
        { "comment", "/* the walk */\n\n    while (pos < n && /* x */ !mf_tbl[subject[pos]]) pos++; // y\n" },
        { "layout",  "while (pos < n && !mf_tbl[subject[pos]]) pos++;\n\n\n" },
        { "edit",    "    while (pos < n && !mf_tbl[subject[pos]]) pos += 2;\n" },
        { "edit2",   "    while (pos <= n && !mf_tbl[subject[pos]]) pos++;\n" },
    };
    for (unsigned i = 0; i < sizeof tx / sizeof tx[0]; i++) {
        char h[17];
        mf_form_hash_text(tx[i].text, h);
        printf("TEXT\t%s\t%s\n", tx[i].name, h);
    }
    return 0;
}

/* The pay rule over stdin: one case per line, `npt s0 f0 ... has_call call
 * cfloor has_next nfloor has_use use ufloor has_wmin wfloor`; prints the
 * bits. */
static int pay_mode(void)
{
    char line[4096];
    while (fgets(line, sizeof line, stdin)) {
        mf_pay_operands in;
        memset(&in, 0, sizeof in);
        char *t = line, *e;
        long long v[64];
        int n = 0;
        while (n < 64) {
            v[n] = strtoll(t, &e, 10);
            if (e == t) break;
            n++;
            t = e;
        }
        if (n < 1) continue;
        in.npt = (unsigned)v[0];
        int k = 1;
        for (unsigned i = 0; i < in.npt && i < MF_PAY_MAXPT; i++) {
            in.saving_e6[i] = v[k++];
            in.saving_floor_e6[i] = v[k++];
        }
        in.has_call = (uint8_t)v[k++]; in.call_e6 = v[k++]; in.call_floor_e6 = v[k++];
        in.has_next = (uint8_t)v[k++]; in.next_floor_e6 = v[k++];
        in.has_use = (uint8_t)v[k++]; in.use_e6 = v[k++]; in.use_floor_e6 = v[k++];
        in.has_wmin = (uint8_t)v[k++]; in.wmin_floor_e6 = v[k++];
        printf("%u\n", mf_finder_pay(&in));
    }
    return 0;
}

int main(int argc, char **argv)
{
    if (argc < 2) { fputs("usage: arm_fixtures OUTDIR [--perturb] [--query] | --gate [--gate-only CASE] | "
                          "--fd-site SITE [--fd-set FILE] [--fd-an FID] | --finder-rows | --hash | --pay-grid\n", stderr); return 2; }
    if (!strcmp(argv[1], "--fd-site") && argc > 2) {
        const char *set = NULL, *opts = NULL;
        int fid = -1;
        for (int i = 3; i + 1 < argc; i += 2) {
            if (!strcmp(argv[i], "--fd-set")) set = argv[i + 1];
            else if (!strcmp(argv[i], "--opts")) opts = argv[i + 1];
            else if (!strcmp(argv[i], "--fd-an")) fid = atoi(argv[i + 1]);
        }
        return fd_site_mode(argv[2], set, opts, fid);
    }
    if (!strcmp(argv[1], "--finder-rows")) return finder_rows_mode();
    if (!strcmp(argv[1], "--hash")) return hash_mode();
    if (!strcmp(argv[1], "--pay-grid")) return pay_mode();
    for (int i = 2; i < argc; i++)
        if (!strcmp(argv[i], "--query")) query_mode = 1;
    if (!strcmp(argv[1], "--gate")) {
        if (argc > 3 && !strcmp(argv[2], "--gate-only")) only = argv[3];
        gate_cases();
        seq_cases();
        if (only && only_seen != 1) {
            fprintf(stderr, "arm_fixtures: --gate-only %s matched %d cases\n", only, only_seen);
            return 2;
        }
        return 0;
    }
    const char *dir = argv[1];
    int perturb = argc > 2 && !strcmp(argv[2], "--perturb");
    if (argc > 3 && !strcmp(argv[2], "--only")) only = argv[3];
    if (only && !strncmp(only, "fd-", 3)) {         /* the finder shadow's fixtures */
        int rc = fd_fixture(dir, only);
        if (rc == 2) fprintf(stderr, "arm_fixtures: --only %s matched no fixture\n", only);
        return rc;
    }
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

    /* precheck_assign_byte (R-15): the gate's one byte KEPT by the handoff
     * ([REQ-HANDOFF-L1]'s byte landmark), its deny (the generic row renders
     * the same site), and three near-misses the row must leave to generic: a
     * two-member set, an OPTIONAL predicate, a later part as ret_pred.
     * run_arm_pins.sh check 14 runs the first two's text on fixed subjects. */
    mf_pred lm[2];
    p_byte(&lm[0], 46);
    s = pre_site(lm, 1, 0);
    bad |= render(dir, "pre-landmark-byte", &s, "rx_reqrun");
    s.opts = "no-precheck-assign-byte";
    bad |= render(dir, "pre-landmark-byte-deny", &s, "rx_reqrun");
    p_byte(&lm[0], 46);
    t_set(&lm[0].term[0], 0, ".:", 0);
    lm[0].term[0].need = MF_REQUIRED;
    s = pre_site(lm, 1, 0);
    bad |= render(dir, "pre-landmark-two-members", &s, "rx_reqrun");
    p_byte(&lm[0], 46);
    lm[0].need = MF_OPTIONAL;
    s = pre_site(lm, 1, 0);
    bad |= render(dir, "pre-landmark-optional", &s, "rx_reqrun");
    p_run(&lm[0], "dog", NULL, 2, 1);
    p_byte(&lm[1], 46);
    s = pre_site(lm, 2, 1);
    bad |= render(dir, "pre-landmark-later", &s, "rx_reqrun");

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
