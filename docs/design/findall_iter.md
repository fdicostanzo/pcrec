# [FINDALL-NEXT] — the find-all iterator `rx_iter` / `<prefix>_next` (DESIGN NOTE, revision 3)

**Revision 3** (lane `iterrev3`, 2026-10-16, from main `37086a1db`, abi 78) answers the
two-critic panel r5 (`docs/dev/reviews/2026-10-16-r5-findall-iter-rev2.md`, IC1-IC9 and
IT1-IT15, all accepted except IT4, which D165 addendum 3 rejects). Read §R3 first. It applies
D165 addendum 3 (no per-call owner check: misuse across artifacts is undefined) and the
manager's ruling on IT3/IC3 (the batch region comes through the iterator's own setter, and
`<prefix>_buffers` is untouched). It moves S and the storage buffer to I2, where the first
row is held and the C compiler can check it. §3.4a and §0.3 are conditional on Q-I1, which is
still open. Revision 3 measured one thing: the struct sizes and the fast path's code, on a
hand-C probe at gcc 15.2 (§1.1).

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

## R3. What revision 3 changed (panel r5 finding → section)

| finding | disposition | what changed | where |
|---|---|---|---|
| IT4 | REJECTED by D165 add. 3 | `owner`, its compare and IT4's setter store are deleted. Handing an iterator (or its buffers) to another artifact's `next` is UNDEFINED, stated in the spec next to subject immutability. S931 and the foreign-owner arm are withdrawn | §1.1, §1.2, §6.2, §6.8 |
| IT9 | dissolved by D165 add. 3 | no owner, so no third load: the BOUND fast path is one `cmpl $imm, (%rdi)` under `-fPIC` (measured, §1.1) | §1.1, §5.1 |
| IT3 + IC3 | ACCEPTED, manager's fix | the batch region is NOT in `<prefix>_buffers`. A new unprefixed setter `rx_iter_batch(&it, ptrdiff_t (*)[2], npairs)` takes it, so `emit_buffers_surface`, `<p>_no_buffers` and the bench's `shim.c` are untouched, `<PREFIX>_BATCH_ENTRY_SIZE` is not added, and F11 is withdrawn | §2.3, §6.1, §11 |
| IC3 (one event) | ACCEPTED | I1 ships the batch ABI (the setter, two fields, one option bit) UNCONDITIONALLY. The fill is a cell of the `iterate` row's `batch` column, set by the parity slot. Turning it on later is one cell and a mover census, never a second layout event | §2.3, §6.9 |
| IC2 | ACCEPTED: S DEFERRED to I2 | I1 ships no `st` and no `PCREC_ITER_STATE_SIZE`. S lands at I2 with the first held row, so check 2 (the C compiler) is live in the same commit as the literal it checks. S936, S937 and check 2 stop being UNREACHED | §1.3, §6.9 |
| IT7 | ACCEPTED | check 1 asserts `S >= max`, and the census reports the headroom | §1.3 |
| IT1 | ACCEPTED | bind writes every optional field (NULL / 0 when its bit is clear) and K into `nbatch`, then stores BOUND. The fill reads fields, never option bits | §1.2, §2.3 |
| IT2 | ACCEPTED | `__fill` begins with `if (rc_next != 1) end(rc_next)`. A counted-work cell (`tests/compound/loads_drv.c`'s instrument) is its detector | §2.3, §6.7, §6.8 |
| IT5 | ACCEPTED | the spec's §3.8 states that `s[0,n)`, the `vars` contents, the bound descriptor and the batch region must not change while the iterator is live; a violation is undefined | §1.2, §6.2 |
| IT6 | ACCEPTED | §3.4a and §0.3 are CONDITIONAL on Q-I1, with the per-logical-search reading as the design of record pending the ruling, and what changes under the literal reading | §0, §3.4, §3.4a, §10 |
| IT8 | ACCEPTED | a setter on an ENDED iterator is a no-op (the sticky `rc` survives); it poisons only a BOUND or unknown header | §1.1 |
| IT10 | ACCEPTED | STEP's destination is always `NCAPS` pairs (a local of `NCAPS` pairs when `caps` is NULL at K = 1) | §2.1 |
| IT11 | ACCEPTED | `it.lo` is defined only after the iterator has ENDED (the failing search's start); before that it is unspecified | §3.4, §6.2 |
| IT12 | ACCEPTED | bind's checks run in `_search`'s prologue order (match_api.md §9.4¶4: the boundary guard first), from the one prologue emitter both entries use | §1.2 |
| IT13 | ACCEPTED | `reports_empty` is the minimum REPORTED width = 0, from one analysis, not a list | §3.3 |
| IT14 | ACCEPTED | filed as U16 with trigger "`DEF_NEWLINE_CONV` gains a producer" | §9 |
| IT15 | ACCEPTED | the mover census counts refusal-set and engine-stamp changes beside the text | §6.4, §6.7 |
| IC1 | ACCEPTED | one plant and one population floor per residual twin, the `-fPIC` build named, the check placed in `make test-codegen` | §2.4, §6.7, §6.8 |
| IC4 | ACCEPTED | every "one combinator emitter" sentence is marked as depending on E0 | §0, §2.1, §8.2 |
| IC5 | ACCEPTED | a mirror plant flips split's `shared` meter cell; the engine of every budget cell is stated | §6.8 |
| IC6 | ACCEPTED | every detector names its target; the ASan cells are built inside `make test`'s own section | §6.7, §6.8 |
| IC7 | ACCEPTED (regression-only) | give-up identity under batching is stated as a REGRESSION control: libpcre2's `match_limit` counts a different unit, so no independent oracle exists | §6.7, §7 |
| IC8 + F12 | ACCEPTED | stage ids are qualified across documents. `compound_entries.md` is not edited here; §11 F16 is the hand-off list for its revision 4 | §6.9, §11 |
| IC9 | ACCEPTED | F9 corrected: `rx_buffers` in D165 add. 2 is the example prefix, not a different type | §11 |
| F13 (itcrit2) | ACCEPTED | F13's `compound_entries.md` claim removed; `docs/design/CLAUDE.md`'s revision 1 entry and the lanes index annotated | §11 |
| sabotage ids | ACCEPTED | existing ids kept (S931 withdrawn, retired). New rows are PROPOSALS P-i..P-q, unnumbered; the next free id is S1035 and the manager allocates | §6.8 |
| NEW-DATASET (UNREACHED rows) | ACCEPTED, dissolved | with S at I2, no row ships UNREACHED at I1; S936/S937/check 2 are I2's landing bar | §1.3, §6.9 |
| UNLOCKS | ACCEPTED | twin-forwarding as a general check (U17); a debug-only misuse check (U18) | §9 |

Revision 3 also corrects one revision-2 number. `sizeof(rx_iter)` at revision 2's layout is
**152 B**, not 160 B (revision 2 counted 96 B of fixed fields; there are 88). Revision 3's
layout measures 96 B at I1 and 160 B at I2 (§1.1).

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

Sabotage ids in §6.8: revision 1's S923-S942 are kept as labels; the new rows (proposed in
this revision as P-a..P-h) were allocated S1009..S1016 in order (P-a = S1009 ... P-h = S1016).

---

## 0. Answers first

1. **The struct** (§1). `rx_iter` is one fixed, unprefixed type in the shared ABI block.
   - Its first eight bytes are a STABLE PREFIX: a header word (tag, layout version, state
     FRESH / BOUND / ENDED, and option bits) and `rc`.
   - `rx_iter it = RX_ITER_INIT(s, n);` binds the subject (D165 add. 2 Q3). PREDICTED: three
     stores (`hdr`, `s`, `n`), never a memset. Revision 1 measured one store for its
     one-field init; the three-store figure is owed by the twin's `init_spellings` probe.
   - Optional inputs are setters on a FRESH iterator: `rx_iter_at(&it, pos)`,
     `rx_iter_vars(&it, vars, nvars)`, `rx_iter_batch(&it, batch, npairs)` (rev 3, the batch
     region) and `<prefix>_iter_buffers(&it, &bufs)` (typed, a header `static inline`).
   - **No owner check** (D165 add. 3). Passing an iterator, or the buffers bound into it, to
     another artifact's `next` is undefined, like changing the subject while iterating.
   - **S is derived** (§1.3) and **lands at I2** (rev 3). It is the maximum over every search
     path of 8 B × the DECLARED carried words of the rows held there at once (D167 add. 1
     A10). Today's declarations give 64 B. I1 holds no row, so I1's `rx_iter` has no buffer
     (96 B on LP64, measured); I2 adds it (160 B).
2. **The entries are controllers** (§2). `int <prefix>_next(rx_iter *, caps)` is an `iterate`
   row of `entry_rows[]` over a STATE part (`__enter`: bind or check), a STEP and a BATCH.
   - STEP = `first-nonzero(R@q, SEARCH@LOWER(adv(q)))` guarded by the retry bit, else
     `SEARCH@lo`. This is split's controller (`compound.md` §B.2) with a different guard.
     That both use ONE combinator emitter DEPENDS ON E0: today `emit_first_nonzero_search`
     (`src/gen/emit_compound.c:115`) is split-only, with no guard or meter column (IC4).
   - SEARCH is `__find(ITER)`. Its layout at `0` is revision 1's §2.2 table (inline, except
     the 233 label-table bodies, which stay one shared static function). At other positions
     the part-layout row decides (§2.2).
   - One exported call per match at most; with batching, one per K matches.
3. **Internal batching** (§2.3). With a batch region bound by `rx_iter_batch`, a call that
   finds the batch empty FILLS it: STEP runs until the region holds K matches or the
   iterator ends. Each later call copies one entry out. A code met during the fill waits in
   `rc_next` until the matches before it are delivered, and the call after them ends the
   iterator without searching again. Without a region, K = 1 and STEP writes straight into
   `caps`. **CONDITIONAL on Q-I1** (§10): IF the meter is per logical search (the leaning, the
   design of record pending the ruling), answers and give-ups equal the unbatched iterator's
   (§3.4a). Under D163 add. 6 Q1 read literally they do not, and §3.4a states what changes.
4. **Semantics** (§3), unchanged from revision 1 and RULED (D165 add. 2 Q1): PCRE2's global
   iteration, the NOTEMPTY_ATSTART retry gated by `reports_empty` (the minimum reported
   width is 0). 1,063 of 29,502 corpus pairs differ from today's §3.1.3 loop, and on 374 of
   those the loop reports a span no oracle reports.
5. **The error contract** (§2.1, §3.4). `next` returns 1 for a match, 0 otherwise. `it.rc`
   says why it stopped: 0 = done, a give-up code (D158) or a refusal (`PCREC_ERR_ITER`,
   `_UTF`, `_STARTPOS`, `_UNSET_VAR`) = it ended there. The ended state is sticky and costs
   nothing on later calls: the header moves to ENDED, so the one header compare routes every
   later call to the slow path.
6. **F-1's static twins** (§2.4). `__adv`, `__valid_upto` and `__var_valid` are the static
   bodies; the exported residuals forward to them; no internal call reaches an exported
   symbol, so nothing pays a PLT call under `-fPIC`. Folded into I1 (every artifact moves
   anyway). Each twin has its own plant and population floor, and the check compiles `-O2
   -fPIC` in `make test-codegen`.
7. **The kit seam** (§4), unchanged in shape: each storage row is a region of `st`, zero at
   bind, persistent across calls; M is `__find`'s mode parameter (R-20 requested). `st`
   exists from I2.
8. **The abi events** (§6). I1 is one pcrec abi event, after E0 and the zero-mover I0. It
   carries the shared block (with the batch setter, unconditionally), `_next`, the residual
   twins and the retry machinery. Whether the fill is emitted is one row cell, set by the
   parity slot. I2 adds `st`/S with the kit's row, in an event I2 has anyway.
9. **Questions for Frank** (§10): Q-I1, the meter's unit under batching and the retry, is
   still OPEN. Q-I2 and Q-I3 are settled (the typed buffers setter; the batch setter). Q-I4,
   the entry stride, stays in discussion with a leaning; it is answer-free.

---

## 1. The `rx_iter` layout

### 1.1 The struct (in the shared ABI block, beside `rx_ctx`)

At I1:

