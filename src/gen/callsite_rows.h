/* src/gen/callsite_rows.h — THE CALL-SITE CODE TABLE (compound.md §A.14;
 * inline_c.md §1.6, [INLINE-C] stage 1b): how a generated call site routes
 * its callee's return code, shared by every emitter that calls a matcher.
 *
 * ONE TABLE, TWO CALLEE CONVENTIONS, told apart by the `conv` column on the
 * callee's facts:
 *
 *   conv      success        no match   below that
 *   part      r > 0 (span)   r == 0     codes (a compound's part, D163)
 *   matchfn   r >= 0 length  r == -1    codes below -1 (every rx_matchfn:
 *                                       a callout's binding, an artifact's
 *                                       `<prefix>_match`)
 *
 * Its producers are the compound's controller (src/gen/emit_compound.c,
 * `part`) and a callout site (src/gen/emit_vm.c's `vm_callout`, `matchfn`).
 * A row is emitted only where the callee CAN RETURN its class, read off the
 * callee's facts; at an extern binding nothing is known, so every row is
 * live. */
#ifndef PCREC_GEN_CALLSITE_ROWS_H
#define PCREC_GEN_CALLSITE_ROWS_H

#include "core/internal.h"
#include "enc/enc.h"

typedef enum { CS_CONV_PART, CS_CONV_MATCHFN } CsConv;

/* What the call site knows about its callee. */
typedef struct {
    CsConv conv;
    bool vm;          /* it can give up, err internally, refuse a variable */
    bool guarded;     /* it can refuse a mid-character position */
    bool utf_check;   /* it can refuse an ill-formed subject */
    bool pred;        /* matchfn: a CHECK (`W_PRED`): it returns 0 or -1 only,
                         so a positive return is a contract break that traps */
    /* matchfn, a consuming callee: the expressions the length is bounded
     * by (the position, the subject, its length) and the encoding whose
     * character-start predicate the continuation position must satisfy. */
    const char *pos, *subj, *len;
    const PcrecEnc *enc;
} CsCallee;

/* The edges the CALLER supplies: one statement each. `giveup` is the
 * give-up row's propagation (NULL: `prop`). */
typedef struct {
    const char *succ;     /* the success edge */
    const char *fail;     /* the failure edge (no match, or -1) */
    const char *prop;     /* propagate the code unchanged */
    const char *giveup;
} CsEdges;

/* Writes the handling of one call's code `r` for callee `f`, at indent
 * `ind`: every applicable row as one `if` line in table order, then the
 * convention's fall-through row (part: no match; matchfn: success) as the
 * straight-line continuation. */
void pcrec_callsite_emit(Ctx *cx, StrBuf *c, const char *ind,
                         const CsCallee *f, const CsEdges *e);

#endif
