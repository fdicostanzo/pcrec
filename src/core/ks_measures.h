/* src/core/ks_measures.h — [MEASURE-SET] M0 the MEASURES kind's document: one
 * loaded measurement set (docs/design/measure_sets.md rev 3 §1, §9.5;
 * docs/spec/measures.md is the contract), the row of the kinds table that
 * reads it (`pcrec_ks_measures`), and the functions a library tier, the embed
 * generator and a future `pcrec-measure` share.
 *
 * Same DEPENDENCY RULE as `core/ksrc.h` (S989): libc and `core/ksrc.h` only,
 * so a tool that links the parts and this row links nothing else of `src/`.
 *
 * The document is DATA in fixed shapes so that `scripts/ksgen.c` can write a
 * committed set as a static initializer (the pre-parse, §2.3) and the
 * loader, the writers and the digest read one type whichever way the set
 * arrived. Every column a section declares is a fixed index here; a column
 * the spec does not name is tolerated on read and not carried (§1.6). */
#ifndef PCREC_KS_MEASURES_H
#define PCREC_KS_MEASURES_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "core/ksrc.h"

/* The header keys, in the spec's order (the canonical writer's order). REQ
 * marks a key the loader requires non-empty. */
#define KS_MEAS_HEADER(X)          \
    X(FORMAT,       "format",       1) \
    X(ID,           "id",           1) \
    X(REV,          "rev",          1) \
    X(CLASS,        "class",        1) \
    X(ISA,          "isa",          0) \
    X(TIER,         "tier",         1) \
    X(COMPOSITE,    "composite",    1) \
    X(MEMBERS,      "members",      0) \
    X(UNIT_KEY,     "unit_key",     1) \
    X(METHOD,       "method",       1) \
    X(RUN,          "run",          0) \
    X(BOX,          "box",          0) \
    X(COMPILER,     "compiler",     0) \
    X(LIBC,         "libc",         0) \
    X(CODE_COMMIT,  "code_commit",  0) \
    X(COUNTERS,     "counters",     0) \
    X(PARTIAL,      "partial",      0) \
    X(ROWS,         "rows",         1) \
    X(VALUES_DIGEST, "values_digest", 1)
#define KS_MEAS_H_ENUM(id, name, req) KS_MH_##id,
typedef enum { KS_MEAS_HEADER(KS_MEAS_H_ENUM) KS_MEAS_NHDR } KsMeasHdr;
#undef KS_MEAS_H_ENUM

/* The four table sections the spec names besides `header`, each with its
 * fixed columns in the spec's order. `rows` is held typed (KsMeasRow); the
 * other three are held as cells. */
#define KS_MEAS_CARD_COLS(X) X(owner) X(quantity) X(ver) X(dims) X(unit) \
    X(subject) X(lengths) X(launches) X(rounds) X(aa_rule) X(gate_e6) X(env) X(deps)
#define KS_MEAS_ROW_COLS(X) X(key) X(unit) X(value_e6) X(abs_ns_e6) X(noise_e6) \
    X(n) X(status) X(derivation) X(inputs) X(deps) X(tags) X(source)
#define KS_MEAS_CELL_COLS(X) X(cell) X(group) X(arm) X(length) X(launch) X(round) X(ns_e6)
#define KS_MEAS_MEMBER_COLS(X) X(member) X(unit_key) X(unit_abs_ns_e6) X(box)
#define KS_MEAS_COUNT(c) +1
enum {
    KS_MEAS_NCARD   = 0 KS_MEAS_CARD_COLS(KS_MEAS_COUNT),
    KS_MEAS_NROWCOL = 0 KS_MEAS_ROW_COLS(KS_MEAS_COUNT),
    KS_MEAS_NCELL   = 0 KS_MEAS_CELL_COLS(KS_MEAS_COUNT),
    KS_MEAS_NMEMBER = 0 KS_MEAS_MEMBER_COLS(KS_MEAS_COUNT)
};
#undef KS_MEAS_COUNT
#define KS_MEAS_COL_ENUM(c) KS_MR_##c,
enum { KS_MEAS_ROW_COLS(KS_MEAS_COL_ENUM) };
#undef KS_MEAS_COL_ENUM

/* The empty `value_e6` (a NULL row's): the value the digest hashes for it. */
#define KS_MEAS_EMPTY INT64_MIN

/* One row of the `rows` section. Every column is kept as its text (`col`,
 * KS_MR_* indices); `value_e6` is also parsed, and `unit`/`status` coded by
 * the spec's table (§1.6: never 0). */
typedef struct {
    const char *col[KS_MEAS_NROWCOL];
    int64_t     value_e6;
    uint8_t     unit_code, status_code;
} KsMeasRow;

/* A cells-held section: `nrows` rows of the section's fixed column count. */
typedef struct {
    size_t             nrows;
    const char *const *cells;
} KsMeasTab;

/* One loaded set. `hdr[i]` is header key i's value, "" where the file has
 * none; `rows` is in CANONICAL order (a bytewise sort of the keys, §1.7) and
 * the three tables in bytewise order of their rows' text, so a document has
 * one form whatever order its file listed things in. */
typedef struct {
    const char *hdr[KS_MEAS_NHDR];
    uint32_t    rev;
    uint8_t     composite;
    uint64_t    digest;         /* values_digest, as read (= recomputed) */
    KsMeasTab   cards, cells, members;
    size_t      nrows;
    const KsMeasRow *rows;
} KsMeasSet;

/* Parses and validates `text[0..len)` as a set (§1.6's checks, the spec's
 * failure table): 0 with `*out` set, or -1 with `err` filled. `where` names
 * the input in a refusal ("FILE", "the built-in store's myset@1"). */
int pcrec_ks_meas_parse(const KsAlloc *a, const char *text, size_t len,
                        const char *where, const KsMeasSet **out, KsErr *err);

/* Reads the file at `path` whole and parses it (`where` is the path). */
int pcrec_ks_meas_read_file(const KsAlloc *a, const char *path,
                            const KsMeasSet **out, KsErr *err);

/* The values digest of `set`'s rows (§1.6): FNV-1a-64 over the 13 domain
 * bytes `pcrec-meas-1\0`, then per row in canonical order the key, a NUL,
 * the unit byte, the status byte and `value_e6` as int64 LE. */
uint64_t pcrec_ks_meas_digest(const KsMeasSet *set);

/* The digest as the stamp spells it: 16 lowercase hex and a NUL. */
void pcrec_ks_meas_hex(uint64_t d, char out[17]);

/* The stamp text `id@rev:digest16` (§3.5) in the caller's allocator. */
const char *pcrec_ks_meas_stamp(const KsAlloc *a, const KsMeasSet *set);

/* The row's two digest roles (ITEM = STAMP, §9.5). */
extern const KsDigest pcrec_ks_meas_values_role;

/* The kind's row. */
extern const KsKind pcrec_ks_measures;

/* One committed set in the embedded store (src/core/measures_table.inc,
 * written by `scripts/ksgen.c measures`): its name `<id>@<rev>` and its
 * pre-parse. Entry i pairs with entry i of the TEXT table
 * (src/core/measures_store.inc), both written from one sorted file list. */
typedef struct {
    const char      *name;
    const KsMeasSet *set;
} KsMeasStoreEntry;

/* One `DEFAULTS` row: the set a bare compile of class `cls` reads. */
typedef struct {
    const char *cls;
    const char *id;
    uint32_t    rev;
} KsMeasDefault;

#endif
