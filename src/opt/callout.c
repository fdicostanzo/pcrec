/* callout.c — [INLINE-C] stage 1b: THE CALLOUT SITES PASS (module
 * `callouts`; docs/design/inline_c.md §1.9, §1.10, §2.2).
 *
 * ONE GENERIC VISIT AND ONE WALK OVER THE TREE AS WRITTEN, run by
 * src/core/compile.c after the composer and the derivation hooks and before
 * `pcrec_altcls` and every optimization pass: the firing class is a fact about the pattern as the
 * user wrote it, and §1.8 forbids a pass that would add fires, so nothing
 * downstream may be what the class is read from. A pattern with no site
 * (`cx->ncallouts == 0`) returns at the first line, which is what keeps every
 * callout-free compile byte-identical.
 *
 * IT DOES FOUR THINGS, in this order, each a declared rule of the design:
 *
 *   1. DECLARATIONS (§2.2): a numbered callout's attributes arrive from the
 *      `.rxt` `callout` line or `--callout`, and are applied to every site
 *      with that number before anything reads a site's width class. A
 *      declaration naming a number no site uses is REFUSED (a stale
 *      declaration is a bug, not a default), as is a number declared twice.
 *   2. NUMBERING: sites are numbered 1..n in textual order (the listing's
 *      and the stamps' `site` column).
 *   3. POSITIONS (§1.9, first match): inside a lookbehind, refused; inside a
 *      group a subroutine call or recursion can reach (a local `(?1)`,
 *      `(?R)`, `(?&n)`, a `(?(DEFINE)` group that is called, and every `lib`
 *      definition, which the composer binds as exactly such a group), refused:
 *      a call re-enters the site at a depth the view does not describe.
 *      Row 2 (a conditional's condition) cannot arise: module `conditionals`
 *      has no producer, so `(?(` is refused before a site inside it exists.
 *   4. THE FIRING CLASS (§1.10) and the `once` check: see `co_site`. A
 *      refused site's message comes from the `once` advice table and its
 *      verdict on the fix (match_api.md §11.8¶3a), below.
 *
 * Spines are walked iteratively (D10/DD-10): a concatenation is as long as
 * the pattern, so a CAT or ALT spine is flattened into an array first, and
 * recursion is bounded by group nesting, which the parser bounds. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"

typedef struct {
    Ctx           *cx;
    unsigned char *called;   /* [ncap + 1]: group g is a call target */
    bool           call_root;/* `(?R)`/`(?0)`: every site is reachable */
    int            next;     /* the next site number */
    Ast          **sites;    /* [ncallouts]: every site, in visit order */
    int            nsites;
    Ast           *root;     /* the tree as written: the advice's verdict */
} CoWalk;

/* Flattens the `k`-spine rooted at `a` (left-deep: `k(k(x, y), z)`) into
 * its items in textual order, arena-allocated; *n is their count. */
static Ast **co_items(Ctx *cx, Ast *a, AKind k, int *n)
{
    int c = 1;
    for (const Ast *t = a; t->k == k; t = t->l) c++;
    Ast **v = pcrec_arena_alloc(&cx->arena, (size_t)c * sizeof *v);
    int i = c;
    Ast *t = a;
    for (; t->k == k; t = t->l) v[--i] = t->r;
    v[--i] = t;
    *n = c;
    return v;
}

/* A group that never runs (`A_REP{..,0}`, the shape `(?(DEFINE)` and every
 * composed `lib` definition take): it holds no choice point the engine can
 * resume, and it can follow a site without making it non-tail. */
static bool co_inert(const Ast *a)
{
    return a->k == A_REP && a->u.rep.rmax == 0;
}

/* The first CHOICE POINT inside `a` the engine can resume after `a`
 * completes (§1.10), or NULL: an alternation, a quantifier whose minimum and
 * maximum differ, or a call (conservatively: its body may hold choices). A
 * choice inside an atomic group, a possessive quantifier
 * (`A_ATOMIC(A_REP)`) or an ATOMIC lookaround is SEALED by the time `a`
 * completes; a NON-ATOMIC lookaround (`(?*...)`, `(*napla:...)`) keeps its
 * choices live after it completes (a later failure re-enters it), so it
 * answers with its body's. A group that never runs holds none, and neither
 * do a backreference, an anchor and a callout site (its callee is atomic,
 * D38 §2). The node returned is the one the `once` refusal names: for a
 * non-atomic lookaround, the lookaround itself. */
