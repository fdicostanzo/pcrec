/* tests/memfn/proof_check.c — [MEMFN] R-26.1-R-26.5 (lane r26z1, MF_SITE_ABI
 * 18), as D172 S2 commit 6 (lane wsc6, MF_SITE_ABI 20) left them: the kit's
 * checks for span 0's and a context stop's class, the REPORT kind and the
 * per-offset proof (docs/design/kit_proof.md rev 2.1 §4.1-§4.3, §6.4;
 * memfn/docs/requests.md R-26), and the window site's RENDERER INTERFACE
 * refusal (R-29; the kit manager's R1). Span 0's prefix facts, the context
 * spans, the absent rule, `consumable`, `read_floor` and `consumer` left the
 * site at that commit, and their checks with them. It reads the kit through
 * memfn.h only (no kit.h).
 *
 *   A  REFUSALS: one site per rule (`span_class` UNSTATED, PRESENCE or on a
 *      reverse FIND; a CONTEXT pred reading its candidate; the REPORT kind's
 *      OPTIONAL term, missing span 0, and a well-formed one, which no row
 *      serves stated in terms (since D172 S3 a REPORT site is a window site,
 *      the family's E-find row's); a window site stating each renderer-interface
 *      field), each held to the field its refusal names in backquotes,
 *      beside ACCEPT controls of every shape.
 *   B  THE CLASS: proven[] at negative offsets, inside span 0, after it,
 *      with the copies proven0 == proven[0] and proven_prev == proven[-1];
 *      the expected sets are member strings (never a bitset built the way the
 *      input's is).
 *   C  C-PROOF and the GENERATED FAMILY (`--gen DIR`): a seeded space of
 *      forward FIND sites (span 0, OPTIONAL terms among them; context stops;
 *      FUNC sites), each defined and used on its own art, its class asked
 *      again under -fmemfn-simd and under each level's deny and held EQUAL
 *      (C-PROOF), its text and its GENERATED facts written to
 *      DIR/proof_sites.c for tests/memfn/proof_run.c, the byte-loop oracle.
 *      The family adds REPORT sites stated in terms (span 0 of 1..3 REQUIRED
 *      terms, the offset-skip FUNC shape, a term below the candidate), each
 *      REFUSED, naming `site_kind` REPORT: since D172 S3 RPT, the row that
 *      served them on an art previewing "R-26.6", is retired with the
 *      preview (window_site.md §4), and REPORT is a window site's kind (its
 *      proof is held by G2's window family and pcrec's C14).
 *   D  THE REPORT KIND SINCE S3: the two-offset-term REPORT site RPT served
 *      through S2 is refused on every art.
 *
 * Expected outcomes are written here from the request's text, never read
 * from the kit's sources. Prints `checks passed:`/`checks failed:`.
 */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "memfn.h"
#include "proof_meta.h"

_Static_assert(PM_NPROOF == MF_MAX_FWD - MF_PROOF_LO, "proof_meta.h's proof range");
_Static_assert(PM_PROOF_LO == MF_PROOF_LO, "proof_meta.h's proof range");

static int passed, failed;

static void verdict(const char *name, const char *why)
{
    if (why && *why) { printf("FAIL: %s: %s\n", name, why); failed++; }
    else             { printf("ok   %s\n", name); passed++; }
}

/* ---- the arena and a text sink ------------------------------------------- */

static void *a_alloc(void *u, size_t n)
{
    (void)u;
    void *p = calloc(1, n ? n : 1);
    if (!p) { perror("calloc"); exit(2); }
    return p;
}
static mf_arena arena = { NULL, a_alloc };

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
    if (n < 0 || n >= (int)sizeof buf) { fputs("proof_check: text too long\n", stderr); exit(2); }
    text_put(u, buf, (size_t)n);
}
static int s_cmt_open(void *u, int tier) { (void)u; (void)tier; return 0; }
static void s_cmt_close(void *u) { (void)u; }
/* The body of a C string literal (the quotes are the kit's): every byte
 * outside printable ASCII, and `\\` `"` `?`, as a three-digit octal escape. */
