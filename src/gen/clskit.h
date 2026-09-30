/* src/gen/clskit.h — THE CLASS-MATCHER KIT ([CLS-TREE] S1;
 * docs/design/cls_tree_design.md §1, §6's S1 row; decisions.md D129, D131).
 *
 * A class matcher is composed from a small kit of forms and selected
 * statically. The kit's input is a code-point SET and nothing else: a
 * sorted, disjoint, non-adjacent interval list, cpset.c's own invariant.
 * No caseless flag, no `\p` tag, no provenance (Constitutional Constraint
 * 1, design §1.1). That is what lets `CUBES` find the ASCII case fold from
 * set structure alone, and it is what makes `kit(A|B) == kit(A)||kit(B)` a
 * law that tests/clskit/ can test against. A "hint" argument added to any
 * entry below retires that test silently.
 *
 * Five things live here:
 *   - the per-section LEAF forms plus the sectioning DP (`pcrec_clskit_
 *     partition`), the design's `K`. It is a SIZE optimizer only (D131
 *     item 2), and its one pinned λ is table data in clskit.c;
 *   - the WHOLE-SET forms `PAGE3`/`PAGE2`/`BITMAP1` (§1.3);
 *   - the shared byte ATOM table ([OPT-CLSPACK], D131 item 6), its FORM and
 *     emitter;
 *   - THE SELECTION, D131 item 1's `--tune` class-form table over the
 *     per-SET forms (`K`/`PAGE3`/`PAGE2`/`BITMAP1`). It is one first-match
 *     table with rows as data (`pcrec_clskit_rows`);
 *   - THE TABLE SELECTION, D131 item 6's ARTIFACT-level choice of how the
 *     byte classes that read a table read it: one shared atom table, or a
 *     table per class. A second first-match table (`pcrec_clskit_table_rows`),
 *     not a `ROWS` row, because its input is every such class in the
 *     artifact at once — `ROWS` sees one set.
 *
 * Callers: the VM (S4 wires the per-set selection for wide classes, S2 for
 * byte classes, and [OPT-CLSPACK] the table selection for byte classes).
 * `--tune` reaches both tables as their position bit. Two per-set row denies
 * are mapped to public flags, both for byte classes only: `CLSD_BYTE_KIT` is
 * `-fno-cls-kit`'s and `CLSD_BYTE_FOLD` is `-fno-cls-fold`'s; the table
 * selection's atom row is `-fno-cls-pack`'s (and `-fno-cls-kit`'s).
 */
#ifndef PCREC_CLSKIT_H
#define PCREC_CLSKIT_H

#include <stdbool.h>
#include <stdint.h>

#include "core/internal.h"

/* The per-section leaf forms, IN OFFER ORDER. The DP keeps the first
 * cheapest form on a tie, so this order is part of the answer. It matches
 * the study's `section.py` `offer` order, which the cross-check pins. */
typedef enum {
    CLSK_ALL,       /* one interval: `1` */
    CLSK_RANGES,    /* an OR of range compares */
    CLSK_MASK64,    /* span <= 64: one 64-bit immediate mask, no load */
    CLSK_CUBES,     /* span <= 256: ONE don't-care cube, `(x & care) == val` */
    CLSK_BITMAP,    /* a bitmap over the section's span, one load */
    CLSK_PAGE64,    /* absolute 64-wide pages -> deduplicated 64-bit leaves */
    CLSK_BSEARCH,   /* binary search over the section's own intervals */
    CLSK_NLEAF
} ClsLeaf;

/* One chosen section: intervals `first..last` of the set, tested by `leaf`.
 * `care`/`val` carry the cube when `leaf == CLSK_CUBES`. */
typedef struct {
    int      first, last;
    ClsLeaf  leaf;
    unsigned care, val;
} ClsSection;

/* A sectioning of one set (the design's `K` when λ is the table's). `bytes`
 * is the MODEL's `.rodata + .text`: exact rodata plus the study's per-form
 * text constants. It is not a measured object size, and that difference is
 * the reason the report gives for the open question on the `0` row's gate. */
typedef struct {
    const PcrecCpRange *iv;
    int                 n;
    ClsSection         *sec;
    int                 nsec;
    long long           bytes;
} ClsKit;

/* The forms a whole class matcher can take. */
typedef enum {
    CLSF_KIT,       /* the sectioned kit matcher, `K` */
    CLSF_PAGE3,     /* whole-set three-stage table, TS = 10 (`P3`) */
    CLSF_PAGE2,     /* whole-set two-stage table (`P2`) */
    CLSF_BITMAP1,   /* one bitmap over the whole span (`B1`) */
    CLSF_ATOM,      /* the artifact's shared byte->atom table + one mask */
    CLSF_NFORM
} ClsForm;

/* The shared byte-class ATOM table: `atom[b]` numbers the set of classes
 * byte `b` belongs to, and `mask[k]` has bit `a` set iff atom `a` is in
 * class `k`. It exists only for byte sets (every hi <= 0xFF) and only when
 * the partition has at most 64 atoms. */
typedef struct {
    unsigned char atom[256];
    uint64_t     *mask;
    int           nset, natoms;
} ClsAtomTable;

/* One row's deny, an ORDINAL (bit `1u << d` in a deny mask). CLSD_NONE is
 * the terminal row's, which cannot be denied. NO `CLSD_ATOM`: the atom
 * table is not a `ROWS` outcome (see `ROWS`'s own comment in clskit.c);
 * the table selection below carries its own deny (`ClsTabDeny`). */
