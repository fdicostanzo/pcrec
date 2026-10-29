/* probe_hooks.c -- rwsurvey probe: AST dumper + neighbour-shape detectors +
 * DFA scan-edge reach counter. Throwaway survey instrument (see CLAUDE.md). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "probe_hooks.h"
#include "enc/enc.h"

static FILE *po(void)
{
    static FILE *f;
    if (!f) {
        const char *p = getenv("PROBE_OUT");
        f = p ? fopen(p, "a") : stderr;
        if (!f) f = stderr;
    }
    return f;
}

static void esc(FILE *f, const char *s, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        unsigned char c = (unsigned char)s[i];
        if (c == '\\') fputs("\\\\", f);
        else if (c == '\t') fputs("\\t", f);
        else if (c == '\n') fputs("\\n", f);
        else if (c == '\r') fputs("\\r", f);
        else if (c < 32 || c > 126) fprintf(f, "\\x%02X", c);
        else fputc(c, f);
    }
}

static unsigned g_maxcp = 0xFF;

void probe_begin(const Ctx *cx)
{
    FILE *f = po();
    {
        const PcrecEnc *e = pcrec_enc_by_id(cx->opt->encoding);
        g_maxcp = e ? e->max_cp : 0xFF;
    }
    fputs("@@\tCOMPILE\t", f);
    esc(f, cx->pat, cx->patlen);
    fputc('\n', f);
}

/* ---- classes --------------------------------------------------------- */
typedef struct { const PcrecCpRange *iv; int n; } PrCls;

static bool pr_of(const Ast *a, PrCls *c)
{
    if (!a) return false;
    if (a->k == A_CLASS) { c->iv = a->u.cls.iv; c->n = a->u.cls.n; return true; }
    return false;
}
static bool pr_has(const PrCls *c, unsigned cp)
{
    for (int i = 0; i < c->n; i++) if (cp >= c->iv[i].lo && cp <= c->iv[i].hi) return true;
    return false;
}
static bool pr_subset(const PrCls *y, const PrCls *x)
{
    for (int i = 0; i < y->n; i++) {
        bool in = false;
        for (int j = 0; j < x->n; j++)
            if (y->iv[i].lo >= x->iv[j].lo && y->iv[i].hi <= x->iv[j].hi) { in = true; break; }
        if (!in) return false;
    }
    return true;
}
static bool pr_eq(const PrCls *a, const PrCls *b) { return pr_subset(a, b) && pr_subset(b, a); }


/* is every code point of [lo,hi] inside the union of x's intervals? */
static bool pr_covers(const PrCls *x, unsigned lo, unsigned hi)
{
    unsigned cur = lo;
    for (int i = 0; i < x->n && cur <= hi; i++) {
        if (x->iv[i].hi < cur) continue;
        if (x->iv[i].lo > cur) return false;
        if (x->iv[i].hi >= hi) return true;
        cur = x->iv[i].hi + 1;
    }
    return cur > hi;
}
/* C minus X non-empty? */
static bool pr_minus_nonempty(const PrCls *c, const PrCls *x)
{
    for (int i = 0; i < c->n; i++) if (!pr_covers(x, c->iv[i].lo, c->iv[i].hi)) return true;
    return false;
}
/* universe [0,max] minus (X union C) non-empty? */
static bool pr_outside_nonempty(const PrCls *x, const PrCls *c, unsigned max)
{
    unsigned cur = 0;
    for (;;) {
        /* find a covering interval of cur in x or c */
        bool moved = false;
        for (int i = 0; i < x->n; i++)
            if (x->iv[i].lo <= cur && x->iv[i].hi >= cur) { cur = x->iv[i].hi + 1; moved = true; break; }
        if (!moved)
            for (int i = 0; i < c->n; i++)
                if (c->iv[i].lo <= cur && c->iv[i].hi >= cur) { cur = c->iv[i].hi + 1; moved = true; break; }
        if (!moved) return cur <= max;
        if (cur > max) return false;
    }
}

