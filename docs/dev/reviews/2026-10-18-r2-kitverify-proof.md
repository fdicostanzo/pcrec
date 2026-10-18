# Review r2 (2026-10-18): [KIT-VERIFY]'s span-0 proof — REQUIRED-by-default vs a proof effort level

Status: PANEL IN FLIGHT (three read-only critics). Nothing ruled; nothing built.

## 1. The proposal under review (manager, session 117, from the conversation with Frank)

Context: `docs/design/memfn/window_contract.md` §4.3 ([KIT-VERIFY]'s two directions),
D161 addenda 4-10, plan row [KIT-VERIFY] (scope: the INITIAL pinned span only, Frank s115).
Today's design: (1) pcrec marks a span `need = REQUIRED` where its consumer would re-test it
(T-NEED), else OPTIONAL; (2) the kit returns a static per-position bitmask `mf_result.proven`
per fixed-offset span (≤ 32 positions), layer-invariant (C-PROOF). `proven0` (a byte set at
offset 0, via the define-time query `mf_ask`) is already BUILT (kit B1-B3).

The manager proposed, as a D161 addendum:

- **P1.** An EXACT span 0 is always REQUIRED. Argument (Frank's): span 0 must be tested by
  someone at every candidate; the test costs no more in the kit than in pcrec; a failure in the
  kit's loop is a `continue`, while a failure in pcrec's consumer is a handback (attempt entry,
  stream re-entry; the K82 handoff ~4.6 ns/call, K88), so testing in the kit wins.
- **P2.** The proof becomes ONE integer per site, `proven_len`: the contiguous proven-prefix
  length from the origin, replacing the per-position mask. Reason (Frank): a DFA cannot skip
  bytes after an unproven gap (it advances one byte at a time), a report needs the whole
  sub-problem, the VM's gap-skipping is marginal.
- **P3.** A compile-only census of sites whose consumer can start past `proven_len`, by
  consumer kind (plain DFA, VM literal prefix, direct report).

## 2. Frank's concerns and counter-proposal (verbatim intent)

- **C1.** Making span 0's proof REQUIRED will slow the candidate-search algorithm.
- **C2.** It bakes complicated class tests into the candidate search, requiring double code
  (the class test emitted in the kit's search AND still in pcrec's engine).
- **C3 (counter-proposal).** Instead of REQUIRED, a LEVEL OF EFFORT to prove the first span.
  The kit can still test SUPERSET classes for speed. Then `proven_len` has meaning; under P1 it
  would always equal the length of span 0.
- **C4.** "Span" is artificial here: pcrec constructs spans. E.g. `abc\d{3,7}`: pcrec's first
  span is length 6 (`abc\d\d\d`), while by the pattern's literal structure it is length 3.

## 3. Panel

Critics (read-only, never run `make`): kvp-cost (search cost and code duplication), kvp-contract
(contract semantics, span construction, invariants), kvp-unlock (general form, sibling family,
unlocks). Findings and dispositions follow below once delivered.

## 4. kvp-unlock (sonnet): general form, family, unlocks

Delivered in four parts (a safety classifier cut the first reply mid-table; the rest was re-asked
narrowly). Summary of record:

- **B1.** `proven_len` is the third-consumer trigger of plan row [MATCH-KNOWN] (one general record of
  what is known about the subject at each emitted point; its member list names the kit's proven facts).
  Build it as that record's first member, never a private field.
- **M1.** An integer prefix is a projection of the per-position fact and loses the proven suffix
  ([PF-KNOW]'s trailing segment), the landmark position (K82/L1 handoff) and the gap pattern. Keep a
  per-position byte set (`proven0` generalised to `proven[k]`, plus −1 = `proven_prev`) with an exact
  flag; pcrec derives prefix length / covers-all / contains-p / suffix in ONE helper read by T-PROOF.
- **M2.** P1's circularity (REQUIRED iff the consumer re-tests; re-test iff unproven) already has a
  designed break: the pure define-time query `mf_ask`. Ask with OPTIONAL, read what the kit proves, re-ask
  REQUIRED only where a T-PROOF row wins. Answers Frank's C1.
- **M3.** An effort level is either OPTIONAL + the query, or a return of consumer price (D161 add. 6);
  a later price-based effort belongs in a kit row reading a measured D166 quantity.
- **M4.** P1/P2 build ahead of [KIT-VERIFY]'s own trigger; P3 first and alone, reporting the prefix-length
  distribution, sites with proven positions outside the prefix, and a savings bound. From armread
  (~0.19 ns/B DFA vs ~4.6 ns re-entry) a short prefix cannot pay on the DFA path; report-without-engine
  is the real win.
- **M5.** Frank's P1 rationale (kit loop `continue`, "no more in the kit") is method/cost; keep it in
  the review, not the contract text; "no more in the kit" is unmeasured.
- **m1** the fact's domain is fixed-offset positions; **m2** `proven0` (a byte set) vs §4.3's bit
  (holds exactly as requested): only positions ≥1 carry new data; **m3** the proven length is relative to
  pcrec's span cut, any census states its cut; **m4** pf_know measured DFA/VM class-table sharing at
  3.4 KB corpus-wide, bounding C2's size cost (re-measure kit vs engine); **m5** §4.3's consumption
  conditions bind any prefix consumer; a decreasing meter vs D158/GIVEUP1 is open.
- **Family (12):** `proven0`, `proven_prev`, PRES `proven_by`/P2 `dominated`, `mf_result.proven`,
  `proven_len`, `mf_site.span_lo/hi`, LOCATE×FINISH's proven bit, the K82/L1 handoff, [PF-KNOW] segments,
  [START-LANDING], MRL `minw`/[VM-LEN-HOIST], the D164 end set — all under [MATCH-KNOWN].
- **Unlocks:** U1 report without an engine (trigger: P3's whole-cover count); U2 DFA entry past the proof
  (P3's prefix-length quantiles vs ~0.19 ns/B); U3 VM entry past literals + length hoist ([VM-LEN-HOIST]
  twin; meter-decrease ruling); U4 `proven_prev` lifts the seeded-machine decline (P3 count); U5 the three
  "dominated" spellings become one containment test (B3b); U6 list the per-site proven set in
  `--emit-facts` (P3 itself).
- **Facts-only:** P1 yes (rationale out of the text); P2 yes but consumer-shaped; C3 no as phrased
  ("superset tests allowed" is method), yes restated as OPTIONAL + query.

## 5. kvp-contract (opus): contract semantics, span construction (SUPERSET addendum folded in)

Evidence at main b39a69c2e; greps and single-pattern compiles only. Delivered in four parts (inbox
truncation at ~4.5k chars).

- **Span today (C4 confirmed).** No `span_facts` producer exists; each site builds its own `mf_pred`.
  One-byte FIND sites: one REQUIRED term at offset 0 (`emit_dfa.c:6548-6553`). Offset-set / run-pinned:
  only `prefix_k`'s chosen offsets, need mixed per term (`emit_dfa.c:1212-1237`). `abc\d{3,7}`: req_run 3
  (`abc`), kset_walk 6 fixed positions, the planned producer 3 or 6 by construction choice. `abc\d\d\dx`
  sends `0,6*`; `a\d{2}bc` sends `0,3*,4`; utf8 `[α-ω]xyz` sends `0,2*`.
- **B1.** P1 contradicts D161 add. 14: obligation 6 allows the unconstrained (NONE) reply only if span 0
  is OPTIONAL; nearly every one-byte site's span 0 is trivially EXACT, so F0 NONE (B5) becomes illegal.
  The only coherent repair, "REQUIRED when the kit scans", reduces P1 to the point C3 contests.
- **M1.** P1/P2 tie obligation and proof to the CUT; define the proof over origin offsets d instead;
  `proven_len` = largest L with every d < L covered and exact; an uncovered position ends the prefix.
- **M2.** P1 would force 7 tests where `prefix_k` chose 2 (`abc\d\d\dx`) once spans become exact;
  today's gap-filled span is SUPERSET so nothing changes yet. Run-pinned already double-reads (prefilter
  verifies the run, the DFA re-reads; `\bfoobar` cannot skip). New duplication only for CLASS positions.
- **M3.** C-PROOF's every-deny clause is stronger than its SIMD-neutrality reason and, under C3 (NONE
  reachable by a deny), forces every proof to nothing. Fix: layer-invariant, deny-VARIANT.
- **M4 (latent over-claim, built code).** `kit_class` intersects EVERY offset-0 term into `proven0`
  regardless of `need` (`memfn/src/compose.c:310-323`); correct today only because every FIND site has
  one REQUIRED term and the generic arm tests every term (`generic.c:25`). Any C3 adoption must make
  `kit_class` honour `need` / the committed set.
- **M5.** P2 as a REPLACEMENT is lossy for built readers (R4 prices the proven0 SET's mass; G1 reads
  the set). Keep per-offset SETS; derive `proven_len` pcrec-side.
- **M6.** REQUIRED on VM_ATTEMPT and presence spans is give-up safety (K64/K65, C-13, D158), not effort;
  an effort level is advisory (refused by add. 4) or REQUIRED on a prefix = per-term `need` (built,
  `mf_term.need`, memfn.h:386), matching C-14 ("need is the EFFORT fact"). A kit-chosen effort needs the
  handback price add. 6 dropped.
- **S1 (SUPERSET addendum).** `byte_form` is design-only (no field or setter), yet most multi-position
  sites send supersets in practice (gaps, k-set unions, utf8 continuation bytes). Exactness is a property
  of a PREFIX: d is exact iff the cross product of sets 0..d equals the language's length-(d+1) prefixes
  (`[α-ω]` exact at length 1, SUPERSET from 2). No kit effort proves the language past that point (the
  kit is encoding-blind). usable = min(contiguous proven-as-sent prefix, `exact_len`), `exact_len` ONE
  pcrec-stated fact replacing `byte_form` (needs an UNSTATED encoding: 0 is legal). Membership proofs
  past it stay useful to R4/G1.
- **S2.** Span-level P1 on a partly exact span loses REQUIRED on the exact prefix; REQUIRED-as-filter is
  meaningful on superset positions (K64); only REQUIRED-as-verify needs exactness. Rule: verify/proof as
  language only below `exact_len`.
- **S3.** Effort beyond `exact_len` cannot raise what consumers use; past it tests only filter.
  Layer invariance holds under the floor rule provided SIMD forms only add guarded text.
- **m1-m6.** REQUIRED has two meanings (filter vs verify); contract states need per span, code per term;
  the DFA row covers literal positions only (class positions help VM/report only); MLINE has no span 0
  (`proven_prev` is its proof); a hybrid's two sites re-test span 0; T-NEED's middle row already
  approximates P1 and its only discriminator on a DFA consumer is "wants".
- **Verdict.** P1+P2 coherent but nearly empty (= `exists` × len(span 0), what proven0 already says),
  couples cost to the cut, breaks add. 14. C3 is right that the information is what the kit proves beyond
  its obligation, but an effort level adds nothing over per-term need. Recommendation: need per position;
  REQUIRED only where K64/K65 demand it or a consumer cannot skip; the kit commits layer-invariantly to
  per-origin-offset proven SETS; pcrec states `exact_len` and derives `proven_len`; the cut drops out.
- **Unlocks.** U1 one proven-at-offset array `proven[d]`, d in [-MF_MAX_BACK, MF_MAX_SPAN_POS) (trigger:
  [KIT-VERIFY]'s build); U2 class-uniform DFA skip (a timed class-led cell); U3 a pcrec-owned measured
  handback quantity in a D166 set so the kit can choose verification by price (a cell where tool-cost-only
  loses to always-verify); U4 offset-pinned union spans raise `exact_len` through a narrow multi-byte
  class (add. 10's first losing utf8 cell inside a VM/report consumer's prefix).

## 6. kvp-cost (opus): search cost and duplication (SUPERSET addendum folded in)

Derivations plus three `build/pcrec -o -` emits and two `gcc -O2 -S` probes; no timing. Five parts.

- **B1.** P1 makes NONE illegal on every EXACT-span-0 site (obligations 4/6; F0's gate,
  r17b_prime.md:458), against D161 add. 14 and §4.3(1). The dense regime NONE exists for is measured
  (opt3 `t-b`: skip loop entered 190,651 times, zero bytes skipped; K88 +4.6 ns/match for an
  always-passing test; K90; k82b §1.1; D161 add. 2 up to 24% at 300k ppm). Frank's C1 at its sharpest.
- **M1.** P1's continue-vs-handback mechanism is a measured null on DFA consumers: both sides pay the
  same memchr re-entry (`rx_ofsskip__body` loops `pos = cand + 1`), so the kit saves only the false
  start's DFA steps; offset_k §7.4 measured that verify-without-scan-move at 0.96-1.02x. The 4.6 ns K88
  figure I cited is an ADDED test on a PASSING candidate: evidence for C1. P1 holds on VM_ATTEMPT,
  already REQUIRED (C-13).
- **M2.** "No more in the kit" is false against a DFA that does not consume: its step is paid anyway, so
  the kit's test is added work (branchy: C_MISPRED × min(p,1−p); branch-free: ~192 instructions per
  candidate for 32 positions). `\b[0-9a-f]{32}\b` cannot consume (`\b` is a context view).
- **M3.** Payoff on a minority, cost on all: `ac\d|bc` has span 0 `[ab]c` fully verified but δ(0,a)=5,
  δ(0,b)=10 (not consumable); pf_know: leading choice-free segment empty on 32 of 47 bench hybrids, twins
  x1.000-1.13.
- **M4.** Under P1 the span cut becomes the effort level (rewards under-sending, inverts add. 9/D157):
  `abc\d{3,7}` offset-skip 38 → 49 instructions (+29%); `proven_len` = |span 0| always.
- **M5.** Match-dense find-all pays P1 on every match where unconsumed: ~a fifth of DFA C_match at
  m=8192 (armread Zen 4, derived).
- **M6.** P1 moves bytes ahead of [KIT-VERIFY]'s D77 trigger; C3 with default "test what today's form
  tests" moves nothing.
- **m1 (C2 counted).** New executed tests: `abc\d{3,7}` +3 range tests, `ac\d|bc` 0, `[a-z]+@x` 0,
  `\b[0-9a-f]{32}\b` up to +29 probes. No UTF-8 decoding (non-product classes are SUPERSET); no duplicated
  data (ofsskip probes pcrec's table by name), though a class pcrec has not tabled may need a new
  membership table (pf_know bounds sharing at 3.4 KB). pcrec's copy is KEPT even when consumed (DFA
  tables, reverse pass, VM instructions). **m2** a REQUIRED class position declines the SIMD rows (no
  vector class verify); **m3** wide classes reject ~nothing; **m4** back-search through overshoot makes
  REQUIRED cost overshoot+1 probes per hit, a wash with OPTIONAL on DFA_SCAN; **m5** per-span byte_form
  makes `abc[α-ω]` prove nothing.
- **SUPERSET.** A SUPERSET position proves nothing; testing it pays only if added rejection × saved DFA
  steps > one probe per candidate. UTF-8 continuation positions reject zero candidates on well-formed text.
  P1 handles a pure-SUPERSET span 0 only because its wording excludes it, and a mixed span badly.
- **Verdict.** Restated C3 weakly dominates P1 (P1 = need all-ones), strictly on B1, M2-M5 and mixed
  spans, ties on VM_ATTEMPT. As true facts: per-position `need` (REQUIRED only where D158/K64-K66 demand),
  per-position `consumable` (pcrec will not re-test if proven; known before asking), per-position `exact`;
  the kit chooses the rest from its measured data and reports proven ⊇ need. kvp-unlock's `mf_ask`
  two-pass needs the consumable fact or the kit under-tests the positions whose proof pays.
- **Unlocks.** U-a per-position need/consumable/exact masks, proven ⊇ need, proven ⊆ exact (trigger: P3
  finds consumable proven positions beyond offset 0 at bench sites, or mixed utf8 spans); U-a′ byte_form
  per position; U-b `delta_uniform[j]` (every byte of span-0 class j drives the forward start path to one
  state), computed from built tables, T-PROOF's DFA precondition and P3's consumable column (false at j=0
  for `ac\d|bc`, true at all six for `abc\d{3,7}`).

## 7. Synthesis and proposed dispositions (manager, pending Frank)

All three critics converge; nothing in the panel defends P1 or P2 as worded.

| item | disposition |
|---|---|
| P1 (EXACT span 0 always REQUIRED) | WITHDRAWN (kvp-cost B1 = kvp-contract B1; M1-M6) |
| P2 (`proven_len` as the transported fact) | WITHDRAWN as transported; KEPT as a pcrec-derived projection |
| C3 (effort level) | ADOPTED IN SUBSTANCE, restated as facts (below) |
| C4 (span cut artificial) | CONFIRMED; the proof is defined over origin offsets, the cut drops out |
| SUPERSET (Frank) | CONFIRMED; exactness per position/prefix replaces per-span `byte_form` |
| kit `proven0` ignores `need` (kvp-contract M4) | FINDING to the kit (latent; must be fixed before any OPTIONAL term reaches a FIND site) |
| C-PROOF every-deny clause (kvp-contract M3) | ACCEPT: layer-invariant, deny-variant |
| home | [MATCH-KNOWN] (kvp-unlock B1): this fact is its first built member |
| P3 census | FIRST and alone, compile-only, with the critics' columns |

The restated design: pcrec states per origin offset d (from −1) the `exact` bit (from its lowering),
`need` (REQUIRED only where give-up safety K64-K66/D158 or a non-skipping consumer demands it), and
possibly `consumable` (open question Q1); the kit commits, layer-invariantly, to per-offset proven byte
sets (`proven[d]`, generalising `proven0`/`proven_prev`) with proven ⊇ need and proven ⊆ exact, choosing
what else to test from its own measured data; pcrec derives prefix length / whole-cover / suffix in one
helper read by T-PROOF.

Open for Frank: **Q1** does pcrec send `consumable` (a binary fact about its consumer, not a price), or
does it discover it by the `mf_ask` two-pass (ask OPTIONAL, re-ask with need on positions whose proof a
T-PROOF row would consume)?

## 8. Rulings (Frank, 2026-10-18) and dispositions applied

Frank agreed the synthesis (§7) and answered Q1 by asking why per-position need beats "please prove up to
N": every consumer consumes a PREFIX, so the request collapses to one number, `consumable_len` (a
statement, not an order; capped by the exact prefix). Per-term `need` stays for give-up safety only. He
then extended the design: spans may precede the origin, so any fixed lookbehind, and `\b` rewritten by
position (`\b` before a word character ≡ `(?<!\w)`), joins the sent sub-problem, and the kit's candidate is
the actual match start. Recorded as **D161 addendum 16**. Applied: plan rows [KIT-VERIFY] and
[MATCH-KNOWN] (status lines); kit finding M4 filed as **R-25**; census launched as lane **kvcensus**
(compile-only, P3 with the critics' columns plus context-span and whole-cover columns). Open follow-up:
does pcrec already rewrite `\b` by position? (the census answers it).
