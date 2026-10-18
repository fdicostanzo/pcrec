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