static void s_cstr(void *u, const uint8_t *bytes, size_t len)
{
    for (size_t i = 0; i < len; i++) {
        char e[8];
        unsigned b = bytes[i];
        if (b >= 0x20 && b < 0x7F && b != '\\' && b != '"' && b != '?')
            snprintf(e, sizeof e, "%c", (char)b);
        else
            snprintf(e, sizeof e, "\\%03o", b);
        text_put(u, e, strlen(e));
    }
}
static mf_sink sink_of(Text *t)
{
    mf_sink s = { 0 };
    s.u = t;
    s.puts = s_puts;
    s.vprintf = s_vprintf;
    s.cmt_open = s_cmt_open;
    s.cmt_close = s_cmt_close;
    s.cstr = s_cstr;
    return s;
}

/* ---- site builders ------------------------------------------------------- */

static void set_of(uint8_t set[32], const char *members)
{
    memset(set, 0, 32);
    for (const char *m = members; *m; m++)
        set[(unsigned char)*m >> 3] |= (uint8_t)(1u << ((unsigned char)*m & 7));
}

static void t_set(mf_term *t, int off, const char *members, mf_need need)
{
    memset(t, 0, sizeof *t);
    t->kind = MF_T_SET;
    t->offset = off;
    set_of(t->set, members);
    t->ppm_hi = MF_PPM_FULL;
    t->need = need;
}

static void t_run(mf_term *t, int off, const char *run, mf_need need)
{
    memset(t, 0, sizeof *t);
    t->kind = MF_T_RUN;
    t->offset = off;
    t->run = (const uint8_t *)run;
    t->run_len = (uint32_t)strlen(run);
    t->ppm_hi = MF_PPM_FULL;
    t->need = need;
}

/* A forward FIND / STMT / ASSIGN site whose span 0 is one SET term `a` at 0,
 * stated BOUNDED (the renderer interface, as the window family's translation
 * and G2 state it). */
static mf_site span_site(void)
{
    mf_site s;
    memset(&s, 0, sizeof s);
    s.abi = MF_SITE_ABI;
    s.form = MF_FORM_STMT;
    s.op = MF_OP_FIND;
    s.handoff = MF_H_ASSIGN;
    s.empty = MF_EMPTY_MISS;
    s.on_miss_leaves = 1;       /* `on_miss` returns the miss (stmt_hooks) */
    s.use = MF_USE_POSITION;
    s.ret_pred = MF_NO_PRED;
    s.span_hi = MF_SPAN_UNBOUNDED;
    s.cand_ppm_hi = MF_PPM_FULL;
    s.policy = MF_P_PORTABLE_ONLY;
    s.body = MF_BODY_ONESHOT;
    s.site_kind = MF_SK_DFA_SCAN;
    s.pred.nterm = 1;
    s.pred.need = MF_REQUIRED;
    s.pred.plan_hint = MF_NO_PRED;
    t_set(&s.pred.term[0], 0, "a", MF_REQUIRED);
    s.pred.span_class = MF_SPAN_BOUNDED;
    return s;
}

/* A context stop: MLINE's shape, `{\n\r}` at -1 (two members: the routed
 * one-byte row D1c takes MLINE's own one-byte stop only with its hooks,
 * src/gen/emit_dfa.c find_hooks). A read below the subject fails its term. */
static mf_site stop_site(void)
{
    mf_site s = span_site();
    t_set(&s.pred.term[0], -1, "\n\r", MF_REQUIRED);
    s.pred.span_class = MF_SPAN_CONTEXT;
    s.empty = MF_EMPTY_AT_N;
    s.site_kind = MF_SK_DFA_ATTEMPT;
    return s;
}

/* A WINDOW site stating its facts only (R-29's table): one alternative with
 * no entry fact, span 0 `{0: a}` verify YES, core all, the floor SUBJECT;
 * its `pred` carries the FUNC name and nothing else. */
static mf_wspan win_span;
static mf_walt win_alt;
static mf_site win_site(void)
{
    mf_site s = span_site();
    memset(&s.pred, 0, sizeof s.pred);
    memset(&win_span, 0, sizeof win_span);
    win_span.start = 0;
    win_span.len = 1;
    win_span.verify = MF_VERIFY_YES;
    win_span.core = MF_CORE_STATED;
    win_span.core_lo = 0;
    win_span.core_len = 1;
    set_of(win_span.set[0], "a");
    win_alt.entry = MF_ENTRY_NONE;
    win_alt.nspan = 1;
    win_alt.spans = &win_span;
    s.nalt = 1;
    s.alts = &win_alt;
    s.wfloor = MF_WFLOOR_SUBJECT;
    return s;
}

