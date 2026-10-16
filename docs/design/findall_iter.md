# [FINDALL-NEXT] — the find-all iterator `rx_iter` / `<prefix>_next` (DESIGN NOTE, revision 2)

**Revision 2** (lane `iterrev`, 2026-10-16, from main `64e77cf9a`, abi 78) is the SHORT
revision that D163 addendum 7 Q4 orders after E0 and before this note's D6 panel. It restates
the iterator as COMPOUND CONTROLLERS (`compound_entries.md` revision 3, branch
`lane/cmprev2`, not yet on main when this was written) and applies D165 addendum 2 (Frank's
rulings on revision 1's Q1-Q4) and D167 addendum 1 A10 (S is derived from declared carried
words). Read §R2 first. Revision 1: lane `iterdes`, 2026-10-14, from main `ee01f4dbb`
(abi 78). DESIGN ONLY: nothing under `src/`, `cli/`, `lib/` or `tests/` changes. The probes
behind every measured sentence are in `findall_iter/` (own CLAUDE.md). Revision 2 measured
nothing new and read no clock. Where its design moves a revision-1 number (the init store
count, `sizeof(rx_iter)`), the number is marked PREDICTED and its re-measurement is owed by
the twin (§5.3).

Ruled inputs this note designs TO, not re-opens: D165 items 1-6 and addenda 1-2, D163
addenda 6-7, D167 addendum 1 (A10), D41 item 5 (the history), D161 addenda 11-13, D166 (the
seam only), R-19 (`mf_site.body`, the start hook). Frank's charter (2026-10-14): "we need a
framework to build into ... set this up with its iters and such so we have the playground
before we start playing with further optimizations." So the first build is the FRAMEWORK: the
struct, the entries, the semantics, the storage rows and their checks. Every state-carrying
optimization is a later row with its own trigger (§9).

---

## R2. What revision 2 changed (ruling → section)

| input | what it says | what changed here | where |
|---|---|---|---|
| D163 add. 7 (model) | every exported entry is a compound controller over parts; `next` is an `iterate` combinator; the retry is `first-nonzero` | `next` is an `iterate` row of `entry_rows[]`. Its STEP is a GUARDED `first-nonzero(R@q, SEARCH@LOWER(adv(q)))`, which is split's controller shape exactly, guard included (split: "floor can be live"; here: the retry bit). Revision 1's `__step` retry arm is no longer iterator-specific machinery | §2.1, §3.3 |
| D163 add. 7 Q4 + `compound_entries.md` r3 I4, §3.8 | the find body's layout comes from the part-layout row | revision 1's §2.2 two-row rule is KEPT as the `0` cell's content. At a non-zero position `__find` is a SUBJECT part, laid out by `compound_entries.md` §3.4's tables (P2 for the attempt route's label-table body, with `noclone` added). The batch fill gives `__find` a designed R3 in-edge, which `compound_entries.md` §3.8 listed as HELD | §2.2 |
| D165 add. 2 Q2 (reframed) | INTERNAL batching: the controller finds several matches per pass, holds them, hands one out per `next`; results in the caller's `_in` memory; a public `next_n` is optional | designed (§2.3): the `iterate` combinator owns a FILL loop over STEP writing into a BATCH region of the bound `<prefix>_buffers`; delivery copies one entry per call. No `_in` memory = no batching (K = 1, written straight to `caps`). The answers and give-ups equal the unbatched iterator's, by construction (§3.4a). `next_n` stays an optional extra, timed beside it | §2.3, §3.4a, §5.3 |
| D165 add. 2 Q3 | bind `(s, n)` at init; `next(&it, caps)` takes no subject | `RX_ITER_INIT(s, n)`; the per-call binding compare is gone. The optional start position, variables and buffers are SETTERS on a FRESH iterator: one mechanism, not one init macro per combination | §1.1, §1.2 |
| D165 add. 2 Q4 + error reporting | `PCREC_ERR_ITER` (-10); `next` returns 1/0 and `it.rc` says why; sticky | unchanged from revision 1, now RULED. Batching adds `rc_next`: a code met by a fill is delivered only after the matches found before it | §2.1, §3.4 |
| D163 add. 7 Q5 + `compound_entries.md` F-1 | no exported entry calls an exported sibling; static twins, applied where a change already moves the bytes | every RESIDUAL leaf (`_next_pos`, `_valid_upto`, `_var_valid`) gets a static twin in I1; every internal caller, the compound controller included, calls the twin; the exported residual forwards to it | §2.4 |
| D167 add. 1 A10 | do not retire K5's 16 B pair-hit row on the merge alone; S from declared carried positions, 8 B each, re-derived at the iterator's abi event; "S = 48 B" withdrawn | §1.3 is a DERIVATION: S = max over paths of Σ 8 × declared words. Today's declarations give **64 B** (kit FIND row 40 + K5 16 + reseed hint 8). K5 retires only on a proof that a kit form is single-pass over its spans | §1.3 |
| D163 add. 6 Q1 (one meter per exported call) | a compound's parts charge the caller's meter | READ as one meter per LOGICAL search: the retry and the following search are two logical searches (pcre2demo makes two `pcre2_match` calls), and a fill is up to K. Inside one logical search, Q1 holds as ruled. Put to Frank as Q-I1 | §3.4, §10 |
| brief lenses | general mechanism; sibling of a family; NEW-DATASET | §8 updated; NEW §8a names each new table, column or record and its home | §8, §8a |
| revision 1 §10 | Q1-Q4 | RULED (D165 add. 2); §10 records them and carries this revision's Q-I1..Q-I4 | §10 |

Sabotage ids in §6.8 are PROPOSALS. Revision 1's S923-S942 are kept as labels; the new rows
are labelled P-a..P-h. The manager allocates.

---

## 0. Answers first

1. **The struct** (§1). `rx_iter` is one fixed, unprefixed type in the shared ABI block.
   - Its first eight bytes are a STABLE PREFIX: a header word (tag, layout version, state
     FRESH / BOUND / ENDED, and option bits) and `rc`.
   - `rx_iter it = RX_ITER_INIT(s, n);` binds the subject (D165 add. 2 Q3). PREDICTED: three
     stores (`hdr`, `s`, `n`), never a memset. Revision 1 measured one store for its
     one-field init; the three-store figure is owed by the twin's `init_spellings` probe.
   - Optional inputs are setters on a FRESH iterator: `rx_iter_at(&it, pos)`,
     `rx_iter_vars(&it, vars, nvars)`, and `<prefix>_iter_buffers(&it, &bufs)` (typed, a
     header `static inline`, Q-I2).
   - **S is derived** (§1.3): the maximum over every search path of 8 B × the DECLARED
     carried words of the rows held there at once (D167 add. 1 A10). Today: kit FIND row
     40 + K5 pair hits 16 + reseed hint 8 = **64 B**, align 8.
2. **The entries are controllers** (§2). `int <prefix>_next(rx_iter *, caps)` is an `iterate`
   row of `entry_rows[]` over a STATE part (`__enter`: bind or check), a STEP and a BATCH.
   - STEP = `first-nonzero(R@q, SEARCH@LOWER(adv(q)))` guarded by the retry bit, else
     `SEARCH@lo`. This is split's controller (`compound.md` §B.2) with a different guard, so
     both use one combinator emitter.
   - SEARCH is `__find(ITER)`. Its layout at `0` is revision 1's §2.2 table (inline, except
     the 233 label-table bodies, which stay one shared static function). At other positions
     the part-layout row decides (§2.2).
   - One exported call per match at most; with batching, one per K matches.
3. **Internal batching** (§2.3). With `_in` memory bound, a call that finds the batch empty
   FILLS it: STEP runs until the batch region holds `nbatch` matches or the iterator ends.
   Each later call copies one entry out. A code met during the fill waits in `rc_next` until
   the matches before it are delivered. Without `_in` memory, K = 1 and STEP writes straight
   into `caps`. Answers and give-ups are those of the unbatched iterator (§3.4a).
4. **Semantics** (§3), unchanged from revision 1 and RULED (D165 add. 2 Q1): PCRE2's global
   iteration, the NOTEMPTY_ATSTART retry gated by `reports_empty` (nullable OR `\K`). 1,063
   of 29,502 corpus pairs differ from today's §3.1.3 loop, and on 374 of those the loop
   reports a span no oracle reports.
5. **The error contract** (§2.1, §3.4). `next` returns 1 for a match, 0 otherwise. `it.rc`
   says why it stopped: 0 = done, a give-up code (D158) or a refusal (`PCREC_ERR_ITER`,
   `_UTF`, `_STARTPOS`, `_UNSET_VAR`) = it ended there. The ended state is sticky and costs
   nothing on later calls (the header word moves to ENDED, so the one fused header/owner
   compare routes every later call to the slow path).
6. **F-1's static twins** (§2.4). `__adv`, `__valid_upto` and `__var_valid` are the static
   bodies; the exported residuals forward to them; no internal call reaches an exported
   symbol, so nothing pays a PLT call under `-fPIC`. Folded into I1 (97 corpus compound
   artifacts move anyway).
7. **The kit seam** (§4), unchanged in shape: each storage row is a region of `st`, zero at
   bind, persistent across calls; M is `__find`'s mode parameter (R-20 requested).
8. **The abi event** (§6). One pcrec abi event, I1, after E0 and the zero-mover I0. It
   carries the shared block, `_next`, the residual twins, the retry machinery, and the
   `<prefix>_buffers` batch region IF the parity slot's batch arm wins (§5.3); otherwise the
   batch region is filed with that trigger.
9. **Questions for Frank** (§10): Q-I1 the meter's unit under batching and the retry; Q-I2
   the typed buffers binder; Q-I3 the batch region's home (extend `<prefix>_buffers`); Q-I4
   the batch entry's stride (full captures per match).

