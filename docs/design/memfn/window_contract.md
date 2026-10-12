# window_contract — what pcrec tells the kit about a search site and a compile (D161, chunk 2)

Lane `d161note`, 2026-10-12, from main `f3569b161` (pcrec abi 76). The kit
branch `lane/memfn-r17` (`5ffbb7d28`) carries R17-a (`MF_SITE_ABI` 11: the
window fields, `decl_point`, `mf_locals`, `mf_defined`), and `lane/r17b`
carries R17-b (`MF_SITE_ABI` 12, N6, pcrec abi 77). Both were read with
`git show`; neither is merged to main. DESIGN ONLY: nothing under `src/`,
`cli/`, `lib/`, `memfn/` or `tests/` changes, and nothing was run.

**Status: PROPOSED.** A light panel reviews it next (§13). The R-18 outline
(§11) is the manager's to file.

The contract carries FACTS only, never the kit's method (D157). Every
selection below is an ordered first-match table (memory
`pcrec-decisions-as-first-match-tables`).

## 0. Answers first

1. **The SITE is a bounded sub-problem pcrec chooses** (D161 add. 4). It is a
   list of SPANS measured from one ORIGIN, the sub-problem's match start. Each
   span has a class per position, an offset interval `[omin, omax]` from the
   origin, and a `need`. The offset interval is sent as `(move_back,
   overshoot)` = `(omax, omax - omin)`, the kit's existing W1/W2 fields. One
   new site fact, `spans_seq` (the SEQUENCE RULE, §2.3), states that two
   spans' starts differ only by the items between them. That makes every
   pairwise distance exact and derivable, so "bounded gaps" and "minimum
   offset" need no fields of their own (§2.2's mapping table). Every value is
   true, required and bounded; an unbounded offset is refused by contract,
   not reserved (D161 add. 5).
2. **The reply is a WINDOW `[L, U]` or a VERDICT.** `L` is today's W3 (no
   sub-problem match begins in `[lo, L)`). `U` is an optional out-hook: the
   largest start a match carrying the located occurrence can have. The
   resume point is `U + 1`. A FIND miss over the whole range is NOMATCH, so a
   bounded span's presence test is part of FIND. Only unbounded-offset
   necessary bytes keep a separate PRESENCE (VERDICT) site. Because every
   span is measured from one origin, the reply needs no span index; the
   kit's planned W8 is rejected (§7).
3. **The ANALYSIS object** (D162) is a versioned list of kinds keyed by the
   [FINDINGS] query name (`byte-rate`, later `run-rarity`). Each kind is
   PRESENT or explicitly ABSENT and carries a PROVENANCE: `prior-authored`,
   `prior-none` or `measured`, plus the bundle identity and the same digest
   the `<PREFIX>_FINDINGS` stamp reports. `byte-rate` is always present. Under
   `-e utf8` today it is `prior-none` with no table, because pcrec has no
   utf8 prior until D160 lands, and a fabricated uniform table would be a
   density claim (§3.2). The kit is encoding-blind (D147 add. 14), so
   `cpfreq` is never sent.
4. **The kit's job is a CHAIN of 1-2 simple searches inside one site** (D161
   add. 5), with a total no-search arm (`L = lo`, D162 ruling 2). A 3+-link
   chain needs one more fact, each span's distance to the PREVIOUS span. The
   sequence rule already delivers it, so the extension is kit-internal:
   specified here, not built (§4.2).
5. **[KIT-VERIFY] fits without a new interface** (§4.3). Direction (1),
   "verify span k", is `need = REQUIRED` on span k, which already exists in
   the vocabulary. Direction (2) is a STATIC return: `mf_result.proven`,
   per span, the positions the chosen form verifies at every returned
   window. It is defined only for spans whose offset from `L` is fixed
   (`overshoot` 0). pcrec may advance its consumer past those positions, or
   ignore them; either way the code is correct.
6. **ONE pcrec-side producer**: a new core fact `span_facts` (E2, proposed
   owner `src/facts/spans.c`). It is one AST walk that generalizes `rb_walk`'s
   offset bookkeeping to `(classes, omin, omax)` per span and adds the
   MINIMUM offset nothing carries today. It cuts segments at unbounded items.
   The facts it absorbs (`req_set`/`req_whole_run`/`*_maxoff`, the k-set
   prefix, `start_set`) first become its CONTROLS (§5). The DECISIONS that
   read the prior to choose among spans move into the kit: the req pick, the
   run window start, set-leads, the offset-k selection, the landmark K
   admission, G1 and `plan_hint`. Unbounded cuts stay pcrec's: the reverse
   pass, landing, rev-end, rev-inner, the attempt loop and the VM retry
   policy.
7. **Retirement sequence** (D161 add. 6, D162 add. 3): the frequency kind
   lands first (S1), then the kit's own ranking, implement-then-replace (S2),
   then the retirement of `mf_pred.rank_*`, `pcrec_find_run_rank`, the never-
   filled `ppm_*`/`cand_ppm_*` and the unread `mf_site.consumer`, in one
   `MF_SITE_ABI` bump with zero pcrec movers (S3). Consumer price was never
   built; it retires as text. The kit's memo stays in `mf_art` (per attempt)
   until a measured compile cost says otherwise (§3.5).
8. **Ratified** (§7): the storage capability, the window fields W0-W3 (with
   the unbounded sentinels made PERMANENTLY refused), N5 in its per-width
   rev-2.3 form, and N6. **Rejected**: W8 (span index), W9 (consumer price).
   **Moved**: W10 (joint survival) becomes the analysis kind `run-rarity`.

## 1. Inputs, and what is already built

**Binding rulings** (read in full; not re-opened):
- D146 (delegation) and D147 (layers);
- D155 add. 3/4/4.1 (composable body pieces; per-width primitives; a stateful
  body is `next_candidate`);
- D157 (facts, never method);
- D161 + add. 1-6;
- D162 + add. 1-4.

Memory rules that also bind: no silent defaults (a value a row USES must be
stated; unused fields are wildcards); K96 row contracts (applicability covers
every parameter a row does not honour; allowlists of honoured fields);
decisions as first-match tables.

**The site vocabulary on the kit branch** (`memfn/include/memfn.h`):