static mf_hooks stmt_hooks(void)
{
    mf_hooks h = { 0 };
    h.s = "subject";
    h.n = "n";
    h.lo = "pos";
    h.result = "r";
    h.miss = MF_MISS_N;
    h.on_miss = "return n;";
    h.indent = "    ";
    return h;
}

/* ---- A: refusals --------------------------------------------------------- */

/* Defines `s` on a fresh art: NULL and the error text in *err on a refusal,
 * the form id otherwise. */
static const char *define_on(const mf_site *s, char *err, size_t n, mf_class *cls,
                             char *row)
{
    static char form[48];
    mf_art *art = mf_art_begin(&arena, "rx", s->policy, s->denies, NULL, NULL);
    Text f = { 0 };
    mf_sink sf = sink_of(&f);
    mf_hooks h = stmt_hooks();
    uint32_t handle = 0;
    err[0] = 0;
    if (!art) { snprintf(err, n, "mf_art_begin failed"); return NULL; }
    if (mf_define(art, s, &h, &sf, &handle)) {
        snprintf(err, n, "%s", mf_art_error(art) ? mf_art_error(art) : "(no text)");
        free(f.p);
        return NULL;
    }
    mf_result r;
    mf_defined(art, handle, &r);
    if (cls) *cls = r.cls;
    if (row) snprintf(row, 16, "%s", r.row);
    snprintf(form, sizeof form, "%s", r.form_id);
    free(f.p);
    return form;
}

static const char *define(const mf_site *s, char *err, size_t n, mf_class *cls)
{
    return define_on(s, err, n, cls, NULL);
}

/* The case refuses, naming `field` in backquotes (or, for a field the text
 * cannot name, carrying `text`), and mf_ask refuses it too. */
static void refuse(const char *name, const mf_site *s, const char *needle)
{
    char err[512], why[640] = "";
    if (define(s, err, sizeof err, NULL)) {
        snprintf(why, sizeof why, "rendered; expected a refusal naming %s", needle);
    } else if (!strstr(err, needle)) {
        snprintf(why, sizeof why, "refused without naming %s: %s", needle, err);
    } else {
        mf_art *art = mf_art_begin(&arena, "rx", s->policy, s->denies, NULL, NULL);
        mf_hooks h = stmt_hooks();
        mf_class c;
        if (!mf_ask(art, s, &h, &c)) snprintf(why, sizeof why, "mf_ask answered it");
    }
    char label[160];
    snprintf(label, sizeof label, "A refuse %s", name);
    verdict(label, why);
}

static void accept(const char *name, const mf_site *s)
{
    char err[512], why[640] = "";
    if (!define(s, err, sizeof err, NULL)) snprintf(why, sizeof why, "refused: %s", err);
    char label[160];
    snprintf(label, sizeof label, "A accept %s", name);
    verdict(label, why);
}

static void family_a(void)
{
    mf_site s;

    /* controls: every shape the refusals below perturb, accepted as stated */
    s = span_site();
    accept("span 0 BOUNDED", &s);
    s = stop_site();
    accept("context stop CONTEXT", &s);
    s = win_site();
    accept("a window site stating its facts only", &s);
    s = win_site();
    s.pred.plan_hint = MF_NO_PRED;
    accept("a window site with plan_hint MF_NO_PRED (no term named)", &s);

    /* R-26.1/R-26.2: the class of a forward FIND's `pred` */
    s = span_site();
    s.pred.span_class = MF_SPAN_UNSTATED;
    refuse("span_class UNSTATED on a forward FIND", &s, "`span_class`");
    s = span_site();
    s.pred.span_class = MF_SPAN_PRESENCE;
    refuse("span_class PRESENCE on a forward FIND", &s, "`span_class`");
    s = span_site();
    s.reverse = 1;
    refuse("span_class on a reverse FIND", &s, "`span_class`");
    s = stop_site();
    t_set(&s.pred.term[0], 0, "x", MF_REQUIRED);
    refuse("a CONTEXT pred reading its candidate", &s, "`span_class`");

    /* R-26.3: REPORT */
    s = span_site();
    s.site_kind = MF_SK_REPORT;
    s.pred.nterm = 2;
    t_set(&s.pred.term[1], 1, "b", MF_OPTIONAL);
    refuse("REPORT with one OPTIONAL span-0 term", &s, "`need`");
    s = stop_site();
    s.site_kind = MF_SK_REPORT;
    refuse("REPORT with no BOUNDED span 0", &s, "BOUNDED");
    s = span_site();
    s.site_kind = MF_SK_REPORT;
    refuse("REPORT well-formed, stated in terms: no row (a REPORT site is a window site)", &s,
           "`site_kind` REPORT");
    s = span_site();
    s.site_kind = MF_SK_REPORT + 1;
    refuse("site_kind outside mf_site_kind", &s, "`site_kind`");

    /* D172 S2 commit 6 (R1): a window site states no renderer-interface
       field, each refused naming it */
    s = win_site();
    s.pred.nterm = 1;
    t_set(&s.pred.term[0], 0, "a", MF_REQUIRED);
    refuse("a window site stating a term", &s, "`pred.nterm`");
    s = win_site();
    s.pred.need = MF_REQUIRED;
    refuse("a window site stating pred.need", &s, "`pred.need`");
    s = win_site();
    s.pred.plan_hint = 1;
    refuse("a window site stating plan_hint", &s, "`plan_hint`");
    s = win_site();
    s.pred.plan_pos = 1;
    refuse("a window site stating plan_pos", &s, "`plan_pos`");
    s = win_site();
    s.pred.rank_n = 1;
    refuse("a window site stating a ranking", &s, "`rank_n`");
    s = win_site();
    s.pred.span_class = MF_SPAN_BOUNDED;
    refuse("a window site stating span_class", &s, "`span_class`");
    s = win_site();
    s.end_back = 1;
    refuse("a window site stating end_back", &s, "`end_back`");
}