```c
#define PCREC_ERR_ITER (-10)  /* [FINDALL-NEXT] below PCREC_ERR_FLOOR: NOT a give-up -- the iterator was refused */

#define PCREC_ITER_LAYOUT      3u   /* bumps with any change to rx_iter's layout */
#define PCREC_ITER_TAG       (0x49540000u | (PCREC_ITER_LAYOUT << 8))
#define PCREC_ITER_FRESH     (PCREC_ITER_TAG | 0x01u)
#define PCREC_ITER_BOUND     (PCREC_ITER_TAG | 0x02u)
#define PCREC_ITER_ENDED     (PCREC_ITER_TAG | 0x03u)
#define PCREC_ITER_OPT_AT    0x10u  /* option bits, set by the setters on a FRESH iterator */
#define PCREC_ITER_OPT_VARS  0x20u
#define PCREC_ITER_OPT_IN    0x40u
#define PCREC_ITER_OPT_BATCH 0x80u
#define PCREC_ITER_STATE_MASK 0x0Fu

typedef struct rx_iter {
    uint32_t hdr;      /* STABLE PREFIX: tag | layout | state | option bits */
    int32_t  rc;       /* STABLE PREFIX: 1 live, 0 done, < 0 the code that ended it */
    uint32_t flags;    /* RX_ITER_F_RETRY, RX_ITER_F_CHECKED */
    int32_t  rc_next;  /* the code a batch fill met, delivered after the batch drains (§2.3) */
    const unsigned char *s;   /* bound at init */
    size_t   n;
    size_t   lo;       /* the next search position; never decreases */
    const rx_var *vars;       /* rx_iter_vars; NULL/0 after bind if not set */
    size_t   nvars;
    const void *bufs;         /* <prefix>_iter_buffers; NULL after bind if not set */
    ptrdiff_t (*batch)[2];    /* rx_iter_batch; NULL after bind if not set */
    size_t   nbatch;          /* as set: capacity in PAIRS; after bind: K, in matches */
    size_t   bhead, bcount;   /* the batch cursor: entries [bhead, bcount) are undelivered */
} rx_iter;                    /* I2 appends: union { unsigned char b[S]; uint64_t align_; } st; */

static inline rx_iter rx_iter_init(const unsigned char *s, size_t n)
{ rx_iter it; it.hdr = PCREC_ITER_FRESH; it.s = s; it.n = n; return it; }
#define RX_ITER_INIT(s_, n_) rx_iter_init((s_), (n_))

/* Setters: legal only on a FRESH iterator. On an ENDED one they do nothing, so the sticky rc
   survives. On anything else they poison the header, so the next call refuses with
   PCREC_ERR_ITER rather than rebinding silently. */
#define PCREC_ITER_SET_(it_, stores_, bit_) \
    do { if (((it_)->hdr & ~0xF0u) == PCREC_ITER_FRESH) { stores_; (it_)->hdr |= (bit_); } \
         else if ((it_)->hdr != PCREC_ITER_ENDED) (it_)->hdr = 0; } while (0)
static inline void rx_iter_at(rx_iter *it, size_t pos)
{ PCREC_ITER_SET_(it, it->lo = pos, PCREC_ITER_OPT_AT); }
static inline void rx_iter_vars(rx_iter *it, const rx_var *v, size_t nv)
{ PCREC_ITER_SET_(it, (it->vars = v, it->nvars = nv), PCREC_ITER_OPT_VARS); }
static inline void rx_iter_batch(rx_iter *it, ptrdiff_t (*b)[2], size_t npairs)
{ PCREC_ITER_SET_(it, (it->batch = b, it->nbatch = npairs), PCREC_ITER_OPT_BATCH); }
```

and, in each artifact's HEADER (not the shared block, because its argument type is the
artifact's own, match_api.md §10.2¶2):

```c
static inline void <prefix>_iter_buffers(rx_iter *it, const <prefix>_buffers *b)
{ PCREC_ITER_SET_(it, it->bufs = b, PCREC_ITER_OPT_IN); }
```

**Measured** (rev 3; `findall_iter/rev3/layout.c` → `rev3/out/layout.out`, gcc 15.2
`-O2 -Wall -Wextra`, LP64, no warnings; this section's struct and setters also compile clean
under `-fanalyzer`): `sizeof(rx_iter)` = **96 B** at I1 and **160 B** at I2 with S = 64. Revision 2's
layout is **152 B**, not the 160 B revision 2 predicted (it counted 96 B of fixed fields where
there are 88). The BOUND fast path `if (it->hdr != PCREC_ITER_BOUND)` compiles under `-fPIC`
to one `cmpl $imm32, (%rdi)` and a `jne`: one load, no GOT access.

The fields, and what revision 3 changed:

| field | storage class | why |
|---|---|---|
| `hdr` | FIXED, stable prefix | the iterator's own state machine (FRESH / BOUND / ENDED), not a misuse guard (D165 add. 3). ENDED makes stickiness free: the BOUND fast path is one compare, and an ended iterator fails it. The option bits record which setters ran, so init writes no optional field. **rev 3**: `OPT_BATCH`; LAYOUT 3 |
| `rc` | FIXED, stable prefix | done (0) and gave-up/refused (< 0) stay distinct after `next` has returned 0, at a fixed offset any layout can read |
| `flags` | FIXED | `RETRY` (the empty-match retry bit) and `CHECKED` (the once-per-iterator checks ran) |
| `rc_next` | FIXED | the pending code under batching (§2.3) |
| `s`, `n` | FIXED | bound at INIT (D165 add. 2 Q3) |
| `lo` | FIXED | the search position, monotone (D165 item 1). Defined to the caller only after the iterator ends (§3.4, IT11) |
| ~~`owner`~~ | removed | **rev 3** (D165 add. 3). It cost 8 B and, under `-fPIC`, a GOT load per call (IT9) |
| `vars`, `nvars` | FIXED | set by `rx_iter_vars`; NULL / 0 after bind otherwise (IT1) |
| `bufs` | FIXED | the `_in` frames and trail, for the iterator's searches (§2.3); NULL after bind otherwise |
| `batch`, `nbatch` | FIXED | **rev 3**: the batch region, from the iterator's own setter, NOT from `<prefix>_buffers` (IT3/IC3) |
| `bhead`, `bcount` | FIXED | the batch cursor (§2.3) |
| `st` | BUFFER, **from I2** | every storage row (§1.3). Absent at I1, where no row is held (IC2) |

**Why setters and not an init macro per combination.** Revision 1 already had `RX_ITER_INIT`
and `_AT`, and needed `_VARS` and `_AT_VARS`; D165 add. 2 adds `_IN`, and revision 3 a batch.
That is 2⁴ spellings for four independent options. The setters are one rule (an option is a
setter on a FRESH iterator, recorded by a header bit), and a fifth option joins without
touching the others. A setter is `static inline`, so it is no exported symbol and no call.
Init still writes no optional field, so D165 item 5's "never a memset" holds.

**Why the batch setter is unprefixed.** The region's element type is the one every artifact's
`caps` already has, `ptrdiff_t[2]`. The capacity is in PAIRS, so the caller sizes it with the
macro it already uses for `caps` (`ptrdiff_t b[64 * RX_NCAPS][2]`), and the artifact divides
by its own `NCAPS` once, at bind. No per-artifact sizing macro is needed (IC3's stamp-inventory
concern), and no per-prefix setter.

### 1.2 Binding (D165 add. 2 Q3: bind at init)

- **INIT.** `RX_ITER_INIT(s, n)` writes `hdr = FRESH`, `s`, `n`. The setters add `lo`,
  `vars`, `bufs`, `batch` and their option bits.
- **FRESH → BOUND, at the first call** (`__enter`). In this order:
  1. **Normalize every optional field** (IT1). When a bit is clear, bind writes the field's
     neutral value: `lo = 0` without `OPT_AT`; `vars = NULL, nvars = 0` without `OPT_VARS`;
     `bufs = NULL` without `OPT_IN`; `batch = NULL` without `OPT_BATCH`. Then K goes into
     `nbatch`: `K = (batch != NULL && nbatch / NCAPS >= 2) ? nbatch / NCAPS : 1`. That is at
     most five stores, once per iterator. From here on nothing reads an option bit, which is
     what lets bind store the bare BOUND word below.
  2. Set `rc = 1`, `rc_next = 1`, `flags = 0`, `bhead = bcount = 0`. From I2, zero the
     storage rows THIS artifact declares (never S).
  3. **Run the once-per-iterator checks in `_search`'s prologue order** (IT12): the startpos
     boundary guard on an `OPT_AT` start first, then the `-futf-check` validation, then the
     variables' validation. match_api.md §9.4¶4 fixes "the boundary guard first, then the
     check". Bind writes the guard and the check through the ONE prologue emitter every
     caller-startpos entry already uses, `pcrec_emit_startpos_guard`
     (`src/gen/emit_dfa.c:848`: the axis's guard, then `emit_utf_check`), and the variable
     check through the body's own (`emit_vm.c:12540`'s twin, §2.4). So a subject that is
     both mid-character at `pos` and ill-formed refuses with the code `_search`'s first call
     would give (`PCREC_ERR_STARTPOS`), under every value of the startpos-guard axis.
  4. Store `BOUND` (the option bits cleared).
- **BOUND, the fast path.** One compare: `it->hdr != PCREC_ITER_BOUND`. There is no owner
  compare (D165 add. 3).
- **Anything else** (ENDED, garbage, an uninitialized struct, a poisoned header, another
  layout) takes the slow path: ENDED returns 0 with no work; everything else sets
  `rc = PCREC_ERR_ITER` at the stable offset, moves the header to ENDED, and returns 0.
  This is the iterator's own state machine, not a misuse guard. An iterator whose header
  happens to read BOUND but was bound by another artifact is not detected.

**Misuse is undefined, not refused** (D165 add. 3; spec hunk §6.2). While the iterator is
BOUND, these are UNDEFINED, and nothing checks for them:
- passing it, or the buffers bound into it, to another artifact's `next`. PCRE2's precedent:
  `pcre2_match` does not check that the match data belongs to the code;
- changing `s[0, n)`, the `vars` contents, the bound `<prefix>_buffers` or the batch region
  (IT5). §3.4a's identity, the kit's cache (§4.1) and validate-once (§3.6) all rest on this.
  A strtok-style tokenizer that writes into the subject between calls is the case the spec
  must name: legal with today's loop, undefined with the iterator.

A debug-only check is filed as U18; none ships in the hot path.