static const struct { const char *name; int n; PcrecCpRange iv[6]; } named[] = {
    { "\\s", 2, { {9, 13}, {32, 32} } },
    { "\\d", 1, { {48, 57} } },
    { "\\w", 4, { {48, 57}, {65, 90}, {95, 95}, {97, 122} } },
    { "[^\\n]", 2, { {0, 9}, {11, 0xFF} } },
    { "[\\x00-\\xFF]", 1, { {0, 0xFF} } },
    { "\\h", 2, { {9, 9}, {32, 32} } },
};
static void pr_print(FILE *f, const PrCls *c)
{
    for (size_t k = 0; k < sizeof named / sizeof *named; k++) {
        if (named[k].n != c->n) continue;
        bool same = true;
        for (int i = 0; i < c->n; i++)
            if (named[k].iv[i].lo != c->iv[i].lo || named[k].iv[i].hi != c->iv[i].hi) same = false;
        if (same) { fputs(named[k].name, f); return; }
    }
    if (c->n == 1 && c->iv[0].lo == c->iv[0].hi) {
        unsigned ch = c->iv[0].lo;
        if (ch >= 33 && ch <= 126 && ch != '\\') fputc((int)ch, f); else fprintf(f, "\\x%02X", ch);
        return;
    }
    fputc('[', f);
    for (int i = 0; i < c->n && i < 12; i++) {
        unsigned lo = c->iv[i].lo, hi = c->iv[i].hi;
        if (lo >= 33 && lo <= 126) fputc((int)lo, f); else fprintf(f, "\\x%02X", lo);
        if (hi != lo) {
            fputc('-', f);
            if (hi >= 33 && hi <= 126) fputc((int)hi, f); else fprintf(f, "\\x%02X", hi);
        }
    }
    if (c->n > 12) fprintf(f, "...(%d iv)", c->n);
    fputc(']', f);
}

/* ---- sexpr ----------------------------------------------------------- */
static void sx(FILE *f, const Ast *a)
{
    if (!a) { fputs("NIL", f); return; }
    switch (a->k) {
    case A_CLASS: { PrCls c; pr_of(a, &c); pr_print(f, &c); break; }
    case A_WCLASS: fprintf(f, "WCLS(%d)", a->u.wcls.n); break;
    case A_CAT: {
        const Ast *p = a;
        fputc('<', f);
        sx(f, p->l);
        while (p->r && p->r->k == A_CAT) { fputc(' ', f); p = p->r; sx(f, p->l); }
        fputc(' ', f); sx(f, p->r);
        fputc('>', f); break;
    }
    case A_ALT: fputs("(|", f); sx(f, a->l); fputc(' ', f); sx(f, a->r); fputc(')', f); break;
    case A_REP:
        fputc('{', f); sx(f, a->l);
        fprintf(f, " %d,%d%s%s", a->u.rep.rmin, a->u.rep.rmax,
                a->u.rep.greedy ? "" : "?", a->u.rep.possessive ? "+" : "");
        fputc('}', f); break;
    case A_EMPTY: fputs("EMPTY", f); break;
    case A_EOL: fputs("$", f); break;
    case A_CTX: fprintf(f, "CTX%03X", (unsigned)a->u.ctx.fn); break;
    case A_GSTART: fputs("\\G", f); break;
    case A_KRESET: fputs("\\K", f); break;
    case A_CAP: fprintf(f, "(#%d ", a->u.cap.no); sx(f, a->l); fputc(')', f); break;
    case A_ATOMIC: fputs("(>", f); sx(f, a->l); fputc(')', f); break;
    case A_BREF: fputs("BREF", f); break;
    case A_LOOK: fprintf(f, "LOOK%s%s[", a->u.look.behind ? "B" : "A", a->u.look.neg ? "!" : "");
        sx(f, a->l); fputc(']', f); break;
    case A_CALL: fprintf(f, "CALL%d", a->u.call.target); break;
    case A_VAR: fputs("VAR", f); break;
    }
}

