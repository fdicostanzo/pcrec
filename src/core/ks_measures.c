/* src/core/ks_measures.c — [MEASURE-SET] M0 the MEASURES kind's row
 * (docs/design/measure_sets.md rev 3 §1, §9.2, §9.5, §9.6;
 * docs/spec/measures.md is the contract): the set file's parse and
 * validation (§1.6's checks), its values digest, its two views (the
 * CANONICAL writer, whose output IS a loadable set, and the DECODED writer,
 * the loaded document field by field for R5), and the `-I` file probe.
 *
 * DEPENDENCY RULE (§9.2, S989): libc and `core/ksrc.h`/`core/ks_measures.h`
 * only. Allocation is the caller's `KsAlloc`; refusals are `KsErr` text. The
 * library tier (src/core/measures.c) adds the store, the resolution and the
 * compile's stamp; this file knows none of them, so the embed generator and
 * a future `pcrec-measure` link it alone. */

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/ks_measures.h"
#include "core/ksrc.h"

/* ---- the spec's closed vocabularies ---------------------------------- */

/* §1.6's code table: a unit or status is a spec row with its own byte, never
 * 0 and never reused. `ratio` is the only unit a unit row may have. */
static const struct { const char *name; uint8_t code; } meas_units[] = {
    { "ratio", 0x01 }, { "walkbytes", 0x02 }, { "bytes", 0x03 }, { "count", 0x04 },
};
enum { MEAS_STATUS_MEASURED = 0x01, MEAS_STATUS_FITTED = 0x02,
       MEAS_STATUS_DERIVED = 0x03, MEAS_STATUS_NULL = 0x04 };
static const struct { const char *name; uint8_t code; } meas_statuses[] = {
    { "measured", MEAS_STATUS_MEASURED }, { "fitted", MEAS_STATUS_FITTED },
    { "derived", MEAS_STATUS_DERIVED },   { "null", MEAS_STATUS_NULL },
};
/* The derivation registry (measure_sets.md §1.6): the names a derived or fitted row may
 * carry. `ratio-complement` (1 - a/b) is the kit's `saving` derivation. */
static const char *const meas_derivations[] = {
    "ratio", "ratio-complement", "diff", "cross-lin", "step", "min", "max",
    "interp-log2", "env-max", "env-min",
};
static const char *const meas_owners[] = { "kit", "pcrec" };
static const char *const meas_tiers[] = { "scratch", "official", "local", "synthetic" };
/* The sections a set may carry, in the canonical writer's order. */
static const char *const meas_sections[] = { "header", "cards", "rows", "cells", "members" };
/* The DERIVED views' section names (§9.5's last row): a file carrying one is
 * a listing fed back and is refused. */
static const char *const meas_derived[] = { "decoded", "item", "readers", "stale", "sets", NULL };

#define NELEM(a) (sizeof (a) / sizeof *(a))

static bool in_list(const char *const *l, size_t n, const char *s)
{
    for (size_t i = 0; i < n; i++)
        if (!strcmp(l[i], s)) return true;
    return false;
}

static uint8_t code_of(const char *s, bool unit)
{
    if (unit) {
        for (size_t i = 0; i < NELEM(meas_units); i++)
            if (!strcmp(meas_units[i].name, s)) return meas_units[i].code;
    } else {
        for (size_t i = 0; i < NELEM(meas_statuses); i++)
            if (!strcmp(meas_statuses[i].name, s)) return meas_statuses[i].code;
    }
    return 0;
}

static const char *const meas_hdr_names[KS_MEAS_NHDR] = {
#define X(id, name, req) name,
    KS_MEAS_HEADER(X)
#undef X
};
static const bool meas_hdr_req[KS_MEAS_NHDR] = {
#define X(id, name, req) req,
    KS_MEAS_HEADER(X)
#undef X
};
#define X(c) #c,
static const char *const card_cols[] = { KS_MEAS_CARD_COLS(X) };
static const char *const row_cols[] = { KS_MEAS_ROW_COLS(X) };
static const char *const cell_cols[] = { KS_MEAS_CELL_COLS(X) };
static const char *const member_cols[] = { KS_MEAS_MEMBER_COLS(X) };
#undef X

/* ---- small parsers ---------------------------------------------------- */

static int mfail(KsErr *err, const char *where, const char *fmt, ...)
    __attribute__((format(printf, 3, 4)));
