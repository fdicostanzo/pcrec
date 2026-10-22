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

#include "core/ksrc.h"

typedef struct Ctx Ctx;

/* One `serves` line of a pre-parsed store block (the same three fields the
 * reader's `RxtServe` keeps). */
typedef struct {
    const char *query, *encs, *via;
} PcrecFindServe;

/* One `row` of a `cpfreq` block: a Unicode scalar value and its count
 * (design §2.2-§2.3; key `U+HHHH`). */
typedef struct {
    uint32_t           cp;
    unsigned long long count;
} PcrecFindCp;

/* One DATA block of a store bundle, PRE-PARSED at build time (design §13 B1
 * (3)): what the one `.rxt` reader returns for the embedded text, generated
 * from that text by `scripts/ksgen.c` into
 * `src/core/findings_table.inc` (committed; `make gen-findings`), so a
 * compile reads a table and never parses.
 * `tests/findings/` parses the embedded text through the library and checks
 * it agrees with this, block for block. */
typedef struct {
    const char               *bundle;   /* the owning bundle's name */
    const char               *kind;     /* "freq" or "cpfreq" */
    size_t                    line;     /* the kind keyword's line */
    const PcrecFindServe     *serves;
    size_t                    nserves;
    const unsigned long long *counts;   /* freq: 256 entries; else NULL */
    const PcrecFindCp        *cps;      /* cpfreq: its rows, ascending */
    size_t                    ncps;     /* ... and how many; else 0 */
    /* [WINDOW-E1] the block's own `provenance` stanza (required under a data
     * block by the schema): its `source` token, its `bytes` row (0 where
     * the stanza has none: `source authored` forbids it) and its closed
     * `fidelity` token, NULL where it declares none. A query's provenance
     * is read from these (D162 add. 4), never from the chain position. */
    const char               *prov_source;
    unsigned long long        prov_bytes;
    const char               *prov_fidelity;
} PcrecFindTblBlock;

/* One BUNDLE of the pre-parsed store: its name, its `include <x>` name (the
 * angle brackets stripped) or NULL, and its `analysis` line — what the chain
 * walk needs of a bundle beyond its blocks ([FINDINGS] B2, design §4.3). */
typedef struct {
    const char *name;
    const char *include;
    size_t      line;
} PcrecFindTblBundle;

/* ---- RESOLUTION: the chain a compile reads (design §4) --------------------
 *
 * Where a link's bundle was found. The stop ORDER is the search order, and
 * `PCREC_FIND_STOP_DEFAULT` is the chain's implicit terminal: the built-in
 * `default`, reached by IDENTITY and never by a name lookup (§0.6), so a
 * `-I` directory holding a `default.rxt` cannot move an artifact that did
 * not name it. An explicit `include <default>` IS a name lookup, and lands
 * as `PCREC_FIND_STOP_STORE` when the store answers it. */
typedef enum {
    PCREC_FIND_STOP_SOURCE,   /* S1: the compiling file / analysis_source   */
    PCREC_FIND_STOP_DIR,      /* S2: an `-I DIR/<name>.rxt` file            */
    PCREC_FIND_STOP_STORE,    /* S3: the embedded store, by name            */
    PCREC_FIND_STOP_DEFAULT   /* the terminal, by identity                  */
} PcrecFindStop;

/* One LINK of a resolved chain: a bundle, where it was found, and its data
 * blocks — COPIED out of whatever parse found it, so a chain owns nothing
 * but its arena and outlives the files it was read from. */
typedef struct {
    const char              *bundle;
    PcrecFindStop            stop;
    const char              *location;  /* S2: the file's path; else NULL  */
    const char              *include;   /* its `include` name, or NULL     */
    const PcrecFindTblBlock *blocks;
    size_t                   nblocks;
} PcrecFindLink;

/* The chain: the selected bundle, its `include`, that bundle's `include`,
 * ..., then the built-in `default` (design §2.1, §4.3). `n == 0` means the
 * compile resolved nothing, which the accessor reads as `[default]`. */
typedef struct {
    const PcrecFindLink *links;
    size_t               n;
} PcrecFindChain;

/* What deriving a query's answer came to ([WINDOW-E1], window_contract.md
 * §3.7.1). The derivation never refuses: the refusal of an UNDERIVABLE or
 * BROKEN answer belongs to the reader that ASKS (the ask path), so offering
 * the answer to the kit cannot refuse a compile that asks nothing (§3.3
 * rule 9). */
