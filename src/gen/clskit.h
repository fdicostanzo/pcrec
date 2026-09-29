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
 * Four things live here:
 *   - the per-section LEAF forms plus the sectioning DP (`pcrec_clskit_
 *     partition`), the design's `K`. It is a SIZE optimizer only (D131
 *     item 2), and its one pinned λ is table data in clskit.c;
 *   - the WHOLE-SET forms `PAGE3`/`PAGE2`/`BITMAP1` (§1.3);
 *   - the shared byte ATOM table ([OPT-CLSPACK], D131 item 6);
 *   - THE SELECTION, D131 item 1's `--tune` class-form table. It is one
 *     first-match table with rows as data (`pcrec_clskit_rows`).
 *
 * NO EMITTER CALLS ANY OF IT YET (S1). The first caller is S4 (VM decode +
 * kit), or S2 for the byte tier. That caller wires `tune` from `--tune` and
 * maps the row denies (`ClsDeny`) onto whatever public deny flag D129 Q2's
 * `-fno-cls-kit` becomes. Until then nothing here is caller-observable.
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
 * the terminal row's, which cannot be denied. */
typedef enum {
    CLSD_NONE,
    CLSD_ATOM,
    CLSD_BYTE_KIT,
    CLSD_BYTE_TABLE,
    CLSD_SIZE_PAGE3,
    CLSD_SPEED_PAGE2,
    CLSD_SPEED_BITMAP1,
    CLSD_MID_PAGE3,
    CLSD_NDENY
} ClsDeny;

/* A row of the selection table, as data a listing can print. */
typedef struct {
    const char *name;
    const char *pred_desc;     /* the predicate, one line */
    unsigned    positions;     /* bit (tune + 2) for each --tune position */
    int         pred;          /* clskit.c's ClsPred tag */
    ClsForm     form;
    ClsDeny     deny;
} ClsRow;

/* What the selection sees beyond the set: the dial position, the row
 * denies, and the artifact's byte-class population (the atom rows' input).
 * `atoms` may be NULL, meaning no shared table is on offer. `kit` may be
 * NULL; if not, it must be this set's `K` (`pcrec_clskit_partition` at
 * `pcrec_clskit_kit_lambda()`, all leaves), and the selection reuses it
 * rather than running the DP again. */
typedef struct {
    int                 tune;       /* -2..+2 */
    unsigned            deny;       /* OR of 1u << ClsDeny */
    int                 nsites;     /* byte-class sites sharing `atoms` */
    const ClsAtomTable *atoms;
    int                 atom_index; /* this set's row in `atoms` */
    const ClsKit       *kit;
} ClsSelectIn;

/* The selection's answer. `kit` is always filled (every predicate but the
 * byte and atom rows reads it). `row` indexes `pcrec_clskit_rows`. */
typedef struct {
    ClsForm   form;
    int       row;
    ClsKit    kit;
    long long bytes;            /* model bytes of `form` */
} ClsChoice;

void pcrec_clskit_partition(Arena *a, const PcrecCpRange *iv, int n,
                            unsigned lam, unsigned leaf_allow, ClsKit *out);
long long pcrec_clskit_whole_bytes(Arena *a, ClsForm f,
                                   const PcrecCpRange *iv, int n);
bool pcrec_clskit_atoms(Arena *a, const PcrecCpRange *const *sets,
                        const int *nivs, int nset, ClsAtomTable *out);
void pcrec_clskit_select(Arena *a, const PcrecCpRange *iv, int n,
                         const ClsSelectIn *in, ClsChoice *out);
const ClsRow *pcrec_clskit_rows(int *nrows);
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