static const Ast *co_choice(Ctx *cx, Ast *a)
{
    if (co_inert(a)) return NULL;
    switch (a->k) {
    case A_ALT:
        return a;
    case A_REP:
        if (a->u.rep.rmin != a->u.rep.rmax) return a;
        return co_choice(cx, a->l);
    case A_CALL:
        return a;
    case A_CAT: {
        int n;
        Ast **v = co_items(cx, a, A_CAT, &n);
        for (int i = 0; i < n; i++) {
            const Ast *c = co_choice(cx, v[i]);
            if (c) return c;
        }
        return NULL;
    }
    case A_CAP:
    case A_WCLASS:
        return co_choice(cx, a->l);
    case A_LOOK:
        /* The lookaround itself is the live construct (the refusal names
         * it, then the choice inside): re-entering it resumes that choice. */
        return !a->u.look.atomic && co_choice(cx, a->l) ? a : NULL;
    case A_CTX: {
        /* A lookaround the parse rewrote into this node keeps the
         * construct as written: the rule reads the pattern, not the rewrite. */
        const Ast *wr = a->u.ctx.written;
        return wr ? co_choice(cx, (Ast *)wr) : NULL;
    }
    case A_ATOMIC:
    case A_CLASS: case A_EMPTY: case A_EOL: case A_GSTART:
    case A_KRESET: case A_BREF: case A_VAR: case A_CALLOUT:
        return NULL;
    }
    return a;   /* unreachable: -Wswitch makes a new kind a build error */
}

/* " at offset N" for a construct node that carries its pattern offset, or
 * "" for one a rewrite built (it has none, and gets no invented offset):
 * arena text for the `once` refusal. */
static const char *co_at(Ctx *cx, const Ast *c)
{
    size_t at = 0;
    bool known = false;
    switch (c->k) {
    case A_REP:  at = c->u.rep.at; known = c->u.rep.at_known; break;
    case A_ALT:  at = c->u.alt.at; known = c->u.alt.at_known; break;
    case A_CALL: at = c->reg_at;   known = c->reg != NULL;    break;
    case A_LOOK: at = c->u.look.at; known = true; break;
    case A_WCLASS:   /* its own arm: the A_CLASS arm reads the set */
        break;
    case A_CAT: case A_CAP: case A_ATOMIC:
    case A_CLASS: case A_EMPTY: case A_EOL: case A_CTX: case A_GSTART:
    case A_KRESET: case A_BREF: case A_VAR: case A_CALLOUT:
        break;   /* never a culprit: co_choice and co_walk name none */
    }
    return known ? pcrec_sb_fragf(&cx->arena, " at offset %zu", at) : "";
}

/* ---- THE `once` ADVICE: a declared table, one row per culprit kind -------
 *
 * Frank's ruling (INLINE-C.md, "go with 3"): the refusal names the live
 * construct and its fix, and says whether the fix CHANGES WHAT THE PATTERN
 * MATCHES. Which sites are refused stays the reading rule above; only the
 * message reads the proofs below, and only when a message is wanted (a `once`
 * refusal, or the `--emit-ir` note), so an accepted compile never runs them.
 *
 * First match on the node's kind and, for the two kinds that have one, its
 * sub-kind (`u.rep.greedy == false`: lazy; `u.look.behind`). A row with no
 * verdict texts offers no seal: a lazy quantifier's possessive form is
 * greedy and its atomic form keeps only its shortest run, so its advice is to
 * drop `once` or rewrite. `clause` takes the inner construct's name and
 * offset on the lookaround rows (the choice that keeps it live); `changes`
 * takes the witness. */
typedef struct {
    AKind       k;
    signed char sub;        /* -1 any; else lazy (A_REP) / behind (A_LOOK) */
    const char *name;
    const char *clause;
    const char *fix;
    const char *same;       /* PROVEN SAME */
    const char *changes;    /* PROVEN CHANGES: %s is the witness clause */
    const char *unproven;   /* neither proof applies */
} CoCulpritRow;

/* The verdict texts every sealing row shares today (the refusal must fit
 * `pcrec_error.msg`, so they are short; `co_culprit` drops the witness when
 * the whole message would not fit). */
#define CO_SAME     "that does not change what it matches"
#define CO_CHANGES  "that loses a match%s; drop `once` to keep it: the " \
                    "site then fires on each retry"
#define CO_UNPROVEN "that may change what it matches"

static const CoCulpritRow co_culprit_rows[] = {
    { A_REP, 1, "the lazy quantifier", "can be backtracked into",
      "drop `once` (the site then fires on each retry) or rewrite: X++ is "
      "greedy and (?>X+?) keeps only its shortest run",
      NULL, NULL, NULL },
    { A_REP, -1, "the quantifier", "can be backtracked into",
      "make it possessive (X++) or use (?>...)",
      CO_SAME, CO_CHANGES, CO_UNPROVEN },
    { A_ALT, -1, "the alternation", "can be backtracked into",
      "wrap it in (?>...)",
      CO_SAME, CO_CHANGES, CO_UNPROVEN },
    { A_CALL, -1, "the subroutine call", "can be backtracked into",
      "wrap it in (?>...)",
      CO_SAME, CO_CHANGES, CO_UNPROVEN },
    { A_LOOK, 0, "the non-atomic lookaround",
      "keeps %s%s live after it completes",
      "use (?=...) or wrap it: (?>(?*...))",
      CO_SAME, CO_CHANGES, CO_UNPROVEN },
    { A_LOOK, 1, "the non-atomic lookaround",
      "keeps %s%s live after it completes",
      "use (?<=...) or wrap it: (?>(?<*...))",
      CO_SAME, CO_CHANGES, CO_UNPROVEN },
};

