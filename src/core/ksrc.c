/* src/core/ksrc.c — [KNOW-SRC] the knowledge-source module's kind-
 * independent PARTS (docs/design/measure_sets.md rev 3 §9.2): the name rule
 * and its classification, the stop-order resolver, fill-only precedence and
 * the digest builder. Each exists once; a kind differs from another only
 * through its `KsKind` row's columns.
 *
 * K3 adds part 6, the views: the view-name dispatch and the loader's refusal
 * of a derived view fed back as an input.
 *
 * INCLUDES libc, POSIX and `core/ksrc.h` ONLY, by rule (§9.2, S989): see the
 * header. No `Arena`, no `pcrec_error`, no stderr — a caller supplies the
 * allocator and receives refusals and notes as text. */

#include <dirent.h>
#include <stdarg.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

#include "core/ksrc.h"

/* ---- helpers --------------------------------------------------------- */

/* Fills `err` with a formatted refusal. */
static void ks_fail(KsErr *err, const char *fmt, ...)
    __attribute__((format(printf, 2, 3)));
static void ks_fail(KsErr *err, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(err->msg, sizeof err->msg, fmt, ap);
    va_end(ap);
}

/* A formatted string in the caller's allocator, sized to its text. */
static char *ks_fmt(const KsAlloc *a, const char *fmt, ...)
    __attribute__((format(printf, 2, 3)));
static char *ks_fmt(const KsAlloc *a, const char *fmt, ...)
{
    va_list ap;
    int n;
    char *s;
    va_start(ap, fmt);
    n = vsnprintf(NULL, 0, fmt, ap);
    va_end(ap);
    s = a->alloc(a->ctx, (size_t)n + 1);
    va_start(ap, fmt);
    vsnprintf(s, (size_t)n + 1, fmt, ap);
    va_end(ap);
    return s;
}

/* `dir` and `entry` joined as the row's `join` column says (ksrc.h). */
static char *ks_join(const KsAlloc *a, KsJoin j, const char *dir,
                     const char *entry)
{
    size_t nd = strlen(dir);
    bool slash = j == KS_JOIN_SLASH || (nd && dir[nd - 1] != '/');
    return ks_fmt(a, "%s%s%s", dir, slash ? "/" : "", entry);
}

/* True iff `p` names an existing regular file. */
static bool ks_path_is_file(const char *p)
{
    struct stat st;
    return stat(p, &st) == 0 && S_ISREG(st.st_mode);
}

/* ---- the name rule and classification -------------------------------- */

bool pcrec_ks_name_ok(const char *s, size_t n)
{
    if (n == 0 || s[0] < 'a' || s[0] > 'z') return false;
    for (size_t i = 1; i < n; i++)
        if (!((s[i] >= 'a' && s[i] <= 'z') || (s[i] >= '0' && s[i] <= '9') ||
              s[i] == '_' || s[i] == '-'))
            return false;
    return true;
}

/* A spelling rule with no probe (§3.2): under NAME_ELSE_FILE a string that
 * is not a legal name is a FILE, whatever exists on disk. */
KsReq pcrec_ks_classify(KsClassify c, const char *s)
{
    bool name = pcrec_ks_name_ok(s, strlen(s));
    switch (c) {
    case KS_CLS_NAME_ONLY:      return name ? KS_REQ_NAME : KS_REQ_BAD;
    case KS_CLS_NAME_ELSE_FILE: return name ? KS_REQ_NAME : KS_REQ_FILE;
    case KS_CLS_FILE_ONLY:      return KS_REQ_FILE;
    }
    return KS_REQ_BAD;
}

/* `NAME@REV` is a NAME only where the row says revisions exist; anything
 * else that is not a legal name classifies exactly as `pcrec_ks_classify`
 * would (so under NAME_ELSE_FILE `x@0`, `x@01` and `x@` are FILEs). */
