/* src/core/findings.h — THE FINDINGS SEAM: the byte-rate accessor, the rate
 * primitives, and the rate READERS that sit beside them ([FINDINGS] B1 =
 * [PATFACTS] step 3.1; docs/design/findings/design.md §6, D122/D126 Q4).
 *
 * Internal. A pass that wants a byte rate reaches it through this header and
 * nothing else: there is no rate table anywhere but `src/core/findings.c`
 * (design §11.7), and no reader outside that file tests a rate pointer. */
#ifndef PCREC_FINDINGS_H
#define PCREC_FINDINGS_H

#include <stdbool.h>
#include <stdint.h>

typedef struct Ctx Ctx;

/* THE CONSUMPTION RECORD for one compile ATTEMPT (design §6.4): the derived
 * answer of each query this attempt ASKED, memoized so every reader derives
 * once. It lives in `Job`, so the `compile_driver` retry ladder resets it
 * with every other per-attempt field and the stamp (§7) reads the FINAL
 * attempt's record. */
typedef struct {
    bool        byte_rate_asked;  /* `pcrec_find_byte_rate` was called */
    bool        byte_rate_have;   /* ... and a block answered (else NONE) */
    const char *byte_rate_bundle; /* the bundle whose block answered */
    uint64_t    byte_rate_digest; /* what it consumed (design §7) */
    uint32_t    byte_rate[256];   /* the answer: ppm, sum 1,000,000 */
} PcrecFindRec;

/* One `serves` line of a pre-parsed store block (the same three fields the
 * reader's `RxtServe` keeps). */
typedef struct {
    const char *query, *encs, *via;
} PcrecFindServe;

/* One DATA block of a store bundle, PRE-PARSED at build time (design §13 B1
 * (3)): what the one `.rxt` reader returns for the embedded text, generated
 * from that text by `src/findings/findgen.c` into
 * `build/gen/findings_table.inc`, so a compile reads a table and never parses.
 * `tests/findings/` parses the embedded text through the library and checks
 * it agrees with this, block for block. */
typedef struct {
    const char               *bundle;   /* the owning bundle's name */
    const char               *kind;     /* "freq" */
    size_t                    line;     /* the kind keyword's line */
    const PcrecFindServe     *serves;
    size_t                    nserves;
    const unsigned long long *counts;   /* 256 entries */
} PcrecFindTblBlock;

/* The embedded store's `.rxt` text for bundle `name` and its length, or NULL
 * when the store has no such bundle (design §8.1). */
const char *pcrec_find_store_text(const char *name, size_t *len);

/* The store's `i`th bundle name, or NULL past the last. */
const char *pcrec_find_store_name(size_t i);

/* The pre-parsed store: every block of every bundle, in store order. */
const PcrecFindTblBlock *pcrec_find_store_blocks(size_t *n);

/* §2.5's NORMALIZATION, the ONE function turning 256 counts into a byte-rate:
 * each count scaled into the mass the floors leave, every byte at least
 * `PCREC_FIND_FLOOR_PPM`, the residue on the largest entry (ties to the
 * lowest byte), so `ppm` sums to exactly 1,000,000. -1 when every count is
 * zero; -2 if a postcondition (the sum, the floor) fails, which no input
 * within the limits reaches. Counts are <= PCREC_MAX_FIND_COUNT, so the
 * arithmetic fits uint64. */
int pcrec_find_normalize(const unsigned long long c[256], uint32_t ppm[256]);

/* ---- THE STAMP (design §7) ----------------------------------------------- */

/* The `<PREFIX>_FINDINGS` / `rx_info.findings` value for this attempt's
 * record: one `query=bundle:digest` item per query the compile ASKED
 * (`query=none` where nothing answered it), in the fixed query order,
 * `;`-joined; the empty string when nothing was asked. Arena text. Read
 * after the last reader has run (§6.4 rule 2). */
const char *pcrec_find_stamp(Ctx *cx);