/* The table row naming culprit `c`: the first whose kind and sub-kind match.
 * Every kind co_choice returns has a row, so NULL is an internal error. */
static const CoCulpritRow *co_culprit_row(Ctx *cx, const Ast *c)
{
    const int sub = c->k == A_REP  ? !c->u.rep.greedy
                  : c->k == A_LOOK ? c->u.look.behind : 0;
    for (size_t i = 0; i < sizeof co_culprit_rows / sizeof *co_culprit_rows; i++) {
        const CoCulpritRow *r = &co_culprit_rows[i];
        if (r->k == c->k && (r->sub < 0 || r->sub == sub)) return r;
    }
    pcrec_ctx_fail(cx, 0, "internal error: no once-advice row for a culprit "
                   "of kind %d", (int)c->k);
    return NULL;
}

/* ---- THE VERDICT: would sealing the culprit, (?>X) at its place, change
 * any match? One question for every kind, answered three ways.
 *
 * PROVEN SAME is the free discharge's own proof, asked about a HYPOTHETICAL
 * cut: the culprit is wrapped in place, possessify's survey
 * (`pcrec_poss_survey`, the discharge's verdict source, src/opt/atomic.c) is
 * asked whether that cut deletes nothing, and the node is put back. A
 * quantifier is sealed as itself (`(?>X{m,n})` is `X{m,n}+`); anything else
 * as `(?>(?:X){1})`, which matches what `(?>X)` matches, so the survey's
 * exact-count arm answers it: a body with a unique iteration has one way to
 * match from a given start and the cut has nothing to delete. A call
 * declines there, as it does for the discharge.
 *
 * A NON-ATOMIC LOOKAROUND has its own proof (manager ruling R1, ic1badvice):
 * it consumes nothing, so a retry into it reaches the continuation at the
 * SAME position, and the continuation already failed from there. The retry
 * is invisible exactly when nothing else it leaves behind differs, which is
 * when its body holds (`co_look_retry_inert`):
 *   - no live capture (`pcrec_has_live_capture`): a retry can set another
 *     span, and a backreference or the caller reads it;
 *   - no `\K`: a retry can move the reported start;
 *   - no callout site: its fires are the caller's to count;
 *   - no call: the callee is outside the body, and can hold any of these;
 *   - no backtracking verb: none has a producer, and a new node kind is a
 *     compile error in that predicate's switch.
 *
 * PROVEN CHANGES needs a WITNESS, built and checked below: a subject on which
 * an attempt at offset 0 matches as written and fails sealed. Otherwise the
 * verdict is UNPROVEN; it never guesses. Both at once is an internal error:
 * the two are independent computations of one fact. */
typedef enum { CO_SEAL_SAME, CO_SEAL_CHANGES, CO_SEAL_UNPROVEN } CoSeal;

typedef struct { const Ast *grp; bool hit; } CoSealHit;

/* True iff a retry into a lookaround body `a` can leave nothing behind but
 * captures: no `\K`, no callout site, no call (see the banner above). No
 * `default:` arm, so a new node kind (a backtracking verb) must be decided
 * here. */
static bool co_look_retry_inert(const Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_EOL: case A_CTX: case A_GSTART:
        case A_BREF: case A_VAR:
            return true;
        case A_KRESET: case A_CALLOUT: case A_CALL:
        case A_WCLASS:   /* below the encoding lowering: never met here */
            return false;
        case A_CAP: case A_REP: case A_ATOMIC: case A_LOOK:
            a = a->l;
            continue;
        case A_CAT: case A_ALT:
            PCREC_SPINE_EACH(e, a, a->k)
                if (!co_look_retry_inert(e)) return false;
            return true;
        }
        return false;
    }
}

/* The survey callback: notes that the hypothetical cut was proved a no-op. */
static void co_seal_hit(void *ud, Ast *grp)
{
    CoSealHit *h = ud;
    if (grp == h->grp) h->hit = true;
}

/* True iff the free discharge's proof says sealing `c` deletes no match,
 * every check site passing (a site in the follow is opaque to the survey, as
 * `\b` is, and the question is about the pattern, not the callee). Rewrites
 * `c` and the check sites in place for the survey and restores them before
 * returning, so the tree the later passes read is the one written. */