**Copying** an iterator is legal at any point, as in revision 1: every field is
position-independent, and the kit says its state is too (D165 add. 1). A copy made while the
batch holds undelivered entries SHARES the batch region with the original, so the two copies
must not both continue (they would overwrite each other's batch). The spec hunk states this
as the batch region's lifetime rule: one live iterator per region.

### 1.3 S is DERIVED: the declared carried words (D167 add. 1 A10)

S is a public constant in the shared block, so changing it changes every artifact (an abi
event, D165 item 4). It is derived from the owners' declarations, never picked.

**S lands at I2, not I1** (rev 3, IC2). At I1 no row is held: `kit-find` arrives with I2
(R17-b″), `pair-hits` with I3 and `reseed-hint` is filed. Revision 2 shipped S = 64 B at I1
anyway, so every artifact's `rx_iter` would carry 64 B that no emitter uses, and every
detector on S was UNREACHED: S936, S937 and check 2 by declaration. Check 1 compared a
literal against a max computed from declarations that one lane writes on both sides, which
fails only if someone forgets to edit one of them (learnings §3, the shared-source failure).
The only independent control, the C compiler's `sizeof(struct <p>__iter_state)`, cannot
exist before a row is held. Revision 3 therefore defers S, and with it the `st` member,
`PCREC_ITER_STATE_SIZE` and `PCREC_ITER_STATE_ALIGN`, to I2.
- I2 is already a pcrec abi event (a kit byte move, D147), so `st` joins that event and adds
  no new one. It moves `PCREC_ITER_LAYOUT` 3 → 4 and `sizeof(rx_iter)` 96 → 160 B, both in
  the shared block that I2's abi ritual re-pins anyway.
- In I2's commit, S's literal, the first held row, the artifact's `_Static_assert` (check 2)
  and the zeroing (S936) all land together. Each detector reaches its site the day the thing
  it checks exists.
- D167 add. 1 A10's "re-derived at the iterator's abi event" reads, under this deferral, as
  "at the event that first holds a row", which is I2. The derivation and the sizing policy
  below are unchanged; only their first event moves. This is a reading of A10, flagged to the
  manager.
- The alternative IC2 offered was a real I1 control: a synthetic row forced into one test
  artifact. That would build a test-only declaration path (a compiler knob) to check a buffer
  nothing uses yet (D77), so it is not taken.

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
- S is derived AT I2 from the declarations then current. If the kit's declaration or K5's
  status moves before I2, I2 takes the new value with no extra event.
- A row that RETIRES after I1 (K5) shrinks the max. Shrinking S is also an every-artifact
  abi event, and it buys 16 B of caller stack. The leaning is to shrink only when another
  abi event already moves the shared block, never as its own event; until then S keeps 16 B
  of headroom that no row uses, and the census (check 3) reports it. Check 1 is `>=`
  (IT7), so the build does not fail at K5's retirement.

**The checks (independent controls)**, revision 1's three, re-sourced:
1. **pcrec's derivation check.** At pcrec's build, a `_Static_assert` holds
   `PCREC_ITER_STATE_SIZE` (the literal in the emitted shared block) **at least** the max the
   declarations compute (IT7: revision 2 asserted equality, which would fail the build the
   day K5 retires while U14 keeps 64 B). A declaration that outgrows S fails pcrec's build,
   naming the row. The headroom `S − max` is reported by check 3, not asserted. This check
   shares its source with the declarations, so it is the REGRESSION half; check 2 is the
   independent one.
2. **The artifact's own check, by the C compiler.** An artifact holding at least one BUFFER
   row emits `struct <p>__iter_state` with one member per held row (unions for alternatives,
   sums for concurrent rows), in the rows' real C types, and
   `_Static_assert(sizeof(struct <p>__iter_state) <= PCREC_ITER_STATE_SIZE && _Alignof(...) <= PCREC_ITER_STATE_ALIGN, ...)`.
   The expectation (S) and the subject (the compiler's layout) share no source. It lands in
   I2's commit with the first held row, so it is never UNREACHED.
3. **The census** (`tests/findall/`'s census step in `make test-findall`, I2 onward). Every
   corpus artifact's `sizeof(<p>__iter_state)` against S, reported as headroom, with a floor
   per row on the number of artifacts holding it (K35). The `pair-hits` floor is the
   67-pattern population, from I3.

**Alignment.** 8: no row keeps a vector register (D165 add. 1). A row needing 16/32/64
raises `PCREC_ITER_STATE_ALIGN`, an abi event.

---

## 2. The entries, as compound controllers

### 2.1 `<prefix>_next` is an `iterate` row of `entry_rows[]`

```c
int <prefix>_next(rx_iter *it, ptrdiff_t (*caps)[2]);
```

- **Returns 1** when a match was found. Then `caps` (if non-NULL) holds `<PREFIX>_NCAPS`
  pairs, exactly as `<prefix>_search` would write them for this match.
- **Returns 0** otherwise. `it->rc` says why: 0 = done; a give-up code (`[PCREC_ERR_FLOOR,
  −2]`, D158) or a refusal (below the floor) = it ended there. Every later call returns 0
  with no work (sticky, §1.2). RULED (D165 add. 2): a three-valued return was rejected
  because `while (next(...))` would spin on a give-up read as a match.
- **`caps` may be NULL.** The span still reaches the advance through the step's own local
  (or the batch entry). STEP's destination is ALWAYS `<PREFIX>_NCAPS` pairs (IT10): at
  K = 1 with NULL `caps` it is a local `ptrdiff_t[NCAPS][2]`, so STEP does the same capture
  work, and charges the same meter, whether its destination is `caps`, the local or a batch
  entry. A one-pair local would make K = 1-with-NULL and batched runs do different work.
- **The signature is uniform** (no subject, no vars), so `rx_entries.next` ([V-E], [ART-MGR]
  S1) is `int (*)(rx_iter *, ptrdiff_t (*)[2])` for every artifact, with no trampoline.

**As a row** (`compound_entries.md` §4.1's `EntryRow`; the field values are this design's):

```
next  = iterate( STATE = __enter ;  STEP ;  BATCH = the region rx_iter_batch bound )   mode ITER
        the row's batch column: fill | off   (one cell, set by the parity slot, §2.3, §6.9)
STEP  = first-nonzero( R @ q ,  SEARCH @ LOWER(adv(q)) )   asked only if RETRY is set (q = lo)
        else SEARCH @ lo
SEARCH = __find(ITER)            the artifact's search body: locate-then-finish, or the
                                 compound controller on a compound artifact
R      = verify-at q under the NOTEMPTY_ATSTART predicate (§3.3): the DFA's notempty root, or
         the VM's guarded attempt; on a compound, F's bounded attempt under the root
_search = locate-then-finish = __find(ONESHOT)                                mode ONESHOT
```

- **`first-nonzero` is split's combinator, guard included.** `compound.md` §B.2 asks F "only
  if the floor can be live" and otherwise asks Q at `x`; on F's NOMATCH it asks Q at
  `LOWER(next_pos(f))`. The retry is the same expression with the retry bit as the guard:
  RETRY clear → SEARCH at `lo`; RETRY set → R at `q`, and on R's NOMATCH, SEARCH at
  `LOWER(adv(q))`. R's give-ups PROPAGATE by the call-site code table (§A.14 rows 3-5, 7),
  which is revision 1's "the retry's give-ups are its own". **That one combinator emitter
  serves both is a design that DEPENDS ON E0** (IC4). Today `emit_first_nonzero_search`
  (`src/gen/emit_compound.c:115`) is split-only and has no `guard` or `meter` column, and
  `src/` has no `iterate`, `CompComb` or `entry_rows`. If E0 lands without them, I1 adds the
  two columns to that emitter in its own commit, and the retry is its second row.
- **The guard is the one per-row difference, and the meter is the second, CONDITIONAL on
  Q-I1** (IT6; §10). Split's F and Q serve one logical search, so they share one meter
  (D163 add. 6 Q1). Under the design of record, pending the ruling, R and SEARCH are two
  logical searches, as pcre2demo makes two `pcre2_match` calls, so each gets a fresh meter,
  and the combinator row carries a `meter` column (`shared` for split, `per-operand` for the
  retry). If Q-I1 is ruled the literal way, the retry's cell is `shared` too, the column has
  one value, and it is not added.
- **`iterate` is the new combinator.** It owns three things: the STATE part's bind/check
  (`__enter`), the delivery (one result per call, from the batch or straight from STEP), and
  the fill loop (§2.3). It writes no search logic. Its first client is `next`; `next_n`
  (HELD) would be a second `iterate` row with a span sink (§2.3).
- **Nothing in this chain is a second exported call** (D165 item 5). `_next` does not call
  `_search`. `__find`, `__enter`, the STEP body and the residual twins (§2.4) are static.

**The emitted shape** (the twin's, `findall_iter/twin/mktwin.py`, re-spelled for binding at
init, batching and no owner; the twin's re-run is owed, §5.3). Where the `batch` cell is
`off`, `__deliver` and the cursor test are not emitted and `__fill` is STEP once:

```c
int <p>_next(rx_iter *it, ptrdiff_t (*caps)[2]) {
    if (__builtin_expect(it->hdr != PCREC_ITER_BOUND, 0))
        if (!<p>__enter(it)) return 0;           /* bind; or refuse; or ENDED */
    if (it->bhead < it->bcount)                   /* deliver a buffered match */
        return <p>__deliver(it, caps);
    return <p>__fill(it, caps);                   /* §2.3: STEP once (K = 1) or up to K */
}
```

### 2.2 The find body's layout comes from the part-layout row

`compound_entries.md` revision 3 makes `__find` a SUBJECT part of the part-layout dial row
and fixes how this design's own rule survives:

- **At position `0` (the default), revision 1's two-row rule is KEPT as the `0` cell's
  content** (that note's invariant I4 and §3.8). The rule:

  | row | when | `__find` linkage at `0` |
  |---|---|---|
  | `shared` | the body defines a static label table (the DFA attempt route: 233 of 4,243 byte, 232 of 4,254 utf8 corpus artifacts, `twin/out/label_census.out`) | `static noinline`; `_search` tail-jumps, `_next` calls |
  | `inline` | otherwise | `static inline always_inline`; a copy in each entry |

  The measurements behind it are unchanged (revision 1 §2.2, `twin/out/run_twin_inline.out`):
  `_search`'s instructions are identical to today's on five of eight DFA twins once its body
  moves into `__find`; the cost is `.text` (`_next` 433-1,079 B inline, 321-666 B shared).
- **At a non-zero position** `__find` goes through `compound_entries.md` §3.4's tables: P2
  (`copyable(part)` false) gives the label-table body `static noinline noclone` at every
  position, which is the `shared` row above with `noclone` added; otherwise the position's
  row (P4/P6 shared at `−2`/`−1`, P7/P8 at `+1` by `θ_hot`, P9 inline at `+2`).
- **`__find`'s in-edges and ranks** (`compound_entries.md` §3.2): from `_search` R2 and from
  the STEP inside `_next` R2 without batching. With the batch fill (§2.3) the STEP runs in a
  loop whose trip count pcrec does not bound (the caller's region size does), so `__find`'s
  in-edge from `_next` is **R3**. The fill loop is in every `_next` while the `iterate`
  row's `batch` cell is `fill` (K is a run-time value), so the edge is R3 on every artifact
  then, and R2 while the cell is `off` (§2.3, §6.9). `compound_entries.md` §3.8 lists this
  edge as HELD;
  revision 2 designs it, which gives that note's `−2`/`−1` pair its first designed witness:
  at `−1` row P5 inlines an R3 part, so `__find` is inlined at `−1` and shared at `−2`.
  The parity gate's `I_shared` arm is then the `−2` layout alone.
- **`__enter`, `__deliver`, `__fill`, the STEP body**: one caller each (`_next`), so row P3
  keeps their `0` layout at every position. The retry R is a body inside STEP with no symbol
  of its own, so it is not a part (`compound_entries.md` §3.8).
- **The `I_shared` trigger** stays as revision 1 stated it, now `compound_entries.md` U1's
  trigger: if the parity gate's `I_shared` arm is within the noise floor of `I`, promoting
  "shared for every body" to the `0` cell is a ruled diff of THIS design.
- **M (the mode) folds where `__find` is inlined** and is one branch per call where it is
  shared (§4.2; `compound_entries.md` §3.5).

### 2.3 Internal batching in caller memory, through the iterator's own setter (D165 add. 2 Q2)

Frank's reframing: "the batching was in my mind an internal thing ... a way to get rid of the
per call overhead by caching the results internally (say at the compound function level) and
then providing them with next calls", with the results in the `_in` memory ("_in versions
provide memory. perhaps the buffered results live there?").

**The region (rev 3: the manager's ruling on IT3 + IC3).** The batch is caller memory, as
D165 add. 2 ruled, but it comes through the iterator's own setter,
`rx_iter_batch(&it, ptrdiff_t (*batch)[2], size_t npairs)` (§1.1). It does NOT become a third
region of `<prefix>_buffers`. Revision 2's extension of the descriptor had three costs the
panel found, and the setter has none of them:
- **A silent hazard for existing callers** (IT3). Callers that fill the descriptor member by
  member would leave new fields indeterminate, with no warning: the pcrec-bench shim
  (`testees/pcrec/shim.c:1728,1759`) and `docs/dev/optloop/artrev/A09/tools/budget_main.c:17`.
- **Moved bytes on every artifact** (IC3). `emit_buffers_surface`
  (`src/gen/emit_dfa.c:2546-2602`) writes the struct and its comment into every header and
  `.c`. `emit_vm.c:13826`'s positional `<p>_no_buffers = { (void*)0, 0, (void*)0, 0 }` would
  have warned under `-Wmissing-field-initializers` in every frameless VM artifact.
- **A sizing macro beside the stamps** (IC3). `<PREFIX>_BATCH_ENTRY_SIZE` would have moved
  the stamp inventory and §10.4's "five macros" count. With the capacity in pairs it is not
  needed (§1.1).

With the setter, `<prefix>_buffers` and its `_in` callers are untouched, and F11 is withdrawn
(§11). The region's lifetime rule attaches to the object it governs, the iterator.

- `<prefix>_iter_buffers` (Q-I2, kept) binds the frames and trail. The iterator's searches run
  on them as `_search_in`'s do, so the iterator gets `_in`'s depth with no `_next_in` entry.
- `rx_iter_batch` binds the results. The two setters are independent: either, both or neither.
- **Lifetime.** The batch region is NOT scratch while an iterator is bound to it. It must
  outlive the iterator's use, the caller must not read or write it while the iterator is live,
  and two live iterators must not share it (§1.2's copy rule). A violation is undefined (§1.2,
  spec §3.8).
- **Stride: full captures per match** (Q-I4). Each entry holds `<PREFIX>_NCAPS` pairs, so a
  caller passing non-NULL `caps` gets exactly what the unbatched `next` writes. On a DFA
  artifact `NCAPS` = 1, so an entry is one span. K = `npairs / NCAPS`, computed once at bind
  (§1.2); a region smaller than two entries is K = 1. The caller sizes K, so S does not
  constrain captures (D165 add. 2).

**The fill and the delivery** (the `iterate` combinator's two halves; `K = it->nbatch` after
bind, `rc_next` = 1 while nothing is pending):

```
fill(it, caps):
    if it->rc_next != 1:                -- IT2: a code is pending and the batch is drained
        end with rc = rc_next; return 0     (no STEP; the K = 1 iterator ended here too)
    K   = it->nbatch
    dst = (K == 1) ? (caps ? caps : local[NCAPS]) : batch[0]
    i = 0
    while i < K:
        r = STEP(it, dst_i)            -- same code, same lo, a fresh meter (§3.4a, Q-I1)
        if r == 1: i += 1; continue
        it->rc_next = r; break          -- 0 (done) or a code
    if K == 1: (i == 1) ? return 1 : end with rc = rc_next, return 0
    it->bhead = 0; it->bcount = i
    if i > 0: return deliver(it, caps)
    end with rc = rc_next; return 0

deliver(it, caps):
    copy batch[bhead] to caps (if non-NULL); bhead += 1; return 1
```

- **A drained batch with a pending code ends without searching** (IT2). Revision 2's fill had
  no such test. The call after the last buffered match found `bhead == bcount`, called the
  fill, and re-ran the failed (or exhausted) search with a fresh meter before ending. The
  answer was the same, because the search is deterministic, but it cost a full budgeted
  search that K = 1 never pays, and it contradicted revision 2's own "the NEXT call ends".
  Its detector is a counted-work cell (§6.7) with its own plant (§6.8 P-i).
- **No batch region, or a region of fewer than two entries, is K = 1**: STEP writes straight
  into `caps` (or the local), and no copy happens. That is the unbatched iterator, the
  degenerate case of the same loop, not a second path. Revision 1's design is exactly this
  case.
- **The `batch` cell** (§6.9). The `iterate` row's `batch` column has one cell for every
  artifact: `fill` emits the loop above; `off` emits `fill` as one STEP with K = 1, no
  `__deliver` and no cursor test, and bind still accepts `rx_iter_batch` (K is forced to 1).
  The answers and the caller's code are the same under both cells (§3.4a), so the parity slot
  can set the cell without moving the ABI.
- **Per match**, a batched call that finds the batch non-empty costs the one header compare,
  one cursor compare and one copy of `NCAPS` pairs. The search work moves into the fill, one
  exported call per K matches.
- **Over-fill is the caller's choice.** A caller that stops consuming after a few matches has
  paid for up to `K − 1` searches it never reads. The caller sizes the region (a "first three
  matches" caller passes a small one or none). pcrec picks no K, so there is no tuning
  constant here (memory `pcrec-suspect-tuning-constants`).
- **The kit's carried rows** see the fill's steps as consecutive calls: `lo` is monotone
  across them, which is the condition the kit's cache pays on (D165 add. 1).

**The public `next_n` stays optional and HELD.** Revision 1 designed and twinned it
(`size_t <prefix>_next_n(rx_iter *, ptrdiff_t (*out)[2], size_t k)`, spans only,
392-1,286 B `.text`, answer-identical to `next` in the twin). D165 add. 2 makes it "an
optional extra, not the mechanism". Under revision 2 it is a second `iterate` row whose sink
is the caller's `out` instead of the bound batch. Both it and the internal fill are timed in
the parity slot (§5.3): the fill's result sets the `batch` cell; `next_n`, a new exported
symbol, enters I1 only if its `N64` arm wins there, and is otherwise filed (U1).

### 2.4 The residual twins (D163 add. 7 Q5; `compound_entries.md` F-1)

`compound_entries.md` F-1: B4's compound controller calls the exported `<p>_next_pos`
(`emit_compound.c:129`), and under `-futf-check` P's prologue calls the exported
`<p>_valid_upto`. Under `-fPIC` both are PLT calls on every compound search. Revision 1
already gave `next_pos` a static twin (`__adv`) for the iterator alone. Revision 2 makes it
the general rule for the residual leaves, applied in I1, which moves every artifact's text
anyway:

| residual (exported, unchanged contract) | static twin | internal callers after I1 |
|---|---|---|
| `<p>_next_pos` | `<p>__adv` | STEP's advances (§3.1); the compound controller's `LOWER(next_pos(f))` |
| `<p>_valid_upto` | `<p>__valid_upto` | `__enter`'s once-per-iterator `-futf-check` (§3.6); every `-futf-check` entry prologue, the compound's included |
| `<p>_var_valid` | `<p>__var_valid` | `__enter`'s once-per-iterator variable check (§3.7); the `_search` prologue of a var-bearing artifact |

- **One emitter writes each body once**, as the twin, and the exported residual is
  `return <p>__twin(args);` (`compound_entries.md` W1's forward shape: an unchanged argument
  list compiles to `jmp`). The two cannot drift.
- **`noclone` on the twins**, under `__has_attribute` (K24's spelling). `compound_entries.md`
  F-3 found gcc partially inlining `_valid_upto` into a `.part.0` clone under `-futf-check`,
  K24's shape on a residual. The twins' layout at non-zero positions is the part-layout
  row's (they are subject parts after I3, `compound_entries.md` §3.1).
- **Not applied here**: the wrapper edges (`_search_in` → `_search` and the DFA `rev-end`
  tie's `SEARCH → MATCH`). Those are `compound_entries.md`'s wrapper step (its I3, "the
  first live cell diff for the wrappers"), so I1 does not grow their scope.
- **Movers**: every artifact moves at I1 anyway. The internal call targets move on three
  populations, one per leaf: the compound artifacts' `LOWER(next_pos(f))` (97 corpus, bench
  0); every `-futf-check` entry prologue (`emit_utf_check`, `src/gen/emit_dfa.c:809`,
  called from the caller-startpos prologue at `:848`, inside and outside the compound
  emitter); and every var-bearing `_search` prologue (`src/gen/emit_vm.c:12540`). The
  `_var_valid` seam entry exists only under an encoding with a `PCREC_ENCE_VAR_VALID` row
  (today `utf8`, `src/enc/enc_utf8.c:523`), so its population is the utf8 var-bearing
  artifacts.
- **Check** (IC1: one twin is not the family). No relocation from inside an artifact's object
  to one of its own exported residuals. The tool reads `objdump -dr`, looking for
  `R_X86_64_PLT32 <p>_next_pos` / `_valid_upto` / `_var_valid` from any function of the
  same artifact, and checks it against the artifact's own exported symbols (`nm`).
  - **The build.** Each artifact is compiled `gcc -O2 -fPIC -c` with default visibility.
    Under `-fPIC` an exported function is interposable, so gcc may not inline it into a
    caller and every internal call to it leaves a relocation. Without `-fPIC` gcc may
    inline the exported leaf and leave nothing to find, so the check would pass whether or
    not the twin exists. The `-fPIC` compile is the check's precondition, not an option.
  - **The home.** A new script `tests/codegen/run_residual_twins.sh` in `make
    test-codegen` (part of `make test`). It follows the precedent of `run_codegen_tests.sh`'s
    `[LOSS-REVIEW c1]` section, which already compiles fixtures `-O2 -fPIC` and reads the
    object.
  - **Population floors, one per leaf** (K35), each counted from the object and not from
    the pattern list: (a) `_next_pos` callers = the compound corpus artifacts, floor 97;
    (b) `_valid_upto` callers = every `-futf-check` artifact the script builds, which are
    `tests/utfcheck/`'s patterns and `tests/compound/split.rxt`'s `-futf-check` blocks;
    (c) `_var_valid` callers = the utf8 var-bearing blocks of `tests/vars/`. Each floor is
    pinned at I1's census. If (c) counts 0 on the corpus, the script carries its own fixture
    (one utf8 `${name}` pattern), so that floor is never vacuous.
  - **Plants, one per leaf** (§6.8): S1012 (`_next_pos`, kept) and the new proposals P-j
    (`_valid_upto`) and P-k (`_var_valid`). Each makes the emitter call the exported symbol
    at one internal site. All three are answer-equivalent, so each detector is this
    structural check.

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

`lo` is only ever written by STEP (§2.1), and every write is strictly greater than the previous
match's start: `__adv` returns a position `> pos`. The retry keeps `lo == q`, then advances
past q in the same call when the retry fails, so it never repeats. `lo > n` ends the iterator
(`rc = 0`). So `lo` is monotone non-decreasing (D165 item 1) and the iterator terminates.
A batch fill is a sequence of STEPs, so the argument holds across a fill unchanged.

### 3.3 NOTEMPTY_ATSTART: the iterator matches PCRE2's global iteration (RULED, D165 add. 2 Q1)

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

**The gate: `reports_empty`, a new E1 fact.** "Can the artifact REPORT an empty span": the
minimum REPORTED width is 0 (rev 3, IT13). It is ONE analysis over the reported span, not a
list of constructs. On today's constructs it evaluates to "nullable OR the pattern holds
`\K`", because `\K` is the only built construct that moves the reported start. A future
construct that changes the reported span joins without a new term, the unbuilt
`(*ACCEPT)` (`src/parse/mod_verbs.c:141`) for one. Its trigger is any module that changes
the reported span; the analysis's own sabotage is the census below, read as a control.
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
18.2%). Elsewhere STEP's `first-nonzero` has no R operand (the row degenerates to
`SEARCH@lo`, no guard emitted), and the iterator is §3.1.3's
loop exactly (twin: 35 cells, `I == L`). A sharper structural fact, `empty_pref` ("some empty
path precedes a non-empty path in priority order", false for `a*`, `a|`, `(a|)`), would arm
only patterns that can diverge. It is FILED as unlock U11, with this census as its control:
a pattern it marks false must never diverge. Its trigger is a measured cost of the futile
retry on a gate-true, non-diverging pattern (one failing anchored attempt per empty match,
e.g. `a*` over `"bbb..."`).

**The retry, per route.** The retry is the operand R of STEP's `first-nonzero` (§2.1): an
anchored attempt at q under a NOTEMPTY_ATSTART predicate, asked only when the RETRY bit is
set. On R's NOMATCH the combinator relocates to `LOWER(__adv(q))` and asks SEARCH there,
which is pcre2demo's "advance one character and search on". R runs with its OWN meter, as
pcre2demo's retry is its own `pcre2_match` call (the combinator row's `per-operand` meter
cell, §2.1; CONDITIONAL on Q-I1). pcre2demo's advance after a failed retry steps over a
whole CRLF under the CRLF/ANY/ANYCRLF newline conventions. pcrec refuses newline verbs today
(`src/parse/mod_verbs.c:174-177`; `DEF_NEWLINE_CONV` is reserved, `docs/spec/registry.md:197`), so the
one-character advance is exact now. The newline-aware arm is filed as U16 (IT14).

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
  correct at any position. On a compound artifact STEP nests the two uses of the one
  combinator: `first-nonzero(R@q, first-nonzero(F@f, Q@LOWER(adv(f)))@LOWER(adv(q)))`, each
  with its own guard and meter cell.

### 3.4 `rc` and the give-up codes (D158)

- `it->rc` is 1 while live, 0 when done, and a code when the iterator ended in a give-up
  (`[PCREC_ERR_FLOOR, −2]`) or a refusal (below the floor: STARTPOS, UNSET_VAR, UTF,
  INTERNAL, ITER). It is sticky (§1.2: the header moves to ENDED).
- On the call that ends it, `caps` is untouched (§3.1¶4 holds per call).
- **One meter per LOGICAL search: the design of record, CONDITIONAL on Q-I1** (§10, still
  open with Frank). A logical search is what one `_search` call (or one `pcre2_match` call
  in pcre2demo's loop) would be: SEARCH at `lo`, or the retry R at q. Each gets the fresh
  budget a `_search` call gets, and the tiered default (§10.9) applies to each exactly as in
  `_search`. Inside one logical search, D163 add. 6 Q1 holds as ruled: a compound's parts
  all charge that search's meter. The two bullets below hold under this reading.
  - Hence: **on every logical search that is not a retry, the iterator gives up exactly
    where today's loop gives up**, same search, same code. The body is the same code at the
    same `lo`, and the carried rows of §1.3 are exact caches that move no attempt position.
  - The retry is NEW work, run only where the global semantics needs it. It is not an
    optimization, so D158's direction rule does not apply to it. Its give-ups are stated in
    the spec hunk as the retry's own.
- **Under batching, a code waits its turn.** A fill that meets a code after finding `i`
  matches stores it in `rc_next` and delivers the `i` matches first; the call after the last
  of them ends the iterator with `rc = rc_next`, without searching again (§2.3, IT2). So the
  caller sees the same sequence (the matches, then the code) as without batching (§3.4a). A
  code met before any match ends the iterator on the filling call.
- **`it.lo` is defined only after the iterator has ended** (IT11). Mid-batch, `lo` runs up to
  `K − 1` searches ahead of what the caller has seen, so before the end it is unspecified.
  After an end with `rc < 0` it is the failing search's start: the fill stops at the
  failure, and every buffered match before it lies below it. After `rc = 0` it is
  unspecified. The spec states it this way (§6.2) rather than adding an accessor.
- **A carried row that is an OPTIMIZATION** (the reseed hint, [OPT-HYB-RESEED-XCALL]) changes
  which positions the VM attempts, so D158 binds it. Its admission is GIVEUP1's direction
  check ([GIVEUP-DIFF]) before it lands (§9 U5).
- **After a give-up** a caller can deliberately skip on with a FRESH iterator and
  `rx_iter_at(&it, pos)`, but nothing resumes a gave-up iterator implicitly. PCRE2's demo
  stops the same way. On a VM artifact a `PCREC_ERR_FRAMES` give-up is retryable with larger
  buffers (§10.3¶3): a fresh iterator, `rx_iter_at(&fresh, it.lo)` (defined, because the
  first one has ended with `rc < 0`), bound to the larger `<prefix>_buffers`.

### 3.4a Batching is answer- and give-up-identical to K = 1, by construction, IF Q-I1 is ruled per logical search

**This section is CONDITIONAL on Q-I1** (IT6). Its step 2 needs each STEP to get a fresh
meter. That is the per-logical-search reading, the design of record pending Frank's ruling.
Under D163 add. 6 Q1 read literally (one meter per exported `next` call), a fill's K steps
share one budget. A fill then gives up where K = 1 does not: on the cell where each search
fits and their sum does not. Under that ruling the claim narrows to ANSWERS on every cell
where no give-up occurs. The give-up sequence then depends on K, which is D158's case (an
internal choice moving a give-up). S1010 and S1011 would invert their expectations, and the
batching-identity check (§6.7) would drop its give-up cells.

Claim, under the design of record: for every subject, the sequence of `next` results (each match with its captures, then
the final `rc`) is the same for every K, including no batch region.

1. The fill calls STEP, and STEP reads only `s`, `n`, `lo`, `flags` (RETRY), `vars`, the
   storage rows and its scratch (`frames`/`trail`). The delivery reads and writes only
   `bhead`, `bcount`, `rc_next` and the batch region, which STEP never reads.
2. So the j-th STEP of a fill sees exactly the state the j-th call's STEP would see at
   K = 1: the same `lo`, the same RETRY bit, the same carried rows. It is the same code with
   a fresh meter (§3.4), so it returns the same result.
3. The delivery hands the entries out in the order STEP wrote them, and `rc_next` only after
   the last. K = 1 is the case where every fill stops after one STEP.

What does differ is WHEN the work happens (up to `K − 1` searches ahead of the caller,
§2.3's over-fill) and which exported call pays for it, never what is answered. The check is
the batch arm of `run_iter_diff.sh` (§6.7): every pair at K ∈ {no region, 2, 3, 64}
against the global-loop oracle, plus the give-up cells, whose sequence must equal K = 1's (a
REGRESSION control, §6.7, IC7).

### 3.5 `\G`, `^`, and the start position

- **`\G` asserts at `lo`, the call's search start.** After a non-empty match that is the
  previous match's END (aligned, K75). During a retry it is q, the empty match's position.
  After a failed retry it is `__adv(q)`.
  - This is PCRE2's global `\G` (`assertions_design.md` §4.3), and the same as today's loop
    on every non-retry call.
  - `\G\w+` over `"ab ab ab"` stays a tokenizer: `(0,2)` then done (twin case `rg`, all
    cells `I == L == libpcre2`).
- **`^`/`\A` assert at absolute offset 0** (§3.1¶7), unchanged.
- **The first position.** A FRESH iterator starts at 0. One with `rx_iter_at(&it, pos)`
  starts at `pos`, which is checked ONCE at bind by the artifact's startpos guard. A mid-character `pos > 0` gives
  `rc = PCREC_ERR_STARTPOS` (§9.2), or is aligned forward once under
  `-fstartpos-guard=align` (D133).
- **No later call runs the guard**, because every `lo` the iterator computes is a character
  boundary (§3.1.3¶6, §9.5). So `next` emits no guard on the BOUND path, which saves one
  load and branch per call under utf8. Sabotage S935 plants the guard's removal at bind and
  is detected by an `rx_iter_at` mid-character cell.

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

- **Variables.** `rx_iter_vars(&it, vars, nvars)` records them in the iterator (§1.1).
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
  - Handing an iterator to the wrong artifact is the caller's error and undefined (D165
    add. 3, §1.2). No callout chain can make that hand-off, because no call chain carries
    the iterator.

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
- **Compound:** SEARCH is the controller (`first-nonzero(F, Q)`), whose parts are static,
  and STEP wraps it in the retry's `first-nonzero` (§3.3). Parts that hold rows get SUMMED regions (§1.3). F runs only where the floor can be
  live (`lo == 0` or `\G`), so in a find-all it runs at most at the first call unless P has
  `\G`.

### 3.9 Reentrancy (§5.3)

The artifact still holds no mutable state of its own; TS-1 and TS-2 are unchanged, since
`rx_iter_init` and the setters are `static inline` with no static object. The iterator is CALLER-owned
mutable state, like `caps`:
- any number of iterators may run concurrently, one thread each;
- two threads sharing one iterator is a data race in the caller;
- a callout that re-enters the same artifact's `next` uses its own iterator;
- a bound batch region belongs to one live iterator (§1.2, §2.3);
- one artifact's iterator handed to another artifact's `next` is undefined (D165 add. 3).

---

## 4. The kit seam (D157: facts only)

### 4.1 Where the kit's state lives

- **pcrec gives the kit:**
  - a REGION of `st`: an lvalue's text and its byte offset;
  - the region's guarantees: zero at the first use of an iterator; persistent across calls of
    the same iterator; `lo` monotone; the same unchanged `(s, n)` (bound at init, §1.2); one
    thread. The steps of one batch fill (§2.3) are consecutive calls in this sense.
- **The kit declares, per stateful form:** its carried WORDS (8 B each, D167 add. 1 A10) and
  alignment (`mf_result` / the form's row), and that ZERO is its fresh state (addendum 1:
  "zero-init + the same unchanged (s, n)"). Today's declaration is r17b_prime.md §6's 5
  words / 40 B (§1.3).
- **Zeroing.** From I2, when `st` exists (§1.3), pcrec's bind code zeroes the region's
  DECLARED bytes (40 today). It never
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
  and `next` passes ITER (the batch fill's steps included). It is the `mode` column of the
  entry's `entry_rows[]` row (`compound_entries.md` §4.1). In the inlined form the parameter is a constant at each call site,
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
  kit keeps it in one of its row's 5 words (r17b_prime.md §6: "the previous step span (8 B,
  H)"), and the mask's popcount is in its 24 B core.
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

| | today's loop (§3.1.3) | `next`, K = 1 | `next`, batched (per match, amortized) |
|---|---|---|---|
| exported calls | 2 (`_search`, `_next_pos`) | **1** | 1/K |
| entry checks | `startpos > n`; utf8 guard; `-futf-check` O(n); var check | one header compare (one load, measured `cmpl $imm, (%rdi)` under `-fPIC`); `bhead < bcount` where the `batch` cell is `fill`; `lo > n` | the same compare and cursor test per call; the step's `lo > n` per fill step |
| advance | the caller's two-arm expression + the `_next_pos` call | inlined `__adv` | inlined |
| result | written by `_search` into `caps` | written by STEP into `caps` | written by STEP into the batch; one copy of `NCAPS` pairs per delivery |
| per-iterator, once | — | bind (≈ 7 stores + ≤ 5 normalizing stores, IT1; from I2 the declared rows' zeroing); the guard/check/vars once | same |
| init | — | **3 stores** (`RX_ITER_INIT(s, n)`), PREDICTED; +2 or 3 per setter | same + the batch setter (3 stores) |

The per-call additions at K = 1 are one L1 load and one compare (the header), and the cursor
test where the `batch` cell is `fill`. Revision 1's per-call `(s, n)` compare is gone (binding
at init), and revision 2's owner compare is gone (D165 add. 3), which also removes the third
load IT9 measured under `-fPIC` (`movq <p>_info@GOTPCREL(%rip)`). The
iterator removes an exported call (a PLT call under `-fPIC`), the caller's advance
expression, the per-call utf8 guard and the O(n) validation per call. So parity or better is
the prediction on every cell at K = 1, and batching is predicted to amortize the remaining
exported call. Both predictions are UNMEASURED; the gate decides them.

### 5.2 Static internals

`__find`, `__enter`, `__deliver`, `__fill`, the STEP body, the residual twins `__adv`,
`__valid_upto`, `__var_valid` (§2.4) and, on `reports_empty` DFA artifacts, the notempty
root are static. The kit's bodies stay static (D88 add. 1). A compound's parts stay static.
The only new exported symbol is `<prefix>_next`, plus `<prefix>_next_n` if the parity slot
rules it in. `<prefix>_iter_buffers` is a header `static inline`, and `rx_iter_batch` and the
other setters are shared-block `static inline`s; none is a symbol.

### 5.3 The PARITY GATE (designed here; run later on a quiet box via main)

D165 item 5's named measurement: "iterator vs today's `_search` loop on dense tiny matches ...
at parity or better; worse is a finding, not a tolerance."

**Cells.** D165 names cells 1, 3 and 5. Cells 2, 4 and 6 are added because the body linkage
differs on them; cell 7 because batching has a cost there (§2.3's over-fill).

| # | pattern | subject | regime |
|---|---|---|---|
| 1 | `a` | `a` × N, N ∈ {64, 4 KiB, 1 MiB} | one match per byte, DFA memchr route |
| 2 | `a` | `"a"`, `"b"`, `""` (whole iteration, init included) | the one-byte subject; the empty subject |
| 3 | `\w+` | prose: rwcorpus's English prose class at 4 KiB and 1 MiB (sha-pinned, `worktrees/.corpus/`) | dense word matches, DFA `landing` route |
| 4 | `(a)` | `a` × 4 KiB | the VM route (captures), one match per byte |
| 5 | `\w+` | one-byte subject `"x"` | per-iteration fixed cost |
| 6 | `^a\|b` `--engine=dfa` (an `attempt`-scan artifact; confirm the stamp) | `b` × 4 KiB | the `shared` (static-label) body linkage |
| 7 | `a` | `a` × 4 KiB, the caller stopping after 3 matches | the over-fill cost of a batch the caller abandons (`B64` only) |

**Arms**, each a separate binary, interleaved:
- `L_old`: today's `_search` loop against the PRE-iterator build (main at I1's parent),
  §3.1.3's code verbatim.
- `L_new`: the same loop against the I1 build. Its gap to `L_old` is the cost the refactor
  puts on `_search` itself.
- `I`: `<prefix>_next` with caps, no batch region (K = 1).
- `B64`: `next` with a 64-entry batch region bound by `rx_iter_batch` (D165 add. 2 Q2's
  internal batching; the `fill` cell).
- `I_shared`: `__find` at its `−2` layout (the twin's `TWIN_SHARED=1` form; §2.2).
- `N64`: the public `next_n` with k = 64 (the optional extra; D165 add. 2 says both are
  timed).
- `A`: an A/A arm (`L_new` built twice) for the noise floor.

The pre-build run uses the TWIN for `I`, `B64`, `I_shared` and `N64`. The twin
(`findall_iter/twin/`) builds revision 1's `I`, `I_shared` and `N64` today (its `I0` arm,
"owner compare removed", is now the design itself and is dropped). It owes revision 3's
re-spelling (binding at init, the header-only compare, the setters, the IT2 test in the
fill) and a `B64` fill arm, and its answer driver (`drv.c`) gains a batched `I == B` check
before any timing. The post-build gate uses the built artifacts.

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
- `B64` is gated the same way (`B64 / L_old ≤ 1 + floor`) on cells 1-6, and it must beat `I`
  beyond the floor on the dense cells 1 and 3 to set the `iterate` row's `batch` cell to
  `fill` (§2.3, §6.9). Otherwise the cell is `off`. Either way the ABI is the same. Cell 7
  is reported as batching's stated cost, not gated.
- `N64` and `I_shared` are reported (the optional `next_n`; §2.2's `I_shared` trigger), not
  gated. The gate binds the `0`, `+1` and `+2` layouts; at `−1`/`−2` the gap is that
  cell's stated cost (D163 add. 7 Q3).

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

I1 bumps `PCREC_ARTIFACT_ABI` (78 at both revisions' bases; "the next number at landing").
Its readers, by grep at `ee01f4dbb` (revision 1; the line numbers are revision 1's, and the
commit re-derives them):

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
- the shared block (`rx_iter` without `st`, the `PCREC_ITER_*` constants, `PCREC_ERR_ITER`,
  `rx_iter_init`, `PCREC_ITER_SET_` and the three unprefixed setters, `rx_iter_batch`
  included, unconditionally);
- `_search`'s text (body moved into `__find`);
- `_next` (+ `_next_n` if ruled in), its declaration, and the `<PREFIX>_ITER_RETRY` stamp
  (§6.3);
- the residual twins and the exported residuals' forwarding bodies (§2.4);
- the header's `<prefix>_iter_buffers` (Q-I2), a byte-count reader's mover (the header's
  size);
- `_next`'s fill, per the `batch` cell the parity slot sets (§2.3). Neither value moves the
  ABI.

**NOT moved, by the manager's IT3/IC3 ruling:** `<prefix>_buffers` and its emitter
`emit_buffers_surface` (`src/gen/emit_dfa.c:2546-2602`, written into the header at `:3513`
and the `.c` at `:13757`), the frameless VM's positional `<p>_no_buffers` initializer
(`src/gen/emit_vm.c:13826`), §10.4's five sizing macros and the stamp inventory. Revision 2's
`<PREFIX>_BATCH_ENTRY_SIZE` is not added. A later lane that adds a region to
`<prefix>_buffers` meets all three sites; F11 records them.

**I2's layout event** (§1.3, §6.9): `st`, `PCREC_ITER_STATE_SIZE`/`_ALIGN`,
`PCREC_ITER_LAYOUT` 3 → 4 and `sizeof(rx_iter)` 96 → 160 B, inside I2's own abi event.

**On `reports_empty` artifacts only:** the retry machinery (VM accept guard / DFA notempty
root).

**Not moved:** `rx_info`'s fields. A batch-entry size field for an FFI consumer
(`rx_info.batch_entry_size`, as §10.4¶1 mirrors the frame sizes) is NOT added in I1: no
consumer has asked (D77); it is filed with [IFACE-PUSH].

### 6.2 Spec hunks (D80), each in I1's commit

- **`docs/spec/match_api.md`:**
  - §1¶2: the per-artifact symbol list gains `<prefix>_next` (`_next_n`); the residuals'
    forwarding to static twins is not caller-visible and needs no hunk.
  - §1¶5, ¶6: the shared block's type list gains `rx_iter`, `rx_iter_init` and the setters
    (`rx_iter_at`, `rx_iter_vars`, `rx_iter_batch`); the contract constants gain
    `PCREC_ITER_*` and `PCREC_ERR_ITER`. The per-artifact header list gains
    `<prefix>_iter_buffers`. No sizing macro is added (§2.3).
  - §2: the verbatim block.
  - §3¶1: the entry table.
  - **NEW §3.8 "The find-all iterator"**: the contract of §1-§3 above, in facts-only spec
    voice, numbered per docs/spec/CLAUDE.md. Three paragraphs are stated explicitly because
    the panel found them missing:
    - **What must not change while the iterator is live, and what is undefined** (IT5,
      D165 add. 3). From the first `next` call until the iterator ends, the caller must not
      change `s[0, n)`, the contents of the `rx_var` array bound by `rx_iter_vars`, the
      `<prefix>_buffers` descriptor bound by `<prefix>_iter_buffers`, or the batch region
      bound by `rx_iter_batch`. It must not pass the iterator, or a descriptor or region
      bound into it, to another artifact's `next`. Each violation is UNDEFINED; none is
      detected. The rule sits beside the copy rule (one live iterator per batch region).
    - **The batch region** (§2.3): `rx_iter_batch(&it, b, npairs)`, capacity in pairs,
      K = `npairs / <PREFIX>_NCAPS`, fewer than two entries = no batching, the region
      not scratch while bound. The answers do not depend on K (§3.4a, under the Q-I1
      ruling).
    - **`lo`** (IT11): `it.lo` is defined only after `next` has returned 0 with `it.rc < 0`,
      where it is the start of the search that ended the iterator. Otherwise it is
      unspecified.
  - §3.1.3: becomes "use the iterator". The hand loop stays as the one-shot alternative,
    with ¶9 corrected per §3.3's findings (not a subset; the CSV idiom; `\K`).
  - §3.1.2¶6: validate-once moves to the iterator.
  - §4: a `PCREC_ERR_ITER` row.
  - §4¶10: no row change. An iterator is never called from a generated call site.
  - §5.3: the iterator is caller-owned state.
  - §9.2¶6: the iterator meets the guard only at bind.
  - §10: an iterator bound to `<prefix>_buffers` uses `frames`/`trail` for its searches
    (no `_next_in` entry). §10.2's descriptor and §10.6's example are UNCHANGED (rev 3: the
    batch region is the iterator's, §3.8). Without `_in` memory the tiered default applies
    per logical search (conditional on Q-I1).
  - §4¶10: the call-site code table's iterator row: none. §3.8 states the meter's unit as
    Q-I1 is ruled: under the design of record, one meter per logical search (§3.4), beside
    D163 add. 6 Q1's per-exported-call wording.
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
- **`docs/spec/vars.md`:** variables bound in the iterator by `rx_iter_vars`.
- **`docs/spec/facts_listing.md`:** the `reports_empty` fact (I0).

### 6.3 Observability (D46)

- **`<PREFIX>_ITER_RETRY`** on every artifact: `"none"` (gate false), `"vm-guard"`, or
  `"dfa-root"`. It is one strategy choice per artifact, so it is a stamp. It joins
  match_api.md §6.3.2's inventory.
- **The held storage rows** go in `--emit-facts`' decisions section, not in a stamp, until a
  consumer asks (D77; [STAMP-REVIEW]).
- **The `batch` cell is not stamped.** It has one value for every artifact a given pcrec
  build emits, the abi number already identifies it, and no answer depends on it (§3.4a).
  A stamp waits for a consumer (D77).

### 6.4 Neutral to every length decision

The iterator's text is fixed scaffolding plus, on `reports_empty` DFA artifacts, a machine
role. The scaffolding is emitted inside the RQ-3 decision bracket (`src/core/sb.c`), so no
entry-shape knee, size term or cap reads it. It is excluded the same way SIMD's guarded bytes
are, so it moves no selection and no refusal set.

The notempty ROOT is a machine and counts like one (§3.3). It is the one size-visible part,
and its population is small: `reports_empty` DFA artifacts.

The check is the mover census of §6.7: every artifact's non-iterator text against I1's parent,
AND its refusal-set membership and `<PREFIX>_ENGINE` stamp (IT15). The notempty root counts
toward the caps on a `reports_empty` DFA pattern. Near a cap it can therefore make the
pattern refused, or move its engine, and a caller can see both. The census counts those
changes as movers; it does not read them as text.

The layout ATTRIBUTES on `__find` and the twins are the part-layout row's, and that row
renders them after every length decision (`compound_entries.md` I5), so a non-zero dial
position cannot move a length decision through this design either.

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

> pcrec abi N adds `<prefix>_next(rx_iter *, caps)` over `rx_iter it = RX_ITER_INIT(s, n)`,
> the find-all iterator (D165). Your
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
> Optional: a batched arm (`rx_iter_batch` with a 64-entry region), which is answer-identical
> and only faster where pcrec's `batch` cell is `fill`; `next_n` if it is built.

### 6.7 The checks (I1), each with its independent control

Every detector names the target that runs it (IC6). K35: a detector outside `make test` has
no population on the default run, so every I1 detector is placed inside it. That includes the
ASan cells: `tests/findall/` builds its handful of exact-size cells with
`-fsanitize=address` itself, so they do not wait on the opt-in `make asan`.

| check | subject | expectation, from | population (K35) | target |
|---|---|---|---|---|
| `run_iter_diff.sh` (new) | every corpus (pattern, subject) pair through `<prefix>_next`, byte and utf8 arms, `--engine=auto` and `vm` | libpcre2 10.46's global loop (`semprobe.c`'s G, promoted to `tests/findall/`). Independent of pcrec | floor = the harvest's own count (29,502 compared pairs byte; utf8 harvested likewise). The diverging subset (1,063 byte) has its own floor, so the retry cells cannot silently vanish | `make test-findall` (new section of `make test`) |
| iterator = loop | every non-`reports_empty` pair: `next` against today's `_search` loop | pcrec's own `_search` (shares the engine). This is the REGRESSION control, not the semantics one | non-gate pairs | `make test-findall` |
| `mg` lines | the harness, per block | written from libpcre2's global loop, oracle-verified at authoring | every diverging corpus pair gets one (generator in I1) | `make test-corpus` |
| sticky / NULL caps / setters / `next_n` | `drv.c`'s arms (`rc`, `Z`, `N`; the foreign-owner `B` arm is WITHDRAWN by D165 add. 3), a setter-on-BOUND arm, a setter-on-ENDED arm (IT8), a dirty-init arm (IT1: after `RX_ITER_INIT`, every field the init does not write is overwritten with `0xA5` bytes, the garbage a reused stack slot may hold; then a var-bearing artifact with no `rx_iter_vars` must give `PCREC_ERR_UNSET_VAR`, and an artifact with no `rx_iter_batch` must run at K = 1), a check-order arm (IT12: mid-character AND ill-formed must give `_search`'s code), all promoted into `tests/findall/` | the iterator's own `next` arm and `_search`'s first-call code (the twin's design) | every pair above; the arms' own cells | `make test-findall` |
| batching identity (§3.4a, conditional on Q-I1) | every pair through `next` at K ∈ {no region, 2, 3, 64}, byte and utf8, `--engine=auto` and `vm` | libpcre2's global loop for the answers (independent). For the give-up cells, the K = 1 sequence: a REGRESSION control by declaration (IC7). libpcre2's `match_limit`/`depth_limit` count a different unit from pcrec's step and work meters, so no setting of them is an independent oracle for WHERE pcrec gives up | as `run_iter_diff.sh`; the give-up cells' own floor (every `tests/findall/` give-up cell) | `make test-findall` |
| counted work under batching (IT2) | `tests/compound/loads_drv.c`'s instrument (every subject load counted through `-fsanitize=kernel-address` hooks; memchr/memcmp interposed), extended with an iterator mode: total subject loads for the whole find-all at K = 1 and at K = 4 on cells whose last fill ends on a pending code (done and a give-up) | the K = 1 count: K = 4 must be EQUAL. A drained batch that re-runs the failed search reads the subject tail again | the constructed cells (a match-dense prefix then a long no-match tail; a `--step-budget` give-up after three matches) | `make test-findall` |
| no internal call to an exported residual (§2.4) | every artifact of the three leaf populations, compiled `gcc -O2 -fPIC -c` | the artifact's own exported symbol list (`nm`), checked against its relocations (`objdump -dr`): a relocation from a function of the artifact to one of its exported residuals fails | one floor per leaf, counted from the objects: `_next_pos` 97; `_valid_upto` and `_var_valid` pinned at I1 (§2.4) | `make test-codegen` (`tests/codegen/run_residual_twins.sh`) |
| mover census | every artifact's text minus the iterator scaffolding, against I1's parent; its refusal-set membership and `<PREFIX>_ENGINE` stamp (IT15) | the parent's bytes, refusal set and stamps | full corpus, both arms (emit_sweep's population) | I1's commit (a delivery-bar run, recorded in the lane report) |
| `-futf-check` once | utf8 ill-formed cells through `next` against the checking artifact's loop | the loop | `tests/utfcheck/`'s pinned sets | `make test-utfcheck` |
| S (I2) | check 1 (`S >= max`), check 2 (the artifact's `_Static_assert`), check 3 (census + headroom) | §1.3 | from I2's first held row | I2's commit: pcrec's build (1), every artifact compile (2), `make test-findall` (3) |

### 6.8 The sabotage plan (existing ids kept; new rows PROPOSED, unnumbered)

Every plant's detector is named, and its witness REACHES the site (the reach column). An
answer-equivalent mutant is declared, with its structural detector. Revision 3 keeps every
existing id and WITHDRAWS S931 (D165 add. 3: the owner compare it planted no longer exists;
the id stays retired, never reused). New rows are proposals P-i..P-q. The next free id is
S1035, and the manager allocates ids. The target column is IC6's.

| id | plant | detector | reach | target |
|---|---|---|---|---|
| S923 | the non-empty advance uses `end`, not `__adv(end − 1)` (K75) | `run_iter_diff.sh` utf8 arm: `a`/`.` over `a\x80a` | `mc_illformed_utf8` + utf8 harvest | `test-findall` |
| S924 | the empty advance steps from `lo`, not the reported start | `(?=a)` over `"xax"` (1, not 2) | lookahead corpus | `test-findall` |
| S925 | the retry bit is never set | every diverging pair (1,063) | the diverging floor | `test-findall` |
| S926 | the retry runs UNANCHORED | `\G\|b` over `"xb"` (4 matches anchored, 3 unanchored). NO corpus pair distinguishes the two (0 of 29,502, `sem/out/retry_anchoring.out`), so I1 adds this cell as an `mg` line | the added cell | `test-corpus` |
| S927 | the retry also fires after a non-empty match | double reports on `a*?`/`aaa` | retry cells | `test-findall` |
| S928 | a failed retry does not advance | watchdog (wall) on `\|a` over `"b"`: the iterator spins. Detected as a timeout (a firing timeout is a finding) | retry cells | `test-findall` |
| S929 | `rc` not sticky after a give-up | a `--step-budget=3` cell (VM, `--engine=vm`): the call after the give-up must return 0 | `tests/findall/` give-up cells | `test-findall` |
| S930 | `rc` not sticky after done | `drv.c`'s post-end call (`STICKY-FAIL`) | every pair | `test-findall` |
| ~~S931~~ | WITHDRAWN (D165 add. 3): the owner compare is not in the design | — | — | — |
| S932 | the header check accepts any word | an uninitialized-word cell (`hdr = 0`) must give `PCREC_ERR_ITER` | `tests/findall/` | `test-findall` |
| S933 | `CHECKED` set before validation | utf8 ill-formed cells through a `-futf-check` artifact's `next` | `tests/utfcheck/` | `test-utfcheck` |
| S934 | validation runs every call (answer-equivalent) | STRUCTURAL: the codegen check counts one validator call in `__enter`'s bind path and none on BOUND | every `-futf-check` artifact | `test-codegen` |
| S935 | the startpos guard at bind removed | `rx_iter_at(&it, mid-char)` must give `PCREC_ERR_STARTPOS` | utf8 `rx_iter_at` cells | `test-findall` |
| S936 | the storage rows not zeroed at bind | I2's first kit row: a two-iterator cell on one stack slot (the second must not inherit the first's carried state) | I2 (lands with `st`, §1.3) | `test-findall` |
| S937 | `PCREC_ITER_STATE_SIZE` decremented below a held row | the artifact's `_Static_assert` | I2 | artifact compile |
| S938 | `next_n` writes `k + 1` spans | an ASan cell with an exact-size `out` (if `next_n` is built) | `tests/findall/` | `test-findall` (ASan built in) |
| S939 | `next_n` continues after a give-up | the give-up cell through `next_n` | as S929 | `test-findall` |
| S940 | `next` writes only the span, not the groups | VM caps differential: `next` vs `_search` per call | captures corpus | `test-findall` |
| S941 | the VM accept guard tests the consumed start, not the reported start | `ab\K` over `"ababab"` (3, not 2) | `\K` cells | `test-findall` |
| S942 | the DFA notempty root keeps the accept-pruned order | `a??b?` over `"ab"` on the DFA arm (`(0,2)`, not `(1,2)`) | DFA `reports_empty` cells | `test-findall` |
| S1009 | a fill delivers its pending code before the matches found ahead of it | the batching-identity arm's give-up cells at K = 4: the sequence must equal K = 1's | `tests/findall/` give-up cells | `test-findall` |
| S1010 | a fill reuses ONE meter across its steps (conditional on Q-I1: under the literal ruling this IS the design and the row inverts) | a `--step-budget` cell on the VM (`--engine=vm`) where each logical search fits and their sum does not: batched must equal K = 1 (no give-up) | a constructed `tests/findall/` cell (none of the harvested cells has a sub-budget sum; the cell ships with the plant) | `test-findall` |
| S1011 | the retry R shares SEARCH's meter (the `meter` cell `shared` on the retry row; conditional on Q-I1) | a `--step-budget` cell on the VM (`--engine=vm`; the VM accept guard is R) whose retry and following search each fit and their sum does not. A second cell runs the DFA arm (`dfa-root`), whose R is the notempty root: the DFA charges no step meter, so on that arm the plant must read IDENTICAL, which is the declared answer-equivalence there | constructed cells, as S1010 | `test-findall` |
| S1012 | the compound controller calls the exported `_next_pos` instead of `__adv` (answer-equivalent) | STRUCTURAL: the relocation check (§6.7) | the 97 compound artifacts | `test-codegen` |
| S1013 | the batch entry stride is one pair, not `NCAPS` | the batching arm on the captures corpus: `next`'s groups vs `_search`'s per match | VM artifacts with `NCAPS` > 1 | `test-findall` |
| S1014 | a setter on a BOUND iterator is accepted (rebinds `lo`) | the setter-on-BOUND arm: the next call must give `PCREC_ERR_ITER` | `tests/findall/` | `test-findall` |
| S1015 | the ENDED state is not set on a refusal (sticky lost after `PCREC_ERR_ITER`) | `drv.c`'s post-refusal call: 0 with `rc` unchanged | `tests/findall/` | `test-findall` |
| S1016 | the fill does not stop at K (writes entry K) | an ASan cell with an exact-size batch region | `tests/findall/`, every K arm | `test-findall` (ASan built in) |
| P-i | `__fill` drops the IT2 test (a drained batch with a pending code re-runs STEP; answer-equivalent) | the counted-work cell (§6.7): K = 4's subject loads exceed K = 1's | the two constructed counted-work cells | `test-findall` |
| P-j | the `-futf-check` prologue calls the exported `<p>_valid_upto` instead of `__valid_upto` (answer-equivalent) | STRUCTURAL: the relocation check | the `_valid_upto` population floor (§2.4) | `test-codegen` |
| P-k | the var-bearing prologue calls the exported `<p>_var_valid` instead of `__var_valid` (answer-equivalent) | STRUCTURAL: the relocation check | the `_var_valid` population floor or the script's own fixture (§2.4) | `test-codegen` |
| P-l | split's `meter` cell flips from `shared` to `per-operand` (IC5's mirror of S1011) | a `--step-budget` cell on a compound artifact (split; its F and Q run on the VM, `--engine=vm`) where F's attempt and Q's search each fit and their sum does not: today's compound gives up, and the plant answers | a constructed `tests/compound/` cell (split.rxt has no sub-budget-sum cell; it ships with the plant) | `test-compound` |
| P-m | bind does not normalize an optional field whose bit is clear (IT1) | the dirty-init arm: `vars` left as `0xA5…` on a var-bearing artifact must still give `PCREC_ERR_UNSET_VAR`; `batch` left as `0xA5…` must not be written (ASan) | the dirty-init cells | `test-findall` (ASan built in) |
| P-n | a setter on an ENDED iterator poisons the header (IT8) | the setter-on-ENDED arm: after a give-up, `rx_iter_at` then `next` must leave `rc` the give-up code | `tests/findall/` give-up cells | `test-findall` |
| P-o | bind runs the `-futf-check` validation before the boundary guard (IT12) | the check-order arm: a mid-character, ill-formed `rx_iter_at` start must give `PCREC_ERR_STARTPOS`, `_search`'s code | utf8 `-futf-check` `rx_iter_at` cells | `test-findall` |
| P-p | STEP's NULL-caps local is one pair (IT10) | an ASan cell: K = 1, NULL `caps`, `NCAPS` > 1 | VM artifacts with `NCAPS` > 1 | `test-findall` (ASan built in) |
| P-q | check 1 asserts `S == max` (IT7) | a synthetic row retirement at pcrec's build: one declared row marked retired must still build | pcrec's build (from I2) | I2's commit |

### 6.9 Staged commits

E0 (`compound_entries.md` §5.1: the zero-mover `entry_rows[]` with its rank column) lands
before I0b's tables are read and before I1 (D163 add. 7 Q4; memory `pcrec-remodel-first`).

**Stage ids** (IC8). The I-ids below are this note's. `compound_entries.md` uses I1-I5 for
its own stages (its I3 is the wrapper step, this note's I3 is `pair-hits`). This note cites
those as "`compound_entries.md` I3", never bare.

| stage | what | movers | abi |
|---|---|---|---|
| **I0** | (a) the `reports_empty` E1 fact (the minimum reported width, IT13) + its `--emit-facts` row; (b) the notempty root as a subset-construction parameter, listed in `--emit-facts` and never emitted into an artifact, with its control (anchored NOTEMPTY_ATSTART against libpcre2 over every `reports_empty` block); (c) the storage-row declarations as the STATE part's column of `entry_rows[]` (§8a), the max over the declarations listed in `--emit-facts` (check 1 itself lands at I2 with the literal), and the `first-nonzero` row's `meter` column (split's cell `shared`, byte-identical; conditional on Q-I1); (d) `tests/findall/` (the global-loop oracle, the harvest, the `mg` generator) and the `mg` line in all three `.rxt` legs | ZERO emitted bytes (emit_sweep, all streams). The facts listing gains rows | none |
| **parity slot** | the twin re-spelled (binding at init, the header-only compare, the setters, IT2's fill test) plus its `B64` fill arm; §5.3's pre-build run, launched by main in a box window. Its `B64` verdict SETS the `iterate` row's `batch` cell (`fill` or `off`); its `N64` verdict decides whether `next_n` joins I1 | none | none |
| **I1** | the shared block (`rx_iter` without `st`, the setters including `rx_iter_batch`, UNCONDITIONALLY); `_next` as an `iterate` row with the `batch` cell the parity slot set; STEP as the guarded `first-nonzero`; the body refactor; the residual twins (§2.4, F-1); the retry machinery; spec hunks; drivers; checks; the sabotage rows. **The batch ABI is in I1 whatever the parity slot finds** (IC3: one layout event). The parity slot runs before I1, so the fill's cell is decided before I1 too. The post-build gate re-checks it on the built artifacts. If the post-build gate reverses the twin's verdict, the cell flips in a follow-up commit: an abi number and a mover census, no layout or caller change. `next_n` is in I1 only if its `N64` arm won | every artifact (text) | ONE |
| **I2** | R17-b″: the kit's ITER form and its 40 B row; R-20 (`MF_BODY_PARAM`); **`st` and S** (§1.3: `PCREC_ITER_STATE_SIZE` = the derived max, 64 B today; `PCREC_ITER_LAYOUT` 3 → 4; check 2 and S936/S937 live) | kit-form artifacts; every artifact's shared block | a pcrec abi event (a kit byte move, D147), the same one |
| **I3** | `pair-hits`: K5's linear pair arm | the 61 corpus / 11 bench two-stream artifacts | one |
| **I4** | `next_n`, if the parity slot filed it; its trigger is its arm beating `I` on a re-run (U1) | every artifact | one |
| **batch cell flip** | only if the parity slot's `off` is later reversed by a measured re-run (U1) | every artifact's `_next` | one, no layout change |
| **S shrink** | K5 retired by a single-pass proof (§1.3): S 64 → 48 B, only when another abi event moves the shared block | every artifact | rides that event |

## 7. The standing design questions (docs/design/CLAUDE.md)

1. **The measurement regime. RELEVANT.**
   - Every number here is compile-only: `.text` sizes, instruction identity, store counts.
     All were taken at gcc 15.2 `-O2` x86-64 on the Linux dev box, plus answer differentials
     against libpcre2 10.46 (byte mode, options 0). None reads a clock. Revision 2 measured
     nothing. Revision 3 measured `sizeof(rx_iter)` (96 B at I1, 160 B at I2; revision 2's
     layout 152 B) and the fast path's instructions on a hand-C probe, at gcc 15.2 `-O2`,
     with and without `-fPIC`. The three init stores remain PREDICTED and owed by the
     twin's re-run.
   - The sizes are compiler-dependent. Another gcc may inline differently, which is why
     `L_new` vs `L_old` is a gate arm.
   - The parity gate (§5.3) is the one timed decision, and since revision 2 it decides two
     things: the iterator's parity (gated) and the `batch` cell (`B64` beats `I`). Since
     revision 3 the batch cell moves no ABI, so a wrong verdict costs one cell flip, not a
     layout event. Both are the latency regime (dependent calls, dense matches), one box, two
     link regimes. Batching's sign could flip with the regime: under R1 (static link) the
     exported call it amortizes is cheapest, so R1 is where `B64`'s margin is smallest and
     where the decision is made conservatively.
   - A different box (Zen 1, the Mac) is the bench's official verdict, not this gate's
     (D144 add. 4).
2. **The independent control. RELEVANT.**
   - Semantics is checked against libpcre2's own global loop (pcre2demo.c's loop over the
     library, sharing no source with pcrec), cross-checked by python on the targeted cells.
   - Batching is checked against the same oracle at four values of K, so the batched answer
     is never checked only against the unbatched one (which shares its STEP). The give-up
     cells compare against K = 1 and are DECLARED the regression control they are (IC7).
     libpcre2's limits count a different unit from pcrec's meters, so no independent oracle
     for where a give-up happens exists. A bug common to STEP at K = 1 and to a fill is
     therefore invisible to the give-up cells, and the design accepts that.
   - The work batching does is checked by COUNTED loads at K = 1 against K = 4 (IT2), which
     reads the subject, not the iterator's own state.
   - The iterator-equals-loop check shares pcrec's engine with its subject, so it is named
     the REGRESSION control, not the semantics one.
   - S (from I2): the C compiler's layout against the literal (independent); the literal
     `>=` the declarations' max at pcrec's build (regression, shares its source). Neither
     exists at I1, where nothing is held (IC2).
   - The residual twins: relocations against the artifact's own exported symbol list, in a
     `-fPIC` build where an internal call to an exported function cannot be inlined away.
   - Populations are counted by the harvest: 29,502 compared byte pairs; 686 gate-true
     patterns; 233 static-label bodies; 97 compound artifacts for F-1; one floor per
     residual leaf; 67 patterns for K5's retirement bound.
   - Each sabotage row names its reach and its target. S1010, S1011, P-i and P-l ship their
     own constructed cells because no harvested cell reaches them.
3. **What moves when the data is regenerated. RELEVANT.**
   - S is derived from the declarations. A declaration change that moves the max moves the
     shared block on EVERY artifact (an abi event, with the readers of §6.1) and
     `sizeof(rx_iter)` for callers. S is first derived AT I2 (rev 3), so a kit row change
     before I2 costs no extra event; after I2, growth is an event and a shrink rides one
     (§1.3).
   - The `mg` expectations are regenerated from libpcre2. A new oracle version is a store key
     (`oracle_store/`), so a moved count is a clean miss, never silent.
   - The `reports_empty` fact gates the retry machinery. A change to its derivation moves
     exactly the artifacts whose gate flips (a mover census by ID). The stamp
     `<PREFIX>_ITER_RETRY` moves with it.
   - A measurement-set change (D166) moves `__find`'s layout only at `+1`, through `θ_hot`
     (`compound_entries.md` §3.3). At `0`, nothing in this design reads the set.

---

## 8. The sibling-family lens

### 8.1 State carried across the calls of one find-all

D165 item 2 named three members. The survey finds these:

| member | carried what | owner | where it lives | status |
|---|---|---|---|---|
| the kit's FIND cache (A3, R3/R4's H, the presence carry) | 5 words: base, top, mask, H, `valid_until` | kit | a row of `st` | I2 |
| the empty-match retry | one bit + `lo == q` | pcrec | `flags` | I1 |
| `-futf-check` validated | one bit | pcrec | `flags` (CHECKED) | I1 |
| variables validated | one bit (CHECKED) | pcrec | `flags` | I1 |
| **the result batch** (rev 2; rev 3 home) | K entries of `NCAPS` pairs + the cursor + `rc_next` | pcrec | caller memory bound by `rx_iter_batch`; the cursor in FIXED fields | I1 (the ABI); the fill per the `batch` cell (§6.9) |
| K5's pair-arm pending hits | `ha`, `hb` | pcrec | a row of `st` | I3 |
| the hybrid's reseed hint | the adaptive block | pcrec | a row of `st` | FILED (U5) |
| [FINDALL-REENTRY]: the forward DFA's state at the previous match end | state + position (≈16 B) | pcrec | a row of `st` (would be) | BOONIES (U6) |
| the hand-off re-entry's landmark ([REQ-HANDOFF-L1], K105) | the next landmark position | pcrec | a row of `st` (would be) | U7 |
| a compound's per-part caches (`compound.md` §C) | per part | pcrec | summed rows | via the sum rule |
| **streaming** ([M3]: state across subject CHUNKS, not across matches) | the automaton state at a chunk boundary | pcrec | its own type | U10, a SIBLING type |

All but streaming and the batch fit ONE mechanism: a declared row of S, zero-fresh,
persistent, owned by the artifact that bound the iterator. The batch is the one member whose
size the CALLER chooses, which is why it lives in caller memory and not in S (D165 add. 2):
S is a public constant and cannot carry a caller's K. Streaming breaks the "same unchanged
subject" invariant every row rests on, so it gets its own type.

### 8.2 The combinator family (`compound.md` §A.2, `compound_entries.md` §4.1)

| combinator | clients | what revision 2 adds |
|---|---|---|
| `first-nonzero(A@x, B@LOWER(g(x)))`, guarded | split (`F@f`, `Q@LOWER(next_pos(f))`, guard: the floor can be live); **the retry** (`R@q`, `SEARCH@LOWER(adv(q))`, guard: RETRY) | the guard is named as a row column (split had it in prose, §B.2); a `meter` column (`shared` for split, `per-operand` for the retry), CONDITIONAL on Q-I1. Both columns are E0's or I1's to add: today's emitter is split-only (IC4) |
| `locate-then-finish` | `_search`; SEARCH | none |
| `iterate(STATE; STEP; BATCH)` | **`next`** (new); `next_n` (HELD) | the new member: bind/check, deliver, fill; a `batch` column (`fill` / `off`) |
| `select-by-arg`, `dispatch`, `min-start-then-finish` | captures on demand, arch variants, 4c | none; an `iterate` row may nest any of them inside STEP |

The retry is therefore not a sibling mechanism to split: it is a second ROW of split's
combinator, once E0 (or I1) gives that combinator its guard and meter columns. The one new combinator, `iterate`, is the only place the iterator adds control
logic, and its first client is the only one designed.

### 8.3 Where batching sits among the "per-call overhead" levers

The parity gate's levers are siblings by purpose: binding at init (removes a compare per
call), the residual twins (remove a PLT call per match under `-fPIC`), `__find`'s layout
(removes or adds a call per match, the part-layout row), and batching (amortizes the exported
call itself). They are not one mechanism: each sits in a different table (the struct, the
linkage rule I3, the dial row, the `iterate` row). The gate measures them together (`I`) and
batching apart (`B64`), so each keeps its own evidence.

---

## 8a. NEW-DATASET: every new table, column or record, and its home

| new item | kind | home | argument |
|---|---|---|---|
| the storage-row declarations (revision 1's proposed `src/gen/iter_rows.def`) | rows (owner, words, align, held-when) | **the STATE part's column in `entry_rows[]`** (`compound_entries.md` §4.1), with the kit's rows arriving as its form's declared words on `mf_result` | Revision 1 proposed a standalone file. The entry table already lists each entry's parts, and "held at once on a path" is a closure over exactly those part references (a compound's parts SUM because they are the same row's parts). A separate file would restate the part list. The kit's words stay the kit's facts (D157). If E0 lands without a per-part declaration slot, the fallback is revision 1's file beside `entries.c`, named as a debt. `entry_rows[]` does not exist yet (`compound_entries.md` §4.1, r3 LK-1). Since S lands at I2 (rev 3), the slot is needed by I2, not by I1 |
| S | a derived constant | the shared block's literal, checked against the declarations | already revision 1's; A10 changes only the unit (words) |
| `reports_empty` | an E1 fact | **PATFACTS** (`src/facts/`, D120), listed by `--emit-facts` (`docs/spec/facts_listing.md`) | a per-pattern analysis fact; PATFACTS is its home by charter |
| the notempty root | a machine ROLE | the machine-role vocabulary of the anchored machine (`anchored_match_unwrapped.md` §2), placed by `compound_place[]` row 3 as an in-Job role (`compound_entries.md` §4.2) | a parameter of an existing construction, not a new machine kind |
| the `first-nonzero` row's guard and `meter` columns | two columns | `compound.md` §A.2's combinator table | split's guard exists in prose (§B.2); the meter column records a difference the two rows already have |
| the `iterate` combinator | a row of the combinator vocabulary | `compound.md` §A.2 / `compound_entries.md` §4.1's `CompComb` enum (which already names `iterate`) | no new table |
| the `mode` (M) per entry | a column | `entry_rows[]`'s `mode` (`compound_entries.md` §4.1) | already there |
| the batch region | caller memory, bound by a setter | **`rx_iter` itself**: `batch`/`nbatch`, set by `rx_iter_batch` (rev 3; the manager's IT3/IC3 ruling) | D165 add. 2 rules "caller-provided `_in` memory". The setter keeps it caller memory without growing `<prefix>_buffers`, whose existing callers would read the new fields indeterminate (IT3). The lifetime rule attaches to the object it governs |
| the `iterate` row's `batch` column | a column (`fill` / `off`), one cell | `entry_rows[]`'s `iterate` row (`compound_entries.md` §4.1) | set by the parity slot; a cell, so turning batching on or off is never a layout event |
| the batch cursor, `rc_next`, the option bits | FIXED fields | `rx_iter` | every artifact can batch; S cannot carry a caller-sized K |
| `<PREFIX>_ITER_RETRY` | a stamp | the stamp inventory (`match_api.md` §6.3.2, `stamp_kinds.c`) | one strategy choice per artifact |
| ~~`<PREFIX>_BATCH_ENTRY_SIZE`~~ | withdrawn (rev 3) | — | the capacity is in pairs, so the caller sizes the region with `<PREFIX>_NCAPS`, which it already has (§1.1) |
| the `mg` `.rxt` line | a line kind | `rxt_schema.def` (all three legs) and `docs/spec/rxt_format.md` | the existing schema |
| the parity gate's results | an acceptance record | a lane report plus `findall_iter/` probe outputs | NOT a D166 measurement set: no selection reads it. If batching's decision ever became per-box, its crossover would be a set row; today it is one ruled yes/no |
| `θ_hot` (read, not added) | a measurement-set row | `measure_sets.md`'s derivation registry (`compound_entries.md` §3.3) | this design only reads it through the part-layout row |

No new standalone table is proposed. The one place this revision could have added one (the
storage rows) is placed in the entry table.

---

## 9. UNLOCKS (each with its trigger)

| # | unlock | trigger |
|---|---|---|
| U1 | the `batch` cell flipped to `fill` if the parity slot set `off`; the public `next_n` if not in I1 | a re-run of the `B64` (resp. `N64`) arm beating `I` by more than the noise floor on cells 1/3 (§5.3). The batch flip moves no layout (§6.9) |
| U2 | validate-once (`-futf-check` O(n) once) | built in I1, no trigger |
| U3 | K5 linear (the `pair-hits` row), ~200× off-bench | its witness exists (walk_survey K5); the first post-framework optimization (I3) |
| U4 | the kit's A3 and R3/R4 rows (R17-b″) | the kit's |
| U5 | the reseed hint row ([OPT-HYB-RESEED-XCALL]) | its restated trigger (a bench find-all cell averaging > 1 re-seed per call, losing to `-fno-hyb-reseed`) + GIVEUP1's direction check |
| U6 | [FINDALL-REENTRY] carried DFA state | a bench find-all cell where re-entry is a measured share |
| U7 | the hand-off re-entry's landmark cache | K105's witness re-measured under the iterator |
| U8 | the substitution global loop ([M4-SUBST]) = an `iterate` row with a splice sink. replace_design.md §3.8's "the §3.1 loop cannot express the retry" seam DISSOLVES | [M4-SUBST] opens |
| U9 | `rx_entries.next` ([V-E] item (1), [ART-MGR] S1): the uniform signature `(rx_iter *, caps)` is ready | [V-E]'s trigger |
| U10 | a streaming sibling `rx_stream` ([M3]) | [M3] opens |
| U11 | `empty_pref`, the structural narrowing of the retry gate | a measured cost of the futile retry on a gate-true, non-diverging pattern |
| U12 | spans-only batch entries (Q-I4's alternative) | a VM find-all cell whose batch fill is dominated by capture copying |
| U13 | `__find`'s `shared` linkage for every body at `0` (`compound_entries.md` U1) | `I_shared` within the noise floor of `I` (§5.3) |
| U14 | S shrink to 48 B | K5 retired by a kit form's single-pass proof AND another abi event moving the shared block (§1.3) |
| U15 | a per-box batch size suggestion (`rx_info` or a header hint) | a measured `B64` vs `B8` crossover that differs across boxes; it would be a D166 set row (§8a) |
| U16 | a newline-aware failed-retry advance (pcre2demo steps over a whole CRLF under CRLF/ANY/ANYCRLF); the non-empty advance is unchanged (IT14) | `DEF_NEWLINE_CONV` gains a producer (`docs/spec/registry.md:197`) |
| U17 | a general "twin-forwarding" check: no exported-to-exported edge inside an artifact, which would also cover `compound_entries.md` I3's wrapper edges (itcrit2's unlock) | `compound_entries.md` I3 lands |
| U18 | debug-only misuse checks under a `-DPCREC_ITER_CHECK`-style switch: an owner tag, and a batch region shared by two live iterators. D165 add. 3 allows a debug build to add checks; none ships in the hot path | the first user report of a foreign iterator or a shared batch region |

---

## 10. Questions for Frank (discussion: the problem, the forces, the leaning)

**Revision 1's Q1-Q4 are RULED (D165 add. 2):** Q1 match PCRE2's global iteration; Q2
internal batching in caller memory, `next_n` optional, both timed; Q3 bind `(s, n)` at init;
Q4 `PCREC_ERR_ITER` (-10) with the 1/0 + `it.rc` contract. D165 add. 3 then ruled out the
per-call owner check. Revision 2's four, as revision 3 leaves them:

**Q-I1. What is "one meter per exported call" for the iterator? STILL OPEN.**
- *The problem.* D163 add. 6 Q1 rules one budget meter per EXPORTED call, so a compound's
  parts charge the caller's meter. Read literally, one `next` call is one exported call,
  so the retry and the following search, and a whole batch fill, would share one meter.
- *The forces.* A shared meter would make the iterator give up where today's loop does not
  (two searches' work against one budget), and would make batching change WHERE it gives up,
  which breaks §3.4a's identity and D158's spirit (an internal change moving a give-up).
  pcre2demo's loop gives the retry its own `pcre2_match` call and so its own limits. Split's
  F and Q are different: they serve one `_search`, so one meter is right there.
- *Leaning, the design of record pending the ruling.* One meter per LOGICAL search (what one
  `_search` call or one `pcre2_match` call would be). Q1 then holds unchanged inside each
  logical search, and the combinator row carries the difference as its `meter` column.
- *What depends on it* (IT6): §0.3, §2.1's `meter` column, §3.4's first bullets, §3.4a,
  S1010, S1011, P-l and the batching-identity check's give-up cells. §3.4a states what each
  becomes under the literal ruling. The panel (itcrit1 IT6) found revision 2 had made these
  read as settled, which they are not.

**Q-I2. How does an iterator get the caller's `_in` memory? SETTLED by the panel and D165
add. 3.** The typed header setter `<prefix>_iter_buffers(&it, &bufs)` (§1.1). Its type check
holds at the setter call. Revision 2 also claimed that "the owner check catches a foreign
iterator". IT4 showed the owner check did not cover buffers, and D165 add. 3 removed it. A
foreign descriptor reaching another artifact's `next` is undefined, which the spec states
(§6.2). Nothing further is asked.

**Q-I3. Where does the batch region live? SETTLED by the manager's ruling on IT3/IC3.** In
caller memory, through the iterator's own setter `rx_iter_batch` (§2.3). It does not go in
`<prefix>_buffers`. That avoids the silent indeterminate fields at existing member-by-member
callers (IT3), the every-artifact header move, the positional `<p>_no_buffers` warning and
the sizing macro (IC3). The lifetime rule attaches to the iterator, and F11 is withdrawn.

**Q-I4. What does one batch entry hold? In discussion; answer-free, so the manager may rule
it.**
- *The problem.* A caller passes `caps` per call, but the fill runs before the caller says
  whether the next call wants captures.
- *The forces.* Full captures per entry (`<PREFIX>_NCAPS` pairs) always answers whatever the
  caller passes. On a DFA artifact `NCAPS` = 1, so it costs nothing there. On a VM artifact
  with many groups it copies `NCAPS` pairs per match even for a caller that only wants spans.
  IT10 adds a reason to keep the entry full: STEP writes `NCAPS` pairs whatever its
  destination, so the metered work is the same at every K. A spans-only mode would need a
  bind-time flag (a fifth setter, which the setter rule absorbs), and a refusal when a
  non-NULL `caps` meets a spans-only batch.
- *Leaning.* Full captures per entry. Spans-only stays filed as U12 with a measured trigger.
  Both choices give identical answers and only the copy cost differs, so this is the
  manager's call (memory `pcrec-answer-free-choices-are-mine`) unless Frank wants it.

## 11. Findings (for the manager)

Revision 1's F1-F8 stand (F7's "superseded" now reads: `compound.md` §C's session pointer is
replaced by the STATE part of the `iterate` row).

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
  by an assumption. (Now `compound_entries.md`'s `copyable(part)` fact, row P2.)
- **F6.** `rx_iter it = { MAGIC }` trips `-Wmissing-field-initializers` under the harness's
  own `-Wextra -Werror`, and any aggregate initializer is a full memset. The
  static-inline-returning spelling costs one store per written field, warning-free.
- **F7.** `compound.md` §C's `rx_ctx` session pointer is superseded by D165's iterator
  (§3.7). That design's foreign-cache hazard needs no owner-tagged region once the state
  lives only in the top-level artifact's iterator.
- **F8.** A var-bearing artifact's `_search` has a non-uniform signature (18 corpus
  patterns). `next`'s is uniform, because the iterator carries `vars`.
- **F9 (rev 2; corrected in rev 3, IC9).** D165 add. 2 writes the `_in` descriptor as
  `rx_buffers`. That is the example prefix `rx` (match_api.md:3108 uses it the same way), not
  a different type. The shipped type is per-artifact `<prefix>_buffers` (match_api.md
  §10.2¶2). What remains true: a binding typed to the descriptor must be per-prefix (Q-I2).
- **F10 (rev 2).** D163 add. 6 Q1's "one meter per exported call", read literally, would make
  the retry and any internal batching move give-ups. The two clients of `first-nonzero`
  already differ on it (Q-I1).
- **F11 (rev 2; WITHDRAWN as this design's cost in rev 3).** Growing `<prefix>_buffers`
  warns every positional initializer of it under `-Wextra`, and silently leaves new fields
  indeterminate at member-by-member callers (IT3). Revision 3 does not grow it. The record
  stays for any later region added to the descriptor, which would meet four sites:
  match_api.md §10.6's example; `docs/dev/lanes/f3search_driver.c:117`; the emitted
  `<p>_no_buffers` (`src/gen/emit_vm.c:13826`); and the member-by-member callers
  (pcrec-bench `testees/pcrec/shim.c:1728,1759`,
  `docs/dev/optloop/artrev/A09/tools/budget_main.c:17`).
- **F12 (rev 2).** `compound_entries.md` §3.8 rates `__find`'s in-edge from `_next` R2 with
  the batch fill HELD. Designing the fill makes that edge R3 on every artifact once batching
  lands (the loop is always compiled; K is a run-time value), which gives that note's
  `−2`/`−1` pair its first designed witness and makes `I_shared` the `−2` layout alone.
  `compound_entries.md` is not edited here.
- **F13 (rev 2; corrected in rev 3).** Under A10, S today is 64 B, not 56 (revision 1) or 48
  (Q-R17P-10): the kit's row grew to 40 B and K5 stays. Revision 2 said
  `compound_entries.md` cites 48/56; it does not (itcrit2's grep of its rev 3), and that half
  is removed. The stale cites that do exist: `r17b_prime.md` on `lane/memfn-r17` (lines 97,
  126, 1115-1120, 1162-1164, 1422, 1453), for the kit manager; `docs/dev/decisions.md:9707`
  (Q-R17P-10's 48 B), historical and superseded by A10 at `:9718`, the manager's to annotate
  if wanted; `docs/design/CLAUDE.md`'s revision 1 entry and `docs/dev/lanes/CLAUDE.md`'s
  iterdes entry, annotated by this lane; `docs/dev/lanes/iterdes_report.md:18,103`, a dated
  lane record left as written. Every one should cite §1.3's derivation rather than a number.
- **F14 (rev 3).** Revision 2's `sizeof(rx_iter)` = 160 B was a miscount: that layout is 152
  B (88 B of fixed fields, not 96). Measured at gcc 15.2 on LP64 (§1.1).
- **F15 (rev 3).** The rule IT12 needs is match_api.md §9.4¶4 ("the boundary guard first,
  then the check"), not §3.2¶2 as the panel cited it. The rule is the same.
- **F16 (rev 3, IC8 + itcrit2 F12): a hand-off list for `compound_entries.md` revision 4.**
  That note is mid-revision (D163 add. 8), so it is not edited here. Its next revision
  should:
  - replace `__step` with this note's parts: `__enter`, `__fill`, `__deliver` and the STEP
    body, each with one caller (`_next`). Of these, `__fill`'s call of `__find` is the R3
    edge while the `batch` cell is `fill` (§2.2). Give `__fill` its own row;
  - re-label `__adv` "I1's static twin" (it says "I3's", `:772-774`) and qualify stage ids
    across the two notes;
  - retire the stale HELD notes: `:54` (the F4 row's "batch-fill R3 witness HELD with
    Q2"), `:192` (`_next_n` held), `:440` ("not designed in `findall_iter.md`", now false),
    `:664`, `:776`, `:781`;
  - re-read `:757` ("two dial rows ... disjoint subjects") against the `-1` witness that
    §2.2 designs.
