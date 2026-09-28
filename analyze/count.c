/* count.c -- pcrec-analyze's data model: counters, sharding, the bundle
 * TEXT reader/writer, strict UTF-8. Ported 1:1 from `scripts/
 * pcrec_analyze.py` (see analyze.h's header and docs/dev/lanes/
 * findb6_report.md for what the port found). Zero dependency on pcrec's
 * own tree -- `analyze/` is its own small standalone binary.
 */
#include "analyze.h"

#include <errno.h>
#include <stdlib.h>
#include <string.h>

/* ---------------------------------------------------------------------
 * Kind identity
 * --------------------------------------------------------------------- */

const Kind PCREC_ANALYZE_CANONICAL_KINDS[KIND__COUNT] = { KIND_FREQ, KIND_CPFREQ, KIND_BIGRAM };

const char *pcrec_analyze_kind_name(Kind k)
{
    switch (k) {
    case KIND_FREQ: return "freq";
    case KIND_CPFREQ: return "cpfreq";
    case KIND_BIGRAM: return "bigram";
    default: return "?";
    }
}

int pcrec_analyze_kind_from_name(const char *name, Kind *out)
{
    if (!strcmp(name, "freq")) { *out = KIND_FREQ; return 0; }
    if (!strcmp(name, "cpfreq")) { *out = KIND_CPFREQ; return 0; }
    if (!strcmp(name, "bigram")) { *out = KIND_BIGRAM; return 0; }
    return -1;
}

/* ---------------------------------------------------------------------
 * The sparse code-point table: open addressing, linear probing. cp is
 * never PCREC_ANALYZE_CP_EMPTY (outside the whole Unicode range), which
 * is what lets U+0000 be a representable key without a separate
 * "occupied" flag array.
 * --------------------------------------------------------------------- */

void cp_table_init(CpTable *t)
{
    t->keys = NULL;
    t->counts = NULL;
    t->cap = 0;
    t->used = 0;
}

void cp_table_free(CpTable *t)
{
    free(t->keys);
    free(t->counts);
    t->keys = NULL;
    t->counts = NULL;
    t->cap = 0;
    t->used = 0;
}

static size_t cp_hash(uint32_t cp, size_t cap)
{
    uint64_t h = (uint64_t)cp * 2654435761ull; /* Knuth multiplicative hash */
    return (size_t)(h & (cap - 1));
}

static void cp_table_grow(CpTable *t)
{
    size_t newcap = t->cap ? t->cap * 2 : 64;
    uint32_t *nk = malloc(newcap * sizeof(uint32_t));
    uint64_t *nc = malloc(newcap * sizeof(uint64_t));
    for (size_t i = 0; i < newcap; i++) nk[i] = PCREC_ANALYZE_CP_EMPTY;
    for (size_t i = 0; i < t->cap; i++) {
        if (t->keys[i] == PCREC_ANALYZE_CP_EMPTY) continue;
        size_t idx = cp_hash(t->keys[i], newcap);
        while (nk[idx] != PCREC_ANALYZE_CP_EMPTY) idx = (idx + 1) & (newcap - 1);
        nk[idx] = t->keys[i];
        nc[idx] = t->counts[i];
    }
    free(t->keys);
    free(t->counts);
    t->keys = nk;
    t->counts = nc;
    t->cap = newcap;
}

void cp_table_add(CpTable *t, uint32_t cp, uint64_t count)
{
    if (t->cap == 0 || t->used * 2 >= t->cap) cp_table_grow(t);
    size_t idx = cp_hash(cp, t->cap);
    while (t->keys[idx] != PCREC_ANALYZE_CP_EMPTY && t->keys[idx] != cp) {
        idx = (idx + 1) & (t->cap - 1);
    }
    if (t->keys[idx] == PCREC_ANALYZE_CP_EMPTY) {
        t->keys[idx] = cp;
        t->counts[idx] = 0;
        t->used++;
    }
    t->counts[idx] += count;
}

static int cprow_cmp(const void *a, const void *b)
{
    uint32_t ca = ((const CpRow *)a)->cp, cb = ((const CpRow *)b)->cp;
    return (ca > cb) - (ca < cb);
}