/* ---- B: the class -------------------------------------------------------- */

/* "" iff `bits` holds exactly the bytes of `members` ("ALL": every byte). */
static const char *expect(const uint8_t bits[32], const char *members)
{
    static char why[96];
    int all = !strcmp(members, "ALL");
    for (int x = 0; x < 256; x++) {
        int want = all || (x != 0 && strchr(members, x) != NULL);
        int got = bits[x >> 3] >> (x & 7) & 1;
        if (want != got) {
            snprintf(why, sizeof why, "byte 0x%02x %s", x,
                     got ? "proven, not expected" : "expected, not proven");
            return why;
        }
    }
    return "";
}

static void family_b(void)
{
    mf_site s = span_site();
    t_run(&s.pred.term[0], 0, "ab", MF_REQUIRED);
    s.pred.nterm = 4;
    t_set(&s.pred.term[1], 2, "cd", MF_OPTIONAL);
    t_set(&s.pred.term[2], -2, "x", MF_REQUIRED);
    t_set(&s.pred.term[3], 3, "yz", MF_REQUIRED);
    mf_class cls;
    char err[512];
    const char *form = define(&s, err, sizeof err, &cls);
    if (!form) { verdict("B the class site defines", err); return; }
    static const struct { int d; const char *set; } want[] = {
        { -8, "ALL" }, { -3, "ALL" }, { -2, "x" }, { -1, "ALL" }, { 0, "a" },
        { 1, "b" }, { 2, "cd" }, { 3, "yz" }, { 4, "ALL" }, { MF_MAX_FWD - 1, "ALL" },
    };
    for (size_t i = 0; i < sizeof want / sizeof want[0]; i++) {
        char name[96];
        snprintf(name, sizeof name, "B proven[%d] (%s)", want[i].d, form);
        verdict(name, expect(cls.proven[want[i].d - MF_PROOF_LO], want[i].set));
    }
    verdict("B proven0 is proven[0]", memcmp(cls.proven0, cls.proven[-MF_PROOF_LO], 32)
                                     ? "differs" : "");
    verdict("B proven_prev is proven[-1]",
            memcmp(cls.proven_prev, cls.proven[-1 - MF_PROOF_LO], 32) ? "differs" : "");
    verdict("B class version", cls.v == MF_CLASS_V ? "" : "not MF_CLASS_V");
    s = stop_site();
    form = define(&s, err, sizeof err, &cls);
    if (!form) { verdict("B context stop defines", err); return; }
    verdict("B context stop: proven[-1] its set", expect(cls.proven[-1 - MF_PROOF_LO], "\n\r"));
    verdict("B context stop: proven_prev its set", expect(cls.proven_prev, "\n\r"));
    verdict("B context stop: proven0 nothing", expect(cls.proven0, "ALL"));
}

/* ---- C: C-PROOF and the generated family --------------------------------- */

static unsigned long long rng = 0x9E3779B97F4A7C15ull;
static unsigned rnd(unsigned n)
{
    rng ^= rng << 13;
    rng ^= rng >> 7;
    rng ^= rng << 17;
    return (unsigned)(rng % n);
}