static bool ast_eq(const Ast *a, const Ast *b)
{
    if (a == b) return true;
    if (!a || !b || a->k != b->k) return false;
    switch (a->k) {
    case A_CLASS: { PrCls x, y; pr_of(a, &x); pr_of(b, &y); return pr_eq(&x, &y); }
    case A_CAT: case A_ALT: return ast_eq(a->l, b->l) && ast_eq(a->r, b->r);
    case A_REP: return a->u.rep.rmin == b->u.rep.rmin && a->u.rep.rmax == b->u.rep.rmax &&
                       a->u.rep.greedy == b->u.rep.greedy && ast_eq(a->l, b->l);
    case A_EMPTY: case A_EOL: case A_GSTART: case A_KRESET: return true;
    case A_CTX: return a->u.ctx.fn == b->u.ctx.fn;
    case A_CAP: case A_ATOMIC: return ast_eq(a->l, b->l);
    default: return false;
    }
}

/* ---- element view ---------------------------------------------------- */
typedef struct {
    const Ast *e;      /* original element */
    const Ast *core;   /* after peeling CAP / ATOMIC */
    int cap, atomic;
} El;

static El peel(const Ast *a)
{
    El r = { a, a, 0, 0 };
    while (r.core && (r.core->k == A_CAP || r.core->k == A_ATOMIC)) {
        if (r.core->k == A_CAP) r.cap = 1; else r.atomic = 1;
        r.core = r.core->l;
    }
    return r;
}
/* a repeat of a bare class: fills cls and returns the REP node, else NULL */
static const Ast *rep_of_cls(const El *el, PrCls *c)
{
    const Ast *r = el->core;
    if (!r || r->k != A_REP) return NULL;
    El b = peel(r->l);
    if (b.cap) return NULL;                /* a capture INSIDE the repeat: not the shape */
    return pr_of(b.core, c) ? r : NULL;
}
static const char *mode_of(const El *el, const Ast *rep)
{
    if (el->atomic || rep->u.rep.possessive) return "poss";
    return rep->u.rep.greedy ? "greedy" : "lazy";
}

static void hit(const char *stage, const char *code)
{
    fprintf(po(), "HIT\t%s\t%s\t", stage, code);
}

static void detail_rep(FILE *f, const PrCls *c, const Ast *rep)
{
    pr_print(f, c);
    fprintf(f, "{%d,%d}", rep->u.rep.rmin, rep->u.rep.rmax);
}

/* ---- spine scan ------------------------------------------------------- */
static void collect(const Ast *a, El *out, int *m, int cap)
{
    if (!a) return;
    if (a->k == A_CAT) { collect(a->l, out, m, cap); collect(a->r, out, m, cap); return; }
    if (*m < cap) out[(*m)++] = peel(a);
}

