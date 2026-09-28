/* analyze.h -- pcrec-analyze, the [FINDINGS] exemplar analyzer, END STATE
 * (design.md §10.1's `analyze/` row; build step B6). A SEPARATE,
 * ZERO-DEPENDENCY binary -- it does not link libpcrec or read anything
 * under src/lib/cli, so it has its own tiny data model, its own bundle
 * reader/writer and its own SHA-256, rather than reaching into pcrec's
 * tree. Ported 1:1 from `scripts/pcrec_analyze.py` (the B3 prototype;
 * see docs/dev/lanes/findb6_report.md for the port's own findings) --
 * same CLI, same output BYTES, so a caller cannot tell them apart.
 */
#ifndef PCREC_ANALYZE_H
#define PCREC_ANALYZE_H

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#define PCREC_ANALYZE_VERSION "0.1"

/* design.md §2.2/§1 row 4: the closed kind set, in CANONICAL order (§5.2,
 * §8.1's "kinds in canonical order") -- both the render order AND the
 * order the "analyzer ... --scan ..." line lists whichever kinds are
 * present, regardless of the order the caller typed --scan in. */
typedef enum {
    KIND_FREQ = 0,
    KIND_CPFREQ = 1,
    KIND_BIGRAM = 2,
    KIND__COUNT = 3,
} Kind;

extern const Kind PCREC_ANALYZE_CANONICAL_KINDS[KIND__COUNT];
const char *pcrec_analyze_kind_name(Kind k);
int pcrec_analyze_kind_from_name(const char *name, Kind *out); /* 0 ok, -1 unknown */

/* A sparse code-point -> count map (design.md §10.3: "sparse code-point
 * map, <= 1,114,112 keys worst case"). Open addressing, linear probing;
 * PCREC_ANALYZE_CP_EMPTY (outside the whole Unicode range) marks a free
 * slot so U+0000 is a representable key. */
#define PCREC_ANALYZE_CP_EMPTY 0xFFFFFFFFu

typedef struct {
    uint32_t *keys;   /* cp, or PCREC_ANALYZE_CP_EMPTY */
    uint64_t *counts;
    size_t cap;        /* power of 2; 0 until first insert */
    size_t used;
} CpTable;

void cp_table_init(CpTable *t);
void cp_table_add(CpTable *t, uint32_t cp, uint64_t count);
void cp_table_free(CpTable *t);
typedef struct { uint32_t cp; uint64_t count; } CpRow;
/* Sorted ascending by cp; caller frees *out with free(). Returns row count. */
size_t cp_table_sorted(const CpTable *t, CpRow **out);

/* One kind's rows + declarations + provenance -- design.md §2.7's exhibit
 * shape. The SAME struct holds a block counted fresh from raw bytes
 * (cmd_scan) and a block parsed back out of bundle TEXT (cmd_merge,
 * cmd_check): the row storage is identical either way, only where it came
 * from differs. */
typedef struct {
    Kind kind;
    int present; /* this block exists in the bundle */

    uint64_t freq[256];         /* KIND_FREQ */
    uint64_t *bigram;           /* KIND_BIGRAM: 65536 counts, malloc'd on demand */
    CpTable cp;                 /* KIND_CPFREQ */

    char encoding[8];           /* "" | "ascii" | "utf8" | "bytes" */

    /* provenance (each NULL/absent unless set) */
    char *source;
    char *retrieved;
    char *url;
    char *ref;
    char *license;
    char *fidelity;
    char *adaptation;
    int have_bytes;
    long long bytes_val;
    int have_sha256;
    char sha256_val[65];
} KindBlock;

void kind_block_init(KindBlock *b, Kind kind);
void kind_block_add_freq(KindBlock *b, unsigned byte, uint64_t count);
void kind_block_add_bigram(KindBlock *b, unsigned a, unsigned bb, uint64_t count);
void kind_block_add_cp(KindBlock *b, uint32_t cp, uint64_t count);
void kind_block_merge_from(KindBlock *dst, const KindBlock *src); /* rows only */
int kind_block_rows_equal(const KindBlock *a, const KindBlock *b); /* recount vs parsed */

typedef struct {
    char *name; /* "analysis NAME" */
    KindBlock blocks[KIND__COUNT];
} Bundle;

void bundle_init(Bundle *bd);

/* design.md §10.4: shard bounds and the three per-kind shard ranges
 * ([r2 A-1]'s k=1 exception on freq/cpfreq, [r2 A-2]'s cpfreq lead-byte
 * ownership seam). All return a (start,len) window into the CALLER's
 * buffer -- no copy. */
void shard_bounds(size_t size, long k, long n, size_t *start, size_t *end);
void freq_shard_range(size_t size, long k, long n, size_t *start, size_t *end);
void bigram_shard_range(size_t size, long k, long n, size_t *start, size_t *end);
void cpfreq_shard_range(const unsigned char *data, size_t size, long k, long n,
                         size_t *start, size_t *end);
int is_continuation_byte(unsigned char b);

/* design.md §10.2's observed-characteristic column. */
const char *classify_encoding(const unsigned char *data, size_t len);
const char *combine_encoding(const char *a, const char *b); /* lattice max; either may be NULL */

/* Strict UTF-8 (Unicode's well-formed byte sequences, CPython's own
 * "strict" rule -- overlong forms, surrogates and > U+10FFFF all refused).
 * Returns 1 and fills `out` (if non-NULL) on success, 0 on the first
 * invalid byte (position optionally returned in *bad_pos). */
int utf8_decode_strict(const unsigned char *data, size_t len, CpTable *out, size_t *bad_pos);

/* Key rendering (design.md §2.3): hex keys, per-kind arity. Each writes
 * into a caller buffer sized generously (>=8 bytes is always enough). */
void byte_key(unsigned b, char out[4]);
void pair_key(unsigned a, unsigned bb, char out[8]);
void cp_key(uint32_t cp, char out[16]);

/* design.md §10.2's table, [r2 M-B1]'s collision-free split: returns the
 * "when" list and "via" derivation for one kind's `serves` line. */
void derive_serves(Kind kind, const char *encoding, int has_freq, int has_cpfreq,
                    char when_out[16], char via_out[16]);

/* Renders the whole bundle to `out` (design.md §2.7's shape); byte-for-byte
 * what scripts/pcrec_analyze.py emits. */
void render_bundle(FILE *out, const char *name, const Bundle *bd);

/* Parses bundle TEXT (this tool's own emitted subset of .rxt, design.md
 * §2.7 -- not the full format) into `bd`. `text` need not be NUL-terminated
 * beyond `len`. Returns 0 on success; on failure returns -1 and (if err_out
 * non-NULL) a heap message the caller frees. */
int parse_bundle(const char *text, size_t len, Bundle *bd, char **err_out);

/* Reads a whole file (or stdin when path is NULL or "-") into a malloc'd
 * buffer; *len is set. Returns 0 on success, -1 on error (errno set for a
 * named file). Caller frees *out. */
int read_whole_file(const char *path, unsigned char **out, size_t *len);

#endif