static int mfail(KsErr *err, const char *where, const char *fmt, ...)
{
    va_list ap;
    int n = snprintf(err->msg, sizeof err->msg, "%s: ", where);
    if (n < 0 || (size_t)n >= sizeof err->msg) n = 0;
    va_start(ap, fmt);
    vsnprintf(err->msg + n, sizeof err->msg - (size_t)n, fmt, ap);
    va_end(ap);
    return -1;
}

/* A decimal integer in its ONE spelling (§9.6: no '+', no leading zero, no
 * "-0"), into `*v`. */
static bool dec_i64(const char *s, int64_t *v)
{
    const char *d = s + (*s == '-');
    unsigned long long m = 0;
    if (!*d || (d[0] == '0' && (d[1] || *s == '-'))) return false;
    for (; *d; d++) {
        if (*d < '0' || *d > '9') return false;
        if (m > (9223372036854775807ull - (unsigned)(*d - '0')) / 10 + 1) return false;
        m = m * 10 + (unsigned)(*d - '0');
    }
    if (*s == '-') {
        if (m > 9223372036854775808ull) return false;
        *v = m == 9223372036854775808ull ? INT64_MIN : -(int64_t)m;
    } else {
        if (m > 9223372036854775807ull) return false;
        *v = (int64_t)m;
    }
    return true;
}

/* §1.3's key grammar: owner "." quantity { "." token }; returns the token
 * count (the arity), or -1. `owner`/`quantity` receive copies' lengths. */
static int key_parse(const char *k, size_t *olen, size_t *qlen)
{
    const char *dot = strchr(k, '.'), *q, *e;
    int ntok = 0;
    if (!dot) return -1;
    *olen = (size_t)(dot - k);
    q = dot + 1;
    if (*q < 'a' || *q > 'z') return -1;
    for (e = q + 1; *e && *e != '.'; e++)
        if (!((*e >= 'a' && *e <= 'z') || (*e >= '0' && *e <= '9') || *e == '_'))
            return -1;
    *qlen = (size_t)(e - q);
    while (*e == '.') {
        const char *t = ++e;
        for (; *e && *e != '.'; e++)
            if (!((*e >= 'a' && *e <= 'z') || (*e >= 'A' && *e <= 'Z') ||
                  (*e >= '0' && *e <= '9') || *e == '_' || *e == '+' || *e == '-'))
                return -1;
        if (e == t || (e - t == 1 && *t == '-')) return -1;
        ntok++;
    }
    return *e ? -1 : ntok;
}

/* A card's `dims` count: `-` or empty is none, else the `;`-joined names. */
static int dims_count(const char *d)
{
    int n = 1;
    if (!*d || !strcmp(d, "-")) return 0;
    for (; *d; d++) n += *d == ';';
    return n;
}

/* ---- the document's order (§1.7) -------------------------------------- */

static int row_cmp(const void *a, const void *b)
{
    return strcmp(((const KsMeasRow *)a)->col[KS_MR_key],
                  ((const KsMeasRow *)b)->col[KS_MR_key]);
}

/* qsort has no context argument, so the cells-held sort compares rows of a
 * width carried in a wrapper. */
typedef struct { size_t w; const char *const *c; } TabRow;
static int tab_cmp(const void *a, const void *b)
{
    const TabRow *x = a, *y = b;
    for (size_t i = 0; i < x->w; i++) {
        int r = strcmp(x->c[i], y->c[i]);
        if (r) return r;
    }
    return 0;
}

/* Copies section `s`'s columns `want[0..w)` (resolved BY NAME) into a
 * cells-held table in bytewise row order; a missing column refuses. */