static const char ALPHA[] = "abcd";

/* Random members of ALPHA (1..3 of them) into `out`. */
static void rand_members(char *out)
{
    int k = 1 + (int)rnd(3), n = 0;
    for (int i = 0; i < 4 && n < k; i++)
        if (rnd(2)) out[n++] = ALPHA[i];
    if (!n) out[n++] = ALPHA[rnd(4)];
    out[n] = 0;
}

static char runbuf[4096][8];
static int nrun;

static void rand_term(mf_term *t, int off, mf_need need, int allow_run)
{
    if (allow_run && rnd(3) == 0) {
        char *r = runbuf[nrun++ % 4096];
        int len = 1 + (int)rnd(2);
        for (int j = 0; j < len; j++) r[j] = ALPHA[rnd(3)];
        r[len] = 0;
        t_run(t, off, r, need);
    } else {
        char m[8];
        rand_members(m);
        t_set(t, off, m, need);
    }
}

static mf_need rand_need(void) { return rnd(3) ? MF_REQUIRED : MF_OPTIONAL; }

/* Site `i` of the family, into *s. */
static void family_site(unsigned i, mf_site *s)
{
    *s = span_site();
    unsigned shape = i % 4;
    if (shape == 2) {                            /* a context stop */
        *s = stop_site();
        if (rnd(2)) t_run(&s->pred.term[0], -2, rnd(2) ? "ab" : "a\n", MF_REQUIRED);
        else t_set(&s->pred.term[0], -1, rnd(2) ? "ab" : "b\n", MF_REQUIRED);
        return;
    }
    if (shape == 3) {                            /* a FUNC / RETURN site */
        s->form = MF_FORM_FUNC;
        s->handoff = MF_H_RETURN;
        s->on_miss_leaves = 0;
        s->pred.fn_ref = 1;
        if (rnd(2)) {
            /* the offset-skip function's shape (ofsskip.c, its vrun SIMD rows
               under -fmemfn-simd): a RUN term scanned at its first position,
               one-member SET terms after it, no context span */
            char *r = runbuf[nrun++ % 4096];
            int len = 2 + (int)rnd(2);
            for (int j = 0; j < len; j++) r[j] = ALPHA[rnd(3)];
            r[len] = 0;
            unsigned nt = 1 + rnd(3);
            s->pred.nterm = (uint8_t)nt;
            t_run(&s->pred.term[0], 0, r, MF_REQUIRED);
            for (unsigned t = 1; t < nt; t++) {
                char m[2] = { ALPHA[rnd(4)], 0 };
                t_set(&s->pred.term[t], len + (int)rnd(2), m, rand_need());
            }
            s->pred.plan_hint = 0;
            return;
        }
    }
    unsigned nt = 1 + rnd(3);
    s->pred.nterm = (uint8_t)nt;
    rand_term(&s->pred.term[0], 0, MF_REQUIRED, 1);
    /* one one-member SET term alone is the routed one-byte row's (D1), whose
       pick is pcrec's tabled site (find_hooks): this family states no table */
    if (nt == 1 && (s->pred.term[0].kind == MF_T_SET || s->pred.term[0].run_len == 1))
        t_set(&s->pred.term[0], 0, rnd(2) ? "ab" : "bcd", MF_REQUIRED);
    for (unsigned t = 1; t < nt; t++) rand_term(&s->pred.term[t], (int)rnd(3), rand_need(), 1);
    if (shape == 0 && rnd(4)) {     /* a term below the candidate (once a context item's) */
        mf_term *t = &s->pred.term[s->pred.nterm++];
        if (rnd(3) == 0) t_run(t, -2, rnd(2) ? "xa" : "ab", rand_need());
        else rand_term(t, -1 - (int)rnd(2), rand_need(), 0);
    }
}

static const char *fn_name(void *u, uint32_t ref) { (void)ref; return u; }

/* The class of `s` asked under policy `policy` and options `opts`. */
static int ask_under(const mf_site *s0, const mf_hooks *h0, uint32_t policy, const char *opts,
                     mf_class *c)
{
    mf_site s = *s0;
    s.policy = policy;
    s.opts = opts;
    mf_art *art = mf_art_begin(&arena, "rx", policy, s.denies, NULL, NULL);
    return mf_ask(art, &s, h0, c);
}