| item | state | where |
|---|---|---|
| one span = an `mf_pred` of terms at fixed offsets | BUILT | `MF_SITE_ABI` ≤ 10, main |
| `mf_pred.window_stated`/`move_back`/`overshoot` (W0-W2), FIND's result is the window's beginning (W3) | BUILT | `MF_SITE_ABI` 11, `lane/memfn-r17` |
| `mf_site.decl_point`, `mf_locals`, `mf_defined`, `fn_ref` as the STMT stem (W4/W5) | BUILT | same |
| `mf_result.keeps_storage`, N6 in `valid_prefix`, the W8 sub-block `pcrec_mfk_w8_*` | BUILT | `MF_SITE_ABI` 12, `lane/r17b` |
| `mf_pred.rank_n/rank_pos/rank_ppm` (RQ-2, D157) | BUILT, read by `vrun` KB | main |
| `mf_term.ppm_*`, `mf_site.cand_ppm_*` | stated "unknown" everywhere, read by nobody | main |
| `mf_site.consumer` | stated `MF_C_ENGINE` everywhere, only range-checked (`compose.c:383`) | main |
| `mf_pred.plan_hint`/`plan_pos` | pcrec's model's scan pick, "permanent until M5" | main |

## 2. Object A: the SITE description

### 2.1 What a site is

A site is one search pcrec delegates. Its description states a SUB-PROBLEM: a
regular language pcrec has cut out of the pattern. The kit must locate where
a match of that language can begin. The sub-problem need not be the whole
pattern. For `a.*aaa.{2,5}zxq`, pcrec may send only `aaa.{2,5}zxq` and recover
`a.*` itself with a reverse walk (D161 add. 4). Every fact in the description
is TRUE of every match of the sub-problem, and the kit must honour every one
(K96: a row that does not honour a stated parameter does not apply).

**The ORIGIN** is the sub-problem's match start `m`. Every offset in the site
is measured from it. That one shared origin keeps the reply span-free (§2.4).

### 2.2 The span list