static int tab_load(const KsAlloc *a, const KsTsvSection *s, const char *const *want,
                    size_t w, KsMeasTab *t, const char *where, KsErr *err)
{
    long ix[16];
    TabRow *rows;
    const char **cells;
    t->nrows = 0;
    t->cells = NULL;
    if (!s || !s->ncols) return 0;
    for (size_t j = 0; j < w; j++)
        if ((ix[j] = pcrec_ks_tsv_col(s, want[j])) < 0)
            return mfail(err, where, "section '%s' has no column '%s'", s->name, want[j]);
    rows = a->alloc(a->ctx, (s->nrows + 1) * sizeof *rows);
    cells = a->alloc(a->ctx, (s->nrows * w + 1) * sizeof *cells);
    for (size_t r = 0; r < s->nrows; r++) {
        for (size_t j = 0; j < w; j++)
            cells[r * w + j] = s->cells[r * s->ncols + (size_t)ix[j]];
        rows[r] = (TabRow){ w, cells + r * w };
    }
    qsort(rows, s->nrows, sizeof *rows, tab_cmp);
    {
        const char **sorted = a->alloc(a->ctx, (s->nrows * w + 1) * sizeof *sorted);
        for (size_t r = 0; r < s->nrows; r++)
            memcpy(sorted + r * w, rows[r].c, w * sizeof *sorted);
        t->cells = sorted;
    }
    t->nrows = s->nrows;
    return 0;
}

/* ---- the digest (§1.6) ------------------------------------------------- */

static uint64_t meas_fold(uint64_t h, const void *doc, const char *subkey)
{
    const KsMeasSet *set = doc;
    (void)subkey;
    for (size_t i = 0; i < set->nrows; i++) {
        const KsMeasRow *r = &set->rows[i];
        unsigned char b[10];
        uint64_t v = (uint64_t)r->value_e6;
        h = pcrec_ks_fnv1a(h, r->col[KS_MR_key], strlen(r->col[KS_MR_key]) + 1);
        b[0] = r->unit_code;
        b[1] = r->status_code;
        for (int k = 0; k < 8; k++) b[2 + k] = (unsigned char)(v >> (8 * k));
        h = pcrec_ks_fnv1a(h, b, sizeof b);
    }
    return h;
}

const KsDigest pcrec_ks_meas_values_role = {
    KS_DOMAIN("pcrec-meas-1"), KS_SUB_NONE, meas_fold
};

uint64_t pcrec_ks_meas_digest(const KsMeasSet *set)
{
    return pcrec_ks_digest(&pcrec_ks_meas_values_role, set, NULL);
}

void pcrec_ks_meas_hex(uint64_t d, char out[17])
{
    snprintf(out, 17, "%016llx", (unsigned long long)d);
}

const char *pcrec_ks_meas_stamp(const KsAlloc *a, const KsMeasSet *set)
{
    char hex[17], *s;
    int n;
    pcrec_ks_meas_hex(set->digest, hex);
    n = snprintf(NULL, 0, "%s@%u:%s", set->hdr[KS_MH_ID], set->rev, hex);
    s = a->alloc(a->ctx, (size_t)n + 1);
    snprintf(s, (size_t)n + 1, "%s@%u:%s", set->hdr[KS_MH_ID], set->rev, hex);
    return s;
}

/* ---- the parse and its checks (§1.6; the spec's failure table) --------- */

/* The header section into `set->hdr`: every key known, none twice. */
static int load_header(const KsTsvSection *s, KsMeasSet *set, const char *where,
                       KsErr *err)
{
    long ck, cv;
    for (int i = 0; i < KS_MEAS_NHDR; i++) set->hdr[i] = NULL;
    if (!s || (ck = pcrec_ks_tsv_col(s, "key")) < 0 ||
        (cv = pcrec_ks_tsv_col(s, "value")) < 0)
        return mfail(err, where, "no 'header' section with 'key' and 'value' columns");
    for (size_t r = 0; r < s->nrows; r++) {
        const char *k = s->cells[r * s->ncols + (size_t)ck];
        int i = 0;
        while (i < KS_MEAS_NHDR && strcmp(meas_hdr_names[i], k)) i++;
        if (i == KS_MEAS_NHDR)
            return mfail(err, where, "line %zu: unknown header key '%s'", s->row_line[r], k);
        if (set->hdr[i])
            return mfail(err, where, "line %zu: header key '%s' appears twice", s->row_line[r], k);
        set->hdr[i] = s->cells[r * s->ncols + (size_t)cv];
    }
    for (int i = 0; i < KS_MEAS_NHDR; i++) {
        if (!set->hdr[i]) set->hdr[i] = "";
        if (meas_hdr_req[i] && !*set->hdr[i])
            return mfail(err, where, "header key '%s' is missing or empty", meas_hdr_names[i]);
    }
    return 0;
}

/* The header's own values: format, id, rev, tier, the flags, the digest's
 * spelling. */