/* The digest of a byte-rate, as the stamp spells it: FNV-1a-64 over the tag
 * `pcrec-find-1\0byte-rate\0` and the 256 derived ppm values, uint32
 * little-endian, in byte order (design §7) — no kind, no `via`, so the same
 * values from any block give the same digest. */
uint64_t pcrec_find_byte_rate_digest(const uint32_t ppm[256]);

/* ---- THE ACCESSOR AND THE PRIMITIVES (design §6.1) -----------------------
 *
 * THE NONE ANSWER IS SPELLED ONCE PER QUESTION KIND, inside the primitive
 * that answers it, and never at a reader [D126 Q4]: a reader hands the
 * accessor's result to a primitive and never tests it. */

/* byte-rate for THIS compile: 256 ppm entries summing to 1,000,000, or NULL
 * (NONE: nothing declares byte-rate under this compile's encoding). Derived
 * once per attempt and memoized in `Job.find`; the call records the ask. */
const uint32_t *pcrec_find_byte_rate(Ctx *cx);

/* PICK: the INDEX of the argmin of rate[cand[i]] over i < n, ties to the
 * EARLIEST candidate. NONE: `rightmost`, the index of the reader's positional
 * rightmost candidate (PCRE2's LASTCODEUNIT rule). The reader chooses only
 * the candidate ORDER, which is its tie rule. n >= 1, 0 <= rightmost < n. */
int pcrec_find_pick(const uint32_t *rate, const unsigned char *cand, int n,
                    int rightmost);

/* COMPARE: is `p` no commoner than `q` (rate[p] <= rate[q])? NONE: false —
 * unknown, so no density claim. Identity (p == q) is not a density fact and
 * stays the caller's own conjunct, ahead of this call. */
bool pcrec_find_no_commoner(const uint32_t *rate, int p, int q);

/* MASS: the rate summed over a SET (`set[b]` nonzero for a member), capped at
 * 1,000,000, or over a SEQUENCE of n bytes (a byte may repeat). NONE, for
 * both: the mass under the UNIFORM rate, floor(k * 10^6 / 256) with k the
 * member or byte count — CARDINALITY (design §0.8). An empty set, or n == 0,
 * is 0 under both arms. */
uint32_t pcrec_find_set_mass(const uint32_t *rate, const uint8_t set[256]);
uint32_t pcrec_find_seq_mass(const uint32_t *rate, const unsigned char *bytes,
                             int n);

/* ---- THE RATE READERS (design §6.1 "Where the rate readers live") --------
 *
 * Each is a SPEED choice among members a derivation already proved
 * necessary, so the worst a bad choice costs is speed on some subject. They
 * take plain byte arrays, so this layer needs no facts-layer type; the
 * derived facts in `src/facts/req.c` call them. */

/* Which member of a necessary SET (`bits`, 256-bit membership) the emitted
 * `memchr` tests. PICK over `[rightmost, the other members 255..0]`: the
 * rarest, ties to `rightmost` when it is among the minima and to the largest
 * such byte otherwise. -1 exactly when the set is empty (`rightmost < 0`). */
int pcrec_find_set_pick(const uint32_t *rate, const unsigned char bits[32],
                        int rightmost);

/* Which member of a necessary RUN (`bytes[0..n)`, n >= 2) the emitted
 * `memchr` tests. PICK over the run in order: the rarest, ties to the
 * leftmost; its positional rightmost member is the NONE answer. */
int pcrec_find_run_scan_index(const uint32_t *rate, const unsigned char *bytes,
                              int n);

/* Where a run longer than `PCREC_MAX_REQ_RUN_EMIT` is truncated to. MASS over
 * each window of that length containing `idx`: the lowest, ties to the
 * leftmost — so under NONE, where every window ties, the leftmost. */
int pcrec_find_run_window_start(const uint32_t *rate,
                                const unsigned char *bytes, int n, int idx);

/* The offset-k selection's per-set cost input (src/opt/prefix_k.c): MASS
 * over `set` (`set[b]` nonzero for a member), in ppm, capped at 1,000,000. */
unsigned pcrec_find_set_ppm(Ctx *cx, const uint8_t set[256]);

#endif /* PCREC_FINDINGS_H */