static bool co_seal_same(CoWalk *w, Ast *c)
{
    if (c->k == A_LOOK)
        return co_look_retry_inert(c->l) && !pcrec_has_live_capture(c->l);
    Ctx *cx = w->cx;
    Ast *site = pcrec_arena_alloc(&cx->arena,
                                  (size_t)w->nsites * sizeof *site);
    for (int i = 0; i < w->nsites; i++) {
        site[i] = *w->sites[i];
        if (!site[i].u.callout.consume) {
            memset(w->sites[i], 0, sizeof *w->sites[i]);
            w->sites[i]->k = A_EMPTY;
        }
    }
    const Ast saved = *c;
    Ast *x = pcrec_arena_alloc(&cx->arena, sizeof *x);
    *x = saved;
    Ast *body = x;
    if (saved.k != A_REP) {
        body = pcrec_arena_alloc(&cx->arena, sizeof *body);
        body->k = A_REP;
        body->l = x;
        body->u.rep.rmin = body->u.rep.rmax = 1;
        body->u.rep.greedy = true;
    }
    memset(c, 0, sizeof *c);
    c->k = A_ATOMIC;
    c->l = body;
    CoSealHit h = { c, false };
    pcrec_poss_survey(cx, w->root, co_seal_hit, &h);
    *c = saved;
    for (int i = 0; i < w->nsites; i++) *w->sites[i] = site[i];
    return h.hit;
}

/* ---- THE WITNESS ---------------------------------------------------------
 *
 * Built only where the whole pattern is ONE LINE of single characters: the
 * root, read through groups, atomic groups and never-run groups, is a
 * sequence P X R where P and R are classes (zero-width check sites passing,
 * `^`/`\A` first, `\z` last) and X is the culprit. X's ways to match, in the
 * order the engine tries them, must be class sequences too: an alternation's
 * branches, or a greedy quantifier's iteration counts from the most down
 * (a call stands for its group's body). Then nothing but X can be retried,
 * so an attempt is decided by which of X's ways is taken:
 *
 *   as written, ANY way of X followed by R succeeds;
 *   sealed, only the FIRST way that matches is tried.
 *
 * The subject is p W r: one character from each class of P, of a later way
 * W, and of R, each picked to also fit the earlier way it competes with, so
 * that way matches first. As written the attempt at 0 matches by
 * construction; the sealed attempt is then evaluated, and the subject is a
 * witness only when it fails. Anything outside that shape declines. */
typedef struct { const PcrecCpRange *iv; int n; } CoChar;

typedef struct {
    CoChar    *v;
    int        n, cap;
    const Ast *culprit;   /* the node the line stops at (NULL: none expected) */
    int        at;        /* index in v where the culprit stands, -1: not met */
    bool       pin_end;   /* a `\z` closed the line */
} CoLine;

/* Appends one character class to the line, growing it from the arena. */
static void co_line_push(Ctx *cx, CoLine *L, const Ast *cls)
{
    if (L->n == L->cap) {
        int ncap = L->cap ? L->cap * 2 : 16;
        CoChar *nv = pcrec_arena_alloc(&cx->arena, (size_t)ncap * sizeof *nv);
        if (L->n) memcpy(nv, L->v, (size_t)L->n * sizeof *nv);
        L->v = nv;
        L->cap = ncap;
    }
    L->v[L->n].iv = cls->u.cls.iv;
    L->v[L->n].n = cls->u.cls.n;
    L->n++;
}

/* Marks the culprit's place on the line: false for any other choice. */
static bool co_line_mark(CoLine *L, const Ast *a, bool inner)
{
    if (a != L->culprit || inner || L->at >= 0 || L->pin_end) return false;
    L->at = L->n;
    return true;
}

/* Reads `a` onto the line: false when it is not a line of characters
 * (`inner`: a way of the culprit, where no anchor and no culprit stand). */
static bool co_line(Ctx *cx, CoLine *L, const Ast *a, bool inner)
{
    switch (a->k) {
    case A_CLASS:
        if (a->u.cls.n == 0 || L->pin_end) return false;
        co_line_push(cx, L, a);
        return true;
    case A_EMPTY:
        return true;
    case A_CALLOUT:
        return !a->u.callout.consume;
    case A_CAT: {
        int n;
        Ast **v = co_items(cx, (Ast *)a, A_CAT, &n);
        for (int i = 0; i < n; i++)
            if (!co_line(cx, L, v[i], inner)) return false;
        return true;
    }
    case A_CAP: case A_ATOMIC:
        return co_line(cx, L, a->l, inner);
    case A_CTX:
        if (inner) return false;
        if (pcrec_ctx_class(a) == CTX_PIN_START) return L->n == 0 && L->at < 0;
        if (pcrec_ctx_class(a) != CTX_PIN_END) return false;
        L->pin_end = true;
        return true;
    case A_REP:
        return co_inert(a) || co_line_mark(L, a, inner);
    case A_ALT: case A_CALL: case A_LOOK:
        return co_line_mark(L, a, inner);
    case A_EOL: case A_GSTART: case A_KRESET: case A_BREF: case A_VAR:
    case A_WCLASS:
        return false;
    }
    return false;
}

/* The culprit's ways to match, in the order the engine tries them: either
 * `nway` branches, or (rep) the body `body` repeated from the most down to
 * `rmin` times, at most `rmax` (-1: unbounded). */
typedef struct {
    CoLine *way;
    int     nway;
    bool    rep;
    CoLine  body;
    int     rmin, rmax;
} CoWays;

/* The group numbered `no`, when exactly one A_CAP carries it. */
typedef struct { int no; const Ast *g; int n; } CoFind;