size_t cp_table_sorted(const CpTable *t, CpRow **out)
{
    CpRow *rows = t->used ? malloc(t->used * sizeof(CpRow)) : NULL;
    size_t n = 0;
    for (size_t i = 0; i < t->cap; i++) {
        if (t->keys && t->keys[i] != PCREC_ANALYZE_CP_EMPTY && t->counts[i] != 0) {
            rows[n].cp = t->keys[i];
            rows[n].count = t->counts[i];
            n++;
        }
    }
    if (n > 1) qsort(rows, n, sizeof(CpRow), cprow_cmp);
    *out = rows;
    return n;
}

/* ---------------------------------------------------------------------
 * KindBlock: one kind's rows + declarations + provenance.
 * --------------------------------------------------------------------- */

void kind_block_init(KindBlock *b, Kind kind)
{
    memset(b, 0, sizeof(*b));
    b->kind = kind;
    cp_table_init(&b->cp);
}

void kind_block_add_freq(KindBlock *b, unsigned byte, uint64_t count)
{
    b->freq[byte & 0xFF] += count;
}

void kind_block_add_bigram(KindBlock *b, unsigned a, unsigned bb, uint64_t count)
{
    if (!b->bigram) b->bigram = calloc(65536, sizeof(uint64_t));
    b->bigram[(a & 0xFF) * 256 + (bb & 0xFF)] += count;
}

void kind_block_add_cp(KindBlock *b, uint32_t cp, uint64_t count)
{
    cp_table_add(&b->cp, cp, count);
}

/* design.md §10.4 "Counts ADD": sums `src`'s rows into `dst` (rows only --
 * the caller combines encoding/provenance itself, since --merge's own
 * rule for those is agreement/lattice-max, not addition). */
void kind_block_merge_from(KindBlock *dst, const KindBlock *src)
{
    dst->present = 1;
    switch (src->kind) {
    case KIND_FREQ:
        for (int i = 0; i < 256; i++) dst->freq[i] += src->freq[i];
        break;
    case KIND_BIGRAM:
        if (src->bigram) {
            if (!dst->bigram) dst->bigram = calloc(65536, sizeof(uint64_t));
            for (int i = 0; i < 65536; i++) dst->bigram[i] += src->bigram[i];
        }
        break;
    case KIND_CPFREQ:
        for (size_t i = 0; i < src->cp.cap; i++) {
            if (src->cp.keys[i] != PCREC_ANALYZE_CP_EMPTY && src->cp.counts[i]) {
                cp_table_add(&dst->cp, src->cp.keys[i], src->cp.counts[i]);
            }
        }
        break;
    default:
        break;
    }
}

int kind_block_rows_equal(const KindBlock *a, const KindBlock *b)
{
    if (a->kind != b->kind) return 0;
    switch (a->kind) {
    case KIND_FREQ:
        for (int i = 0; i < 256; i++) if (a->freq[i] != b->freq[i]) return 0;
        return 1;
    case KIND_BIGRAM:
        for (int i = 0; i < 65536; i++) {
            uint64_t av = a->bigram ? a->bigram[i] : 0;
            uint64_t bv = b->bigram ? b->bigram[i] : 0;
            if (av != bv) return 0;
        }
        return 1;
    case KIND_CPFREQ: {
        CpRow *ra = NULL, *rb = NULL;
        size_t na = cp_table_sorted(&a->cp, &ra);
        size_t nb = cp_table_sorted(&b->cp, &rb);
        int eq = (na == nb);
        if (eq) {
            for (size_t i = 0; i < na; i++) {
                if (ra[i].cp != rb[i].cp || ra[i].count != rb[i].count) { eq = 0; break; }
            }
        }
        free(ra);
        free(rb);
        return eq;
    }
    default:
        return 0;
    }
}

void bundle_init(Bundle *bd)
{
    bd->name = NULL;
    for (int i = 0; i < KIND__COUNT; i++) kind_block_init(&bd->blocks[i], (Kind)i);
}

/* ---------------------------------------------------------------------
 * Sharding (design.md §10.4; [r2 A-1] the k=1 exception, [r2 A-2] the
 * cpfreq lead-byte ownership seam).
 * --------------------------------------------------------------------- */

