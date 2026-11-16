/* src/gen/known.h — [KIT-VERIFY] U1: what is KNOWN at a `cover` candidate
 * (docs/design/kit_proof.md §5.1; [MATCH-KNOWN]'s first member).
 *
 * Two records, both gen's:
 *   - `MkEnd`, a MACHINE fact read off the route's anchored machine A
 *     (`Job.adfa`): the end at k, the context before and after, and A's own
 *     per-position sets, the statement the REPORT site makes;
 *   - `MkKnown`, a SUBJECT fact: a REFERENCE to the kit's class at the
 *     point `(at, src)`, never a copy of it.
 * The admission is `cover_conj[]` (known.c), read in order, whose first
 * failing row is the `why`. The exact stretch has ONE producer, the walk of
 * A (docs/design/cover_cap.md §3.1); its record is `PcrecCover`'s. */
#ifndef PCREC_GEN_KNOWN_H
#define PCREC_GEN_KNOWN_H

#include "gen/memfn_sites.h"

/* A context side's absent rule: what holds where the side's byte lies
 * outside the subject. The zero is UNSTATED, refused where read. */
typedef enum { MK_ABS_UNSTATED = 0, MK_ABS_SATISFIES, MK_ABS_FAILS } MkAbsent;

typedef struct {
    uint16_t k;                          /* the fixed width; 0 = no fixed end */
    uint8_t  ctx_before[32];             /* C_{-1}: bytes whose entry is live  */
    uint8_t  ctx_after[32];              /* C_k: bytes before which k accepts  */
    uint8_t  absent_before, absent_after;  /* MkAbsent                         */
    const uint8_t (*set)[32];            /* A's S_d, d < k: the record's arena
                                            sets (`PcrecCover.sets`), never a copy */
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

/* How the cover walk of A ended (cover_cap.md §3.1): at the first depth a
 * row accepts (ACCEPT), one past a view-gated final newline (VIEW), where no
 * live row is left (EMPTY), or at the first depth two rows allow different
 * next-byte sets (BRANCH, the end of the exact stretch `L`). NONE: no walk
 * ran (a decline before C7). */
typedef enum { COVER_STOP_NONE = 0, COVER_STOP_ACCEPT, COVER_STOP_BRANCH,
               COVER_STOP_EMPTY, COVER_STOP_VIEW } PcrecCoverStop;

/* THE COVER DECISION of one compile attempt, memoized on the Job: the walk of
 * `cover_conj[]` (kit_proof.md §1.1), the records it read, and the kit's
 * class for the REPORT description it asked. `why` is the first failing
 * row's id (`fixed-width`, `exact/machine-inexact`, ...), NULL where every
 * row holds. */
typedef struct PcrecCover {
    const char   *why;
    MkEnd         end;
    MkKnown       known;
    /* THE RECORD (cover_cap.md §3.3), kept on every decision: how the walk
     * ended (`PcrecCoverStop`), the depth `k` it ended at (known where it
     * ended at ACCEPT or VIEW), the exact stretch `exact_len` (`L` on a
     * BRANCH, `k` otherwise; known wherever a walk ran) and its sets
     * `S_0..S_{exact_len-1}` in the Job's arena. The listing's `cover`
     * section and C12 read it; `MkEnd.set` points at it (C8). */
    uint8_t         stop;
    bool            k_known, exact_known;
    uint16_t        k, exact_len;
    const uint8_t (*sets)[32];
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