/* pcrec_ast_visit callback: collects the A_CAP nodes numbered `no`. */
static void co_find_cap(void *ud, const Ast *a)
{
    CoFind *f = ud;
    if (a->k == A_CAP && a->u.cap.no == f->no) { f->g = a; f->n++; }
}

/* Fills `w` with culprit `c`'s ways: false when they are not class lines. */
static bool co_ways(Ctx *cx, Ast *root, const Ast *c, CoWays *w)
{
    memset(w, 0, sizeof *w);
    if (c->k == A_CALL) {
        /* A call matches what its group's body matches; a body that is itself
         * a call, or a group the pattern holds twice, declines. */
        CoFind f = { c->u.call.target, NULL, 0 };
        if (f.no <= 0) return false;
        pcrec_ast_visit(root, co_find_cap, &f);
        if (f.n != 1) return false;
        c = f.g->l;
        while (c->k == A_CAP) c = c->l;
    }
    if (c->k == A_ALT) {
        Ast **v = co_items(cx, (Ast *)c, A_ALT, &w->nway);
        w->way = pcrec_arena_alloc(&cx->arena, (size_t)w->nway * sizeof *w->way);
        for (int i = 0; i < w->nway; i++) {
            w->way[i].at = -1;
            if (!co_line(cx, &w->way[i], v[i], true)) return false;
        }
        return true;
    }
    if (c->k == A_REP && c->u.rep.greedy && c->u.rep.rmin != c->u.rep.rmax) {
        w->rep = true;
        w->body.at = -1;
        w->rmin = c->u.rep.rmin;
        w->rmax = c->u.rep.rmax;
        return co_line(cx, &w->body, c->l, true) && w->body.n > 0;
    }
    return false;
}

/* The smallest code point in a, also in b (NULL: any) and in [lo, hi]. */
static bool co_char_min(const CoChar *a, const CoChar *b, unsigned lo,
                        unsigned hi, unsigned *out)
{
    bool found = false;
    for (int i = 0; i < a->n; i++) {
        unsigned alo = a->iv[i].lo > lo ? a->iv[i].lo : lo;
        unsigned ahi = a->iv[i].hi < hi ? a->iv[i].hi : hi;
        if (alo > ahi) continue;
        if (!b) {
            if (!found || alo < *out) *out = alo;
            found = true;
            continue;
        }
        for (int j = 0; j < b->n; j++) {
            unsigned x = b->iv[j].lo > alo ? b->iv[j].lo : alo;
            unsigned y = b->iv[j].hi < ahi ? b->iv[j].hi : ahi;
            if (x <= y && (!found || x < *out)) { *out = x; found = true; }
        }
    }
    return found;
}

/* A member of `w`, preferring one also in `s` (NULL: no preference), and a
 * printable one: the witness is printed in the refusal. */
static unsigned co_pick(const CoChar *w, const CoChar *s)
{
    unsigned c = 0;
    if (s && co_char_min(w, s, 0x21, 0x7e, &c)) return c;
    if (s && co_char_min(w, s, 0, ~0u, &c))     return c;
    if (co_char_min(w, NULL, 0x21, 0x7e, &c))   return c;
    co_char_min(w, NULL, 0, ~0u, &c);
    return c;
}

/* True iff code point `c` is in the class. */
static bool co_char_has(const CoChar *a, unsigned c)
{
    for (int i = 0; i < a->n; i++)
        if (c >= a->iv[i].lo && c <= a->iv[i].hi) return true;
    return false;
}

/* True iff line `L` matches t[off..off+L->n). */
static bool co_line_at(const CoLine *L, const unsigned *t, int nt, int off)
{
    if (off + L->n > nt) return false;
    for (int i = 0; i < L->n; i++)
        if (!co_char_has(&L->v[i], t[off + i])) return false;
    return true;
}

/* The length the SEALED culprit takes at t[0..], or -1 when no way matches. */
static int co_seal_len(const CoWays *w, const unsigned *t, int nt)
{
    if (w->rep) {
        int c = 0;
        while ((w->rmax < 0 || c < w->rmax) &&
               co_line_at(&w->body, t, nt, c * w->body.n))
            c++;
        return c >= w->rmin ? c * w->body.n : -1;
    }
    for (int i = 0; i < w->nway; i++)
        if (co_line_at(&w->way[i], t, nt, 0)) return w->way[i].n;
    return -1;
}

/* Tries one subject: the way `W` (n characters, W[q] the class at q) then R,
 * each character preferring `S` (the way it competes with; S[q] for q < ns).
 * Returns the witness text when the sealed attempt fails, else NULL. */