void shard_bounds(size_t size, long k, long n, size_t *start, size_t *end)
{
    *start = (size_t)(((unsigned long long)(k - 1)) * (unsigned long long)size / (unsigned long long)n);
    *end = (size_t)(((unsigned long long)k) * (unsigned long long)size / (unsigned long long)n);
}

void freq_shard_range(size_t size, long k, long n, size_t *start, size_t *end)
{
    shard_bounds(size, k, n, start, end);
}

/* Mirrors Python slice semantics (a negative index wraps from the end,
 * both ends clamp to [0, len], an inverted range reads empty) for the
 * ONE place this analyzer needs it: shard K>1's bigram range starts one
 * byte before its nominal cut. */
static void py_slice(long long len, long long lo, long long hi, size_t *start, size_t *end)
{
    if (lo < 0) lo += len;
    if (lo < 0) lo = 0;
    if (lo > len) lo = len;
    if (hi < 0) hi += len;
    if (hi < 0) hi = 0;
    if (hi > len) hi = len;
    if (lo > hi) hi = lo;
    *start = (size_t)lo;
    *end = (size_t)hi;
}

void bigram_shard_range(size_t size, long k, long n, size_t *start, size_t *end)
{
    size_t s, e;
    shard_bounds(size, k, n, &s, &e);
    long long lo = (k > 1) ? (long long)s - 1 : (long long)s;
    py_slice((long long)size, lo, (long long)e, start, end);
}

int is_continuation_byte(unsigned char b)
{
    return b >= 0x80 && b <= 0xBF;
}

void cpfreq_shard_range(const unsigned char *data, size_t size, long k, long n,
                         size_t *start, size_t *end)
{
    size_t s, e;
    shard_bounds(size, k, n, &s, &e);
    size_t cp_start = s;
    while (cp_start < e && is_continuation_byte(data[cp_start])) cp_start++;
    size_t cp_end = e;
    while (cp_end < size && is_continuation_byte(data[cp_end])) cp_end++;
    *start = cp_start;
    *end = cp_end;
}

/* ---------------------------------------------------------------------
 * Strict UTF-8 (Unicode's own well-formed-byte-sequence table, matching
 * CPython's "strict" errors handler): overlong forms, surrogates and
 * code points past U+10FFFF are all refused, per lead byte.
 * --------------------------------------------------------------------- */

int utf8_decode_strict(const unsigned char *data, size_t len, CpTable *out, size_t *bad_pos)
{
    size_t i = 0;
    while (i < len) {
        unsigned char b0 = data[i];
        uint32_t cp;
        size_t seqlen;

        if (b0 < 0x80) {
            cp = b0;
            seqlen = 1;
        } else if (b0 >= 0xC2 && b0 <= 0xDF) {
            if (i + 1 >= len) goto bad;
            unsigned char b1 = data[i + 1];
            if (b1 < 0x80 || b1 > 0xBF) goto bad;
            cp = ((uint32_t)(b0 & 0x1Fu) << 6) | (uint32_t)(b1 & 0x3Fu);
            seqlen = 2;
        } else if (b0 >= 0xE0 && b0 <= 0xEF) {
            if (i + 2 >= len) goto bad;
            unsigned char b1 = data[i + 1], b2 = data[i + 2];
            unsigned char lo1, hi1;
            if (b0 == 0xE0) { lo1 = 0xA0; hi1 = 0xBF; }        /* excludes overlong */
            else if (b0 == 0xED) { lo1 = 0x80; hi1 = 0x9F; }   /* excludes D800-DFFF */
            else { lo1 = 0x80; hi1 = 0xBF; }
            if (b1 < lo1 || b1 > hi1) goto bad;
            if (b2 < 0x80 || b2 > 0xBF) goto bad;
            cp = ((uint32_t)(b0 & 0x0Fu) << 12) | ((uint32_t)(b1 & 0x3Fu) << 6) | (uint32_t)(b2 & 0x3Fu);
            seqlen = 3;
        } else if (b0 >= 0xF0 && b0 <= 0xF4) {
            if (i + 3 >= len) goto bad;
            unsigned char b1 = data[i + 1], b2 = data[i + 2], b3 = data[i + 3];
            unsigned char lo1, hi1;
            if (b0 == 0xF0) { lo1 = 0x90; hi1 = 0xBF; }        /* excludes overlong */
            else if (b0 == 0xF4) { lo1 = 0x80; hi1 = 0x8F; }   /* excludes > U+10FFFF */
            else { lo1 = 0x80; hi1 = 0xBF; }
            if (b1 < lo1 || b1 > hi1) goto bad;
            if (b2 < 0x80 || b2 > 0xBF) goto bad;
            if (b3 < 0x80 || b3 > 0xBF) goto bad;
            cp = ((uint32_t)(b0 & 0x07u) << 18) | ((uint32_t)(b1 & 0x3Fu) << 12) |
                 ((uint32_t)(b2 & 0x3Fu) << 6) | (uint32_t)(b3 & 0x3Fu);
            seqlen = 4;
        } else {
            goto bad;
        }

        if (out) cp_table_add(out, cp, 1);
        i += seqlen;
    }
    return 1;

bad:
    if (bad_pos) *bad_pos = i;
    return 0;
}