typedef enum {
    PCREC_FIND_ST_UNDERIVED,    /* not derived yet: the memo is empty */
    PCREC_FIND_ST_OK,           /* a block answered and derived a table */
    PCREC_FIND_ST_NONE,         /* nothing along the chain answers */
    PCREC_FIND_ST_UNDERIVABLE,  /* the answering block normalizes to nothing */
    PCREC_FIND_ST_BROKEN        /* its table breaks the postcondition */
} PcrecFindStatus;

/* THE CONSUMPTION RECORD for one compile ATTEMPT (design §6.4): the chain
 * this attempt resolved, the memo of each query's derived answer, and which
 * queries a reader ASKED. The memo (`*_status` ... `byte_rate[]`) is filled
 * by whoever derives first — the ask or the analysis object's offer — and
 * the ASK alone (`*_asked`) is consumption, the stamp's input. It lives in
 * `Job`, so the `compile_driver` retry ladder resets it with every other
 * per-attempt field and the stamp (§7) reads the FINAL attempt's record.
 * Only `src/core/findings.c` reads the memo fields
 * (tests/findings/structural_check.py S4). */
typedef struct {
    PcrecFindChain chain;         /* resolved at the attempt's start (§4.3) */
    bool        byte_rate_asked;  /* `pcrec_find_byte_rate` was called */
    PcrecFindStatus byte_rate_status; /* what the derivation came to;
                                     UNDERIVED until the memo is filled */
    const PcrecFindTblBlock *byte_rate_block; /* the answering block, or NULL */
    const char *byte_rate_via;    /* ... and its `serves` line's derivation */
    bool        byte_rate_have;   /* the memo holds a table (a block answered
                                     and derived), whether or not anything
                                     asked */
    const char *byte_rate_bundle; /* the bundle whose block answered */
    uint64_t    byte_rate_digest; /* what it consumed (design §7) */
    uint32_t    byte_rate[256];   /* the answer: ppm, sum 1,000,000 */
#ifdef PCREC_KS_TRACE
    const char *trace_last;       /* the last traced reader: a repeat is one record */
#endif
} PcrecFindRec;

/* The embedded store's `.rxt` text for bundle `name` and its length, or NULL
 * when the store has no such bundle (design §8.1). */
const char *pcrec_find_store_text(const char *name, size_t *len);

/* The store's `i`th bundle name, or NULL past the last. */
const char *pcrec_find_store_name(size_t i);

/* The pre-parsed store: every block of every bundle, in store order. */
const PcrecFindTblBlock *pcrec_find_store_blocks(size_t *n);

/* The pre-parsed store's bundles, in store order. */
const PcrecFindTblBundle *pcrec_find_store_bundles(size_t *n);

/* The link the store answers for bundle `name` (its blocks point into the
 * store's own table), with `stop` as given; false when the store has no
 * such bundle. `PCREC_FIND_STOP_DEFAULT` with `name` "default" is the
 * chain's terminal. */
bool pcrec_find_store_link(const char *name, PcrecFindStop stop,
                           PcrecFindLink *out);

/* THE SELECTION RULE (design §2.4, §4.4), its one spelling: the FIRST block
 * along `chain` with a `serves <query> when …<enc>…` line, or NULL (NONE).
 * `*link` receives its link index. The compile's accessor and the
 * `--list-analysis` resolution section both ask it, so the listing's
 * `resolution` row is the stamp's answer by construction. */
const PcrecFindTblBlock *pcrec_find_chain_answer(const PcrecFindChain *chain,
                                                 const char *query,
                                                 const char *enc,
                                                 size_t *link,
                                                 const PcrecFindServe **serve);

/* ---- THE QUERY VOCABULARY ([WINDOW-E1], window_contract.md §3.2) ---------
 *
 * One row per [FINDINGS] query, in the stamp's fixed order: the query's
 * tag, the version of the payload pcrec carries for it (0: none yet, so the
 * kind is listed ABSENT), and what the kind is when nothing MEASURED
 * answers it — `ARRIVES` (present anyway, as an authored table or as
 * pcrec's no-information answer: D162 add. 2, on exactly the queries a
 * pcrec reader asks, add. 3's refinement) or `ABSENT`. The vocabulary's ONE
 * home: the derivation table, the `.rxt` reader, the chain's no-query note
 * and the listings all read it through `pcrec_find_query`. */
typedef enum {
    PCREC_FIND_UNMEASURED_UNSTATED,   /* refused by the table's self-check */
    PCREC_FIND_UNMEASURED_ARRIVES,
    PCREC_FIND_UNMEASURED_ABSENT
} PcrecFindUnmeasured;

