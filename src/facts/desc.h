/* src/facts/desc.h — [RUN-POS-SET] the fixed-width PIECE DESCRIPTION
 * (docs/design/alt_normal_form.md §3.4-§3.5, stage 2p).
 *
 * A node-grain pure function over a subtree, built bottom-up by its callers
 * through ARM COMBINATORS (unit, zero, pos, cat, alt, none): a small set of WIDTH
 * GROUPS, each a sequence of position SETS over the caller's alphabet. The
 * soundness statement: every match of the subtree is, at contiguous
 * offsets, a string of ONE group's position product (a group is a superset
 * of the strings of its width). The callers walk; the module never does, so
 * one walk serves the run and the description alike (FIX-4: the combinator
 * interface, not a whole-subtree call). Two callers: the run walk (byte
 * level, src/facts/req.c) and the alternation owner (code-point level,
 * src/opt/altnf.c, the adjacency head below).
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
PdDesc pcrec_pd_zero(void);
PdDesc pcrec_pd_none(void);
PdDesc pcrec_pd_pos(Ctx *cx, const void *pos);
PdDesc pcrec_pd_cat(Ctx *cx, const PdCfg *c, PdDesc l, PdDesc r);
PdDesc pcrec_pd_alt(Ctx *cx, const PdCfg *c, PdDesc l, PdDesc r);

/* THE ADJACENCY HEAD, the module's second column (§3.5 r7 FIX-2; stage 2b,
 * the owner's, code-point level). Its rule at a zero-width node is the RUN's
 * opposite (read THROUGH, where the run cuts), so it is its own value and
 * never a field of `PdDesc`.
 *   h, pos   the positions every match consumes FIRST, at offsets 0..h-1 (at
 *            most `max_pos`, the first ones)
 *   closed   the subtree is fixed-width and `pos` covers all of it, so a
 *            following subtree's head continues it
 *   minw     the least it consumes, in the alphabet's symbols (FIX-3: the
 *   maxw     module's own widths); `maxw` is read only when `bounded`
 *   writes   it may write a capture or `\K`, a lookaround's body included;
 *            UNKNOWN counts as writes (§3.5 WRITES)
 * Arms: unit (EMPTY, and a zero-width node read through), pos (a class),
 * wall (no head: a repeat, FIX-1, or a node the head cannot read), cat, alt. */
typedef struct {
    int          h;
    bool         closed;
    bool         bounded;
    bool         writes;
    long long    minw, maxw;
    const void **pos;
} PdHead;

PdHead pcrec_ph_unit(void);
PdHead pcrec_ph_pos(Ctx *cx, const void *pos);
PdHead pcrec_ph_wall(long long minw, bool bounded, long long maxw, bool writes);
PdHead pcrec_ph_cat(Ctx *cx, const PdCfg *c, PdHead l, PdHead r);
PdHead pcrec_ph_alt(Ctx *cx, const PdCfg *c, PdHead l, PdHead r);

#endif