static int check_header(KsMeasSet *set, const char *where, KsErr *err)
{
    const char *const *h = set->hdr;
    int64_t v;
    if (strcmp(h[KS_MH_FORMAT], "1"))
        return mfail(err, where, "format %s (this pcrec reads format 1)", h[KS_MH_FORMAT]);
    if (!pcrec_ks_name_ok(h[KS_MH_ID], strlen(h[KS_MH_ID])))
        return mfail(err, where, "id '%s' is not a set name ([a-z][a-z0-9_-]*)", h[KS_MH_ID]);
    if (!dec_i64(h[KS_MH_REV], &v) || v < 1 || v > 0xffffffffll)
        return mfail(err, where, "rev '%s' is not a positive decimal", h[KS_MH_REV]);
    set->rev = (uint32_t)v;
    if (!in_list(meas_tiers, NELEM(meas_tiers), h[KS_MH_TIER]))
        return mfail(err, where, "tier '%s' (scratch, official, local, synthetic)", h[KS_MH_TIER]);
    if (strcmp(h[KS_MH_COMPOSITE], "0") && strcmp(h[KS_MH_COMPOSITE], "1"))
        return mfail(err, where, "composite '%s' (0 or 1)", h[KS_MH_COMPOSITE]);
    set->composite = h[KS_MH_COMPOSITE][0] == '1';
    if (*h[KS_MH_PARTIAL] && strcmp(h[KS_MH_PARTIAL], "0") && strcmp(h[KS_MH_PARTIAL], "1"))
        return mfail(err, where, "partial '%s' (0 or 1)", h[KS_MH_PARTIAL]);
    {
        const char *d = h[KS_MH_VALUES_DIGEST];
        bool ok = strlen(d) == 16;
        uint64_t x = 0;
        for (size_t i = 0; ok && i < 16; i++) {
            int c = d[i];
            ok = (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f');
            x = x << 4 | (uint64_t)(c <= '9' ? c - '0' : c - 'a' + 10);
        }
        if (!ok)
            return mfail(err, where, "values_digest '%s' is not 16 lowercase hex", d);
        set->digest = x;
    }
    return 0;
}

/* The `rows` section into `set->rows`, typed, in canonical order. */
static int load_rows(const KsAlloc *a, const KsTsvSection *s, KsMeasSet *set,
                     const char *where, KsErr *err)
{
    long ix[KS_MEAS_NROWCOL];
    KsMeasRow *rows;
    set->nrows = 0;
    set->rows = NULL;
    if (!s || !s->ncols) return 0;
    for (size_t j = 0; j < KS_MEAS_NROWCOL; j++)
        if ((ix[j] = pcrec_ks_tsv_col(s, row_cols[j])) < 0)
            return mfail(err, where, "section 'rows' has no column '%s'", row_cols[j]);
    rows = a->alloc(a->ctx, (s->nrows + 1) * sizeof *rows);
    for (size_t r = 0; r < s->nrows; r++) {
        KsMeasRow *m = &rows[r];
        size_t ln = s->row_line[r];
        for (size_t j = 0; j < KS_MEAS_NROWCOL; j++)
            m->col[j] = s->cells[r * s->ncols + (size_t)ix[j]];
        if (!(m->unit_code = code_of(m->col[KS_MR_unit], true)))
            return mfail(err, where, "line %zu: unit '%s' is not in the unit table",
                         ln, m->col[KS_MR_unit]);
        if (!(m->status_code = code_of(m->col[KS_MR_status], false)))
            return mfail(err, where, "line %zu: status '%s' (measured, fitted, derived, null)",
                         ln, m->col[KS_MR_status]);
        if (!*m->col[KS_MR_value_e6]) {
            if (m->status_code != MEAS_STATUS_NULL)
                return mfail(err, where, "line %zu: an empty value_e6 on a %s row "
                             "(only a null row has none)", ln, m->col[KS_MR_status]);
            m->value_e6 = KS_MEAS_EMPTY;
        } else if (m->status_code == MEAS_STATUS_NULL) {
            return mfail(err, where, "line %zu: a null row carries value_e6 %s",
                         ln, m->col[KS_MR_value_e6]);
        } else if (!dec_i64(m->col[KS_MR_value_e6], &m->value_e6) ||
                   m->value_e6 == KS_MEAS_EMPTY) {
            return mfail(err, where, "line %zu: value_e6 '%s' is not an integer in "
                         "its one decimal spelling", ln, m->col[KS_MR_value_e6]);
        }
    }
    qsort(rows, s->nrows, sizeof *rows, row_cmp);
    set->rows = rows;
    set->nrows = s->nrows;
    return 0;
}

/* The card for `owner.quantity`, or NULL; two cards for one quantity
 * refuse (a set is one method version). */
static const char *const *card_of(const KsMeasSet *set, const char *k, size_t olen,
                                  size_t qlen, bool *twice)
{
    const char *const *hit = NULL;
    *twice = false;
    for (size_t i = 0; i < set->cards.nrows; i++) {
        const char *const *c = set->cards.cells + i * KS_MEAS_NCARD;
        if (strlen(c[0]) == olen && !memcmp(c[0], k, olen) &&
            strlen(c[1]) == qlen && !memcmp(c[1], k + olen + 1, qlen)) {
            if (hit) *twice = true;
            hit = c;
        }
    }
    return hit;
}

static bool is_row_key(const KsMeasSet *set, const char *k)
{
    size_t lo = 0, hi = set->nrows;
    while (lo < hi) {
        size_t mid = (lo + hi) / 2;
        int c = strcmp(set->rows[mid].col[KS_MR_key], k);
        if (!c) return true;
        if (c < 0) lo = mid + 1; else hi = mid;
    }
    return false;
}

static bool is_cell_id(const KsMeasSet *set, const char *id, size_t n)
{
    for (size_t i = 0; i < set->cells.nrows; i++) {
        const char *c = set->cells.cells[i * KS_MEAS_NCELL];
        if (strlen(c) == n && !memcmp(c, id, n)) return true;
    }
    return false;
}

/* Every per-row rule of §1.6, the unit row, the count and the digest. */
static int check_rows(const KsAlloc *a, const KsMeasSet *set, const char *where,
                      KsErr *err)
{
    const KsMeasRow *unit = NULL;
    int64_t declared;
    for (size_t i = 0; i < set->cards.nrows; i++) {
        const char *const *c = set->cards.cells + i * KS_MEAS_NCARD;
        if (!in_list(meas_owners, NELEM(meas_owners), c[0]))
            return mfail(err, where, "card %s.%s: owner '%s' (kit, pcrec)", c[0], c[1], c[0]);
    }
    for (size_t i = 0; i < set->nrows; i++) {
        const KsMeasRow *r = &set->rows[i];
        const char *k = r->col[KS_MR_key], *d = r->col[KS_MR_derivation];
        size_t olen, qlen;
        int ar = key_parse(k, &olen, &qlen);
        bool twice, computed = r->status_code == MEAS_STATUS_DERIVED ||
                                r->status_code == MEAS_STATUS_FITTED;
        const char *const *card;
        if (i && !strcmp(set->rows[i - 1].col[KS_MR_key], k))
            return mfail(err, where, "key '%s' appears twice", k);
        if (ar < 0)
            return mfail(err, where, "key '%s' breaks the key grammar "
                         "(owner.quantity{.token})", k);
        {
            char o[16];
            if (olen >= sizeof o) olen = sizeof o - 1;
            memcpy(o, k, olen);
            o[olen] = 0;
            if (!in_list(meas_owners, NELEM(meas_owners), o))
                return mfail(err, where, "key '%s': owner '%s' (kit, pcrec)", k, o);
        }
        card = card_of(set, k, olen, qlen, &twice);
        if (!card)
            return mfail(err, where, "key '%s' has no card for %.*s", k, (int)(olen + 1 + qlen), k);
        if (twice)
            return mfail(err, where, "two cards for %.*s (a set is one method version)",
                         (int)(olen + 1 + qlen), k);
        if (ar != dims_count(card[3]))
            return mfail(err, where, "key '%s' has %d dimension tokens where its card's "
                         "dims '%s' declares %d", k, ar, card[3], dims_count(card[3]));
        if (computed) {
            if (!in_list(meas_derivations, NELEM(meas_derivations), d))
                return mfail(err, where, "key '%s': derivation '%s' is not in the "
                             "registry", k, d);
        } else if (*d && strcmp(d, "-")) {
            return mfail(err, where, "key '%s': a %s row names derivation '%s'",
                         k, r->col[KS_MR_status], d);
        }
        {
            const char *in = r->col[KS_MR_inputs];
            if (*in && strcmp(in, "-")) {
                if (!computed)
                    return mfail(err, where, "key '%s': a %s row names inputs",
                                 k, r->col[KS_MR_status]);
                for (const char *p = in; *p;) {
                    const char *e = strchr(p, ';');
                    size_t n = e ? (size_t)(e - p) : strlen(p);
                    char *one = a->alloc(a->ctx, n + 1);
                    memcpy(one, p, n);
                    if (!is_row_key(set, one) && !is_cell_id(set, p, n))
                        return mfail(err, where, "key '%s': input '%s' is neither a "
                                     "row of this set nor a cell", k, one);
                    p += n + (e ? 1 : 0);
                }
            }
        }
        if (!strcmp(k, set->hdr[KS_MH_UNIT_KEY])) unit = r;
    }
    if (!unit)
        return mfail(err, where, "unit_key '%s' names no row", set->hdr[KS_MH_UNIT_KEY]);
    if (unit->unit_code != 0x01 || unit->value_e6 != 1000000)
        return mfail(err, where, "the unit row '%s' must be a ratio of value_e6 1000000",
                     set->hdr[KS_MH_UNIT_KEY]);
    if (!dec_i64(set->hdr[KS_MH_ROWS], &declared) || declared < 0 ||
        (uint64_t)declared != set->nrows)
        return mfail(err, where, "header rows %s, but the rows section has %zu",
                     set->hdr[KS_MH_ROWS], set->nrows);
    for (size_t i = 0; i < set->cells.nrows; i++)
        for (size_t j = i + 1; j < set->cells.nrows; j++)
            if (!strcmp(set->cells.cells[i * KS_MEAS_NCELL], set->cells.cells[j * KS_MEAS_NCELL]))
                return mfail(err, where, "cell id '%s' appears twice",
                             set->cells.cells[i * KS_MEAS_NCELL]);
    if (set->composite != (set->members.nrows > 0) ||
        set->composite != (*set->hdr[KS_MH_MEMBERS] != 0))
        return mfail(err, where, "composite %u with %zu member rows and members '%s' "
                     "(an envelope has both, a measured set neither)",
                     set->composite, set->members.nrows, set->hdr[KS_MH_MEMBERS]);
    {
        uint64_t got = pcrec_ks_meas_digest(set);
        if (got != set->digest) {
            char h1[17], h2[17];
            pcrec_ks_meas_hex(set->digest, h1);
            pcrec_ks_meas_hex(got, h2);
            return mfail(err, where, "values_digest %s, but the rows hash to %s", h1, h2);
        }
    }
    return 0;
}

int pcrec_ks_meas_parse(const KsAlloc *a, const char *text, size_t len,
                        const char *where, const KsMeasSet **out, KsErr *err)
{
    KsTsv t;
    KsMeasSet *set = a->alloc(a->ctx, sizeof *set);
    KsErr terr;
    if (pcrec_ks_tsv_read(a, text, len, &t, &terr))
        return mfail(err, where, "%s", terr.msg);
    for (size_t i = 0; i < t.nsec; i++) {
        const KsTsvSection *s = &t.sec[i];
        if (!*s->name) {
            if (s->nrows)
                return mfail(err, where, "line %zu: data before the first #section",
                             s->row_line[0]);
            continue;
        }
        if (in_list(meas_derived, NELEM(meas_derived) - 1, s->name))
            return mfail(err, where, "line %zu: '#section %s' is a derived view of a "
                         "set and never an input: --list-measurements X "
                         "--view=canonical writes the loadable form", s->line, s->name);
        if (!in_list(meas_sections, NELEM(meas_sections), s->name))
            return mfail(err, where, "line %zu: unknown section '%s' (header, cards, "
                         "rows, cells, members)", s->line, s->name);
    }
    if (load_header(pcrec_ks_tsv_section(&t, "header"), set, where, err) ||
        check_header(set, where, err) ||
        tab_load(a, pcrec_ks_tsv_section(&t, "cards"), card_cols, KS_MEAS_NCARD,
                 &set->cards, where, err) ||
        tab_load(a, pcrec_ks_tsv_section(&t, "cells"), cell_cols, KS_MEAS_NCELL,
                 &set->cells, where, err) ||
        tab_load(a, pcrec_ks_tsv_section(&t, "members"), member_cols, KS_MEAS_NMEMBER,
                 &set->members, where, err) ||
        load_rows(a, pcrec_ks_tsv_section(&t, "rows"), set, where, err) ||
        check_rows(a, set, where, err))
        return -1;
    *out = set;
    return 0;
}

/* ---- the views (§9.6) -------------------------------------------------- */

/* Writes `n` cells joined by TAB and a newline. */
static int put_row(const KsOut *o, const char *const *c, size_t n)
{
    for (size_t i = 0; i < n; i++)
        if ((i && pcrec_ks_out(o, "\t")) || pcrec_ks_out(o, c[i])) return -1;
    return pcrec_ks_out(o, "\n");
}

/* A section line and its header line. */
static int put_head(const KsOut *o, const char *name, const char *const *cols, size_t n)
{
    if (pcrec_ks_out(o, "#section ") || pcrec_ks_out(o, name) ||
        pcrec_ks_out(o, "\n#"))
        return -1;
    return put_row(o, cols, n);
}

static int put_tab(const KsOut *o, const char *name, const char *const *cols, size_t w,
                   const KsMeasTab *t)
{
    if (put_head(o, name, cols, w)) return -1;
    for (size_t r = 0; r < t->nrows; r++)
        if (put_row(o, t->cells + r * w, w)) return -1;
    return 0;
}

static int meas_write_canonical(const KsOut *o, const void *doc, KsErr *err)
{
    const KsMeasSet *set = doc;
    static const char *const kv[] = { "key", "value" };
    int rc = pcrec_ks_out(o, "# pcrec measurement set (spec: docs/spec/measures.md)\n") ||
             put_head(o, "header", kv, 2);
    for (int i = 0; !rc && i < KS_MEAS_NHDR; i++) {
        const char *c[2] = { meas_hdr_names[i], set->hdr[i] };
        rc = put_row(o, c, 2);
    }
    rc = rc || put_tab(o, "cards", card_cols, KS_MEAS_NCARD, &set->cards) ||
         put_head(o, "rows", row_cols, KS_MEAS_NROWCOL);
    for (size_t r = 0; !rc && r < set->nrows; r++)
        rc = put_row(o, set->rows[r].col, KS_MEAS_NROWCOL);
    rc = rc || put_tab(o, "cells", cell_cols, KS_MEAS_NCELL, &set->cells) ||
         put_tab(o, "members", member_cols, KS_MEAS_NMEMBER, &set->members);
    if (rc) snprintf(err->msg, sizeof err->msg, "the view's writer failed");
    return rc ? -1 : 0;
}

/* One decoded row: scope, field, value. */
static int dec(const KsOut *o, const char *scope, const char *field, const char *value)
{
    const char *c[3] = { scope, field, value };
    return put_row(o, c, 3);
}

static int dec_tab(const KsOut *o, const char *what, const char *const *cols, size_t w,
                   const KsMeasTab *t)
{
    char scope[40];
    for (size_t r = 0; r < t->nrows; r++) {
        snprintf(scope, sizeof scope, "%s:%zu", what, r);
        for (size_t j = 0; j < w; j++)
            if (dec(o, scope, cols[j], t->cells[r * w + j])) return -1;
    }
    return 0;
}

/* The LOADED document field by field, every value as the loader holds it
 * (the parsed value_e6, the unit and status CODES), so R5 can hold the C
 * interpretation to an independent reader of the original file. */
static int meas_write_decoded(const KsOut *o, const void *doc, KsErr *err)
{
    const KsMeasSet *set = doc;
    static const char *const sdf[] = { "scope", "field", "value" };
    static const char *const item[] = { "rows", "values_digest" };
    char num[32], hex[17];
    int rc = pcrec_ks_out(o, "# pcrec measurement set, decoded (spec: docs/spec/measures.md)\n") ||
             put_head(o, "decoded", sdf, 3);
    for (int i = 0; !rc && i < KS_MEAS_NHDR; i++)
        rc = dec(o, "header", meas_hdr_names[i], set->hdr[i]);
    for (size_t r = 0; !rc && r < set->nrows; r++) {
        const KsMeasRow *m = &set->rows[r];
        char scope[600];
        snprintf(scope, sizeof scope, "row:%s", m->col[KS_MR_key]);
        for (size_t j = 1; !rc && j < KS_MEAS_NROWCOL; j++) {
            if (j == KS_MR_value_e6) {
                if (m->value_e6 == KS_MEAS_EMPTY) num[0] = 0;
                else snprintf(num, sizeof num, "%lld", (long long)m->value_e6);
                rc = dec(o, scope, row_cols[j], num);
            } else {
                rc = dec(o, scope, row_cols[j], m->col[j]);
            }
        }
        snprintf(num, sizeof num, "%u", m->unit_code);
        rc = rc || dec(o, scope, "unit_code", num);
        snprintf(num, sizeof num, "%u", m->status_code);
        rc = rc || dec(o, scope, "status_code", num);
    }
    rc = rc || dec_tab(o, "card", card_cols, KS_MEAS_NCARD, &set->cards) ||
         dec_tab(o, "cell", cell_cols, KS_MEAS_NCELL, &set->cells) ||
         dec_tab(o, "member", member_cols, KS_MEAS_NMEMBER, &set->members) ||
         put_head(o, "item", item, 2);
    if (!rc) {
        const char *c[2];
        snprintf(num, sizeof num, "%zu", set->nrows);
        pcrec_ks_meas_hex(pcrec_ks_meas_digest(set), hex);
        c[0] = num;
        c[1] = hex;
        rc = put_row(o, c, 2);
    }
    if (rc) snprintf(err->msg, sizeof err->msg, "the view's writer failed");
    return rc ? -1 : 0;
}

/* ---- the file probe (stop S2, and a FILE value) ------------------------ */

int pcrec_ks_meas_read_file(const KsAlloc *a, const char *path,
                            const KsMeasSet **out, KsErr *err)
{
    FILE *f = fopen(path, "rb");
    char *buf;
    long sz;
    size_t got;
    if (!f) return mfail(err, path, "cannot open");
    if (fseek(f, 0, SEEK_END) || (sz = ftell(f)) < 0 || fseek(f, 0, SEEK_SET)) {
        fclose(f);
        return mfail(err, path, "cannot read");
    }
    buf = a->alloc(a->ctx, (size_t)sz + 1);
    got = fread(buf, 1, (size_t)sz, f);
    fclose(f);
    if (got != (size_t)sz) return mfail(err, path, "cannot read");
    return pcrec_ks_meas_parse(a, buf, got, path, out, err);
}

/* S2's probe: the file's set, FOUND when its header id is `name` (one set
 * per file by construction, so never MULTI). */
static KsFile meas_probe(const KsAlloc *a, const char *path, const char *name,
                         void **doc, size_t *nitems, KsErr *err)
{
    const KsMeasSet *set;
    *nitems = 1;
    if (pcrec_ks_meas_read_file(a, path, &set, err)) return KS_FILE_ERROR;
    if (strcmp(set->hdr[KS_MH_ID], name)) return KS_FILE_OTHER;
    *doc = (void *)set;
    return KS_FILE_FOUND;
}

const KsKind pcrec_ks_measures = {
    .kind          = "measures",
    .suffix        = ".measures.tsv",
    .stops         = KS_STOP_BIT(KS_AT_DIRS) | KS_STOP_BIT(KS_AT_STORE),
    .flag_classify = KS_CLS_NAME_ELSE_FILE,
    .list_classify = KS_CLS_NAME_ELSE_FILE,
    .revs          = true,
    .s2_mismatch   = KS_S2_REFUSE,
    .s2_multi      = KS_S2_REFUSE,
    .entry_match   = KS_ENTRY_EXACT,
    .join          = KS_JOIN_CLEAN,
    .bare_view     = KS_VIEW_CANONICAL,
    .r4            = KS_R4_REQUIRED,
    .list_surface  = KS_LIST_CLI,
    .cli_flag      = "--measures",
    .cfg_line      = "measures",
    .list_flag     = "--list-measurements",
    .noun          = "measurement set",
    .nouns         = "measurement sets",
    .item_noun     = "set",
    .item          = &pcrec_ks_meas_values_role,
    .stamp         = &pcrec_ks_meas_values_role,
    .probe         = meas_probe,
    .write_canonical = meas_write_canonical,
    .write_decoded   = meas_write_decoded,
    .derived_sections = meas_derived,
};