/* design.md §10.2's observed-characteristic column. */
const char *classify_encoding(const unsigned char *data, size_t len)
{
    if (!utf8_decode_strict(data, len, NULL, NULL)) return "bytes";
    for (size_t i = 0; i < len; i++) if (data[i] >= 0x80) return "utf8";
    return "ascii";
}

static int enc_rank(const char *e)
{
    if (!strcmp(e, "ascii")) return 0;
    if (!strcmp(e, "utf8")) return 1;
    return 2; /* "bytes" */
}

const char *combine_encoding(const char *a, const char *b)
{
    if (!a || !a[0]) return b;
    if (!b || !b[0]) return a;
    return (enc_rank(a) >= enc_rank(b)) ? a : b;
}

/* ---------------------------------------------------------------------
 * Key rendering (design.md §2.3: hex keys, per-kind arity, ascending).
 * --------------------------------------------------------------------- */

void byte_key(unsigned b, char out[4])
{
    snprintf(out, 4, "%02x", b & 0xFFu);
}

void pair_key(unsigned a, unsigned bb, char out[8])
{
    snprintf(out, 8, "%02x %02x", a & 0xFFu, bb & 0xFFu);
}

void cp_key(uint32_t cp, char out[16])
{
    if (cp <= 0xFFFFu) snprintf(out, 16, "U+%04X", cp);
    else if (cp <= 0xFFFFFu) snprintf(out, 16, "U+%05X", cp);
    else snprintf(out, 16, "U+%06X", cp);
}

/* ---------------------------------------------------------------------
 * Declaration synthesis (design.md §10.2's table; [r2 M-B1] collision-free).
 * --------------------------------------------------------------------- */

void derive_serves(Kind kind, const char *encoding, int has_freq, int has_cpfreq,
                    char when_out[16], char via_out[16])
{
    (void)has_freq; /* design's own table never reads this half of the split */
    int enc_au = (!strcmp(encoding, "ascii") || !strcmp(encoding, "utf8"));
    if (kind == KIND_BIGRAM) {
        strcpy(when_out, enc_au ? "byte,utf8" : "byte");
        strcpy(via_out, "markov1");
    } else if (kind == KIND_FREQ) {
        if (has_cpfreq) strcpy(when_out, "byte");
        else strcpy(when_out, enc_au ? "byte,utf8" : "byte");
        strcpy(via_out, "unigram");
    } else { /* KIND_CPFREQ: only reachable with encoding ascii/utf8 (R26) */
        strcpy(when_out, "utf8");
        strcpy(via_out, "encode-utf8");
    }
}

/* ---------------------------------------------------------------------
 * Rendering (design.md §2.3/§2.7's exhibit shape) -- byte for byte what
 * scripts/pcrec_analyze.py's render_bundle emits.
 * --------------------------------------------------------------------- */