static void scan_spine(const char *stage, const Ast *cat)
{
    static El el[8192];
    int m = 0;
    collect(cat, el, &m, 8192);
    FILE *f = po();
    for (int i = 0; i < m; i++) {
        if (el[i].e->k == A_EMPTY) { hit(stage, "C-EMPTY-CAT"); fprintf(f, "idx=%d/%d\n", i, m); }
        PrCls x, y;
        const Ast *rx = rep_of_cls(&el[i], &x);
        if (i + 1 >= m) continue;
        const El *nx = &el[i + 1];
        const Ast *ry = rep_of_cls(nx, &y);
        if (rx && rx->u.rep.rmax == -1) {
            /* (a) run then optional/starred subset */
            if (ry && ry->u.rep.rmin == 0 && pr_subset(&y, &x)) {
                hit(stage, "A-ABSORB-OPT");
                fprintf(f, "mode=%s capgap=%d X=", mode_of(&el[i], rx), el[i].cap | nx->cap);
                detail_rep(f, &x, rx); fputs(" Y=", f); detail_rep(f, &y, ry); fputc('\n', f);
            }
            /* (c) run then the same class again, single or repeated: merge-run */
            PrCls z;
            if (pr_of(nx->core, &z) && pr_eq(&z, &x)) {
                hit(stage, "C-MERGE-RUN"); fprintf(f, "mode=%s capgap=%d X=", mode_of(&el[i], rx), el[i].cap | nx->cap);
                detail_rep(f, &x, rx); fputs(" then single same class\n", f);
            } else if (ry && ry->u.rep.rmin > 0 && pr_eq(&y, &x)) {
                hit(stage, "C-MERGE-RUN"); fprintf(f, "mode=%s capgap=%d X=", mode_of(&el[i], rx), el[i].cap | nx->cap);
                detail_rep(f, &x, rx); fputs(" then ", f); detail_rep(f, &y, ry); fputc('\n', f);
            }
            /* (b) run then $ */
            if (nx->e->k == A_EOL && pr_has(&x, '\n')) {
                hit(stage, "B-ABSORB-EOL");
                fprintf(f, "mode=%s capgap=%d rmin=%d X=", mode_of(&el[i], rx), el[i].cap, rx->u.rep.rmin);
                pr_print(f, &x); fputc('\n', f);
            }
            /* (d) a context assertion after a maximal run whose truth is already decided by
             * "the next byte is outside X": X+ then A with A true for every feasible
             * (previous = last run byte, next = not-in-X or absent) cell. */
            if (nx->core->k == A_CTX && rx->u.rep.rmin >= 1) {
                PrCls cc = { nx->core->u.ctx.iv, nx->core->u.ctx.n };
                unsigned fn = nx->core->u.ctx.fn;
                int p = pr_subset(&x, &cc) ? 1 : (!pr_minus_nonempty(&x, &cc) ? 1 : -1);
                /* p: 1 = every run byte in C, 0 = none in C, -1 = mixed */
                bool all_in = pr_subset(&x, &cc);
                bool none_in = true;
                for (int i = 0; i < x.n && none_in; i++)
                    for (int j = 0; j < cc.n; j++)
                        if (x.iv[i].lo <= cc.iv[j].hi && cc.iv[j].lo <= x.iv[i].hi) { none_in = false; break; }
                p = all_in ? 1 : none_in ? 0 : -1;
                if (p >= 0) {
                    bool q_in = pr_minus_nonempty(&cc, &x);          /* a next byte in C and not in X */
                    PrCls cx_ = x;
                    bool q_out = pr_outside_nonempty(&cx_, &cc, g_maxcp);
                    bool t_abs = ctxfn_cell(fn, (unsigned)p, 2) != 0;
                    bool t_in = ctxfn_cell(fn, (unsigned)p, 1) != 0;
                    bool t_out = ctxfn_cell(fn, (unsigned)p, 0) != 0;
                    bool all_true = t_abs && (!q_in || t_in) && (!q_out || t_out);
                    bool all_false = !t_abs && (!q_in || !t_in) && (!q_out || !t_out);
                    if (all_true || all_false) {
                        hit(stage, all_true ? "D-CTX-IMPLIED-TRUE" : "D-CTX-IMPLIED-FALSE");
                        fprintf(f, "mode=%s fn=%03X X=", mode_of(&el[i], rx), fn); pr_print(f, &x);
                        fputs(" C=", f); pr_print(f, &cc); fputc('\n', f);
                    }
                }
            }
        }
        /* bounded first repeat then equal class repeat */
        if (rx && rx->u.rep.rmax != -1 && ry && pr_eq(&x, &y)) {
            hit(stage, "C-MERGE-RUN"); fprintf(f, "bounded X=");
            detail_rep(f, &x, rx); fputs(" then ", f); detail_rep(f, &y, ry); fputc('\n', f);
        }
        {
            PrCls z;
            if (!rx && pr_of(el[i].core, &z) && ry && pr_eq(&z, &y)) {
                hit(stage, "C-MERGE-RUN"); fputs("single then ", f); detail_rep(f, &y, ry); fputc('\n', f);
            }
        }
        /* identical adjacent zero-width */
        if ((el[i].e->k == A_CTX || el[i].e->k == A_EOL) && ast_eq(el[i].e, nx->e)) {
            hit(stage, "D-DUP-ZW"); sx(f, el[i].e); fputc('\n', f);
        }
        /* \z then a consumer; consumer then \A */
        if (el[i].e->k == A_CTX && el[i].e->u.ctx.fn == CTXFN_SUBJECT_END) {
            const Ast *n2 = nx->core;
            if (n2->k == A_CLASS || (n2->k == A_REP && n2->u.rep.rmin > 0)) {
                hit(stage, "D-PIN-DEAD"); fputs("\\z then consumer\n", f);
            }
        }
        if (nx->e->k == A_CTX && nx->e->u.ctx.fn == CTXFN_SUBJECT_START) {
            const Ast *n2 = el[i].core;
            if (n2->k == A_CLASS || (n2->k == A_REP && n2->u.rep.rmin > 0)) {
                hit(stage, "D-PIN-DEAD"); fputs("consumer then \\A\n", f);
            }
        }
    }
}

