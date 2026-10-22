/* src/gen/known.h — [KIT-VERIFY] U1: what is KNOWN at a `cover` candidate
 * (docs/design/kit_proof.md §5.1; [MATCH-KNOWN]'s first member).
 *
 * Three records and one helper. `MkLang` is a PATTERN fact (src/facts,
 * `span_facts`); the two here are gen's:
 *   - `MkEnd`, a MACHINE fact read off the route's anchored machine A
 *     (`Job.adfa`): the end at k, the context before and after, and A's own
 *     per-position sets, C8's other producer;
 *   - `MkKnown`, a SUBJECT fact: a REFERENCE to the kit's class at the
 *     point `(at, src)`, never a copy of it.
 * `pcrec_known_derive` derives knowledge from them, never an admission: the
 * admission is `cover_conj[]` (known.c), read in order, whose first failing
 * row is the `why`. */
#ifndef PCREC_GEN_KNOWN_H
#define PCREC_GEN_KNOWN_H

#include "gen/memfn_sites.h"

/* A context side's absent rule: what holds where the side's byte lies
 * outside the subject. The zero is UNSTATED, refused where read. */
typedef enum { MK_ABS_UNSTATED = 0, MK_ABS_SATISFIES, MK_ABS_FAILS } MkAbsent;

typedef struct {
    uint8_t  k;                          /* the fixed width; 0 = no fixed end */
    uint8_t  ctx_before[32];             /* C_{-1}: bytes whose entry is live  */
    uint8_t  ctx_after[32];              /* C_k: bytes before which k accepts  */
    uint8_t  absent_before, absent_after;  /* MkAbsent                         */
    uint8_t  set[MF_MAX_SPAN_POS][32];   /* A's S_d, d < k (C8's control)      */
    int      x;                          /* the EMITTED entry constant (s0)    */
    int      r0;                         /* the walk's one live entry row      */
} MkEnd;

typedef enum { MK_AT_UNSTATED = 0, MK_AT_KIT_CANDIDATE } MkAt;
typedef enum { MK_SRC_UNSTATED = 0, MK_SRC_KIT_PROOF } MkSrc;
typedef struct {
    MkAt            at;
    MkSrc           src;
    const mf_class *cls;                 /* NULL: nothing known              */
} MkKnown;

/* What follows from the three: knowledge, not admission. */
typedef struct {
    uint8_t prefix;       /* largest L <= exact_len with proven[d] ⊆ S_d, d < L */
    int8_t  suffix_lo;    /* first offset of the trailing proven run, or -1     */
    uint8_t ctx_proven;   /* bit 0: before, bit 1: after                        */
} MkDerived;

MkDerived pcrec_known_derive(const MkLang *lang, const MkEnd *end, const MkKnown *known);

/* THE COVER DECISION of one compile attempt, memoized on the Job: the walk of
 * `cover_conj[]` (kit_proof.md §1.1), the records it read, and the kit's
 * class for the REPORT description it asked. `why` is the first failing
 * row's id (`fixed-width`, `exact/producers-disagree`, ...), NULL where every
 * row holds. */
typedef struct PcrecCover {
    const char   *why;
    MkEnd         end;
    const MkLang *lang;
    MkKnown       known;
    mf_class      cls;
    /* the machines the decision read (its memo key, known.c) */
    bool          key_ok;
    const void   *key_st;
    int           key_n;
    int           key_fin;
} PcrecCover;

/* The memo, walked on first ask. Every reader (the `cover` row's predicate,
 * `emit_cover`, the trace records) reads this one decision. */
const PcrecCover *pcrec_cover(Ctx *cx);

/* THE REPORT DESCRIPTION (kit_proof.md §2.5): the FIND / STMT / ASSIGN site
 * `cover` asks and defines, from the admitted decision `cv` alone: its WINDOW
 * statement (D172, window_site.md §1.2's cover row: span 0 = S_0..S_{k-1},
 * one span per constrained context side, its core empty where absence
 * SATISFIES; every span verify YES; the floor SUBJECT) and the frame
 * (`site_kind` REPORT), and its hooks at indent `ind` (NULL at a define).
 * `stem` is the storage stem the define offers (W5). The ask (C13) and the
 * define read this one constructor. */
mf_site *pcrec_cover_site(Ctx *cx, const PcrecCover *cv, const char *stem,
                          const char *ind, mf_hooks *h, PcrecMfU *u);

/* C14 AS A CHECK (kit_proof.md §2.5 step 2): "" where class `cls` proves
 * EXACTLY the stated sets at every offset of `cv`'s description (S_d for
 * d < k, C_{-1} and C_k where an item states them, nothing elsewhere), else
 * the first difference, named, in either direction. */
const char *pcrec_cover_proof_diff(Ctx *cx, const PcrecCover *cv, const mf_class *cls);

#endif /* PCREC_GEN_KNOWN_H */
