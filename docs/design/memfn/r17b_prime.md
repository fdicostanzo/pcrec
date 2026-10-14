# R17-b′ — the candidate-finder table's first build: no iterator, both layers, thresholds from a measurement set

**Revision 1 (2026-10-14), lane r17bp, design only.** Branch `lane/memfn-r17bp`,
cut from the kit branch `lane/memfn-r17` at `9775409fc` (R17-b built there,
pcrec abi 77 on that branch; main is at abi 78 and has never had R17-b).
Nothing under `src/`, `memfn/src/`, `tests/` or `lib/` changes. No timing was
run. The three compile-only instruments this note cites are in
`r17b_prime/`, with their transcripts in `r17b_prime/out/` (own CLAUDE.md).
A D6 panel reviews this note before anything is built.

What it designs is the kit's proposal "R17-b′" (memfn/docs/responses.md,
notice of 2026-10-14). Main and Frank accepted it in principle on 2026-10-13/14
(D161 addenda 11-12, D166). R17-b shipped ONE form unconditionally (the table
walk became `mask8_swar`), and ALPHA read 62 WIN / 87 REGRESSION / 11 NULL.
R17-b′ replaces the unconditional swap with the kit's candidate-finder table
(D161 add. 11). It is seeded with the rows of `docs/design/regime_tables.md`
(rev 0.2, main) that need no iterator: R0, R1/R2, R5/R6 (only when E arrives)
and R7. Every threshold is a reference into a MEASUREMENT SET (D166).