typedef enum {
    CLSD_NONE,
    CLSD_BYTE_KIT,
    CLSD_BYTE_TABLE,
    CLSD_SIZE_PAGE3,
    CLSD_SPEED_PAGE2,
    CLSD_SPEED_BITMAP1,
    CLSD_MID_PAGE3,
    CLSD_BYTE_FOLD,
    CLSD_NDENY
} ClsDeny;

/* The selection table's rows, by name: `ROWS` is indexed by these, so a
 * caller that spells a row's form itself (the VM's inline byte compares)
 * asks `ClsChoice.row == CLSR_...` rather than comparing a name. */
typedef enum {
    CLSR_BYTE_RANGE,
    CLSR_BYTE_FOLD,
    CLSR_BYTE_KIT,
    CLSR_BYTE_TABLE,
    CLSR_SIZE_PAGE3,
    CLSR_SPEED_PAGE2,
    CLSR_SPEED_BITMAP1,
    CLSR_MID_PAGE3,
    CLSR_KIT,
    CLSR_NROWS
} ClsRowId;

/* A row of the selection table, as data a listing can print. */
typedef struct {
    const char *name;
    const char *pred_desc;     /* the predicate, one line */
    unsigned    positions;     /* bit (tune + 2) for each --tune position */
    int         pred;          /* clskit.c's ClsPred tag */
    ClsForm     form;
    ClsDeny     deny;
} ClsRow;

/* What the selection sees beyond the set: the dial position and the row
 * denies. `kit` may be NULL; if not, it must be this set's `K`
 * (`pcrec_clskit_partition` at `pcrec_clskit_kit_lambda()`, all leaves),
 * and the selection reuses it rather than running the DP again. NO atom
 * fields: a PER-SET selection cannot see the artifact-level byte-class
 * population an atom-table choice needs (`ROWS`'s own comment); S2's own
 * artifact-level call carries whatever input its mechanism needs. */
typedef struct {
    int                 tune;       /* -2..+2 */
    unsigned            deny;       /* OR of 1u << ClsDeny */
    const ClsKit       *kit;
} ClsSelectIn;

/* The selection's answer. `kit` is always filled (every predicate but the
 * byte row reads it). `row` indexes `pcrec_clskit_rows`. `bytes` is the
 * DP's own MODEL bytes for a `CLSF_KIT` row (never the selection-only
 * `kit_sel_bytes` estimate, clskit.c D131 addendum 1) or the whole-set
 * form's model bytes otherwise; `ROWS` answers no `CLSF_ATOM` row. */
typedef struct {
    ClsForm   form;
    int       row;
    ClsKit    kit;
    long long bytes;            /* model bytes of `form` */
} ClsChoice;

/* THE TABLE SELECTION's answer for an artifact's TABLE-READING byte
 * classes (the ones no compare shape covers): one shared byte->atom table
 * plus a 64-bit mask per class, or a 32-byte bitmap per class. */
typedef enum {
    CLST_SITE,      /* one bitmap per class, the caller's own table */
    CLST_ATOM       /* the shared atom table, `pcrec_clskit_emit_atom*` */
} ClsTabForm;

/* A table-selection row's deny, an ORDINAL like `ClsDeny`. */
typedef enum {
    CLSTD_NONE,
    CLSTD_ATOM,
    CLSTD_NDENY
} ClsTabDeny;

/* A row of the table selection, as data a listing can print. */
typedef struct {
    const char *name;
    const char *pred_desc;     /* the predicate, one line */
    unsigned    positions;     /* bit (tune + 2) for each --tune position */
    int         pred;          /* clskit.c's ClsTabPred tag */
    ClsTabForm  form;
    ClsTabDeny  deny;
} ClsTabRow;

/* The table selection's answer. `atoms` is filled when `form` is
 * `CLST_ATOM`, and `atoms.mask[k]` is set `k`'s mask in the caller's order. */
typedef struct {
    ClsTabForm   form;
    int          row;
    ClsAtomTable atoms;
} ClsTabChoice;

void pcrec_clskit_partition(Arena *a, const PcrecCpRange *iv, int n,
                            unsigned lam, unsigned leaf_allow, ClsKit *out);
long long pcrec_clskit_whole_bytes(Arena *a, ClsForm f,
                                   const PcrecCpRange *iv, int n);
bool pcrec_clskit_atoms(Arena *a, const PcrecCpRange *const *sets,
                        const int *nivs, int nset, ClsAtomTable *out);
void pcrec_clskit_select(Arena *a, const PcrecCpRange *iv, int n,
                         const ClsSelectIn *in, ClsChoice *out);
const ClsRow *pcrec_clskit_rows(int *nrows);
void pcrec_clskit_select_tables(Arena *a, const PcrecCpRange *const *sets,
                                const int *nivs, int nset, int tune,
                                unsigned deny, ClsTabChoice *out);
const ClsTabRow *pcrec_clskit_table_rows(int *nrows);
unsigned pcrec_clskit_kit_lambda(void);

const char *pcrec_clskit_leaf_name(ClsLeaf l);
const char *pcrec_clskit_form_name(ClsForm f);

void pcrec_clskit_emit_kit(StrBuf *c, const char *fn, const ClsKit *k);
void pcrec_clskit_emit_whole(StrBuf *c, Arena *a, const char *fn, ClsForm f,
                             const PcrecCpRange *iv, int n);
void pcrec_clskit_emit_atom_table(StrBuf *c, const char *tab,
                                  const ClsAtomTable *t);
void pcrec_clskit_emit_atom(StrBuf *c, const char *fn, const char *tab,
                            const ClsAtomTable *t, int k);

#endif