static void visit(const char *stage, const Ast *a, bool parent_cat)
{
    if (!a) return;
    FILE *f = po();
    switch (a->k) {
    case A_CAT:
        if (!parent_cat) scan_spine(stage, a);
        visit(stage, a->l, true); visit(stage, a->r, true);
        return;
    case A_ALT:
        if (ast_eq(a->l, a->r)) { hit(stage, "C-ALT-SAME"); sx(f, a); fputc('\n', f); }
        if ((a->l && a->l->k == A_EMPTY) || (a->r && a->r->k == A_EMPTY)) {
            hit(stage, "C-ALT-EMPTY"); sx(f, a); fputc('\n', f);
        }
        visit(stage, a->l, false); visit(stage, a->r, false);
        return;
    case A_REP: {
        El b = peel(a->l);
        if (b.core && b.core->k == A_REP && !b.cap) {
            hit(stage, "C-REP-REP"); sx(f, a); fputc('\n', f);
        }
        if (a->u.rep.rmin == 1 && a->u.rep.rmax == 1) { hit(stage, "C-REP-TRIVIAL"); sx(f, a); fputc('\n', f); }
        if (a->u.rep.rmax == 0) { hit(stage, "C-REP-ZERO"); sx(f, a); fputc('\n', f); }
        visit(stage, a->l, false);
        return;
    }
    case A_ATOMIC: {
        const Ast *b = a->l;
        if (b && (b->k == A_CLASS || b->k == A_EMPTY || b->k == A_CTX || b->k == A_EOL)) {
            hit(stage, "C-ATOMIC-NOOP"); sx(f, a); fputc('\n', f);
        }
        if (b && b->k == A_ATOMIC) { hit(stage, "C-ATOMIC-ATOMIC"); sx(f, a); fputc('\n', f); }
        if (b && b->k == A_REP && b->u.rep.possessive) { hit(stage, "C-ATOMIC-POSS"); sx(f, a); fputc('\n', f); }
        visit(stage, a->l, false);
        return;
    }
    case A_CAP: case A_LOOK:
        visit(stage, a->l, false); return;
    case A_CLASS: case A_WCLASS: case A_EMPTY: case A_EOL: case A_CTX: case A_GSTART:
    case A_KRESET: case A_BREF: case A_CALL: case A_VAR:
        return;
    }
}

void probe_ast(const Ctx *cx, const char *stage, const Ast *root)
{
    (void)cx;
    FILE *f = po();
    fprintf(f, "AST\t%s\t", stage); sx(f, root); fputc('\n', f);
    visit(stage, root, false);
}