static void put_bytes(FILE *o, const uint8_t *b, size_t n)
{
    fputs("{", o);
    for (size_t i = 0; i < n; i++) fprintf(o, "%s%u", i ? "," : "", b[i]);
    fputs("}", o);
}

static void put_pred(FILE *o, const mf_pred *p, int context)
{
    fprintf(o, "{ %u, {", p->nterm);
    for (unsigned t = 0; t < p->nterm; t++) {
        const mf_term *tm = &p->term[t];
        uint8_t run[8] = { 0 };
        if (tm->kind == MF_T_RUN) memcpy(run, tm->run, tm->run_len);
        fprintf(o, "%s{ %d, %d, %u, ", t ? ", " : "", tm->kind == MF_T_RUN ? PM_RUN : PM_SET,
                tm->offset, tm->kind == MF_T_RUN ? tm->run_len : 1u);
        put_bytes(o, tm->set, 32);
        fputs(", ", o);
        put_bytes(o, run, 8);
        fprintf(o, ", %d }", tm->need == MF_REQUIRED ? PM_REQ : PM_OPT);
    }
    fprintf(o, "}, %d, %d, %d }", p->need == MF_REQUIRED ? PM_REQ : PM_OPT, context,
            context ? PM_FAILS : 0);
}

/* ---- the REPORT sites stated in terms (refused since D172 S3) ------------ */

static void r_set(mf_term *t, int off, const char *members)
{
    t_set(t, off, members, MF_REQUIRED);
}

static void r_run(mf_term *t, int off, const char *run)
{
    t_run(t, off, run, MF_REQUIRED);
}

/* REPORT site `i`: every term REQUIRED (R-26.3), span 0 BOUNDED. Shapes: 0
 * span 0 alone, 1 the offset-skip FUNC shape, 2 span 0 with one term below
 * its candidate (once a context item's). */
static void family_report(unsigned i, mf_site *s)
{
    *s = span_site();
    s->site_kind = MF_SK_REPORT;
    unsigned shape = i % 3;
    char m[8];
    if (shape == 1) {
        s->form = MF_FORM_FUNC;
        s->handoff = MF_H_RETURN;
        s->on_miss_leaves = 0;
        s->pred.fn_ref = 1;
        char *r = runbuf[nrun++ % 4096];
        int len = 2 + (int)rnd(2);
        for (int j = 0; j < len; j++) r[j] = ALPHA[rnd(3)];
        r[len] = 0;
        unsigned nt = 1 + rnd(3);
        s->pred.nterm = (uint8_t)nt;
        r_run(&s->pred.term[0], 0, r);
        for (unsigned t = 1; t < nt; t++) {
            char one[2] = { ALPHA[rnd(4)], 0 };
            r_set(&s->pred.term[t], len + (int)rnd(2), one);
        }
        s->pred.plan_hint = 0;
        return;
    }
    unsigned nt = 1 + rnd(3);
    s->pred.nterm = (uint8_t)nt;
    for (unsigned t = 0; t < nt; t++) {
        int off = t ? (int)rnd(4) : 0;
        if (rnd(3) == 0) {
            char *r = runbuf[nrun++ % 4096];
            int len = 1 + (int)rnd(2);
            for (int j = 0; j < len; j++) r[j] = ALPHA[rnd(3)];
            r[len] = 0;
            r_run(&s->pred.term[t], off, r);
        } else {
            rand_members(m);
            r_set(&s->pred.term[t], off, m);
        }
    }
    if (shape == 0) return;
    rand_members(m);
    r_set(&s->pred.term[s->pred.nterm++], -1 - (int)rnd(2), m);
}

/* One site's define, use and end on a fresh art named `pfx`: 0, or -1 with
 * the art's error in *err. */
static int render_site(const mf_site *s, const mf_hooks *h, const char *pfx,
                       Text *def, Text *use, mf_result *r, const char **err)
{
    mf_art *art = mf_art_begin(&arena, pfx, s->policy, s->denies, NULL, NULL);
    mf_sink sd = sink_of(def), su = sink_of(use);
    uint32_t handle;
    *err = "mf_art_begin failed";
    if (!art) return -1;
    if (mf_define(art, s, h, &sd, &handle) || mf_flush_helpers(art, &sd) ||
        (s->form == MF_FORM_FUNC ? mf_call(art, handle, h, &su)
                                 : mf_use(art, handle, h, &su, r)) ||
        mf_defined(art, handle, r) || mf_art_end(art, NULL)) {
        *err = mf_art_error(art) ? mf_art_error(art) : "refused";
        return -1;
    }
    return 0;
}