typedef struct {
    const char         *tag;
    uint32_t            version;
    PcrecFindUnmeasured unmeasured;
} PcrecFindQuery;

/* The rows by index: the derivation table names its query by one of these. */
enum { PCREC_FQ_BYTE_RATE, PCREC_FQ_RUN_RARITY, PCREC_FQ_N };

/* The vocabulary's `i`th query, or NULL past the last. */
const PcrecFindQuery *pcrec_find_query(size_t i);

/* The tags joined with ", " in vocabulary order ("byte-rate, run-rarity"),
 * arena text for a diagnostic that lists the vocabulary. */
const char *pcrec_find_query_tags(Arena *a);

/* One word of the closed DERIVATION vocabulary (design §2.4): the block KIND
 * that may declare it and the QUERY it answers (a `pcrec_find_query` row).
 * The vocabulary's one home — the `.rxt` reader validates `serves ... via`
 * against it and `pcrec_find_derive_counts` implements it, beside each other
 * here. */
typedef struct {
    const char *kind, *name;
    size_t      query;
} PcrecFindDeriv;

/* The vocabulary's `i`th derivation, or NULL past the last. */
const PcrecFindDeriv *pcrec_find_deriv(size_t i);

/* The 256 byte COUNTS a block's rows yield under byte-rate derivation `via`
 * (design §2.4), into `out`: `unigram` the `freq` block's own `counts`;
 * `encode-utf8` each `cps` count added once per byte of its UTF-8 encoding
 * (the enc seam's encoder, R5); `encode-latin1` each code point <= U+00FF's
 * count on that byte, the larger ones DROPPED with their total count in
 * `*dropped` (NULL to ignore; 0 for the other two). -1 when a derived count
 * exceeds `PCREC_MAX_FIND_COUNT` (the normalization's arithmetic bound);
 * -2 when `via` is not a byte-rate derivation. The `.rxt` reader asks it at
 * a block's close, so a stored block never reaches -1 at a compile. */
int pcrec_find_derive_counts(const char *via, const unsigned long long *counts,
                             const PcrecFindCp *cps, size_t ncps,
                             unsigned long long out[256],
                             unsigned long long *dropped);

/* The byte-rate block `fb` answers through derivation `via`: its derived
 * counts (`pcrec_find_derive_counts`) normalized (`pcrec_find_normalize`).
 * 0, or the first nonzero code of the two (a derivation's -1 is returned as
 * -3, so every code names one cause). The compile's accessor and the
 * `--list-analysis` resolution both read a rate through it. */
int pcrec_find_block_byte_rate(const PcrecFindTblBlock *fb, const char *via,
                               uint32_t ppm[256], unsigned long long *dropped);

/* §2.5's NORMALIZATION, the ONE function turning 256 counts into a byte-rate:
 * each count scaled into the mass the floors leave, every byte at least
 * `PCREC_FIND_FLOOR_PPM`, the residue on the largest entry (ties to the
 * lowest byte), so `ppm` sums to exactly 1,000,000. -1 when every count is
 * zero; -2 if a postcondition (the sum, the floor) fails, which no input
 * within the limits reaches. Counts are <= PCREC_MAX_FIND_COUNT, so the
 * arithmetic fits uint64. */
int pcrec_find_normalize(const unsigned long long c[256], uint32_t ppm[256]);

/* ---- THE STAMP (design §7) ----------------------------------------------- */

/* The queries a reader ASKED on this attempt, a bit per `PCREC_FQ_*` row
 * (`PCREC_FQ_BIT`). The knowledge stamp ORs it with every other attempt's
 * and every compound part's (D167 addendum 3). */
#define PCREC_FQ_BIT(q) (1u << (q))
unsigned pcrec_find_asked(const Ctx *cx);

/* The `<PREFIX>_FINDINGS` / `rx_info.findings` value for `consulted`, the
 * queries ANY attempt of the compile (and any compound part) consulted, a
 * bit per `PCREC_FQ_*` row (D167 addendum 3): one `query=bundle:digest`
 * item per query in it (`query=none` where nothing answered it), in the
 * fixed query order, `;`-joined; the empty string when it is empty. The
 * bundle and digest are this attempt's derivation, which every attempt of
 * one compile shares. Arena text. Read after the last reader has run (§6.4
 * rule 2; window_contract.md §3.7.3a). */
const char *pcrec_find_stamp(Ctx *cx, unsigned consulted);

/* The digest of a byte-rate, as the stamp spells it: FNV-1a-64 over the tag
 * `pcrec-find-1\0byte-rate\0` and the 256 derived ppm values, uint32
 * little-endian, in byte order (design §7) — no kind, no `via`, so the same
 * values from any block give the same digest. */