/* ---- DFA scan-edge reach --------------------------------------------- */
static void pr_bytes(FILE *f, const Dfa *d, int c)
{
    int lo = -1, cnt = 0;
    for (int b = 0; b <= 256; b++) {
        bool in = b < 256 && d->clsmap[b] == c;
        if (in) cnt++;
        if (in && lo < 0) lo = b;
        if (!in && lo >= 0) {
            int hi = b - 1;
            if (lo >= 33 && lo <= 126) fputc(lo, f); else fprintf(f, "\\x%02X", lo);
            if (hi != lo) { fputc('-', f); if (hi >= 33 && hi <= 126) fputc(hi, f); else fprintf(f, "\\x%02X", hi); }
            lo = -1;
        }
    }
    fprintf(f, "(%d)", cnt);
}

/* Chain-member model (a hypothesis-level stand-in for scanedge.c's eight
 * preconditions: it checks precondition (1) shape and the chain-link/loop
 * condition of (5); view-ok (precondition 2/3) is reported separately).
 * A state is SET-SHAPED when its transitions take exactly two distinct values
 * and the ADVANCE side (the value that is a live state) is chosen; it is
 * ONE-SHAPED when that advance side is a single class (today's rule).
 * A state is a chain MEMBER when it self-loops on the advance side, or its
 * advance target is shaped with the same (class set, exit), or some shaped
 * state with the same (class set, exit) advances into it. */
typedef struct { bool ok, one; int adv, exit; unsigned long long sig; int ncl; } Shape;

static unsigned long long sig_of(const Dfa *d, const int *tr, int target)
{
    unsigned long long h = 1469598103934665603ULL;
    for (int c = 0; c < d->ncls; c++)
        if (tr[c] == target) { h ^= (unsigned long long)(c + 1); h *= 1099511628211ULL; }
    return h;
}

