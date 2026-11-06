/* src/facts/desc.h — [RUN-POS-SET] the fixed-width PIECE DESCRIPTION
 * (docs/design/alt_normal_form.md §3.4-§3.5, stage 2p).
 *
 * A node-grain pure function over a subtree, built bottom-up by its callers
 * through ARM COMBINATORS (unit, pos, cat, alt, none): a small set of WIDTH
 * GROUPS, each a sequence of position SETS over the caller's alphabet. The
 * soundness statement: every match of the subtree is, at contiguous
 * offsets, a string of ONE group's position product (a group is a superset
 * of the strings of its width). The callers walk; the module never does, so
 * one walk serves the run and the description alike (FIX-4: the combinator
 * interface, not a whole-subtree call).
 *
 * Not a sealed-fact derivation: it reads no fact and no option, only the
 * positions its caller hands it (src/facts/CLAUDE.md's node-grain carve-out).
 * The alphabet is a PARAMETER (`PdAlpha`): a position is an opaque set its
 * alphabet's two operations know. The byte alphabet (a 256-bit set) is the
 * run walk's, in src/facts/req.c. */
#ifndef PCREC_FACTS_DESC_H
#define PCREC_FACTS_DESC_H

#include "core/internal.h"

/* A position set's two operations: the union, and equality. `join` may
 * return either argument where the union equals it (no allocation). */
typedef struct {
    const void *(*join)(Ctx *cx, const void *a, const void *b);
    bool (*same)(const void *a, const void *b);
} PdAlpha;

/* The caller's bounds and alphabet: at most `max_groups` width groups (over
 * it the description is dropped, `PD_OVER`), at most `max_pos` positions
 * stored per group (the LAST ones; a suffix of a piece is still a piece). */
typedef struct {
    const PdAlpha *alpha;
    int max_groups;
    int max_pos;
} PdCfg;

/* `PdGroup`/`PdDesc`, the value types, are facts.h's (the record holds
 * one: `PatFacts.req_pieces`). */
PdDesc pcrec_pd_unit(void);
PdDesc pcrec_pd_none(void);
PdDesc pcrec_pd_pos(Ctx *cx, const void *pos);
PdDesc pcrec_pd_cat(Ctx *cx, const PdCfg *c, PdDesc l, PdDesc r);
PdDesc pcrec_pd_alt(Ctx *cx, const PdCfg *c, PdDesc l, PdDesc r);

#endif