static const char *co_try(Ctx *cx, const CoLine *L, const CoWays *w,
                          const CoChar *const *W, int n,
                          const CoChar *const *S, int ns)
{
    const int np = L->at, k = L->n - L->at, nt = n + k;
    unsigned *t = pcrec_arena_alloc(&cx->arena,
                                    (size_t)(np + nt + 1) * sizeof *t);
    for (int q = 0; q < np; q++) t[q] = co_pick(&L->v[q], NULL);
    unsigned *u = t + np;
    for (int q = 0; q < nt; q++) {
        const CoChar *wq = q < n ? W[q] : &L->v[np + q - n];
        u[q] = co_pick(wq, q < ns ? S[q] : NULL);
    }
    const int sl = co_seal_len(w, u, nt);
    if (sl >= 0) {
        CoLine R = { L->v + np, k, k, NULL, -1, L->pin_end };
        if (co_line_at(&R, u, nt, sl) && (!L->pin_end || sl + k == nt))
            return NULL;   /* the sealed attempt matches too */
    }
    /* Rendered for the refusal: printable ASCII as is, the rest escaped. */
    char *out = pcrec_arena_alloc(&cx->arena, (size_t)(np + nt) * 12 + 1);
    size_t o = 0;
    for (int q = 0; q < np + nt; q++) {
        unsigned c = t[q];
        if (c >= 0x20 && c <= 0x7e && c != '"' && c != '\\') out[o++] = (char)c;
        else o += (size_t)sprintf(out + o, "\\x{%x}", c);
    }
    out[o] = '\0';
    return pcrec_sb_fragf(&cx->arena, " (offset 0 of \"%s\")", out);
}

/* A witness subject for sealing culprit `c` in `root`, or NULL. */
static const char *co_seal_witness(Ctx *cx, Ast *root, const Ast *c)
{
    CoLine L = { NULL, 0, 0, c, -1, false };
    CoWays w;
    if (!co_line(cx, &L, root, false) || L.at < 0 || !co_ways(cx, root, c, &w))
        return NULL;
    if (w.rep) {
        /* The fewest iterations as written; the seal is offered more by
         * picking R's characters to fit further iterations. */
        const int bl = w.body.n, n = w.rmin * bl, ns = n + (L.n - L.at) + bl;
        const CoChar **W = pcrec_arena_alloc(&cx->arena, (size_t)(n + 1) * sizeof *W);
        const CoChar **S = pcrec_arena_alloc(&cx->arena, (size_t)ns * sizeof *S);
        for (int q = 0; q < n; q++)  W[q] = &w.body.v[q % bl];
        for (int q = 0; q < ns; q++) S[q] = &w.body.v[q % bl];
        return co_try(cx, &L, &w, W, n, S, ns);
    }
    /* A later branch as written, against each earlier one it competes with. */
    for (int j = 1; j < w.nway; j++) {
        const CoChar **W = pcrec_arena_alloc(&cx->arena,
                                             (size_t)(w.way[j].n + 1) * sizeof *W);
        for (int q = 0; q < w.way[j].n; q++) W[q] = &w.way[j].v[q];
        for (int i = 0; i < j; i++) {
            const CoChar **S = pcrec_arena_alloc(&cx->arena,
                                                 (size_t)(w.way[i].n + 1) * sizeof *S);
            for (int q = 0; q < w.way[i].n; q++) S[q] = &w.way[i].v[q];
            const char *why = co_try(cx, &L, &w, W, w.way[j].n, S, w.way[i].n);
            if (why) return why;
        }
    }
    return NULL;
}

/* The verdict on sealing culprit `c` (see the banner above); *why is the
 * witness for PROVEN CHANGES. */
static CoSeal co_seal_verdict(CoWalk *w, const Ast *c, const char **why)
{
    Ctx *cx = w->cx;
    const bool same = co_seal_same(w, (Ast *)c);
    *why = co_seal_witness(cx, w->root, c);
    if (same && *why)
        pcrec_ctx_fail(cx, 0, "internal error: sealing the construct%s is "
                       "both proved a no-op and witnessed to change a match "
                       "(%s)", co_at(cx, c), *why);
    return same ? CO_SEAL_SAME : *why ? CO_SEAL_CHANGES : CO_SEAL_UNPROVEN;
}

/* The `once` refusal's naming of the live choice point `c` before a site,
 * its fix, and (`verdict`: a message is wanted) whether the fix changes what
 * the pattern matches: arena text, from the row co_culprit_row picks. A
 * witness that would push the text past `room` bytes is left out (the
 * verdict stays); the refusal prefixes this text, and `pcrec_error.msg` is
 * fixed-size. */
static const char *co_culprit(CoWalk *w, const Ast *c, bool verdict,
                              size_t room)
{
    Ctx *cx = w->cx;
    const CoCulpritRow *r = co_culprit_row(cx, c);
    const char *clause = r->clause;
    if (c->k == A_LOOK) {
        /* The choice that makes it live is the first one inside its body. */
        const Ast *in = co_choice(cx, c->l);
        while (in && in->k == A_LOOK) in = co_choice(cx, in->l);
        clause = pcrec_sb_fragf(&cx->arena, r->clause,
                                in ? co_culprit_row(cx, in)->name
                                   : "a choice point",
                                in ? co_at(cx, in) : "");
    }
    const char *text = pcrec_sb_fragf(&cx->arena, "%s%s %s; %s", r->name,
                                      co_at(cx, c), clause, r->fix);
    if (!verdict || !r->same) return text;
    const char *why;
    switch (co_seal_verdict(w, c, &why)) {
    case CO_SEAL_SAME:
        return pcrec_sb_fragf(&cx->arena, "%s; %s", text, r->same);
    case CO_SEAL_CHANGES: {
        const char *t = pcrec_sb_fragf(&cx->arena, "%s; %s", text,
                            pcrec_sb_fragf(&cx->arena, r->changes, why));
        return strlen(t) <= room ? t : pcrec_sb_fragf(&cx->arena, "%s; %s",
                            text, pcrec_sb_fragf(&cx->arena, r->changes, ""));
    }
    case CO_SEAL_UNPROVEN:
        return pcrec_sb_fragf(&cx->arena, "%s; %s", text, r->unproven);
    }
    return text;
}

