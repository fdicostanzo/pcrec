/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/formhash.c — FORM HASHES (R-MS3, R17-b' B1; measure_sets.md §2.4,
 * r17b_prime.md §4.7): `mf_form_hash(form_id)`, the hash of a form's
 * INSTANCES with their scaffolding normalized out, which a measurement set's
 * `deps` column records and staleness compares (pcrec compares the strings
 * and nothing else). An id with one instance hashes that instance's text; an
 * id with several (a verify form's classes) hashes ONE text, every instance's
 * site text in table order joined by a newline (span_cards.md §2.4, review
 * r9 G4 FOLD): a change to any instance moves the id's hash, so it stales
 * every row the id's instances price.
 *
 * THE CANONICAL INSTANCE. A form's text for ONE fixed site of the form,
 * rendered through the kit's own entries in a scratch art over a scratch
 * arena with the fixed prefix (`mf`): the ENTRY TABLE below (span_cards.md
 * §3.2, unit S2c) states each instance's site shape, facts, target token and
 * deny string, and ONE renderer path builds every instance, so the text
 * hashed here is the text a span_cards cell times (the TEST entries
 * mf_form_site_text / mf_form_hash_cls, kit.h). A verify form has one
 * instance per class, the canonical one marked (the instance --site-text and
 * --facts name by default). A form id this kit does not
 * render (V1 until B4, the W64 forms until B6, NONE until B5, the dispatch
 * twin) is refused (-1), never hashed as something else.
 *
 * THE NORMALIZATION (what moves the hash and what does not):
 *   - comments (`/ * ... * /`, `//`) are dropped, outside string and
 *     character literals;
 *   - white space is layout: each line is trimmed at both ends, blank
 *     lines are dropped, and inside a line a run of white space survives
 *     only as ONE space between two word characters (`unsigned char`), so
 *     indentation, alignment and a removed inline comment move nothing;
 *   - every IDENTIFIER that is not in the kept list below (the C keywords,
 *     the standard types and the C-library names a form calls) is replaced
 *     by `$k`, k its order of first appearance: a renamed helper, a renamed
 *     variable or another prefix moves nothing, while an operator, a
 *     constant, a statement or a call moves the hash.
 * Then FNV-1a-64 over the normalized lines, each followed by `\n`, as 16
 * lowercase hex. The same function is `mf_form_hash_text` for a text the
 * caller holds (the kit's fixtures; R-MS3's bar is two of them: a rename and
 * a comment edit leave the hash, a one-instruction body edit moves it).
 *
 * D149: no tuning constant; the arena's block list is a bound on one
 * rendering's allocations (asserted, refusing past it).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "kit.h"

/* ---- normalization ----------------------------------------------------------- */

/* The identifiers the normalization keeps: C keywords and standard types,
 * and the C-library names a form's text calls (a different library call is
 * a different instruction stream). */
static const char *const kept[] = {
    "auto", "break", "case", "char", "const", "continue", "default", "do", "double",
    "else", "enum", "extern", "float", "for", "goto", "if", "inline", "int", "long",
    "register", "restrict", "return", "short", "signed", "sizeof", "static", "struct",
    "switch", "typedef", "union", "unsigned", "void", "volatile", "while", "_Bool",
    "__builtin_ctzll", "__builtin_expect", "__attribute__",
    "size_t", "ptrdiff_t", "uint8_t", "uint16_t", "uint32_t", "uint64_t", "int64_t",
    "NULL", "memchr", "memcmp", "memcpy", "memrchr",
    NULL,
};

static int is_kept(const char *p, size_t n)
{
    for (unsigned i = 0; kept[i]; i++)
        if (strlen(kept[i]) == n && !strncmp(kept[i], p, n)) return 1;
    return 0;
}

static int id_start(char c) { return c == '_' || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'); }
static int id_char(char c)  { return id_start(c) || (c >= '0' && c <= '9'); }

/* FNV-1a-64 over bytes, continued from h. */
static uint64_t fnv(uint64_t h, const char *p, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        h ^= (unsigned char)p[i];
        h *= 1099511628211ull;
    }
    return h;
}

/* A growable byte buffer over malloc (the normalization's scratch). */
typedef struct { char *p; size_t len, cap; int oom; } nbuf;

static void nb_put(nbuf *b, const char *s, size_t n)
{
    if (b->oom) return;
    if (b->len + n + 1 > b->cap) {
        size_t cap = b->cap ? b->cap * 2 : 1024;
        while (cap < b->len + n + 1) cap *= 2;
        char *q = realloc(b->p, cap);
        if (!q) { b->oom = 1; return; }
        b->p = q;
        b->cap = cap;
    }
    memcpy(b->p + b->len, s, n);
    b->len += n;
    b->p[b->len] = '\0';
}

void mf_form_hash_text(const char *text, char out[17])
{
    /* pass 1: drop comments outside literals */
    nbuf a = { 0 }, line = { 0 };
    for (const char *p = text; *p; ) {
        if (*p == '"' || *p == '\'') {
            char q = *p;
            const char *e = p + 1;
            while (*e && *e != q) e += (*e == '\\' && e[1]) ? 2 : 1;
            if (*e) e++;
            nb_put(&a, p, (size_t)(e - p));
            p = e;
        } else if (p[0] == '/' && p[1] == '*') {
            const char *e = strstr(p + 2, "*/");
            p = e ? e + 2 : p + strlen(p);
        } else if (p[0] == '/' && p[1] == '/') {
            while (*p && *p != '\n') p++;
        } else {
            nb_put(&a, p, 1);
            p++;
        }
    }
    /* pass 2: per line, trim, drop blanks, rename identifiers; hash */
    const char *names[256];             /* each ends where id_char stops */
    unsigned nn = 0;
    uint64_t h = 1469598103934665603ull;
    const char *s = a.p ? a.p : "";
    while (*s) {
        const char *e = strchr(s, '\n');
        size_t n = e ? (size_t)(e - s) : strlen(s);
        while (n && (*s == ' ' || *s == '\t' || *s == '\r')) { s++; n--; }
        size_t m = n;
        while (m && (s[m - 1] == ' ' || s[m - 1] == '\t' || s[m - 1] == '\r')) m--;
        line.len = 0;
        for (size_t i = 0; i < m; ) {
            if (s[i] == ' ' || s[i] == '\t') {
                /* layout: one space survives only between two word characters */
                size_t j = i;
                while (j < m && (s[j] == ' ' || s[j] == '\t')) j++;
                if (line.len && j < m && id_char(line.p[line.len - 1]) && id_char(s[j]))
                    nb_put(&line, " ", 1);
                i = j;
                continue;
            }
            if (s[i] == '"' || s[i] == '\'') {
                char q = s[i];
                size_t j = i + 1;
                while (j < m && s[j] != q) j += (s[j] == '\\' && j + 1 < m) ? 2 : 1;
                if (j < m) j++;
                nb_put(&line, s + i, j - i);
                i = j;
            } else if (id_start(s[i]) && (i == 0 || !id_char(s[i - 1]))) {
                size_t j = i;
                while (j < m && id_char(s[j])) j++;
                if (is_kept(s + i, j - i)) {
                    nb_put(&line, s + i, j - i);
                } else {
                    unsigned k = 0;
                    while (k < nn && (strncmp(names[k], s + i, j - i) || id_char(names[k][j - i]))) k++;
                    if (k == nn && nn < 256) names[nn++] = s + i;
                    char tok[16];
                    int w = snprintf(tok, sizeof tok, "$%u", k);
                    nb_put(&line, tok, (size_t)w);
                }
                i = j;
            } else {
                nb_put(&line, s + i, 1);
                i++;
            }
        }
        if (line.len) {
            h = fnv(h, line.p, line.len);
            h = fnv(h, "\n", 1);
        }
        if (!e) break;
        s = e + 1;
    }
    snprintf(out, 17, "%016llx", (unsigned long long)h);
    free(a.p);
    free(line.p);
}

/* ---- the canonical instances ----------------------------------------------- */

/* A scratch arena over malloc whose blocks are freed after the rendering.
 * The block table is heap too (a 4096-slot array was a 32 KB stack frame, R-28);
 * a refused table growth sets `full` like the cap does, a loud -1. */
enum { FH_MAXBLK = 4096 };
typedef struct { void **blk; unsigned n, cap; int full; } fh_arena;

static void *fh_alloc(void *u, size_t n)
{
    fh_arena *a = u;
    if (a->n == FH_MAXBLK) { a->full = 1; return NULL; }
    if (a->n == a->cap) {
        unsigned cap = a->cap ? a->cap * 2 : 64;
        void **q = realloc(a->blk, cap * sizeof *q);
        if (!q) { a->full = 1; return NULL; }
        a->blk = q;
        a->cap = cap;
    }
    void *p = calloc(1, n ? n : 1);
    if (p) a->blk[a->n++] = p;
    return p;
}

static void fh_free(fh_arena *a)
{
    for (unsigned i = 0; i < a->n; i++) free(a->blk[i]);
    free(a->blk);
    a->blk = NULL;
    a->n = a->cap = 0;
}

static void fh_puts(void *u, const char *s) { nb_put(u, s, strlen(s)); }
static void fh_vprintf(void *u, const char *fmt, va_list ap)
{
    char tmp[512];
    va_list cp;
    va_copy(cp, ap);
    int n = vsnprintf(tmp, sizeof tmp, fmt, cp);
    va_end(cp);
    if (n < 0) return;
    if ((size_t)n < sizeof tmp) { nb_put(u, tmp, (size_t)n); return; }
    char *big = malloc((size_t)n + 1);
    if (!big) { ((nbuf *)u)->oom = 1; return; }
    vsnprintf(big, (size_t)n + 1, fmt, ap);
    nb_put(u, big, (size_t)n);
    free(big);
}
static int fh_cmt_open(void *u, int tier) { (void)u; (void)tier; return 0; }

static const char *fh_table(void *u, uint32_t ref) { (void)u; (void)ref; return "mf_tbl"; }

/* A C string literal's BODY, escaped as pcrec_sb_cstr escapes it (the run
 * compare's literals: the sink's `cstr` op, memfn.h). */
static void fh_cstr(void *u, const uint8_t *b, size_t n)
{
    char buf[8];
    for (size_t i = 0; i < n; i++) {
        if (b[i] == '"' || b[i] == '\\' || b[i] == '?') snprintf(buf, sizeof buf, "\\%c", b[i]);
        else if (b[i] >= 32 && b[i] < 127) snprintf(buf, sizeof buf, "%c", b[i]);
        else snprintf(buf, sizeof buf, "\\%03o", b[i]);
        nb_put(u, buf, strlen(buf));
    }
}

/* The site's function name (a WINDOW site's handle prefix asks for one). */
static const char *fh_fn(void *u, uint32_t ref) { (void)u; (void)ref; return "mf_fn"; }

/* ---- THE ENTRY TABLE (span_cards.md §3.2, unit S2c) -------------------------
 *
 * One row per INSTANCE: an id's canonical instance (`canon` 1; `cls` "-" for
 * an id with one instance) and, for the verify forms, one per class. Each row
 * states the site shape, the facts, the TARGET (a kit token, the art's
 * mf_art_target, unit U2: timed and shipped text planned for one target,
 * target_seam.md §4) and the deny string; ONE renderer path (fh_render)
 * builds the site from them and reaches the form by the kit's own selection,
 * so the text mf_form_hash folds is the text a cell times. `row` is the
 * kit row the facts must reach (the composer's arm for a FIND, T-FIND's row
 * deciding a window's stop, T-CMP's row for a run): an instance whose facts
 * reach another is REFUSED (-1), never hashed as the id (a form no fact set
 * reaches is reported, never forced).
 *
 *   walk, libc   canon()'s two sites before S2c, byte for byte: their hashes
 *                did not move (grid1's and the interim sets' readers)
 *   pair         a window site's stop `{X,x}` at offset 0 (the window asker
 *                renders PAIR: T-FIND's PAIR row, E-find's two streams)
 *   settest      kit_set_test on the candidate's byte, by COMPARE count: c1 a
 *                singleton, c2 two singletons, cn three or more (\w: 7)
 *   rc-words     T-CMP `words` (a masked run), by WORD count: w1 one word (L 4),
 *                w2 two (L 3: two 2-byte words), w3 three (L 18: 8-byte words)
 *   rc-memcmp    T-CMP `memcmp` (an exact run at L 4, where `overlap` does not
 *                take it)
 * A caseless run states its letters' upper case under mask 0xDF (T & ~K must
 * be 0: run_pos_sat).
 *
 * `walk-set` (the walk over the two-member stop the composer would ask about)
 * is NOT an id: its site, the composer's FIND over `{X,x}` named by pcrec's
 * table, renders the walk's text byte for byte (the table carries the set,
 * not the text), so it hashes as `walk` and folds into it (span_cards.md
 * §2.4: the hash decides); with no table the composer renders the generic
 * byte loop, which is not the walk. */
static const char DIGITS[] = "0123456789";
static const char WORD[]   = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz";

static const mf_form_entry entries[] = {
    /* id          cls  canon shape          row          bytes                case tbl empty              leaves on_miss      target              deny */
    { "walk",      "-",  1, MF_FH_FIND,    "pf_walk",   DIGITS,               0, 1, MF_EMPTY_NOP,      0, NULL,        "generic",          NULL },
    { "libc",      "-",  1, MF_FH_FIND,    "pf_memchr", "x",                  0, 0, MF_EMPTY_EXCLUDED, 1, "return 0;", "generic",          NULL },
    { "pair",      "-",  1, MF_FH_WINDOW,  "PAIR",      "Xx",                 0, 0, MF_EMPTY_MISS,     0, NULL,        "generic",          NULL },
    { "settest",   "c1", 0, MF_FH_SETTEST, NULL,        "/",                  0, 0, 0,                 0, NULL,        "generic",          NULL },
    { "settest",   "c2", 1, MF_FH_SETTEST, NULL,        "Xx",                 0, 0, 0,                 0, NULL,        "generic",          NULL },
    { "settest",   "cn", 0, MF_FH_SETTEST, NULL,        WORD,                 0, 0, 0,                 0, NULL,        "generic",          NULL },
    { "rc-words",  "w1", 0, MF_FH_RUNCMP,  "words",     "USER",               1, 0, 0,                 0, NULL,        "generic",          NULL },
    { "rc-words",  "w2", 1, MF_FH_RUNCMP,  "words",     "ABC",                1, 0, 0,                 0, NULL,        "generic",          NULL },
    { "rc-words",  "w3", 0, MF_FH_RUNCMP,  "words",     "ABCDEFGHIJKLMNOPQR", 1, 0, 0,                 0, NULL,        "generic",          NULL },
    { "rc-memcmp", "l1", 1, MF_FH_RUNCMP,  "memcmp",    "/use",               0, 0, 0,                 0, NULL,        "generic",          NULL },
};
#define NENTRIES (sizeof entries / sizeof entries[0])

/* The site shapes: the word the slot harness reads, the kit entry that
 * reaches the form, and the C names the text reads and writes (one spelling
 * per shape, so a wrapper is one text per shape). */
static const mf_form_shape shapes[] = {
    [MF_FH_FIND]    = { "find-stmt",   "mf_emit (composer STMT/FIND/ASSIGN; the composer's arm table)",
                        "subject", "n", "pos", "pos", NULL },
    [MF_FH_WINDOW]  = { "window-find", "mf_emit (window REPORT STMT/FIND/ASSIGN; E-find, T-FIND on the stop)",
                        "subject", "n", "pos", "pos", NULL },
    [MF_FH_RUNCMP]  = { "cmp-expr",    "mf_emit (EXPR/VERIFY/BOOL, runcmp_arm; T-CMP) + mf_flush_helpers",
                        "subject", NULL, "pos", NULL, "pos" },
    [MF_FH_SETTEST] = { "cmp-expr",    "kit_set_test",
                        "subject", NULL, NULL, NULL, "pos" },
};

/* kit.h: the i-th instance, NULL past the last. */
const mf_form_entry *mf_form_entry_at(size_t i)
{
    return i < NENTRIES ? &entries[i] : NULL;
}

/* kit.h: an instance's site shape, NULL for none. */
const mf_form_shape *mf_form_shape_of(const mf_form_entry *e)
{
    return e && e->shape < sizeof shapes / sizeof shapes[0] ? &shapes[e->shape] : NULL;
}

/* kit.h: the instance of `id` in class `cls` (NULL: the canonical one). */
const mf_form_entry *mf_form_entry_of(const char *id, const char *cls)
{
    for (size_t i = 0; id && i < NENTRIES; i++)
        if (!strcmp(entries[i].id, id) && (cls ? !strcmp(entries[i].cls, cls) : entries[i].canon))
            return &entries[i];
    return NULL;
}

/* The 256-bit set of entry `e`'s bytes. */
static void fh_set(const mf_form_entry *e, uint8_t set[32])
{
    memset(set, 0, 32);
    for (const char *p = e->bytes; *p; p++)
        set[(unsigned char)*p >> 3] |= (uint8_t)(1u << ((unsigned char)*p & 7));
}

/* A RUN term of entry `e` at offset 0: its bytes and, caseless, the mask
 * 0xDF at every letter (the case bit a don't-care), 0xFF elsewhere. */
static void fh_run(const mf_form_entry *e, mf_term *t, uint8_t *mask)
{
    size_t L = strlen(e->bytes);
    for (size_t i = 0; i < L; i++) {
        unsigned char c = (unsigned char)e->bytes[i];
        mask[i] = e->caseless && ((c | 0x20) >= 'a' && (c | 0x20) <= 'z') ? 0xDF : 0xFF;
    }
    t->kind = MF_T_RUN;
    t->need = MF_REQUIRED;
    t->ppm_hi = MF_PPM_FULL;
    t->run = (const uint8_t *)e->bytes;
    t->mask = e->caseless ? mask : NULL;
    t->run_len = (uint32_t)L;
}

/* The scratch of one rendering, on the heap (an mf_site and a window span
 * are a few KB together: R-28's 4 KB frame bar). */
typedef struct {
    mf_site  s;
    mf_hooks h;
    mf_wspan sp;
    mf_walt  al;
    mf_result res;                  /* its class alone is ~3 KB */
    uint8_t  mask[64];              /* a RUN entry's mask (fh_run) */
} fh_work;

/* The common site facts every shape states. */
static void fh_site(const mf_form_entry *e, mf_site *s)
{
    s->abi = MF_SITE_ABI;
    s->use = MF_USE_POSITION;
    s->ret_pred = MF_NO_PRED;
    s->span_hi = MF_SPAN_UNBOUNDED;
    s->cand_ppm_hi = MF_PPM_FULL;
    s->opts = e->deny;
    s->body = MF_BODY_ONESHOT;
    s->pred.plan_hint = MF_NO_PRED;
}

/* THE ONE RENDERER: entry `e`'s site text (the file sink's text, then the
 * body's) into `all`, and the kit row its facts reached into *row (NULL:
 * the shape has no row). 0, or -1 (a kit refusal, a scratch failure, or a
 * row other than the entry's). */
static int fh_render(const mf_form_entry *e, nbuf *all, const char **row, size_t *flen)
{
    fh_work *w = calloc(1, sizeof *w);
    if (!w) return -1;
    fh_arena fa = { 0 };
    mf_arena ar = { &fa, fh_alloc };
    nbuf body = { 0 }, file = { 0 };
    mf_sink sb = { .u = &body, .puts = fh_puts, .vprintf = fh_vprintf, .cmt_open = fh_cmt_open,
                   .cstr = fh_cstr };
    mf_sink sf = { .u = &file, .puts = fh_puts, .vprintf = fh_vprintf, .cmt_open = fh_cmt_open,
                   .cstr = fh_cstr };
    const mf_form_shape *sh = &shapes[e->shape];
    mf_site *s = &w->s;
    mf_hooks *h = &w->h;
    mf_result *res = &w->res;
    int rc = 1;
    *row = NULL;
    mf_art *art = mf_art_begin(&ar, "mf", 0, NULL, NULL);
    if (!art) goto out;
    if (mf_art_target(art, mf_target_parse(e->target, strlen(e->target), NULL, 0))) goto out;
    h->s = sh->s;
    h->n = sh->n;
    h->lo = e->shape == MF_FH_RUNCMP ? sh->cand : sh->lo;
    h->result = sh->result;
    h->indent = "";
    switch ((mf_form_shape_id)e->shape) {
    case MF_FH_FIND:
        /* canon()'s site: FIND / STMT / ASSIGN over one SET term at offset 0
           (the PF shape) */
        fh_site(e, s);
        s->form = MF_FORM_STMT;
        s->op = MF_OP_FIND;
        s->handoff = MF_H_ASSIGN;
        s->empty = e->empty;
        s->on_miss_leaves = e->leaves;
        s->pred.nterm = 1;
        s->pred.need = MF_REQUIRED;
        s->pred.span_class = MF_SPAN_BOUNDED;       /* span 0 (MF_SITE_ABI 18) */
        s->pred.term[0].kind = MF_T_SET;
        s->pred.term[0].need = MF_REQUIRED;
        s->pred.term[0].ppm_hi = MF_PPM_FULL;
        fh_set(e, s->pred.term[0].set);
        s->pred.term[0].table_ref = e->table;
        h->miss = MF_MISS_N;
        h->on_miss = e->on_miss;
        h->table_name = e->table ? fh_table : NULL;
        if (mf_emit(art, s, h, &sb, &sf, res) || mf_art_end(art, NULL)) goto out;
        *row = art->sites[res->handle - 1].arm->id;
        break;
    case MF_FH_WINDOW:
        /* a window site whose one span is the stop at offset 0, verify YES,
           its core the stop: the window asker (renders_pair) */
        fh_site(e, s);
        s->form = MF_FORM_STMT;
        s->op = MF_OP_FIND;
        s->handoff = MF_H_ASSIGN;
        s->empty = e->empty;
        s->site_kind = MF_SK_REPORT;
        s->pred.fn_ref = 1;
        s->wfloor = MF_WFLOOR_SUBJECT;
        w->sp.start = 0;
        w->sp.len = 1;
        w->sp.verify = MF_VERIFY_YES;
        w->sp.core = MF_CORE_STATED;
        w->sp.core_lo = 0;
        w->sp.core_len = 1;
        fh_set(e, w->sp.set[0]);
        w->al.entry = MF_ENTRY_NONE;
        w->al.nspan = 1;
        w->al.spans = &w->sp;
        s->nalt = 1;
        s->alts = &w->al;
        h->miss = MF_MISS_N;
        h->fn_name = fh_fn;
        if (mf_emit(art, s, h, &sb, &sf, res) || mf_art_end(art, NULL)) goto out;
        {
            const site_rec *r = &art->sites[res->handle - 1];
            *row = r->wplan ? wf_plan_brow(r->wplan) : NULL;
        }
        break;
    case MF_FH_RUNCMP:
        /* the run compare's own site: one RUN term behind the caller's
           guard; its word loads declared into the file sink after the use */
        fh_site(e, s);
        s->form = MF_FORM_EXPR;
        s->op = MF_OP_VERIFY;
        s->handoff = MF_H_BOOL;
        s->guard_by_caller = 1;
        s->pred.nterm = 1;
        s->pred.need = MF_REQUIRED;
        if (strlen(e->bytes) > sizeof w->mask) goto out;
        fh_run(e, &s->pred.term[0], w->mask);
        if (mf_emit(art, s, h, &sb, &sf, res) || mf_flush_helpers(art, &sf) ||
            mf_art_end(art, NULL))
            goto out;
        /* the arm that rendered must be the run compare's (an earlier arm of
           the composer's table claiming the site would render another text
           under this row's name); then T-CMP's row, re-read off the term */
        if (art->sites[res->handle - 1].arm != &runcmp_arm) goto out;
        *row = run_cmp_row(art, &s->pred.term[0]);
        break;
    case MF_FH_SETTEST: {
        /* the kit's own membership test of the candidate's byte: a LEAF
           render, no site and no selection (row NULL: no row to reach) */
        uint8_t set[32];
        kb b;
        fh_set(e, set);
        kb_init(&b, &ar);
        kb_printf(&b, "%s[%s]", sh->s, sh->cand);
        const char *byte = b.p;
        kb_init(&b, &ar);
        if (!byte || !kit_set_test(&b, set, byte) || b.oom || !b.p) goto out;
        fh_puts(&body, b.p);
        break;
    }
    }
    if (e->row && (!*row || strcmp(*row, e->row))) goto out;    /* reached another row */
    rc = fa.full || body.oom || file.oom;
    if (!rc) {
        if (file.len) nb_put(all, file.p, file.len);
        if (flen) *flen = file.len;
        if (body.len) nb_put(all, body.p, body.len);
        rc = all->oom;
    }
out:
    free(body.p);
    free(file.p);
    fh_free(&fa);
    free(w);
    return rc ? -1 : 0;
}

/* kit.h: the instance's site text and the length of its FILE part. */
int mf_form_site_split(const char *id, const char *cls, char **out, size_t *file_len)
{
    const mf_form_entry *e = mf_form_entry_of(id, cls);
    const char *row;
    nbuf all = { 0 };
    *out = NULL;
    *file_len = 0;
    if (!e || fh_render(e, &all, &row, file_len)) {
        free(all.p);
        return -1;
    }
    if (!all.p) nb_put(&all, "", 0);
    if (all.oom) return -1;
    *out = all.p;
    return 0;
}

/* kit.h: the instance's site text. */
int mf_form_site_text(const char *id, const char *cls, char **out)
{
    size_t flen;
    return mf_form_site_split(id, cls, out, &flen);
}

/* kit.h: the kit row the instance's facts reached ("-": none); renders the
 * whole site to read it (a test entry, never on a production path). */
const char *mf_form_row(const char *id, const char *cls)
{
    const mf_form_entry *e = mf_form_entry_of(id, cls);
    const char *row;
    nbuf all = { 0 };
    int rc = !e || fh_render(e, &all, &row, NULL);
    free(all.p);
    return rc ? NULL : row ? row : "-";
}

/* kit.h: the hash of ONE instance's site text (the cell-text check's). */
int mf_form_hash_cls(const char *id, const char *cls, char out[17])
{
    char *text;
    if (mf_form_site_text(id, cls, &text)) return -1;
    mf_form_hash_text(text, out);
    free(text);
    return 0;
}

/* memfn.h: the hash of the id's instances, one text: every instance's site
 * text in table order, a newline between two (one instance: its own text, so
 * walk's and libc's hashes are their single instance's). */
int mf_form_hash(const char *form_id, char out[17])
{
    nbuf all = { 0 };
    int n = 0;
    for (size_t i = 0; form_id && i < NENTRIES; i++) {
        char *t;
        if (strcmp(entries[i].id, form_id)) continue;
        if (mf_form_site_text(entries[i].id, entries[i].cls, &t)) {
            free(all.p);
            return -1;
        }
        if (n++) nb_put(&all, "\n", 1);
        nb_put(&all, t, strlen(t));
        free(t);
    }
    if (!n || all.oom) {
        free(all.p);
        return -1;
    }
    mf_form_hash_text(all.p ? all.p : "", out);
    free(all.p);
    return 0;
}