KsReq pcrec_ks_classify_ref(KsClassify c, bool revs, const char *s,
                            size_t *nlen, uint32_t *rev)
{
    const char *at = revs && c != KS_CLS_FILE_ONLY ? strchr(s, '@') : NULL;
    *nlen = strlen(s);
    *rev = 0;
    if (at && pcrec_ks_name_ok(s, (size_t)(at - s)) && at[1] >= '1' &&
        at[1] <= '9') {
        unsigned long long v = 0;
        const char *d = at + 1;
        while (*d >= '0' && *d <= '9' && v <= 0xffffffffull)
            v = v * 10 + (unsigned)(*d++ - '0');
        if (!*d && v <= 0xffffffffull) {
            *nlen = (size_t)(at - s);
            *rev = (uint32_t)v;
            return KS_REQ_NAME;
        }
    }
    return pcrec_ks_classify(c, s);
}

/* ---- part 1: the section-TSV reader ---------------------------------- */

/* A growable array in the caller's allocator; the allocator never frees, so
 * growth abandons the old block (the arena's own discipline). */
typedef struct {
    void  *p;
    size_t n, cap, sz;
} KsVec;

static void *ks_vec_push(const KsAlloc *a, KsVec *v)
{
    if (v->n == v->cap) {
        size_t cap = v->cap ? v->cap * 2 : 16;
        void *np = a->alloc(a->ctx, cap * v->sz);
        if (v->n) memcpy(np, v->p, v->n * v->sz);
        v->p = np;
        v->cap = cap;
    }
    return (char *)v->p + v->sz * v->n++;
}

static char *ks_dup(const KsAlloc *a, const char *p, size_t n)
{
    char *d = a->alloc(a->ctx, n + 1);
    memcpy(d, p, n);
    d[n] = 0;
    return d;
}

/* Splits `line[0..n)` on TAB into the vector `cells` of `char *` copies. */
static size_t ks_split(const KsAlloc *a, const char *line, size_t n, KsVec *cells)
{
    size_t k = 0, at = 0;
    for (size_t i = 0; i <= n; i++)
        if (i == n || line[i] == '\t') {
            *(char **)ks_vec_push(a, cells) = ks_dup(a, line + at, i - at);
            at = i + 1;
            k++;
        }
    return k;
}

/* The section being read: its header (once seen) and its rows so far. */
typedef struct {
    KsTsvSection s;
    KsVec        cols, cells, lines;
    bool         has_rows;
    const char  *hdr;           /* the latest `#` line before the first row */
    size_t       hdr_len;
} KsTsvOpen;

/* Closes `o` into the output vector `secs`. */
static void ks_tsv_close(const KsAlloc *a, KsTsvOpen *o, KsVec *secs)
{
    if (!o->has_rows && o->hdr) {
        o->s.ncols = ks_split(a, o->hdr + 1, o->hdr_len - 1, &o->cols);
        o->s.cols = o->cols.p;
    }
    o->s.cells = o->cells.p;
    o->s.row_line = o->lines.p;
    *(KsTsvSection *)ks_vec_push(a, secs) = o->s;
}

static void ks_tsv_open(KsTsvOpen *o, const char *name, size_t line)
{
    memset(o, 0, sizeof *o);
    o->s.name = name;
    o->s.line = line;
    o->cols.sz = o->cells.sz = sizeof(char *);
    o->lines.sz = sizeof(size_t);
}