/* The `once` refusal's head; its reason follows. */
#define CO_ONCE_HEAD "callout at offset %zu is marked once but can fire again: "

const char *pcrec_callout_class_name(int fclass)
{
    switch ((CalloutClass)fclass) {
    case CO_CLASS_ONCE_PER_MATCH: return "once-per-match";
    case CO_CLASS_ONCE_PER_START: return "once-per-start";
    case CO_CLASS_REPEATED:       return "repeated";
    }
    return "?";
}

/* One site: its number, its position check, its class, its `once` check.
 * `rep`: the innermost enclosing quantified group whose maximum is 2 or more
 * (NULL: none); `live`: the first choice point before it that can be resumed
 * (NULL: none); `tail`: nothing follows it on any path to accept;
 * `behind`/`called`: §1.9 rows 1 and 3. */
static void co_site(CoWalk *w, Ast *a, const Ast *rep, const Ast *live,
                    bool tail, bool behind, bool called)
{
    Ctx *cx = w->cx;
    size_t at = a->u.callout.at;
    a->u.callout.site = w->next++;
    cx->callout_nodes[a->u.callout.site] = a;
    if (behind)
        pcrec_ctx_fail(cx, at, "a callout inside a lookbehind is not "
                       "supported");
    if (called || w->call_root)
        pcrec_ctx_fail(cx, at, "a callout inside a group reached by a "
                       "subroutine call or recursion (including a lib "
                       "definition) is not supported: a call re-enters the "
                       "site at a depth its view does not describe");
    CalloutClass c;
    if (rep) {
        c = CO_CLASS_REPEATED;
        a->u.callout.why = pcrec_sb_fragf(&cx->arena, "inside the repeat "
            "whose quantifier%s has a maximum of 2 or more", co_at(cx, rep));
    } else if (live) {
        c = CO_CLASS_REPEATED;
        /* The verdict only when a message is wanted: the refusal itself, or
         * the `--emit-ir` note; `room` is what the refusal's head leaves of
         * `pcrec_error.msg`. */
        const bool wanted = a->u.callout.once || cx->want_ir;
        const size_t head = strlen(pcrec_sb_fragf(&cx->arena, CO_ONCE_HEAD, at));
        const size_t msg = sizeof ((pcrec_error *)0)->msg - 1;
        const size_t room = msg > head ? msg - head : 0;
        a->u.callout.why = co_culprit(w, live, wanted, room);   /* same text as the refusal */
    } else if (tail) {
        c = CO_CLASS_ONCE_PER_MATCH;
        a->u.callout.why = "no repeat and no live choice point before it; "
                           "tail";
    } else {
        c = CO_CLASS_ONCE_PER_START;
        a->u.callout.why = "no repeat and no live choice point before it";
    }
    a->u.callout.fclass = (int)c;
    a->u.callout.tail = tail;
    if (a->u.callout.once && c == CO_CLASS_REPEATED)
        pcrec_ctx_fail(cx, at, rep
            ? CO_ONCE_HEAD "%s; a site in such a repeat cannot be marked once"
            : CO_ONCE_HEAD "%s", at, a->u.callout.why);
}

static void co_walk(CoWalk *w, Ast *a, const Ast *rep, const Ast *live,
                    bool tail, bool behind, bool called)
{
    switch (a->k) {
    case A_CALLOUT:
        co_site(w, a, rep, live, tail, behind, called);
        return;
    case A_CAT: {
        int n;
        Ast **v = co_items(w->cx, a, A_CAT, &n);
        /* `last`: the index after which every item is inert. */
        int last = n - 1;
        while (last > 0 && co_inert(v[last])) last--;
        const Ast *before = live;
        for (int i = 0; i < n; i++) {
            co_walk(w, v[i], rep, before, tail && i >= last, behind, called);
            if (!before) before = co_choice(w->cx, v[i]);
        }
        return;
    }
    case A_ALT: {
        /* An enclosing alternation resumes LATER branches, which do not hold
         * the site: no choice is added on the way down. */
        int n;
        Ast **v = co_items(w->cx, a, A_ALT, &n);
        for (int i = 0; i < n; i++)
            co_walk(w, v[i], rep, live, tail, behind, called);
        return;
    }
    case A_REP: {
        const int mx = a->u.rep.rmax;
        const bool many = mx < 0 || mx >= 2;
        co_walk(w, a->l, many ? a : rep, live, tail && !many, behind,
                called);
        return;
    }
    case A_CAP: {
        const int no = a->u.cap.no;
        const bool c = called ||
            (no >= 0 && (unsigned)no <= w->cx->ncap && w->called[no]);
        co_walk(w, a->l, rep, live, tail, behind, c);
        return;
    }
    case A_ATOMIC:
    case A_WCLASS:
        co_walk(w, a->l, rep, live, tail, behind, called);
        return;
    case A_LOOK:
        co_walk(w, a->l, rep, live, false, behind || a->u.look.behind,
                called);
        return;
    /* The callee's body is visited at its own lexical position, never
     * through the call (the AST's one back edge). */
    case A_CALL:
    case A_CLASS: case A_EMPTY: case A_EOL: case A_CTX: case A_GSTART:
    case A_KRESET: case A_BREF: case A_VAR:
        return;
    }
}

