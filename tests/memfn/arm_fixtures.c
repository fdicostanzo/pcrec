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
#include <errno.h>
#include <stddef.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "memfn.h"
/* the form-hash entry table's TEST entries (span_cards.md §3.2, unit S2c):
   kit.h, the kit's internal header, as tests/memfn/proven_check.c reads it */
#include "../../memfn/src/kit.h"

/* MF_SITE_ABI 18 (R-26.1/R-26.2): a forward FIND's predicate STATES its class
 * (the renderer interface since MF_SITE_ABI 20, as the window family's
 * translation writes it): a context stop (every term below the candidate) is
 * CONTEXT; every other one is span 0, BOUNDED. Applied at the kit call, so
 * every fixture keeps its description; a site with no terms, or that states
 * a class itself, is passed unchanged. (The window facts W0-W2 and R-26's
 * prefix and context facts this once stated left the site at D172 S2
 * commit 6.) */
static void fx_span0(mf_site *w)
{
    if (w->op != MF_OP_FIND || w->reverse || !w->pred.nterm || w->pred.span_class) return;
    int below = 1;
    for (unsigned i = 0; i < w->pred.nterm && i < MF_MAX_TERM; i++) {
        const mf_term *t = &w->pred.term[i];
        if (t->offset + (t->kind == MF_T_RUN ? (int32_t)t->run_len : 1) > 0) below = 0;
    }
    w->pred.span_class = below ? MF_SPAN_CONTEXT : MF_SPAN_BOUNDED;
}

