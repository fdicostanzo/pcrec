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