int pcrec_ks_tsv_read(const KsAlloc *a, const char *text, size_t len,
                      KsTsv *out, KsErr *err)
{
    static const char tag[] = "#section ";
    KsVec secs = { .sz = sizeof(KsTsvSection) };
    KsTsvOpen o;
    size_t ln = 0;
    ks_tsv_open(&o, "", 0);
    for (size_t at = 0; at < len;) {
        const char *line = text + at;
        const char *nl = memchr(line, '\n', len - at);
        size_t n = nl ? (size_t)(nl - line) : len - at;
        at += n + (nl ? 1 : 0);
        ln++;
        if (memchr(line, '\r', n) || memchr(line, '\0', n)) {
            ks_fail(err, "line %zu: a CR or NUL byte (a section TSV is "
                    "TAB-separated text with LF line ends)", ln);
            return -1;
        }
        if (n == 0) continue;
        if (n > sizeof tag - 1 && !memcmp(line, tag, sizeof tag - 1)) {
            const char *name = ks_dup(a, line + sizeof tag - 1, n - (sizeof tag - 1));
            ks_tsv_close(a, &o, &secs);
            for (size_t i = 0; i < secs.n; i++)
                if (!strcmp(((KsTsvSection *)secs.p)[i].name, name)) {
                    ks_fail(err, "line %zu: section '%s' appears twice", ln, name);
                    return -1;
                }
            ks_tsv_open(&o, name, ln);
            continue;
        }
        if (line[0] == '#') {
            if (!o.has_rows) { o.hdr = line; o.hdr_len = n; }
            continue;
        }
        if (!o.has_rows) {
            if (!o.hdr) {
                ks_fail(err, "line %zu: a data row before any header line in "
                        "section '%s'", ln, o.s.name);
                return -1;
            }
            o.s.ncols = ks_split(a, o.hdr + 1, o.hdr_len - 1, &o.cols);
            o.s.cols = o.cols.p;
            o.has_rows = true;
        }
        {
            size_t got = ks_split(a, line, n, &o.cells);
            if (got != o.s.ncols) {
                ks_fail(err, "line %zu: %zu fields where section '%s''s header "
                        "names %zu", ln, got, o.s.name, o.s.ncols);
                return -1;
            }
            *(size_t *)ks_vec_push(a, &o.lines) = ln;
            o.s.nrows++;
        }
    }
    ks_tsv_close(a, &o, &secs);
    out->nsec = secs.n;
    out->sec = secs.p;
    return 0;
}

const KsTsvSection *pcrec_ks_tsv_section(const KsTsv *t, const char *name)
{
    for (size_t i = 0; i < t->nsec; i++)
        if (!strcmp(t->sec[i].name, name)) return &t->sec[i];
    return NULL;
}

long pcrec_ks_tsv_col(const KsTsvSection *s, const char *name)
{
    for (size_t i = 0; i < s->ncols; i++)
        if (!strcmp(s->cols[i], name)) return (long)i;
    return -1;
}

/* ---- part 2: the resolver -------------------------------------------- */

/* An equality test over the entries, never discovery: a case-insensitive
 * filesystem would open `Log.rxt` for `log.rxt`, and this is what refuses
 * that [r2 M-S6]. */
bool pcrec_ks_dir_has_exact(const char *dir, const char *fname)
{
    DIR *d = opendir(dir);
    struct dirent *e;
    bool hit = false;
    if (!d) return false;
    while (!hit && (e = readdir(d)) != NULL)
        hit = !strcmp(e->d_name, fname);
    closedir(d);
    return hit;
}

/* Probes one directory stop for `entry` (a NAME's `<name><suffix>`, or a
 * PATH as written), applying the row's entry match, join, probe and S2
 * columns. FOUND fills `hit`; ABSENT means continue; ERROR has filled
 * `w->err`. */
static KsRes ks_probe_dir(const KsWalk *w, const char *dir, const char *entry,
                          const char *name, size_t stop, KsAt at, KsHit *hit)
{
    const KsKind *k = w->kind;
    char *path = ks_join(w->alloc, k->join, dir, entry);
    void *doc = NULL;
    size_t nitems = 0;
    switch (k->entry_match) {
    case KS_ENTRY_EXACT:
        if (!pcrec_ks_dir_has_exact(dir, entry)) return KS_RES_ABSENT;
        break;
    case KS_ENTRY_PROBE_EXISTS:
        if (!ks_path_is_file(path)) return KS_RES_ABSENT;
        break;
    }
    {
        const char *sec = pcrec_ks_derived_section(k, path);
        if (sec) {
            ks_fail(w->err, "%s carries '#section %s', a derived view of %s "
                    "and never an input: %s %s --view=canonical writes the "
                    "loadable form", path, sec, k->list_flag, k->list_flag,
                    name);
            return KS_RES_ERROR;
        }
    }
    if (k->probe) {
        switch (k->probe(w->alloc, path, name, &doc, &nitems, w->err)) {
        case KS_FILE_FOUND:
            break;
        case KS_FILE_ERROR:
            return KS_RES_ERROR;
        case KS_FILE_MULTI:
            if (k->s2_multi == KS_S2_REFUSE) {
                ks_fail(w->err, "%s defines %zu %s: an -I file defines ONE "
                        "%s, the one its name names", path, nitems, k->nouns,
                        k->item_noun);
                return KS_RES_ERROR;
            }
            return KS_RES_ABSENT;
        case KS_FILE_OTHER:
            if (k->s2_mismatch == KS_S2_REFUSE) {
                ks_fail(w->err, "%s defines no %s '%s': an -I file defines "
                        "the %s its name names", path, k->noun, name,
                        k->item_noun);
                return KS_RES_ERROR;
            }
            if (w->note)
                w->note(w->ctx, ks_fmt(w->alloc, "%s defines no %s '%s'; "
                                       "continuing the search", path,
                                       k->noun, name));
            return KS_RES_ABSENT;
        }
    }
    hit->stop = stop;
    hit->at = at;
    hit->path = path;
    hit->doc = doc;
    return KS_RES_FOUND;
}