A site carries `1 + npred` spans: `pred` (span 0) and `preds[0..npred)`
(spans 1..npred, the kit's planned W7 reading, generalized). Each span is one
`mf_pred`:

| field | meaning | today's field | new? |
|---|---|---|---|
| terms (SET / RUN) | the class of each position, at fixed offsets inside the span. Positions no term covers are "any byte" | `term[]`, `nterm` | no |
| `move_back` | `omax`: the span's largest start offset from the origin. The window begins `move_back` bytes before the span. Signed; MLINE states -1 | W1 | no (R17-a) |
| `overshoot` | `omax - omin`: how far the window's beginning may lie before the match start | W2 | no (R17-a) |
| `window_stated` | 1 = the two above are STATED; 0 (the zero fill) = unstated, refused on a window site | W0 | no (R17-a) |
| `need` | REQUIRED: every returned window is consistent with this span (§2.4); OPTIONAL: the kit may use or ignore it | `mf_pred.need` | no (meaning widened from "the set-leads lead") |
| `spans_seq` (site-level) | 1 = the SEQUENCE RULE holds for this site's spans (§2.3); 0 = it is not stated, and no row may read a pairwise distance | — | **yes** (R-18) |

D161 and the brief name five span parameters. The table below says where each
one lives. None of them gets a field of its own, because each one is derivable
from the fields above:

| D161 / brief item | carried as |
|---|---|
| classes per position | the span's terms |
| move-back | `move_back` (= `omax`) |
| overshoot | `overshoot` |
| MINIMUM offset | `omin = move_back - overshoot` (signed). It is a fact pcrec must newly COMPUTE (wingame §1.2: no req fact carries a minimum today), but it travels inside `overshoot`. A separate field would be a second spelling of one fact (D122) |
| bounded gaps | the distance between consecutive spans. Under `spans_seq` it is `[omin_j - omin_i, omax_j - omax_i]`, exact (§2.3) |

### 2.3 The rules

- **True and required.** Every span is NECESSARY: every match of the
  sub-problem carries, at some start offset `d ∈ [omin, omax]`, a byte of each
  position's class at `m + d + j`. Each REQUIRED span binds the reply.
- **Bounded only.** `move_back` and `overshoot` are finite. The reserved
  `MF_MOVE_UNBOUNDED`/`MF_OVER_UNBOUNDED` (R17-a) become PERMANENTLY refused.
  D161 add. 5: unbounded is automata and pcrec's, so no future row will
  define them (§7, item W1/W2).
- **No silent defaults.** `window_stated` and `spans_seq` are stated bits.
  The zero fill reads "unstated", never "0 / not sequential": a FIND builder
  that forgets W0 is refused at define (R17-a's rule), and a multi-span site
  whose builder forgets `spans_seq` simply has no row that reads a pairwise
  distance. That is the K96 shape: the field is a wildcard for every row
  that does not use it, and stated for every row that does.
- **THE SEQUENCE RULE** (`spans_seq` = 1). The spans are listed in order of
  position, and they are a subsequence of ONE flattened sequence of positions
  and bounded gaps that every match of the sub-problem follows. So for
  `i < j`:

      start_j - start_i  ∈  [omin_j - omin_i,  omax_j - omax_i]

  Without the rule, only the LOOSE interval `[omin_j - omax_i,
  omax_j - omin_i]` is sound. wingame §8.1 measured the difference on its
  witness `.{0,6}\d.{0,3}#`: a region of 3 starts (tight) against 15 (loose),
  costing the refine policy 1.4x-2x. The producer emits only sequential spans
  by construction (§5.2) and states 1. A future producer of BRANCH spans
  (`(?:GET|POST)...`, wingame §2.2) states 0 (§8, example ii).
- **Range.** Unchanged from the shipped vocabulary: `[lo, n - end_back)`,
  with `empty` declared, no wrap, and `lo > n` empty.

### 2.4 The reply

A site's reply is one of two TYPES, keyed on its op. These are
`locate_finish.md`'s result types, restricted to what a kit site can prove:

| op | reply | meaning |
|---|---|---|
| FIND (a window site) | WINDOW: `L` (the `result` hook, today's W3) and optionally `U` (a new out-hook `start_hi`; when unstated, nothing is written) | No sub-problem match begins in `[lo, L)`. Every match carrying the occurrence `s` the kit located begins in `[L, U]`, where `U = s - omin` of the span that located it (so `U - L ≤ overshoot`, with equality unless W3 clamped `L` to `lo`). A miss means NO sub-problem match begins in `[lo, n)`: NOMATCH for the range |
| ALL_PRESENT (a presence site) | VERDICT (and, under ASSIGN, the leftmost hit of `preds[ret_pred]`, unchanged) | Every REQUIRED predicate occurs somewhere in `[lo, hi)`. No window fields: such spans state `window_stated` 0, which R17-a already requires on non-FIND sites |

- **Why no span index (W8).** Every span's offsets share the origin, so `L`
  and `U` mean the same thing whichever span located them. pcrec needs `U`
  (or nothing) and never the span.
- **Resume point.** A consumer that rejects every start in `[L, U]` calls
  the site again with `lo = U + 1`. This is sound: a match beginning after
  `U` carries a later occurrence of the located span, because `d ≥ omin`.
- **REQUIRED, for more than one span.** A returned window is CONSISTENT with
  every REQUIRED span: there is some start `m' ∈ [L, U]` at which each
  REQUIRED span occurs within its offset interval. A REQUIRED span the kit
  did not locate with must still be checked by the kit, which is direction
  (1) of [KIT-VERIFY] (§4.3).
- **A bounded span's presence is part of FIND.** A FIND that misses has
  proved the span absent from the range. So the pre-check that the K82/L1
  handoff fuses today (presence plus location in one pass) is simply a FIND
  with the landmark as a span: `move_back = K`, and an `overshoot` the
  producer can now compute. The kit's reply replaces pcrec's `c - K` text,
  which is the R-18 re-routing of the handoff that setfind §2.1 already
  foresaw.

### 2.5 The degenerate cases, in these fields

| site today | spans | `move_back` / `overshoot` | reply |
|---|---|---|---|
| PF FIND, DFA hat, VM hat (R-17) | one span, one position, class `S` | 0 / 0 | WINDOW, `L` = the candidate (`U = L`) |
| MLINE `(?m)^` | one span at offset -1, class `{\n}` | -1 / 0 | WINDOW, `L` = the hit + 1 |
| offset-skip FUNC | one span: the k-set positions 0..k | 0 / 0 | WINDOW, `L` = the candidate |
| run pre-check (unbounded offset) | the run, as a presence span | none (window_stated 0) | VERDICT |
| K82/L1 handoff | the landmark span | K / K - omin | today: a VERDICT plus pcrec's `c - K`. At R-18: a WINDOW |

## 3. Object B: the ANALYSIS object

### 3.1 Shape (spellings PROPOSED; the layout is the kit's to finalize)

```c
#define MF_ANALYSIS_LIST_V 1        /* the LIST's own shape, not any kind's */
typedef enum { MF_PROV_PRIOR_AUTHORED, MF_PROV_PRIOR_NONE,
               MF_PROV_MEASURED } mf_prov_source;
typedef struct {
    uint8_t     source;     /* mf_prov_source                                  */
    const char *bundle;     /* MEASURED: the answering bundle; PRIOR: "default" */
    uint64_t    digest;     /* what was consumed: pcrec_find_byte_rate_digest,
                               the value `<PREFIX>_FINDINGS` reports; 0 under
                               PRIOR_NONE                                      */
} mf_prov;
typedef struct {
    const char *tag;        /* the [FINDINGS] query name: "byte-rate", ...     */
    uint32_t    version;    /* this kind's payload shape                        */
    uint8_t     present;    /* 1 PRESENT, 0 explicitly ABSENT                   */
    mf_prov     prov;
    const void *payload;    /* per tag; NULL when absent or PRIOR_NONE          */
} mf_akind;
typedef struct mf_analysis {
    uint32_t        list_v;     /* MF_ANALYSIS_LIST_V                          */
    uint16_t        nkinds;
    const mf_akind *kinds;      /* every kind THIS pcrec knows, by tag         */
} mf_analysis;
```

The site reaches it as `mf_site.analysis`, appended last (D162 ruling 1);
NULL is "none stated" and is legal only for a stand-alone K3 caller.

### 3.2 The kinds today, and their provenance

| tag | when present | provenance | payload |
|---|---|---|---|
| `byte-rate` | ALWAYS (D162 add. 2) | `measured` (bundle, digest) when a `--analysis` block answers; `prior-authored` ("default", digest) under `-e byte`, which is `default.rxt`'s unigram block; `prior-none` under any encoding no shipped block serves, which today is `-e utf8` | `uint32_t ppm[256]`, summing to 1,000,000 (`pcrec_find_normalize`'s rule). NULL under `prior-none` |
| `run-rarity` | when a bundle's `bigram` block answers ([FINDINGS] B4, not landed) | `measured` only | B4's shape; the kit sees the kind only once a row reads it |

- **Why `prior-none` carries no table.** pcrec's own answer with no data is
  per question kind (D126 Q4): MASS is cardinality, PICK ties to its
  reader's rightmost, and COMPARE is false. A uniform table would answer
  COMPARE "true" for every pair, which is a density claim no data supports.
  It is also the "false confidence" Frank warned against (D162 add. 2). So
  the kind ARRIVES, which honours D162 add. 2, and its provenance states that
  pcrec's prior here is the no-information answer. The kit spells those
  per-question answers for its own questions. When D160's authored utf8 prior
  lands, the utf8 kind becomes `prior-authored` with a table. That is an abi
  event only where a kit row reads the kind (§8 example i).
- **Evidence.** A row that needs EVIDENCE (D162 add. 1's decline on positive
  density) reads only `measured` (D162 add. 3).
- **`cpfreq` is never a kind.** The kit is encoding-blind (D147 add. 14), so
  pcrec derives the byte-domain kind (`encode-utf8` is already the
  derivation, `findings.c:188`) and sends that.

### 3.3 Rules

1. **Keyed by tag, never positional.** The kit looks a kind up by its tag. An
   unknown tag is IGNORED. A known tag whose `version` the kit does not serve
   reads as ABSENT.
2. **Every kind this pcrec knows is LISTED, present or absent.** An absent
   entry is the explicit absence D162 asks for. A tag missing from the list
   can only mean an older pcrec, and the kit treats it as absent too. The
   two cases never differ in behaviour; listing makes the absence visible in
   a trace.
3. **One object per compile attempt.** pcrec builds it from `Job.find`, which
   is per attempt, at the first site ask. Every site of one `mf_art` states
   the SAME pointer. The kit refuses a site whose pointer differs from the
   art's first ("one analysis object per compile"), which turns D162's "one
   per compile" from a convention into a check.
4. **The per-site slot stays RESERVED** (D162 ruling 1). No field is added
   until a measured case needs a fact the kit cannot derive.
5. **Totality.** Every kit selection is TOTAL when the object, or any kind
   in it, is absent or `prior-none`. The no-data path is a stated decision
   (D162 ruling 2; R-17's ADMIT, D162 add. 1).
6. **Lifetime.** The object lives in pcrec's arena until the attempt ends,
   which outlives `mf_art_end`.

### 3.4 What the object is not

It holds no per-site answers: not a set's mass, not a ranking, not a
survivor estimate. Those are derived by the kit (D162 add. 3's rule: a
derived fact pcrec computes only to hand over is the kit's to derive). It
also holds no consumer price (D161 add. 6).

### 3.5 The kit's per-compile memo (D162 add. 4)

- **What.** Anything the kit derives from the object: cube masses, a byte
  order, a site's run ranking (§6 S2).
- **The rule.** The memo is a PURE function of `(analysis object, the art's
  kit options)`. A site's text therefore never depends on which sites were
  rendered before it.
  - **The check** shares no source with the memo: a test build renders every
    corpus artifact's sites twice, in forward and in reverse site order, into
    two fresh arts, and compares each site's text.
  - **Its sabotage row:** a memo that is filled lazily from the first site's
    term (order-dependent).
- **Where: keep it in `mf_art` (per ATTEMPT).** The `mf_art` comment says
  "one per Job ATTEMPT (the size ladder re-emits)". The object itself is per
  attempt (`Job.find`), so a per-attempt memo is trivially keyed right, and
  it costs one rebuild per ladder attempt over 256-entry tables.
- **Trigger to move it per compile:** a measured compile-time cost of the
  memo build above the noise of a minimal compile. At that point it would be
  keyed by the `byte-rate` digest, in kit state passed to `mf_art_begin`
  (D77; no such cost has been measured).

## 4. The kit's job: a chain of simple searches

### 4.1 One or two links (D161 add. 5)

The kit's plan for a site is a CHAIN.
- **Length 1:** scan one span (the best tool for it), then verify.
- **Length 2:** scan a rarer span B, then search the bounded region where an
  earlier span A must lie (§2.3's tight interval), then verify.

Which spans, which positions, which tool, whether to verify an OPTIONAL span,
and whether to search at all are all the kit's (D161, D161 add. 6).

**The no-search arm** is `L = lo`, `U = lo + overshoot(span 0)`: the
consumer meets every byte. It is total, so every site renders even when no
link pays (D162 ruling 2). It is the kit's DECLINE. pcrec never asks for it.

Storage belongs to the SITE, not to a link (§7, storage).

### 4.2 The 3+-link extension (specified, not built)

- **The one extra fact Frank named** (D161 add. 5): "fallback/overshoot to
  previous span, not just start of function". That is each span's distance
  to the PREVIOUS span, rather than only to the origin. The sequence rule
  supplies it exactly, for every pair (§2.3). So the extension adds NO site
  field. What it adds is kit-internal:
  - **Resume semantics.** When link `k` fails at a candidate of link `k-1`,
    the chain resumes link `k-1` at its next candidate inside link `k-2`'s
    region, not link 1. Soundness: a match whose link-`(k-1)` occurrence is
    the failed one cannot exist, and every other occurrence inside the
    region is still enumerated in order.
  - **Its G2 family:** generated 3-span sites with planted region
    off-by-ones, against the byte-loop oracle.
- **Trigger (D77):** a real pattern whose best 2-chain still loses to a
  measured 3-chain twin. No such cell is known; wingame §2.1 found 18 of 327
  patterns with two or more bounded spans.

### 4.3 [KIT-VERIFY]'s two directions

**(1) pcrec → kit, "verify span k".** This is `need = REQUIRED` on span k
(§2.4), which already exists in the vocabulary. It is a requirement on the
REPLY: every returned window is consistent with span k. It never names a
method; the kit chooses memcmp, a class compare or a fused form. pcrec marks
a span REQUIRED where its consumer would otherwise re-test it. Everything
else stays OPTIONAL, so the kit keeps the freedom to skip a dense span.

**(2) kit → pcrec, PROVEN FACTS** (a new channel):

- **What it carries.** `mf_result.proven`: for each span `k`, a bitmask of
  that span's positions which the CHOSEN FORM verifies at every window the
  site returns. It is reported through `mf_defined` (STATIC, known at define
  time).
  - It is defined only for spans whose offset from `L` is FIXED: `overshoot`
    0, so the occurrence lies at `L + omin`. For any other span the mask is 0
    in v1. A span with a runtime position needs a runtime `occurrence`
    out-hook, which is specified here, not built, and waits for a consumer.
  - A REQUIRED span's positions are proven by definition, so the mask
    reports the OPTIONAL positions that the form happens to verify (a fused
    pair, a whole-run compare).
  - The positions per span are bounded by a shape bound `MF_MAX_SPAN_POS`,
    derived from `PCREC_MAX_REQ_RUN_SCAN` (32) and asserted where pcrec
    builds a span, on `MF_RANK_MAX`'s precedent.
- **Exactness.** The kit must never over-claim. A form whose verification
  differs from candidate to candidate (an adaptive or stateful form that
  sometimes skips the verify) reports 0 for that position. Under-claiming is
  always correct.
- **How pcrec consumes it.** A first-match table decides, per span and
  consumer route (T-PROOF in §9):
  - DFA route, a prefix span at offset 0 whose proven positions `0..j-1` all
    hold exact bytes: pcrec starts the forward scan at state
    `δ*(s0, those bytes)` at `L + j`. That state is a compile-time constant.
  - DFA route, a proven position holding a class whose members lead to
    different states: pcrec does not use the proof.
  - VM route: pcrec enters the attempt past the leading instructions only
    where those instructions ARE the proven literal tests and open no
    capture group.
  - Anything else: the proof is ignored. A site whose consumer cannot use a
    proof still gets correct code (the [KIT-VERIFY] force).
- **Checks.**
  - **G2:** for every generated site and subject, at every returned window,
    every proven position holds (the byte-loop oracle).
  - **pcrec's trace build** re-tests every proven position it consumes, at
    run time.
  - **A sabotage row:** a form that sets a proof bit it does not test.
- **Events.** `mf_result.proven` is a layout change (an `MF_SITE_ABI` bump)
  with no byte moved. pcrec's first CONSUMER of it moves bytes, which is a
  pcrec abi event plus a deny of its own (`-fno-kit-proof`, PROPOSED). That
  is not built: [KIT-VERIFY]'s trigger, a measured consumer re-read cost on
  real cells, comes first.

## 5. The ONE pcrec-side producer

### 5.1 Today's derivations, read from `src/` (main `f3569b161`)

| derivation | function (file:line) | computes | becomes |
|---|---|---|---|
| necessary set + per-member max offset | `pcrec_req_walk` → `RbSet` (`src/facts/req.c:638`); facts `req_set`, `req_set_maxoff` | bytes every match contains; each member's max offset (`RbSet.off`) | one-position spans `{b}` with `omax`; the producer adds `omin` |
| the necessary run + its max offset | `pcrec_req_walk` → `RbRun` (`req.c:638`, `rn_better` ranking by information); `req_whole_run`, `whole_maxoff` | the most informative contiguous run, positions as cubes `(T, K)` | a multi-position span; `omin` added |
| run window | `pcrec_req_window` (`req.c:667`) via `pcrec_find_run_scan_index` / `pcrec_find_run_window_start` (`src/core/findings.c:522/:586`) | the scanned member and a truncation to ≤ 8 bytes, priced by the prior | a DECISION; moves to the kit (which positions to scan) |
| required byte | `pcrec_req_pick` (`req.c:709`) via `pcrec_find_set_pick` (`findings.c:476`) | which set member the `memchr` tests | DECISION → the kit |
| landmark K | `pcrec_fact_req_landmark_maxoff` (`req.c`, [REQ-HANDOFF-L1]) | the run window's K, else the req byte member's | the landmark span's `move_back`; `overshoot` added |
| set-leads | `req_set_leads_applies` (`src/gen/emit_dfa.c:7608`), a PICK over [run scan cube, set pick] | whether the set's pick leads the run | DECISION → the kit (lead order is the composite's form, integration.md rev 4.5) |
| landmark admission | `req_landmark_admits` (`emit_dfa.c:7810`) | re-entered handoff vs the start-byte row, priced by the prior | DECISION → the kit (two windows of one segment) |
| G1 | `req_byte_dominated_by` (`emit_dfa.c:7554`) | whether the DFA prefilter makes the pre-check redundant | DECISION → the kit, once the PF and PRE sites are one site |
| k-set walk | `pcrec_kset_walk` (`src/facts/kset.c:226`, E3, NFA from `anch_start`, assertions passed) | per fixed offset, the byte set every match carries | the prefix segment's classes; it stays as the producer's CONTROL (§5.3) |
| offset-k selection | `pcrec_prefix_ksets` / `model_cost` (`src/opt/prefix_k.c:179/:114`) | which offsets to scan/verify, under four measured cost constants | DECISION → the kit (D147 add. 4's M5 planner move) |
| run pin | `pcrec_run_pin` (`kset.c:298`) | the fixed offset at which the k-set spells the run window | a span with `overshoot` 0; its PICK goes to the kit |
| start set | `pcrec_start_set` (`src/facts/startset.c:141`, E2) | a superset of the first consumed byte | span 0's offset-0 class; it stays as a control and as pcrec's own fact (DFA hat, route) |
| widths | `pcrec_width_walk` (`kset.c:335`); `pcrec_minw`/`pcrec_cwmax` (`src/opt/mrl.c`) | byte width intervals | the arithmetic for `omin`/`omax` |
| run rank | `pcrec_find_run_rank` (`findings.c:553`) → `ofs_pred_rank` (`emit_dfa.c:1181`) | RQ-2's ranking | RETIRES (§6) |
| scan plan sent | `mf_pred.plan_hint`/`plan_pos` (`emit_dfa.c:1210-1228`) | pcrec's model's scan pick | RETIRES into the kit at M5 / R-18 (§6 S4) |

### 5.2 The producer

- **What.** One new CORE fact, `span_facts` (E2, on the lowered tree, so it
  reads the encoding, `-i` and `--ucp` by construction). Proposed owner
  `src/facts/spans.c`; no prior and no option read.
- **The walk** generalizes `rb_walk`'s per-subtree accumulators (head and
  tail runs to JOIN, `RbRun.off` from `maxw`) in two ways:
  - each subtree carries its spans as `(classes, omin, omax)`, with `omin`
    from `pcrec_minw` beside `omax` from the `maxw` arithmetic `req.c`
    already does;
  - an alternation contributes its branches' common HULL span (the
    `rn_common_head/tail` rule, cubes at most `pos_set`).
- **Output.** A list of SEGMENTS. A segment is the maximal stretch between
  unbounded items (an unbounded repeat or gap, a backreference, a call, a
  variable). Each segment holds:
  - its spans, sequential by construction (one flattened sequence, so
    `spans_seq` = 1);
  - its origin: the match start for segment 0, else the segment's start.

  The output also holds the PRESENCE spans: necessary sets and runs whose
  offset is unbounded, as `req_set`/`req_whole_run` have today.
- **The declines** are `req.c`'s, each for its stated reason: a lookaround's
  body is never descended; min-0 repeats do not join; a repeat's head and
  tail never cross an iteration.

### 5.3 Its controls (none shares the producer's source)

| control | expectation from | checks |
|---|---|---|
| C-SP1 prefix classes | `pcrec_kset_walk` (an NFA walk, E3) | segment 0's fixed-offset positions equal the k-set's sets wherever both are fixed (wingame's control: 582/582 positions on 166 patterns) |
| C-SP2 first byte | `pcrec_start_set` | segment 0's offset-0 class ⊆ start_set, with equality where no assertion precedes it |
| C-SP3 run / set | `req_whole_run`, `req_set`, `*_maxoff` | the most informative span equals the whole run; each set member's `omax` equals `req_set_maxoff` (until those facts retire into the producer, one reader per commit) |
| C-SP4 pairwise distance | a direct walk of the items between two spans (wingame `spans.rel_from_items`, 152/152) | the sequence rule's interval is exact |
| C-SP5 soundness | libpcre2 10.46 answers | every match's bytes lie in each span's class at an offset inside `[omin, omax]`, over the corpus's `m` cells, with a planted off-by-one control |

**K35 (who counts).** A floor on the number of artifacts carrying a multi-span
segment, read off a stamp-free census. The trigger population is wingame §2.1's
18 of 327; the floor stays a measured literal.

### 5.4 Which sub-problem pcrec sends: the CUT table (first match)

| row | predicate | sends | FINISH |
|---|---|---|---|
| `anchored` | `start_anchor` is BOT/GSTART | no window site | the attempt at the anchor |
| `rev-inner` | [ENG-TACTICS]'s own gates G1-G4 admit an inner segment (where_to_start.md, rincensus) | that segment, origin = its start | RECOVER reverse walk, then forward. pcrec's |
| `segment-0` | segment 0 has a span | segment 0's spans, origin = the match start | forward from `L` |
| `presence` | a presence span exists | a PRESENCE site (VERDICT) | the body as today |
| `none` | always | nothing | the attempt loop / every byte |

- **The table holds no prior.** `rev-inner` sits above `segment-0` only
  where its own admission passes. Frank's `a.*aaa.{2,5}zxq` is that row's
  case: segment 0 is `a`, and the inner segment is chosen by rev-inner's
  gates, not by a new price here. Q1 (§12) asks whether that is enough.
- **One site per segment.** Today, segment 0's facts reach the kit as
  several sites chosen by several rows: the PF FIND, the run-pinned
  offset-skip, the K82/L1 handoff gate and set-leads. Under this contract
  they are ONE window site carrying every span of segment 0. That is the
  "cross-site" opportunity Q42 named.

### 5.5 What stays pcrec's: the unbounded cuts

| cut | row |
|---|---|
| an unbounded head before the sent segment (`a.*` in Frank's example) | RECOVER `reverse-pass` / `landing` / `end-minus-width` |
| an end-pinned pattern | LOCATE `rev-end` (the reverse walk from `n`) |
| a landmark behind an unbounded gap | `rev-inner` ([ENG-TACTICS], filed) |
| no span at all | the attempt loop; the DFA stepping every byte |
| a backreference's relaxed language | `locate_finish.md` §4.5 (filed) |
| the VM hybrid's retry policy (step vs re-seed; R4 `cand_rs_dense_applies`, `emit_dfa.c:8789`) | RETRY, the [ADAPTIVE-ARM] family (chunk 5): a FINISH-side policy, not a window choice |
| unbounded-offset presence | the PRESENCE site's existence is pcrec's; its FORM is the kit's (wingame §8.4's tail gate) |

## 6. The retirement sequence

The rule (D162 add. 3 refinement): the frequency kind lands first, the kit's
own ranking second, the retirement third. The same three steps also carry the
other density fields that pcrec only forwards.

| step | what | movers | events |
|---|---|---|---|
| **S1** frequency kind | `mf_analysis` in `memfn.h`; `mf_site.analysis` appended last; pcrec builds the object per attempt from `Job.find` (`pcrec_find_byte_rate`, its digest, its bundle) and states it on every site; the kit's one-object check (§3.3 rule 3) | 0 (no row reads it) | `MF_SITE_ABI` bump; no pcrec abi event; no spec hunk (not caller-observable) |
| **S2** kit ranking | the kit derives each RUN term's position order from `byte-rate` in its memo (§3.5), applying the D126 Q4 per-question NONE answers under `prior-none`. IMPLEMENT beside `rank_*` with a shadow comparator: the kit's order equals `rank_pos` for every site of every corpus compile, at `-e byte` and `-e utf8`. Then REPLACE: `vrun`'s KB reads the kit's order | 0 (same order, proven by the shadow) | kit-only; no `MF_SITE_ABI` move; no pcrec abi event |
| **S3** retirement | delete `mf_pred.rank_n/pos/ppm`, `MF_RANK_MAX` and its `_Static_assert`, `ofs_pred_rank`, `pcrec_find_run_rank`, `rank_probe`; delete `mf_term.ppm_*`, `mf_site.cand_ppm_*`, `MF_PPM_FULL`, and the unread `mf_site.consumer`. Re-aim `make test-memfn-rank` to check the kit's order against its independent brute force. RQ-2's sabotage rows S731-S737 are re-aimed or retired, derived by `scripts/sabotage_anchors.py --step` | 0 | ONE `MF_SITE_ABI` bump (layout); no pcrec abi event; D80: none (internal) |
| **S4** the picks | `plan_hint`/`plan_pos` and the prior-reading decisions of §5.1 move into the kit with R-18's multi-span site: the req pick, the run window start, set-leads, the offset-k selection, the landmark admission, G1. Each is implement-then-replace at zero movers, then its own form event | per form event | each a pcrec abi event when bytes move, with its own `--memfn=` deny. Stamps that report a pick (`REQ_BYTE`, `REQ_RUN`, `DFA_PREFILTER`'s offset form) become kit-attributed; their readers are found by grep, including the byte-count reader class (D94 addendum) |

- **Consumer price.** It was never built, so nothing is deleted. The text
  retires:
  - setfind.md §2.2's W9 row is struck (§7);
  - wingame §5.5 item 2 and §7's first question are annotated SUPERSEDED by
    D161 add. 6;
  - [PRIOR-COST-UNIFY]'s operation-kind table keeps only its METERING plane,
    for [EFFORT-BUDGET]: the CONTRACT plane, not a price handed to the kit.
- **The memo** stays in `mf_art` (§3.5).

## 7. The kit's proposed facts: ratified or rejected

| item | verdict | reason |
|---|---|---|
| STORAGE capability (`decl_point` + `mf_locals`, one handle per site, automatic per-call storage, G-S1/G-S2 invariance, stem `<fn>_pf` with `<stem>__*` reserved) | **RATIFIED** as built at `MF_SITE_ABI` 11 | It is a host CAPABILITY, stated as a fact (D157), the mirror of `count_by_caller`. Dominance and invariance are checked (`-Wjump-misses-init`, const heads, the trace trap). One handle per site is what lets the VM hat's entry and retry share one cache. Under this contract storage belongs to the SITE, so a 2-link chain shares it. Cross-call state stays out (chunk 5) |
| window fields W0-W2 (`window_stated`, `move_back` signed from the span's beginning, `overshoot`; `omin` derived) | **RATIFIED**, extended to every span of a multi-span site, with one amendment: `MF_MOVE_UNBOUNDED` / `MF_OVER_UNBOUNDED` change from "reserved for R-18" to PERMANENTLY refused | D161 add. 5 rules unbounded out of memfn, so no row will ever define them. The macros stay as the refusal's name; the comment change moves no byte and no layout. "`move_back` = `overshoot` = 0 today" holds on every R-17 site (MLINE -1 / 0) |
| W3 (FIND's result is the window's beginning, never below `lo`, non-wrapping) | **RATIFIED** as `L` (§2.4) | `U` is added as an optional out-hook, and the miss is defined as NOMATCH for the range |
| W7 (FIND reads `preds` as further spans) | **RATIFIED**, with `spans_seq` (§2.3) | It is the multi-span shape. Without the sequence rule a 2-chain's region is loose |
| W8 (the reply names its span) | **REJECTED** | One origin for every span makes `[L, U]` span-independent (§2.4). An index would be a second spelling of `U` |
| W9 (consumer price) | **REJECTED** | D161 add. 6 |
| W10 (joint survival rate per span) | **MOVED** to the analysis kind `run-rarity` | A joint rate is a distribution fact (D162), present only when measured |
| N5 (shared per-width sub-blocks, stem `pcrec_mfk_`, guards `PCREC_MFK_W8_H` / `_V16_H` / `_V32_H`, no version, keyed by K80) | **RATIFIED** in the rev-2.3 form, plus one corollary | First-wins is correct per width because a sub-block's bytes are a function of its width within one abi. A mixed-abi translation unit already fails at K80's valued `PCREC_RX_ABI_H` `#error`, so a version or value in the kit's guards would be a second copy of K80's check. The block is emitted scaffolding: its first appearance (R17-b) and every later byte move are pcrec abi events. **The corollary:** pcrec also reserves the stem on the SUFFIX side. No emitted `<PREFIX>_<suffix>` may have a suffix beginning `mfk_`/`MFK_`, or `-p pcrec` would collide. Today none does (`grep -i mfk_ src/`: 0). A C-check over emitter strings holds it |
| N6 (refuse a prefix that, case-folded, is `pcrec_mfk` or begins `pcrec_mfk_`) | **RATIFIED** as built on `lane/r17b` | Every name is `<PREFIX>_<suffix>` and every macro is uppercase, so the bare stem and any case collide. One check serves `-p`, a `.rxt` target's prefix and `pcrec_options.prefix`. It refuses inputs only, so it is not an abi event. It is caller-observable, so it carries its spec hunks (cli.md §1.6¶1, match_api.md §8.0¶4) and a sabotage row. Its message is not a contract beyond naming the prefix (D26) |

## 8. Flexibility: what changes, and what is an event

### 8.1 The worked examples

**(i) A new analysis kind: `run-rarity`, when [FINDINGS] B4 lands.**
- **pcrec:** a `bigram` block that answers becomes one more `mf_akind`
  (`tag "run-rarity"`, `version 1`, `prov measured`). The query vocabulary
  already lists it (`findings.c:190`); the kind's payload type is added to
  `memfn.h` beside the list.
- **No other change.** No existing struct changes, so there is no
  `MF_SITE_ABI` move, no `MF_VOCAB` move and no site builder edited. A
  kit row that ignores the tag renders the same bytes, so pcrec's abi does
  not move.
- **Later.** The day a kit row reads the kind and moves a byte, that is the
  kit's FORM event: its own `--memfn=` deny, a pcrec abi event in the same
  commit, and G1 timing at both layers. A regeneration of the bundle's data
  that moves a byte is likewise an abi event (memfn/CLAUDE.md "What moves
  when data is regenerated").

**(ii) A new site parameter: BRANCH spans.**
- **The case.** `(?:GET|POST) /x`: a span exists only on some paths, a
  disjunction of windows (wingame §2.2, `alt-dropped` on 27/71 capability
  patterns).
- **pcrec:** the producer emits one span per branch and states `spans_seq`
  = 0 for them, plus a new fact. One candidate is `mf_pred.alt_group`: spans
  in one group are ALTERNATIVES, so a match carries one of them, not all.
- **The kit:** every row's honours allowlist is re-read. A row that does not
  honour `alt_group` declines on a site that states it (K96). G2's generator
  gains the field.
- **Events.** One `MF_SITE_ABI` bump (new meaning plus layout), landed in
  ONE commit on both sides (the kit is in-tree, Q36). A pcrec abi event
  follows only if a byte moves, which is when a kit row starts serving
  branch spans.

**(iii) A derived fact pcrec also uses, against one it only forwards.**
- **Sent always: the START SET.** pcrec uses it for its own route and DFA
  hat (`T = S ∩ E*`). So it rides every window site, as span 0's offset-0
  class whenever segment 0 has a fixed first position, and it is never
  sometimes-sent (D162 add. 3).
- **Kit-derived: the RUN RANKING.** pcrec computes it only to hand it over
  (`emit_dfa.c:1185` and a debug dump are its only uses), so the kit derives
  it (§6 S2-S3). The same holds for a set's mass (`cand_ppm`), a survivor
  estimate, and the choice of positions.
- **The test.** Does any pcrec DECISION read it? If yes, send it always. If
  no, it is the kit's.

### 8.2 Which change is which event

| change | `MF_VOCAB` | `MF_SITE_ABI` | pcrec abi | spec (D80) |
|---|---|---|---|---|
| a new analysis kind no row reads | no | no | no | no |
| a kind's payload shape changes | no | no (its own `version`) | only if a row's bytes move | no |
| a kit row starts reading a kind or a field | no | no | yes iff a byte moves, same commit, own deny | only if a stamp's meaning moves |
| bundle or prior data regenerated | no | no | yes iff a byte moves | no |
| a new site field (fact) | no | YES (layout + meaning) | yes iff a byte moves | no |
| a new reading of an existing field (W7's `preds` on FIND) | no | YES (meaning) | yes iff a byte moves | no |
| a new op, handoff or term kind | YES | YES | yes iff a byte moves | no |
| a field retired (S3) | no | YES (layout) | no (zero movers) | no |
| a refused input (N6) | no | no | no | YES |
| the kit's shared sub-block's bytes | no | no | YES | no |

## 9. First-match tables, and the sibling-of-a-family lens

Every selection this note introduces is an ordered first-match table:

| table | owner | rows (in order) |
|---|---|---|
| T-CUT: which sub-problem (§5.4) | pcrec | `anchored` → `rev-inner` → `segment-0` → `presence` → `none` |
| T-REPLY: reply type by op (§2.4) | contract | FIND → WINDOW; ALL_PRESENT → VERDICT; others unchanged |
| T-NEED: a span's `need` (§4.3) | pcrec | `the FIND definition requires it` (today's single-span terms) → REQUIRED; `pcrec's consumer cannot re-test it cheaply and wants it verified` → REQUIRED; `else` → OPTIONAL |
| T-PROOF: consuming a proven position (§4.3) | pcrec | `dfa-exact-prefix` → `vm-literal-prefix` → `ignore` |
| T-KIND: one kind's state (§3.2) | pcrec | `a --analysis block answers` → measured; `a shipped block serves this encoding` → prior-authored; `the kind is byte-rate` → prior-none; `else` → ABSENT |
| T-MEMO: where the memo lives (§3.5) | kit | `measured compile cost` → per compile, keyed by digest; `else` → `mf_art` |

**Families this touches (the sibling-of-a-family lens):**

1. **The prior-cost family** ([PRIOR-COST-UNIFY], 10 members derived by
   call graph; rev 2's census). This note splits it three ways:
   - the window choices go to the kit (§5.1, §6 S4);
   - the RETRY arm (R4, `vm_reseed_cal`) goes to [ADAPTIVE-ARM] (chunk 5);
   - the metering kinds go to [EFFORT-BUDGET] (chunk 6).

   No member is left as a lone pcrec-side reader of the prior that chooses
   among spans. That leftover is exactly the shape the forest-for-trees
   memory warns about.
2. **The start table's site-building rows.** Today PF FIND, `offset-set`,
   `run-pinned`, the handoff gate, `set-leads` and the req pre-check each
   build a kit site from one row of `cand_rows[]`. Under T-CUT they become
   ONE window site per segment, plus at most one PRESENCE site. The slots
   still decide WHERE a site sits; the kit decides what it searches.
3. **"A pick sent as a fact"**: `plan_hint`/`plan_pos`, `rank_*`,
   `cand_ppm`, `ppm_*`. These are one family by D162 add. 3's rule, retired
   by one sequence (§6), not one at a time.
4. **The reverse walks** (RECOVER `reverse-pass`/`landing`, `rev-end`,
   `rev-inner`). They are pcrec's unbounded cuts (§5.5), already one family
   under `locate_finish.md`'s parameterized reverse block. This contract
   leaves it intact.
5. **The kit's own row tables** (`pffind`, `precheck`, `fn_rows[]`, `arms`
   under `kit_walk`). A chain is a form of those tables, never a parallel
   planner beside them.

## 10. The three standing questions

1. **Measurement regime: RELEVANT, and no number decides this note.** The
   evidence it leans on is counts:
   - wingame's survivors, regions and policy flips, on the bench's 256 KiB
     throughput subjects (§2.3, §4.2);
   - the R-17 timings already read in setfind §13.

   No consumer price exists any more, so no regime-dependent price enters
   the contract. Every kit choice remains under its own regime rule (K-1;
   two-tier verdicts, D144 add. 4).
2. **Independent control: RELEVANT.**
   - The producer's five controls share no source with it (§5.3).
   - The proof channel is held to G2's byte-loop oracle and pcrec's
     trace-build re-test (§4.3).
   - The memo's order-independence is checked by rendering in two orders
     (§3.5).
   - S2's ranking is held to a shadow of today's `pcrec_find_run_rank` and
     then to an independent brute force.
   - K35: a multi-span floor (§5.3). [MECH-REACH]: every sabotage row named
     here (memo order, proof over-claim, region off-by-one, sequence-rule
     plant) gets a witness that reaches its site, derived at build time.
3. **What moves when data is regenerated: RELEVANT.** The `byte-rate` kind
   is `Job.find`'s answer.
   - A bundle or prior regeneration moves bytes only through a kit row that
     reads the kind, and then it is a pcrec abi event (§8.2).
   - The digest in each kind's provenance is the same value the
     `<PREFIX>_FINDINGS` stamp reports, so "which data built this artifact"
     has one answer.
   - D160's authored utf8 prior turns `-e utf8`'s kind from `prior-none` to
     `prior-authored`. That is a byte move only where a row reads it, and
     the S2 shadow covers `-e utf8` explicitly.

## 11. The R-18 outline (facts only; main files it)

**R-18: THE WINDOW SEARCH (D161), the general category**

- **Customer.** D161 and add. 1-6; chunk 3. It supersedes the per-shape
  interfaces of R-15 (the ASSIGN gate), R-17 (the set FIND) and the PF/OFS/
  PRE sites. Their forms and measurements carry over.
- **Facts pcrec will state** (docs/design/memfn/window_contract.md §2-§3):
  - a site is a bounded sub-problem with one origin;
  - spans are `mf_pred`s with stated `move_back`/`overshoot` and `need`;
  - `spans_seq` states the sequence rule;
  - the reply is `L` with an optional `start_hi` (`U`); a FIND miss is
    NOMATCH for the range;
  - presence sites carry no window;
  - `mf_site.analysis` (S1 above, possibly landed first): a `byte-rate` kind
    that is always present, with provenance.
- **Facts pcrec will NOT state:** a consumer price, a span index, a scan
  position (`plan_hint` retires), a ranking (`rank_*` retires), per-site
  rates.
- **Deliverable.** The kit's method is its own. It must:
  - serve every degenerate site at zero SIMD-off movers first (R-17's routing
    carried over);
  - then serve multi-span sites behind their own denies;
  - land each SIMD-off byte move together with pcrec's abi event in the same
    commit.
- **Capabilities pcrec provides:** storage as ratified (§7); proven facts
  consumed per T-PROOF only after [KIT-VERIFY]'s trigger.
- **Trigger.** This note, ratified. R-17's PF routing event merged.
  - The first multi-span consumer: the K82/L1 handoff re-routed as a
    window (§2.4), cells loglines/ipv6, ipv4, bounded/dotted4.
  - Then wingame's syslogbase-expanded and the refine witnesses.
- **Sequencing (main's).** S1-S3 (§6) may land before the R-18 build. S4
  rides it.
- **Capacity.** The migration thread.
- **Sabotage ids.** Main allocates at filing (consult `requests.md`'s
  reserved ranges).

## 12. Questions for Frank (discussion, each with a leaning)

1. **How pcrec picks the sub-problem when an inner segment beats segment 0.**
  - **The problem.** Your `a.*aaa.{2,5}zxq` example is a choice pcrec makes
    BEFORE the kit sees anything.
  - **The forces.** If pcrec prices the segments with the prior, the
    consumer-price problem comes back one level up. If it uses no price, it
    may send `a` and miss `zxq`.
  - **My leaning.** Let rev-inner's own gates (G1-G4, where G3 is
    structural; rincensus) decide when an inner segment is worth the reverse
    walk, and otherwise always send segment 0. A third path is to send both
    and let the kit say which it can search. I lean against it: that is a
    capability query, the K0 shape D146 retired.
2. **Proven facts only at fixed offsets (v1).**
  - **The leaning.** Report proofs only for spans whose offset from `L` is
    fixed. Leave the runtime `occurrence` out-hook (which would cover
    `overshoot` > 0) until a VM per-start consumer is measured to re-read
    proven bytes.
  - **The alternative.** Specify the occurrence now. That costs a runtime
    write per window on every site that states it, for a consumer nobody has
    timed.
3. **`U` (the start upper bound) now or later.**
  - **What it is for.** `U` matters only for a consumer that pays per start:
    the VM, or anchored attempts.
  - **The leaning.** Define it in the contract now, so `L`'s meaning is
    stated with its partner. Build it with the first per-start consumer,
    which is the handoff re-routed for VM hybrids.

## 13. What a light panel should attack

1. **The sequence rule's soundness.** Is every span the producer emits on
   ONE flattened sequence for EVERY path? Look in particular at:
   - hull spans from an alternation whose branches have different widths
     before the hull;
   - a min-0 repeat between two spans.

   Try to build a pattern where `[omin_j - omin_i, omax_j - omax_i]` excludes
   a real match.
2. **The NOMATCH-on-miss claim (§2.4).** A FIND that misses claims "no
   sub-problem match begins in `[lo, n)`". Check:
   - the range's end (`end_back`);
   - negative offsets (MLINE);
   - a REQUIRED span whose occurrence for a match starting near `n - 1`
     would lie past `n`.
3. **The resume point `U + 1`.** Is it sound when the located span is not
   span 0, and when two spans' occurrences interleave?
4. **`prior-none` with no table.** Does any shipped kit row read the
   frequency kind in a way that needs a table under `-e utf8`? Does S2's
   shadow really reproduce `pcrec_find_run_rank`'s NONE order (cube size,
   then rightmost) from the provenance alone?
5. **Proof exactness under stateful forms (R-17's mask).** Can a carried
   mask return a window at which an OPTIONAL position was NOT re-tested,
   while the form still reports it proven?
6. **The one-object-per-art check versus the size ladder.** Each attempt
   has its own `Job.find` and `mf_art`. Confirm that no site of one art can
   carry a previous attempt's pointer.
7. **The cut table versus today's rows.** Is T-CUT a re-expression of
   `cand_rows[]`'s FIRST/NEXT/PRESENCE rows, or a parallel mechanism (D82)?
   Name the row each T-CUT row becomes in `cand_rows[]`.
8. **The family split** (§9 item 1). Is any member of the prior-cost family
   left with no owner, or with two?
9. **An unlock lens** (memory `pcrec-critics-propose-unlocks`). Propose
   what the general form opens beyond today's sites, each with its trigger:
   - span-relative proofs feeding the DFA's start state;
   - presence absorbed into a chain link;
   - per-segment sites for `rev-inner`.