static mf_site fx_win(const mf_site *s)
{
    mf_site w = *s;
    fx_span0(&w);
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

/* An art begun as pcrec begins one (unit U3): no art-level policy word, the
 * CPU target stated at once; the fixtures render the portable target's text. */
static mf_art *art_begin(mf_arena *a, const char *pfx, uint64_t denies,
                         const mf_measures *ms, const mf_analysis *an)
{
    mf_art *art = mf_art_begin(a, pfx, denies, ms, an);
    return art && !mf_art_target(art, mf_portable_target()) ? art : NULL;
}

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

/* Adds byte `b` to the 256-bit set `set`. */
static void set_add(uint8_t set[32], unsigned b)
{
    set[b >> 3] |= (uint8_t)(1u << (b & 7));
}

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
        set_add(t->set, (unsigned char)*m);
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

/* THE RUN's presence span in SET FORM (R-38 K38-2, MF_SITE_ABI 27): one
 * window alternative with no entry fact, one span uncut at `start` 0, each
 * position its cube's byte set (`mask` NULL: exact), core all, verify NO,
 * the floor SUBJECT, no term. `a` and `w` are the caller's storage. */
static void ps_run(mf_pred *p, mf_walt *a, mf_wspan *w, const char *run, const uint8_t *mask)
{
    unsigned n = (unsigned)strlen(run);
    memset(p, 0, sizeof *p);
    memset(w, 0, sizeof *w);
    w->len = (uint8_t)n;
    w->verify = MF_VERIFY_NO;
    w->core = MF_CORE_STATED;
    w->core_len = (uint8_t)n;
    for (unsigned j = 0; j < n; j++)
        for (unsigned b = 0; b < 256; b++)
            if ((b & (mask ? mask[j] : 0xFFu)) == (unsigned char)run[j])
                w->set[j][b >> 3] |= (uint8_t)(1u << (b & 7));
    *a = (mf_walt){ MF_ENTRY_NONE, 1, w };
    p->nalt = 1;
    p->alts = a;
    p->wfloor = MF_WFLOOR_SUBJECT;
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
                    set_add(b, x);
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
        else if (qa->npres != s->npspan) why = "NPRES";   /* one link per presence span
                                                                  (R-38 Part D's pre-wide-* state them) */
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
    mf_art *art = art_begin(&a, "rx", s->denies, NULL, NULL);
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
    mf_art *art = art_begin(&a, "rx", s->denies, NULL, NULL);
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
    mf_art *art = art_begin(&a, "rx", s->denies, NULL, NULL);
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
                set_add(t->set, (unsigned)b);
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
    mf_art *art = art_begin(&a, "rx", s.denies, NULL, NULL);
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
    mf_art *art = art_begin(&a, "rx", s->denies, NULL, NULL);
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
    mf_art *art = art_begin(&a, "rx", s->denies, NULL, NULL);
    Text def = { 0 }, use = { 0 };
    mf_sink sd = sink_of(&def), su = sink_of(&use);
    mf_result res = { 0 };
    uint32_t h = 0;
    mf_site sc = *s;
    fx_span0(&sc);          /* the window cases state span 0 as pcrec does */
    int rc = mf_define(art, &sc, hd, &sd, &h);
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
 * protocol define -> locals -> use(s) -> end, then each refusal. (The window
 * rules W0-W2 left with their fields at D172 S2 commit 6.) */
static void seq_cases(void)
{
    mf_site w = pf_site(0, 1);
    t_set(&w.pred.term[0], 0, "xyz", 1);
    w.pred.term[0].need = MF_REQUIRED;
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
 * (r17b_prime.md rev 3 §1, §4.5, §4.7; lane fdb1; B4', lane b4p: every row
 * decides, the trace-only shadow is retired.) A FIND decision is the routed
 * `MFTRACE FDROUTE` record and a PRES decision the `MFTRACE FD ... slot=PRES`
 * record. Fixtures render only when named:
 *
 *   arm_fixtures OUTDIR --only fd-<name>   one witness (rows.tsv's table
 *       `fd`): a site rendered under a fixture set; its .def/.use are the
 *       decided row's text, its FDROUTE/FD records the decision
 *   arm_fixtures --fd-site SITE [--fd-set FILE] [--opts STR] [--fd-an DIGEST]
 *       one site under a set FILE and a `--memfn=` string, and (span_pick
 *       unit 1g) with an analysis object whose kinds all state the fixed
 *       rates below and `mf_akind.digest` DIGEST
 *       (measure_sets §1.2's section TSV, its `rows` section read here, with
 *       no pcrec code), printing `CONSULTED<TAB>0|1` (R-MS2): the R-MS1/R-MS4
 *       loops of tests/memfn/finder_check.py
 *   arm_fixtures --finder-rows     mf_finder_rows as TSV (R-MS4's listing)
 *   arm_fixtures --hash            R-MS3's fixtures (mf_form_hash): a `FORM`
 *       line per id (the fold of its instances), a `FORMCLS` line per
 *       instance of the entry table
 *       (`FORMCLS<TAB>id<TAB>cls<TAB>rc<TAB>hash<TAB>row<TAB>canon`), the
 *       `TEXT` variants, and per entry-table instance its fixtures
 *       (`TEXT<TAB><id>/<cls>.rename|.edit|.foldedit<TAB>hash`,
 *       `TEXT<TAB><id>/<cls>.renamed<TAB>count`)
 *   arm_fixtures --site-text ID [CLS]   the instance's SITE TEXT on stdout,
 *       exactly the text mf_form_hash folds (span_cards.md §3.2; the slot
 *       harness's cell text)
 *   arm_fixtures --site-parts ID [CLS]  the same text in two parts: the
 *       FILE part, a form-feed line, the BODY part (the slot's wrapper
 *       places them)
 *   arm_fixtures --hash-text FILE|-  mf_form_hash_text of a text (the slot's
 *       cell-text check folds a cell TU's site span with it)
 *   arm_fixtures --facts ID [CLS]  `key<TAB>value` lines the slot harness
 *       wraps and drives the site text with (the declared `facts[]` table)
 *
 * Every expectation is finder_check.py's, never this file's. */

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
    mf_art *art = art_begin(&a, "rx", s->denies, ms, an);
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
    mf_art *art = art_begin(&a, "rx", s->denies, NULL, NULL);
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
        static mf_walt sa;
        static mf_wspan sw;
        static const uint8_t cube[3] = { 0xDF, 0xDF, 0xDF };
        int decl = !strcmp(name, "pre-decl");          /* pre-lead's member, a WIDE run */
        if (decl) name = "pre-lead";
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
        if (lead) ps_run(&sp[1], &sa, &sw, "ABC", cube);   /* the run, LAST, nterm 0 */
        /* `pre-decl` (R-38 Part D, part_d.md §2.4 item 2): the run's every
           position the digits (WIDE, no findable position), so on the
           OPTIONAL route the decline row PD leaves it untested and the
           member `q` is the set's pick, verified at the HEAD; only ASKED */
        if (decl)
            for (unsigned j = 0; j < 3; j++) {
                memset(sw.set[j], 0, 32);
                for (unsigned b = '0'; b <= '9'; b++) sw.set[j][b >> 3] |= (uint8_t)(1u << (b & 7));
            }
        for (int i = 0; i < 1 + lead; i++) {
            sp[i].nterm = i == 0;
            sp[i].need = need;
            sp[i].plan_hint = MF_NO_PRED;
            sp[i].span_class = MF_SPAN_PRESENCE;
        }
        if (omin) sp[0].omin = -1;
        int nparts = 0;
        if (!strcmp(name, "pre-dom") || decl) {
            *s = pre_site(p, 0, -1);
            s->preds = NULL;
        } else {
            if (!norun_part) {
                p_byte(&p[nparts], 'q');
                p[nparts].need = lead ? MF_OPTIONAL : MF_REQUIRED;
                p[nparts++].term[0].need = lead ? MF_OPTIONAL : MF_REQUIRED;
            }
            if (lead) {     /* the run part: its name only, the kit derives it (K38-2) */
                memset(&p[nparts], 0, sizeof p[nparts]);
                p[nparts++].fn_ref = 1;
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

/* --only fd-<row>: the finder witnesses and their controls. */
static int fd_fixture(const char *dir, const char *name)
{
    /* (D172 S3: `fd-RPT`, the REPORT row's witness on an art previewing
       R-26.6, retired with RPT and the preview, window_site.md §4) */
    static const struct { const char *name, *site; const mf_measures *ms; const char *opts;
                        } fx[] = {
        { "fd-R7w",     "set10",  NULL, NULL },       /* a set FIND: R7w, the default   */
        { "fd-D2",      "run3",   NULL, NULL },       /* a RUN landmark: D2 (routed: the walk) */
        { "fd-P0",      "pre-req", NULL, NULL },      /* a REQUIRED presence span: P0   */
        { "fd-P3",      "pre-opt", NULL, NULL },      /* an OPTIONAL one: P3, the pick  */
        { "fd-P9",      "pre-opt", NULL, "no-fd-pres-pick" }, /* the pick denied: P9 */
        { "fd-P4",      "pre-lead", NULL, NULL },     /* a member rarer than the run: P4 */
        { "fd-P4-den",  "pre-lead-run", NULL, "no-pres-set-lead" }, /* P4 denied: the run alone */
        { "fd-P2",      "pre-dom", NULL, NULL },      /* the proof stands: P2 (asked) */
        { "fd-P2-den",  "pre-dom", NULL, "no-fd-pres-g1" }, /* P2 denied: P3 (asked) */
        { "fd-PD",      "pre-decl", NULL, NULL },     /* no findable run position: PD (asked) */
        { "fd-nobody",  "set10-nobody", NULL, NULL }, /* body UNSTATED: refused (R-23, S1089's witness) */
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
        rows[ms->nrows] = (mf_measure){ keys[ms->nrows], strtoll(cell[cv], NULL, 10), "-", "-",
                                        MF_NOISE_UNMEASURED, 0 };
        ms->nrows++;
    }
    fclose(f);
    return 0;
}

/* span_pick unit 1g (MF_SITE_ABI 22): an analysis object every one of whose
 * kinds states the same fixed rates and the digest `digest`, handed to
 * mf_art_begin so a kit row that READ the digest would show it (finder_check.py
 * L: the same site renders identically whatever the digest; span_pick R22,
 * the rates held fixed). Each kind is PRESENT with the payload. */
static const uint32_t an_rates[256] = { 1000000 };
static mf_akind an_kinds[2];
static mf_analysis an_obj;

/* The analysis object stating `rates` (256 ppm) and `digest` on both kinds. */
static const mf_analysis *an_make(unsigned long long digest, const uint32_t *rates)
{
    static const char *const tags[2] = { "byte-rate", "run-rarity" };
    for (int i = 0; i < 2; i++) {
        memset(&an_kinds[i], 0, sizeof an_kinds[i]);
        an_kinds[i].tag = tags[i];
        an_kinds[i].version = 1;
        an_kinds[i].present = MF_KIND_PRESENT;
        an_kinds[i].digest = digest;
        an_kinds[i].payload = rates;
    }
    an_obj.list_v = MF_ANALYSIS_LIST_V;
    an_obj.nkinds = 2;
    an_obj.kinds = an_kinds;
    return &an_obj;
}

static const mf_analysis *fd_an_make(unsigned long long digest)
{
    return an_make(digest, an_rates);
}

static int fd_site_mode(const char *site, const char *setpath, const char *opts,
                        const char *digest)
{
    mf_site s;
    mf_pred p[2];
    mf_measures ms;
    if (fd_site_of(site, &s, p)) { fprintf(stderr, "no fd site %s\n", site); return 2; }
    s.opts = opts;
    if (setpath && fd_load_set(setpath, &ms)) return 2;
    if (s.op == MF_OP_ALL_PRESENT && s.npspan && !s.npred)
        return fd_ask_links(site, &s) ? 1 : 0;
    const mf_analysis *an = NULL;
    if (digest) {
        char *end;
        errno = 0;
        unsigned long long d = strtoull(digest, &end, 0);
        if (!*digest || *end || errno) {
            fprintf(stderr, "--fd-an %s: not a digest (an unsigned integer, base 0)\n", digest);
            return 2;
        }
        an = fd_an_make(d);
    }
    return fd_render(NULL, site, &s, setpath ? &ms : NULL, an) ? 1 : 0;
}

static int finder_rows_mode(void)
{
    static mf_finder_listing l;
    mf_finder_rows(&l);
    size_t n = l.n;
    const mf_finder_row *r = l.rows;
    printf("#id\tslot\tneeds\tpick\tunpaid\tdeny\tbasis\tstep\tkeys\n");
    for (size_t i = 0; i < n; i++) {
        printf("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t", r[i].id, r[i].slot, r[i].needs,
               r[i].pick, r[i].unpaid, r[i].deny, r[i].basis,
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

/* plan_frame.md 3.0a §2.5.2: THE SUPPORT TABLE as the kit holds it (window.c
 * wf_support, kit.h wf_support_rows), one line per row: the search, then
 * yes/no for RESTART, MASK and SHIFT. rows_check.py §S holds it to
 * tests/memfn/stream_support.tsv, whose RULING rows are the owner's text. */
static int streams_mode(void)
{
    size_t n;
    const wf_support_row *r = wf_support_rows(&n);
    printf("#search\tRESTART\tMASK\tSHIFT\n");
    for (size_t i = 0; i < n; i++)
        printf("%s\t%s\t%s\t%s\n", r[i].search, r[i].streams & WF_ST_RESTART ? "yes" : "no",
               r[i].streams & WF_ST_MASK ? "yes" : "no", r[i].streams & WF_ST_SHIFT ? "yes" : "no");
    return 0;
}

/* R-MS3's fixtures: the forms that render resolve, others are refused; the
 * text hash ignores a rename, a comment and layout, and moves on a one-
 * operator edit. */
/* R-MS3's two fixtures per entry-table INSTANCE (span_cards.md §8.2, unit
 * S2c; review r9 CHECKS-6: every instance a cell times, not only the
 * canonical one), made from the instance's SITE TEXT: `rename` renames every
 * identifier the text spells (the hooks' names and the `mf` prefix's) and
 * must keep the hash, having renamed at least one (`renamed`, CHECKS-4);
 * `edit` makes ONE instruction edit (the first `from`, which must occur) and
 * must move the instance's hash, and `foldedit` is the id's fold (every
 * instance's site text in table order, a newline between two: G4) with this
 * one instance edited, which must move mf_form_hash(id). */
static const struct { const char *id, *cls, *from, *to; } hash_edits[] = {
    { "walk",      "-",  "pos++",      "pos += 2" },
    { "libc",      "-",  "120",        "121" },
    { "pair",      "-",  "mf_mf1_c++", "mf_mf1_c += 2" },
    { "settest",   "c1", "== 47",      "!= 47" },
    { "settest",   "c2", "== 120",     "!= 120" },
    { "settest",   "cn", "== 95",      "!= 95" },
    { "rc-words",  "w1", ") == ",      ") != " },
    { "rc-words",  "w2", " && ",       " || " },
    { "rc-words",  "w3", "pos + 10",   "pos + 9" },
    { "rc-memcmp", "l1", ", 4)",       ", 3)" },
    { "every-pos", "-",  "pos++",      "pos += 2" },
};
static const struct { const char *from, *to; } hash_renames[] = {
    { "subject", "buf" }, { "pos", "cursor" }, { "n", "len" },
};

/* `t` with every whole identifier `from` (or, for `mf`, every identifier
 * beginning `mf_`) spelled `to`; malloc'd; *nr counts the renamed. */
static char *rename_idents(const char *t, unsigned *nr)
{
    Text o = { 0 };
    text_put(&o, "", 0);
    for (const char *p = t; *p; ) {
        int st = (*p == '_' || (*p >= 'a' && *p <= 'z') || (*p >= 'A' && *p <= 'Z')) &&
                 (p == t || !(p[-1] == '_' || (p[-1] >= '0' && p[-1] <= '9') ||
                              (p[-1] >= 'a' && p[-1] <= 'z') || (p[-1] >= 'A' && p[-1] <= 'Z')));
        if (!st) { text_put(&o, p++, 1); continue; }
        const char *e = p;
        while (*e == '_' || (*e >= '0' && *e <= '9') || (*e >= 'a' && *e <= 'z') ||
               (*e >= 'A' && *e <= 'Z'))
            e++;
        size_t n = (size_t)(e - p);
        const char *to = NULL;
        for (unsigned i = 0; i < sizeof hash_renames / sizeof hash_renames[0]; i++)
            if (strlen(hash_renames[i].from) == n && !strncmp(p, hash_renames[i].from, n))
                to = hash_renames[i].to;
        if (to) { text_put(&o, to, strlen(to)); (*nr)++; }
        else if (n > 3 && !strncmp(p, "mf_", 3)) { text_put(&o, "zz_", 3); text_put(&o, p + 3, n - 3); (*nr)++; }
        else text_put(&o, p, n);
        p = e;
    }
    return o.p;
}

/* `t` with its first `from` spelled `to`, malloc'd; NULL when `from` does
 * not occur. */
static char *edit_once(const char *t, const char *from, const char *to)
{
    const char *at = strstr(t, from);
    if (!at) return NULL;
    Text o = { 0 };
    text_put(&o, t, (size_t)(at - t));
    text_put(&o, to, strlen(to));
    text_put(&o, at + strlen(from), strlen(at + strlen(from)));
    return o.p;
}

/* --hash: R-MS3's fixtures (the header block above lists the lines). */
static int hash_mode(void)
{
    static const char *const ids[] = { "walk", "libc", "pair", "settest", "rc-words", "rc-memcmp",
                                       "every-pos", "V1", "W64", "NONE", "dispatch-twin", NULL };
    for (unsigned i = 0; ids[i]; i++) {
        char h[17] = "-";
        int rc = mf_form_hash(ids[i], h);
        printf("FORM\t%s\t%d\t%s\n", ids[i], rc, rc ? "-" : h);
    }
    for (size_t i = 0; mf_form_entry_at(i); i++) {
        const mf_form_entry *e = mf_form_entry_at(i);
        char h[17] = "-";
        int rc = mf_form_hash_cls(e->id, e->cls, h);
        const char *row = mf_form_row(e->id, e->cls);
        printf("FORMCLS\t%s\t%s\t%d\t%s\t%s\t%d\n", e->id, e->cls, rc, rc ? "-" : h,
               row ? row : "-", e->canon);
    }
    for (unsigned i = 0; i < sizeof hash_edits / sizeof hash_edits[0]; i++) {
        char *t, h[17] = "-", g[17] = "-", f[17] = "-";
        unsigned nr = 0;
        if (mf_form_site_text(hash_edits[i].id, hash_edits[i].cls, &t) == 0) {
            char *r = rename_idents(t, &nr);
            mf_form_hash_text(r, h);
            free(r);
            char *ed = edit_once(t, hash_edits[i].from, hash_edits[i].to);
            if (ed) {
                mf_form_hash_text(ed, g);
                /* the id's fold, this instance's text edited (written here
                   from the design, never formhash.c's loop) */
                Text o = { 0 };
                int k = 0, bad = 0;
                for (size_t j = 0; mf_form_entry_at(j); j++) {
                    const mf_form_entry *e = mf_form_entry_at(j);
                    char *u;
                    if (strcmp(e->id, hash_edits[i].id)) continue;
                    if (k++) text_put(&o, "\n", 1);
                    if (!strcmp(e->cls, hash_edits[i].cls)) { text_put(&o, ed, strlen(ed)); continue; }
                    if (mf_form_site_text(e->id, e->cls, &u)) { bad = 1; continue; }
                    text_put(&o, u, strlen(u));
                    free(u);
                }
                if (!bad && o.p) mf_form_hash_text(o.p, f);
                free(o.p);
                free(ed);
            }
            free(t);
        }
        printf("TEXT\t%s/%s.rename\t%s\n", hash_edits[i].id, hash_edits[i].cls, h);
        printf("TEXT\t%s/%s.renamed\t%u\n", hash_edits[i].id, hash_edits[i].cls, nr);
        printf("TEXT\t%s/%s.edit\t%s\n", hash_edits[i].id, hash_edits[i].cls, g);
        printf("TEXT\t%s/%s.foldedit\t%s\n", hash_edits[i].id, hash_edits[i].cls, f);
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

/* ---- the slot harness's two reads of the entry table (span_cards.md §3.2,
 * unit S2c) ------------------------------------------------------------------ */

/* --site-text: exactly the hashed text, nothing added. */
static int site_text_mode(const char *id, const char *cls)
{
    char *t;
    if (mf_form_site_text(id, cls, &t)) {
        fprintf(stderr, "arm_fixtures: no rendered instance %s %s\n", id, cls ? cls : "(canonical)");
        return 1;
    }
    fputs(t, stdout);
    free(t);
    return 0;
}

/* --site-parts: the site text's FILE part, a form-feed line, its BODY part
 * (the slot harness's wrapper places them; their concatenation is
 * --site-text's). */
static int site_parts_mode(const char *id, const char *cls)
{
    char *t;
    size_t fl;
    if (mf_form_site_split(id, cls, &t, &fl)) {
        fprintf(stderr, "arm_fixtures: no rendered instance %s %s\n", id, cls ? cls : "(canonical)");
        return 1;
    }
    fwrite(t, 1, fl, stdout);
    fputs("\f\n", stdout);
    fputs(t + fl, stdout);
    free(t);
    return 0;
}

/* --hash-text FILE|-: mf_form_hash_text of a whole text (the slot harness's
 * cell-text check folds a cell TU's site span with it; check B folds the
 * instances' texts with it). */
static int hash_text_mode(const char *path)
{
    FILE *f = strcmp(path, "-") ? fopen(path, "rb") : stdin;
    if (!f) { perror(path); return 1; }
    size_t cap = 4096, n = 0;
    char *b = malloc(cap);
    for (size_t k; b && (k = fread(b + n, 1, cap - n - 1, f)) > 0; ) {
        n += k;
        if (n + 1 == cap) {
            char *nb = realloc(b, cap *= 2);
            if (!nb) free(b);
            b = nb;
        }
    }
    if (f != stdin) fclose(f);
    if (!b) return 1;
    b[n] = 0;
    char h[17];
    mf_form_hash_text(b, h);
    printf("%s\n", h);
    free(b);
    return 0;
}

/* --facts: one line per row of `facts[]`, its value `-` where the key does
 * not apply to the instance's shape. Every value is read off the entry
 * table's row and its shape (kit.h), never restated here. */
typedef struct { const mf_form_entry *e; const mf_form_shape *sh; const char *row; } FactIn;
typedef void (*fact_fn)(const FactIn *x, Text *o);

/* The fact writers. f_str/f_hex write one value (NULL: `-`); f_set_shape
 * and f_find_shape test the instance's shape; every f_<key> below writes the
 * facts[] row <key> for the instance, read off its entry and shape. */
static void f_str(Text *o, const char *v) { text_put(o, v ? v : "-", strlen(v ? v : "-")); }
static void f_hex(Text *o, const uint8_t *b, size_t n)
{
    char buf[8];
    for (size_t i = 0; i < n; i++) {
        snprintf(buf, sizeof buf, "%s%02x", i ? " " : "", b[i]);
        text_put(o, buf, strlen(buf));
    }
    if (!n) f_str(o, NULL);
}
static int f_set_shape(const FactIn *x) { return x->e->shape != MF_FH_RUNCMP; }
static int f_find_shape(const FactIn *x)
{
    return x->e->shape == MF_FH_FIND || x->e->shape == MF_FH_WINDOW;
}
/* the run's mask byte at i: 0xDF at a caseless letter, else 0xFF (fh_run's) */
static uint8_t f_mask(const mf_form_entry *e, size_t i)
{
    unsigned c = (unsigned char)e->bytes[i] | 0x20;
    return e->caseless && c >= 'a' && c <= 'z' ? 0xDF : 0xFF;
}
static void f_id(const FactIn *x, Text *o) { f_str(o, x->e->id); }
static void f_cls(const FactIn *x, Text *o) { f_str(o, x->e->cls); }
static void f_canon(const FactIn *x, Text *o) { f_str(o, x->e->canon ? "1" : "0"); }
static void f_shape(const FactIn *x, Text *o) { f_str(o, x->sh->word); }
static void f_entry(const FactIn *x, Text *o) { f_str(o, x->sh->entry); }
static void f_row(const FactIn *x, Text *o) { f_str(o, x->row); }
static void f_target(const FactIn *x, Text *o) { f_str(o, x->e->target); }
static void f_deny(const FactIn *x, Text *o) { f_str(o, x->e->deny); }
static void f_prefix(const FactIn *x, Text *o) { (void)x; f_str(o, "mf"); }
static void f_s(const FactIn *x, Text *o) { f_str(o, x->sh->s); }
static void f_s_type(const FactIn *x, Text *o) { f_str(o, x->sh->s ? "const unsigned char *" : NULL); }
static void f_n(const FactIn *x, Text *o) { f_str(o, x->sh->n); }
static void f_n_type(const FactIn *x, Text *o) { f_str(o, x->sh->n ? "size_t" : NULL); }
static void f_lo(const FactIn *x, Text *o) { f_str(o, f_find_shape(x) ? x->sh->lo : NULL); }
static void f_lo_type(const FactIn *x, Text *o) { f_str(o, f_find_shape(x) && x->sh->lo ? "size_t" : NULL); }
static void f_result(const FactIn *x, Text *o) { f_str(o, x->sh->result); }
static void f_result_type(const FactIn *x, Text *o) { f_str(o, x->sh->result ? "size_t" : NULL); }
static void f_cand(const FactIn *x, Text *o) { f_str(o, x->sh->cand); }
static void f_cand_type(const FactIn *x, Text *o) { f_str(o, x->sh->cand ? "size_t" : NULL); }
static void f_value(const FactIn *x, Text *o)
{
    f_str(o, f_find_shape(x) ? "the result: the found position, else the miss value"
                             : "a C boolean expression: 1 iff the candidate passes");
}
static void f_miss(const FactIn *x, Text *o)
{
    f_str(o, !f_find_shape(x) ? NULL : x->e->on_miss ? "on_miss runs (the result is not written)"
                                                       : x->sh->n);
}
static void f_on_miss(const FactIn *x, Text *o) { f_str(o, x->e->on_miss); }
/* the empty range's statement (mf_site.empty), the find shapes' */
static void f_empty(const FactIn *x, Text *o)
{
    static const struct { uint8_t v; const char *says; } em[] = {
        { MF_EMPTY_NOP,      "nop: at lo >= n the text writes nothing" },
        { MF_EMPTY_EXCLUDED, "excluded: the caller guarantees lo < n" },
        { MF_EMPTY_MISS,     "miss: at lo >= n the result is the miss value" },
    };
    const char *v = NULL;
    for (unsigned i = 0; f_find_shape(x) && i < sizeof em / sizeof em[0]; i++)
        if (em[i].v == x->e->empty) v = em[i].says;
    f_str(o, v);
}
static void f_table(const FactIn *x, Text *o) { f_str(o, x->e->table ? "mf_tbl" : NULL); }
static void f_table_members(const FactIn *x, Text *o)
{
    if (x->e->table) f_hex(o, (const uint8_t *)x->e->bytes, strlen(x->e->bytes));
    else f_str(o, NULL);
}
static void f_table_value(const FactIn *x, Text *o)
{
    f_str(o, x->e->table ? "unsigned char[256]: nonzero at a member, 0 elsewhere" : NULL);
}
static void f_members(const FactIn *x, Text *o)
{
    if (f_set_shape(x)) f_hex(o, (const uint8_t *)x->e->bytes, strlen(x->e->bytes));
    else f_str(o, NULL);
}
/* the first byte from 'a' up (mod 256) outside the set, or one failing the
   run's first position under its mask */
static void f_miss_byte(const FactIn *x, Text *o)
{
    const mf_form_entry *e = x->e;
    for (unsigned k = 0; k < 256; k++) {
        uint8_t b = (uint8_t)('a' + k);
        int hit = f_set_shape(x) ? strchr(e->bytes, b) != NULL
                                 : (b & f_mask(e, 0)) == (uint8_t)e->bytes[0];
        if (b && !hit) { f_hex(o, &b, 1); return; }
    }
    f_str(o, NULL);
}
static void f_L(const FactIn *x, Text *o)
{
    char buf[24];
    snprintf(buf, sizeof buf, "%zu", strlen(x->e->bytes));
    f_str(o, f_set_shape(x) ? NULL : buf);
}
static void f_run(const FactIn *x, Text *o)
{
    if (f_set_shape(x)) f_str(o, NULL);
    else f_hex(o, (const uint8_t *)x->e->bytes, strlen(x->e->bytes));
}
static void f_runmask(const FactIn *x, Text *o)
{
    uint8_t m[64];
    size_t L = strlen(x->e->bytes);
    if (f_set_shape(x) || L > sizeof m) { f_str(o, NULL); return; }
    for (size_t i = 0; i < L; i++) m[i] = f_mask(x->e, i);
    f_hex(o, m, L);
}
static void f_hit(const FactIn *x, Text *o)
{
    f_str(o, f_set_shape(x) ? "a byte of `members`"
                            : "the bytes b[0..L) with (b[i] & mask[i]) == run[i]");
}
static void f_reads(const FactIn *x, Text *o)
{
    char buf[24];
    snprintf(buf, sizeof buf, "%zu", x->e->shape == MF_FH_SETTEST ? (size_t)1 : strlen(x->e->bytes));
    f_str(o, f_find_shape(x) ? NULL : buf);
}

static const struct { const char *key; fact_fn f; } facts[] = {
    { "id", f_id },                 { "cls", f_cls },             { "canon", f_canon },
    { "shape", f_shape },           { "entry", f_entry },         { "row", f_row },
    { "target", f_target },         { "deny", f_deny },           { "prefix", f_prefix },
    { "subject", f_s },             { "subject_type", f_s_type },
    { "n", f_n },                   { "n_type", f_n_type },
    { "lo", f_lo },                 { "lo_type", f_lo_type },
    { "result", f_result },         { "result_type", f_result_type },
    { "cand", f_cand },             { "cand_type", f_cand_type },
    { "value", f_value },           { "miss_value", f_miss },     { "on_miss", f_on_miss },
    { "empty", f_empty },
    { "table", f_table },           { "table_type", f_table_value },
    { "table_members", f_table_members },
    { "members", f_members },       { "L", f_L },                 { "run", f_run },
    { "mask", f_runmask },          { "hit", f_hit },             { "miss_byte", f_miss_byte },
    { "reads_past_cand", f_reads },
};

static int facts_mode(const char *id, const char *cls)
{
    FactIn x = { mf_form_entry_of(id, cls), NULL, NULL };
    x.sh = mf_form_shape_of(x.e);
    x.row = x.e ? mf_form_row(x.e->id, x.e->cls) : NULL;
    if (!x.e || !x.sh || !x.row) {
        fprintf(stderr, "arm_fixtures: no rendered instance %s %s\n", id, cls ? cls : "(canonical)");
        return 1;
    }
    for (unsigned i = 0; i < sizeof facts / sizeof facts[0]; i++) {
        Text o = { 0 };
        facts[i].f(&x, &o);
        printf("%s\t%s\n", facts[i].key, o.p ? o.p : "-");
        free(o.p);
    }
    return 0;
}

/* ---- THE PURITY HARNESS (span_pick unit 1d; span_pick.md rev 5.2 §Staging,
 * 1d's test row) ----------------------------------------------------------
 *
 * The plan face (mf_wdecide) is a PURE FUNCTION of the site's facts, the
 * frame, the measurement set and the handed rates (D186 add. 2): the same
 * site gets the same reply on a fresh art and on an art that has defined
 * any number of other sites, in any order. Since unit 3.0b (MF_SITE_ABI 28,
 * plan_frame.md §2.2-§2.3, §5) every site is asked twice, NONE and FRAMED
 * (call DEFINE with the define's own hooks), each reply compared WHOLE
 * (memcmp, so a member added later is compared too); a site's NONE and
 * framed replies agree on the decision group (the prefix up to `framed`).
 * Every ask states COUNTING callbacks (no hook callback is called: the
 * count stays 0) on an art whose COUNTING ARENA does not grow across an
 * ask; their populations (a framed ask whose T-FIND picks PAIR, a refused
 * framed ask) are counted, a count of 0 a named failure. Then the call's
 * own fixtures (mf_wcall: UNSTATED and out-of-range calls refused, NONE's
 * frame part zero and blind to the frame, EMIT walking DEFINE|USE), the
 * site's `--memfn=` options reaching a framed ask, and the same-class-
 * different-text fixture (a renamed hook of the same class moves no reply).
 *
 * WHY THE DEFINES ARE INTERLEAVED: `art->nsites`' one writer is mf_define
 * and the plan face takes a `const mf_art *`, so plan calls alone see one
 * nsites in every order, and a row keyed on it would stay green (K35).
 * Order reaches the plan face only through the defines, the real phase-1 /
 * phase-2 interleave, so every site is asked between every two defines.
 *
 *   arm_fixtures --purity          per rate table (NONE, a skewed one with
 *       ties) and per define order (in order, reversed, repeated): before
 *       each define and after the last, every site's reply compared field
 *       by field with its reply on a FRESH art; then THE STICKY-ERR CASE:
 *       after a refused define every plan call answers -1 (breaker (a),
 *       FENCED: pcrec fails the compile on any refusal, so no such reply
 *       reaches an artifact; asserted as the fence, not as purity). One
 *       `FAIL:` line per difference; `checks passed/failed` counts.
 *   arm_fixtures --purity-control  THE CONTROL: each site's NONE and framed
 *       replies after ONE define of the next site, printed as a hex dump of
 *       the whole struct; run_finder.sh compares a planted build's print (a
 *       KEY row keyed on nsites) with this build's, so the plant is shown
 *       REACHED on the unharnessed fixture.
 *
 * The sites reach every Table A row but A-empty and A-floor's floor-only
 * path (A-mass, A-parked, A-model, MARGIN's two alternatives) and the run
 * member (a verify-YES run R). */
enum { PUR_N = 11 };
static mf_wspan pur_spans[PUR_N][2][4];
static mf_walt pur_alts[PUR_N][2];

static void pur_span(mf_wspan *w, int32_t start, const char *const *sets, unsigned len,
                     int verify, unsigned core_lo, unsigned core_len)
{
    memset(w, 0, sizeof *w);
    w->start = start;
    w->len = (uint8_t)len;
    w->verify = (uint8_t)verify;
    w->core = MF_CORE_STATED;
    w->core_lo = (uint8_t)core_lo;
    w->core_len = (uint8_t)core_len;
    for (unsigned j = 0; j < len; j++)
        for (const char *c = sets[j]; *c; c++)
            set_add(w->set[j], (unsigned char)*c);
}

/* The RESEED alternative of sites 2 and 3: F0 and three walked offsets, two
 * of equal rate under the skewed table (C-model's exchange order). */
static void pur_reseed(mf_wspan *sp, mf_walt *a)
{
    pur_span(&sp[0], 0, (const char *const[]){ "f" }, 1, MF_VERIFY_YES, 0, 1);
    pur_span(&sp[1], 1, (const char *const[]){ "g" }, 1, MF_VERIFY_NO, 0, 1);
    pur_span(&sp[2], 2, (const char *const[]){ "h" }, 1, MF_VERIFY_NO, 0, 1);
    pur_span(&sp[3], 3, (const char *const[]){ "i" }, 1, MF_VERIFY_NO, 0, 1);
    *a = (mf_walt){ MF_ENTRY_RESEED, 4, sp };
}

static mf_site pur_site(unsigned i)
{
    mf_site s = base_site();
    s.pred.need = 0;            /* a window site states no renderer interface */
    s.op = MF_OP_FIND;
    s.form = MF_FORM_FUNC;
    s.handoff = MF_H_RETURN;
    s.use = MF_USE_POSITION;
    s.site_kind = MF_SK_DFA_SCAN;
    s.pred.fn_ref = 1;
    mf_wspan (*sp)[4] = pur_spans[i];
    mf_walt *a = pur_alts[i];
    s.nalt = 1;
    switch (i) {
    case 0:                     /* NONE: A-mass, a set position among one-byte ones */
        pur_span(&sp[0][0], 0, (const char *const[]){ "a", "bc", "q" }, 3, MF_VERIFY_YES, 0, 3);
        pur_span(&sp[0][1], 4, (const char *const[]){ "z" }, 1, MF_VERIFY_YES, 0, 1);
        a[0] = (mf_walt){ MF_ENTRY_NONE, 2, sp[0] };
        break;
    case 1:                     /* PARKED: A-parked */
        pur_span(&sp[0][0], 0, (const char *const[]){ "x" }, 1, MF_VERIFY_YES, 0, 1);
        pur_span(&sp[0][1], 1, (const char *const[]){ "y", "w" }, 2, MF_VERIFY_YES, 0, 2);
        a[0] = (mf_walt){ MF_ENTRY_PARKED, 2, sp[0] };
        break;
    case 2:                     /* RESEED: A-model, C-model */
        pur_reseed(sp[0], &a[0]);
        break;
    case 3:                     /* PARKED + RESEED: the MARGIN */
        pur_span(&sp[0][0], 0, (const char *const[]){ "fF" }, 1, MF_VERIFY_YES, 0, 1);
        a[0] = (mf_walt){ MF_ENTRY_PARKED, 1, sp[0] };
        pur_reseed(sp[1], &a[1]);
        s.nalt = 2;
        break;
    case 4:                     /* NONE with a verify-YES run R: the run member */
        pur_span(&sp[0][0], 0, (const char *const[]){ "a", "b", "c", "d" }, 4, MF_VERIFY_YES,
                 0, 4);
        a[0] = (mf_walt){ MF_ENTRY_NONE, 1, sp[0] };
        break;
    case 5:                     /* A-empty: an empty meet inside a core */
        pur_span(&sp[0][0], 0, (const char *const[]){ "a" }, 1, MF_VERIFY_YES, 0, 1);
        pur_span(&sp[0][1], 0, (const char *const[]){ "b" }, 1, MF_VERIFY_YES, 0, 1);
        a[0] = (mf_walt){ MF_ENTRY_NONE, 2, sp[0] };
        break;
    case 6:                     /* A-floor: no core position; a full-set one (C-bound) */
        pur_span(&sp[0][0], 0, (const char *const[]){ "a" }, 1, MF_VERIFY_YES, 0, 0);
        pur_span(&sp[0][1], 1, (const char *const[]){ "" }, 1, MF_VERIFY_YES, 0, 0);
        memset(sp[0][1].set[0], 0xFF, 32);
        a[0] = (mf_walt){ MF_ENTRY_NONE, 2, sp[0] };
        break;
    case 7:                     /* A-mass with a full-set verify-YES position (C-bound) */
        pur_span(&sp[0][0], 0, (const char *const[]){ "ab" }, 1, MF_VERIFY_YES, 0, 1);
        pur_span(&sp[0][1], 2, (const char *const[]){ "" }, 1, MF_VERIFY_YES, 0, 0);
        memset(sp[0][1].set[0], 0xFF, 32);
        a[0] = (mf_walt){ MF_ENTRY_NONE, 2, sp[0] };
        break;
    case 8:                     /* RESEED first, PARKED second: M-parked wins at index 1 */
        pur_reseed(sp[0], &a[0]);
        pur_span(&sp[1][0], 0, (const char *const[]){ "F" }, 1, MF_VERIFY_YES, 0, 1);
        a[1] = (mf_walt){ MF_ENTRY_PARKED, 1, sp[1] };
        s.nalt = 2;
        break;
    case 9:                     /* NONE with a verify-NO run R: the exact run member */
        pur_span(&sp[0][0], 0, (const char *const[]){ "x" }, 1, MF_VERIFY_YES, 0, 1);
        pur_span(&sp[0][1], 1, (const char *const[]){ "m", "jk", "n" }, 3, MF_VERIFY_NO, 0, 3);
        a[0] = (mf_walt){ MF_ENTRY_NONE, 2, sp[0] };
        break;
    default:                    /* RESEED, a rare non-scan walked offset: C-model's pick */
        pur_span(&sp[0][0], 0, (const char *const[]){ "f" }, 1, MF_VERIFY_YES, 0, 1);
        pur_span(&sp[0][1], 1, (const char *const[]){ "p" }, 1, MF_VERIFY_NO, 0, 1);
        pur_span(&sp[0][2], 2, (const char *const[]){ "rR" }, 1, MF_VERIFY_NO, 0, 1);
        a[0] = (mf_walt){ MF_ENTRY_RESEED, 3, sp[0] };
        break;
    }
    s.alts = a;
    return s;
}

/* A site no define accepts: two NONE alternatives (wf_check: only a PARKED
 * and a RESEED one pair). */
static mf_site pur_refused(void)
{
    mf_site s = pur_site(0);
    static mf_walt two[2];
    two[0] = two[1] = pur_alts[0][0];
    s.alts = two;
    s.nalt = 2;
    return s;
}

/* The skewed rate table: ties among g/h (equal walked masses) and b/d. */
static uint32_t pur_rates[256];

static const mf_analysis *pur_rated(void)
{
    for (int b = 0; b < 256; b++) pur_rates[b] = 3000;
    static const struct { char c; uint32_t r; } skew[] = {
        { 'a', 90000 }, { 'b', 500 }, { 'c', 70000 }, { 'd', 500 }, { 'q', 800 },
        { 'z', 100 }, { 'f', 500000 }, { 'F', 600 }, { 'g', 400 }, { 'h', 400 },
        { 'i', 30000 }, { 'x', 5000 }, { 'y', 900 }, { 'w', 900 }, { 'j', 100 }, { 'k', 100 }, { 'p', 100000 }, { 'r', 300 }, { 'R', 300 },
    };
    for (size_t i = 0; i < sizeof skew / sizeof skew[0]; i++)
        pur_rates[(unsigned char)skew[i].c] = skew[i].r;
    return an_make(1, pur_rates);
}

/* The reply members by offset, for naming where two replies differ. */
#define PUR_M(m) { #m, offsetof(mf_wreply, m), sizeof ((mf_wreply *)0)->m }
static const struct { const char *name; size_t off, size; } pur_members[] = {
    PUR_M(alt), PUR_M(reseed), PUR_M(has_stop), PUR_M(stop), PUR_M(stop_set), PUR_M(nplan),
    PUR_M(plan), PUR_M(plan_term), PUR_M(pinned), PUR_M(run_stated), PUR_M(run_member),
    PUR_M(run_lo), PUR_M(run_len), PUR_M(path), PUR_M(framed), PUR_M(frame_row),
    PUR_M(method), PUR_M(search), PUR_M(stream), PUR_M(fused), PUR_M(plan_test),
    PUR_M(stop_test),
};
#undef PUR_M

/* NULL iff replies `a` and `b` are equal byte for byte over their first
 * `n` bytes (the whole struct, or the decision group's prefix), else the
 * first member that differs ("padding" where only padding does). The kit
 * zeroes every reply whole first (contract line 3), so memcmp is exact. */
static const char *pur_diff_n(const mf_wreply *a, const mf_wreply *b, size_t n)
{
    if (!memcmp(a, b, n)) return NULL;
    for (size_t i = 0; i < sizeof pur_members / sizeof *pur_members; i++)
        if (pur_members[i].off < n &&
            memcmp((const char *)a + pur_members[i].off, (const char *)b + pur_members[i].off,
                   pur_members[i].size))
            return pur_members[i].name;
    return "padding";
}

static const char *pur_diff(const mf_wreply *a, const mf_wreply *b)
{
    return pur_diff_n(a, b, sizeof *a);
}

static long pur_pass, pur_fail;

static void pur_ok(int ok, const char *what)
{
    if (ok) { pur_pass++; return; }
    pur_fail++;
    printf("FAIL: %s\n", what);
}

/* THE COUNTING HOOKS (plan_frame.md Goal 3, §5 rows G and V): every
 * callback an mf_hooks can state, each counting its calls into
 * `pur_hook_calls`. The plan face calls none, so the count stays 0 across
 * every ask (a define may call them: the count is read around asks only). */
static long pur_hook_calls;

static const char *pc_fn_name(void *u, uint32_t ref) { (void)u; (void)ref; pur_hook_calls++; return "rx_pur"; }
static const char *pc_table_name(void *u, uint32_t ref) { (void)u; (void)ref; pur_hook_calls++; return "rx_t"; }
static void pc_note(void *u, mf_sink *c, uint32_t part) { (void)u; (void)c; (void)part; pur_hook_calls++; }
static const char *pc_note_tag(void *u, uint32_t part) { (void)u; (void)part; pur_hook_calls++; return "t"; }
static const char *pc_member(void *u, uint32_t term, const char *byte_expr)
{
    (void)u; (void)term; (void)byte_expr; pur_hook_calls++;
    return "1";
}
static void pc_on_cand(void *u, mf_sink *c, const char *cand) { (void)u; (void)c; (void)cand; pur_hook_calls++; }

/* The define's hooks (pur_define's stated-ness: fn_name, table_name, note,
 * note_tag, miss N) with counting callbacks; `all` adds `member` and
 * `on_cand`, the six stated callbacks. */
static mf_hooks pur_hooks(int all)
{
    mf_hooks h = { .fn_name = pc_fn_name, .table_name = pc_table_name, .note = pc_note,
                   .note_tag = pc_note_tag, .miss = MF_MISS_N };
    if (all) {
        h.member = pc_member;
        h.on_cand = pc_on_cand;
    }
    return h;
}

/* THE COUNTING ARENA (plan_frame.md §2.2 "Allocation", §5 row AC): every
 * purity art allocates through it; an ask must not grow it. */
static long pur_arena_n;

static void *pur_alloc(void *u, size_t n)
{
    (void)u;
    pur_arena_n++;
    return calloc(1, n);
}

/* One ask through mf_wdecide on `art`, held to the plan face's purity: no
 * hook callback called, no arena allocation. Its rc. */
static int pur_ask(const mf_art *art, const mf_site *s, const mf_hooks *h, uint8_t call,
                   mf_wreply *out, const char *what)
{
    char m[200];
    long a0 = pur_arena_n, h0 = pur_hook_calls;
    int rc = mf_wdecide(art, s, h, call, out);
    snprintf(m, sizeof m, "%s: the ask grew the art's arena by %ld (plan_frame.md §2.2: a "
             "phase-1 ask allocates on the heap only)", what, pur_arena_n - a0);
    pur_ok(pur_arena_n == a0, m);
    snprintf(m, sizeof m, "%s: the ask called %ld hook callback(s) (Goal 3: the plan face "
             "calls none)", what, pur_hook_calls - h0);
    pur_ok(pur_hook_calls == h0, m);
    return rc;
}

/* Site `i`'s define on `art` (FUNC/RETURN, the fixture hooks): 0 or the
 * kit's refusal. */
static int pur_define(mf_art *art, const mf_site *s)
{
    Text def = { 0 };
    mf_sink sd = sink_of(&def);
    Fx fd = { s, "rx_pur", NULL };
    mf_hooks hd = { .fn_name = h_fn_name, .table_name = h_table_name, .note = h_note,
                    .note_tag = h_note_tag, .u = &fd, .miss = MF_MISS_N };
    uint32_t h = 0;
    int rc = mf_define(art, s, &hd, &sd, &h);
    free(def.p);
    return rc;
}

/* A STMT window site over purity site `i`'s facts: ASSIGN (ON_MISS where
 * `onmiss`), kind `kind`, the site's `--memfn=` options `opts`. */
static mf_site pur_stmt(unsigned i, int onmiss, uint8_t kind, const char *opts)
{
    mf_site s = pur_site(i);
    s.form = MF_FORM_STMT;
    s.handoff = onmiss ? MF_H_ON_MISS : MF_H_ASSIGN;
    s.site_kind = kind;
    s.pred.fn_ref = 0;
    s.opts = opts;
    return s;
}

/* The one-call (EMIT) hooks of a STMT site: every text hook stated, the
 * counting callbacks too. */
static mf_hooks pur_text_hooks(int onmiss)
{
    mf_hooks h = pur_hooks(0);
    h.fn_name = NULL;
    h.s = "s"; h.n = "n"; h.lo = "lo"; h.floor = "fl"; h.result = "r";
    h.miss = "((size_t)-1)";
    h.on_miss = onmiss ? "{ m = 1; }" : NULL;
    return h;
}

/* `site`'s one-call render on a fresh art under `h`: 0 and the rendered
 * text's body+file in *text (caller frees), or the refusal. */
static int pur_emit(const mf_site *site, const mf_hooks *h, char **text, mf_result *res)
{
    static mf_arena ar = { NULL, a_alloc };
    Text b = { 0 }, f = { 0 };
    mf_sink sb = sink_of(&b), sf = sink_of(&f);
    mf_art *art = art_begin(&ar, "pur", 0, NULL, NULL);
    int rc = mf_emit(art, site, h, &sb, &sf, res);
    size_t nb = b.p ? strlen(b.p) : 0, nf = f.p ? strlen(f.p) : 0;
    *text = calloc(1, nb + nf + 2);
    if (nb) memcpy(*text, b.p, nb);
    if (nf) memcpy(*text + nb + 1, f.p, nf), (*text)[nb] = '\n';
    free(b.p);
    free(f.p);
    return rc;
}

/* A STMT/ASSIGN site with one stated one-byte span whose miss leaves: the
 * PF memchr row renders it on E-stmt under pur_pf_hooks (a leaving `on_miss`,
 * every hook the row reads an identifier). */
static mf_site pur_pf_site(void)
{
    static mf_wspan sp[1];
    static mf_walt al[1];
    mf_site site = pur_stmt(0, 0, MF_SK_DFA_SCAN, NULL);
    pur_span(&sp[0], 0, (const char *const[]){ "q" }, 1, MF_VERIFY_NO, 0, 1);
    al[0] = (mf_walt){ MF_ENTRY_NONE, 1, sp };
    site.alts = al;
    site.nalt = 1;
    site.on_miss_leaves = 1;
    return site;
}

static mf_hooks pur_pf_hooks(void)
{
    mf_hooks h = pur_text_hooks(0);
    h.floor = NULL;
    h.note = NULL;
    h.note_tag = NULL;
    h.on_miss = "goto o;";
    return h;
}

/* THE CALL's fixtures (plan_frame.md §2.2 contract lines 1-4, §5 rows S, T,
 * U, I, AD) and the counted asks the counting arena must reach (row AC). */
static void pur_call_fixtures(mf_arena *ar)
{
    char m[200];
    mf_wreply r, q;
    mf_hooks h = pur_hooks(1);
    static const uint8_t zero[sizeof(mf_wreply)];
    for (unsigned i = 0; i < PUR_N; i++) {
        mf_site site = pur_site(i);
        mf_art *art = art_begin(ar, "pur", 0, NULL, NULL);
        /* (S) UNSTATED is refused, never read as NONE; (line 1) every call
           above EMIT too */
        snprintf(m, sizeof m, "call: site %u: call 0 (UNSTATED) did not answer -1", i);
        pur_ok(pur_ask(art, &site, &h, MF_WCALL_UNSTATED, &r, m) == -1, m);
        int above = 0;
        for (unsigned c = MF_WCALL_EMIT + 1; c < 256; c++)
            above += mf_wdecide(art, &site, &h, (uint8_t)c, &r) != -1;
        snprintf(m, sizeof m, "call: site %u: %d call value(s) above EMIT were not refused", i,
                 above);
        pur_ok(!above, m);
        /* (T) NONE's frame part is zero; (line 4) NONE reads no frame field
           and no `def`: a site differing in every frame field asks equal */
        snprintf(m, sizeof m, "call: site %u: the NONE ask refused", i);
        pur_ok(pur_ask(art, &site, NULL, MF_WCALL_NONE, &r, m) == 0, m);
        snprintf(m, sizeof m, "call: site %u: NONE's frame part is not zero (framed %u)", i,
                 r.framed);
        pur_ok(!memcmp((const char *)&r + offsetof(mf_wreply, framed),
                       zero + offsetof(mf_wreply, framed),
                       sizeof r - offsetof(mf_wreply, framed)), m);
        mf_site other = site;
        other.form = MF_FORM_STMT;
        other.handoff = MF_H_ON_MISS;
        other.empty = MF_EMPTY_AT_N;
        other.use = MF_USE_ENTRY;
        other.site_kind = MF_SK_REPORT;
        other.decl_point = 1;
        other.on_miss_leaves = 1;
        other.pred.fn_ref = 0;
        other.reverse = 1;
        pur_ask(art, &other, &h, MF_WCALL_NONE, &q, "call: NONE over another frame");
        const char *d = pur_diff(&r, &q);
        snprintf(m, sizeof m, "call: site %u: two NONE asks differing only in frame fields "
                 "and def differ at %s", i, d ? d : "-");
        pur_ok(!d, m);
        /* a framed ask and the NONE ask agree on the decision group */
        snprintf(m, sizeof m, "call: site %u: the framed ask refused", i);
        pur_ok(pur_ask(art, &site, &h, MF_WCALL_DEFINE, &q, m) == 0, m);
        d = pur_diff_n(&r, &q, offsetof(mf_wreply, framed));
        snprintf(m, sizeof m, "call: site %u: NONE and DEFINE differ in the decision group at "
                 "%s", i, d ? d : "-");
        pur_ok(!d, m);
        snprintf(m, sizeof m, "call: site %u: a framed reply is not `framed` 1 (%u)", i, q.framed);
        pur_ok(q.framed == 1, m);
    }

    /* (U) EMIT walks Table E under DEFINE|USE, as mf_emit: a STMT/ASSIGN
       site with one stated one-byte span, whose `on_miss` (an expression
       statement, on a site whose miss leaves) the PF memchr row serves at
       DEFINE and declines at USE (its contract: a jump or a braced block),
       so mf_define renders it on E-stmt and mf_emit on E-find */
    {
        mf_site site = pur_pf_site();
        mf_hooks th = pur_pf_hooks();
        th.on_miss = "x = 1;";
        mf_art *art = art_begin(ar, "pur", 0, NULL, NULL);
        mf_wreply rd, re;
        int cd = pur_ask(art, &site, &th, MF_WCALL_DEFINE, &rd, "emit: DEFINE");
        int ce = pur_ask(art, &site, &th, MF_WCALL_EMIT, &re, "emit: EMIT");
        char *text;
        mf_result res;
        memset(&res, 0, sizeof res);
        int ee = pur_emit(&site, &th, &text, &res);
        free(text);
        snprintf(m, sizeof m, "emit: the EMIT ask answers %d where mf_emit answers %d", ce, ee);
        pur_ok(ce == ee, m);
        snprintf(m, sizeof m, "emit: the EMIT ask's frame row %s is not mf_emit's (%s: E-find iff "
                 "window-search)", re.frame_row, res.form_id);
        pur_ok(!ce && !strcmp(re.frame_row, "E-find") == !strcmp(res.form_id, "window-search"), m);
        snprintf(m, sizeof m, "emit: DEFINE (%d, %s) and EMIT (%d, %s) answer one frame row on "
                 "the population site: the fixture reaches no difference", cd, rd.frame_row, ce,
                 re.frame_row);
        pur_ok(!cd && !ce && strcmp(rd.frame_row, re.frame_row), m);
    }

    /* (I) the site's `--memfn=` options reach a framed ask's walks: a REPORT
       site under no-window-search is refused as mf_define refuses it (and
       that refusal is wf_plan_site's own, reaching why_room: AC's counted
       refused ask); under a T-FIND deny the framed search is the text's */
    long refused_n = 0, pair_n = 0;
    {
        mf_site site = pur_stmt(1, 0, MF_SK_REPORT, "no-window-search");
        mf_hooks th = pur_text_hooks(0);
        mf_art *art = art_begin(ar, "pur", 0, NULL, NULL);
        mf_wreply rr;
        pur_ok(pur_ask(art, &site, &th, MF_WCALL_NONE, &rr, "opts: NONE") == 0,
               "opts: the REPORT site's NONE ask refused (the fixture is not a refusal of the "
               "framed ask's own)");
        int cf = pur_ask(art, &site, &th, MF_WCALL_EMIT, &rr, "opts: EMIT");
        char *text;
        mf_result res;
        int ee = pur_emit(&site, &th, &text, &res);
        free(text);
        snprintf(m, sizeof m, "opts: a framed ask on a REPORT site under no-window-search "
                 "answers %d, mf_emit %d (it must refuse, as the define does)", cf, ee);
        pur_ok(cf == -1 && ee != 0, m);
        refused_n += cf == -1 && ee != 0;
    }
    static const char *const deny[] = { NULL, "no-fd-d1" };
    for (unsigned k = 0; k < 2; k++)
        for (unsigned i = 0; i < PUR_N; i++) {
            mf_site site = pur_stmt(i, 0, MF_SK_REPORT, deny[k]);
            mf_hooks th = pur_text_hooks(0);
            mf_art *art = art_begin(ar, "pur", 0, NULL, NULL);
            mf_wreply rr;
            if (pur_ask(art, &site, &th, MF_WCALL_EMIT, &rr, "opts: EMIT over T-FIND")) continue;
            char *text;
            mf_result res;
            if (pur_emit(&site, &th, &text, &res)) { free(text); continue; }
            int libc = strstr(text, "memchr(") != NULL;
            free(text);
            if (strcmp(rr.frame_row, "E-find")) continue;
            pair_n += rr.search == MF_WSEARCH_PAIR;
            if (rr.search == MF_WSEARCH_PAIR) continue;
            snprintf(m, sizeof m, "opts: site %u under %s: the framed search %u (method %s) "
                     "is %sLIBC where the define's text %s memchr", i, deny[k] ? deny[k] : "-",
                     rr.search, rr.method,
                     rr.search == MF_WSEARCH_LIBC ? "" : "not ", libc ? "calls" : "does not call");
            pur_ok((rr.search == MF_WSEARCH_LIBC || rr.search == MF_WSEARCH_LIBC_BACK) == libc,
                   m);
        }
    /* AC's populations, counted: a count of 0 is a named failure (the
       counting arena would have nothing to see) */
    snprintf(m, sizeof m, "arena population: %ld framed asks picked PAIR on E-find "
             "(wf_find_decide's allocation); 0 reaches none", pair_n);
    pur_ok(pair_n > 0, m);
    snprintf(m, sizeof m, "arena population: %ld refused framed asks reached the plan "
             "function's refusal (why_room); 0 reaches none", refused_n);
    pur_ok(refused_n > 0, m);

    /* (AD) THE SAME-CLASS-DIFFERENT-TEXT FIXTURE (plan_frame.md §2.2's round
       trip; R21): STMT/ASSIGN and STMT/ON_MISS sites asked with EMIT (the
       window rows read the text hooks at USE only), every text hook stated,
       each replaced by a text of the SAME class: the reply does not move.
       The population: every purity site in both frames (their rows serve
       every class of the text hooks), and the PF site (pur_pf_site: the PF
       memchr row serves `s`, `n`, `lo` and `result` as identifiers only, so a
       gate reading a spelling beyond its class moves its frame row). */
    long ad_n = 0, ad_moved = 0, ad_pf = 0;
    for (int onm = 0; onm < 3; onm++)
        for (unsigned i = 0; i < (onm < 2 ? PUR_N : 1); i++) {
            mf_site site = onm < 2 ? pur_stmt(i, onm, MF_SK_DFA_SCAN, NULL) : pur_pf_site();
            mf_art *art = art_begin(ar, "pur", 0, NULL, NULL);
            mf_hooks base = onm < 2 ? pur_text_hooks(onm) : pur_pf_hooks();
            mf_wreply r0, r1;
            if (pur_ask(art, &site, &base, MF_WCALL_EMIT, &r0, "same-class: base")) continue;
            ad_n++;
            ad_pf += onm == 2 && r0.fused == MF_WFUSED_NO && !strcmp(r0.frame_row, "E-stmt");
            for (int c = 0; c < 9; c++) {
                mf_hooks from = base, to = base;
                const char *what;
                switch (c) {
                case 0: to.s = "subj"; what = "s"; break;
                case 1: to.n = "len"; what = "n"; break;
                case 2: to.lo = "lo2"; what = "lo"; break;
                case 3: to.floor = to.floor ? "fl2" : NULL; what = "floor"; break;
                case 4: to.result = "r2"; what = "result"; break;
                case 5: to.miss = "((size_t)-2)"; what = "miss (a text)"; break;
                case 6: to.on_miss = onm == 1 ? "{ k = 1; }" : onm ? "goto p;" : NULL;
                        what = "on_miss"; break;
                /* the cross-hook relation (cl_miss): a miss equal to n's text
                   is the N class, so the two rename together; and the N
                   token (compared by address) stands for that text */
                case 7: from.miss = "n"; to.miss = "len"; to.n = "len";
                        what = "n with the miss equal to it"; break;
                default: from.miss = "n"; to.miss = MF_MISS_N;
                         what = "miss (the N token for n's text)"; break;
                }
                mf_wreply rf;
                if (pur_ask(art, &site, &from, MF_WCALL_EMIT, &rf, "same-class: from")) continue;
                int rc = pur_ask(art, &site, &to, MF_WCALL_EMIT, &r1, "same-class: renamed");
                const char *d = rc ? "the ask's refusal" : pur_diff(&rf, &r1);
                snprintf(m, sizeof m, "same-class: site %u (%s): renaming %s moved the reply "
                         "at %s", i, onm == 2 ? "PF" : onm ? "ON_MISS" : "ASSIGN", what,
                         d ? d : "-");
                pur_ok(!d, m);
            }
            /* ONE class move: n renamed while the miss keeps n's old text,
               so miss leaves the N class: the reply MAY differ (asserted as
               the class move it is, never as an equality) */
            mf_hooks a = base, b = base;
            a.miss = "n";
            b.miss = "n";
            b.n = "len";
            mf_wreply ra, rb2;
            int ca = pur_ask(art, &site, &a, MF_WCALL_EMIT, &ra, "class-move: before");
            int cb = pur_ask(art, &site, &b, MF_WCALL_EMIT, &rb2, "class-move: after");
            ad_moved += ca != cb || (!ca && pur_diff(&ra, &rb2));
        }
    snprintf(m, sizeof m, "same-class population: %ld STMT sites asked with EMIT; 0 holds "
             "nothing", ad_n);
    pur_ok(ad_n > 0, m);
    snprintf(m, sizeof m, "same-class population: the PF site is not rendered by the PF memchr "
             "row on E-stmt (%ld): no row in it reads a class narrower than every text", ad_pf);
    pur_ok(ad_pf == 1, m);
    printf("purity: framed fixtures: pair %ld refused %ld same-class %ld (pf %ld) "
           "class-move-moved %ld\n", pair_n, refused_n, ad_n, ad_pf, ad_moved);
}

static int purity_mode(void)
{
    static mf_arena ar = { NULL, pur_alloc };
    mf_site site[PUR_N];
    for (unsigned i = 0; i < PUR_N; i++) site[i] = pur_site(i);
    unsigned in_order[PUR_N], reversed[PUR_N], repeated[2 * PUR_N];
    for (unsigned i = 0; i < 2 * PUR_N; i++) {
        if (i < PUR_N) {
            in_order[i] = i;
            reversed[i] = PUR_N - 1 - i;
        }
        repeated[i] = i % PUR_N;
    }
    const struct { const char *name; const unsigned *seq; unsigned n; } orders[] = {
        { "in-order", in_order, PUR_N }, { "reversed", reversed, PUR_N },
        { "repeated", repeated, 2 * PUR_N },
    };
    static const uint8_t calls[2] = { MF_WCALL_NONE, MF_WCALL_DEFINE };
    mf_hooks hk = pur_hooks(0);
    char m[200];
    for (int rated = 0; rated < 2; rated++) {
        const mf_analysis *an = rated ? pur_rated() : NULL;
        mf_wreply fresh[2][PUR_N];
        for (unsigned i = 0; i < PUR_N; i++)
            for (int c = 0; c < 2; c++) {
                mf_art *art = art_begin(&ar, "pur", 0, NULL, an);
                snprintf(m, sizeof m, "%s: site %u: the fresh art's %s plan call refused",
                         rated ? "rated" : "none", i, c ? "framed" : "NONE");
                pur_ok(pur_ask(art, &site[i], &hk, calls[c], &fresh[c][i], m) == 0, m);
            }
        for (size_t o = 0; o < sizeof orders / sizeof orders[0]; o++) {
            mf_art *art = art_begin(&ar, "pur", 0, NULL, an);
            for (unsigned k = 0; k <= orders[o].n; k++) {
                for (unsigned i = 0; i < PUR_N; i++)
                    for (int c = 0; c < 2; c++) {
                        mf_wreply r;
                        int rc = pur_ask(art, &site[i], &hk, calls[c], &r, "interleaved");
                        const char *d = rc ? "the plan call refused" : pur_diff(&r, &fresh[c][i]);
                        snprintf(m, sizeof m, "%s %s: site %u after %u defines: %s %s differs "
                                 "from the fresh art's", rated ? "rated" : "none",
                                 orders[o].name, i, k, c ? "framed" : "NONE", d ? d : "-");
                        pur_ok(!d, m);
                    }
                if (k == orders[o].n) break;
                unsigned j = orders[o].seq[k];
                int rc = pur_define(art, &site[j]);
                if (rc) snprintf(m, sizeof m, "%s %s: site %u's define refused: %s",
                                 rated ? "rated" : "none", orders[o].name, j, mf_art_error(art));
                pur_ok(rc == 0, m);
            }
        }
    }
    pur_call_fixtures(&ar);
    /* THE STICKY-ERR CASE: breaker (a), FENCED (no reply after a refusal
       reaches an artifact); equal replies are asserted only once a later
       unit makes the refusal non-sticky */
    mf_art *art = art_begin(&ar, "pur", 0, NULL, NULL);
    pur_ok(pur_define(art, &site[0]) == 0, "sticky-err: the first define refused");
    mf_site bad = pur_refused();
    pur_ok(pur_define(art, &bad) != 0, "sticky-err: the two-NONE site's define was accepted");
    for (unsigned i = 0; i < PUR_N; i++)
        for (int c = 0; c < 2; c++) {
            mf_wreply r;
            snprintf(m, sizeof m, "sticky-err: site %u's %s plan call after a refused define "
                     "did not answer -1 (breaker (a) is FENCED by the refusal)", i,
                     c ? "framed" : "NONE");
            pur_ok(mf_wdecide(art, &site[i], &hk, calls[c], &r) == -1, m);
        }
    printf("checks passed: %ld\n", pur_pass);
    printf("checks failed: %ld\n", pur_fail);
    return pur_fail ? 1 : 0;
}

/* `r` as a hex dump of the whole struct (the control's print: every member,
 * present and future, and the padding the kit zeroes). */
static void pur_hex(const mf_wreply *r)
{
    const unsigned char *b = (const unsigned char *)r;
    for (size_t k = 0; k < sizeof *r; k++) printf("%02x", b[k]);
}

/* THE CONTROL's print: each site's NONE and framed replies after one define
 * of the next. */
static int purity_control_mode(void)
{
    static mf_arena ar = { NULL, a_alloc };
    mf_site site[PUR_N];
    mf_hooks hk = pur_hooks(0);
    for (unsigned i = 0; i < PUR_N; i++) site[i] = pur_site(i);
    for (int rated = 0; rated < 2; rated++)
        for (unsigned i = 0; i < PUR_N; i++) {
            mf_art *art = art_begin(&ar, "pur", 0, NULL,
                                       rated ? pur_rated() : NULL);
            mf_wreply r, f;
            if (pur_define(art, &site[(i + 1) % PUR_N]) ||
                mf_wdecide(art, &site[i], NULL, MF_WCALL_NONE, &r) ||
                mf_wdecide(art, &site[i], &hk, MF_WCALL_DEFINE, &f)) {
                printf("%s site %u: refused: %s\n", rated ? "rated" : "none", i,
                       mf_art_error(art));
                continue;
            }
            printf("%s site %u: none=", rated ? "rated" : "none", i);
            pur_hex(&r);
            printf(" framed=");
            pur_hex(&f);
            printf(" (%s %s)\n", f.frame_row, r.path);
            /* 3.0b: the STMT frames' one-call (EMIT) replies, so Table E's
               E-stmt row and the composer's search rows print too */
            static const uint8_t kinds[2] = { MF_SK_DFA_SCAN, MF_SK_REPORT };
            for (int k = 0; k < 2; k++) {
                mf_site st = pur_stmt(i, 0, kinds[k], NULL);
                mf_hooks th = pur_text_hooks(0);
                mf_wreply e;
                printf("%s site %u stmt%d: ", rated ? "rated" : "none", i, k);
                if (mf_wdecide(art, &st, &th, MF_WCALL_EMIT, &e)) printf("refused\n");
                else { pur_hex(&e); printf(" (%s)\n", e.frame_row); }
            }
        }
    {
        mf_art *art = art_begin(&ar, "pur", 0, NULL, NULL);
        mf_site st = pur_pf_site();
        mf_hooks th = pur_pf_hooks();
        mf_wreply e;
        printf("pf site: ");
        if (mf_wdecide(art, &st, &th, MF_WCALL_EMIT, &e)) printf("refused\n");
        else { pur_hex(&e); printf(" (%s)\n", e.frame_row); }
    }
    return 0;
}

int main(int argc, char **argv)
{
    if (argc < 2) { fputs("usage: arm_fixtures OUTDIR [--perturb] [--query] | --gate [--gate-only CASE] | "
                          "--fd-site SITE [--fd-set FILE] [--fd-an DIGEST] | --finder-rows | --hash | "
                          "--site-text ID [CLS] | --site-parts ID [CLS] | --hash-text FILE|- | --facts ID [CLS] | "
                          "--purity | --purity-control\n", stderr); return 2; }
    if (!strcmp(argv[1], "--fd-site") && argc > 2) {
        const char *set = NULL, *opts = NULL, *digest = NULL;
        for (int i = 3; i + 1 < argc; i += 2) {
            if (!strcmp(argv[i], "--fd-set")) set = argv[i + 1];
            else if (!strcmp(argv[i], "--opts")) opts = argv[i + 1];
            else if (!strcmp(argv[i], "--fd-an")) digest = argv[i + 1];
        }
        return fd_site_mode(argv[2], set, opts, digest);
    }
    if (!strcmp(argv[1], "--finder-rows")) return finder_rows_mode();
    if (!strcmp(argv[1], "--streams")) return streams_mode();
    if (!strcmp(argv[1], "--hash")) return hash_mode();
    if (!strcmp(argv[1], "--site-text") && argc > 2) return site_text_mode(argv[2], argc > 3 ? argv[3] : NULL);
    if (!strcmp(argv[1], "--site-parts") && argc > 2) return site_parts_mode(argv[2], argc > 3 ? argv[3] : NULL);
    if (!strcmp(argv[1], "--hash-text") && argc > 2) return hash_text_mode(argv[2]);
    if (!strcmp(argv[1], "--facts") && argc > 2) return facts_mode(argv[2], argc > 3 ? argv[3] : NULL);
    if (!strcmp(argv[1], "--purity")) return purity_mode();
    if (!strcmp(argv[1], "--purity-control")) return purity_control_mode();
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
    if (only && !strncmp(only, "fd-", 3)) {         /* the finder fixtures */
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

    /* R-38 Part D (part_d.md §5.1.1 D2 [r2pd P10]): fn-every-pos's witness,
     * a REQUIRED run with NO findable position (two positions of the digits,
     * each WIDE): P0 verifies it scan-less (K66), its derived part has no
     * RUN term, and the offset-skip function's BODY is every-pos; and its
     * CONTROL, the same run with position 1 the one byte 'a' (findable): the
     * scan is 'a', the part a RUN term and a tableless SET term, fn-memchr */
    for (int findable = 0; findable < 2; findable++) {
        static mf_pred wp[1], wr[1];
        static mf_walt wa;
        static mf_wspan ww;
        memset(wr, 0, sizeof wr);
        memset(&ww, 0, sizeof ww);
        ww.len = 2;
        ww.verify = MF_VERIFY_NO;
        ww.core = MF_CORE_STATED;
        ww.core_len = 2;
        for (unsigned b = '0'; b <= '9'; b++) set_add(ww.set[0], b);
        if (findable) set_add(ww.set[1], 'a');
        else for (unsigned b = '0'; b <= '9'; b++) set_add(ww.set[1], b);
        wa = (mf_walt){ MF_ENTRY_NONE, 1, &ww };
        wr[0].nalt = 1;
        wr[0].alts = &wa;
        wr[0].wfloor = MF_WFLOOR_SUBJECT;
        wr[0].need = MF_REQUIRED;
        wr[0].plan_hint = MF_NO_PRED;
        wr[0].span_class = MF_SPAN_PRESENCE;
        memset(wp, 0, sizeof wp);
        wp[0].fn_ref = 1;               /* the derived run part: its name only */
        s = pre_site(wp, 1, -1);
        s.body = MF_BODY_ONESHOT;
        s.site_kind = MF_SK_VM_ATTEMPT;
        s.pspans = wr;
        s.npspan = 1;
        s.pres_proof = (mf_pres_proof){ .byte = -1, .stated = 1 };
        bad |= render(dir, findable ? "pre-wide-findable" : "pre-wide-every-pos", &s, "rx_reqrun");
    }

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