static int family_c(const char *dir, unsigned nsites, unsigned nreport)
{
    char path[1024];
    snprintf(path, sizeof path, "%s/proof_sites.c", dir);
    FILE *o = fopen(path, "w");
    if (!o) { perror(path); return 2; }
    Text files = { 0 }, bodies = { 0 };
    fputs("/* generated by tests/memfn/proof_check.c --gen: the kit's text for the\n"
          " * proof family, and the facts each site was generated with */\n"
          "#include <stddef.h>\n#include <stdint.h>\n#include <string.h>\n#include \"proof_meta.h\"\n\n", o);
    unsigned ok = 0, cproof = 0, shapes[4] = { 0 }, nform[16] = { 0 };
    unsigned rrefused = 0;
    char forms[16][48] = { { 0 } };
    /* the REPORT sites stated in terms: each refused (D172 S3) */
    for (unsigned i = 0; i < nreport; i++) {
        mf_site s;
        family_report(i, &s);
        char fn[32], name[96];
        snprintf(fn, sizeof fn, "pm_r%u", i);
        Text def = { 0 }, use = { 0 };
        mf_hooks h = stmt_hooks();
        h.fn_name = fn_name;
        h.u = fn;
        mf_result r;
        const char *err;
        if (render_site(&s, &h, "pr", &def, &use, &r, &err) == 0 ||
            !strstr(err, "`site_kind` REPORT")) {
            snprintf(name, sizeof name, "C REPORT site %u stated in terms refused", i);
            verdict(name, "rendered, or refused for another reason");
        } else {
            rrefused++;
        }
        free(def.p);
        free(use.p);
    }
    fputs("const pm_site pm_sites[] = {\n", o);
    for (unsigned i = 0; i < nsites; i++) {
        int stop = i % 4 == 2;
        mf_site s;
        family_site(i, &s);
        char fn[32];
        snprintf(fn, sizeof fn, "pm_f%u", i);
        char *pfx = a_alloc(NULL, 16);      /* one art per site: names its own */
        snprintf(pfx, 16, "p%u", i);
        Text def = { 0 }, use = { 0 };
        mf_hooks h = stmt_hooks();
        h.fn_name = fn_name;
        h.u = fn;
        if (stop) {                             /* a stop's range reaches n */
            h.miss = "((size_t)-1)";
            h.on_miss = "return (size_t)-1;";
        }
        mf_result r;
        const char *err;
        char name[96];
        snprintf(name, sizeof name, "C site %u defines and uses", i);
        if (render_site(&s, &h, pfx, &def, &use, &r, &err)) {
            verdict(name, err);
            free(def.p);
            free(use.p);
            continue;
        }
        ok++;
        for (unsigned f = 0; f < 16; f++) {    /* the forms the family reaches */
            if (!forms[f][0]) { snprintf(forms[f], sizeof forms[f], "%s", r.form_id); }
            if (!strcmp(forms[f], r.form_id)) { nform[f]++; break; }
        }
        shapes[i % 4]++;
        if (def.p) text_put(&files, def.p, def.len);
        char head[160];
        snprintf(head, sizeof head, "static unsigned long pm_s%u(const unsigned char *subject, "
                 "unsigned long n, unsigned long pos)\n{\n", ok - 1);
        text_put(&bodies, head, strlen(head));
        if (s.form == MF_FORM_FUNC) {
            s_puts(&bodies, "    return ");
            if (use.p) text_put(&bodies, use.p, use.len);
            s_puts(&bodies, ";\n}\n\n");
        } else {
            s_puts(&bodies, "    size_t r;\n");
            if (use.p) text_put(&bodies, use.p, use.len);
            s_puts(&bodies, "    return r;\n}\n\n");
        }
        free(def.p);
        free(use.p);
        /* C-PROOF: the class under -fmemfn-simd, and with each SIMD row denied,
           equals the SIMD-off class at every offset (LAYER-INVARIANT) */
        mf_class off, on, w16, w32;
        snprintf(name, sizeof name, "C site %u C-PROOF", i);
        if (ask_under(&s, &h, MF_P_PORTABLE_ONLY, NULL, &off) ||
            ask_under(&s, &h, 0, NULL, &on) ||
            ask_under(&s, &h, 0, "no-vrun-w32", &w16) ||
            ask_under(&s, &h, 0, "no-vrun-w16", &w32))
            verdict(name, "a layer refuses the site");
        else if (memcmp(off.proven, r.cls.proven, sizeof off.proven))
            verdict(name, "mf_ask's class is not the define's");
        else if (memcmp(off.proven, on.proven, sizeof off.proven) ||
                 memcmp(off.proven, w16.proven, sizeof off.proven) ||
                 memcmp(off.proven, w32.proven, sizeof off.proven))
            verdict(name, "proven[] differs across the layers");
        else
            cproof++;
        /* the facts, then the claim */
        fprintf(o, "  { \"%u\", %d, 1, {\n    ", i, stop);
        put_pred(o, &s.pred, s.pred.span_class == MF_SPAN_CONTEXT);
        fputs(" },\n    {", o);
        for (unsigned d = 0; d < MF_MAX_FWD - MF_PROOF_LO; d++) {
            if (d) fputs(",", o);
            put_bytes(o, r.cls.proven[d], 32);
        }
        fprintf(o, "},\n    \"abcdx\\n\", 6 },\n");
    }
    fputs("};\n\n", o);
    if (files.p) fputs(files.p, o);
    if (bodies.p) fputs(bodies.p, o);
    fputs("const pm_fn pm_fns[] = {\n", o);
    for (unsigned i = 0; i < ok; i++) fprintf(o, "    pm_s%u,\n", i);
    fprintf(o, "};\nconst unsigned pm_nsites = %u;\n", ok);
    fclose(o);
    free(files.p);
    free(bodies.p);
    char name[128];
    snprintf(name, sizeof name, "C every generated site renders (%u of %u)", ok, nsites);
    verdict(name, ok == nsites ? "" : "a site was refused");
    snprintf(name, sizeof name, "C C-PROOF held on %u sites", cproof);
    verdict(name, cproof == ok ? "" : "a site's class moved with the layer");
    snprintf(name, sizeof name, "C REPORT stated in terms: %u of %u refused (floor 100)",
             rrefused, nreport);
    verdict(name, rrefused == nreport && nreport >= 100 ? ""
                  : "a REPORT site rendered, or the population is short");
    printf("C family: %u span+below, %u span, %u stop, %u func; forms:", shapes[0],
           shapes[1], shapes[2], shapes[3]);
    unsigned nf = 0;
    for (unsigned f = 0; f < 16 && forms[f][0]; f++) {
        if (nform[f]) nf++;
        printf(" %s %u", forms[f], nform[f]);
    }
    printf("\n");
    /* K35: the family reaches the generic row and at least one other (the
       class every row computes, held at every candidate) */
    snprintf(name, sizeof name, "C the family reaches %u forms (floor 2)", nf);
    verdict(name, nf >= 2 ? "" : "one form only");
    return 0;
}