void probe_dfa(const Ctx *cx, const Dfa *d, const char *name, int line)
{
    (void)cx;
    FILE *f = po();
    Shape *sh = calloc((size_t)d->n + 1, sizeof *sh);
    if (!sh) return;
    for (int s = 0; s < d->n; s++) {
        const int *tr = d->st[s].tr;
        int v[2] = { -2, -2 }, cnt[2] = { 0, 0 }, nd = 0;
        for (int c = 0; c < d->ncls && nd <= 2; c++) {
            int k;
            for (k = 0; k < nd; k++) if (v[k] == tr[c]) break;
            if (k == nd) { if (nd == 2) { nd = 3; break; } v[nd++] = tr[c]; }
            cnt[k]++;
        }
        if (nd != 2) continue;
        bool live0 = v[0] >= 0, live1 = v[1] >= 0;
        if (!live0 && !live1) continue;
        /* the one-class rule's side wins when it exists, so one => set */
        int adv;
        bool one = false;
        if (cnt[0] == 1 && live0 && !(cnt[1] == 1 && live1 && v[1] == s)) { adv = 0; one = true; }
        else if (cnt[1] == 1 && live1) { adv = 1; one = true; }
        else if (v[0] == s) adv = 0;
        else if (v[1] == s) adv = 1;
        else if (!live0) adv = 1;
        else if (!live1) adv = 0;
        else adv = cnt[0] >= cnt[1] ? 0 : 1;
        sh[s].ok = true; sh[s].one = one; sh[s].adv = v[adv]; sh[s].exit = v[1 - adv];
        sh[s].ncl = cnt[adv]; sh[s].sig = sig_of(d, tr, v[adv]);
    }
    /* has-predecessor over the same (sig, exit) */
    bool *haspred = calloc((size_t)d->n + 1, sizeof *haspred);
    if (!haspred) { free(sh); return; }
    for (int s = 0; s < d->n; s++) {
        if (!sh[s].ok) continue;
        int t = sh[s].adv;
        if (t >= 0 && t < d->n && t != s && sh[t].ok && sh[t].sig == sh[s].sig && sh[t].exit == sh[s].exit)
            haspred[t] = true;
    }
    int mem_one = 0, mem_set = 0, mem_one_v = 0, mem_set_v = 0;
    int gain_self = 0, gain_chain = 0, gain_self_v = 0, gain_chain_v = 0;
    int shown = 0;
    for (int s = 0; s < d->n; s++) {
        if (!sh[s].ok) continue;
        int t = sh[s].adv;
        bool loop = t == s;
        bool link = !loop && t >= 0 && t < d->n && sh[t].ok && sh[t].sig == sh[s].sig && sh[t].exit == sh[s].exit;
        bool member = loop || link || haspred[s];
        if (!member) continue;
        bool vok = pcrec_state_view_invariant(d, &d->st[s]);
        /* one-class membership: every link in the chain must itself be one-shaped */
        bool omember = sh[s].one && (loop || (link && sh[t].one) || (haspred[s]));
        if (omember && !loop && !(link && sh[t].one)) {
            /* member only through a predecessor: need that predecessor one-shaped */
            bool pone = false;
            for (int p = 0; p < d->n; p++)
                if (sh[p].ok && sh[p].one && sh[p].adv == s && sh[p].sig == sh[s].sig && sh[p].exit == sh[s].exit) { pone = true; break; }
            omember = pone;
        }
        mem_set++; mem_set_v += vok;
        if (omember) { mem_one++; mem_one_v += vok; continue; }
        if (loop) { gain_self++; gain_self_v += vok; } else { gain_chain++; gain_chain_v += vok; }
        if (shown++ < 4) {
            const int *tr = d->st[s].tr;
            fprintf(f, "GAIN\t%s\tstate=%d\tself=%d\tvok=%d\tnS=%d\tS=", name, s, loop, vok, sh[s].ncl);
            int first = -1, second = -1;
            for (int c = 0; c < d->ncls; c++)
                if (tr[c] == sh[s].adv) {
                    if (first < 0) first = c; else if (second < 0) second = c;
                    if (sh[s].ncl <= 4) { pr_bytes(f, d, c); fputc(' ', f); }
                }
            if (sh[s].ncl > 4) fputs("(many classes)", f);
            fprintf(f, "\texit=%d\tsplit:", sh[s].exit);
            int ns = 0;
            for (int u = 0; u < d->n && ns < 3 && second >= 0; u++)
                if (d->st[u].tr[first] != d->st[u].tr[second]) {
                    fprintf(f, " s%d[%d|%d]", u, d->st[u].tr[first], d->st[u].tr[second]); ns++;
                }
            if (!ns && second >= 0)
                fprintf(f, " none-in-tr(ctx-atom %d|%d, clsctx=%d, tagged=%d)", d->catom[d->rep[first]], d->catom[d->rep[second]], d->clsctx, d->tagged);
            fputc('\n', f);
        }
    }
    fprintf(f, "DFA\t%s\tline=%d\tn=%d\tncls=%d\tmem_one=%d\tmem_one_vok=%d\tmem_set=%d\tmem_set_vok=%d"
               "\tgain_self=%d\tgain_self_vok=%d\tgain_chain=%d\tgain_chain_vok=%d\n",
            name, line, d->n, d->ncls, mem_one, mem_one_v, mem_set, mem_set_v,
            gain_self, gain_self_v, gain_chain, gain_chain_v);
    free(haspred); free(sh);
}

/* ---- the REAL scan-edge pass's outcome, read before and after it ------- */
static int se_n0, se_line;
static const char *se_name;

void probe_se_pre(const Ctx *cx, const Dfa *d, const char *name, int line)
{
    probe_dfa(cx, d, name, line);          /* the chain-member MODEL line (hypothesis-level) */
    se_n0 = d->n; se_name = name; se_line = line;
}

void probe_se_post(const Ctx *cx, const Dfa *d)
{
    (void)cx;
    int unb = 0, bnd = 0;
    for (int s = 0; s < d->n; s++) {
        if (d->st[s].scan_span < 0) unb++;
        else if (d->st[s].scan_span > 0) bnd++;
    }
    fprintf(po(), "SE\t%s\tline=%d\tn_before=%d\tn_after=%d\tunb=%d\tbnd=%d\n", se_name, se_line, se_n0, d->n, unb, bnd);
}
