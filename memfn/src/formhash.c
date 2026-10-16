/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/formhash.c — FORM HASHES (R-MS3, R17-b' B1; measure_sets.md §2.4,
 * r17b_prime.md §4.7): `mf_form_hash(form_id)`, the hash of a form's
 * CANONICAL INSTANCE with its scaffolding normalized out, which a measurement
 * set's `deps` column records and staleness compares (pcrec compares the
 * strings and nothing else).
 *
 * THE CANONICAL INSTANCE. A form's text for ONE fixed site of the form,
 * rendered through the kit's own public entries (mf_art_begin, mf_emit) in a
 * scratch art over a scratch arena: the fixed set (`[0-9]` for a set form,
 * the byte `x` for a one-byte form), the fixed span (the whole subject) and
 * the fixed prefix (`mf`). A form id this kit does not render (V1 until B4,
 * the W64 forms until B6, NONE until B5, the dispatch twin) is refused (-1),
 * never hashed as something else.
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
    const char *names[256];
    size_t nlen[256];
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
                    while (k < nn && !(nlen[k] == j - i && !strncmp(names[k], s + i, j - i))) k++;
                    if (k == nn && nn < 256) { names[nn] = s + i; nlen[nn] = j - i; nn++; }
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

/* A scratch arena over malloc whose blocks are freed after the rendering. */
enum { FH_MAXBLK = 4096 };
typedef struct { void *blk[FH_MAXBLK]; unsigned n; int full; } fh_arena;

static void *fh_alloc(void *u, size_t n)
{
    fh_arena *a = u;
    if (a->n == FH_MAXBLK) { a->full = 1; return NULL; }
    void *p = calloc(1, n ? n : 1);
    if (p) a->blk[a->n++] = p;
    return p;
}

static void fh_free(fh_arena *a)
{
    for (unsigned i = 0; i < a->n; i++) free(a->blk[i]);
    a->n = 0;
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

/* The canonical site of form `id`: FIND / STMT / ASSIGN over one SET term at
 * offset 0 (the PF shape), the walk's set `[0-9]` named by a table, the libc
 * form's one byte `x`. 0 and the site and hooks, or -1 for an id no kit row
 * renders. */
static int canon(const char *id, mf_site *s, mf_hooks *h)
{
    int walk = !strcmp(id, "walk"), libc = !strcmp(id, "libc");
    if (!walk && !libc) return -1;
    memset(s, 0, sizeof *s);
    memset(h, 0, sizeof *h);
    s->abi = MF_SITE_ABI;
    s->form = MF_FORM_STMT;
    s->op = MF_OP_FIND;
    s->handoff = MF_H_ASSIGN;
    s->empty = walk ? MF_EMPTY_NOP : MF_EMPTY_EXCLUDED;
    s->on_miss_leaves = libc;
    s->use = MF_USE_POSITION;
    s->consumer = MF_C_ENGINE;
    s->ret_pred = MF_NO_PRED;
    s->span_hi = MF_SPAN_UNBOUNDED;
    s->cand_ppm_hi = MF_PPM_FULL;
    s->policy = MF_P_PORTABLE_ONLY;
    s->body = MF_BODY_ONESHOT;
    s->pred.nterm = 1;
    s->pred.need = MF_REQUIRED;
    s->pred.plan_hint = MF_NO_PRED;
    s->pred.window_stated = 1;
    mf_term *t = &s->pred.term[0];
    t->kind = MF_T_SET;
    t->need = MF_REQUIRED;
    t->ppm_hi = MF_PPM_FULL;
    if (walk) {
        for (unsigned b = '0'; b <= '9'; b++) t->set[b >> 3] |= (uint8_t)(1u << (b & 7));
        t->table_ref = 1;
    } else {
        t->set['x' >> 3] |= (uint8_t)(1u << ('x' & 7));
    }
    h->s = "subject";
    h->n = "n";
    h->lo = "pos";
    h->result = "pos";
    h->miss = MF_MISS_N;
    h->on_miss = libc ? "return 0;" : NULL;
    h->table_name = walk ? fh_table : NULL;
    h->indent = "";
    return 0;
}

int mf_form_hash(const char *form_id, char out[17])
{
    mf_site s;
    mf_hooks h;
    if (!form_id || canon(form_id, &s, &h)) return -1;
    fh_arena fa = { .n = 0 };
    mf_arena ar = { &fa, fh_alloc };
    nbuf body = { 0 }, file = { 0 };
    mf_sink sb = { .u = &body, .puts = fh_puts, .vprintf = fh_vprintf, .cmt_open = fh_cmt_open };
    mf_sink sf = { .u = &file, .puts = fh_puts, .vprintf = fh_vprintf, .cmt_open = fh_cmt_open };
    mf_art *art = mf_art_begin(&ar, "mf", MF_P_PORTABLE_ONLY, 0, NULL, NULL);
    int rc = !art || mf_emit(art, &s, &h, &sb, &sf, NULL) || mf_art_end(art, NULL)
          || fa.full || body.oom || file.oom;
    if (!rc) {
        nbuf all = { 0 };
        if (file.len) nb_put(&all, file.p, file.len);
        if (body.len) nb_put(&all, body.p, body.len);
        if (all.oom) rc = 1;
        else mf_form_hash_text(all.p ? all.p : "", out);
        free(all.p);
    }
    free(body.p);
    free(file.p);
    fh_free(&fa);
    return rc ? -1 : 0;
}