/* ---- D: the REPORT kind since D172 S3 ------------------------------------- */

static void family_d(void)
{
    /* the REPORT site RPT served through S2 (a two-offset term below its
       candidate, once a context item's) is refused on every art since RPT
       and the preview retired (window_site.md §4): a REPORT site is a window
       site, rendered by the family's E-find row */
    char err[512], row[16] = "";
    mf_site s = span_site();
    s.site_kind = MF_SK_REPORT;
    s.pred.nterm = 2;
    t_run(&s.pred.term[1], -2, "xa", MF_REQUIRED);
    const char *form = define_on(&s, err, sizeof err, NULL, row);
    verdict("D REPORT with a two-offset term below its candidate, stated in terms: refused",
            form ? "rendered" : strstr(err, "`site_kind` REPORT") ? "" : err);
}

int main(int argc, char **argv)
{
    const char *dir = NULL;
    unsigned nsites = 400, nreport = 150;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--gen") && i + 1 < argc) dir = argv[++i];
        else if (!strcmp(argv[i], "--sites") && i + 1 < argc) nsites = (unsigned)atoi(argv[++i]);
        else if (!strcmp(argv[i], "--report-sites") && i + 1 < argc) nreport = (unsigned)atoi(argv[++i]);
        else { fprintf(stderr, "usage: proof_check [--gen DIR] [--sites N] [--report-sites N]\n"); return 2; }
    }
    family_a();
    family_b();
    family_d();
    if (dir && family_c(dir, nsites, nreport)) return 2;
    printf("checks passed: %d\n", passed);
    printf("checks failed: %d\n", failed);
    return failed ? 1 : 0;
}