uint64_t pcrec_find_byte_rate_digest(const uint32_t ppm[256]);

/* `--list-analyses`' `rows_digest` (design §5.2): FNV-1a-64 over the tag
 * `pcrec-find-rows-1\0` and then, per block in order, the block's kind and a
 * NUL followed by each nonzero `(key, count)` as `u8, u64le` (a `cpfreq`
 * block's code point as `u32le`), ascending. A
 * DIFFERENT hash from the stamp's, named apart so the two cannot be
 * confused (§7): this one covers a bundle's rows, the stamp's covers what a
 * compile consumed. */
uint64_t pcrec_find_rows_digest(const PcrecFindTblBlock *blocks, size_t n);

/* [KNOW-SRC] the analysis kind's two digest ROLES (measure_sets.md §9.2
 * part 5), the two functions above as `pcrec_ks_digest` data: the STAMP role
 * (domain `pcrec-find-1\0`, the QUERY as its sub-key, a fold over the 256
 * ppm values; its document is a `const uint32_t[256]`) and the ITEM role
 * (domain `pcrec-find-rows-1\0`, no sub-key, a fold over the blocks; its
 * document is a `PcrecFindRowsDoc`). The analysis kind's row names both. */
typedef struct {
    const PcrecFindTblBlock *blocks;
    size_t                   n;
} PcrecFindRowsDoc;
extern const KsDigest pcrec_find_rate_role;
extern const KsDigest pcrec_find_rows_role;

/* ---- THE ACCESSOR AND THE PRIMITIVES (design §6.1) -----------------------
 *
 * THE NONE ANSWER IS SPELLED ONCE PER QUESTION KIND, inside the primitive
 * that answers it, and never at a reader [D126 Q4]: a reader hands the
 * accessor's result to a primitive and never tests it. */

/* byte-rate for THIS compile: 256 ppm entries summing to 1,000,000, or NULL
 * (NONE: nothing declares byte-rate under this compile's encoding). Derived
 * once per attempt and memoized in `Job.find`; the call records the ask. */
const uint32_t *pcrec_find_byte_rate(Ctx *cx);

/* The same ask, answered as a fact rather than a table: does a byte-rate
 * table answer THIS compile (else NONE)? For a reader that reports which
 * rule a pick answered by and must not test a rate pointer. */
bool pcrec_find_byte_rate_answers(Ctx *cx);

/* ---- THE OFFER: one query's state for the kit's analysis object ----------
 * ([WINDOW-E1], window_contract.md §3.2 T-KIND, §3.7.1).
 *
 * The facts pcrec states about one query of this attempt, in pcrec's own
 * vocabulary (src/gen/memfn_sites.c maps them onto `memfn.h`'s
 * `mf_analysis`; `src/core` never includes the kit's header). The source
 * is the answering block's own provenance stanza (D162 add. 4), never its
 * chain position: `prior-authored` for `source authored` or `fidelity
 * synthesized`, `measured` otherwise, `prior-none` when no table exists. */
typedef enum {
    PCREC_FIND_KIND_UNSTATED,
    PCREC_FIND_KIND_PRESENT,
    PCREC_FIND_KIND_ABSENT
} PcrecFindKindState;

typedef enum {
    PCREC_FIND_SRC_UNSTATED,     /* an ABSENT kind */
    PCREC_FIND_SRC_PRIOR_AUTHORED,
    PCREC_FIND_SRC_PRIOR_NONE,
    PCREC_FIND_SRC_MEASURED
} PcrecFindSource;

typedef struct {
    const char        *row;      /* the T-KIND row that decided (a trace word) */
    PcrecFindKindState present;
    PcrecFindSource    source;
    const char        *bundle;   /* the answering bundle; NULL unless
                                    PRIOR_AUTHORED or MEASURED */
    uint64_t           digest;   /* the payload's digest; 0 without one */
    unsigned long long bytes;    /* MEASURED: the stanza's `bytes`; else 0 */
    const char        *fidelity; /* the stanza's `fidelity`, NULL if none */
    const void        *payload;  /* non-NULL iff PRESENT and PRIOR_AUTHORED
                                    or MEASURED (byte-rate: uint32_t[256]) */
} PcrecFindOffer;

/* Query `query`'s offer for THIS attempt, into `*out`: evaluates T-KIND
 * through the query's NON-RAISING derivation. It never records an ask and
 * never refuses (an underivable answer offers `prior-none` or ABSENT, and
 * refuses only when a reader asks: §3.3 rule 9), so building the object
 * moves no stamp and no refusal. */
