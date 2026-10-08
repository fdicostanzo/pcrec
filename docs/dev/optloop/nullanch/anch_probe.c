/* docs/dev/optloop/nullanch/anch_probe.c -- [NULLABLE-ANCH] STEP 0 census
 * probe (lane nullanch0, MEASUREMENT ONLY: links build/libpcrec.a, changes
 * nothing under src/).
 *
 * WHAT IT COMPUTES. For each pattern on stdin (`id<TAB>pattern`, the pattern
 * in the --list-source escape vocabulary \t \n \r \\ \xNN), parsed at the
 * default (byte) encoding under `--features all`, the pipeline prefix
 * parse -> altcls -> discharge_atomic -> callgraph_build, then:
 *
 *   nullable  pcrec_nullable(root) -- the predicate select_engine.c's
 *             lang_nullable_declinable reads (via pcrec_fact_nullable).
 *   masks     the CORRECTED-PREDICATE CANDIDATE. The set of "empty-path
 *             constraint masks" the pattern's EMPTY matches can carry:
 *             bit 1 = the path crosses an absolute START assertion (^ or \A
 *             non-multiline), bit 2 = an absolute END assertion ($, \Z, \z
 *             non-multiline). Every other zero-width node (lookaround,
 *             \b/\B, \G, \K, multiline ^/$, a backreference, a call) is
 *             mask 0, i.e. treated as always satisfiable -- the same answer
 *             as today, so this analysis can only ever ADMIT MORE than
 *             today's decline, never decline more.
 *   dismissable  nullable AND every empty path carries BOTH an absolute
 *             start and an absolute end assertion, so the pattern matches
 *             the empty string only on subjects of at most one newline and
 *             an exact prefilter DISMISSES every other subject that has no
 *             non-empty match. This is the population the plan row's
 *             "anchor-aware nullability" would stop declining.
 *   nested    an A_REP that can iterate more than once (rmax -1 or > 1)
 *             whose body contains another such A_REP -- the ReDoS shape.
 *   nullbody  an unbounded A_REP whose body is nullable (the
 *             empty-iteration-guard shape of `(a*)*`).
 *
 * The pcrec_nullable cross-check: masks != 0 must equal nullable on every
 * pattern (printed as `xchk` = 1 on a disagreement; a nonzero total is a
 * probe bug, not a finding).
 *
 * Build: see run_census.sh. Output: one TSV row per input line. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>

#include "core/internal.h"

static size_t unesc(const char *s, unsigned char *out)
{
    size_t n = 0;
    for (size_t i = 0; s[i]; ) {
        unsigned char c = (unsigned char)s[i];
        if (c == '\\' && s[i + 1]) {
            char x = s[i + 1];
            if (x == 't') { out[n++] = 9;  i += 2; continue; }
            if (x == 'n') { out[n++] = 10; i += 2; continue; }
            if (x == 'r') { out[n++] = 13; i += 2; continue; }
            if (x == '\\') { out[n++] = '\\'; i += 2; continue; }
            if (x == 'x' && s[i + 2] && s[i + 3]) {
                char h[3] = { s[i + 2], s[i + 3], 0 };
                char *e;
                long v = strtol(h, &e, 16);
                if (*e == 0) { out[n++] = (unsigned char)v; i += 4; continue; }
            }
        }
        out[n++] = c; i++;
    }
    out[n] = 0;
    return n;
}

/* 4-bit set of achievable masks (bit m = mask m reachable on an empty path). */
static unsigned or_sets(unsigned a, unsigned b)
{
    unsigned r = 0;
    for (int i = 0; i < 4; i++)
        if (a & (1u << i))
            for (int j = 0; j < 4; j++)
                if (b & (1u << j)) r |= 1u << (i | j);
    return r;
}

static unsigned closure(unsigned b)
{
    unsigned c = b;
    for (;;) {
        unsigned n = c | or_sets(c, b);
        if (n == c) return c;
        c = n;
    }
}

static unsigned emp(const Ast *a)
{
    switch (a->k) {
    case A_WCLASS: case A_CLASS: return 0;
    case A_EMPTY: case A_CTX: case A_GSTART: case A_KRESET: case A_LOOK:
    case A_BREF: case A_VAR: return 1u << 0;
    case A_CALL: return a->u.call.nonnullable ? 0 : (1u << 0);
    case A_BOL: return a->u.anch.multiline ? (1u << 0) : (1u << 1);
    case A_EOL: return a->u.anch.multiline ? (1u << 0) : (1u << 2);
    case A_END: return 1u << 2;
    case A_CAP: case A_ATOMIC: return emp(a->l);
    case A_CAT: {
        unsigned l = emp(a->l);
        return l ? or_sets(l, emp(a->r)) : 0;
    }
    case A_ALT: return emp(a->l) | emp(a->r);
    case A_REP: {
        unsigned b = emp(a->l);
        int rmin = a->u.rep.rmin, rmax = a->u.rep.rmax;
        unsigned it = (rmax == 1) ? b : closure(b);
        return rmin == 0 ? ((1u << 0) | it) : it;
    }
    }
    return 1u << 0;
}