static void render_kind_block(FILE *out, const KindBlock *b, int has_freq, int has_cpfreq,
                               const char *scan_csv)
{
    char when[16], via[16];
    derive_serves(b->kind, b->encoding, has_freq, has_cpfreq, when, via);
    const char *query = (b->kind == KIND_BIGRAM) ? "run-rarity" : "byte-rate";

    fprintf(out, "    %s\n", pcrec_analyze_kind_name(b->kind));
    switch (b->kind) {
    case KIND_FREQ:
        fprintf(out, "        question How often does each byte occur in this exemplar?\n");
        break;
    case KIND_CPFREQ:
        fprintf(out, "        question How often does each Unicode code point occur in this exemplar?\n");
        break;
    case KIND_BIGRAM:
        fprintf(out, "        question How often does each adjacent byte pair occur in this exemplar?\n");
        break;
    default:
        break;
    }
    fprintf(out, "        reader %s (docs/spec/findings.md §4)\n", query);
    fprintf(out, "        analyzer pcrec-analyze %s --scan %s\n", PCREC_ANALYZE_VERSION, scan_csv);
    fprintf(out, "        encoding %s\n", b->encoding);
    fprintf(out, "        serves %s when %s via %s\n", query, when, via);

    if (b->kind == KIND_FREQ) {
        for (int i = 0; i < 256; i++) {
            if (!b->freq[i]) continue;
            char bk[4];
            byte_key((unsigned)i, bk);
            fprintf(out, "        row %s %llu\n", bk, (unsigned long long)b->freq[i]);
        }
    } else if (b->kind == KIND_BIGRAM) {
        if (b->bigram) {
            for (int idx = 0; idx < 65536; idx++) {
                if (!b->bigram[idx]) continue;
                char pk[8];
                pair_key((unsigned)(idx >> 8), (unsigned)(idx & 0xFF), pk);
                fprintf(out, "        row %s %llu\n", pk, (unsigned long long)b->bigram[idx]);
            }
        }
    } else {
        CpRow *rows = NULL;
        size_t n = cp_table_sorted(&b->cp, &rows);
        for (size_t i = 0; i < n; i++) {
            char ck[16];
            cp_key(rows[i].cp, ck);
            fprintf(out, "        row %s %llu\n", ck, (unsigned long long)rows[i].count);
        }
        free(rows);
    }

    fprintf(out, "        provenance\n");
    fprintf(out, "            source %s\n", (b->source && b->source[0]) ? b->source : "exemplar");
    if (b->retrieved) fprintf(out, "            retrieved %s\n", b->retrieved);
    if (b->have_bytes) fprintf(out, "            bytes %lld\n", b->bytes_val);
    if (b->have_sha256) fprintf(out, "            sha256 %s\n", b->sha256_val);
    if (b->url) fprintf(out, "            url %s\n", b->url);
    if (b->ref) fprintf(out, "            ref %s\n", b->ref);
    if (b->license) fprintf(out, "            license %s\n", b->license);
    if (b->fidelity) fprintf(out, "            fidelity %s\n", b->fidelity);
    if (b->adaptation) fprintf(out, "            adaptation %s\n", b->adaptation);
}

void render_bundle(FILE *out, const char *name, const Bundle *bd)
{
    int has_freq = bd->blocks[KIND_FREQ].present;
    int has_cpfreq = bd->blocks[KIND_CPFREQ].present;

    char csv[64];
    csv[0] = '\0';
    for (int i = 0; i < KIND__COUNT; i++) {
        Kind k = PCREC_ANALYZE_CANONICAL_KINDS[i];
        if (!bd->blocks[k].present) continue;
        if (csv[0]) strcat(csv, ",");
        strcat(csv, pcrec_analyze_kind_name(k));
    }

    fprintf(out, "analysis %s\n", name);
    for (int i = 0; i < KIND__COUNT; i++) {
        Kind k = PCREC_ANALYZE_CANONICAL_KINDS[i];
        if (bd->blocks[k].present) render_kind_block(out, &bd->blocks[k], has_freq, has_cpfreq, csv);
    }
}

/* ---------------------------------------------------------------------
 * A minimal reader for the bundle text THIS tool emits (--merge/--check).
 * Not the full .rxt schema -- only design.md §2.7's bundle subset, the
 * same deliberate scope `scripts/pcrec_analyze.py`'s own parse_bundle
 * carried (single writer, single reader).
 * --------------------------------------------------------------------- */

typedef struct {
    size_t indent;
    char *token; /* trimmed, NUL-terminated, heap-owned */
} PLine;