---

## 1. The `rx_iter` layout

### 1.1 The struct (in the shared ABI block, beside `rx_ctx`)

```c
#define PCREC_ERR_ITER (-10)  /* [FINDALL-NEXT] below PCREC_ERR_FLOOR: NOT a give-up -- the iterator was refused */

#define PCREC_ITER_STATE_SIZE  64   /* S: derived, §1.3 */
#define PCREC_ITER_STATE_ALIGN 8
#define PCREC_ITER_LAYOUT      2u   /* bumps with any change to rx_iter's layout or to S */
#define PCREC_ITER_TAG       (0x49540000u | (PCREC_ITER_LAYOUT << 8))
#define PCREC_ITER_FRESH     (PCREC_ITER_TAG | 0x01u)
#define PCREC_ITER_BOUND     (PCREC_ITER_TAG | 0x02u)
#define PCREC_ITER_ENDED     (PCREC_ITER_TAG | 0x03u)
#define PCREC_ITER_OPT_AT    0x10u  /* option bits, set by the setters on a FRESH iterator */
#define PCREC_ITER_OPT_VARS  0x20u
#define PCREC_ITER_OPT_IN    0x40u
#define PCREC_ITER_STATE_MASK 0x0Fu

typedef struct rx_iter {
    uint32_t hdr;      /* STABLE PREFIX: tag | layout | state | option bits */
    int32_t  rc;       /* STABLE PREFIX: 1 live, 0 done, < 0 the code that ended it */
    uint32_t flags;    /* RX_ITER_F_RETRY, RX_ITER_F_CHECKED */
    int32_t  rc_next;  /* the code a batch fill met, delivered after the batch drains (§2.3) */
    const unsigned char *s;   /* bound at init */
    size_t   n;
    size_t   lo;       /* the next search position; never decreases */
    const void *owner;        /* &<prefix>_info of the artifact that bound it, at the first call */
    const rx_var *vars;       /* rx_iter_vars; read only if OPT_VARS */
    size_t   nvars;
    const void *bufs;         /* the binding artifact's <prefix>_buffers; read only if OPT_IN */
    size_t   bhead, bcount;   /* the batch cursor: entries [bhead, bcount) are undelivered */
    union { unsigned char b[PCREC_ITER_STATE_SIZE]; uint64_t align_; } st;   /* the storage rows */
} rx_iter;

static inline rx_iter rx_iter_init(const unsigned char *s, size_t n)
{ rx_iter it; it.hdr = PCREC_ITER_FRESH; it.s = s; it.n = n; return it; }
#define RX_ITER_INIT(s_, n_) rx_iter_init((s_), (n_))

/* Setters: legal only on a FRESH iterator. On any other state they poison the header,
   so the next call refuses with PCREC_ERR_ITER rather than rebinding silently. */
static inline void rx_iter_at(rx_iter *it, size_t pos)
{ if ((it->hdr & ~0xF0u) == PCREC_ITER_FRESH) { it->lo = pos; it->hdr |= PCREC_ITER_OPT_AT; }
  else it->hdr = 0; }
static inline void rx_iter_vars(rx_iter *it, const rx_var *v, size_t nv)
{ if ((it->hdr & ~0xF0u) == PCREC_ITER_FRESH) { it->vars = v; it->nvars = nv; it->hdr |= PCREC_ITER_OPT_VARS; }
  else it->hdr = 0; }
```

and, in each artifact's HEADER (not the shared block, because its argument type is the
artifact's own, match_api.md §10.2¶2):

```c
static inline void <prefix>_iter_buffers(rx_iter *it, const <prefix>_buffers *b)
{ if ((it->hdr & ~0xF0u) == PCREC_ITER_FRESH) { it->bufs = b; it->hdr |= PCREC_ITER_OPT_IN; }
  else it->hdr = 0; }
```