void pcrec_find_offer(Ctx *cx, size_t query, PcrecFindOffer *out);

/* PICK: which of n candidates to scan. Candidate i is the CUBE
 * (cand[i], care[i]): its members are the bytes b with (b & care[i]) ==
 * cand[i] (cand[i] & ~care[i] == 0). care == NULL means every care[i] is
 * 0xFF, i.e. every candidate is the one byte cand[i]. Cost of a candidate:
 * the rate summed over its members (MASS's own definition, so a byte costs
 * rate[cand[i]]). Returns the INDEX of the argmin, ties to `rightmost` (the
 * index of the reader's positional rightmost candidate, PCRE2's LASTCODEUNIT
 * rule) when it is among the minima and to the EARLIEST candidate otherwise.
 * NONE: the same argmin over MASS's NONE answer, the UNIFORM mass
 * (cardinality), so a byte beats a pair and a list of bytes alone answers
 * `rightmost` ([K82] (C), abi 60). The reader chooses only the candidate
 * ORDER, which is its tie rule. n >= 1, 0 <= rightmost < n. ([OPT-LITSCAN]
 * S4 C3 extended the candidates from bytes to cubes, litscan_s4.md §2.3.3:
 * one PICK kind, one NONE.) */
int pcrec_find_pick(const uint32_t *rate, const unsigned char *cand,
                    const unsigned char *care, int n, int rightmost);

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

/* Which position of a necessary RUN (`bytes[0..n)` with per-position masks
 * `mask[0..n)`, each position the cube (bytes[i], mask[i]); n >= 2,
 * n <= PCREC_MAX_REQ_RUN_SCAN) the emitted scan tests. PICK over the
 * positions as cubes in the order `[n-1, n-2, ..., 0]`
 * (`pcrec_find_set_pick`'s own `[rightmost, ...]` shape): the cheapest by
 * member-set mass, ties to the RIGHTMOST — its own positional rightmost
 * position, which is also the NONE answer [FIND-TIE]. */
int pcrec_find_run_scan_index(const uint32_t *rate, const unsigned char *bytes,
                              const unsigned char *mask, int n);

/* Where a run longer than `PCREC_MAX_REQ_RUN_EMIT` positions is truncated to.
 * MASS over each window of that many positions containing `idx`, a window's
 * mass being that of its MEMBERS (T for an exact position, T and T | ~K for
 * a pair): the lowest, ties to the leftmost — so on an exact run under NONE,
 * where every window ties, the leftmost. */
int pcrec_find_run_window_start(const uint32_t *rate,
                                const unsigned char *bytes,
                                const unsigned char *mask, int n, int idx);

/* MASS over `set` (`set[b]` nonzero for a member), in ppm, capped at
 * 1,000,000: a per-set cost input (the DFA candidate rate,
 * `pcrec_dfa_cand_ppm`; the offset-k selection's until D172 S2 commit 6). */
unsigned pcrec_find_set_ppm(Ctx *cx, const uint8_t set[256]);

/* ---- [KNOW-SRC] THE LOOKUP TRACE (measure_sets.md rev 3 §9.3) -------------
 *
 * In a `-DPCREC_KS_TRACE` build every rate read writes one stderr record,
 * `KSTRACE\tanalysis\t<query>\t<reader>\t<bundle|none>`, the READER being the
 * calling function (`__func__`, so no call site is edited; a reader's
 * consecutive repeats are one record), and each attempt's
 * resolution writes `KSTRACE\tanalysis\t-\tresolve\t-` first. It is the data-
 * mover census's ATTRIBUTION (`scripts/emit_sweep.py --data`): a moved
 * artifact names the readers that asked, and the FINAL attempt's queries and
 * bundles must equal the `<PREFIX>_FINDINGS` stamp's items (the cross-
 * check). The default build is unchanged: no record, no byte, no symbol. */
#ifdef PCREC_KS_TRACE
const uint32_t *pcrec_find_byte_rate_at(Ctx *cx, const char *reader);
unsigned pcrec_find_set_ppm_at(Ctx *cx, const uint8_t set[256],
                               const char *reader);
#ifndef PCREC_FIND_DEFINING
#define pcrec_find_byte_rate(cx) pcrec_find_byte_rate_at((cx), __func__)
#define pcrec_find_set_ppm(cx, set) pcrec_find_set_ppm_at((cx), (set), __func__)
#endif
#endif

#endif /* PCREC_FINDINGS_H */