static size_t split_lines(const unsigned char *text, size_t len, PLine **out)
{
    size_t cap = 64, n = 0;
    PLine *lines = malloc(cap * sizeof(PLine));
    size_t i = 0;
    while (i < len) {
        size_t start = i;
        while (i < len && text[i] != '\n') i++;
        size_t end = i;
        if (i < len) i++; /* consume the newline */
        if (end > start && text[end - 1] == '\r') end--;

        size_t p = start;
        while (p < end && text[p] == ' ') p++;
        size_t indent = p - start;

        size_t q = end;
        while (q > p && (text[q - 1] == ' ' || text[q - 1] == '\t')) q--;
        if (q <= p) continue; /* blank line */

        size_t tok_len = q - p;
        char *token = malloc(tok_len + 1);
        memcpy(token, text + p, tok_len);
        token[tok_len] = '\0';

        if (n == cap) { cap *= 2; lines = realloc(lines, cap * sizeof(PLine)); }
        lines[n].indent = indent;
        lines[n].token = token;
        n++;
    }
    *out = lines;
    return n;
}

static void set_str(char **dst, const char *val)
{
    free(*dst);
    *dst = strdup(val);
}

static void set_provenance_field(KindBlock *blk, const char *field, const char *val)
{
    if (!strcmp(field, "source")) set_str(&blk->source, val);
    else if (!strcmp(field, "retrieved")) set_str(&blk->retrieved, val);
    else if (!strcmp(field, "bytes")) { blk->have_bytes = 1; blk->bytes_val = strtoll(val, NULL, 10); }
    else if (!strcmp(field, "sha256")) {
        blk->have_sha256 = 1;
        strncpy(blk->sha256_val, val, 64);
        blk->sha256_val[64] = '\0';
    }
    else if (!strcmp(field, "url")) set_str(&blk->url, val);
    else if (!strcmp(field, "ref")) set_str(&blk->ref, val);
    else if (!strcmp(field, "license")) set_str(&blk->license, val);
    else if (!strcmp(field, "fidelity")) set_str(&blk->fidelity, val);
    else if (!strcmp(field, "adaptation")) set_str(&blk->adaptation, val);
    /* an unrecognized field is carried by no known reader; ignored, same
     * as this file's own writer never emitting one. */
}

static void parse_row_line(KindBlock *blk, const char *rest)
{
    char toks[4][40];
    int ntok = 0;
    const char *p = rest;
    while (*p && ntok < 4) {
        while (*p == ' ') p++;
        if (!*p) break;
        const char *s = p;
        while (*p && *p != ' ') p++;
        size_t l = (size_t)(p - s);
        if (l >= sizeof(toks[0])) l = sizeof(toks[0]) - 1;
        memcpy(toks[ntok], s, l);
        toks[ntok][l] = '\0';
        ntok++;
    }
    if (ntok < 2) return; /* malformed row; ignored defensively */
    uint64_t count = strtoull(toks[ntok - 1], NULL, 10);
    switch (blk->kind) {
    case KIND_FREQ:
        kind_block_add_freq(blk, (unsigned)strtoul(toks[0], NULL, 16), count);
        break;
    case KIND_BIGRAM:
        kind_block_add_bigram(blk, (unsigned)strtoul(toks[0], NULL, 16),
                               (unsigned)strtoul(toks[1], NULL, 16), count);
        break;
    case KIND_CPFREQ: {
        const char *k = toks[0];
        if (k[0] == 'U' && k[1] == '+') k += 2;
        kind_block_add_cp(blk, (uint32_t)strtoul(k, NULL, 16), count);
        break;
    }
    default:
        break;
    }
}