/* a repeat that can iterate more than once */
static int multi_rep(const Ast *a) { return a->k == A_REP && (a->u.rep.rmax == -1 || a->u.rep.rmax > 1); }

static int has_multi_rep(const Ast *a)
{
    if (!a) return 0;
    if (multi_rep(a)) return 1;
    switch (a->k) {
    case A_CAT: case A_ALT: return has_multi_rep(a->l) || has_multi_rep(a->r);
    case A_REP: case A_CAP: case A_ATOMIC: case A_WCLASS: case A_LOOK:
        return has_multi_rep(a->l);
    default: return 0;
    }
}

static int nested(const Ast *a)
{
    if (!a) return 0;
    switch (a->k) {
    case A_CAT: case A_ALT: return nested(a->l) || nested(a->r);
    case A_REP:
        if (multi_rep(a) && has_multi_rep(a->l)) return 1;
        return nested(a->l);
    case A_CAP: case A_ATOMIC: case A_WCLASS: case A_LOOK: return nested(a->l);
    default: return 0;
    }
}

static int nullbody(const Ast *a)
{
    if (!a) return 0;
    switch (a->k) {
    case A_CAT: case A_ALT: return nullbody(a->l) || nullbody(a->r);
    case A_REP:
        if (a->u.rep.rmax == -1 && pcrec_nullable(a->l)) return 1;
        return nullbody(a->l);
    case A_CAP: case A_ATOMIC: case A_WCLASS: case A_LOOK: return nullbody(a->l);
    default: return 0;
    }
}

static void one(const char *id, const unsigned char *pat, size_t plen)
{
    pcrec_options defo;
    pcrec_default_options(&defo);
    Ctx cx;
    memset(&cx, 0, sizeof cx);
    cx.pat = (const char *)pat;
    cx.patlen = plen;
    cx.opt = &defo;
    cx.enabled_features = pcrec_enabled_mask();
    cx.want_caps = 1;
    cx.first_cap_pos = (size_t)-1;
    cx.first_vmonly_pos = (size_t)-1;
    cx.arena.cx = &cx;
    cx.job = calloc(1, sizeof(Job));
    if (!cx.job) { fprintf(stderr, "oom\n"); exit(2); }
    if (setjmp(cx.jb) == 0) {
        pcrec_parse_mods_init(&cx);
        Ast *root = pcrec_parse(&cx);
        root = pcrec_altcls(&cx, root);
        root = pcrec_discharge_atomic(&cx, root);
        pcrec_callgraph_build(&cx, root);
        unsigned m = emp(root);
        int nul = pcrec_nullable(root) ? 1 : 0;
        int dism = (m != 0) && !(m & 0x7);   /* only mask 3 reachable */
        printf("%s\tok\t%d\t%x\t%d\t%d\t%d\t%d\n", id, nul, m, dism,
               nested(root), nullbody(root), (m != 0) != nul);
    } else {
        printf("%s\trefused\t\t\t\t\t\t\n", id);
    }
    free(cx.job->nfa.st); free(cx.job->rnfa.st); free(cx.job->dfa.st);
    free(cx.job->dfa.tab); free(cx.job->rdfa.st); free(cx.job->rdfa.tab);
    free(cx.job->adfa.st); free(cx.job->adfa.tab);
    free(cx.job);
    pcrec_arena_free(&cx.arena);
}

int main(void)
{
    char ferr[256];
    if (pcrec_enabled_set_spec("all", ferr, sizeof ferr) != 0) {
        fprintf(stderr, "features: %s\n", ferr);
        return 2;
    }
    static char line[1 << 16];
    static unsigned char pat[1 << 16];
    printf("#id\tparse\tnullable\tmasks\tdismissable\tnested\tnullbody\txchk\n");
    while (fgets(line, sizeof line, stdin)) {
        size_t L = strlen(line);
        while (L && (line[L - 1] == '\n')) line[--L] = 0;
        char *tab = strchr(line, '\t');
        if (!tab) continue;
        *tab = 0;
        if (strlen(tab + 1) > 3000) { printf("%s\tskipped-long\t\t\t\t\t\t\n", line); continue; }
        size_t n = unesc(tab + 1, pat);
        one(line, pat, n);
    }
    return 0;
}