/* The pass's one generic visit (`pcrec_ast_visit`): marks every call
 * target (group number; 0 is the whole pattern) and collects every site.
 * The visitor's node is const by its signature; a site is the arena's, and
 * the declarations below write its attributes. */
static void co_scan(void *ud, const Ast *a)
{
    CoWalk *w = ud;
    if (a->k == A_CALL) {
        const int t = a->u.call.target;
        if (t == 0) w->call_root = true;
        else if (t > 0 && (unsigned)t <= w->cx->ncap) w->called[t] = 1;
    } else if (a->k == A_CALLOUT && w->nsites < w->cx->ncallouts) {
        w->sites[w->nsites++] = (Ast *)a;
    }
}

void pcrec_callout_sites(Ctx *cx, Ast *root)
{
    const PcrecEmitIn *in = cx->emit_in;
    const int nd = in ? in->ncallout_decls : 0;
    if (cx->ncallouts == 0) {
        /* A declaration with no site at all is still stale. */
        if (nd > 0)
            pcrec_ctx_fail(cx, 0, "a callout declaration names callout %d, "
                           "which the pattern does not use",
                           in->callout_decls[0].num);
        return;
    }
    CoWalk w = { cx, NULL, false, 1, NULL, 0, root };
    w.called = pcrec_arena_alloc(&cx->arena, cx->ncap + 1);
    memset(w.called, 0, cx->ncap + 1);
    w.sites = pcrec_arena_alloc(&cx->arena,
                                (size_t)cx->ncallouts * sizeof *w.sites);
    pcrec_ast_visit(root, co_scan, &w);
    if (w.nsites != cx->ncallouts)
        pcrec_ctx_fail(cx, 0, "internal error: the parse built %d callout "
                       "sites and the visit reached %d", cx->ncallouts,
                       w.nsites);

    for (int i = 0; i < nd; i++) {
        const PcrecCalloutDecl *d = &in->callout_decls[i];
        for (int j = 0; j < i; j++)
            if (in->callout_decls[j].num == d->num)
                pcrec_ctx_fail(cx, 0, "callout %d is declared twice", d->num);
        bool used = false;
        for (int k = 0; k < w.nsites; k++) {
            Ast *a = w.sites[k];
            if (a->u.callout.bind != CO_NUM || a->u.callout.num != d->num)
                continue;
            used = true;
            const char *msg = pcrec_callout_attrs(cx, a, d->attrs,
                                                  strlen(d->attrs), ',');
            if (msg)
                pcrec_ctx_fail(cx, a->u.callout.at, "callout %d's "
                               "declaration: %s", d->num, msg);
        }
        if (!used)
            pcrec_ctx_fail(cx, 0, "a callout declaration names callout %d, "
                           "which the pattern does not use", d->num);
    }

    cx->callout_nodes = pcrec_arena_alloc(&cx->arena,
        (size_t)(cx->ncallouts + 1) * sizeof *cx->callout_nodes);
    memset(cx->callout_nodes, 0,
           (size_t)(cx->ncallouts + 1) * sizeof *cx->callout_nodes);
    co_walk(&w, root, NULL, NULL, true, false, false);
    if (w.next != cx->ncallouts + 1)
        pcrec_ctx_fail(cx, 0, "internal error: the parse built %d callout "
                       "sites and the numbering walk reached %d",
                       cx->ncallouts, w.next - 1);
    /* §1.4 D19: an unbound binding is a link error by design, and the
     * standalone driver `--emit-main` writes could not link one. Every
     * site is a binding at stage 1b (embedded code is stage 2's). */
    if (pcrec_opt_has(cx->opt, PCREC_EMIT_MAIN)) {
        const Ast *a = cx->callout_nodes[1];
        const PcrecCalloutBinding b = pcrec_callout_binding(&cx->arena, a);
        if (b.is_extern)
            pcrec_ctx_fail(cx, a->u.callout.at, "--emit-main cannot define "
                           "the binding %s; link your own", b.symbol);
    }
}