int parse_bundle(const char *text, size_t len, Bundle *bd, char **err_out)
{
    PLine *lines;
    size_t n = split_lines((const unsigned char *)text, len, &lines);
    if (err_out) *err_out = NULL;

    if (n == 0) {
        if (err_out) *err_out = strdup("empty bundle");
        free(lines);
        return -1;
    }
    if (strncmp(lines[0].token, "analysis ", 9) != 0) {
        if (err_out) {
            char buf[256];
            snprintf(buf, sizeof(buf), "expected 'analysis NAME' header, got: %s", lines[0].token);
            *err_out = strdup(buf);
        }
        free(lines);
        return -1;
    }

    bundle_init(bd);
    const char *namep = lines[0].token + 9;
    while (*namep == ' ') namep++;
    bd->name = strdup(namep);

    size_t i = 1;
    while (i < n) {
        if (lines[i].indent != 4) {
            if (err_out) {
                char buf[256];
                snprintf(buf, sizeof(buf), "expected a kind header at indent 4: %s", lines[i].token);
                *err_out = strdup(buf);
            }
            free(lines);
            return -1;
        }
        const char *tok = lines[i].token;
        size_t klen = 0;
        while (tok[klen] && tok[klen] != ' ') klen++;
        char kindbuf[16];
        if (klen >= sizeof(kindbuf)) klen = sizeof(kindbuf) - 1;
        memcpy(kindbuf, tok, klen);
        kindbuf[klen] = '\0';
        Kind kind;
        if (pcrec_analyze_kind_from_name(kindbuf, &kind) != 0) {
            if (err_out) {
                char buf[64];
                snprintf(buf, sizeof(buf), "unknown kind '%s'", kindbuf);
                *err_out = strdup(buf);
            }
            free(lines);
            return -1;
        }
        KindBlock *blk = &bd->blocks[kind];
        blk->present = 1;
        i++;

        int in_provenance = 0;
        while (i < n && lines[i].indent >= 8) {
            size_t findent = lines[i].indent;
            const char *ftoken = lines[i].token;
            if (findent == 8) {
                in_provenance = 0;
                if (!strcmp(ftoken, "provenance")) {
                    in_provenance = 1;
                } else if (!strncmp(ftoken, "encoding ", 9)) {
                    strncpy(blk->encoding, ftoken + 9, sizeof(blk->encoding) - 1);
                } else if (!strncmp(ftoken, "row ", 4)) {
                    parse_row_line(blk, ftoken + 4);
                }
                /* "serves "/question/reader/analyzer: free prose, unread
                 * by this tool (design.md §10.2's split is re-derived by
                 * the caller who scanned, never round-tripped). */
            } else if (findent == 12 && in_provenance) {
                const char *sp = strchr(ftoken, ' ');
                char field[32];
                const char *val;
                if (sp) {
                    size_t flen = (size_t)(sp - ftoken);
                    if (flen >= sizeof(field)) flen = sizeof(field) - 1;
                    memcpy(field, ftoken, flen);
                    field[flen] = '\0';
                    val = sp + 1;
                } else {
                    strncpy(field, ftoken, sizeof(field) - 1);
                    field[sizeof(field) - 1] = '\0';
                    val = "";
                }
                set_provenance_field(blk, field, val);
            } else if (findent > 12) {
                if (err_out) {
                    char buf[256];
                    snprintf(buf, sizeof(buf), "unexpected indent: %s", ftoken);
                    *err_out = strdup(buf);
                }
                free(lines);
                return -1;
            }
            /* else: an indent that is neither 8, nor (12 while inside a
             * provenance block), nor >12 -- silently skipped, mirroring
             * scripts/pcrec_analyze.py's own parse_bundle exactly (its
             * `elif findent > 12 or (findent == 8 and False)` leaves this
             * combination unmatched by any branch). */
            i++;
        }
    }

    free(lines);
    return 0;
}

/* ---------------------------------------------------------------------
 * I/O
 * --------------------------------------------------------------------- */

int read_whole_file(const char *path, unsigned char **out, size_t *len)
{
    FILE *f;
    int is_stdin = (path == NULL || !strcmp(path, "-"));
    if (is_stdin) {
        f = stdin;
    } else {
        f = fopen(path, "rb");
        if (!f) return -1;
    }

    size_t cap = 65536, n = 0;
    unsigned char *buf = malloc(cap);
    for (;;) {
        if (n == cap) { cap *= 2; buf = realloc(buf, cap); }
        size_t r = fread(buf + n, 1, cap - n, f);
        n += r;
        if (r == 0) break;
    }
    if (!is_stdin) fclose(f);

    *out = buf;
    *len = n;
    return 0;
}