On LP64, sizeof = 96 + S = 160 B (PREDICTED; revision 1's was 120 B at S = 56). The fields,
and what revision 2 changed:

| field | storage class | why |
|---|---|---|
| `hdr` | FIXED, stable prefix | the validity word. Its state values tell a fresh iterator from a bound, an ended, or a foreign one. ENDED makes stickiness free: the BOUND fast path is one fused compare (below), and an ended iterator fails it. The option bits record which setters ran, so init writes no optional field (**rev 2**: replaces revision 1's FRESH_AT state and its `RX_ITER_INIT_AT`/`_VARS` macro family) |
| `rc` | FIXED, stable prefix | unchanged: done (0) and gave-up/refused (< 0) stay distinct after `next` has returned 0, at a fixed offset any layout can read |
| `flags` | FIXED | `RETRY` (the empty-match retry bit) and `CHECKED` (the once-per-iterator checks ran) |
| `rc_next` | FIXED | **rev 2**: the pending code under batching (§2.3). It reuses revision 1's `reserved_` word, so it costs no bytes |
| `s`, `n` | FIXED | **rev 2**: bound at INIT (D165 add. 2 Q3). A subject mismatch is impossible by construction |
| `lo` | FIXED | the search position, monotone (D165 item 1) |
| `owner` | FIXED | written at the first call; checked on every later one (§1.2) |
| `vars`, `nvars` | FIXED | unchanged in role; now set by `rx_iter_vars` |
| `bufs`, `bhead`, `bcount` | FIXED | **rev 2**: the `_in` binding and the batch cursor (§2.3). FIXED, not storage rows: every artifact can batch, as every artifact can need the retry bit |
| `st` | BUFFER | every storage row (§1.3) |

**Why setters and not an init macro per combination.** Revision 1 already had `RX_ITER_INIT`
and `_AT`, and needed `_VARS` and `_AT_VARS`; D165 add. 2 adds `_IN`. That is 2³ spellings
for three independent options, and each new option would double it again. The setters are
one rule (an option is a setter on a FRESH iterator, recorded by a header bit) that a fourth
option joins without touching the others. A setter is `static inline`, so it is no exported
symbol and no call. Init still writes no optional field, so D165 item 5's "never a memset"
holds.

### 1.2 Binding (D165 add. 2 Q3: bind at init)

- **INIT.** `RX_ITER_INIT(s, n)` writes `hdr = FRESH`, `s`, `n`. The setters add `lo`,
  `vars`, `bufs` and their option bits.
- **FRESH → BOUND, at the first call.** `next` records `owner = &<prefix>_info`, sets
  `rc = 1`, `rc_next = 1`, `flags = 0`, `bhead = bcount = 0`, and `lo = 0` unless `OPT_AT`
  set it. It zeroes the storage rows THIS artifact declares (never S). It runs the
  once-per-iterator checks (§3.5-§3.7: the startpos guard on an `OPT_AT` start, the
  `-futf-check` validation, the variables' validation), then stores `BOUND`.
- **BOUND, the fast path.** One fused compare:
  `((it->hdr ^ PCREC_ITER_BOUND) | ((uintptr_t)it->owner ^ (uintptr_t)&<prefix>_info)) != 0`.
  Revision 1's per-call `(s, n)` compare is gone (Q3). The owner compare stays: an iterator
  bound by artifact A and handed to artifact B's `next` would give B A's carried rows, a
  WRONG ANSWER through the kit's cache, not merely a cost.
- **Anything else** (ENDED, garbage, an uninitialized struct, a poisoned header, another
  layout) takes the slow path: ENDED returns 0 with no work; everything else sets
  `rc = PCREC_ERR_ITER` at the stable offset, moves the header to ENDED, and returns 0.

**Copying** an iterator is legal at any point, as in revision 1: every field is
position-independent and the kit says its state is too (D165 add. 1). A copy made while the
batch holds undelivered entries SHARES the batch region with the original, so the two copies
must not both continue (they would overwrite each other's batch). The spec hunk states this
as the `_in` lifetime rule's corollary: one live iterator per batch region.

### 1.3 S is DERIVED: the declared carried words (D167 add. 1 A10)

S is a public constant in the shared block, so changing it changes every artifact (an abi
event, D165 item 4). It is derived from the owners' declarations, never picked.

**The rule.** Every storage user declares a ROW: the words it carries across calls, at 8 B
each (a position, a mask, a span: D165 item 6 as A10 reads it), its alignment, and the paths
on which it is held. Then

  S = max over every search path π of Σ { 8 × words(r) : r held on π at once },

rounded up to `PCREC_ITER_STATE_ALIGN`. "Held at once" means held ACROSS CALLS by one
iterator, not live inside one call. The composition rules are revision 1's:
- distinct sites on mutually exclusive ROUTES of one artifact are a union (one artifact takes
  one route for every call);
- the rev-end route's relocate path and the forward scan's FIND site are one site
  (r17b_prime.md §2.1), so one region;
- a compound's parts SUM (D165 item 4).

**The declared rows today** (the home of these declarations is §8a):

| row | owner | words → bytes | class | held when | declared by | status |
|---|---|---|---|---|---|---|
| `retry` | pcrec | a bit of `flags` | FIXED | a `reports_empty` artifact | §3.3 | I1 |
| `checked` | pcrec | a bit of `flags` | FIXED | every artifact | §1.2 | I1 |
| `kit-find` | kit | 5 → 40 B, align 8: `base`, `top`, the u64 mask, H's previous step span, `valid_until` | BUFFER | a site whose kit form keeps state (A3 and its SIMD siblings) | r17b_prime.md §6 (rev 2, on `lane/memfn-r17` `c90d65e53`): 24 B (D165 add. 1) + H 8 B + the presence carry 8 B | I2 (R17-b″) |
| `pair-hits` | pcrec | 2 → 16 B: `ha`, `hb` | BUFFER | the two-stream run pre-check (K5) | walk_survey.md K5 | I3; KEPT by A10 |
| `reseed-hint` | pcrec | 1 → 8 B: two `uint32_t` | BUFFER | adaptive VM hybrids | xcall.md §5 | FILED (U5) |

**Today's value: S = 40 + 16 + 8 = 64 B, align 8.** The worst path is revision 1's: one FIND
site (PF, MLINE, OFS or the VM hat; r17b_prime.md F1 counted one `__next_candidate` site on
all 3,906 R17-b movers), plus the run pre-check, plus, on an adaptive hybrid, the reseed
hint. A compound's worst sum is smaller: split's F holds no row, its Q at most
`kit-find + pair-hits` = 56 B.

How the value moved from revision 1's 56 B: the kit's row grew 32 → 40 B (the presence carry
`valid_until`, r17b_prime.md §6), and K5's 16 B stays (A10). Q-R17P-10's "48 B" assumed K5
retired on the merge; A10 withdrew that.

**K5's retirement is a proof, not a merge.** A10: one `valid_until` does not keep find-all
linear where there are two or more REQUIRED spans or a two-stream form, because a far span is
rescanned on each expiry (67 corpus patterns on P0's no-DFA routes with 2+ required spans).
So `pair-hits` retires only when a kit form DECLARES that it is single-pass over its spans and
that declaration is checked (the kit's evidence, D157: a fact, not its method). The check is
the kit's to name; pcrec's side is a find-all differential over the 67-pattern population
held to a linear work bound (the `run_iter_diff.sh` population, §6.7, with a counted-loads
arm). Retiring it re-derives S to 48 B.

**The sizing policy (answer-free, the manager's call).** Revision 1's policy stands: S covers
every DECLARED row, filed rows included, so landing a declared row never changes S. Two
consequences A10 makes explicit:
- S is re-derived AT the iterator's abi event (I1) from the declarations then current. If
  the kit's declaration or K5's status moves before I1, I1 takes the new value with no extra
  event.
- A row that RETIRES after I1 (K5) shrinks the max. Shrinking S is also an every-artifact
  abi event, and it buys 16 B of caller stack. The leaning is to shrink only when another
  abi event already moves the shared block, never as its own event; until then S keeps 16 B
  of headroom that no row uses, and the census (check 3) reports it.

**The checks (independent controls)**, revision 1's three, re-sourced:
1. **pcrec's derivation check.** At pcrec's build, a `_Static_assert` holds
   `PCREC_ITER_STATE_SIZE` (the literal in the emitted shared block) equal to the max the
   declarations compute. A declaration that outgrows S fails pcrec's build, naming the row.
2. **The artifact's own check, by the C compiler.** An artifact holding at least one BUFFER
   row emits `struct <p>__iter_state` with one member per held row (unions for alternatives,
   sums for concurrent rows), in the rows' real C types, and
   `_Static_assert(sizeof(struct <p>__iter_state) <= PCREC_ITER_STATE_SIZE && _Alignof(...) <= PCREC_ITER_STATE_ALIGN, ...)`.
   The expectation (S) and the subject (the compiler's layout) share no source. EMPTY at I1
   (no row held yet): declared UNREACHED with its trigger (I2's first kit row).
3. **The census** (`make test-iter`, I2 onward). Every corpus artifact's
   `sizeof(<p>__iter_state)` against S as headroom, with a floor per row on the number of
   artifacts holding it (K35). The `pair-hits` floor is the 67-pattern population.

**Alignment.** 8: no row keeps a vector register (D165 add. 1). A row needing 16/32/64
raises `PCREC_ITER_STATE_ALIGN`, an abi event.

---

## 2. The entries

### 2.1 `<prefix>_next` (exported, contains the search body)

```c
int <prefix>_next(rx_iter *it, const unsigned char *s, size_t n, ptrdiff_t (*caps)[2]);
```

- **Returns 1** when a match was found. Then `caps` (if non-NULL) holds `<PREFIX>_NCAPS`
  pairs, exactly as `<prefix>_search` would write them for this position.
- **Returns 0** otherwise. `it->rc` says why: 0 means done; a give-up or refusal code means it
  ended there (§3.4). Every later call returns 0 again with no work (sticky).
- **Two-valued on purpose.** `while (<prefix>_next(...))` is D165's idiom, and §3.1¶3 records
  what a three-valued return does in a `while`: a give-up read as a match spins forever. The
  code lives in `it->rc`.
- **`caps` may be NULL.** `next` then uses a local `<PREFIX>_NCAPS`-pair array for the advance
  (it needs the span). The twin's `Z` arm checks the count with `caps == NULL`.

**The emitted shape** (each piece measured in the twin, `findall_iter/twin/mktwin.py`):

```c
static inline __attribute__((always_inline))   /* or static noinline: §2.2 */
int <p>__find(const unsigned char *subject, size_t subject_length, size_t search_from,
              ptrdiff_t (*capture_spans)[2] /*, the mode: §4.2 */) { <today's _search body> }

__attribute__((noclone))                        /* K24, as today */
int <p>_search(...) { return <p>__find(..., ONESHOT); }

static inline __attribute__((always_inline)) size_t <p>__adv(s, n, pos)  { <next_pos's body> }
static inline __attribute__((always_inline)) int <p>__step(rx_iter *it, s, n, c) {
    /* the RETRY arm (§3.3), the search from it->lo, the advance (§3.1) */ }
static inline __attribute__((always_inline)) int <p>__enter(rx_iter *it, s, n) {
    /* §1.2: bind or check; the once-per-iterator checks */ }

__attribute__((noclone))
int <p>_next(rx_iter *it, s, n, caps) {
    if (!<p>__enter(it, s, n)) return 0;
    ptrdiff_t local[<P>_NCAPS][2];
    int r = <p>__step(it, s, n, caps ? caps : local);
    if (r == 1) return 1;
    it->rc = r; return 0;
}
```

- **Nothing in this chain is a second exported call**, as D165 item 5 requires. `_next`
  does not call `_search`. `__find`, `__adv`, `__step` and `__enter` are static, so no PLT
  or semantic-interposition indirection reaches them under `-fPIC`. That PLT cost on the
  exported seam entries was the cost [LOSS-REVIEW] candidate 1 removed.
- **`<prefix>_next_pos` stays exported and unchanged** (§3.1.1). The iterator calls its
  static twin `__adv`. One emitter writes both from one string, so they cannot drift.
  Today's loop pays one exported `_next_pos` call per match; the iterator pays none.
- **`rx->entries->next`** (D165 item 3, [V-E] S1). `<prefix>_next`'s type is
  prefix-independent: `int (*)(rx_iter *, const unsigned char *, size_t, ptrdiff_t (*)[2])`.
  It is variable-independent too, because vars ride `rx_iter`. So the pointer in
  `rx_entries` is the function itself, with no trampoline.

### 2.2 The body: one source function, inlined where gcc can copy it

**Measured in the twin** (`twin/out/run_twin_inline.out`; gcc 15.2 `-O2`, x86-64).

**DFA artifacts: `_search`'s instructions are IDENTICAL to today's** once the body moves into
`__find`. `_search` keeps the same size, and its `objdump` matches after relative-address
normalization. This holds on `a`, `\w+`, `a*`, `(?:ab|a)` and utf8 `a`. On `[0-9]+x`
(579 → 563 B), `a(b|c)+d` and utf8 `.` the instructions DIFFER. Gcc schedules the inlined
copy differently; no source change caused it. The parity gate's `L_old` against `L_new` arm
(§5.3) decides whether that matters.

**The cost is `.text`.** `_next` and `_next_n` each carry a copy of the body:

| twin | plain `.text` | + `_next` + `_next_n` (inline) | + both (shared noinline body) |
|---|---|---|---|
| `a` | 1,576 | +1,136 | +840 |
| `\w+` | 2,718 | +1,546 | +832 |
| `[0-9]+x` | 2,564 | +1,724 | +840 |
| utf8 `.` | 3,509 | +2,587 | +989 |
| VM hybrid `a(b|c)+d` | 3,574 | +1,587 | +848 |

`next` alone is about half of each "+" column (`_next` 433-1,079 B inline, 321-666 B shared).
These are OBJECT bytes. The emitted-C SOURCE bytes the size caps count grow by a fixed amount
(the wrappers' text), and §6.4 keeps them out of every length decision.

**One body that gcc cannot copy: the DFA attempt route.** Its direct-threaded dispatch keeps
label addresses in a `static const void *const <p>_targets_N[]`. Gcc refuses to inline such
a function anywhere, with "can never be copied because it saves address of local label in a
static variable" (twin case `\G\w+`).
- The census (`twin/label_census.py`) finds this shape on exactly the DFA `attempt`-scan
  artifacts: 233 of 4,243 compiled byte artifacts and 232 of 4,254 utf8. The VM and the
  other DFA routes have none in their search body.
- For those bodies `__find` is `static __attribute__((noinline))`, and both entries call it.
  `_search` becomes a 9-byte tail jump, and `_next` makes one internal direct call per
  match.

**The emission rule**, a two-row first-match table read off the body the emitter just wrote:

| row | when | `__find` linkage |
|---|---|---|
| `shared` | the body defines a static label table | `static noinline`; `_search` tail-jumps, `_next` calls |
| `inline` | otherwise | `static inline always_inline`; a copy in each entry |

**The alternative: one rule, `shared` for every body.** It is priced in the twin's
`TWIN_SHARED=1` arm. `.text` grows by a constant +832..+989 B instead of +997..+2,587, and
`next` makes one internal call per match. The parity gate has an `I_shared` arm for exactly
this. If `I_shared` is within the noise floor of `I`, the one-row rule wins on size and on
simplicity (D77: decided by measurement). Until it is measured, `inline` is the design of
record, because D165 item 5 asks for one call per match.

### 2.3 Batching: `<prefix>_next_n` (designed and twinned, HELD — Q2)

```c
size_t <prefix>_next_n(rx_iter *it, const unsigned char *s, size_t n,
                       ptrdiff_t (*out)[2], size_t k);
```

- **Writes** up to `k` whole-match spans into `out[0..k)` and returns the count. A count below
  `k` means the iterator ended, and `it->rc` says how. The iterator state is the same as for
  `next`, so `next` and `next_n` calls may be MIXED on one iterator.
- **Spans only.** Captures are deferred to [CAPTURE-ARRAY], whose array model (one row per
  match, opt-in per group) is where a batched capture layout belongs. A caller wanting
  captures calls `next`.
- **One body.** `next` and `next_n` share `__step` (inlined into both). `next` is not
  literally `next_n(K = 1)`, because it writes full captures where `next_n` writes spans. The
  sharing is the step, so the semantics cannot diverge. The twin checks `I == N` on every
  case, batch boundaries crossed at K = 3.

**Its price against the parity gate:**
- per match it saves the exported call, `__enter`'s checks and the epilogue (§5.1);
- per artifact it costs 392-1,286 B `.text` (twin, both forms);
- the DENSE-NOTES hypothesis ("batching pays one unpredictable exit per block, not per match")
  is unmeasured.

**D41 item 5 rejected "batch find-all as a PRIMITIVE"** because "capacity negotiation
reinvents the cursor with worse ergonomics". `next_n` is a METHOD of the cursor D41 named as
the additive extension. Capacity is the caller's `k`, and the cursor continues.

**Recommendation.** Time the twin's `N` arm in the parity slot. Fold `next_n` into I1 if it
beats `I` by more than the noise floor on the dense cells; otherwise file it with that
trigger (I4). Adding it later is a second every-artifact abi event, and that is the price of
waiting.

---

## 3. Semantics

### 3.1 The advances move inside

`next` applies `match_api.md` §3.1.3's two advances internally, so a caller never transcribes
them. After a NON-EMPTY match it resumes at `__adv(s, n, end − 1)` (K75, D132: the aligned
end). After an EMPTY match it applies the retry rule of §3.3, which for a pattern that cannot
report an empty match degenerates to §3.1.3's `__adv(s, n, start)` exactly. The twin checks
that on every non-retry case (`I == L`, 35 cells incl. utf8 `a`/`.` over stray continuation
bytes, `twin/out/run_twin_inline.out`).

### 3.2 `lo` and termination

`lo` is only ever written by `__step`, and every write is strictly greater than the previous
match's start: `__adv` returns a position `> pos`. The retry keeps `lo == q`, then advances
past q in the same call when the retry fails, so it never repeats. `lo > n` ends the iterator
(`rc = 0`). So `lo` is monotone non-decreasing (D165 item 1) and the iterator terminates.

### 3.3 NOTEMPTY_ATSTART: the iterator matches PCRE2's global iteration (Q1)

**The rule, pcre2demo.c's:** after an EMPTY match whose reported span is `(q, q)`, retry at q,
ANCHORED, under NOTEMPTY_ATSTART. On a match, report it. On no match, advance one character
and search on. An empty match at `q == n` ends the iterator with no retry.
The retry is ANCHORED, as pcre2demo's is. On every corpus pair an unanchored retry answers
the same, but `\G` tells them apart: `\G|b` over `"xb"` gives `(0,0) (1,1) (1,2) (2,2)`
anchored and `(0,0) (1,2) (2,2)` unanchored, because an unanchored retry still reads `\G`
at q (`sem/out/retry_anchoring.out`).
NOTEMPTY_ATSTART rejects a match whose REPORTED span is `(q, q)` with the report starting at
q. It tests the reported start, not the consumed one (PCRE2's `Fstart_match ==
start_offset`). That is why `ab\K` gives `(2,2) (4,4) (6,6)`: the retry at 2 consumes `ab` and
reports `(4,4)`, which is empty but not at 2.

**Measured** (`findall_iter/sem/`; libpcre2 10.46, byte mode, options 0):

| population | pairs | same | diverging | of which the loop is NOT a subset |
|---|---|---|---|---|
| `tests/encseam/findall_cases.txt` + 18 targeted cells | 44 | 32 | 12 | 1 (`a??b?` over `"ab"`) |
| the corpus: every plain byte block × its own inline subjects | 29,502 compared (157 skipped) | 28,439 | 1,063 (160 of 3,778 patterns) | **374** |

**Python's `re.finditer` agrees with libpcre2's global loop on every targeted cell checked**
(`|a`, `a??b?`, `x*|y`, `(?<=a)|b`, `(?=b)|b`, `a*?|b`, `(?:a|)*?`). So the global semantics
is the one both of pcrec's oracles share.

**Findings against today's spec, for the I1 spec hunk:**
- **§3.1.3¶9's "the divergence is always an OMISSION ... a strict subset" is FALSE.** It fails
  on 374 of 1,063 diverging pairs. `a??b?` over `"ab"`: the loop reports `(0,0) (1,2) (2,2)`
  and PCRE2 `(0,0) (0,2) (2,2)`, so `(1,2)` is a span no oracle reports. On
  `(?:(?:b*|a+){0,2})*` over `"aab"` the loop reports MORE matches (4 vs 3).
- **¶9's "every greedy quantifier among the agreeing cases does not diverge" names the wrong
  axis.** `x*|y` is all-greedy and diverges, because an earlier alternative prefers the empty
  string. The CSV-field idiom `(?:^|,)([^,]*)` drops fields under the loop: over `","` the loop
  reports one field and PCRE2 two.
- **¶11's `\K` sentence** ("identical to libpcre2 driven through the same loop") is true, but
  libpcre2's own global iteration reports `ab\K` over `"ababab"` THREE times where the loop
  reports two.

**The gate: `reports_empty`, a new E1 fact.** "Can the artifact REPORT an empty span" =
nullable OR the pattern holds `\K`.
- Bare nullability is UNSOUND as the gate: `ab\K` and `ab\Kc?` are non-nullable and diverge
  (`sem/out/nullable_census.out`).
- Census over 3,778 patterns with a verdict:

  | | count |
  |---|---|
  | gate true | 686 (605 nullable; 81 more by `\K` alone) |
  | diverging on its own subjects | 160 |
  | gate false yet diverging | **0** (the soundness control) |

- Bare nullability as the gate would have shown 2 as gate-false and diverging, which is why
  the gate includes `\K`.

**Where the retry machinery is emitted:** only on `reports_empty` artifacts (686/3,778 =
18.2%). Elsewhere `__step`'s retry arm is absent from the text, and the iterator is §3.1.3's
loop exactly (twin: 35 cells, `I == L`). A sharper structural fact, `empty_pref` ("some empty
path precedes a non-empty path in priority order", false for `a*`, `a|`, `(a|)`), would arm
only patterns that can diverge. It is FILED as unlock U11, with this census as its control:
a pattern it marks false must never diverge. Its trigger is a measured cost of the futile
retry on a gate-true, non-diverging pattern (one failing anchored attempt per empty match,
e.g. `a*` over `"bbb..."`).

**The retry, per route.** The retry is an anchored attempt at q under a NOTEMPTY_ATSTART
predicate. It runs with its OWN budget, as pcre2demo's retry is its own `pcre2_match` call.

- **VM (and the VM hybrid).** The accept label gains one guard: reject when
  `reported_start == scan_position && reported_start == ctx->pos`. Here `reported_start` is
  the `\K` slot when set, else `ctx->pos`, which is `vm_report_captures`'s own rule.
  - The guard reads the run state's `notempty` field, which the retry sets and `_search`
    leaves 0. In an inlined body it constant-folds away; in a framed body it is one
    predictable branch per ACCEPT, not per step.
  - The twin's guard is exactly this, carried in `ctx->user`. It reproduces libpcre2's
    global loop on all 25 retry cells: `|a`, `a*?`, `x*|y`, `a??b?`, `(?<=a)|b`,
    `(?=b)|b`, the CSV idiom, `ab\K`, each over 2-4 subjects incl. the empty one.
- **DFA.** No guard exists in a DFA. The retry is a NOTEMPTY START ROOT of the anchored
  (unwrapped) machine, a parameter of the same subset construction rooted at
  `Nfa.anch_start` (`anchored_match_unwrapped.md` §2).
  - The root is the start closure with its ACCEPTING threads removed and with NO accept
    pruning. In a leftmost-first construction those threads are the empty matches. Removing
    them lets lower-priority non-empty threads continue, which is exactly "the preferred
    match among the non-empty ones".
  - States are interned with the anchored machine's, so the root adds the states only it
    reaches.
  - On a `reports_empty` DFA artifact the root is MANDATORY. A DFA artifact has no VM to
    fall back to, so no other correct retry exists.
  - The root is a new machine ROLE (`notempty-anchored`). The size ladder's drop rungs never
    list it; its bytes count toward the caps like any machine. `-fno-anchored-dfa` still
    stops `_match` from using the anchored machine, but the root and the states it reaches
    stay on these artifacts.
  - On a DFA route `\K` never occurs (`\K` forces the VM, §3.1¶20), so "reported span empty
    at q" is "zero bytes consumed".
  - The root is not twinned (it needs the compiler). Its control at I0 is a zero-mover step:
    the construction with an `--emit-ir`/`--emit-facts` listing of the root, held against
    libpcre2's anchored NOTEMPTY_ATSTART answers on every `reports_empty` corpus block,
    before any artifact emits it (§7, I0b).
- **Compound.** The controller's `_match` is F's one attempt at `ctx->pos` (`compound.md`
  §B.3), so the retry is F's attempt under the notempty root. F is P bounded to one attempt,
  correct at any position.

### 3.4 `rc` and the give-up codes (D158)

- `it->rc` is 1 while live, 0 when done, and a code when a call ended in a give-up
  (`[PCREC_ERR_FLOOR, −2]`) or a refusal (below the floor: STARTPOS, UNSET_VAR, UTF,
  INTERNAL, ITER). It is sticky: after a non-1 `rc`, `next` returns 0 with no work.
- On the call that ends it, `caps` is untouched (§3.1¶4 holds per call).
- **Budgets per call, as today.** Each `next` call's search gets the fresh budget a
  `_search` call gets. The retry gets its own, like pcre2demo's separate `pcre2_match` call.
  The tiered default (§10.9) applies per call exactly as in `_search`.
  - Hence: **on every call that does not run a retry, the iterator gives up exactly where
    today's loop gives up**, same call, same code. The body is the same code at the same
    `lo`, and the carried rows of §1.3 are exact caches that move no attempt position.
  - The retry is NEW work, run only where the global semantics needs it. It is not an
    optimization, so D158's direction rule does not apply to it. Its give-ups are stated in
    the spec hunk as the retry's own.
- **A carried row that is an OPTIMIZATION** (the reseed hint, [OPT-HYB-RESEED-XCALL]) changes
  which positions the VM attempts, so D158 binds it. Its admission is GIVEUP1's direction
  check ([GIVEUP-DIFF]) before it lands (§9 U5).
- **After a give-up** a caller can deliberately skip on, e.g. with
  `RX_ITER_INIT_AT(lo + 1)` after reading the failing position from a FRESH iterator's
  record, but nothing resumes a gave-up iterator implicitly. PCRE2's demo stops the same way.

### 3.5 `\G`, `^`, and the start position

- **`\G` asserts at `lo`, the call's search start.** After a non-empty match that is the
  previous match's END (aligned, K75). During a retry it is q, the empty match's position.
  After a failed retry it is `__adv(q)`.
  - This is PCRE2's global `\G` (`assertions_design.md` §4.3), and the same as today's loop
    on every non-retry call.
  - `\G\w+` over `"ab ab ab"` stays a tokenizer: `(0,2)` then done (twin case `rg`, all
    cells `I == L == libpcre2`).
- **`^`/`\A` assert at absolute offset 0** (§3.1¶7), unchanged.
- **The first position.** FRESH starts at 0. FRESH_AT starts at the caller's `pos`, which is
  checked ONCE at bind by the artifact's startpos guard. A mid-character `pos > 0` gives
  `rc = PCREC_ERR_STARTPOS` (§9.2), or is aligned forward once under
  `-fstartpos-guard=align` (D133).
- **No later call runs the guard**, because every `lo` the iterator computes is a character
  boundary (§3.1.3¶6, §9.5). So `next` emits no guard on the BOUND path, which saves one
  load and branch per call under utf8. Sabotage S935 plants the guard's removal at bind and
  is detected by an `RX_ITER_INIT_AT` mid-character cell.

### 3.6 UTF-8 boundaries and `-futf-check`

- **Boundaries:** §3.1, §3.5. K73's offset-0 start (a subject beginning with continuation
  bytes) is the body's own SEEK, unchanged. K74 (the empty-match family at an ill-formed
  END) is unchanged and stays open.
- **`-futf-check`: validate ONCE per iterator.** At bind, `next` runs the artifact's
  validator over `[f, n)`, with `f` = the first `lo` stepped back LB characters (§9.4). If it
  finds an ill-formed sequence, `rc = PCREC_ERR_UTF` and the iterator ends; later calls
  never re-validate.
  - **This is answer-identical to today's checking artifact called through the loop.** Every
    later call's checked range `[f', n)` has `f' ≥ f`: `lo` is monotone and PCRE2's raw
    step-back walk is monotone in its start. So if the first range is clean, every later one
    is, and the first call is where today's loop is refused too.
  - Cost: O(n) once instead of O(n·m). That retires §3.1.2¶6's two-artifact idiom
    ("validate once, loop on the default artifact"). The spec hunk points that paragraph at
    the iterator.
  - Sabotage S933 (set CHECKED before validating) and S934 (validate every call: an
    answer-equivalent mutant, detected structurally) cover it.

### 3.7 Variables and callouts

- **Variables.** `RX_ITER_INIT_VARS(vars, nvars)` (and `_AT`) record them in the iterator.
  They are constant for one find-all, as the subject is. A var-bearing artifact validates
  them ONCE at bind; an unset or ill-formed variable gives `rc = PCREC_ERR_UNSET_VAR`, which
  is sticky. An artifact with no variables ignores the fields. `docs/spec/vars.md` gains the
  hunk.
- **Callouts.** Module `callouts` is not built. When it builds, a callout receives
  `rx_ctx`, never the iterator: the iterator is not threaded into any call chain.
  - This SUPERSEDES `compound.md` §C's plan of an `rx_ctx` session pointer "of
    [FINDALL-NEXT]". That plan existed to carry find-all state through every call. D165 puts
    the state in the TOP-LEVEL artifact's iterator, so a compound used as a callout runs its
    `_match` with no iterator and stateless, and §C's foreign-cache hazard cannot arise.
  - The owner check of §1.2 is the same guard at the one place an iterator can be handed to
    the wrong artifact.

### 3.8 Routes

- **DFA routes** (`unanchored`, `rev-end`, `attempt`, `empty`, `compound`): the body is the
  route's own code, untouched. The iterator adds entry/exit and the retry root (§3.3).
  - A `rev-end` find-all ends after its one match.
  - A pinned search at `lo > 0` on a context-dependent start state can return 0, as §3.1¶21
    states for `_search` at `startpos > 0`; the iterator reports it identically.
- **VM and VM hybrid:** the body is `_search_run` with the same tiered storage. The hybrid's
  inlined prefilter is a static function both bodies call. The retry is the accept guard.
  - The prefilter-less VM's start-set hat (§3.1¶12) and the hybrid's re-seed are per-call
    logic in the body, unchanged.
  - The reseed hint is the one row that would carry across calls (FILED, §9 U5).
- **Compound:** `next`'s body is the controller (`first-nonzero(F, Q)`), whose parts are
  static. Parts that hold rows get SUMMED regions (§1.3). F runs only where the floor can be
  live (`lo == 0` or `\G`), so in a find-all it runs at most at the first call unless P has
  `\G`.

### 3.9 Reentrancy (§5.3)

The artifact still holds no mutable state of its own; TS-1 and TS-2 are unchanged, since
`rx_iter_fresh*` are `static inline` with no static object. The iterator is CALLER-owned
mutable state, like `caps`:
- any number of iterators may run concurrently, one thread each;
- two threads sharing one iterator is a data race in the caller;
- a callout that re-enters the same artifact's `next` uses its own iterator.

---

## 4. The kit seam (D157: facts only)

### 4.1 Where the kit's state lives

- **pcrec gives the kit:**
  - a REGION of `st`: an lvalue's text and its byte offset;
  - the region's guarantees: zero at the first use of an iterator; persistent across calls of
    the same iterator; `lo` monotone; the same unchanged `(s, n)`; one thread.
- **The kit declares, per stateful form:** its bytes and alignment (`mf_result` / the form's
  row), and that ZERO is its fresh state (addendum 1: "zero-init + the same unchanged
  (s, n)").
- **Zeroing.** pcrec's bind code zeroes the region's DECLARED bytes, 24 or 32. It never
  memsets S: D165 item 5 as the manager read it in addendum 1. This is R17-b″'s zero-init
  hook, carried as a fact rather than as the kit's code.
- **How the kit's text reaches the region is the kit's choice.** It may copy in at the
  storage point and out at every exit (ISO C via `memcpy`; the local stays
  register-resident), or use a `__attribute__((may_alias))` pointer into the buffer (GNU C,
  which the artifact's dialect allows). Both are legal; the union's `uint64_t` member gives
  the alignment.
- **What pcrec does NOT allow:** a plain cast of `st.b` to a struct pointer without
  `may_alias`. That is a strict-aliasing violation the house's `-O2` users would compile
  into wrong code, so G2's SIMD family and C5 should plant it.

### 4.2 M, N and H reach the kit's dispatch (D161 add. 11, R-19)

- **M (the call mode).** `<p>__find` takes the mode as a parameter: `_search` passes ONESHOT
  and `next` passes ITER. In the inlined form the parameter is a constant at each call site,
  so a kit dispatch on M folds to one arm per entry. In the `shared` (static-label) form it
  is one runtime branch per call, not per use.
  - **This changes R-19's fact shape.** R-19 states `mf_site.body` per BODY, and
    r17b_prime.md §2.4 assumes `_search` and `next` are two bodies. With one parameterized
    body, the fact becomes "the body's mode is the C expression `<mode>`, constant per
    entry".
  - **REQUEST (for main to file as R-20 at R17-b″):** `mf_site.body` gains
    `MF_BODY_PARAM` plus a hook naming the mode expression.
  - **The alternative** keeps R-19 as filed by emitting TWO source bodies, one per mode, with
    the DFA tables hoisted to file scope so `.rodata` is not doubled. It costs a second
    emitter walk and the body's source bytes twice. It gains R-19 unchanged and `_search`'s
    TEXT untouched. The twin cannot price the source half (it writes one source); the object
    half is the same, two copies either way.
  - Recommendation: the parameter. One emitter walk, one source, and the twin shows
    `_search`'s object code unchanged.
- **N.** Unchanged: `n − start` at the storage point, with R-19's start hook the origin
  expression (`search_from` inside `__find`, which IS `lo` in `next`).
  - Inside an iterator N is still the REMAINING subject. regime_tables.md §2's note ("dense
    find-all is invisible at call time") is answered by H, not by N.
- **H.** The kit's own, in its region. The previous step's span is `lo_now − lo_prev`; the
  kit keeps `lo_prev` (the `kit-h` row's 8 B), and the mask's popcount is in its 24 B.
  pcrec does not compute H. It promises only the region and `lo`'s monotonicity.

### 4.3 The contract facts (D161 add. 11)

The knowledge record's keys and who produces each, as of I1:

| key | producer | through the iterator |
|---|---|---|
| P | pcrec (site description) | unchanged |
| E | pcrec (analysis object, D162) | unchanged |
| A | pcrec (measurement set, D166; the seam only) | unchanged |
| N | pcrec entry | `n − lo` at the storage point |
| M | pcrec API | the body's mode parameter (§4.2) |
| H | storage pcrec (`st` region); content kit | the region, zero-fresh, persistent |

**Emission fact owed by pcrec (addendum 1).** On every search path today pcrec emits at most
ONE stateful FIND site, so the kit's rows never sum with each other. r17b_prime.md F1 counted
one `__next_candidate` site on all 3,906 R17-b movers, and §1.3 argues the route structure.
They DO sum with pcrec's own rows: the pre-check's `pair-hits` and the hybrid's
`reseed-hint`. A compound sums across parts. §1.3's table carries both.

---

## 5. Overhead (D165 item 5) and the parity gate

### 5.1 The call and instruction count, per match

| | today's loop (§3.1.3) | the iterator `next` | `next_n` (per match, amortized) |
|---|---|---|---|
| exported calls | 2 (`_search`, `_next_pos`) | **1** | 1/k |
| entry checks | `startpos > n`; utf8 guard; `-futf-check` O(n); var check | `hdr` compare; one fused binding compare; `rc` test; `lo > n` | per batch |
| advance | the caller's two-arm expression + the `_next_pos` call | inlined `__adv` | inlined |
| per-iterator, once | — | bind (6 stores + the declared rows' zeroing); the guard/check/vars once | same |
| init | — | **1 store** (`RX_ITER_INIT`), 2 (`_AT`) | same |

The iterator's per-call additions are three L1 loads and two predictable branches. It removes
an exported call (a PLT call under `-fPIC`), the caller's advance expression, the per-call
utf8 guard, and the O(n) validation per call. So parity or better is the prediction on every
cell. The prediction is UNMEASURED and is exactly what the gate decides.

### 5.2 Static internals

`__find`, `__adv`, `__step`, `__enter` and (on `reports_empty` artifacts) `__retry` and the
notempty root are static. The kit's bodies stay static (D88 add. 1). A compound's parts stay
static. The only new exported symbols are `<prefix>_next` and, if Q2 rules it in,
`<prefix>_next_n`.

### 5.3 The PARITY GATE (designed here; run later on a quiet box via main)

D165 item 5's named measurement: "iterator vs today's `_search` loop on dense tiny matches ...
at parity or better; worse is a finding, not a tolerance."

**Cells.** D165 names cells 1, 3 and 5. Cells 2, 4 and 6 are added because the body linkage
differs on them.

| # | pattern | subject | regime |
|---|---|---|---|
| 1 | `a` | `a` × N, N ∈ {64, 4 KiB, 1 MiB} | one match per byte, DFA memchr route |
| 2 | `a` | `"a"`, `"b"`, `""` (whole iteration, init included) | the one-byte subject; the empty subject |
| 3 | `\w+` | prose: rwcorpus's English prose class at 4 KiB and 1 MiB (sha-pinned, `worktrees/.corpus/`) | dense word matches, DFA `landing` route |
| 4 | `(a)` | `a` × 4 KiB | the VM route (captures), one match per byte |
| 5 | `\w+` | one-byte subject `"x"` | per-iteration fixed cost |
| 6 | `^a\|b` `--engine=dfa` (an `attempt`-scan artifact; confirm the stamp) | `b` × 4 KiB | the `shared` (static-label) body linkage |

**Arms**, each a separate binary, interleaved:
- `L_old`: today's `_search` loop against the PRE-iterator build (main at I1's parent),
  §3.1.3's code verbatim.
- `L_new`: the same loop against the I1 build. Its gap to `L_old` is the cost the refactor
  puts on `_search` itself.
- `I`: `<prefix>_next` with caps.
- `I_shared`: the twin's `TWIN_SHARED=1` form (§2.2's alternative rule).
- `N64`: `next_n` with k = 64 (Q2's evidence).
- `I0`: `next` with the binding check removed (§1.2's price).
- `A`: an A/A arm (`L_new` built twice) for the noise floor.

The pre-build run uses the TWIN for `I`, `I_shared`, `N64` and `I0` (`findall_iter/twin/`
builds them today). The post-build gate uses the built artifacts.

**Regimes:**
- R1: artifact `.o` linked statically into the driver (direct calls).
- R2: artifact in a shared object, `-fPIC`, called through the PLT. The iterator's predicted
  margin is largest here.
- Both at gcc 15.2 `-O2` on the Linux dev box (Zen 4).
- The kit's verdict regime: one core pinned with its SMT sibling idle (`taskset`), 5
  launches, arms interleaved per launch, median and IQR per (cell, arm).

**Verdict.**
- Per cell and regime, `I / L_old ≤ 1 + floor`, where floor = the A/A arm's
  max(|median ratio − 1|, IQR/median).
- A worse cell is a FINDING, recorded with its numbers.
- `L_new / L_old` within the floor is the "`_search` unharmed" half.
- `N64` and `I_shared` are reported for Q2 and §2.2, not gated.

**Async discipline.**
- The run is a detached chain script (BOILERPLATE: `nohup setsid`, a `.lift` waiter, one
  waiter per worktree, a completion trailer `== parity COMPLETE`), launched by main in a box
  window.
- Its harness is `findall_iter/twin/` (the twin builder) plus a timing driver written at I1's
  pre-build stage, beside `drv.c`'s answer driver. The answer driver runs first on every arm
  as the run's correctness gate.
- This lane read no clock.

---

## 6. The abi event, the spec, the migration, the checks

### 6.1 The abi event (one, at I1; D76/D94 readers found by grep)

I1 bumps `PCREC_ARTIFACT_ABI` (78 at this lane's base; "the next number at landing"). Its
readers, by grep at `ee01f4dbb`:

| reader | site |
|---|---|
| the constant | `src/gen/emit_dfa.c:54` |
| the shared-block guard text and `rx_info.abi` row | `docs/spec/match_api.md` §1¶7, §6 (the `abi` row of the `rx_info` table) |
| the change log | `docs/dev/history/abi_changelog.md` (+ the entry) |
| `ABI_EXPECT` | `tests/codegen/run_codegen_tests.sh:3149` |
| recursion-identity (B) FILEPIN self-pin | `tests/codegen/run_recursion_identity.sh:1251` |
| sabotage S693's anchor | `tests/mech/sabotages/S693_abi_not_bumped.sh:51` |
| byte-count readers (the second reader class: their text cites no abi digit, their values move) | `tests/resource/run_resource_tests.sh:756`'s K59-PREMUL rung pin (`a{5,25000}`, 762911); `run_cpset_structure.sh`'s `EMITTED_BYTES` manifest; the size tripwires; `run_anchored_match.sh` §5's drop-rung caps; `emit_sweep.py`'s VARIANT_PINS. All recompiled and re-measured at the SAME `-o` basename, never re-typed |
| suites that move without citing the number (D94 addendum) | registry (dump surfaces: `PCREC_ERR_ITER` in the code list; a stamp), codegen, rxtsource (`mg` line), cpset, startset manifests if any byte-count-keyed |

**The commit carries the ritual's own grep.** The list above is a floor (coding_guide §3.5),
and the readers are re-derived at the commit.

**What changes on EVERY artifact:**
- the shared block (rx_iter, the PCREC_ITER_* constants, PCREC_ERR_ITER, the two inline
  helpers);
- `_search`'s text (body moved into `__find`);
- `_next` (+ `_next_n`), its declaration, and the `<PREFIX>_ITER_RETRY` stamp (§6.3).

**On `reports_empty` artifacts only:** the retry machinery (VM accept guard / DFA notempty
root).

**Not moved:** `rx_info`'s fields.

### 6.2 Spec hunks (D80), each in I1's commit

- **`docs/spec/match_api.md`:**
  - §1¶2: the per-artifact symbol list gains `<prefix>_next` (`_next_n`).
  - §1¶5, ¶6: the shared block's type list gains `rx_iter` and its two inline helpers; the
    contract constants gain `PCREC_ITER_*` and `PCREC_ERR_ITER`.
  - §2: the verbatim block.
  - §3¶1: the entry table.
  - **NEW §3.8 "The find-all iterator"**: the contract of §1-§3 above, in facts-only spec
    voice, numbered per docs/spec/CLAUDE.md.
  - §3.1.3: becomes "use the iterator". The hand loop stays as the one-shot alternative,
    with ¶9 corrected per §3.3's findings (not a subset; the CSV idiom; `\K`).
  - §3.1.2¶6: validate-once moves to the iterator.
  - §4: a `PCREC_ERR_ITER` row.
  - §4¶10: no row change. An iterator is never called from a generated call site.
  - §5.3: the iterator is caller-owned state.
  - §9.2¶6: the iterator meets the guard only at bind.
  - §10: no `_in` variant; the tiered default applies per call.
  - §6.3: the new stamp.
  - The contents table is regenerated (`scripts/spec_toc.py`).
- **`docs/spec/rxt_format.md`:**
  - §1.7 `mc` is unchanged in meaning: still the §3.1.3 loop's count, still checked through
    `_search`.
  - NEW §1.7a `mg "<subject>" <n>`: the GLOBAL count, libpcre2's pcre2demo loop. The harness
    checks it through `<prefix>_next`. Where a block has an `mc` and no `mg`, the iterator is
    held to the `mc` count, and that is VALID only on a non-`reports_empty` block.
  - The parser (three legs, `rxt_schema.def`) gains the row. The spelling is the manager's
    (memory `pcrec-dd13b-syntax-is-managers`).
- **`docs/spec/vars.md`:** variables bound in the iterator.
- **`docs/spec/facts_listing.md`:** the `reports_empty` fact (I0).

### 6.3 Observability (D46)

- **`<PREFIX>_ITER_RETRY`** on every artifact: `"none"` (gate false), `"vm-guard"`, or
  `"dfa-root"`. It is one strategy choice per artifact, so it is a stamp. It joins
  match_api.md §6.3.2's inventory.
- **The held storage rows** go in `--emit-facts`' decisions section, not in a stamp, until a
  consumer asks (D77; [STAMP-REVIEW]).

### 6.4 Neutral to every length decision

The iterator's text is fixed scaffolding plus, on `reports_empty` DFA artifacts, a machine
role. The scaffolding is emitted inside the RQ-3 decision bracket (`src/core/sb.c`), so no
entry-shape knee, size term or cap reads it. It is excluded the same way SIMD's guarded bytes
are, so it moves no selection and no refusal set.

The notempty ROOT is a machine and counts like one (§3.3). It is the one size-visible part,
and its population is small: `reports_empty` DFA artifacts.

The check is the mover census of §6.7: every artifact's non-iterator text against I1's parent.

### 6.5 The in-tree drivers' migration (in I1's commit)

| driver | today | after I1 |
|---|---|---|
| `tests/assertions/gstart_findall.c` | the §3.1.3 loop, against libpcre2 driven through the same loop | gains an iterator arm held against libpcre2's GLOBAL loop. `\G` cells: the two agree on every non-retry cell, and the arm's own expectations come from the global loop |
| `tests/encseam/findall_driver.c` (+ `findall_cases.txt`) | the loop vs `re.finditer`, classes `exact`/`lossy` | gains the iterator arm. Under the iterator EVERY case is `exact` against finditer, so the class column gains an `iter` reading: `lossy` cases flip to `exact`. A case that stays lossy under the iterator fails. The loop arm keeps its classes, corrected by §3.3: `lossy` means "differs", no longer "a strict subset" |
| `tests/codegen/entry_shape_driver.c` | the loop over `_search` per entry shape | gains `_next` per entry shape: every shape's iterator equals its loop on its non-`reports_empty` cases |
| `tests/harness/driver.c` (the `mc` line) | the loop | runs BOTH: the loop for `mc`, the iterator for `mg` (or for `mc` where no `mg` and gate false) |
| `tests/compound/split_diff.c`, `loads_drv.c` | the loop over the compound's `_search` | gain the compound `next` |
| `docs/dev/lanes/f3search_driver.c` | doc-only reproduction | untouched (historical) |

### 6.6 The bench relay (for main)

DRAFT inbox text:

> pcrec abi N adds `<prefix>_next(rx_iter *, s, n, caps)`, the find-all iterator (D165). Your
> find-all cells call `_search` in the K75 loop and see none of its gain until the adapter
> uses it. Suggested: an adapter mode `iter` for every find-all cell, keeping the loop as
> `loop` for one release so the ledger shows both.
>
> SEMANTICS: on patterns that can report an empty match, the iterator follows PCRE2's global
> iteration (the empty-match retry, pcre2demo.c). The loop does not. Counts differ on those
> patterns: corpus 160 of 3,778, e.g. `(?:^|,)([^,]*)`, `x*|y`, lazy-empty patterns. Your
> equal-answer checks against pcre2/rust must take the iterator's count where the testee runs
> the iterator. Rust's `find_iter` semantics for empty matches is the bench's to check.
>
> Optional: `next_n` (if built) for a batched arm.

### 6.7 The checks (I1), each with its independent control

| check | subject | expectation, from | population (K35) |
|---|---|---|---|
| `run_iter_diff.sh` (new, `make test`) | every corpus (pattern, subject) pair through `<prefix>_next`, byte and utf8 arms, `--engine=auto` and `vm` | libpcre2 10.46's global loop (`semprobe.c`'s G, promoted to `tests/findall/`). Independent of pcrec | floor = the harvest's own count (29,502 compared pairs byte; utf8 harvested likewise). The diverging subset (1,063 byte) has its own floor, so the retry cells cannot silently vanish |
| iterator = loop | every non-`reports_empty` pair: `next` against today's `_search` loop | pcrec's own `_search` (shares the engine). This is the REGRESSION control, not the semantics one | non-gate pairs |
| `mg` lines | the harness, per block | written from libpcre2's global loop, oracle-verified at authoring | every diverging corpus pair gets one (generator in I1) |
| S derivation | pcrec build | the table's max vs the literal (§1.3 check 1) | every row |
| the artifact's `_Static_assert` | per artifact | S, against the C compiler's layout | EMPTY at I1 (declared UNREACHED, trigger I2) |
| binding / sticky / NULL caps / `next_n` | `drv.c`'s arms (`B`, `rc`, `Z`, `N`) promoted into `tests/findall/` | the iterator's own `next` arm (the twin's design) | every pair above |
| mover census | every artifact's text minus the iterator scaffolding, against I1's parent | the parent's bytes | full corpus, both arms (emit_sweep's population) |
| `-futf-check` once | utf8 ill-formed cells through `next` against the checking artifact's loop | the loop | `tests/utfcheck/`'s pinned sets |

### 6.8 The sabotage plan (S923-S942)

Every plant's detector is named, and its witness REACHES the site (the reach column). An
answer-equivalent mutant is declared, with its structural detector.

| id | plant | detector | reach |
|---|---|---|---|
| S923 | the non-empty advance uses `end`, not `__adv(end − 1)` (K75) | `run_iter_diff.sh` utf8 arm: `a`/`.` over `a\x80a` | `mc_illformed_utf8` + utf8 harvest |
| S924 | the empty advance steps from `lo`, not the reported start | `(?=a)` over `"xax"` (1, not 2) | lookahead corpus |
| S925 | the retry bit is never set | every diverging pair (1,063) | the diverging floor |
| S926 | the retry runs UNANCHORED | `\G\|b` over `"xb"` (4 matches anchored, 3 unanchored: the unanchored retry reads `\G` at q, not at q+1). NO corpus pair distinguishes the two (0 of 29,502, `sem/out/retry_anchoring.out`), so I1 adds this cell as an `mg` line | the added cell |
| S927 | the retry also fires after a non-empty match | double reports on `a*?`/`aaa` | retry cells |
| S928 | a failed retry does not advance | watchdog (wall) on `|a` over `"b"`: the iterator spins. Detected as a timeout (a firing timeout is a finding) | retry cells |
| S929 | `rc` not sticky after a give-up | a `--step-budget=3` cell: the call after the give-up must return 0 | `tests/findall/` give-up cells |
| S930 | `rc` not sticky after done | `drv.c`'s post-end call (`STICKY-FAIL`) | every pair |
| S931 | the binding check removed | `B=-10` arm | every pair |
| S932 | the header check accepts any word | an uninitialized-word cell (`hdr = 0`) must give `PCREC_ERR_ITER` | `tests/findall/` |
| S933 | `CHECKED` set before validation | utf8 ill-formed cells through a `-futf-check` artifact's `next` | `tests/utfcheck/` |
| S934 | validation runs every call (answer-equivalent) | STRUCTURAL: the codegen check counts one validator call in `__enter`'s bind path and none on BOUND | every `-futf-check` artifact |
| S935 | the startpos guard at bind removed | `RX_ITER_INIT_AT(mid-char)` must give `PCREC_ERR_STARTPOS` | utf8 `_AT` cells |
| S936 | the storage rows not zeroed at bind | UNREACHED at I1 (no row). Its trigger is I2 | declared |
| S937 | `PCREC_ITER_STATE_SIZE` decremented below a held row | the artifact's `_Static_assert` | UNREACHED at I1, DETECTED at I2 |
| S938 | `next_n` writes `k + 1` spans | an ASan cell with an exact-size `out` (if `next_n` is built) | `tests/findall/` |
| S939 | `next_n` continues after a give-up | the give-up cell through `next_n` | as S929 |
| S940 | `next` writes only the span, not the groups | VM caps differential: `next` vs `_search` per call | captures corpus |
| S941 | the VM accept guard tests the consumed start, not the reported start | `ab\K` over `"ababab"` (3, not 2) | `\K` cells |
| S942 | the DFA notempty root keeps the accept-pruned order | `a??b?` over `"ab"` on the DFA arm (`(0,2)`, not `(1,2)`) | DFA `reports_empty` cells |

### 6.9 Staged commits

| stage | what | movers | abi |
|---|---|---|---|
| **I0** | (a) the `reports_empty` E1 fact + its `--emit-facts` row; (b) the notempty root as a subset-construction parameter, listed in `--emit-facts` and never emitted into an artifact, with its control: anchored NOTEMPTY_ATSTART against libpcre2 over every `reports_empty` block; (c) `iter_rows.def` + the derivation check; (d) `tests/findall/` (the global-loop oracle, the harvest, the `mg` generator) and the `mg` line in all three `.rxt` legs, before any artifact reads it | ZERO emitted bytes (emit_sweep, all streams). The facts listing gains rows | none |
| **I1** | the shared block; `_next` (+ `_next_n` if Q2 says now); the body refactor; the retry machinery; spec hunks; drivers; checks; S923-S942 | every artifact (text) | ONE |
| **I2** | R17-b″: the kit's ITER form, its `kit-find`/`kit-h` regions; R-20 (`MF_BODY_PARAM`) | kit-form artifacts | a pcrec abi event (a kit byte move, D147) |
| **I3** | `pair-hits`: K5's linear pair arm | the 61 corpus / 11 bench two-stream artifacts | one |
| **I4** | `next_n` if Q2 holds it for a trigger | every artifact | one |

---

## 7. The standing design questions (docs/design/CLAUDE.md)

1. **The measurement regime. RELEVANT.**
   - Every number here is compile-only: `.text` sizes, instruction identity, store counts.
     All were taken at gcc 15.2 `-O2` x86-64 on the Linux dev box, plus answer differentials
     against libpcre2 10.46 (byte mode, options 0). None reads a clock.
   - The sizes are compiler-dependent. Another gcc may inline differently, which is why
     `L_new` vs `L_old` is a gate arm.
   - The parity gate (§5.3) is the one timed decision. It is in the latency regime (dependent
     calls, dense matches), on one box, in two link regimes. The PLT regime could widen the
     margin but is not predicted to flip its sign.
   - A different box (Zen 1, the Mac) is the bench's official verdict, not this gate's
     (D144 add. 4).
2. **The independent control. RELEVANT.**
   - Semantics is checked against libpcre2's own global loop. The probe is pcre2demo.c's
     loop over the library, which shares no source with pcrec. It is cross-checked by python
     on the targeted cells.
   - The iterator-equals-loop check shares pcrec's engine with its subject, so it is named
     the REGRESSION control, not the semantics one.
   - S is checked by the C compiler's layout against the literal.
   - Populations are counted by the harvest: 29,502 compared byte pairs; 686 gate-true
     patterns; 233 static-label bodies.
   - Each sabotage row names its reach.
   - The gate's soundness control (gate false ⇒ never diverges) was run and caught this
     lane's first gate (bare nullability, 2 counterexamples).
3. **What moves when the data is regenerated. RELEVANT.**
   - S is generated from the row table. A row change that changes the max moves the shared
     block on EVERY artifact (an abi event, with the readers of §6.1) and `sizeof(rx_iter)`
     for callers.
   - The `mg` expectations are regenerated from libpcre2. A new oracle version is a store key
     (`oracle_store/`), so a moved count is a clean miss, never silent.
   - The `reports_empty` fact gates the retry machinery. A change to its derivation moves
     exactly the artifacts whose gate flips (a mover census by ID).
   - The stamp `<PREFIX>_ITER_RETRY` moves with it.

---

## 8. The sibling-family lens: state carried across the calls of one find-all

D165 item 2 named three members. The survey finds these:

| member | carried what | owner | status |
|---|---|---|---|
| the kit's FIND cache (A3, R3/R4's H) | block mask, base/top, lo_prev | kit | I2 |
| the empty-match retry | one bit + `lo == q` | pcrec | I1 |
| `-futf-check` validated | one bit | pcrec | I1 |
| variables validated | one bit (CHECKED) | pcrec | I1 |
| K5's pair-arm pending hits | `ha`, `hb` | pcrec | I3 |
| the hybrid's reseed hint | the adaptive block | pcrec | FILED (U5) |
| [FINDALL-REENTRY]: the forward DFA's state at the previous match end | state + position (≈16 B) | pcrec | BOONIES (U6) |
| the hand-off re-entry's landmark ([REQ-HANDOFF-L1], K105) | the next landmark position | pcrec | U7 |
| a compound's per-part caches (`compound.md` §C) | per part | pcrec | via the sum rule |
| **streaming** ([M3]: state across subject CHUNKS, not across matches) | the automaton state at a chunk boundary | pcrec | U10, a SIBLING type |

All but streaming fit ONE mechanism: a declared row in S, zero-fresh, persistent, owned by the
artifact that bound the iterator. Streaming breaks the "same unchanged subject" invariant that
every row's validity rests on, so it gets its own type with its own invariants rather than a
mode of this one.

---

## 9. UNLOCKS (each with its trigger)

| # | unlock | trigger |
|---|---|---|
| U1 | `next_n` batching | the twin's `N64` arm beats `I` by more than the noise floor on cells 1/3 (§5.3) |
| U2 | validate-once (`-futf-check` O(n) once) | built in I1, no trigger |
| U3 | K5 linear (the `pair-hits` row), ~200× off-bench | its witness exists (walk_survey K5); the first post-framework optimization (I3) |
| U4 | the kit's A3 and R3/R4 rows (R17-b″) | the kit's |
| U5 | the reseed hint row ([OPT-HYB-RESEED-XCALL]) | its restated trigger (a bench find-all cell averaging > 1 re-seed per call, losing to `-fno-hyb-reseed`) + GIVEUP1's direction check |
| U6 | [FINDALL-REENTRY] carried DFA state | a bench find-all cell where re-entry is a measured share |
| U7 | the hand-off re-entry's landmark cache | K105's witness re-measured under the iterator |
| U8 | the substitution global loop ([M4-SUBST]) = `next` + a splice. replace_design.md §3.8's "the §3.1 loop cannot express the retry" seam DISSOLVES: the iterator expresses it | [M4-SUBST] opens |
| U9 | `rx_entries.next` ([V-E] item (1), [ART-MGR] S1): the uniform signature is ready | [V-E]'s trigger |
| U10 | a streaming sibling `rx_stream` ([M3]) | [M3] opens |
| U11 | `empty_pref`, the structural narrowing of the retry gate | a measured cost of the futile retry on a gate-true, non-diverging pattern |
| U12 | captures in `next_n` | [CAPTURE-ARRAY]'s design |
| U13 | `next`'s `shared` linkage for every body (one rule, smaller `.text`) | `I_shared` within the noise floor of `I` (§5.3) |

---

## 10. Questions for Frank (discussion: the problem, the forces, the leaning)

**Q1. Do we match PCRE2's global iteration (the empty-match retry), or keep today's loop
semantics?**
- *The problem.* The two answer differently on 160 of 3,778 corpus patterns. The real-world
  CSV idiom `(?:^|,)([^,]*)` loses fields under the loop. The loop is not a subset of PCRE2's
  answer (374 pairs report spans no oracle reports).
- *The forces.* D26: PCRE2 is the source of truth for what a pattern MATCHES, and python
  agrees. The cost is the retry machinery: a VM guard, and on DFA artifacts a mandatory
  notempty root. It is emitted only on the 18% of patterns that can report an empty match.
  `_search` and its documented loop are untouched.
- *Leaning.* Match PCRE2. The iterator is new, so it has no installed base to break, and
  shipping it lossy would freeze a known-wrong answer into a second entry.

**Q2. Batching `next_n` now or on a measured trigger?**
- *The problem.* It costs an every-artifact abi event whenever it lands, and 392-1,286 B
  `.text` per artifact. Its win is the per-match exported call, which the parity slot can
  measure on the twin before I1.
- *Leaning.* Measure in the parity slot first (the twin is ready). Fold it into I1 if it
  beats `next` beyond the noise floor on dense cells, otherwise file it. Captures stay with
  [CAPTURE-ARRAY].

**Q3. `(s, n)` per call (D165 as ruled) or bound at init?**
- *The problem.* D165's shape passes `s, n` on every call, and the iterator must then check
  them (§1.2) or trust them.
- *The alternative.* `rx_iter it = RX_ITER_INIT(s, n); while (<p>_next(&it, caps))`. This
  makes the mismatch impossible by construction, needs no per-call compare, and costs three
  init stores instead of one. `rx_entries.next` gets a shorter signature.
- *Leaning.* Keep D165's ruled shape with the checked binding. The alternative is recorded
  here because it is cheap to adopt BEFORE I1 and costly after.

**Q4. A new refusal code `PCREC_ERR_ITER` (−10)?**
- *The problem.* A foreign, uninitialized or misbound iterator must not be silently rebound
  (re-reported matches) or trusted (a wrong answer through the kit's cache).
- *The alternatives.* Silent rebind (cheaper, silent); undefined behavior (cheapest).
- *Leaning.* The code. It is one row in §4's table, and generated call sites never meet it.

---

## 11. Findings (for the manager)

- **F1.** §3.1.3¶9's "the loop's spans are a strict subset" is false on 374 of 1,063
  diverging corpus pairs. The witness is `a??b?` over `"ab"` (the loop reports `(1,2)`; no
  oracle does). `tests/encseam`'s four `lossy` cases happen to be subsets.
- **F2.** The divergence is not a laziness property. All-greedy `x*|y` diverges, and the CSV
  idiom `(?:^|,)([^,]*)` loses fields under the documented loop.
- **F3.** `ab\K` reports 2 matches under the loop and 3 under libpcre2's global iteration.
  §3.1.3¶11's "identical to libpcre2" is true only of libpcre2 driven through pcrec's loop.
- **F4.** The retry gate is `reports_empty` (nullable OR `\K`), not nullability. Two corpus
  `\K` patterns are the counterexamples.
- **F5.** Every DFA `attempt`-scan artifact keeps label addresses in a static table, so its
  search body cannot be duplicated by inlining (233 of 4,243 byte artifacts). Any design
  that inlines a body into two entries must special-case them by a declared row (§2.2), not
  by an assumption.
- **F6.** `rx_iter it = { MAGIC }` trips `-Wmissing-field-initializers` under the harness's
  own `-Wextra -Werror`, and any aggregate initializer is a full memset. The
  static-inline-returning spelling costs one store, warning-free at every `-O` level.
- **F7.** `compound.md` §C's `rx_ctx` session pointer is superseded by D165's iterator
  (§3.7). That design's foreign-cache hazard needs no owner-tagged region once the state
  lives only in the top-level artifact's iterator.
- **F8.** A var-bearing artifact's `_search` has a non-uniform signature (18 corpus
  patterns). `next`'s is uniform, because the iterator carries `vars`.
