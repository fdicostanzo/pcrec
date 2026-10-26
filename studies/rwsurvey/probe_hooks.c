/* probe_hooks.c -- rwsurvey probe: AST dumper + neighbour-shape detectors +
 * DFA scan-edge reach counter. Throwaway survey instrument (see CLAUDE.md). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "probe_hooks.h"

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

void probe_begin(const Ctx *cx)
{
    FILE *f = po();
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
            /* (d) run of C-chars then \b, or then (?!C) */
            if (nx->core->k == A_CTX && rx->u.rep.rmin >= 1) {
                PrCls cc = { nx->core->u.ctx.iv, nx->core->u.ctx.n };
                if ((nx->core->u.ctx.fn == CTXFN_BOUNDARY || nx->core->u.ctx.fn == CTXFN_NOT_NEXT) &&
                    pr_subset(&x, &cc)) {
                    hit(stage, nx->core->u.ctx.fn == CTXFN_BOUNDARY ? "D-BOUND-AFTER-RUN" : "D-NOTNEXT-AFTER-RUN");
                    fprintf(f, "mode=%s X=", mode_of(&el[i], rx)); pr_print(f, &x); fputs(" C=", f);
                    pr_print(f, &cc); fputc('\n', f);
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

void probe_dfa(const Ctx *cx, const Dfa *d, const char *name, int line)
{
    (void)cx;
    FILE *f = po();
    int one_self = 0, one_other = 0, gain_self = 0, gain_other = 0;
    int one_self_v = 0, gain_self_v = 0, gain_other_v = 0, one_other_v = 0;
    int shown = 0;
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
        bool vok = pcrec_state_view_invariant(d, &d->st[s]);
        bool live0 = v[0] >= 0, live1 = v[1] >= 0;
        if (!live0 && !live1) continue;                 /* no advance target at all */
        bool self = v[0] == s || v[1] == s;
        bool one = (cnt[0] == 1 && live0) || (cnt[1] == 1 && live1);
        if (one) {
            if (self) { one_self++; one_self_v += vok; } else { one_other++; one_other_v += vok; }
            continue;
        }
        if (self) { gain_self++; gain_self_v += vok; } else { gain_other++; gain_other_v += vok; }
        if (shown++ < 4) {
            int adv = (v[0] == s) ? 0 : (v[1] == s) ? 1 : !live0 ? 1 : !live1 ? 0 : (cnt[0] >= cnt[1] ? 0 : 1);
            fprintf(f, "GAIN\t%s\tstate=%d\tself=%d\tvok=%d\tnS=%d\tS=", name, s, self, vok, cnt[adv]);
            int first = -1, second = -1;
            for (int c = 0; c < d->ncls; c++)
                if (tr[c] == v[adv]) {
                    if (first < 0) first = c; else if (second < 0) second = c;
                    if (cnt[adv] <= 4) { pr_bytes(f, d, c); fputc(' ', f); }
                }
            if (cnt[adv] > 4) fputs("(many classes)", f);
            fprintf(f, "\texit=%d\tsplit:", v[1 - adv]);
            int ns = 0;
            for (int t = 0; t < d->n && ns < 3; t++)
                if (d->st[t].tr[first] != d->st[t].tr[second]) {
                    fprintf(f, " s%d[%d|%d]", t, d->st[t].tr[first], d->st[t].tr[second]); ns++;
                }
            if (!ns) fprintf(f, " none-in-tr(ctx-atom %d|%d, clsctx=%d, tagged=%d)", d->catom[d->rep[first]], d->catom[d->rep[second]], d->clsctx, d->tagged);
            fputc('\n', f);
        }
    }
    fprintf(f, "DFA\t%s\tline=%d\tn=%d\tncls=%d\tone_self=%d\tone_self_vok=%d\tone_other=%d\tone_other_vok=%d"
               "\tgain_self=%d\tgain_self_vok=%d\tgain_other=%d\tgain_other_vok=%d\n",
            name, line, d->n, d->ncls, one_self, one_self_v, one_other, one_other_v,
            gain_self, gain_self_v, gain_other, gain_other_v);
}