Labels: **MEASURED** (read from a row or a counter), **DERIVED** (follows from
a measured value or from the form's text), **INTERPRETATION** (my inference),
**PROPOSED** (this note's design, for ruling).

---

## 0. Answers first

1. **The table (§1).** It is ONE declared array `fd_rows[]` in a new
   `memfn/src/finder.c`. Each row has an id, a `needs` bitset over the
   knowledge keys {P, E, A, N, M, H}, a layer set, a CONDITION, and a pick
   of (stop, form) with its `unpaid` fallback and an optional deny. The
   condition is a closed enum of predicate kinds whose operands are references
   into the active set. A row is evaluated at compile time when its needs are
   all compile-time knowledge, and becomes an emitted dispatch row when it
   needs N. Rows needing H are skipped until R17-b″. The STOP column is
   present now, with one value: the site's own one-span stop, which is
   R17-b's stop. R-18 adds stop rows to the same table. The table is listed
   with the active set's name and provenance (§1.4).
2. **The dispatch (§2).** The decision is evaluated ONCE per activation at
   the site's existing storage point (`mf_locals`), from N = `n − start`. It
   is stored as a form byte in the site's struct. Every use is ONE statement,
   the same at both layers: `if (lo < c.n) lo = <stem>__next(&c, lo, <table>);`.
   `<stem>__next` is a selector over per-layer bodies, each of which branches
   on the form byte. This shape is forced by the floor rule plus D155: a SIMD
   arm may add only guarded definitions and selector arms (§2.2). The
   thresholds are integer literals taken from the active set.
   - **M is not a run-time fact.** Every entry is its own body, so M is fixed
     per body at compile time (§2.4).
   - **Inside a find-all loop through `_search`, N is the REMAINING subject.**
     R17-b′ does not fix ALPHA's dense 1 MiB find-all rows: bounded prose1m
     all is +599 µs, dfa-hat prose1m is +232/+234 µs (§2.4, §7.2).
   - **A dispatch row must pay for its compare (§2.5).** Its standing charge
     must be NULL on the calls it does not help, and its gain must exceed the
     charge on the calls it does. That rule needs two quantities NO RUN HAS
     MEASURED. So under today's data no dispatch row is emitted, and R17-b′
     reduces to R0 + R7 until the first real set is measured (§3.3).
3. **The measurement set (§3).** The table has 18 quantity families (about 45
   values), keyed (quantity, form, site kind, cover shape), in walk-byte units
   or bytes. Fifteen families come from ONE run, grid1. Three are ABSENT: the
   per-call dispatch charge, the per-use dispatch charge, and the scaffold's
   walk charge. D166's one-run rule means grid1 cannot be patched with them,
   so the first EMBEDDED set needs a new run (`zen4-grid2`). Totality: a row
   whose reference is absent from the set is not evaluated, exactly like a
   row whose knowledge is missing. The table's last row (R7, LINER) reads no
   set value, so the table is total even with no set at all.
4. **The contract (§4).**
   - P is mostly there.
   - **Missing on the site:** `mf_site.body` (M, one-shot or iterator; today
     it is presumed, which is a silent default); a site-kind fact (needed by
     R5/R6 only); and the storage point's `start` hook.
   - **E is entirely missing.** No `mf_analysis` exists on any branch, and a
     set FIND site gets no frequency at all.
   - **The set's channel is a new read-only `mf_measures`, handed to
     `mf_art_begin`.** pcrec parses the container and passes the rows through
     uninterpreted. The key vocabulary is the kit's (D157).
5. **Bytes (§5).**
   - **SIMD-off vs main:** every R17-b mover moves (996 byte / 2,910 byte-vm
     artifacts). Most become WALK+V1+dispatch. R0's 219 / 243 become a
     walk-only scaffold, or stay bare walk if the scaffold cannot pay.
   - **vs R17-b:** every mover moves again.
   - **One abi event**, with readers found by grep (the R17-b list is the
     floor), plus a new every-artifact stamp `<PREFIX>_MEASURES`. The
     `MEMFN_FORMS` question is Q-R17P-1.
   - **Size, MEASURED on hand twins:** +0.32-0.42 KB of object per site over
     R17-b at SIMD-off (+0.64-1.02 KB over main); SIMD-on three forms
     +1.9-3.4 KB over main. These are guarded, so outside the caps.
6. **Denies and controls (§6).** Four new kit denies: `pf-terms-ndisp`,
   `pf-terms-r0`, `pf-terms-w32`, `pf-terms-w16`; the floor moves 7 → 11. G1
   runs at both layers. The G2 families extend to generated thresholds and
   W=64 forms. `make test-memfn-sets` checks answers under every committed set
   plus three synthetic extreme sets, which turns "answers never depend on the
   set" into a per-form corpus differential. There are 12 sabotage rows.
7. **Acceptance (§7).**
   - **SIMD-off:** R17-b′ turns hex-run and word-eq to NULL (R0) and most of
     bounded short find-all (R1). That removes 5.5% of ALPHA's OFF-layer loss
     ns. The named residual (1.17 ms) belongs to E and R17-b″.
   - **SIMD-on:** it renders A1/S1 above one block, which the spike says turns
     at least 7 of 30 losing groups.
   - **Refuted by:** a non-NULL R0 cell; a dispatch interval losing to its
     neighbour; a non-NULL dispatch charge on a LINER/TUG cell; any cell worse
     than R17-b.
8. **R17-b″ (§8).** The iterator adds rows (needs H) and one form (A3,
   storage in `rx_iter`). The table, the selector shape and the form byte are
   already there, so nothing is rebuilt.
9. **Questions (§9):** Q-R17P-1..8, each with a recommendation. Q-R17P-4 (the
   gate) and Q-R17P-7 (the first set needs a run) decide when anything ships.

---

## 1. The table as declared data

### 1.1 The C shape (PROPOSED; `memfn/src/finder.c`, `memfn/src/finder.h`)

```c
/* The knowledge keys (regime_tables.md §2). A row's `needs` names the keys
 * its condition reads. KN_COMPILE keys are known when the site is defined;
 * KN_N is known at the storage point; KN_H only inside an iterator body. */
enum { KN_P = 1u << 0, KN_E = 1u << 1, KN_A = 1u << 2,
       KN_M = 1u << 3,                  /* fixed per entry body (§2.4)      */
       KN_N = 1u << 4, KN_H = 1u << 5 };
#define KN_COMPILE (KN_P | KN_E | KN_A | KN_M)

/* The layer key a row applies under. A SIMD-on artifact evaluates the table
 * once per variant it renders: OFF (the floor body), W16, W32. */
enum { FL_OFF = 1u << 0, FL_W16 = 1u << 1, FL_W32 = 1u << 2 };

typedef enum { FS_SPAN0 } fd_stop;            /* R-17: the site's one span   */
typedef enum { FF_NONE, FF_WALK, FF_V1, FF_W64 /* A1 at w32, S1 at w16 */,
               FF_A3 /* R17-b'': W64 with its state in rx_iter */ } fd_form;

/* A reference into the active measurement set. `q` is the kit's quantity
 * id, `form`/`other` the forms it compares, `kind` the site kind (FK_ANY
 * until site kind is a fact, §4.1), `shape` the cover class (§3.2). */
typedef struct { uint16_t q; uint8_t form, other, kind, shape; } fd_ref;

typedef enum {
    FC_ALWAYS,          /* R7                                                  */
    FC_NO_SAVING,       /* R0: cover has >= 2 RANGE terms AND the measured
                           per-byte saving of `a.form` over the walk at the
                           2-range cover is <= the set's null floor `b`       */
    FC_N_BELOW,         /* R1/R2: N < a (a crossover, bytes)                   */
    FC_G_BELOW,         /* R5/R6: E's landing gap < a (bytes)                  */
    FC_H_SPAN_BELOW, FC_H_SPAN_IN, FC_H_POP_BELOW   /* R3a/R3b/R4, R17-b''     */
} fd_cond;

typedef struct {
    const char *id;       /* "R1": listed; cited by `evidence`                 */
    uint8_t     needs;    /* KN_*                                              */
    uint8_t     layers;   /* FL_*                                              */
    fd_cond     cond;
    fd_ref      a, b;     /* the condition's operands (set references)         */
    fd_stop     stop;
    fd_form     pick;
    fd_form     unpaid;   /* what the row picks when its own form cannot pay
                             (§2.5); FF_NONE = the row is dropped and its
                             interval falls through                            */
    const char *deny;     /* memfn/src/options.def name, or NULL               */
    const char *evidence; /* listing text                                      */
} fd_row;

static const fd_row fd_rows[] = {
 { "R0",  KN_P|KN_A,            FL_OFF,        FC_NO_SAVING,
   { Q_BETA, FF_V1, FF_WALK, FK_ANY, SH_R2 }, { Q_NULL_FLOOR },
   FS_SPAN0, FF_WALK, FF_NONE, "pf-terms-r0",
   "SWAR saving ~0 at 2 RANGE terms; one more term raises V1's beta" },
 { "R1",  KN_P|KN_M|KN_N|KN_A,  FL_OFF|FL_W16|FL_W32, FC_N_BELOW,
   { Q_XOVER_SINGLE, FF_V1, FF_WALK, FK_ANY, SH_ANY }, { 0 },
   FS_SPAN0, FF_WALK, FF_NONE, "pf-terms-ndisp",
   "one-shot member-free call: V1 pays from ~36 B" },
 { "R2",  KN_P|KN_M|KN_N|KN_A,  FL_W16|FL_W32, FC_N_BELOW,
   { Q_BLOCK, FF_W64 }, { 0 },
   FS_SPAN0, FF_V1, FF_WALK, "pf-terms-ndisp",
   "below one 64-byte block W=64 pays the sub-block tail" },
 /* R3a, R3b, R4: needs KN_H; never satisfied outside an iterator body (§8). */
 { "R5",  KN_E|KN_P|KN_A,       FL_W16|FL_W32, FC_G_BELOW,
   { Q_GSTAR, FF_W64, FF_WALK, FK_SITE, SH_ANY }, { 0 },
   FS_SPAN0, FF_WALK, FF_NONE, NULL, "g* per site kind" },
 { "R6",  KN_E|KN_P|KN_A,       FL_OFF,        FC_G_BELOW,
   { Q_GSTAR, FF_V1, FF_WALK, FK_SITE, SH_ANY }, { 0 },
   FS_SPAN0, FF_WALK, FF_NONE, NULL, "g* per site kind (FRAGILE)" },
 { "R7",  KN_P,                 FL_OFF,        FC_ALWAYS, {0}, {0},
   FS_SPAN0, FF_V1,  FF_NONE, NULL, "LINER default, SIMD off" },
 { "R7s", KN_P,                 FL_W16|FL_W32, FC_ALWAYS, {0}, {0},
   FS_SPAN0, FF_W64, FF_NONE, NULL, "LINER default, SIMD on" },
};
```

Notes on the shape:

- **This is the house idiom, not a planner.** The table is first-match
  (memory `pcrec-decisions-as-first-match-tables`). R-18's priced argmin over
  candidate CHAINS (D161 add. 4-9, Frank's "combining or priced-argmin models
  all OK") becomes one more `fd_cond` kind whose operands are a listed
  candidate set. It is not a second mechanism.
- **R7 is two rows, one per layer.** Under the floor rule a SIMD-on artifact
  carries the SIMD-off body as well, so the OFF variant and the W16/W32
  variants are each the table evaluated under their own layer key. Each
  variant reads only rows declaring its key.
- **R2's `unpaid` is WALK, not FF_NONE.** If R2 were dropped, `[36, 64)`
  would fall through to R7s and get W64, which loses there by +1.3 to +15.8 ns
  (gridread §4.4). "V1 if emitted, else WALK" (regime_tables R2) becomes
  this column.
- **R5/R6 are present now and are never evaluated** until E exists (§4.2).
  Their row text is already the condition and the pick they will have.

### 1.2 Evaluation: one table, two times

For each defined PF set site, the kit evaluates `fd_rows[]` once per layer
variant it renders (OFF; plus W16 and W32 at SIMD-on). Per variant:

1. Walk the rows in order. Skip a row whose `layers` excludes the variant.
2. Skip a row whose `needs` are not available. That means: E absent; H, which
   is not available in a one-shot body; M unstated; or a set reference that
   resolves to ABSENT. The last one is the totality rule (§3.4).
3. If `needs ⊆ KN_COMPILE`, evaluate the condition now. If it is true, this row
   is the TERMINAL pick for every N not caught by an earlier runtime row, and
   evaluation stops. If it is false, skip the row.
4. If `needs ∋ KN_N`, the row becomes an EMITTED dispatch row. Its operands
   are resolved to integer literals from the set, its interval is
   `[previous boundary, its threshold)`, and evaluation continues.
5. **Merge:** adjacent emitted intervals with the same pick merge. A
   dispatch row whose pick equals the terminal pick disappears.
6. **Pay (§2.5):** each remaining dispatch row is tested. One that cannot
   pay takes its `unpaid` pick (or is dropped). Then merge again.
7. **The emitted form set** is the union of the picks that remain. With one
   form there is no dispatch at all, and the site renders exactly that form,
   as R17-b did.

### 1.3 Where the window-search stop sits

The pick is a (stop, form) pair. R17-b′ has one stop, `FS_SPAN0`: the site's
own predicate, one REQUIRED SET term at offset 0. That is R17-b's stop,
unchanged (setfind.md §2: the degenerate window). Every R17-b′ row picks it.

R-18 (D161 add. 3-9) adds stop values: another span, a span chained to a
back-search, and so on. It also adds rows whose conditions choose among them,
including the priced argmin. Nothing in §1.1's shape is specific to one stop.

### 1.4 The listing (PROPOSED)

- **The accessor:** `mf_finder_rows(size_t *n)`, beside `mf_options()`.
- **Printed by:** `pcrec --list-finder [--measures=NAME]`, a TSV under
  `docs/spec/table_contract.md`. It folds into [LIST-TABLES] when that row
  builds.
- **The header names the active set** with its provenance; each row shows
  the values its references resolve to.

```
# finder rows (memfn/src/finder.c); set zen4-grid2 v1 sha256:3f9a… box=zen4-7700x
#   run=<date> method=<id>@<ver> tier=kit composite=no
#row  needs        layers       condition                 value   unit     provenance           pick  unpaid  deny            status
R0    P,A          off          no-saving(V1,2-range)     0.022   ratio    grid1 F3 an.2.1      WALK  -       pf-terms-r0     compile
R1    P,M,N,A      off,w16,w32  N < xover1(V1,walk)       36      bytes    grid1 an.4.3 interp  WALK  -       pf-terms-ndisp  dispatch
R2    P,M,N,A      w16,w32      N < block(W64)            64      bytes    derived W; an.4.4    V1    WALK    pf-terms-ndisp  dispatch
R5    E,P,A        w16,w32      g < g*(W64,kind)          -       bytes    -                    WALK  -       -               skipped:E
R6    E,P,A        off          g < g*(V1,kind)           -       bytes    -                    WALK  -       -               skipped:E
R7    P            off          always                    -       -        -                    V1    -       -               terminal
R7s   P            w16,w32      always                    -       -        -                    W64   -       -               terminal
```

`--emit-facts` gains one row per delegated site with what the table produced
there: the emitted form set, the dispatch rows with their literals, and the
set name. Bytes stay countable per site (§5.4). Answering this needs a kit
accessor `mf_site_plan(art, handle)`, which the kit fills and pcrec prints.
No artifact byte moves for this listing.

---

## 2. Compile-time collapse and the emitted dispatch

### 2.1 Where it sits

- **The storage point.** This is the R17-a storage point (setfind.md §7.1),
  unchanged. pcrec already calls `mf_locals` there once per activation:
  - in `unanch_scan`, ahead of `size_t scan_position = <from>;`
    (src/gen/emit_dfa.c, the R17-a comment);
  - in the VM hat, at the entry seek in `<searchfn>_run`, ahead of the entry
    use (`pf_vm_emit_first_class`);
  - in the rev-end relocate path's own activation, with its own `from`.
- **The dispatch is evaluated there.** The form byte is written in the
  struct's initializer. This is after the entry's pre-checks and before the
  attempt loop. It is before pcrec's `if (search_from > subject_length)
  return 0;` (DFA), so the span arithmetic must not wrap (below).
- **The use is where R17-b's use is:** inside the attempt loop, at the DFA's
  candidate-start block and at the VM hat's entry seek and every retry.
- **`<stem>__next_candidate` is unchanged** (R17-b's `mask8_swar`). It is
  called only from inside `<stem>__next`. The dispatch is never inside
  `next_candidate`.

### 2.2 The C text

For one DFA prefilter site `rx_search_pf`, the stem and table are those of the
emitted artifact for `[0-9]+x`. Text marked `// R17-b` is R17-b's, unchanged.

**(a) WALK + V1: every SIMD-off artifact with a dispatch.**

```c
/* define (file scope) */
struct rx_search_pf__c {
    const unsigned char *s;
    size_t n;
    size_t base, top;
    unsigned long long m;
    unsigned char f;            /* the form this activation runs: 0 WALK, 1 V1, 2 W64 */
};
/* rx_search_pf__mask, __member, __next_candidate: R17-b's text, unchanged */
static inline size_t rx_search_pf__walk(const struct rx_search_pf__c *c, size_t lo,
                                        const unsigned char *t)
{
    while (lo < c->n && !t[c->s[lo]]) lo++;   /* pcrec's walk, bound read off the struct */
    return lo;
}
static inline unsigned char rx_search_pf__form__body(size_t n, size_t lo)
{
    size_t span = n - lo;       /* lo > n wraps high: the last row's pick, and the use's guard reads nothing */
    if (span < 36) return 0;    /* R1 -> WALK */
    return 1;                   /* R7 -> V1 */
}
static inline unsigned char rx_search_pf__form(size_t n, size_t lo)
{
    return rx_search_pf__form__body(n, lo);
}
static inline size_t rx_search_pf__next__body(struct rx_search_pf__c *c, size_t lo,
                                              const unsigned char *t)
{
    if (c->f == 0) return rx_search_pf__walk(c, lo, t);
    return rx_search_pf__next_candidate(c, lo);
}
static inline size_t rx_search_pf__next(struct rx_search_pf__c *c, size_t lo,
                                        const unsigned char *t)
{
    return rx_search_pf__next__body(c, lo, t);
}

/* storage point (rx_search, unanch_scan's position) */
    struct rx_search_pf__c rx_search_pf__c = { subject, subject_length, 0, 0, 0,
                                               rx_search_pf__form(subject_length, search_from) };
/* use (inside the attempt loop) */
            if (scan_position < rx_search_pf__c.n) scan_position = rx_search_pf__next(&rx_search_pf__c, scan_position, rx_can_begin_match);
```

- pcrec emits `rx_can_begin_match` again whenever WALK is in the form set
  (`mf_defined.reads_table = 1`).
- The table is passed at the use. This follows the K1-1 / `<p>_ofsskip`
  precedent: a helper that reads pcrec's table takes it as a parameter named
  at each use. That keeps the table's emission point where R17-a placed it,
  ahead of the loop in both bodies.
- A bounded site (`end_back` 1) keeps R17-b's two-part guard
  (`lo < c.n && c.n - lo > 1`), and its walk stops at `c->n - 1`.

**(b) WALK + V1 + A1: SIMD-on, R2 paid.** The SIMD-on rendering is (a) plus
guarded insertions only. The floor rule (C18) and D155 forbid anything else.

```c
#if defined(__x86_64__) && !defined(__ILP32__) && defined(__AVX2__)     /* levels.def LV_X86_W32 */
/* the V32 sub-block (setfind.md §3.4b), then: */
static inline size_t rx_search_pf__next_candidate__w32(struct rx_search_pf__c *c, size_t lo)
{ /* mask64_avx2: R17-b's body at W = 64 over the V32 primitives */ }
static inline unsigned char rx_search_pf__form__w32(size_t n, size_t lo)
{
    size_t span = n - lo;
    if (span < 36) return 0;    /* R1 -> WALK */
    if (span < 64) return 1;    /* R2 -> V1 (below one 64-byte block) */
    return 2;                   /* R7s -> W64 */
}
static inline size_t rx_search_pf__next__w32(struct rx_search_pf__c *c, size_t lo,
                                             const unsigned char *t)
{
    if (c->f == 0) return rx_search_pf__walk(c, lo, t);
    if (c->f == 1) return rx_search_pf__next_candidate(c, lo);
    return rx_search_pf__next_candidate__w32(c, lo);
}
#endif
/* the w16 (SSE2) arm: the same three definitions over V16 */

static inline unsigned char rx_search_pf__form(size_t n, size_t lo)
{
#if defined(__x86_64__) && !defined(__ILP32__) && defined(__AVX2__)     /* inserted */
    return rx_search_pf__form__w32(n, lo);                              /* inserted */
#elif defined(__x86_64__) && !defined(__ILP32__) && defined(__SSE2__)   /* inserted */
    return rx_search_pf__form__w16(n, lo);                              /* inserted */
#else                                                                   /* inserted */
    return rx_search_pf__form__body(n, lo);
#endif                                                                  /* inserted */
}
/* rx_search_pf__next: the same selector over __next__w32 / __next__w16 / __next__body */
```

The storage point and the use are byte-identical to (a). So a SIMD-on
artifact compiled where no guard holds runs exactly (a).

**(c) WALK + A1: SIMD-on, R2 unpaid.** R2 takes its `unpaid` pick (WALK) and
merges with R1. The w32 rows become `if (span < 64) return 0; return 2;` and
`__next__w32` loses its `f == 1` line. V1's `__next_candidate` stays in the
text because it is the floor body's form. Under the floor rule, "WALK + A1" is
a REACHABLE set, never a text set: the SIMD-off forms are always present.

**Single-form sites.**
- If only one form is emitted, there is no struct field `f`, no `__form`, and
  `__next__body` is that form alone.
- A V1-only site is R17-b's text routed through `__next`.
- A WALK-only site at SIMD-off (R0) is the scaffold with a walk body. The
  alternative is main's bare walk, and which of the two applies is the pay
  rule's call (§2.5, T3).
- The scaffold exists so that a SIMD arm can add W64 without editing a body
  (§5.1, F5).

### 2.3 Why the dispatch sits behind `__next` and not in the use

Two shapes were considered:
- **(U)** the walk inline in the use, under `if (c.f == 0)`;
- **(C)** the use always calls `__next`, which branches inside.

(U) is one predictable branch per use and keeps the walk's text where it is
today. But its use statement differs between layers (SIMD-on needs an
`f == 2` arm), and D155 forbids putting an `#if` into the body. Only (C) keeps
the use identical at every layer. (U) survives as the hand-twin shape used for
the size estimate (§5.4).

Measured on the cost side (`r17b_prime/out/walk_helper_asm.out`): the walk
moved into the helper and reached through the struct is NOT the same code as
today's inline walk. The holding function changes by −3 to +14 instructions on
six cells, and not one of the six is identical. That cost is the quantity
C_scaffold (§3.2, M18). Nothing is assumed free.

### 2.4 What N is, and what M is

- **N.** `N = n − start` at the storage point, where `start` is the
  activation's origin: `search_from` in the DFA forward scan and in the VM's
  `_search_run`, or the relocate path's moved start. It is computed once per
  activation.
- **One-shot calls.** For a single `_search` call, N is the span the call may
  scan.
- **Find-all through `_search`.** Inside a find-all loop (the caller's loop
  over `<prefix>_search`, match_api.md §3.1.3), N is the REMAINING subject,
  not the step to the next match. A dense find-all over 1 MiB makes about
  160,000 calls whose N is hundreds of KB, so every one is a LINER pick
  (V1 / W64) and every call restarts cold.
- **R17-b′ does not fix ALPHA's dense 1 MiB find-all rows.** bounded prose1m
  all (161,476 calls of +3.71 ns, +599,268 ns) and dfa-hat prose1m all/first
  (+231,943 / +234,456 ns) stay exactly as R17-b had them. Fixing them needs E
  (R6: the measured gap is below g\*) or the iterator (R3a/R4, R17-b″).
- **dfa-hat prose1m `first` is not a state-lost cell.** It is one call with
  75,836 uses and the state carried. It loses because the DFA consumes past
  the cached block (11% cache-served; r17loss §3.2). That loss is not
  predicted by any seed row; see §7.2 and F7.
- **M is not a call-entry fact.** regime_tables lists M (one-shot vs
  iterator) as known at call entry. But each entry is its own emitted body:
  `_search`/`_search_run` are one-shot, and D165's `next` will be an iterator
  body. So M is fixed per body at compile time, and no row ever emits a
  compare on M. R17-b′ states it as a site fact (§4.1) instead of presuming
  it.

### 2.5 The compare's cost, and the rule that drops a row that cannot pay

**The cost (INTERPRETATION; nothing measured).**
- Per activation: one subtraction, one or two compares, a byte store into the
  struct. That is one or two cycles' worth, roughly 0.1-0.4 ns on Zen 4.
- Per use: a load and test of a loop-invariant byte (register-resident after
  scalar replacement) and a well-predicted branch.
- Scaffold: whatever the scaffold adds to the walk path (§2.3).

None of these is measured. They are §3.2's M16-M18.

**The rule (PROPOSED).** Every quantity is in walk-byte units from the
active set. No call-length distribution is assumed, because the kit has none
(Q-R17P-3). A dispatch row r has interval I_r = [a_r, b_r), pick p_r and
alternative a′_r (its `unpaid`, else the pick the interval would fall through
to). Let ε be the set's null floor (M6), and let cost(f, N) be the measured or
derived single-call cost of form f at span N (from M7/M8 and β).

- **T1 (the row pays where it fires).** max over the set's measured points
  N ∈ I_r of [cost(a′_r, N) − cost(p_r, N)] > C_disp_call + ε · cost(a′_r, N).
- **T2 (the row costs nothing measurable where it does not fire).**
  C_disp_call ≤ ε · cost(f_next, b_r), where f_next is the pick just above
  b_r. That call is the cheapest one that pays the compare and gains nothing.
- **T3 (the site's dispatch costs nothing measurable per use).**
  C_disp_use ≤ ε · w_min. Here w_min is the smallest measured per-use cost
  among the forms behind the dispatch (M14's absolute w). The same test
  applies to C_scaffold on a walk-only scaffold site, against the walk's own
  per-use cost.

**Consequences.**
- A row that fails T1 or T2 takes its `unpaid` pick (or is dropped), and the
  table re-merges.
- A site that fails T3 gets NO dispatch: it renders its terminal pick alone.
  A walk-only scaffold that fails T3 renders main's bare walk, and that site
  then has no W64 arm at SIMD-on either (F5).
- An ABSENT C_disp_call, C_disp_use or C_scaffold fails the test it appears
  in. A dispatch can be emitted only when the set proves it pays.

**Why T2/T3 are bars and not a trade.** A dispatch that costs 0.3 ns on every
long call to save 2 ns on some short ones is a good trade if short calls are
common. The kit cannot know whether they are (the bench says 86% of its cells
are short, regimefacts §3, but that is the bench's mix, not this caller's).
"Never a measurable loss, sometimes a measurable gain" is the rule that needs
no distribution. It is strict by construction: at ε = 0.031 the bar is about
0.25 ns on a 36-byte V1 call, and about 0.07 ns per use at V1's w. If a
measured C_disp exceeds that, the dispatch is not emitted. That is the honest
outcome, and it is what the measurement exists to decide.

### 2.6 The thresholds are literals from the set

- The literals in `__form__*` (36, 64) are resolved from the active set at
  compile time and written as integer constants, with the set reference in a
  nonessential comment that is gated off by default.
- A different set produces different literals. So changing the default set
  moves bytes, and that is an abi event (D162: "data regeneration that moves
  an emitted byte is an abi event"; D166 item 1: the mover census rides the
  same commit).
- The `<PREFIX>_MEASURES` stamp (§5.3) changes with it on every artifact
  that read the set.

---

## 3. The measurement set (D166)

### 3.1 The unit, the keys, the rows

- **Unit u.** u = the scalar walk's per-byte cost on a PF one-term site,
  β_walk(PF, 1 term) = **0.1892 ns/B** (MEASURED, gridread §2.1 F3:
  member-free single calls, slope 64 KiB → 1 MiB). Costs are stored in u·B
  ("walk-bytes"). Per-byte rates are dimensionless ratios to u. Crossovers are
  in bytes. Absolute ns is provenance only.
- **Key.** (quantity, form, compared form, site kind, cover shape).
  - Site kind is `PF` / `PF-bounded` / `DFA-hat` / `VM-hat`, or `ANY` where
    the cell is not split by kind.
  - The cover shape is the cover's term multiset as `(RANGE, EQ, CUBE)`
    counts, read off the kit's own `mf_set_terms` result.
- **Provenance per row:** the slot, the report section, the method (the
  reader script and its commit), the box, the compiler, the run window and
  the tier (kit, UNOFFICIAL).

### 3.2 The table: every quantity R17-b′'s rows need (the FIRST INPUT to [MEASURE-SET])

Source: ONE run, slot grid1 (Zen 4 7700X dev box, CPU 14, 2026-10-13
19:33-20:56 EDT, five launches with an A/A pair per group, governor
performance, gcc 15.2 -O2), read by `docs/dev/lanes/gridread/gridread.py`
on `lane/memfn-gridread` @ 540649453. Citations "§x" are to
`docs/dev/lanes/gridread_report.md`. "Reader" names the R17-b′ rows or rules
that read the quantity.

| id | quantity | key (form / vs / kind / shape) | relative value | absolute (provenance) | source | reader | in grid1? |
|---|---|---|---|---|---|---|---|
| M1 | β, the unit | walk / – / PF / (1,0,0) | 1.000 | 0.1892 ns/B | §2.1 F3 | all | yes |
| M2 | β walk by terms | walk / – / ANY / 2t, 3t, 4t | 0.992, 1.002, 0.999 | 0.1877, 0.1896, 0.1891 | §2.1 | R0 | yes |
| M3 | β V1 by shape | V1 / – / ANY / (1,0,0), (2,0,0), (2,0,1), (3,1,0), (0,1,1) | 0.572, 0.978, 1.132, 1.410, 0.731 | 0.1082, 0.1851, 0.2141, 0.2667, 0.1384 | §2.1; (0,1,1) an. 2.3 | R0, T1 | yes |
| M4 | β S1 by shape | S1 / same five | 0.108, 0.177, 0.220, 0.285, 0.112 | 0.0205, 0.0334, 0.0417, 0.0540, 0.0212 | §2.1; an. 2.3 | T1 (W16) | yes |
| M5 | β A1 by shape | A1 / same five | 0.056, 0.079, 0.101, 0.143, 0.057 | 0.0106, 0.0150, 0.0192, 0.0270, 0.0107 | §2.1; an. 2.3 | T1 (W32) | yes |
| M6 | null floor ε | – | 0.031 (ratio) | p90 A/A over 141 F1 groups = 3.09% of base | §1.2 | R0, T1-T3 | yes |
| M7 | single-call fixed part F, n ≥ 64 | walk, V1, S1, A1 / – / PF / (1,0,0) | 25.1, 22.1, 24.8, 26.3 u·B | 4.74, 4.18, 4.70, 4.98 ns | §2.2 | T1, T2 | yes |
| M8 | single-call fixed part F, n = 48 (sub-block tail) | walk, V1, S1, A1 / – / PF | 25.6, 22.0, 129.7, 77.9 u·B | 4.84, 4.17, 24.54, 14.73 ns | §2.2 | T1, T2 | yes |
| M9 | single-call crossover | V1 / walk / ANY (measured PF) / member-free | 36 B (bracket 32-48) | L=32: V1 +0.6 ns; n=48: V1 −4.5 ns | §4.3 (interp.), §4.4 | R1 | yes |
| M10 | single-call crossover | S1, A1 / walk / ANY / member-free | 18 B, 20 B | interpolated | §4.3 | listed, not read by R17-b′ | yes |
| M11 | block step | W64 / V1 / ANY | 64 B | DERIVED (W = 64); MEASURED step at n 63→64 | §4.4 | R2 | yes |
| M12 | single-call delta at measured N | V1 − walk / PF member-free / N = 8, 32, 48, 63 | +12.2, +3.2, −23.8, −29.6 u·B | +2.3, +0.6, −4.5, −5.6 ns | §4.3, §4.4 | T1 (R1, R2) | yes |
| M13 | c_cold, per activation | V1, S1, A1 / walk / PF | +13.1, +15.3, +15.4 u·B | +2.47, +2.90, +2.91 ns | §2.4 | T1 (§7 checks) | yes |
| M14 | per warm use, absolute | walk, V1, S1, A1 / – / PF | 8.8, 12.6, 11.7, 11.8 u·B | 1.67, 2.38, 2.22, 2.23 ns | §2.3 (dig) | T3 (w_min) | yes |
| M15 | g\* | V1, S1, A1 / walk / PF, DFA-hat, bounded | V1 10.8-16.7 / 3.0-3.3 / 21.5 B; S1 4.3-4.7 / 2.1-2.4 / 3.6-5.8 B; A1 4.2-4.4 / 2.1-2.3 / 2.4-3.0 B | interpolated in log2 g | §4.1 | R5, R6 (with E) | yes |
| M16 | dispatch charge per activation | dispatch / none / ANY | — | — | no run | T1, T2 | **ABSENT** |
| M17 | dispatch charge per use | dispatch / none / ANY | — | — | no run | T3 | **ABSENT** |
| M18 | scaffold charge on the walk path, per use | walk-in-helper / walk-inline / PF, VM-hat | — | — (asm differs by −3..+14 insns, `r17b_prime/out/walk_helper_asm.out`) | no run | T3 (R0 sites) | **ABSENT** |

That is 18 quantity families and about 45 values. The cover shapes
(R, E, C) are those `mf_set_terms` gives for grid1's F3 sets, read off this
tree's emitted masks:

| set | shape |
|---|---|
| `[0-9]` | (1,0,0) |
| `[a-f0-9]` | (2,0,0) |
| `[A-Za-z_]` | (2,0,1) |
| `[0-9A-Fa-f_]` | (3,1,0) |
| dfa-hat's `{f,n,t}` | (0,1,1) |

### 3.3 Under today's data, R17-b′ is R0 + R7

- **The dispatch cannot be emitted on grid1.** M16-M18 are absent from
  grid1, so T1-T3 fail and every emitted dispatch row takes its `unpaid` pick
  or is dropped.
- **D166's one-run rule** ("one box, one run, one method version, never mixed
  across runs") forbids completing grid1 with a second run's dispatch numbers.
- **So the first EMBEDDED set must be a new run, `zen4-grid2`.** It re-measures
  M1-M15 on grid1's cells and adds the dispatch arms: the WALK+V1 scaffold
  with `f` forced to each form, against the single-form artifact, as
  member-free single calls at the M12 points and as dense in-call uses
  (M16-M18).
- **grid1 stays a design-time provisional set.** Embedded as it stands, it
  would ship R0 + R7 only: R17-b on the ≥2-range sites returned to the walk,
  with no dispatch anywhere (Q-R17P-7).

### 3.4 How rows read the set, and what an absent quantity does

- **When references resolve.** A row's operands are `fd_ref`s, resolved
  against the active set when the table is evaluated for a site.
- **ABSENT means not evaluable.** A reference that resolves to ABSENT makes
  the row's knowledge unavailable. The row is SKIPPED, exactly as a row
  needing E is skipped when E is absent.
- **No fallbacks.** There is no fallback to another set (sets are never
  mixed) and no fallback to a nearby key (no presumed values, memory
  `pcrec-no-silent-defaults`).
- **The stated no-data row** is the table's last row for the layer (R7 / R7s:
  LINER). It reads no set value. So the table is total with a partial set, an
  absent set, or a NULL `mf_measures` (the kit's own tests). The no-data
  output is R17-b's single-form site (D162 totality; D161 add. 12: "the
  default pick stays LINER").
- **The pay rule obeys the same rule.** An absent M16-M18 fails its test
  (§2.5), and the row falls to its `unpaid` pick. This is the same rule
  applied one level down, not a second mechanism.
- **R0's key uses a derived bound, not a presumption.** R0 reads β(V1) at
  the 2-RANGE cover (M3: saving 1 − 0.1851/0.1892 = 0.022 ≤ ε). The rule
  "another term cannot lower V1's β" is DERIVED from the form, not presumed:
  the SWAR cover ORs one more term's ops into every word
  (`mf_cover_mask_w8`), and M3 shows β rising with every added term
  (0.108 → 0.185 → 0.214 → 0.267). So the 2-range value bounds every cover
  with ≥ 2 RANGE terms. That makes R0 exactly regime_tables' "≥ 2 RANGE
  terms" (all 219 / 243 corpus sites, §5.1).
- **Keyed by exact shape instead, R0 would miss most of its population.** It
  would fire on only the measured shapes (2,0,0) and (2,0,1), which is 22 of
  219 sites. It would miss `\w`'s (3,0,1), which is 179 of them. That is the
  kit's call, noted here so the panel can see it (F6).

### 3.5 The set's shape for [MEASURE-SET] (what this note asks of it)

- **Format and store.** One set is one directory, `measures/<name>/`
  (third_party's shape: rows, `PROVENANCE.md`, the method id, the raw
  transcript and the reader). Rows are `key, value, unit, source`. The header
  holds the box, run, method, version, tier, the composite flag and a content
  hash. `make gen-tables` compiles the default into the binary.
- **Who interprets what.** pcrec parses the container. The kit interprets the
  rows whose keys are its own (§4.3). A main-owned quantity (armread's
  C_call, C_match and engine c_byte) uses the same format with pcrec's keys.
- **Generic class.** The generic class (D161 add. 12) is a DERIVED envelope
  set, labelled composite, built from measured sets by a stated rule. R17-b′
  needs none until a second box's set exists (F5).
- **Phases (Q-R17P-6).** M0 rides R17-b′'s build: the store, the embedded
  default, `mf_measures`, the read-only listing and the stamp. M1 is
  [MEASURE-SET]'s own build: `--measures=FILE|NAME`, the config line, the
  install-time tool and the envelope derivation.

---

## 4. Knowledge in the contract

### 4.1 P (site facts): present, and what is missing

**Present on `mf_site` / `mf_hooks` today (MF_SITE_ABI 12 on the kit
branch):**
- **Cover shape and range-term count:** `pred.term[0].set`, from which the
  kit derives the cover (`mf_set_terms`).
- **Bounded or not:** `end_back` (0/1).
- **Storage and stem:** `decl_point` (W4) and `pred.fn_ref` (W5).
- **Layer:** `policy`, the `MF_P_PORTABLE_ONLY` bit.
- **Window:** W0-W2 (`window_stated`, `move_back`, `overshoot`).
- **Spans:** `span_lo`/`span_hi`.
- **The walk's table:** `table_name` (rule 7).

**Missing:**
1. **`mf_site.body` (M):** `MF_BODY_ONESHOT` or `MF_BODY_ITER`, with 0 =
   UNSTATED.
   - R1/R2's condition is "one-shot". Without the fact the kit would be
     presuming it, so an unstated `body` makes R1/R2 skip.
   - Every builder states ONESHOT at R17-b′. `next` bodies state ITER at
     R17-b″.
   - Appended last; part of the MF_SITE_ABI bump.
2. **`mf_hooks.start` (a hook, at the storage point only):** the text of the
   activation's origin. That is `search_from` (DFA forward scan, VM
   `_search_run`) or the relocate path's moved start. Unstated, the dispatch
   rows skip. pcrec has the text at all three storage points
   (`fwd->from` in `unanch_scan`).
3. **Site kind:** `PF` / `PF-bounded` / `DFA-hat` / `VM-hat`.
   - Today every site states `consumer = MF_C_ENGINE`. The kit can tell
     bounded from unbounded (`end_back`), but not a DFA hat from a DFA
     prefilter, or either from the VM hat.
   - R5/R6's g\* is per site kind (M15), so this fact is needed when E
     arrives, not before (D77).
   - It is a categorical fact, not a price: D161 add. 6 dropped the consumer
     PRICE, and this is the "site kind" regime_tables §2 lists under P.
   - **Proposal:** an appended `mf_site.site_kind`, stated by `find_site`.
   - **The awkward part (Q-R17P-8):** R1/R2's thresholds come from PF
     member-free calls (M9) and apply to every kind until then.

### 4.2 E (the analysis object): missing entirely

- **No `mf_analysis` exists**, on the kit branch or on main. D162 ruled it on
  2026-10-12; it is not built.
- The frequency kind reaches the kit today only as `mf_pred.rank_*` on RUN
  sites (RQ-2). A set FIND site gets nothing.
- **What R17-b′'s E rows need (pcrec's to-do, D162 add. 2-3):**
  - the analysis object itself, with a provenance tag on each kind (prior vs
    measured);
  - the measured LANDING data per stop. For a single-class stop that is the
    unigram rate; for a multi-position stop it is the bigram kind
    (pcrec-analyze already counts bigrams). The kit derives g per candidate
    stop from it.
  - R5/R6 read only MEASURED provenance (D162 add. 3). The prior's
    p(1−p)-derived gap regrets more than "always walk" in SIMD-off
    DINGHY/TUG (gridread §6.2: 5.9% / 10.0%), so it is not evidence.
- **Totality when E is absent:** R5/R6 are skipped, which is R17-b′'s
  shipping state. When E arrives, R5/R6 become compile-time rows. A site with
  measured g < g\* picks WALK for all N, which collapses its dispatch away.

### 4.3 A (now: which measurement set): the channel

- **D166:** "The knowledge record's key A becomes 'which measurement set';
  ISA availability stays a separate fact". The ISA fact remains the
  compile-time guards plus `MF_P_PORTABLE_ONLY`.
- **pcrec loads the set; the kit must see it.** The facts-only shape
  (PROPOSED):

```c
typedef struct {
    const char *key;        /* the kit's or pcrec's key, e.g. "kit.beta.V1.ANY.r2e0c0";
                               pcrec never interprets a kit key */
    int64_t     value_e6;   /* the value x 10^6 (integers: no float in a selection) */
    uint8_t     unit;       /* MF_MU_RATIO, MF_MU_WALKBYTES, MF_MU_BYTES */
    const char *source;     /* "grid1 an.4.3" */
} mf_measure;

typedef struct {
    uint32_t          abi;        /* MF_MEASURES_ABI */
    const char       *name;       /* "zen4-grid2" */
    uint32_t          version;
    const char       *hash;       /* content hash, hex */
    const char       *box, *run, *method, *tier;
    uint8_t           composite;  /* 1: a derived envelope set */
    uint32_t          nrows;
    const mf_measure *rows;
} mf_measures;

mf_art *mf_art_begin(mf_arena *a, const char *prefix, uint32_t policy,
                     const mf_measures *ms /* NULL = no set */, ...);
```

- **Why per compile on `mf_art`, not per site.**
  - Every site of one compile reads the same set.
  - A per-site pointer, D162's precedent for `mf_site.analysis`, would let
    two sites disagree.
  - The kit's per-compile memo (D162 add. 4) builds its resolved row values
    once per art.
  - This is Q-R17P-5, because it departs from the analysis object's placement.
- **Facts only (D157).** pcrec states which set is active and hands over its
  rows unread. It computes no threshold. Every threshold is the kit's,
  resolved from the rows by the kit's own keys.
- **Totality (§3.4).** `ms == NULL`, an unknown key and a malformed row all
  make the rows that read them skip. The table's last row decides.

---

## 5. Emitted-byte consequences

### 5.1 Which artifacts move

Census (`r17b_prime/out/census_shapes.out`, compile-only, every distinct
corpus pattern at `--features all` on this tree):

| arm | compiled | R17-b movers | stateful sites per mover | R0 movers (≥ 2 RANGE) | top shapes |
|---|---|---|---|---|---|
| byte | 4,164 | 996 | 1 on all 996 | 219 | (1,0,0) 285, (3,0,1) 179, (0,1,0) 157, (0,2,0) 132 |
| byte-vm | 4,165 | 2,910 | 1 on all 2,910 | 243 | (0,1,0) 1,673, (1,0,0) 485, (3,0,1) 200 |

These counts show two things.
- **Every R17-b artifact has exactly ONE stateful FIND site.** That answers
  D165 add. 1's owed emission fact on the corpus's byte arms: no artifact
  needs two states at once.
- **R0's population is 22% of byte movers and 8% of VM movers.** It is mostly
  `\w` (3,0,1).

**SIMD-off default (no E), against main (which has only the walk).**
- **R0 sites (219 / 243).** They render the walk-only scaffold if M18 passes
  T3, or main's bare walk if it does not.
  - Under the scaffold the text moves and the code moves by −3..+14
    instructions.
  - Under the bare walk the site is byte-identical to main, except the abi
    digit and the new stamp.
- **The other R17-b movers (777 / 2,667):** WALK + V1 + dispatch if M16/M17
  pass, else V1 alone (R17-b's form behind `__next`). Either way they move.
- **utf8 arms:** R17-b's own census reads 964 / 2,907 movers on the same
  pattern. Their R0 split was not run here.

**Against R17-b, which never reached main:** every mover moves.
- R0 sites go back to the walk.
- The others gain the selector, the form byte and the table parameter (all
  of them), and the table and the dispatch if paid.

**SIMD-on against SIMD-off:** guarded insertions only (C18).
- Every non-R0 mover gains the V16/V32 sub-blocks, `__next_candidate__w32` /
  `__w16`, `__form__w*` and `__next__w*`.
- An R0 site gains them only if its SIMD-off text is the scaffold.

### 5.2 The abi event

- **One pcrec abi event** for R17-b′. It REPLACES R17-b's abi event, which
  never landed. R17-b's branch number (77) is renumbered at landing (main is
  at 78; main assigns the number).
- **The kit changes in the same commit (D147: a kit byte move is a pcrec abi
  event):**
  - `MF_SITE_ABI` 12 → 13 (`body`, `site_kind`, the `start` hook, and
    `mf_art_begin`'s `mf_measures`);
  - the finder table;
  - the four denies;
  - the W64 forms (V16/V32 sub-blocks).
- **Readers are found BY GREP (D76/D94).** The floor of the list is R17-b's
  own (setfind.md §11.2, `docs/dev/lanes/r17b_report.md`) and integration.md
  §18.3's classes:
  - **the digit's readers:** `PCREC_ARTIFACT_ABI`; match_api §1¶7's K80
    `#error` text; the spec's "abi is N" sentence; the
    `docs/dev/history/abi_changelog.md` entry; `run_codegen_tests.sh`'s
    `ABI_EXPECT`; `run_recursion_identity.sh`'s FILEPIN / `ABI_SUBJ`; the
    alpha scripts' normalizers;
  - **the byte-count readers, moved by the new every-artifact stamp:**
    `tests/codegen/manifests/m5_stage1_stamps.tsv`'s `EMITTED_BYTES` rows;
    `run_resource_tests.sh`'s `a{5,25000}` count; the size-term and K59/K53
    rung witnesses; the cpset manifest; emit_sweep's lowsize/lowboth
    `VARIANT_PINS`;
  - **the mover-by-ID manifests that read VM-hat or PF-site text:** the
    startset VM manifests, re-derived.
- **Then the suites that count are run** (registry, codegen, rxtsource), per
  D94's addendum.

### 5.3 Stamps

- **`<PREFIX>_MEMFN_FORMS`.** At SIMD-off it stays `"none"` on every artifact,
  as ruled (match_api.md §6.3.10¶4: none iff byte-identical to the SIMD-off
  compile). At SIMD-on, each PF site with a W64 arm adds one token in site
  order (`pf-terms@w32+w16`, the rendered levels, §6.3.10¶4's grammar
  unchanged).
  - The brief asks for forms-per-site IN this stamp. The ruled spec says "a
    scalar form never appears here". That conflict is Q-R17P-1. This note
    recommends keeping the ruled meaning and reporting per-site form sets
    (scalar included) and their bytes in `--emit-facts` and the size log.
- **`<PREFIX>_MEASURES` (new, every artifact, PROPOSED):**
  - `"none"` iff no selection in the artifact read a set value;
  - otherwise `"<name>@<version>:<hash8>"`, the active set.
  - Every artifact with a PF set site reads it, because R0's condition and the
    pay rule both read it.
  - It is written by the kit through `mf_stamps`, beside `MEMFN_FORMS`. It
    rides R17-b′'s abi event (Q-R17P-2).
  - Why a stamp at all: D166 makes an artifact a function of (pattern,
    options, analysis, measurements), so the fourth input must be readable
    off the artifact. The bench and [ART-MGR]'s cache key read it.
- **`<PREFIX>_MEMFN_LIBC`:** unchanged. No new libc call: the W64 forms use
  builtins.
- **`<PREFIX>_SIMD_GUARDED_BYTES`:** counts the new guarded text at SIMD-on
  (RQ-3, no cap reads it).
- **`RX_DFA_PREFILTER` / `RX_VM_START_SCAN` values:** unchanged, as at R17-b.

### 5.4 Artifact size (MEASURED on hand twins; SIZE ONLY)

`r17b_prime/out/twin_sizes.out` reports `gcc -O2 -c`, `.text` +
`.rodata`/`.data` in bytes. The twins use the use-branch shape (§2.3). They
are not answer-checked, and their thresholds are 36/64.

| cell | main (walk) | R17-b (V1) | WALK+V1 | WALK+A1 | WALK+V1+A1 |
|---|---|---|---|---|---|
| dig | 2,436 | 2,692 | 3,076 | 3,844 | 4,292 |
| bounded | 2,372 | 2,794 | 3,204 | 3,972 | 4,612 |
| dfa-hat | 4,196 | 4,708 | 5,028 | 5,860 | 6,564 |
| vm-hat | 1,358 | 1,966 | 2,382 | 3,758 | 4,718 |
| hex-run | 2,572 | 2,892 | 3,276 | 4,236 | 4,748 |
| vm-hat-1 | 1,423 | 1,871 | 2,287 | 3,535 | 4,367 |

**Per site, compared with R17-b and main:**
- **SIMD-off WALK+V1:** +320 to +416 B over R17-b. About 256 B of that is the
  restored table; the walk arm, the form function and the field are the rest.
  Against main it is +640 to +1,024 B.
- **SIMD-on three forms:** +1.9 to +3.4 KB over main, compiled `-mavx2`.
  These bytes are guarded, so they are excluded from the caps and counted by
  `SIMD_GUARDED_BYTES`.

**Source and corpus effects:**
- **Source:** WALK+V1 adds about 1.8 KB of source per site over R17-b, most of
  it the table's text.
- **Corpus:** every mover has one site, so these are per-artifact deltas.
  Against the corpus median object of 6,760 B (`artifact_size_census.md`),
  WALK+V1 is +10-15% at SIMD-off.

**Size caps:**
- `pf-terms-ndisp` is declared `MF_SZ_ADDS`, like `pf-terms-mask`. So the
  `drop-kit-bytes` rung (R17-b's tuning.md section, lane/memfn-r17 only) denies both on a cap refusal, and the
  site takes the walk.
- `pf-terms-w32` / `pf-terms-w16` are `MF_SZ_NEUTRAL` (guarded bytes never
  reach a cap).

### 5.5 Spec hunks (D80), found by grep at build

1. **`match_api.md`:**
   - §6.3: the new `<PREFIX>_MEASURES` row and paragraph, and the
     value-set table entry;
   - §6.3.10¶4: the PF site's SIMD token named among the rows that render one;
   - §1¶7: the V16/V32 sub-block guards (setfind.md §11.3's sentence, now
     reached);
   - the `RX_DFA_PREFILTER` method sentences (setfind.md §11.3, carried from
     R17-b).
2. **`tuning.md`:**
   - §2.42¶2 (the VM hat seek, carried);
   - §2.43¶3a (what On renders: the PF set forms);
   - R17-b's `drop-kit-bytes` tuning section, its first paragraph (the `size` rows: `pf-terms-ndisp`).
3. **`registry.md`:** §6¶8a (the SIMD rows) and §6¶8b, the `memfn` floor
   7 → 11.
4. **`limits.md` §8.3¶3:** the guarded-byte bound for the W64 rows.
5. **`table_contract.md`:** the `--list-finder` table. `cli.md` gains
   `--list-finder`, and `--measures=` arrives only with [MEASURE-SET] M1.
6. **The set format** becomes a spec document only when a caller can load a
   set (M1). Under M0 the listing is its only observable surface.

---

## 6. Deny rows and controls

### 6.1 The kit's denies (`memfn/src/options.def`; `--memfn=no-NAME`)

| name | kind | budget | layer | size | what it denies | the OFF arm it gives |
|---|---|---|---|---|---|---|
| `pf-terms-mask` (exists) | DENY | SCAN | SCALAR | ADDS | V1 everywhere | the walk at every set site = main |
| `pf-terms-ndisp` (new) | DENY | SCAN | SCALAR | ADDS | every emitted N-dispatch row (R1, R2) | each site's terminal pick alone (R17-b's single form, or WALK on R0) |
| `pf-terms-r0` (new) | DENY | SCAN | SCALAR | NEUTRAL | R0 | V1 on ≥ 2-range sites (R17-b's choice there), for R0's own alpha |
| `pf-terms-w32` (new) | DENY | SCAN | SIMD | NEUTRAL | the W64 form at w32 | the w16 arm or the floor body |
| `pf-terms-w16` (new) | DENY | SCAN | SIMD | NEUTRAL | the W64 form at w16 | the floor body |

The `memfn` section floor goes 7 → 11. Each new row is the OFF arm of the
change it names (D144 item 4).

### 6.2 G1: pcrec's timing against the deny, both layers

The population is a pcrec-side artifact diff (the R17-b census reader,
extended to the scaffold), never the kit's `moved`.

**SIMD-off:**
- default against `--memfn=no-pf-terms-ndisp`: the dispatch's own effect, on
  the dispatched sites;
- default against `--memfn=no-pf-terms-r0`: R0's, on the 219 / 243;
- default against `--memfn=no-pf-terms-mask`: the whole change against main.

**SIMD-on:**
- `-fmemfn-simd` against `-fmemfn-simd --memfn=no-pf-terms-w32`: A1's
  effect;
- `-fmemfn-simd` against `-fmemfn-simd --memfn=no-pf-terms-w32,no-pf-terms-w16`:
  the whole SIMD layer against the CURRENT scalar (D147).

Both layers are reported. The kit tier is the Linux dev box under D144 add. 1:
taskset-pinned, A/A, layout-perturbed pairs (the I-148 corrigendum's rule).

### 6.3 G2: the kit's tests against the byte loop, over a generated space

These extend `tests/run_g2_setfind.py` and the setfind §12.1/§12.2 families.
They are authored D27-blinded, as before.

1. **Thresholds and spans.**
   - Generated sets × synthetic thresholds N1 ∈ {0, 1, 7, 8, 35, 36, 63, 64,
     65, SIZE_MAX} × (n, start). These include `n − start` ∈ {N1−1, N1,
     N1+1} and `start > n`.
   - Every call's answer is checked against the byte loop.
   - The form byte the artifact chose is checked against an INDEPENDENT
     evaluation of the declared rows. The G2 script parses the set file and
     the table's listing itself; it never calls the kit's resolver.
2. **W64 candidate sequences.** setfind §12.2's generated `lo` sequences
   (backwards, repeats, jumps, past `n`, `n = 0`) at W = 64 for the
   `mask64_*` forms. Guard pages, ASan and UBSan, as §12.4.
3. **Form-independence of the cache.** A test-only build flips `f` between
   uses within one call. Answers must stay equal: each form's fill is the
   exact membership of [base, top) with top − base ≤ 64, so the invariant
   does not depend on which form wrote it (§8.2's proof, extended). This
   checks that the design does not rely on `f` being constant.

### 6.4 Answers are identical under every committed set (D166)

`make test-memfn-sets` (new, in TEST_SECTIONS):

- **The sample.** The R17-b mover population, 1 in 8 by pattern, plus every
  `.rxt` cell for those patterns. It is compiled once per committed set (the
  store) and once per synthetic extreme set:
  - **`all-walk`:** N1 = SIZE_MAX;
  - **`all-v1`:** N1 = 0, R0 off;
  - **`all-wide`:** N1 = N2 = 0.

  The extreme sets are TEST fixtures under `tests/memfn/sets/`, labelled
  synthetic, and never selectable as a default. They are reached through the
  harness-only binary (`build/pcrec-harness --harness=measures=FILE`, D163's
  lever lane) until M1's `--measures=` exists.
- **The answer arm.** Every compile is run against the harness's own
  oracle-verified expectations, and all must pass. The extreme sets force one
  form across the whole corpus sample, so this arm is also a per-form corpus
  differential. "Answers never depend on the set" is checked by exercising
  every form, not just asserted.
- **The structural arm.** Each artifact's `__form__*` literals must equal the
  set's values, as read by an independent parser of the set file.
  `<PREFIX>_MEASURES` must name the set loaded. A K35 floor is set on the
  number of dispatch sites reached per set.

### 6.5 Sabotage rows (ids are main's to allocate): 12

| # | plant | detected by |
|---|---|---|
| SB1 | a dispatch literal off by one | §6.4 structural arm; G2 1's form-choice check |
| SB2 | the comparison inverted (WALK for N ≥ N1) | the same |
| SB3 | the form byte not written per activation (always 0) | §6.4 structural census (dispatch sites reached) and the trace build |
| SB4 | the bounded walk arm ignores `end_back` | answers: G2 1 and corpus bounded cells; ASan over-read |
| SB5 | the walk arm passed the wrong table (DFA hat's `start_bytes` vs `can_begin_match`) | answers on dfa-hat cells |
| SB6 | the W64 tail path (`hi < 64`) reads past `hi` | G2 2 under ASan |
| SB7 | R0 counts EQ terms as RANGE | movers-by-ID against `census_shapes.py` |
| SB8 | an ABSENT set key read as 0 | the totality test: a set with the key removed must give R7 only |
| SB9 | the pay rule ignores C_disp | per-set expected-emission manifest |
| SB10 | `<PREFIX>_MEASURES` names the default set when another is loaded | §6.4 stamp check |
| SB11 | the SIMD-on use differs from the SIMD-off use | C18 (`make test-memfn-simdfloor`) |
| SB12 | the w32 `__next__` routes f == 1 to the W64 form | NOT answer-detectable (every form answers alike); trace and form census only, declared as such |

R17-b's own rows (S820-S843, S850-S854, S867-S870) whose anchors sit on the
use, the struct or the helper are re-aimed. The re-aims are derived by
`scripts/sabotage_anchors.py --step` at the build, not counted here.

---

## 7. Acceptance

### 7.1 What would accept R17-b′

All verdicts are Linux (D144 add. 1) and kit tier until the bench reads them
(D144 add. 4). They are taken on the build compiled against the first real set
(`zen4-grid2`, §3.3), at both layers. Zen 1 needs its own set (F5 through a
bench window), and selections for a Zen 1 target come from that set, never
from Zen 4's.

1. **R0 cells read NULL against `--memfn=no-pf-terms-mask`** (the walk). They
   also read no worse than `--memfn=no-pf-terms-r0` beyond the floor.
2. **Every dispatch interval holds.**
   - In the WALK interval (N < N1) the artifact is no slower than the V1 deny
     arm.
   - In the V1 interval it is no slower than the WALK arm.
   - At SIMD-on, `[N1, 64)` is no slower than W64, and ≥ 64 is no slower
     than V1.
3. **The dispatch charge is NULL** on LINER and TUG cells: default against
   `no-pf-terms-ndisp` on cells whose N never falls below N1.
4. **No cell is worse than R17-b** beyond the floor, at either layer.
5. **The named residual is reported, not gated** (Q-R17P-4): bounded dense
   find-all, dfa-hat on prose, dig on digits, vm-hat prose1m.

### 7.2 Predictions

**ALPHA cells, OFF layer.** The slot25c log has 80 rows: 32 WIN / 42 REG /
6 NULL. The deltas sum to −353,962 ns of wins and +1,241,235 ns of losses
(`lane/r17loss:docs/dev/lanes/r17loss/time.log`, the new−deny column).

- **R0 turns hex-run and word-eq.**
  - hex-run: 9 REG (+49,368 ns) and 1 WIN (−21,296 ns) go to NULL.
  - word-eq: 5 REG (+18,373 ns: its 2 reached mix64k rows and 3 unreached
    rows, whose deltas are codegen side effects of the changed function) and
    3 WIN (−21 ns) go to NULL. The site's text returns to the walk, so the
    unreached rows' side effects go with it.
  - That is −14 REG and −4 WIN. The OFF loss falls by 67,741 ns (5.5%).
- **R1 turns most of bounded short all** (+28.12 ns). Calls after the first
  few have N < 36 and walk. The prediction is about +3-4 ns left from the
  calls with N ≥ 36. dfa-hat short all (+1.71 ns) turns partly.
  - It does not turn bounded short `first` (+2.84 ns) or dfa-hat short
    `first` (+1.83 ns): N = 40 ≥ 36 (Q-R17P-8, F7).
- **Everything else stays as it is under R17-b.** That includes the named
  residual of 1.17 ms of OFF loss:
  - bounded 661,011 ns, of which prose1m all is 599,268;
  - dfa-hat 478,964 ns;
  - vm-hat prose1m all 33,470 ns.
- **The predicted OFF tally** is about 28 WIN / 28 REG / 24 NULL, net
  +840,849 ns against R17-b's +887,273 ns.
- **dfa-hat prose contradicts R6.** The grid says V1 wins dfa-hat at
  g > 3.0-3.3 B (M15), and ALPHA's dfa-hat prose has g = 10.2 B and LOSES:
  +1.33 ns/use at 64K, +3.06 ns/use at 1M (r17loss §3.1). R6 would therefore
  admit V1 there even with E. The missing fact is near-hit depth: the DFA
  consumes past the cached block, and only 11% of uses are served from the
  cache. It is in no grid (regime_tables §5). This refutes R6 for that cell.
  It is recorded so the residual is not attributed to E alone (F7).

**ALPHA cells, ON layer.** R17-b's ON layer timed the identical artifact.
R17-b′ ON renders W64 for N ≥ 64.
- The spike's reading says width alone turns 7 of the 30 losing ALPHA groups
  (`vecspike_reading.md`; A1 vs walk by regime: DINGHY 6/14/3, +658 µs; TUG
  16/0/2, −2.89 ms; LINER 17/0/0, −1.88 ms).
- So dfa-hat prose (TUG, one call) is predicted to turn at SIMD-on, and
  bounded dense find-all is not (c_cold W64 3.8-4.3 ns per call).

**Grid rows (gridread §4.3, §4.4), member-free single calls.**
- The L = 8 losses (V1 +2.3, S1 +2.9, A1 +3.2 ns) go to the walk, so regret
  is 0.
- At n = 48 and 63, SIMD-on picks V1 (−4.6 / −5.6 against the walk, the best
  member-free form there) where W64 lost (+1.3..+15.8), so regret is 0.
- Single calls with landings (g = 8 at L = 32, +3.6..+19.6; g = 2) keep losing.
  N cannot see landings.

**Regret per regime (gridread §6.2, find-all, the S0 {P, N, M} row).**
- SIMD-on: 11.1 / 1.2 / 0.0% (DINGHY / TUG / LINER).
- SIMD-off: 18.8 / 16.6 / 0.1%.

R1/R2 change no find-all grid row, because N is the remaining subject (§2.4).
R0 changes no grid row either, because the grid's cells are 1-term, cube+eq
and 1-range covers. So R17-b′'s predicted grid regret is S0's exactly. Moving
it needs E (S1: 6.6 / 0.1 / 0.0 on, 2.7 / 0.4 / 0.1 off, in sample) or H (S2/S3).

### 7.3 What refutes it

- **An R0 cell not NULL against the walk.** Either V1 pays at ≥ 2 RANGE terms
  on some cell, or the scaffold costs.
- **A WALK-interval call losing to V1, or a V1-interval call losing to the
  walk, beyond the floor.** M9's crossover is wrong for that kind or box.
  The vm-hat cells test the transfer from PF.
- **A non-NULL dispatch charge on a cell the dispatch does not help.** The
  pay rule's measurement or bar is wrong.
- **Any cell worse than R17-b.**
- **At SIMD-on, a W64 interval losing to V1.** That would be D147's check
  failing for this site kind.
- **On Zen 1 (F5), the crossovers move.** A1's β approaches S1's on 2×128 AVX2.
  That refutes nothing on Zen 4. It is why Zen 1 gets its own set and never
  reads Zen 4's (D161 add. 12).

---

## 8. R17-b″'s seam: what the D165 iterator adds, and why the table stays

The iterator adds:
- an entry body of kind `MF_BODY_ITER` (`next`);
- H (the previous step's span and the block's popcount), held in the
  iterator's state buffer;
- one form, A3: W64 with its cache kept across calls, its storage the
  `rx_iter` buffer instead of the automatic struct.

None of these needs a rebuilt table:
- **Rows.** R3a, R3b and R4 are rows with `needs ∋ KN_H`. They are already
  listed and already skipped (H is unavailable in a one-shot body). In a `next`
  body H is available, so the same evaluation emits them, either as dispatch
  rows read at `next`'s entry or, for R4, at the block's refill.
- **Storage.** The site struct (24 B cache + the form byte; `s` and `n` live
  in `rx_iter`'s own fields) plus the previous span (8 B) is the 32 B the kit
  declared (D161 add. 11 item 3.4). `__next` and its per-form bodies are
  unchanged. A3 is `__next_candidate__w32` over storage that persists.
- **Dispatch.** The dispatch keeps its shape. The form byte is computed at
  `next`'s entry instead of `_search`'s storage point, from N and H.
- **Acceptance.** It carries F4 (the iterator reproduces A3's hand-edit win),
  F7 (H's observation cost against its regret) and D165's parity gate (dense
  tiny matches at parity or better).

---

## 9. Open questions (for Frank and main), each with a recommendation

**Q-R17P-1. `MEMFN_FORMS` and forms-per-site.** The brief puts forms-per-site
in `<PREFIX>_MEMFN_FORMS`. The spec rules that stamp SIMD-only ("a scalar form
never appears here", match_api.md §6.3.10¶3-4, D147 add. 10 / Q55), and its
readers bucket on `none`.
- **Recommendation:** keep the ruled meaning. At SIMD-on the PF site's token
  appears in the stamp. Per-site form sets (scalar included) and their bytes
  go to `--emit-facts` and the size log, not to the artifact (D77: no consumer
  of a per-site scalar form set in the artifact has been named).
- If Frank wants scalar form sets in the artifact, the alternative is an
  explicit amendment of Q55's grammar with its reader list. The
  recommendation is against it.

**Q-R17P-2. The `<PREFIX>_MEASURES` stamp.** The proposal is an every-artifact
stamp: `"none"` iff no selection read the set, else `name@version:hash8`.
- **Recommendation:** yes, in R17-b′'s abi event.
- The alternative, naming the default set on every artifact even where unread,
  moves every artifact on a set change that changes no decision. That is the
  kit-version objection of integration.md §18.1.

**Q-R17P-3. The pay rule.** The proposal is a no-measurable-overhead rule
(§2.5 T1-T3) rather than an expected-gain rule over a call-length
distribution.
- **Recommendation:** the no-overhead rule. It presumes no distribution, and
  the kit has none.
- The cost: a dispatch whose standing charge is real but small never ships,
  even where short calls dominate. E's call-pattern facts, or the bench's
  population, would be the trigger to revisit.

**Q-R17P-4. The acceptance gate.** D162 add. 1 gates R17-b on "a real cell
losing beyond the regression floor returns to the kit". Under that gate
R17-b′ cannot merge SIMD-off. Its predicted residual (dense find-all, dfa-hat
prose) loses by construction, because N is the remaining subject.
- **Recommendation:** replace the no-loss gate, for this delivery, with
  §7.1's five conditions. The named residual is reported with absolute ns
  per regime.
- Merge SIMD-off only if the BENCH population, not ALPHA (which
  over-represents dense 1 MiB find-all), nets at or below the walk per
  regime. Otherwise ship the SIMD-on layer and hold the SIMD-off default at
  the walk (R0 for every shape) until E or R17-b″.

**Q-R17P-5. The set's channel.** The proposal is one read-only `mf_measures`
handed to `mf_art_begin` (per compile). D162 put the analysis object on each
site (`mf_site.analysis`).
- **Recommendation:** per compile, on `mf_art`, as proposed. pcrec parses the
  container; the kit's keys are opaque to pcrec, like `--memfn=` options.
- The analysis object should move the same way when it is built. Ask main.

**Q-R17P-6. [MEASURE-SET] phasing and [IFACE-PUSH].**
- **Recommendation:** M0 rides R17-b′: the store, the embedded default, the
  channel, the read-only `--list-finder` listing and the stamp. M1 is
  [MEASURE-SET]'s own build: `--measures=FILE|NAME`, the config line, the
  install-time tool and the envelope.
- M1's CLI surface is D166-ruled. It should proceed as its own surface event
  (the `--analysis=` precedent) instead of waiting for [IFACE-PUSH]'s batch.
  Frank's call: memory `pcrec-iface-push-later` puts CLI options and stamps
  in one push.

**Q-R17P-7. The first set needs a run.** D166's one-run rule means grid1
cannot gain M16-M18 from a second run. Embedded as it stands, grid1 ships
R0 + R7 and no dispatch.
- **Recommendation:** measure `zen4-grid2` as one slot. Re-run grid1's cells
  plus the dispatch arms (§3.3), then build R17-b′ against it.
- grid1 stays a provisional design set and is never embedded.
- This is one heavy slot, by main's grant.

**Q-R17P-8. Site kind, and R1/R2's transfer.** R1/R2's crossover (M9) is
measured on PF member-free calls. The kit cannot tell site kinds apart today.
- **Recommendation:** add `mf_site.site_kind` with E (D77: R5/R6 are its
  first reader).
- Until then, R1/R2 apply to every kind, with the provenance shown in the
  listing ("measured on PF only"). ALPHA's vm-hat and dfa-hat cells are in
  the acceptance set and will refute the transfer if it is wrong.
- The alternative restricts R1/R2 to `end_back == 0` sites, which still
  cannot separate the DFA prefilter from the VM hat. Frank's call: whether a
  measured-elsewhere crossover may be read, labelled, at all (the D161 add. 12
  analogy says yes, through a generic class).

---

## 10. Standing design questions (docs/design/CLAUDE.md)

1. **Measurement regime: RELEVANT.**
   - Every value R17-b′ reads is Zen 4 (7700X), gcc 15.2 -O2, CPU-pinned,
     from one slot.
   - The sources are member-free single calls (M7-M12) and find-all passes
     over synthetic 64 KiB subjects, repeated or streamed (M13-M15).
   - Regimes that would flip a decision:
     - Zen 1 (2×128 AVX2) moves every W64 row (F5);
     - fresh irregular landings move g\* down 2-4× (gridread §5.3);
     - single calls with landings move R1's crossover past 32 B (§4.3);
     - near-hit text (ALPHA's dfa-hat prose) flips V1 against the grid (F7).
   - The dispatch charge (M16-M18) is unmeasured in any regime. It must be
     measured in the same slot as the rest (§3.3).
2. **Independent control: RELEVANT.**
   - **G1** times pcrec's artifacts against the kit's own denies, with a
     population read off pcrec's emitted C. It never reads the kit's `moved`.
   - **G2** checks answers against the byte loop over a GENERATED space. Its
     form-choice check evaluates the declared rows from the set FILE with its
     own parser, never the kit's resolver.
   - **`test-memfn-sets`** runs the harness's oracle-verified expectations.
     Those expectations come from libpcre2 and python `re`, not from the kit.
     Its extreme sets force each form, so a wrong form cannot hide behind the
     dispatch.
   - **The R0 population** is counted by `census_shapes.py` reading emitted
     masks (K35), checked against the kit's census by ID.
   - **Witness reach ([MECH-REACH]).** SB12 is declared answer-undetectable. Its
     detector is the trace and form census, so each sabotage row names a
     witness that reaches its site.
3. **What moves when the data is regenerated: RELEVANT.**
   - A new set changes the `__form__*` literals on every dispatched site. It
     can flip R0 or the pay rule on whole shapes, so sites may gain or lose a
     dispatch or the scaffold.
   - It also changes `<PREFIX>_MEASURES` on every artifact that reads it.
   - So changing the default set is a pcrec abi event (D162, D166 item 1).
     The commit carries a mover census (by ID, from a pcrec-side diff) and
     re-pins the byte-count readers (§5.2).
   - It is caller-observable through the listing and the stamp, so it needs a
     spec hunk (D80), but only where a value-set or a listing row changes.
   - A set added without becoming the default moves nothing.

---

## 11. Findings

- **F1. One stateful site per artifact, corpus-wide.** All 996 byte and all
  2,910 byte-vm R17-b movers have exactly one `__next_candidate` site. This
  answers D165 add. 1's owed emission fact on these arms: D165's sum rule has
  no corpus case today.
- **F2. The scaffold is not free in code.** The walk reached through a helper
  and the struct compiles to a different holding function (−3..+14
  instructions, 0 of 6 cells identical). So C_scaffold is a measured quantity
  (M18), not an assumption.
- **F3. The brief's "forms-per-site in `MEMFN_FORMS`" conflicts with the ruled
  spec** (§5.3, Q-R17P-1).
- **F4. M is fixed per entry body.** It is compile-time and is never an
  emitted compare (§2.4).
- **F5. Under the floor rule and D155, a SIMD W64 arm can be added to a site
  only if its SIMD-off text already routes through the `__next` selector.**
  So R0 sites at SIMD-off carry a walk-only scaffold, or get no W64 arm at
  either layer. The pay rule (T3 against M18) decides which.
- **F6. R0 keyed by exact measured shape would miss `\w`** (179 of 219 byte
  R0 sites). Keyed by range-term count, with the derived monotonicity of V1's
  β in its terms, it covers all 219 (§3.4).
- **F7. ALPHA's residual is not all E's.** dfa-hat on prose loses with its
  state carried, at g = 10.2 B above every measured g\*. R6 would admit V1
  there. The missing knowledge is near-hit depth (regime_tables §5).
- **F8. D166's one-run rule makes the dispatch impossible on grid1 data.** The
  first embedded set needs a new run (§3.3, Q-R17P-7).
- **F9. Two R17-b statements stay true only at SIMD-off.** setfind.md
  §11.2's "`MEMFN_FORMS` stays `none`" holds only there, and the SIMD-off
  "no SIMD text" claim of §3.4b holds as well. At SIMD-on the W64 arms make
  `MEMFN_FORMS` non-`none` on PF sites, as setfind §11.4 anticipated.

---

## 12. Charter vs committed

| brief item | where | status |
|---|---|---|
| Read the kit's view, D161 add. 11-12, D162 (+ add.), D165 (+ add. 1), D166, D157, D147, D76/D94, D80, [MEASURE-SET], regime_tables rev 0.2, gridread, costmodel, vecspike_reading, setfind §8/§9/§12, pffind.c/terms.c, row_contracts, R-17, journal, integration §14/§18 | cited throughout | done |
| D166: every threshold as a set reference keyed (quantity, form, site kind), as ratio or crossover | §1.1 `fd_ref`, §2.6, §3.1 | done |
| The measurement table (quantity, key, relative value, absolute provenance, source) | §3.2 (18 families, ~45 values) | done |
| How rows read the set; an absent quantity (D162 totality) | §3.4 | done |
| 1. The table: C shape, needs, condition, pick (stop, form); the stop; the listing with set provenance | §1.1-§1.4 | done |
| 2. The C text of the N dispatch for WALK+V1, WALK+A1, WALK+V1+A1; placement; N; the compare's cost; the drop rule; literals from the set, an abi/mover event | §2.1-§2.6 | done (the cost is unmeasured and stated so) |
| State plainly that R17-b′ does not fix ALPHA's dense 1 MiB find-all | §0 item 2, §2.4, §7.2 | done |
| 3. P/E/A fields today and missing; E per stop incl. bigram; the set's channel (facts-only); totality | §4.1-§4.3 | done |
| 4. Which artifacts move vs R17-b and vs main; the abi event; stamps (`_MEMFN_FORMS`, set name); spec hunks; size estimate | §5.1-§5.5 | done (MEMFN_FORMS conflict raised as Q-R17P-1) |
| 5. Denies per new form/dispatch; G1; G2; the every-committed-set answer test; sabotage count | §6.1-§6.5 (12 rows) | done |
| 6. Acceptance: ALPHA cells and grid rows turned; predicted regret by regime; refutation; both layers; Linux; Zen 1 via F5 | §7.1-§7.3 | done |
| 7. R17-b″'s seam | §8 | done |
| 8. Open questions Q-R17P-n with recommendations; standing questions answered | §9 (8), §10 | done |
| Deliverable: this note + its CLAUDE.md line, committed | `docs/design/memfn/r17b_prime.md`, `docs/design/memfn/CLAUDE.md` | done |
| Do not put measured constants into any source file | nothing under src/, memfn/src/, tests/, lib/ changed | done |
| Instruments (beyond the brief, compile-only) | `r17b_prime/` (census, size twins, asm check) | done |