/* The one stop loop. A NAME looks for `<name><suffix>` at each directory
 * stop and asks the caller's `has` at S1 and the store; a PATH (a
 * resolve-only kind's reference) is probed as written, once if absolute.
 * A stop the row does not declare, or that is absent this time, is skipped
 * and keeps its index. */
KsRes pcrec_ks_resolve(const KsWalk *w, KsReq req, const char *ref, size_t from,
                 KsHit *hit)
{
    const KsKind *k = w->kind;
    const size_t store = w->ndirs + 1;
    const char *entry = ref;
    memset(hit, 0, sizeof *hit);
    if (req == KS_REQ_PATH && ref[0] == '/') {
        if (from > 0 || !ks_path_is_file(ref)) return KS_RES_ABSENT;
        hit->at = KS_AT_DIRS;
        hit->path = ref;
        return KS_RES_FOUND;
    }
    if (req == KS_REQ_NAME) entry = ks_fmt(w->alloc, "%s%s", ref, k->suffix);
    for (size_t s = from; s <= store; s++) {
        KsRes r = KS_RES_ABSENT;
        if (s == 0) {
            if ((k->stops & KS_STOP_BIT(KS_AT_S1)) && w->s1 &&
                w->has(w->ctx, KS_AT_S1, ref)) {
                hit->stop = s;
                hit->at = KS_AT_S1;
                return KS_RES_FOUND;
            }
            if (k->stops & KS_STOP_BIT(KS_AT_SRCDIR))
                r = ks_probe_dir(w, w->srcdir, entry, ref, s, KS_AT_SRCDIR,
                                 hit);
        } else if (s < store) {
            if (k->stops & KS_STOP_BIT(KS_AT_DIRS))
                r = ks_probe_dir(w, w->dirs[s - 1], entry, ref, s, KS_AT_DIRS,
                                 hit);
        } else if ((k->stops & KS_STOP_BIT(KS_AT_STORE)) &&
                   w->has(w->ctx, KS_AT_STORE, ref)) {
            hit->stop = s;
            hit->at = KS_AT_STORE;
            return KS_RES_FOUND;
        }
        if (r != KS_RES_ABSENT) return r;
    }
    return KS_RES_ABSENT;
}

/* The list is the diagnostic's contract, so it comes before anything that
 * merely helps. */
const char *pcrec_ks_stops_text(const KsWalk *w)
{
    size_t n = 64;
    char *t;
    for (size_t i = 0; i < w->ndirs; i++) n += strlen(w->dirs[i]) + 8;
    t = w->alloc->alloc(w->alloc->ctx, n);
    t[0] = 0;
    if (w->s1) strcat(t, "the compiling file, ");
    for (size_t i = 0; i < w->ndirs; i++) {
        strcat(t, "-I ");
        strcat(t, w->dirs[i]);
        strcat(t, ", ");
    }
    strcat(t, "the built-in store");
    return t;
}

void pcrec_ks_refuse_unknown(const KsWalk *w, const char *name)
{
    ks_fail(w->err, "unknown %s '%s' (searched: %s)", w->kind->noun, name,
            pcrec_ks_stops_text(w));
}

/* ---- part 3: fill-only precedence (D93) ------------------------------ */

