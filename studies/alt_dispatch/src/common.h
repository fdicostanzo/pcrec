/* common.h -- shared types for the alternation-dispatch study [ENG-ISL.S0].
 *
 * A branch is a sequence of ByteSets rather than a plain literal string
 * DELIBERATELY: it mirrors src/ir/nfa.c's TItem (a class-bitmap sequence,
 * not raw bytes), which is what lets a `ci`-wrapped branch (each alphabetic
 * position admits {lower, upper}) be a first-class input to every algorithm
 * here with no special-casing -- exactly as nfa.c's trie treats a `(?i)`
 * word as a class chain, never as two literal copies. For this study's
 * inputs every ByteSet has 1 or 2 members (case-fold pairs are the only
 * multi-member class the bench's seven shapes produce), which is also why
 * nfa.c's rule 2 (overlapping non-identical classes) stays vacuous here --
 * see docs/design/alt_dispatch_study.md for the argument.
 */
#ifndef ALT_DISPATCH_COMMON_H
#define ALT_DISPATCH_COMMON_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t w[8]; /* 256-bit membership bitmap, bit (byte & 31) of w[byte>>5] */
} ByteSet;

static inline void bs_clear(ByteSet *s) { for (int i = 0; i < 8; i++) s->w[i] = 0; }
static inline void bs_add(ByteSet *s, unsigned char c) { s->w[c >> 5] |= (1u << (c & 31)); }
static inline bool bs_test(const ByteSet *s, unsigned char c) {
    return (s->w[c >> 5] >> (c & 31)) & 1u;
}
static inline bool bs_eq(const ByteSet *a, const ByteSet *b) {
    for (int i = 0; i < 8; i++) if (a->w[i] != b->w[i]) return false;
    return true;
}
static inline bool bs_disjoint(const ByteSet *a, const ByteSet *b) {
    for (int i = 0; i < 8; i++) if (a->w[i] & b->w[i]) return false;
    return true;
}
/* Lowest byte value the set admits (used only to give trie construction a
 * deterministic sort key; membership at match time never uses this). */
static inline int bs_min_byte(const ByteSet *s) {
    for (int i = 0; i < 8; i++) {
        if (s->w[i]) {
            for (int b = 0; b < 32; b++) if ((s->w[i] >> b) & 1u) return i * 32 + b;
        }
    }
    return -1;
}

typedef struct {
    ByteSet *seq;   /* length `len` */
    int len;
    int index;      /* original alternation index, 0-based, preference order */
} Branch;

typedef struct {
    Branch *br;
    int n;
    char name[64];
    char mode[16];  /* "literal" or "ci" */
} BranchSet;

/* Load a .branches file: header comments (`# ...`), one literal word per
 * remaining line. `mode` "ci" builds a 2-member {lower,upper} class at every
 * alphabetic position; "literal" builds singleton classes throughout. */
BranchSet *bset_load(const char *path);
void bset_free(BranchSet *bs);

typedef struct {
    unsigned char *data;
    size_t len;
    char name[64];
} Subject;

Subject *subject_load(const char *path);
void subject_free(Subject *s);

/* One dispatch algorithm's answer at one subject position: `hit` false means
 * no branch matches here; else `index`/`match_len` are the leftmost-first
 * winner's alternation index and consumed length. */
typedef struct {
    bool hit;
    int index;
    int match_len;
} Answer;

/* Per-position cost counters, accumulated by the caller across a whole
 * subject sweep. What each field means is algorithm-specific; see each
 * algo's header for the definition it fills in. */
typedef struct {
    long long tries;       /* branch attempts / trie steps / hash probes */
    long long verify_bytes; /* byte-level compares performed */
    /* (e) VM-NATIVE TRIE WALK only (ruling R1, 2026-09-03): a frame is
     * "pushed" at a COMMIT node (a resumable point) or once for the post-
     * walk deferred-mask fallback -- see algo_trie.c's trie_dispatch_vm.
     * `deferred_seen` is the size the deferred list reached on THIS call;
     * the harness tracks the running max across a whole sweep as the
     * "mask width needed" the ruling asks for. Zero for every other
     * algorithm. */
    long long frames;
    int deferred_seen;
} Cost;

double now_ns(void);

#endif