KsPick pcrec_ks_pick(const char *flag_value, const char *file_value)
{
    KsPick p = { .flag_value = flag_value, .file_value = file_value };
    if (file_value) {
        p.chosen = file_value;
        p.source = KS_SRC_FILE;
        p.disagree = flag_value && strcmp(flag_value, file_value) != 0;
    } else if (flag_value) {
        p.chosen = flag_value;
        p.source = KS_SRC_FLAG;
    }
    return p;
}

/* ---- part 6: the views ----------------------------------------------- */

int pcrec_ks_out(const KsOut *o, const char *s)
{
    return o->write(o->ctx, s, strlen(s));
}

/* The views a name selects, first match: each is one writer COLUMN of the
 * row, named by its offset. The index, derived and per-target views (§9.2
 * part 6) are the listing's own and are not written through a column. */
typedef int (*KsWriter)(const KsOut *, const void *, KsErr *);
static const struct {
    const char *view;
    size_t      col;
} ks_views[] = {
    { "canonical", offsetof(KsKind, write_canonical) },
    { "decoded",   offsetof(KsKind, write_decoded) },
};

int pcrec_ks_view_write(const KsKind *k, const char *view, const KsOut *o,
                        const void *doc, KsErr *err)
{
    const char *who = k->list_flag ? k->list_flag : k->kind;  /* `lib` has none */
    for (size_t i = 0; i < sizeof ks_views / sizeof *ks_views; i++) {
        KsWriter w;
        if (strcmp(ks_views[i].view, view) != 0) continue;
        memcpy(&w, (const char *)k + ks_views[i].col, sizeof w);
        if (!w) {
            ks_fail(err, "%s has no %s view", who, view);
            return -1;
        }
        return w(o, doc, err);
    }
    ks_fail(err, "%s: unknown view '%s' (canonical, decoded)", who, view);
    return -1;
}

const char *pcrec_ks_derived_section(const KsKind *k, const char *path)
{
    static const char tag[] = "#section ";
    FILE *f;
    const char *hit = NULL;
    char name[64];
    size_t at = 0, n = 0;
    bool line_start = true, in_name = false;
    int c;
    if (!k->derived_sections || !(f = fopen(path, "rb"))) return NULL;
    while (!hit && (c = getc(f)) != EOF) {
        if (in_name) {
            if (c == '\n' || c == '\r' || c == '\t' || c == ' ') {
                name[n] = 0;
                for (size_t i = 0; k->derived_sections[i]; i++)
                    if (!strcmp(k->derived_sections[i], name))
                        hit = k->derived_sections[i];
                in_name = false;
                line_start = c == '\n';
                at = 0;
            } else if (n + 1 < sizeof name) {
                name[n++] = (char)c;
            } else {
                in_name = false;            /* too long to be a section name */
            }
            continue;
        }
        if (c == '\n') { line_start = true; at = 0; continue; }
        if (line_start && (unsigned char)c == (unsigned char)tag[at]) {
            if (++at == sizeof tag - 1) { in_name = true; n = 0; line_start = false; }
            continue;
        }
        line_start = false;
        at = 0;
    }
    if (in_name && !hit) {                  /* the name ran to end of file */
        name[n] = 0;
        for (size_t i = 0; k->derived_sections[i]; i++)
            if (!strcmp(k->derived_sections[i], name)) hit = k->derived_sections[i];
    }
    fclose(f);
    return hit;
}

/* ---- part 5: the digests --------------------------------------------- */

const uint64_t pcrec_ks_fnv_basis = 0xcbf29ce484222325ull;

uint64_t pcrec_ks_fnv1a(uint64_t h, const void *p, size_t n)
{
    const unsigned char *b = p;
    for (size_t i = 0; i < n; i++) {
        h ^= b[i];
        h *= 0x100000001b3ull;
    }
    return h;
}

uint64_t pcrec_ks_digest(const KsDigest *role, const void *doc,
                   const char *subkey_val)
{
    uint64_t h = pcrec_ks_fnv1a(pcrec_ks_fnv_basis, role->domain, role->domain_len);
    if (role->subkey == KS_SUB_QUERY)
        h = pcrec_ks_fnv1a(h, subkey_val, strlen(subkey_val) + 1);
    return role->fold(h, doc, subkey_val);
}
