# window_contract — what pcrec tells the kit about a search site and a compile (D161, chunk 2)

Revision 1: lane `d161note`, 2026-10-12, from main `f3569b161` (pcrec abi 76).
**Revision 2: lane `wcrev`, 2026-10-12, from main `76067df80`.** It applies
the light D6 panel r4 (`../../dev/reviews/2026-10-12-r4-window-contract.md`,
1 blocker, 10 majors) and Frank's rulings D161 addenda 7-8 (the finder STREAMS
exact span-0 starts; proven facts are KEPT as a layer-invariant compile-time
statement). Kit branches read with `git show`: `lane/memfn-r17` (now
`f1cf102c5`; R17-a, `MF_SITE_ABI` 11) and `lane/r17b` (now `174f3e320`;
R17-b, `MF_SITE_ABI` 12, N6). Neither is merged to main. DESIGN ONLY: nothing
under `src/`, `cli/`, `lib/`, `memfn/` or `tests/` changes, and nothing was
run.

**Revision 2.1: lane `wcrev2`, 2026-10-12.** It applies D161 add. 9 (see §R2.1).

**Revision 3: lane `wcrev3`, 2026-10-16, from main `063b4a4b4` (pcrec abi 78).**
It is the design main's build step **E-1** implements (§3.7). It applies the
kit's winreq C-items C-1..C-16 (`lane/memfn-r17:docs/dev/lanes/winreq_report.md`
§4) and R17-b′ revision 2 (`lane/memfn-r17:docs/design/memfn/r17b_prime.md`,
`c90d65e53`, §3-§4). It also applies D161 add. 10-15, D162 add. 4, D166 (+ add.
1-2) and D167, and the kit's relayed sequencing (B1 declares the slot, E-1 fills
it after B2). Read §R3 first. DESIGN ONLY: nothing under `src/`, `cli/`, `lib/`,
`memfn/` or `tests/` changes. One compile-only census was run
(`window_contract_rev3/`).

**Revision 3.1: lane `wcfix`, 2026-10-16, from main `2288ad1cb` (pcrec abi
78).** It answers the light panel r4
(`../../dev/reviews/2026-10-16-r4-window-contract-rev3.md`: 1 blocker, 5 majors,
6 minors, all ACCEPTED by the manager) and Frank's Q3 ruling (D167 add. 2:
CONSULTED). It adds the manager's finding X1, an independent PERTURBATION check
of the stamp (§3.7.7 C-PERT). Read §R3.1 first. DESIGN ONLY again, plus two
compile-only censuses and one prototype run on main's binary
(`window_contract_rev31/`).

**Status: PROPOSED, revision 3.1.** Q1 (§12) is ANSWERED by D161 add. 9; Q2 is a
leaning; **Q3 is RULED (D167 add. 2: CONSULTED)**; Q4 is the manager's; Q5 and
Q6 are new and in discussion form. Q5 asks whether a kind's provenance may be
read from the answering block's own declared `provenance` stanza (the design of
record, pending the ruling). Q6 asks what the stamp records when a compile takes
more than one attempt. The R-18 ledger edit (§11, Appendix A) is main's to
apply.

The contract carries FACTS only, never the kit's method (D157). Every
selection below is an ordered first-match table (memory
`pcrec-decisions-as-first-match-tables`). Revision-2 changes are tagged
`[r4 ID]` or `[D161.7]`/`[D161.8]` where they land.

## §R3.1. What revision 3.1 changed (finding → section, disposition)

Every panel r4 finding was ACCEPTED by the manager (2026-10-16). No finding was
rejected. Sabotage ids marked PROPOSED start at S1009 and are the manager's to
allocate.

| finding | where | disposition |
|---|---|---|
| Q3 | §3.7.3, §12 Q3, header | **RULED: CONSULTED** (D167 add. 2). §3.7.5's OFFERED build text is withdrawn to a pointer (it is in revision 3's git text) |
| **B1** (blocker): the offer's derivation can refuse a compile that succeeds today | **§3.7.1, §3.2 (T-KIND), §3.3 rule 9, §3.7.4a, §3.7.7 G1-E1** | **Discharged.** The panel's witness REPRODUCES on main `2288ad1cb` (`window_contract_rev31/b1_witness.out`). The derivation splits into a NON-RAISING `find_derive_byte_rate_status` that the offer calls, and the ASK path that keeps today's `pcrec_ctx_fail`, so a refusal stays the asker's. T-KIND gains two `underivable` rows. A new rule 9 says an underivable kind refuses the compile iff it is CONSULTED, which keeps today's refusal set at E-1 and at B3b. G1-E1 is widened to deny arms × {no analysis, `--analysis weblog`, an `-I` user bundle, the `l1none` fixture}, with floors MEASURED by a census (`analysiscount.out`): 1,905 / 3,246 / 5,367 utf8 compiles succeed today with `""` under `l1none` and refuse when asked. The D80 route (making the spec's unconditional refusal true) is NOT taken |
| M1: `arrives` does not keep a MEASURED-ONLY kind absent | §3.2 | The column is renamed `unmeasured` (`ARRIVES` / `ABSENT`) after what it decides, and it is a conjunct of every non-measured PRESENT row. An `authored-absent` row precedes the fall-through. Witness: UNREACHED until B4 gives `run-rarity` a shape (then a user `-I` authored `bigram` bundle reaches it); sabotage S1011 PROPOSED. The header cites D162 add. 3's refinement, and check C-E1-5 holds the column to the kinds pcrec itself reads |
| M2: provenance re-derived from the chain LINK although each block declares it | §3.1, §3.2, §3.6, §3.7.1, **§12 Q5** | Design of record, PENDING Q5: `mf_prov.source` is read from the answering block's own `provenance` stanza (`source authored` → AUTHORED, anything else → MEASURED). `mf_prov` also carries `bytes` (the evidence strength, now built, not filed) and `fidelity`. `PcrecFindTblBlock`, `findgen`'s pre-parse and `rxt_find.c`'s copy carry the stanza. Link identity stays as C-E1-1's cross-check. This changes the manager's reading of D162 add. 3 ("pcrec's prior vs measured from a bundle") for a user's authored block, so it is Q5, in discussion form, with a leaning |
| M3: the CONSULTED design's render point was unplaced | **§3.7.3a (new)**, §3.7.9, §9 family 7 | ONE render point: the art-end pass, AFTER `mf_art_end`, for `_FINDINGS` and `.findings =` and, at M0, for `_MEASURES` and `.measures =`. The lines keep their byte positions through marks, so the move alone is zero-byte. It is its own commit, RP, landing no later than the first of B3b/M0 and before any OR. Check C-RP, sabotage S1014 PROPOSED. `measure_sets.md` needs the same sentence: an OWED sibling edit (§3.7.3a), not made here |
| M4: C-CONS is blind on its population | §3.7.7 | `consulted` is read from a named trace record (`KSRCTRACE`'s new `consulted` field), compared directly. The stamp half runs on the deny arms crossed with `-fmemfn-simd`, with a floor of kit-only consumers. C-PERT (X1) is the stamp half's independent partner |
| M5: the offer was built at a lazy, first-caller-wins point | §3.7.1, §3.3 rule 3 | Built EAGERLY at one stated point: `compile_driver`, right after `pcrec_find_resolve`, stored on `Job`. `pcrec_memfn_art` only passes it. Sabotage S1013 PROPOSED |
| m1: `find_kinds[]` should own the vocabulary | §3.2, §3.7.1, §3.7.6 F-3 | Renamed `find_queries[]` and made the query vocabulary's ONE home. `find_derivs[]`'s third column becomes a row index into it, and `rxt_find.c`, `findings_dump.c` and `rxt_source.c`'s error text read it. F-3 is RETIRED at E-1, not filed |
| m2: C-E1-4 shares a source with what it checks | §3.7.7, §3.7.8 | Labelled an AGREEMENT check; C-E1-1's python digest is named as the independent line. S996's plant site is stated |
| m3: G1-E1 omits the VM deny arm | §3.7.7 | Added (`--engine=vm -fno-req-byte -fno-req-run`, 5,337 `""`), with a floor of its own |
| m4: F-2 is not reachable through the listing it names | §3.7.6 F-2, §12 Q4 | Restated as LATENT. Trigger: the first path that lists facts under a non-default analysis |
| m5: rule 7 names kit rows and their outcome (D157) | §3.3 rule 7 | Cut to the fact. The row list and the KEEP default are a pointer to r17b′ |
| m6: `have ∧ ¬asked` is a new state | §3.7.6, §3.7.7 C-E1-6 | The record's comment is re-worded. `req_rate_why` reads `pcrec_find_byte_rate`'s return. A structural check (C-E1-6) holds that `byte_rate_have` and `byte_rate_status` have no reader outside `findings.c` |
| U1-U4 (the panel's unlocks) | §13 | U3 is BUILT here (the render point, RP). U4 is BUILT for the build point (M5); its retirement half stays filed. U1 and U2 are filed with their triggers (U2 is mostly built by M2) |
| **X1** (manager): nothing detects a kit row that reads a kind but reports `consulted = false` | **§3.7.7 C-PERT (new)**, §3.7.8 | An independent PERTURBATION check: compile the population twice, with each kind's data held and perturbed under the same bundle name and stop. Any artifact whose bytes outside the stamp lines move while its stamp omits that kind FAILS. It reads only emitted bytes and the stamp text. A prototype ran on main (`window_contract_rev31/perturb_proto.py`). Planted sabotage: a kit row that drops its consulted bit (S1015, B3b's) and a pcrec accessor that marks only on derivation (S1016, E-1's) |
| a finding from the prototype | **§3.7.6 F-5, §12 Q6** | **The stamp reports the FINAL attempt only.** A compile whose earlier attempt consulted the byte-rate and whose final attempt did not stamps `""`, yet its bytes move with the data. Two corpus witnesses (`(\p{Xwd})x`, `x(\p{Xwd})y` under `-e utf8 -fno-req-byte`). C-PERT finds them on day one. Q6 asks for the union over attempts |

## §R3. What revision 3 changed (input → section, disposition)

| input | where | disposition |
|---|---|---|
| E-1 (r17b′ §3.1 row "(main) E-1"; D167's consequences) | **§3.7 (new)** | The build step, stated in full: the object, where it is built, the slot it fills, the stamp, the census, the readers, the spec hunks, the checks and the sabotage |
| the per-site slot vs the kit's per-`mf_art_begin` slot | §3.1, §3.3 rule 3, §3.7.2 | **The object rides `mf_art_begin`**, not `mf_site.analysis`. One object per art, stated once. Rule 3's same-pointer check and its NULL-mixing refusal dissolve, because nothing can differ. Reasons in §3.7.2 |
| rev 2 open question 5 (S1's mover population) | §3.7.4, §14 item 5 | **MEASURED** (`window_contract_rev3/`). At default flags the population is EMPTY: 0 of 5,336 byte, 0 of 5,364 utf8 and 0 of 5,337 `--engine=vm` corpus artifacts stamp `""` today. Every default compile already asks, by the findings design's byte-rate rule 1 (docs/design/findings/design.md). The `""` population is entirely in the deny arms: 1,973 of 5,336 under `-fno-req-byte`, and every artifact under `--engine=vm -fno-req-byte -fno-req-run` |
| the sibling-of-a-family check against [KNOW-SRC] (`measure_sets.md` §9) | **§3.7.3**, §9 family 7, F-1 | **A conflict, found.** Rev 2's R1 makes `_FINDINGS` mean OFFERED. [KNOW-SRC] §9.2 part 5 has ONE stamp grammar for the family ("EMPTY = nothing asked"), and `<PREFIX>_MEASURES` means CONSULTED (§3.5: a pcrec reader asked, or the kit returned `consulted`). Two siblings would have two rules. This revision's design of record is **CONSULTED** for both. Under it, E-1 is ZERO-MOVER and not an abi event. The OFFERED alternative's event is also stated exactly (§3.7.5). Q3 asks Frank |
| general-mechanism lens on the object | §3.2 (T-KIND), §3.7.1 | Rev 2's T-KIND row "the kind is `byte-rate`" was a special case for one kind. It becomes an `arrives` COLUMN of ONE kinds table keyed by the [FINDINGS] query vocabulary: `ALWAYS` for `byte-rate` (D162 add. 2), `MEASURED-ONLY` for the rest. Provenance is decided by the answering LINK's identity, not by its name |
| C-1, C-2, C-16 (the PRESENCE class; member order, `omin`) | §2.2, §2.3 | ADOPTED as r17b′ §4.1 states it: `mf_span_class` gains PRESENCE; `omin` is measured from the match start, ≥ 0, and 0 is a sound under-estimate; `head_max`; `member_order`. Carved out of "bounded only" |
| C-3, C-4, C-12 (the reply) | §0 item 2, §2.4 | ADOPTED. ALL_PRESENT → VERDICT is deleted. Every span's presence is part of FIND: range binding, EMPTY = NOMATCH, decided first, one verdict per activation, per-candidate use as a PERMISSION, the unconstrained reply as a range. NONE's safety per consumer is r17b′ §4.6's table |
| C-5 (the K82/L1 and run-pre-check rows) | §2.5 | ADOPTED (Q-WR-5 (a)): origin = the landmark |
| C-6 (T-PRES superseded) | §5.4a, §9 | ADOPTED. `dominated` is the kit's row P2. Presence is not a separate site. Withholding presence (Q-WR-4) is pcrec's sub-problem choice and stays here as a one-row table, T-WITHHOLD |
| **C-7** (R-18's text and §11 in step) | **§11, Appendix A** | DONE here for §11. The ledger edit to `memfn/docs/requests.md` R-18 is drafted verbatim in Appendix A for main (single writer) |
| **C-8** (unlock (c) becomes the contract) | **§13** | DONE: unlock (c) is struck. Its trigger dissolves, because presence is a span class of the one request (D161 add. 14's clarification) |
| C-9, C-13, C-14 (applicability; the VM-route exclusion; `need` is the effort fact) | §2.3 | ADOPTED as rules |
| C-10 (give-up direction per consumer) | §2.4, §10 | ADOPTED: D161 add. 15's Q-WR-3. No move in either direction through ST3. From B5, D158 applies per measured cell, direction-checked by GIVEUP1 |
| C-11 (`consumer` replaced, not dropped) | §6 S3 | ADOPTED: S3 retires `mf_site.consumer` with `site_kind` as its replacement (Q-WR-8), and `site_kind` is stated from B2 |
| C-15 (evidence rows read MEASURED only) | §3.3 rule 7 | ADOPTED (D162 add. 3, D161 add. 15 Q-WR-9) |
| D161 add. 10 (verify and proofs only on EXACT spans) | §2.2, §4.3 | ADOPTED: a per-span `byte_form` fact, EXACT or SUPERSET, required. A proof or verify request is legal only on EXACT |
| a finding from the stamp's readers | §3.7.6 F-2 | `req.c`'s `req_rate_why` writes `rate:builtin-prior` whenever ANY block answered, `--analysis weblog` included. facts_listing.md 4.1.3¶4 says "the shipped byte-frequency prior". FILED, not fixed by E-1 |

## §R2.1. What revision 2.1 changed

D161 add. 9: pcrec chooses only the ORIGIN of the handed sub-problem; given it, pcrec sends ALL spans bounded to that origin with the analysis object, and the kit chooses which spans to search and how (§0.1, §2.1, §5.2, §5.4, §9, §11, §12 Q1).

## §R2. What revision 2 changed (finding → section, disposition)

| id | sev | where | disposition |
|---|---|---|---|
| E1 | BLOCKER | §2.3 (context terms), §2.4 (coverage, the edge), §2.5 | RESOLVED by D161 add. 7. A context check (`(?m)^`'s preceding `\n`) is not a span. pcrec tries the edge itself (today's shape, `emit_dfa.c:12376` at the review's commit) and opens the stream after it. "Miss = NOMATCH" is restated as "no match begins at any COVERED candidate"; the edge is outside the coverage |
| E2 | MAJOR | §0.6, §5.1, §5.2, §5.6, §8.1(iii), §13 | ACCEPTED. The producer's claim is narrowed to per-path-common (hull) spans. `start_set` and the k-set stay their own facts. `span_facts` is specified as a MEMBER of the position-pin fact family. The offset-pinned union span is a filed unlock with a trigger. C-SP1/C-SP2 get non-vacuity floors |
| E3 | MAJOR | §5.4 (T-CUT), §5.4a (T-PRES), §13 unlock (c) | ACCEPTED. Presence is its own table beside the cut, so `a.*zxq` sends segment 0 AND the `zxq` presence site |
| E4 | MAJOR | §4.3 (T-PROOF) | KEPT as pcrec-side consumption conditions of a proof (D161 add. 8): no proof-skip on seeded or context-viewed machines; the VM row skips no assertion and moves no meter |
| E5 | MAJOR | §2.3 (Range) | ACCEPTED. Candidates are span-0 STARTS, not occurrences. Reads below `lo` are bounded by `floor` under Q-R7-1's reads-below rule. Character alignment under `-e utf8` is pcrec's consumer obligation; the kit stays encoding-blind |
| E6 | minor | §2.3 (sequence rule), §5.2, §5.3 C-SP4 | ACCEPTED. The rule is a TIGHT HULL, not exact. Its soundness obligation is that `omin`/`omax` are PREFIX SUMS over the one flattened sequence. C-SP4 gains an under-estimate plant |
| E7 | minor | §2.4 | DISSOLVED by D161 add. 7. There is no `[L, U]` and no resume-at-`U + 1`; the stream is ascending and complete, so "where to resume" has one answer |
| E8 | minor | §5.3 C-SP3 | ACCEPTED. C-SP3 compares `req_set_maxoff` against the MIN of `omax` over that byte's spans |
| R1 | MAJOR | §6 S1, §8.2 | ACCEPTED. S1 is a pcrec abi event: building the object sets `byte_rate_asked` (`findings.c` `pcrec_find_stamp`), so `<PREFIX>_FINDINGS` and `rx_info.findings` move from `""` on every artifact with no prior asker. The stamp now means OFFERED, with one entry per kind. A mover census and a D80 hunk are owed |
| R2 | MAJOR | §4.3 (the R2 record) | **REJECTED by D161 add. 8.** Proven facts are KEPT, as a compile-time statement for the SITE that is identical in every layer. Frank's reasoning is quoted in §4.3 |
| R3 | MAJOR | §4 | ACCEPTED. §4 keeps only facts (pairwise distances under `spans_seq`, the stream's obligations, totality) and quotes D161 add. 5. The resume semantics, the G2 family and the 3+-link mechanics are removed as kit method. §11 no longer lists a kit output as a pcrec capability |
| R4 | MAJOR | §2.3, §3.1 | ACCEPTED. Explicit UNSTATED sentinels: `mf_prov.source`, `mf_need`, `mf_akind.present`, and a tri-state `spans_seq`. Payload invariant: non-NULL iff PRESENT and the source carries a table, checked at define |
| R5 | MAJOR | §6 S2-S4 | ACCEPTED. The shadow comparator is KEPT until S4: S3 retires the fields but keeps `pcrec_find_run_rank` as the shadow's oracle; S4 retires it with the picks |
| R6 | MAJOR | §6 S3 (file list) | ACCEPTED. The full grep-derived list, including the D27-blinded G2 generators (a BLINDED LANE edits them), `arm_fixtures.c`, `memfn_sites.c`, `run_rank.sh`/`rank_check.py` and the six `consumer` setters. `plan_hint` is read by kit arms and retires only at S4 |
| R7 | minor-major | §2.3 (Bounded only), §7 W1/W2 | ACCEPTED. "Permanently refused" is a KIT CODE CHANGE (`compose.c`'s back<0 check exempts `MF_MOVE_UNBOUNDED` on `lane/memfn-r17`) plus a refusal test. `span_hi` = `MF_SPAN_UNBOUNDED` stays legal, and §2.3 says why |
| R8 | minor | §2.2 (naming) | ACCEPTED. The rejected span-index proposal is called the SPAN-INDEX FIELD (setfind's "W8"), never "W8", which is also the built width-8 sub-block `pcrec_mfk_w8_*`. `mf_site.span_lo/hi` are called the PROVEN RANGE, never "span" |
| R9 | minor | §8.2 | ACCEPTED. New event rows: `need`/`preds` re-read on FIND (W7) is an `MF_SITE_ABI` event; the `mf_prov`/`mf_akind` layout; a per-site analysis slot; mixed NULL/non-NULL analysis in one art is refused |
| R10 | gaps | §3.6, §5.4, §9, §13 | ACCEPTED. The per-site ACTIVATION fact and the EVIDENCE-STRENGTH fact are filed with triggers. T-MEMO is relabelled a filed placement with a trigger, not a table. T-CUT and T-PRES gain a deny column (D46) |
| family | — | §5.6 | ACCEPTED, with one correction: the unification proposal is `match_split_pinonly.md` §4.3 / §9 U3. `compound.md`, which supersedes that note, does not re-file it (its own U3 is [EMIT-ENTRIES]), so this note carries it |
| unlocks | — | §13 | (a) end-origin spans, (b) offset-pinned union spans with per-group `spans_seq`, (c) presence as a chain link: all filed with the panel's triggers |
| kit verdicts | — | §7 | The panel's verdicts stand. The span-index rejection is re-grounded on the stream (one origin, one candidate type) instead of on `U` |

Revision 1's §12 Q3 (`U` now or later) is DELETED: D161 add. 7 removes `U`.

## 0. Answers first

1. **The SITE is a bounded sub-problem handed over at an origin pcrec chooses**
   (D161 add. 4, 9). pcrec's ONLY choice is the ORIGIN: segment 0's start, or
   an inner segment's start under the rev-inner gates, where pcrec recovers
   the head itself. Given the origin, pcrec sends EVERY span whose distance to
   it is bounded, never pre-selecting among them; the kit chooses which spans
   to search and how (D161 add. 9). The site is a list of those SPANS measured
   from the ORIGIN, **the start of span 0** `[D161.7]`. Each span has a class per position, an offset interval
   `[omin, omax]` from the origin, and a `need`. The offset interval is sent
   as `(move_back, overshoot)` = `(omax, omax - omin)`, the kit's existing
   W1/W2 fields; span 0 states `(0, 0)` by definition. One new site fact,
   `spans_seq` (the SEQUENCE RULE, §2.3), states that two spans' starts differ
   only by the items between them. That makes every pairwise distance a tight
   hull, so "bounded gaps" and "minimum offset" need no fields of their own
   (§2.2's mapping table). Every value is true, required and bounded; an
   unbounded offset is refused by contract, not reserved (D161 add. 5).
2. **The reply is a STREAM of exact candidates** `[D161.7]`: each candidate
   is a position where span 0 starts. It has three obligations: COMPLETE
   (every covered position where all spans hold appears), ASCENDING with no
   repeats, and each candidate IS span 0's start. pcrec matches from each
   candidate. A context check is not a span: pcrec tries the edge itself and
   the stream covers the positions after it `[r4 E1]`. `[rev3 C-3, C-4]` There
   is no separate presence reply: a PRESENCE span (unbounded offset) is a span
   class of the same site, and an EMPTY stream is NOMATCH (D161 add. 14). Because every candidate has one meaning, the reply needs no
   span index (§7).
3. **The ANALYSIS object** (D162) is a versioned list of kinds keyed by the
   [FINDINGS] query name (`byte-rate`, later `run-rarity`). Each kind is
   PRESENT or explicitly ABSENT and carries a PROVENANCE: `authored`,
   `prior-none` or `measured`, plus the bundle identity, the same digest
   the `<PREFIX>_FINDINGS` stamp reports and, for `measured`, the evidence
   strength (`bytes`, `fidelity`). `[rev3.1 M2]` The source is read from the
   answering block's own declared `provenance` stanza, pending Q5. Every enum
   has an UNSTATED zero `[r4 R4]`. `byte-rate` is always present. Under
   `-e utf8` today it is `prior-none` with no table (§3.2). The kit is encoding-blind (D147 add. 14),
   so `cpfreq` is never sent. `[rev3]` The object reaches the kit ONCE per
   art, on `mf_art_begin` (the slot the kit's B1 declares), not per site
   (§3.7.2).
4. **The kit's job is a CHAIN of 1-2 simple searches inside one site** (D161
   add. 5, quoted in §4.1). The contract states the facts a chain reads and
   the obligations its stream meets; the chain itself is the kit's `[r4 R3]`.
5. **[KIT-VERIFY]** (§4.3). Direction (1), "verify span k", is `need =
   REQUIRED` on span k. Direction (2), PROVEN FACTS, is KEPT `[D161.8]`: a
   static `mf_result.proven`, per span, the positions every candidate of the
   site has proven. It is a function of the SITE REQUEST, identical in every
   layer (SIMD off or on, any `--memfn=` deny), and pcrec emits code for it:
   with "fo" of `foobar` proven, pcrec asks a span test for the rest or starts
   its engine past the proof; with "foobar" proven and nothing else to check,
   pcrec reports the match.
6. **ONE pcrec-side producer of HULL spans**: a new core fact `span_facts`
   (E2, proposed owner `src/facts/spans.c`), a MEMBER of the position-pin fact
   family (`start_set`, the k-set, `run_pin`, `end_pin`, compound's split
   facts, landmark K; §5.6) `[r4 E2]`. It is one AST walk that generalizes
   `rb_walk`'s offset bookkeeping to `(classes, omin, omax)` per span and adds
   the MINIMUM offset nothing carries today. It produces only spans common to
   every path. `start_set` and the k-set (unions over paths at a fixed offset)
   stay their own facts; carrying them in a sequenced multi-span site is a
   filed unlock (§13 (b)). The DECISIONS that read the prior to choose among
   spans move into the kit: the req pick, the run window start, set-leads,
   the offset-k selection, the landmark K admission, G1 and `plan_hint`.
   Unbounded cuts stay pcrec's.
7. **Retirement sequence** (D161 add. 6, D162 add. 3): the frequency kind
   lands first (S1 = main's E-1, §3.7; ZERO-MOVER, D167 add. 2), then the kit's own ranking,
   implement-then-replace (S2), then the retirement of `mf_pred.rank_*`, the
   never-filled `ppm_*`/`cand_ppm_*` and the unread `mf_site.consumer` in one
   `MF_SITE_ABI` bump with zero pcrec movers (S3). `pcrec_find_run_rank`
   survives S3 as the shadow's oracle and retires at S4 with the picks
   `[r4 R5]`. Consumer price was never built; it retires as text.
8. **Ratified** (§7): the storage capability, the window fields W0-W3 (with
   the unbounded sentinels PERMANENTLY refused, a kit code change `[r4 R7]`),
   N5 in its per-width rev-2.3 form, and N6. **Rejected**: the span-index
   field (setfind's W8) and W9 (consumer price). **Moved**: W10 (joint
   survival) becomes the analysis kind `run-rarity`.
9. **E-1, main's build step** `[rev3]` (§3.7). pcrec builds the analysis object
   per compile attempt from `Job.find` through ONE table over the [FINDINGS]
   query vocabulary (`find_queries[]`). `byte-rate` is ALWAYS present:
   measured, authored or prior-none. pcrec builds it EAGERLY, right after the
   attempt's chain resolves, and hands it to the slot the kit's B1 declares on
   `mf_art_begin`, with no kit edit, after B2 merges.
   - **The stamp.** `<PREFIX>_FINDINGS` means CONSULTED, the [KNOW-SRC]
     family's one rule (RULED, D167 add. 2). Building the object is an OFFER,
     and an offer is not an ask.
   - **The offer never refuses** `[rev3.1 B1]`. It derives through a
     NON-RAISING status derivation; the refusal of an underivable block stays
     on the ASK path, so it fires only where a reader consults the kind, as
     today. With both, E-1 moves no byte and no refusal in any arm: it is not
     a pcrec abi event and not a D80 event.
   - **What the stamp gains later.** The kit's per-kind `consulted` joins the
     stamp at the first commit that ROUTES a kit row reading a kind (B3b).
     Before that, a zero-mover commit (RP) moves the stamp's render point to
     after `mf_art_end` (§3.7.3a). B3b carries the findings.md §5 hunk.
   - **The honesty check** `[rev3.1 X1]`. A perturbation check (C-PERT)
     compiles every artifact with each kind's data held and perturbed, and
     fails any artifact whose bytes move while its stamp omits the kind. It
     does not read pcrec's ask record or the kit's report. Its prototype
     found that the stamp reports only the FINAL attempt (F-5, Q6).

## 1. Inputs, and what is already built

**Binding rulings** (read in full; not re-opened):
- D146 (delegation) and D147 (layers);
- D155 add. 3/4/4.1 (composable body pieces; per-width primitives; a STATEFUL
  FIND's body contract is `next_candidate(&state, lo)`);
- D157 (facts, never method);
- D161 + add. 1-8 (add. 7: the stream; add. 8: proven facts kept);
- D162 + add. 1-4.
- `[rev3]` D161 add. 10 (EXACT byte form gates verify and proof), add. 11-13
  (the candidate finder table; measured generic class; lockdown), add. 14 and
  its clarification (single-byte sites and presence are ONE window request),
  add. 15 (Q-WR-1/2/3/6/9); D166 + add. 1-2 (measurement sets); D167 (build GO;
  E-1 sits between the kit's B2 and B3a);
- `[rev3]` the kit's merged list `winreq_report.md` §4 (C-1..C-16) and R17-b′
  rev 2 §3-§4, both on `lane/memfn-r17` at `c90d65e53`. Requests R-18..R-21 on
  main (`memfn/docs/requests.md`).

Memory rules that also bind: no silent defaults (a value a row USES must be
stated; unused fields are wildcards); K96 row contracts (applicability covers
every parameter a row does not honour; allowlists of honoured fields);
decisions as first-match tables.

**The site vocabulary on the kit branch** (`memfn/include/memfn.h`):

| item | state | where |
|---|---|---|
| one span = an `mf_pred` of terms at fixed offsets | BUILT | `MF_SITE_ABI` ≤ 10, main |
| READS-BELOW FIND: a term wholly below its candidate bounds the range by its reads (Q-R7-1); `floor` bounds every read (Q-G2-6) | BUILT | main |
| `mf_pred.window_stated`/`move_back`/`overshoot` (W0-W2), FIND's result is the window's beginning (W3) | BUILT | `MF_SITE_ABI` 11, `lane/memfn-r17` |
| `mf_site.decl_point`, `mf_locals`, `mf_defined`, `fn_ref` as the STMT stem (W4/W5) | BUILT | same |
| `mf_result.keeps_storage`, N6 in `valid_prefix`, the width-8 sub-block `pcrec_mfk_w8_*` | BUILT | `MF_SITE_ABI` 12, `lane/r17b` |
| `mf_pred.rank_n/rank_pos/rank_ppm` (RQ-2, D157) | BUILT, read by `vrun` KB | main |
| `mf_term.ppm_*`, `mf_site.cand_ppm_*` | stated "unknown" everywhere, read by nobody | main |
| `mf_site.consumer` | stated `MF_C_ENGINE` everywhere, only range-checked (`compose.c`) | main |
| `mf_pred.plan_hint`/`plan_pos` | pcrec's model's scan pick; READ by kit arms (`vrun.c`, `precheck.c`, `ofsskip.c`, `compose.c`'s rank check) | main |

## 2. Object A: the SITE description

### 2.1 What a site is

A site is one search pcrec delegates. Its description states a SUB-PROBLEM: a
regular language pcrec has cut out of the pattern at an origin it chose. The
kit must locate where the sub-problem's span 0 can begin. The sub-problem need
not be the whole pattern. For `a.*aaa.{2,5}zxq`, pcrec may take the origin at
`aaa` and recover `a.*` itself with a reverse walk (D161 add. 4). Given the
origin, pcrec sends all spans bounded to it (`aaa` and `zxq` here) and the
kit picks among them (D161 add. 9); pcrec does not pick `zxq` for it. Every fact in the description
is TRUE of every match of the sub-problem, and the kit must honour every one
(K96: a row that does not honour a stated parameter does not apply).

**The ORIGIN** is the start of span 0 `[D161.7]`. Every offset in the site is
measured from it. A bounded HEAD of the sub-problem before span 0 (`[a-z]{0,8}`
in `[a-z]{0,8}ing`) is not sent; its width `[h_min, h_max]` is pcrec's private
fact, and pcrec maps each candidate `c` to its own start (an anchored attempt
at `c` when `h = 0`, else a scan from `max(search_from, c - h_max)`). That one
shared origin keeps the reply span-free (§2.4).

### 2.2 The span list

A site carries `1 + npred` predicates: `pred` (span 0) and `preds[0..npred)`
(spans 1..npred, the kit's planned W7 reading, generalized). Each is one
`mf_pred`:

| field | meaning | today's field | new? |
|---|---|---|---|
| terms (SET / RUN) | the class of each position, at fixed offsets inside the span. Positions no term covers are "any byte" | `term[]`, `nterm` | no |
| `move_back` | `omax`: the span's largest start offset from the origin. Signed; span 0 states 0; a CONTEXT predicate states a negative value (below) | W1 | no (R17-a) |
| `overshoot` | `omax - omin` | W2 | no (R17-a) |
| `window_stated` | 1 = the two above are STATED; 0 (the zero fill) = unstated, refused on a window site | W0 | no (R17-a) |
| `need` | UNSTATED (the zero fill, refused at define), REQUIRED (every candidate satisfies this span), OPTIONAL (the kit may use or ignore it) `[r4 R4]` | `mf_pred.need` | values re-numbered (§2.3) |
| `spans_seq` (site-level) | UNSTATED (zero fill), SEQ (the sequence rule holds, §2.3), NOT-SEQ (it does not; no row may read a pairwise distance) `[r4 R4]` | — | **yes** (R-18) |

**PRESENCE spans** `[rev3 C-1, C-2, C-16]`. A span with no bounded distance to
the origin, but necessary for every match, is a PRESENCE span. Examples are an
unbounded-offset necessary byte or run (`zxq` in `a.*zxq`), or each member of a
necessary set. It rides in the SAME site, as `mf_span_class = MF_SPAN_PRESENCE`.
r17b′ §4.1 is the field text, adopted here:
- It states `window_stated 0`, `omin ≥ 0` and a `need`. `move_back` and
  `overshoot` are not read.
- `omin` is measured from the MATCH START, not from span 0. Presence is a fact
  of the match, and binding is per activation (§2.4), so the verdict window is
  `[start + omin, n)`. At `omin = 0` that is today's `[posvar, n)`. `0` is the
  sound under-estimate B3a states; the true `omin` is B5's.
- The UNPICKED form (PR-5): every necessary-set member is its own one-byte
  presence span, carrying `member_order`, its position in pattern order (PR-7).
  The whole run is one span with its mask. The pick, the window and set-leads
  are the kit's rows.
- The site gains `head_max` (`h_max`, PR-6): the largest distance from a match
  start to span 0's start. It is 0 for a head-0 origin and K for the handoff's
  landmark origin.

**The span class enum** `[rev3]` is `{UNSTATED = 0, BOUNDED, CONTEXT, PRESENCE}`.
It replaces the reading "a negative `move_back` is a context predicate" with a
stated fact. C-1's split of "below the origin" falls out of it: a bounded span
with a negative offset is BOUNDED, and a byte only read for context is CONTEXT.

**The byte form** `[rev3, D161 add. 10]`. Every span states `byte_form`:
`{UNSTATED = 0, EXACT, SUPERSET}`. EXACT means the per-position byte sets accept
exactly the span's language (literal bytes, single-byte classes, a multi-byte
class whose cross product is the class). SUPERSET means a filter only (`[α-ω]`
under `-e utf8` arrives as `{CE,CF}{80..BF}`). pcrec knows which, because it
did the lowering. Only an EXACT span may be marked for verify (§4.3 direction
(1)) or receive a proof (direction (2)). A SUPERSET span's candidates remain
COMPLETE, and pcrec re-checks them.

**Context predicates** `[r4 E1]`. A predicate whose every term lies below the
origin (Q-R7-1's reads-below FIND) is a CONTEXT check, not a span (D161 add. 7).
`(?m)^`'s preceding `\n` is the one built today: R-17 spells it as the `{\n}`
predicate with `move_back -1`, read here as "the context term lies one byte
before the origin". The candidate is unchanged (the hit + 1), so no field and
no byte moves. A context predicate is true at every candidate the stream
covers, but it is NOT a fact of every sub-problem match: `(?m)^abc` matches at
the edge with no `\n` before it. That is why the edge is pcrec's (§2.4).

D161 and the brief name five span parameters. None gets a field of its own:

| D161 / brief item | carried as |
|---|---|
| classes per position | the span's terms |
| move-back | `move_back` (= `omax`) |
| overshoot | `overshoot` |
| MINIMUM offset | `omin = move_back - overshoot` (signed). pcrec must newly COMPUTE it (wingame §1.2), but it travels inside `overshoot`. A separate field would be a second spelling of one fact (D122) |
| bounded gaps | under `spans_seq` = SEQ, the distance between spans `i < j` lies in `[omin_j - omin_i, omax_j - omax_i]` (§2.3) |

**Naming** `[r4 R8]`. In this note a SPAN is a sub-problem span (an
`mf_pred`). `mf_site.span_lo`/`span_hi` are the PROVEN RANGE (the bytes known
to exist), never "span". The rejected reply-names-its-span proposal is the
SPAN-INDEX FIELD (setfind's W8), never "W8": `W8` is also the built width-8
sub-block `pcrec_mfk_w8_*`.

### 2.3 The rules

- **True and required.** Every span is NECESSARY: every match of the
  sub-problem carries, at some start offset `d ∈ [omin, omax]` from its span-0
  start, a byte of each position's class at `origin + d + j`. Each REQUIRED
  span binds the reply.
- **Bounded only.** `move_back` and `overshoot` are finite. The reserved
  `MF_MOVE_UNBOUNDED`/`MF_OVER_UNBOUNDED` (R17-a) become PERMANENTLY refused
  (D161 add. 5). **This is a kit code change** `[r4 R7]`: `lane/memfn-r17`'s
  window check in `compose.c` currently exempts `MF_MOVE_UNBOUNDED` from its
  back<0 test. It becomes a named refusal at define, with a G2 refusal case
  for each sentinel. `mf_site.span_hi = MF_SPAN_UNBOUNDED` stays LEGAL: it
  states that nothing is proven about the subject's length (an absent bound on
  the PROVEN RANGE), which is a fact about the call, while an unbounded
  `move_back` would be an offset inside the sub-problem, which D161 add. 5
  rules is automata and pcrec's.
  `[rev3 C-2]` The rule binds BOUNDED and CONTEXT spans. A PRESENCE span is
  carved out as its own class: it has no `omax` and states `window_stated 0`.
  The unbounded sentinels stay refused on every class, and a PRESENCE span
  carries no pairwise distance, so `spans_seq` never covers it.
- **`need` is the EFFORT fact** `[rev3 C-14]`. A span is REQUIRED exactly where
  dropping it, narrowing it, or answering unconstrained over it could let a
  budgeted engine do more work on an input the denied build answers (D158).
  It is OPTIONAL elsewhere. No separate effort field exists.
- **Applicability** `[rev3 C-9]` (K96). A kit row that would drop, narrow or
  answer unconstrained over a REQUIRED span does not apply to the site.
- **The VM-route exclusion** `[rev3 C-13]`. On a route with no DFA scan in front
  of a budgeted engine (the VM hat, the no-DFA VM route's pre-check, the framed
  one-attempt VM of K64), pcrec states every presence span REQUIRED (K64, K65,
  K66) and states the VM hat's span 0 REQUIRED. r17b′ §4.6's table is the
  per-consumer statement.
- **No silent defaults** `[r4 R4]`. Every stated enum has an UNSTATED zero:
  - `window_stated`: 0 = unstated, refused on a window site (R17-a's rule).
  - `mf_need`: re-numbered `{MF_NEED_UNSTATED = 0, MF_REQUIRED,
    MF_OPTIONAL}`. Today `MF_REQUIRED` is 0, so a builder that forgets `need`
    gets REQUIRED silently, and REQUIRED now binds the reply. Refused at
    define. An `MF_SITE_ABI` event (values and meaning) with zero movers when
    every builder states it.
  - `spans_seq`: tri-state `{UNSTATED = 0, SEQ, NOT_SEQ}`. UNSTATED on a
    multi-span window site is refused; a single-span site may leave it
    UNSTATED (no pairwise distance exists). NOT_SEQ is how a future BRANCH
    producer says "not sequential" (§8.1 ii), which a 0/1 bit could not say.
  That is the K96 shape: a field is a wildcard for every row that does not use
  it, and stated for every row that does.
- **THE SEQUENCE RULE** (`spans_seq` = SEQ). The spans are listed in order of
  position, and they are a subsequence of ONE flattened sequence of positions
  and bounded gaps that every match of the sub-problem follows, starting at
  span 0. So for `i < j`:

      start_j - start_i  ∈  [omin_j - omin_i,  omax_j - omax_i]

  This is a TIGHT HULL, not an exact set `[r4 E6]`: every real distance lies
  inside it, and its ends are reached, but not every value between them need
  be. **Its soundness obligation**: `omin_k` and `omax_k` are PREFIX SUMS of
  the minimum and maximum widths of the items before span k along that one
  sequence. An `omin` under-estimate on one span (and not on the other) can
  push a real distance outside the interval: `pcrec_minw` under-estimates on
  some shapes, and `req.c`'s `rn_tail_off` takes a SUBTREE `maxw`, so neither
  may be used per span; the producer computes both sums along the sequence
  (§5.2) and C-SP4 checks them with an under-estimate plant (§5.3). Without
  the rule only the LOOSE interval `[omin_j - omax_i, omax_j - omin_i]` is
  sound. wingame §8.1 measured the difference on `.{0,6}\d.{0,3}#`: a region
  of 3 starts (tight) against 15 (loose).
- **Range** `[r4 E5]`. Three definitions:
  - **Starts, not occurrences.** A candidate is a span-0 START. Under
    `move_back > 0` on a later span the kit may locate that span's occurrence
    first, but what it yields is the span-0 start(s) the occurrence implies.
  - **The range** is the shipped one: `[lo, n - end_back)`, with `empty`
    declared, no wrap, and `lo > n` empty. A site with a context predicate
    takes Q-R7-1's reads-below range (a candidate is in range iff `lo ≤ c`
    and every read lies below `n - end_back`).
  - **Reads.** Every read the kit makes lies in `[floor, n)`. A context
    predicate reads below `lo`; `floor ≤ lo` is the caller's precondition
    (Q-G2-6). pcrec states `floor` on every site that carries one.
  - **Alignment under `-e utf8`.** Candidates are byte positions. The kit is
    encoding-blind (D147 add. 14) and never rounds. When span 0's first class
    can contain a non-start byte, pcrec's consumer rounds the candidate up to
    a character start, or rejects it (`litscan_k82h.md` Claim 3 is that
    consumer obligation, kept pcrec-side). A span 0 derived from a lowered
    character class contains no continuation byte at position 0, and the
    build asserts that where it relies on it.

### 2.4 The reply

`[rev3 C-3, C-4]` A site's reply has ONE type: the STREAM. Revision 2's
`ALL_PRESENT → VERDICT` row is deleted (D161 add. 14's clarification: the
pre-scan and the candidate search are one request).

| op | reply | meaning |
|---|---|---|
| FIND (every window site, presence spans included) | STREAM of candidates `[D161.7]`. Stateless: each FIND call returns the next candidate `≥ lo` (W3's `result`). Stateful: `next_candidate(&state, lo)` (D155 add. 4.1, R-17's forms). Both deliver the same sequence | see the obligations below |

ALL_PRESENT's renderers (`precheck`, `precheck_assign`, `precheck_assign_byte`)
survive as the merged site's ENTRY-USE rendering (KW-7, B3b), not as a separate
reply type. A presence-only site (no span 0, `pred.nterm = 0`) replies with the
range form of obligation 6 below.

**The stream's obligations** (D161 add. 7):

1. **COMPLETE.** Every COVERED position in range where all spans (and all
   context predicates) hold appears.
2. **ASCENDING, no repeats.** A back-search from a later span can imply
   several, or overlapping, span-0 positions; each is yielded once, in order.
   A `lo` passed to the next call raises the floor of the sequence and never
   lowers it.
3. **Each candidate is span 0's start**, the origin.
4. **REQUIRED spans bind** (this note's existing rule): every candidate
   satisfies every REQUIRED span at an offset inside its interval. A
   candidate may fail an OPTIONAL span (a superset is legal). So a stream
   that yields every position in range is legal iff no span is REQUIRED.
5. **Range-level binding of PRESENCE spans** `[rev3 C-3 (i), (ii)]`. If a
   REQUIRED presence span has no occurrence in `[start + omin, n)`, the stream
   is EMPTY, and EMPTY = NOMATCH (with §2.4's edge rule below where a context
   predicate exists). EMPTY or the first element is returned only after every
   REQUIRED presence span is established over its whole window: DECIDED
   FIRST. One verdict per activation. Later uses in the same activation (the
   loop's next candidate, the handoff's re-entry) yield candidates and never
   re-verify. Where a pre-check today turns an engine give-up into NOMATCH
   (K65), the empty complete stream does the same.
6. **The unconstrained reply is a RANGE** `[rev3 C-3 (iv)]`. "Every position in
   `[lo, hi′]`" with `hi′ = n` is legal iff span 0 is OPTIONAL or absent. A
   presence-only site replies this way: today's VM entry runs every position
   after the pre-check. No output hook is added. A `result_hi` hook is filed for
   the iterator's cut (Q-WR-6).
7. **Per-candidate use is a PERMISSION** `[rev3 C-3 (iii), D161 add. 15
   Q-WR-6]`. The kit MAY end the stream after the last occurrence `p` of a
   REQUIRED presence span, at `c > p − omin + head_max`. This is never
   required. It is exercised only by the D165 iterator, after its build, with
   `S` raised once.

**NONE's safety per consumer, and the give-up direction** `[rev3 C-10, C-12]`.
r17b′ §4.6 is the per-consumer table, adopted as the contract's worked
statement. It follows from obligation 4 once `need` is stated (§2.3). An
unconstrained reply is answer- and give-up-safe on DFA_SCAN, DFA_HAT, HYB_PF and
ATTEMPT_PRED. It is NOT legal on VM_ATTEMPT, whose span 0 and presence spans are
REQUIRED. The give-up direction is D161 add. 15's Q-WR-3: through the
zero-mover steps (B0-B3b) nothing moves in either direction. From B5, D158
applies per measured cell (an answer never becomes a give-up; a give-up may
become an answer, direction-checked by GIVEUP1).

**Coverage and the edge** `[r4 E1]`. A position is COVERED unless deciding a
context predicate there would need a byte the site does not offer as context,
which is the EDGE: `search_from` (equal to `lo` at the first call), and `0`.
pcrec tries the edge itself, as it does today (the FIND is skipped at the
edge, `emit_dfa.c:12376` at the review's commit; `\G` makes `search_from` the
edge), and opens the stream at edge + 1. So a stream that ends means: no
sub-problem match begins at any COVERED position in range. Together with
pcrec's edge attempt that is NOMATCH for the range. With no context predicate
there is no edge, and an exhausted stream is NOMATCH outright.

- **Why no span index.** Every candidate is span 0's start, so it means the
  same thing whichever span the kit located first.
- **No resume rule** `[r4 E7]`. Revision 1's `U` and resume-at-`U + 1` are
  gone: the next candidate after one pcrec rejected is the stream's next
  element. The 2-chain ambiguity in `U` dissolves with it.
- **Every span's presence is part of FIND** `[rev3 C-3]` (revision 2 said
  "a bounded span's"; PRESENCE spans now join, by obligation 5). An exhausted
  stream has proved that no covered position carries all spans. So the pre-check the
  K82/L1 handoff fuses today (presence plus location in one pass) is a FIND
  whose span 0 is the landmark. **Correction to revision 1**: pcrec's `c - K`
  text does NOT retire. `K` is the bounded head before span 0 (`h_max`, §2.1),
  and recovering the head is pcrec's. What moves at R-18 is the fused gate,
  which becomes this FIND.

### 2.5 The degenerate cases, in these fields

| site today | spans / context | `move_back` / `overshoot` | reply |
|---|---|---|---|
| PF FIND, DFA hat, VM hat (R-17) | one span, one position, class `S` (an offset-pinned union, §5.6) | 0 / 0 | stream; candidate = the hit |
| MLINE `(?m)^` | no span; one context predicate `{\n}` one byte before the origin | -1 / 0 (R-17's spelling) | stream from edge + 1; candidate = the hit + 1; the edge is pcrec's |
| offset-skip FUNC | one span: the k-set positions 0..k (an offset-pinned union, from the k-set, not from `span_facts`) | 0 / 0 | stream; candidate = the hit |
| run pre-check (unbounded offset) `[rev3 C-5]` | the run as a PRESENCE span (and each necessary-set member as its own, unpicked), beside span 0 where one exists | none (`window_stated` 0); `omin` 0 at B3a | the same stream: EMPTY = NOMATCH (obligation 5); on a presence-only site, the range `[lo, n)` (obligation 6) |
| K82/L1 handoff `[rev3 C-5, Q-WR-5 (a)]` | origin = the landmark: span 0 is the landmark (one byte, or a RUN term); presence is fused (an exhausted stream is the landmark's absence); `head_max` = K | 0 / 0 | a stream; pcrec keeps `max(lo, c − K)`, the utf8 round-up and the re-entry (a further USE of the same site at `scan_position`). Framing (b), origin = the match start, is a later byte move behind its own deny |

## 3. Object B: the ANALYSIS object

### 3.1 Shape (spellings PROPOSED; the layout is the kit's to finalize)

```c
#define MF_ANALYSIS_LIST_V 1        /* the LIST's own shape, not any kind's */
typedef enum { MF_PROV_UNSTATED = 0,      /* refused at define              */
               MF_PROV_AUTHORED, MF_PROV_PRIOR_NONE,
               MF_PROV_MEASURED } mf_prov_source;
typedef enum { MF_FID_UNSTATED = 0,       /* the block declares no fidelity */
               MF_FID_VERBATIM, MF_FID_ADAPTED,
               MF_FID_SYNTHESIZED } mf_prov_fidelity;
typedef enum { MF_KIND_UNSTATED = 0,      /* refused at define              */
               MF_KIND_PRESENT, MF_KIND_ABSENT } mf_kind_state;
typedef struct {
    uint8_t     source;     /* mf_prov_source, read from the answering block's
                               own `provenance` stanza [rev3.1 M2, pending Q5]  */
    uint8_t     fidelity;   /* mf_prov_fidelity: the stanza's `fidelity` row;
                               UNSTATED where the block declares none (the
                               schema requires it only under a pattern block)
                               [rev3.1 M2]                                      */
    const char *bundle;     /* the answering bundle's name (AUTHORED and
                               MEASURED); NULL under PRIOR_NONE (stated,
                               checked at build) [rev3]                         */
    uint64_t    bytes;      /* MEASURED: the stanza's `bytes` row, the
                               exemplar's size (the evidence strength, §3.6);
                               0 under AUTHORED and PRIOR_NONE, where the
                               schema forbids or does not ask for it
                               [rev3.1 M2]                                      */
    uint64_t    digest;     /* the kind's digest of what it carries, the value
                               the kind's `<PREFIX>_FINDINGS` item reports when
                               a reader consults it (byte-rate:
                               pcrec_find_byte_rate_digest); 0 under PRIOR_NONE */
} mf_prov;
typedef struct {
    const char *tag;        /* the [FINDINGS] query name: "byte-rate", ...     */
    uint32_t    version;    /* this kind's payload shape                        */
    uint8_t     present;    /* mf_kind_state                                    */
    mf_prov     prov;
    const void *payload;    /* per tag; see the invariant below                 */
} mf_akind;
typedef struct mf_analysis {
    uint32_t        list_v;     /* MF_ANALYSIS_LIST_V                          */
    uint16_t        nkinds;
    const mf_akind *kinds;      /* every kind THIS pcrec knows, by tag         */
} mf_analysis;
```

`[rev3.1 M2]` `bytes` and `fidelity` are in the layout from its first
declaration. The layout is new at the kit's B1, so adding them now costs no
extra `MF_SITE_ABI` event; adding them after B1 lands would. If B1 has already
merged a layout without them when this revision is read, the kit's B1 owes the
two fields in a re-declaration before E-1, which is still one event.

**The payload invariant** `[r4 R4]`, checked at define: `payload` is non-NULL
iff `present == MF_KIND_PRESENT` and `prov.source` is `AUTHORED` or
`MEASURED`. So `byte-rate` under `-e utf8` today reads `PRESENT`,
`PRIOR_NONE`, `payload == NULL`, and that combination is stated, not
accidental. An `ABSENT` kind has `source == MF_PROV_UNSTATED` and no payload.

`[rev3]` **The object reaches the kit on `mf_art_begin`**, in the slot the kit's
B1 declares (NULL-tolerant; no kit row reads it before B3a). Revision 2's
`mf_site.analysis` is WITHDRAWN (§3.7.2 gives the reasons). NULL is "none
stated", legal for a stand-alone K3 caller and for every pcrec compile before
E-1 lands.

### 3.2 The kinds table, and provenance `[rev3: one table; rev3.1: the vocabulary's home, an `unmeasured` column, content provenance]`

The object is built from ONE pcrec-side table, `find_queries[]`
`[rev3.1 m1]`, whose rows ARE the [FINDINGS] query vocabulary. It is the
vocabulary's one home: `find_derivs[]`'s third column becomes a row index into
it, and every other spelling reads it (§3.7.1, F-3). Each row has a tag, a
payload version (`0` = pcrec carries no payload for the kind yet), and an
`unmeasured` column. No row names a kind in a predicate.

`[rev3.1 M1]` **`unmeasured`** says what the kind is when nothing MEASURED
answers it: `ARRIVES` (it is present anyway, as an authored table or as
pcrec's no-information answer) or `ABSENT`. The column is D162 add. 2 stated
as data: the frequency kind always arrives, and every other kind is present
only when measured. Its values are not free choices: D162 add. 3's refinement
("a derived fact pcrec also uses is sent ALWAYS") puts `ARRIVES` on exactly the
kinds a pcrec reader asks, and check C-E1-5 holds the column to that.

| tag | payload version | `unmeasured` | payload |
|---|---|---|---|
| `byte-rate` | 1 | `ARRIVES` (D162 add. 2; pcrec's readers ask it) | `uint32_t ppm[256]`, summing to 1,000,000 (`pcrec_find_normalize`'s rule); NULL under `prior-none` |
| `run-rarity` | 0 until [FINDINGS] B4 lands its shape | `ABSENT` (D162 add. 2; no pcrec reader asks it) | none yet; B4's shape |

**T-KIND, one kind's state (first match, the same rows for every kind):**

"A block answers" is `pcrec_find_chain_answer`'s selection: the ONE block the
chain's first answering link declares for (query, encoding). "Derives" is the
NON-RAISING status derivation of §3.7.1 returning OK.

| row | predicate | `present` | `prov` (source, bundle, digest, bytes, fidelity) |
|---|---|---|---|
| `no-shape` | the row's payload version is 0 | ABSENT | UNSTATED |
| `underivable-arrives` `[rev3.1 B1]` | a block answers, its derivation FAILS, and `unmeasured` is `ARRIVES` | PRESENT | PRIOR_NONE (NULL, 0, 0, UNSTATED) |
| `underivable` `[rev3.1 B1]` | a block answers and its derivation FAILS | ABSENT | UNSTATED |
| `measured` | a block answers, derives, and its `provenance` declares a `source` other than `authored` | PRESENT | MEASURED (the answering bundle, the kind's digest, the stanza's `bytes`, its `fidelity`) |
| `authored` `[rev3.1 M1, M2]` | a block answers, derives, declares `source authored`, and `unmeasured` is `ARRIVES` | PRESENT | AUTHORED (the answering bundle, the kind's digest, 0, the stanza's `fidelity`) |
| `authored-absent` `[rev3.1 M1]` | a block answers and declares `source authored` | ABSENT | UNSTATED |
| `prior-none` | nothing answers, and `unmeasured` is `ARRIVES` | PRESENT | PRIOR_NONE (NULL, 0, 0, UNSTATED) |
| `absent` | else | ABSENT | UNSTATED |

- **Why `underivable` reads PRIOR_NONE for an arriving kind** `[rev3.1 B1]`.
  The block that answers has no table to carry, so no payload exists, and
  falling through to a later link would break the selection rule (the FIRST
  answering block is the answer, findings design §4.4). D162 add. 2 still asks
  the kind to arrive, and pcrec's answer with no table IS the no-information
  answer, so the state is the one `prior-none` already states. It is never
  observable on an artifact: rule 9 (§3.3) refuses the compile the moment any
  reader, pcrec's or the kit's, consults the kind. The state matters only for
  compiles in which nothing reads it.
- **Provenance from the block's own declaration** `[rev3.1 M2, pending Q5]`.
  Every data block carries a schema-validated `provenance` stanza
  (`rxt_schema.def`: `bytes` and `sha256` are required under a data block iff
  `source` is not `authored`; `fidelity` is a closed vocabulary,
  `verbatim adapted synthesized`). The source is read from it: `source
  authored` → AUTHORED, any other value → MEASURED. Revision 3 decided the
  source by the answering LINK's identity instead (the store's `default` →
  `prior-authored`, anything else → `measured`). That called a byte-identical
  user copy of `default.rxt` "measured", and rule 7 would have admitted the
  authored prior as EVIDENCE (M2's probe, reproduced on main:
  `window_contract_rev31/b1_witness.out` shows the copy resolving at link 0,
  stop `-I`, with the store's own digest `1822fb973b95a4da`). Link identity
  stays as a CROSS-CHECK (C-E1-1): an answer reached through
  `PCREC_FIND_STOP_DEFAULT` must be AUTHORED, because the store's `default`
  is authored by construction (E-1 adds that assertion to `findgen`'s
  pre-parse, §3.7.1).
- **Today's cells.** Under `-e byte` with no `--analysis`, `byte-rate` is
  `authored` (bundle `default`). Under `-e utf8` with no `--analysis`, it is
  `prior-none`: `default.rxt` declares `serves byte-rate when byte` only.
  Naming `weblog` or `log` makes it `measured` under both encodings (`cpfreq`
  via `encode-utf8` under utf8), with `bytes` 1,000,000 and 999,960. `log`'s
  stanza says `fidelity synthesized`, `weblog`'s states no fidelity. A user's
  `-I` bundle is `authored` or `measured` by what its own stanza declares, and
  the `l1none` fixture is `underivable-arrives` under `-e utf8`.
- **Why `prior-none` carries no table.** pcrec's own answer with no data is
  per question kind (D126 Q4): MASS is cardinality, PICK ties to its
  reader's rightmost, and COMPARE is false. A uniform table would answer
  COMPARE "true" for every pair, which is a density claim no data supports
  (the "false confidence" of D162 add. 2). So the kind ARRIVES, honouring
  D162 add. 2, and its provenance states that pcrec's prior here is the
  no-information answer. When D160's authored utf8 prior lands, the utf8 kind
  becomes `authored` with a table.
- **Evidence.** A row that needs EVIDENCE reads only `measured` (D162 add. 3).
  How MUCH evidence is now carried in `bytes` (§3.6).
- **`cpfreq` is never a kind.** The kit is encoding-blind (D147 add. 14), so
  pcrec derives the byte-domain kind (`encode-utf8`, `findings.c`) and sends
  that.

### 3.3 Rules

1. **Keyed by tag, never positional.** The kit looks a kind up by its tag. An
   unknown tag is IGNORED. A known tag whose `version` the kit does not serve
   reads as ABSENT.
2. **Every kind this pcrec knows is LISTED, present or absent.** An absent
   entry is the explicit absence D162 asks for. A tag missing from the list
   can only mean an older pcrec, and the kit treats it as absent too.
3. **One object per compile attempt, stated once** `[rev3]`. pcrec builds it
   from `Job.find`, which is per attempt. `[rev3.1 M5]` It is built EAGERLY,
   in `compile_driver` right after `pcrec_find_resolve` (the attempt's chain is
   resolved there, before the parse), and stored on `Job`.
   `pcrec_memfn_art` only passes the stored object to `mf_art_begin`, so the
   build point does not depend on which kit call comes first. It is stated
   ONCE, on `mf_art_begin`. Revision 2's same-pointer check and its NULL-mixing refusal
   `[r4 R9]` dissolve: one value per art cannot differ from itself.
4. **The per-site slot stays RESERVED** (D162 ruling 1). It is a different
   thing from the object: a per-SITE fact the kit cannot derive (match density,
   the activation fact of §13). No field is added until a measured case needs
   one. Filling it is an `MF_SITE_ABI` event (§8.2).
5. **Totality.** Every kit selection is TOTAL when the object, or any kind in
   it, is absent or `prior-none` (D162 ruling 2).
6. **Lifetime.** The object lives in the arena the art's `mf_arena` wraps, for
   the attempt. That outlives `mf_art_end`, and a retry attempt builds a new
   one with its new art.
7. **Evidence reads MEASURED only** `[rev3 C-15; rev3.1 m5]`. A reader of a
   kind as EVIDENCE reads it only under `measured` provenance (D162 add. 3).
   That is the whole of pcrec's obligation: the provenance FACT. Which kit
   rows read a kind as evidence, and what they select otherwise, is the
   kit's method and is stated in r17b′ (`lane/memfn-r17:docs/design/memfn/
   r17b_prime.md` §3-§4), not here (D157).
8. **What the kit reports back** `[rev3]` (§3.7.3). From the first commit that
   ROUTES a kit row reading a kind, the kit returns, at `mf_art_end`, a
   per-kind `consulted` bit: true iff a kit row of this art read that kind.
   This is R-MS2's boolean per knowledge source, at the analysis object's grain
   of one bit per kind, never per key. It is LAYER-INVARIANT: the same under
   `-fno-memfn-simd`, `-fmemfn-simd` at every level and every `--memfn=` deny,
   by the same rule as `proven` (§4.3). The checks are C-CONS and C-PERT
   (§3.7.7).
9. **An underivable kind refuses iff it is consulted** `[rev3.1 B1]`. A kind
   in an `underivable*` state (§3.2) refuses the compile with today's
   diagnostic ("analysis 'X': its 'K' block at line N counts nothing via V, so
   it has no byte-rate") exactly when a reader consults it: a pcrec reader's
   ask raises at the ask, as today; from B3b, a kit row's read is reported in
   the kit's `consulted` and pcrec raises the same refusal at the art-end
   pass (§3.7.3a), before the stamp renders. A compile in which nothing
   consults the kind compiles, as it does today. So the refusal set is the
   same before E-1, after E-1 and after B3b. This is today's reading of
   `docs/spec/findings.md` 3a¶3 ("is refused at compile"), which holds only
   when something asks; the alternative reading, an unconditional refusal,
   would be a caller-observable change with a D80 hunk, and is not taken.

### 3.4 What the object is not

It holds no per-site answers: not a set's mass, not a ranking, not a
survivor estimate. Those are derived by the kit (D162 add. 3's rule). It also
holds no consumer price (D161 add. 6).

### 3.5 The kit's per-compile memo (D162 add. 4)

- **What.** Anything the kit derives from the object: cube masses, a byte
  order, a site's run ranking (§6 S2).
- **The rule.** The memo is a PURE function of `(analysis object, the art's
  kit options)`. A site's text never depends on which sites were rendered
  before it.
  - **The check** shares no source with the memo: a test build renders every
    corpus artifact's sites twice, in forward and reverse site order, into
    two fresh arts, and compares each site's text.
  - **Its sabotage row:** a memo filled lazily from the first site's term.
- **Placement** `[r4 R10]` (a filed decision with a trigger, not a table):
  the memo lives in `mf_art` (per ATTEMPT), which the object's own lifetime
  keys correctly. **Trigger to move it per compile**: a measured compile-time
  cost of the memo build above the noise of a minimal compile; it would then
  be keyed by the `byte-rate` digest in kit state passed to `mf_art_begin`
  (D77; no such cost has been measured).

### 3.6 Filed analysis facts `[r4 R10]`

- ~~**Evidence strength**~~ `[rev3.1 M2]`: BUILT, no longer filed. Its trigger
  ("the first kit row that reads `measured` provenance as EVIDENCE") fires
  inside this very plan, at B3a/B3b, and the fact already lives in each data
  block's `provenance bytes` row. So `mf_prov.bytes` (and `fidelity`) are in
  the layout from its first declaration (§3.1), at no extra `MF_SITE_ABI`
  event. A SAMPLE count (for a kind whose exemplar is not a byte stream) is
  the remaining filed half: **trigger**, the first measured kind whose
  provenance states no `bytes`.

### 3.7 E-1: main's build step (window_contract S1) `[rev3]`

E-1 is r17b′ §3.1's "(main) E-1" row. pcrec builds `mf_analysis` with the
frequency kind ALWAYS present (`authored`, `prior-none` or `measured`;
`underivable-arrives` reads `prior-none`) and states it to the kit. D167 makes it buildable now. It lands AFTER the kit's
B2 merges and BEFORE B3a, whose five ported picks read it (KW-8: "a NULL
analysis would move bytes").

#### 3.7.1 What E-1 builds

| piece | where | what |
|---|---|---|
| the query table `[rev3.1 m1]` | `src/core/findings.c` | `find_queries[]`, the §3.2 rows: tag, payload version, `unmeasured`. It is the query vocabulary's ONE home. `find_derivs[]`'s third column becomes an index into it (a compile-time constant, so a `_Static_assert` on the row count holds). `rxt_find.c`'s `queries[]` (`chain_serves_enc`), `findings_dump.c`'s `FIND_QUERIES[]` and `rxt_source.c`'s error text ("query (byte-rate, run-rarity)") read it through one accessor. F-3 is retired here, not filed. The name avoids [KNOW-SRC]'s `ksrc_kinds[]`, which lists knowledge SOURCES, one tier up |
| the non-raising derivation `[rev3.1 B1]` | `src/core/findings.c` | `find_derive_byte_rate_status(Ctx *, PcrecFindRec *)` returns a status: OK, NONE (nothing answers), UNDERIVABLE (the answering block normalizes to nothing, today's `nr == -1`) or BROKEN (today's postcondition arm). It never calls `pcrec_ctx_fail`. It memoizes into the record: `byte_rate_derived` (the memo is filled) and `byte_rate_status`. Today's `find_derive_byte_rate` becomes this function plus the raise, and the raise lives only on the ASK path |
| the ASK path | `src/core/findings.c` | `pcrec_find_byte_rate` sets `byte_rate_asked`, calls the status derivation, and on UNDERIVABLE or BROKEN calls `pcrec_ctx_fail` with today's two messages verbatim. Its observable behaviour is unchanged: the same compiles refuse, with the same text and offset |
| the OFFER accessor | `src/core/findings.c` / `.h` | `pcrec_find_offer(Ctx *, size_t query, PcrecFindOffer *)`: evaluates T-KIND (§3.2) for one row through the status derivation and returns `{present, source, bundle, digest, bytes, fidelity, payload}`. It never sets `byte_rate_asked` and never refuses. The split between `asked` (consumption) and `derived` (the memo) is what keeps E-1 zero-mover |
| provenance in the block `[rev3.1 M2]` | `src/core/findings.h`, `scripts/findgen.c`, `src/parse/rxt_find.c` | `PcrecFindTblBlock` gains `prov_source` (the stanza's `source` token), `prov_bytes` (its `bytes`, 0 if absent) and `prov_fidelity` (its `fidelity`, or none). `findgen`'s pre-parse writes them into the committed `findings_table.inc`; `link_from_source` copies them for a runtime (`-I`, S1) bundle, from `RxtFindBlock`, which gains the same three fields from the source parser. `findgen` asserts that the store's `default` bundle declares `source authored` on every block (the cross-check of §3.2). `findings_table.inc` changes; no emitted byte does |
| the object builder `[rev3.1 M5]` | `src/core/compile.c` (the build point) and `src/gen/memfn_sites.c` (the mapping) | In `compile_driver`, right after `pcrec_find_resolve(&cx, …)`, one call builds the object for the attempt and stores it on `Job` (`job->analysis`), in the attempt's arena. The mapping `PcrecFind*` → `MF_PROV_*`/`MF_KIND_*`/`MF_FID_*` stays in `memfn_sites.c`, the one file that includes `memfn.h` for art state; `src/core` never includes `memfn.h`, so the call is through a `src/gen` function compile.c already links against. It asserts the payload invariant (§3.1). `pcrec_memfn_art` passes `job->analysis` to `mf_art_begin` and builds nothing |
| the record's comment `[rev3.1 m6]` | `src/core/findings.h` | `byte_rate_have`'s comment is re-worded from "... and a block answered" to "the memo holds a table (a block answered and derived), whether or not anything asked". `req_rate_why` (`src/facts/req.c`) reads `pcrec_find_byte_rate`'s return instead of `byte_rate_have`, so no reader outside `findings.c` reads the memo fields (C-E1-6 holds that) |
| nothing else | — | no emitter text, no stamp code, no flag, no listing. `pcrec_find_stamp` is UNCHANGED at E-1. Its generalization over the kinds table belongs to [KNOW-SRC]'s `ks_stamp` (`measure_sets.md` §9.2 part 5), so it is not built twice |

**Every attempt builds it** `[rev3.1 M5]`, at one stated point, whether or not
the attempt reaches a kit call. That is D162's "pcrec should send what it has",
stated once per art.

**Compile cost.** At default flags every compile already derives `byte-rate`
(§3.7.4), so the offer adds no derivation. It adds one derivation per attempt
only on the deny arms that ask nothing today: one normalization of 256 counts
(`pcrec_find_normalize`) over the pre-parsed store. The parse itself was moved
out of compile time by [FINDINGS] B1. `[rev3.1 M5]` The eager build also runs
on attempts that later refuse for an unrelated reason (a parse error), which
today never derive; the cost is the same one normalization. This is
UNMEASURED but bounded by that arithmetic. The E-1 census run reports compile
time beside its byte compare, with no gate on it.

**Compound artifacts.** Each part is its own compile (`part_compile` calls
`pcrec_compile_driver`) with its own `Job`, record and art, under the parent's
analysis and encoding. So each part builds an object of equal content at the
same eager point. C-E1-4's compound fixture checks the equality.

#### 3.7.2 The slot: per `mf_art_begin`, not per site (the reconciliation)

Revision 2 §3.1 put `mf_site.analysis` on every site. The kit's B1 declares the
slot on `mf_art_begin`, and E-1 fills it there. **The choice is per art**, for
five reasons:

1. **D162 ruling 1 is "ONE `mf_analysis` per compile".** A per-site pointer
   restates one compile-wide value on every site. Revision 2 then needed rule
   3's same-pointer check and the R9 NULL-mixing refusal to keep the copies
   equal. Stated once, the object cannot disagree with itself, so the check,
   its refusal and its sabotage row all disappear.
2. **The sibling knowledge source already rides there.** `mf_measures` is on
   `mf_art_begin` (R-MS1, `measure_sets.md` §4.1), and `consulted` comes back
   from `mf_art_end` (R-MS2). [KNOW-SRC]'s two knowledge kinds reach the kit
   through ONE channel shape.
3. **The memo keys exactly.** D162 add. 4's memo lives in `mf_art` and is a
   pure function of (object, the art's kit options) (§3.5). Handing the object
   to the art that owns the memo makes the key the art's own input.
4. **The art already carries compile-wide facts that way.** `mf_art_begin`
   takes `prefix`, `policy` and `denies`, which are compile-wide.
5. **The per-site slot D162 reserves is a different fact.** It is a per-SITE
   fact the kit cannot derive (match density, §13's activation fact). It stays
   reserved and is not spent on a compile-wide value.

**What revision 2 loses: nothing.** A site never needed a different object from
its art's. A stand-alone K3 caller passes NULL at `mf_art_begin`, and totality
holds.

#### 3.7.3 The stamp: CONSULTED, the [KNOW-SRC] family's one rule (RULED, D167 add. 2)

**The conflict revision 3 found.** Revision 2's R1 disposition made
`<PREFIX>_FINDINGS` mean OFFERED, while its sibling `<PREFIX>_MEASURES`
(`measure_sets.md` §3.5) means CONSULTED and [KNOW-SRC] (§9.2 part 5) builds
ONE stamp grammar for the family. Frank ruled CONSULTED for both ("q3:
consulted", D167 add. 2).

**The rule.**
- A kind's item appears in `<PREFIX>_FINDINGS` iff the kind was consulted: a
  pcrec reader asked it (`pcrec_find_byte_rate`, as today), OR a kit row read
  it (§3.3 rule 8's per-kind `consulted`). The item's text is today's
  (`query=bundle:digest`, or `query=none` where nothing answered).
- **The offer is not an ask.** Building the object (§3.7.1's
  `pcrec_find_offer`) does not set `byte_rate_asked`, and it never refuses
  (§3.3 rule 9).
- **So E-1 moves NO byte and no refusal.** It is not a pcrec abi event, it
  moves no byte-count reader, and it carries no D80 hunk. The object is an
  internal kit channel, and nothing caller-observable changes (§3.7.9).
  Revision 3 claimed this without the second half; B1 showed the offer's
  raising derivation would have moved the refusal set (§3.7.4a).
- **When the stamp's meaning becomes observable.** The kit's per-kind
  `consulted` joins the stamp at the first commit that ROUTES a kit row reading
  a kind. In r17b′'s plan that is **B3b**: the five ported picks route there
  and pcrec's own pick readers retire. That commit is zero-mover in the stamp
  iff, on every artifact, (kit consulted ∪ pcrec asked) equals today's pcrec
  asked set. Its emit_sweep compare proves that, S997 (§3.7.8) plants the OR's
  loss, and C-PERT (§3.7.7) checks the stamp against the bytes. B3b carries
  the findings.md §5 / match_api hunks of §3.7.9. S2's kit ranking, if it
  routes earlier than B3b, takes the same obligations at its own commit.
- **Where the OR is computed: after `mf_art_end`** (§3.7.3a). The render
  point moves there in its own zero-mover commit, RP, before any OR exists.

**What CONSULTED keeps** (the reasons it was the leaning): one rule for the
family (`ks_stamp` once, one census attribution); findings.md 5¶9's "moves the
digest of every artifact that CONSUMED it" stays true, so a regeneration of the
default prior does not move unread artifacts; and findings §6 #22 / S314 keep
their `""` witness.

**What CONSULTED costs:**
- **One more kit output.** It is the per-kind `consulted` bit, R-MS2's shape,
  owed at B3b and not at E-1.
- **A layer-invariance obligation.** If a SIMD-only row consulted a kind that
  SIMD-off did not, the pattern-level `_FINDINGS` stamp would differ by layer,
  which breaks the floor rule (SIMD-on = SIMD-off + guarded text). So
  `consulted` must be a function of the site request, the same in every layer,
  as `proven` is (§4.3). The check is C-CONS (§3.7.7). The same obligation
  already binds `<PREFIX>_MEASURES`'s `consulted`, and `measure_sets.md` does
  not state it (F-4).
- **An honesty obligation** `[rev3.1 X1]`. A stamp built from the readers' own
  reports can only be as honest as the reports. A kit row that reads a kind
  and does not report it, or a pcrec reader that reads the memo without
  asking, gives an artifact whose bytes depend on data its stamp does not
  name. Nothing in revision 3 detected that. C-PERT (§3.7.7) does, from the
  bytes alone.

#### 3.7.3a The ONE render point: after `mf_art_end` `[rev3.1 M3, U3]`

**The problem.** Today `<PREFIX>_FINDINGS` and its `rx_info` initializer
`.findings = "…"` are written in `emit_info_def` (`src/gen/emit_dfa.c`, the
stamp beside its comment "the stamp must read the record after the LAST
reader"), on both engines' paths. The kit's per-kind `consulted` exists only at
`mf_art_end`, which pcrec calls at the end of `pcrec_memfn_stamps_render`
(`src/gen/memfn_stamps.c`), the finishing pass `compile.c` runs after the
engine emitter and before the size caps measure the text. So the OR of §3.7.3
has no point at which both of its inputs exist and the stamp is still unwritten.
Once the kit can consult, the kit IS the last reader, and findings design §6.4
rule 2 moves the stamp after it.

**The render point, stated once for the family.**
1. **When.** In the finishing pass, after the kit's own three stamp lines
   (`mf_stamps`) are rendered and AFTER `mf_art_end` returns (the art's last
   act, which also reports the per-kind `consulted` from B3b on), and before
   the pass splices its lines and returns, so still before the size caps
   measure the artifact. The order inside `pcrec_memfn_stamps_render`
   becomes: libc scan, `mf_stamps`, `mf_art_end` (`pcrec_memfn_art_end`'s
   checks), §3.3 rule 9's refusal check, then pcrec's knowledge stamps, then
   the splices.
2. **What.** `_FINDINGS`: the `#define <PREFIX>_FINDINGS` line and the
   `.findings = "…"` initializer. `_MEASURES` (at M0): the
   `#define <PREFIX>_MEASURES` line and the `.measures = "…"` initializer.
   Both are rendered by one call, the natural single call site of [KNOW-SRC]'s
   `ks_stamp` (before [KNOW-SRC], `pcrec_find_stamp` for `_FINDINGS` and
   M0's renderer for `_MEASURES`, at the same call site).
3. **Where in the text: unchanged.** The engine emitters write a MARK in place
   of each line and initializer, at today's byte positions (the same
   placeholder-lead mechanism as `pcrec_emit_memfn_mark`, a second mark kind),
   and the pass splices the rendered text over them. So the move changes no
   byte, and no reader of the stamp's position or of the rx_info layout moves.
4. **Both engines, and compounds.** The DFA's `emit_info_def` and the VM's
   epilogue (`vm_emit_epilogue` → `pcrec_emit_info`) reach the same info
   writer, so both write the marks. A compound artifact's `rx_info` is the
   shell's (P's, written by the DFA emitter's shell branch,
   `src/gen/emit_compound.c`'s header). Its stamp is the union of what P's
   attempt and every part's attempt consulted, because the artifact's bytes
   depend on all of them. Each part's finishing pass hands its consulted set
   up; the shell's pass renders the union. Whether today's shell already
   unions its parts' asks is not verified here. The perturbation prototype ran
   over the whole corpus, which includes the compound-admitted patterns, and
   found no compound FAIL (§3.7.7 C-PERT), so the rule is stated to keep that
   true.
5. **The prefix.** The pass renders at the prefix placeholder, as the kit's
   stamps do, so `-p` cannot move it (K79).

**The commit, RP.** It is its own commit and lands no later than the first of
B3b and M0, ahead of any OR in that series, so its zero-byte property is
proven while the OR cannot yet change a stamp.
- **Check C-RP**: emit_sweep, every stream and arm of G1-E1, the RP tree
  against its parent: 0 movers, tokens and refusals identical. A mark left
  unreplaced is an internal-error refusal (as for the kit's mark), so a lost
  splice cannot ship.
- **Sabotage S1014 PROPOSED (lands with B3b)**: the stamp is rendered before
  `mf_art_end` with the OR present. It is detectable only where the kit is the
  only consumer, so its detectors are B3b's emit_sweep and C-PERT on the
  kit-only population.

**The sibling edit owed** (not made here): `measure_sets.md` §3.5 and §4.2 need
the same render-point sentence for `_MEASURES` and `.measures =`, and §9.2
part 5 needs it for `ks_stamp`'s call site. It belongs in that note's next
revision, beside F-4 (layer invariance). Until then, M0's builder reads §3.7.3a
here.

#### 3.7.4 The mover population (revision 2's open question 5): MEASURED

**Instrument:** `window_contract_rev3/stampcount.py` and `stampcount_deny.py`.
They compile emit_sweep's own corpus enumeration (the argv stream: 5,790
`pattern` lines over every `tests/**/*.rxt`, `-p rx --features all -o -`) with
this tree's `build/pcrec` (main `063b4a4b4`) and tally each artifact's
`#define RX_FINDINGS` value. Run on the Linux dev box, 2026-10-16.

| arm | compiled | `""` today | `byte-rate=default:…` | `byte-rate=none` |
|---|---|---|---|---|
| default, `-e byte` | 5,336 | **0** | 5,336 | 0 |
| default, `-e utf8` | 5,364 | **0** | 0 | 5,364 |
| `--engine=vm` | 5,337 | **0** | 5,337 | 0 |
| `-fno-req-byte` | 5,336 | 1,973 | 3,363 | 0 |
| `-fno-req-byte -fno-req-run` | 5,336 | 1,973 | 3,363 | 0 |
| `-fno-req-byte -fno-req-run -fno-prefilter` | 5,336 | 3,275 | 2,061 | 0 |
| the same, `-e utf8` | 5,364 | 3,246 | 0 | 2,118 |
| `--engine=vm -fno-req-byte -fno-req-run` | 5,337 | **5,337** | 0 | 0 |

(The remaining 454 / 426 / 453 lines are compile refusals in each arm.)

**The answer.** "Every artifact with `""` today" IS the whole population of
the OFFERED event, because a non-empty stamp cannot move: the same derivation
gives the same bundle and digest. That population is EMPTY at default flags in
all three default arms. Every default compile already asks, by design:
`pcrec_req_window` asks the byte-rate "FIRST, before any branch, so whether the
compile consumed it does not depend on the pattern" (findings design §6.4
rule 1, `req.c`). The `""` artifacts exist only where the asking readers are
denied, which is the test-axes deny arms and the findings "nothing asked" cell.

Two consequences:
- **The OFFERED event's default-population cost is zero.** Its cost falls on
  the deny arms (up to every artifact of `--engine=vm -fno-req-byte
  -fno-req-run`) and on the two checks that read `""` (§3.7.6).
- **A zero-mover gate for E-1 is VACUOUS on the default arms**, because no
  default artifact can show the offer leaking into the stamp. The E-1 gate must
  include a deny arm (§3.7.7 G1-E1); that is the K35 point here.

**Not measured:** the bench's patterns (read-only, not compiled here) and the
composition stream (`--source FILE`). Both are owed by the E-1 census
(§3.7.7).

#### 3.7.4a The refusal population (B1): MEASURED `[rev3.1]`

**The defect revision 3 carried.** Revision 3's offer derived through
`find_derive_byte_rate`, which calls `pcrec_ctx_fail` when the answering block
normalizes to nothing ("counts nothing via V"). Today that refusal is LAZY: it
fires only when a reader asks. An offer on every attempt would have fired it on
compiles that ask nothing.

**The witness, reproduced on main `2288ad1cb`**
(`window_contract_rev31/b1_witness.sh`, transcript `b1_witness.out`), with
`tests/findings`' own `l1none` fixture (one `cpfreq` block, `serves byte-rate
when utf8 via encode-latin1`, one row `U+20AC`), all under
`-e utf8 -I L1 --analysis l1none`:

| invocation | today |
|---|---|
| `--pattern 'abc'` | refused: "counts nothing via encode-latin1" |
| `--pattern 'caf.'` | refused, same |
| `--pattern '^abc' -fno-req-byte` | compiles, `RX_FINDINGS ""` |
| `--pattern '^abc' -fno-req-byte -fno-req-run -fno-prefilter` | compiles, `""` |
| `--pattern 'caf.' --engine=vm -fno-req-byte -fno-req-run` | compiles, `""` |

Revision 3's E-1 would have refused the last three.

**The population, crossed with the analysis axis**
(`window_contract_rev31/analysiscount.py`, output `analysiscount.out`, the
same argv stream as §3.7.4, 5,790 `pattern` lines, main `2288ad1cb`, Linux dev
box). Per arm, the count of compiles that SUCCEED today with `""` under
`l1none`. Each of them refuses when asked, so each is a compile a raising offer
would have refused:

| arm (all `-e utf8 -I L1 --analysis l1none`) | compiles `""` | refused underivable | refused other |
|---|---|---|---|
| default | 0 | 5,364 | 426 |
| `--engine=vm` | 0 | 5,367 | 423 |
| `-fno-req-byte` | **1,905** | 3,459 | 426 |
| `-fno-req-byte -fno-req-run -fno-prefilter` | **3,246** | 2,118 | 426 |
| `--engine=vm -fno-req-byte -fno-req-run` | **5,367** | 0 | 423 |

The other analysis cells (none, `weblog`, `log`, a measured user `-I` bundle
`mine`) never refuse underivable, and their `""` counts equal the no-analysis
arm's exactly (1,973 / 3,275 / 5,337 under byte, 1,907 / 3,246 / 5,367 under
utf8). So the analysis axis does not move WHICH compiles ask; it moves only
whether an ask can refuse. Two utf8 patterns are `""` with no analysis but
refuse under `l1none` in the `-fno-req-byte` arm (1,907 against 1,905): they
are F-5's two witnesses, whose EARLIER attempt asked (§3.7.6 F-5).

**The fix**, §3.7.1: the offer derives through the non-raising status
derivation, the ASK path keeps the raise, and §3.3 rule 9 keeps the refusal
the consumer's at B3b. G1-E1 (§3.7.7) holds the bold cells as floors.

#### 3.7.5 The OFFERED alternative: NOT TAKEN (D167 add. 2)

Frank ruled CONSULTED. Revision 3's exact build text for OFFERED (the abi
event, the stamp change, the movers, the census, the re-aims, the sibling) is
kept in that revision (`git show cd9fda38d:docs/design/memfn/window_contract.md`,
§3.7.5) and is not carried forward. One fact from it stays true and is used
above: a deny-arm artifact within 68 bytes of either size cap would change its
ladder decision if its stamp grew, which is why §3.7.3a moves no byte.

#### 3.7.6 Readers, found by grep (`063b4a4b4`)

**Readers of the stamp's VALUE and of the consumption record** (grep
`FINDINGS`, `byte_rate_asked`, `byte_rate_have`, `\.findings`, `byte-rate=`,
`nothing asked`):

| reader | what it reads | E-1 (CONSULTED) | OFFERED |
|---|---|---|---|
| `src/core/findings.c` `pcrec_find_stamp`; the accessor `pcrec_find_byte_rate` | `byte_rate_asked` | the stamp unchanged; the accessor gains the status derivation and keeps the raise (§3.7.1); the record gains `byte_rate_derived` and `byte_rate_status` | `asked` is set by the build; `""` unreachable |
| `src/core/findings.h` (the record, `byte_rate_have`'s comment; the stamp's "the empty string when nothing was asked") | the record's comment | `byte_rate_derived`/`byte_rate_status` added; `byte_rate_have`'s comment re-worded `[rev3.1 m6]`; the stamp comment unchanged | comment changes |
| `src/gen/emit_dfa.c` `emit_info_def` (the stamp and its comment; the `.findings =` initializer) | the stamp text | unchanged at E-1; at RP the two become marks rendered by the finishing pass (§3.7.3a), the comment moving with them | comment changes |
| `src/facts/req.c` `req_rate_why` | `byte_rate_have` DIRECTLY, not through the accessor | `[rev3.1 m6]` reads `pcrec_find_byte_rate`'s return instead (its two callers ask first, so the value is the same); C-E1-6 holds that no reader outside `findings.c` reads the memo fields. See F-2 | same |
| `tests/findings/run_findings_tests.sh:19-22`, `:141-166` (§4 incl. `check_stamp "nothing asked" ""`), `:392-403` (§6 #22, `_FINDINGS ""` on `t_quiet.c`) | the stamp, `""` included | unchanged; they become E-1's own detectors (§3.7.7) | re-aimed |
| `tests/mech/sabotages/S314_findings_record_outlives_compile.sh` (`SAB_BEFORE` = the `return "";` line; `SAB_REACH` greps `_FINDINGS ""`) | the anchor and a `""` witness | unchanged | re-aimed or retired |
| `tests/resource/run_resource_tests.sh:665-669`; `tests/codegen/run_cpset_structure.sh:772` | byte counts (+55 macro, +56 initializer) | unchanged | re-measured at the same `-o` basename |
| `tests/codegen/run_encoding_checks.sh:599-606`, `:642`, `:1506-1508` | utf8 side `== byte-rate=none`, byte side `!= none` | unchanged (holds: every default utf8 compile asks) | unchanged |
| `tests/codegen/run_recursion_identity.sh:1135-1140` | the (B) pin's named-lines narrative | unchanged | re-pin (abi event) |
| `docs/spec/findings.md` §5¶1-¶9; `docs/spec/match_api.md` 6.3.10¶10-¶11, the `rx_info` row 28 (`:1287`), 6¶14, the stamp-class table (`:2467`) | the stamp's meaning | unchanged at E-1; B3b's hunk (§3.7.9) | E-1's hunk |
| `docs/design/measure_sets.md` §3.5, §9.2 part 5, §9.3, §9.5 | the sibling's statement of the shared rule | consistent | reopened |
| `lib/pcrec.h:1582` | "built under it" | unchanged | unchanged |
| `src/core/findings.c` `find_derivs[]`; `src/parse/rxt_find.c` `chain_serves_enc`'s `queries[]`; `src/dump/findings_dump.c` `FIND_QUERIES[]`; `src/parse/rxt_source.c` the "(byte-rate, run-rarity)" error text `[rev3.1 m1]` | the query vocabulary, four spellings | read `find_queries[]` (§3.7.1); the error text and the listings print identical bytes | n/a |
| `src/core/findings.h` `PcrecFindTblBlock`; `scripts/findgen.c`; `src/core/findings_table.inc`; `src/parse/rxt_find.c` `link_from_source`; `src/core/internal.h` `RxtFindBlock` `[rev3.1 M2]` | the block's fields | gain the provenance stanza's `source`, `bytes`, `fidelity`; `findings_table.inc` regenerated (`make gen-findings`); `tests/findings`' block-for-block agreement check (embedded text parsed vs the table) covers the new fields | n/a |
| `src/core/compile.c` `compile_driver`, after `pcrec_find_resolve`; `src/gen/memfn_sites.c` `pcrec_memfn_art` `[rev3.1 M5]` | where the object is built | the eager build and the hand-over (§3.7.1) | n/a |

**Readers of the abi NUMBER** (OFFERED only; grep `78` beside `abi`/`ABI`):
`src/gen/emit_dfa.c:54` `PCREC_ARTIFACT_ABI`; `match_api.md §1¶7`
(the K80 `#error` text) and its "abi is N" sentence;
`docs/dev/history/abi_changelog.md`; `tests/codegen/run_codegen_tests.sh:3149`
`ABI_EXPECT`; `tests/codegen/run_recursion_identity.sh:1251` FILEPIN;
`tests/mech/sabotages/S693_abi_not_bumped.sh:51`. The rest of the reader list
is re-derived by grep at landing (D94): the byte-count class (r17b′ §3.4's
list), the alpha normalizers, then the registry, codegen and rxtsource suites
and `make test-codegen`. At E-1 under CONSULTED none of these moves.

**Findings from the grep:**
- **F-2, LATENT** `[rev3.1 m4]`. `req_rate_why` writes `rate:builtin-prior`
  iff `byte_rate_have`, which is true for ANY answering block, a measured
  bundle included. `docs/spec/facts_listing.md` 4.1.3¶4 defines
  `rate:builtin-prior` as "the shipped byte-frequency prior". But no CLI path
  can list facts under a non-default analysis today: `pcrec -p rx --analysis
  weblog --emit-facts --pattern abc` is refused ("--analysis applies to a
  compile (a file operand or --pattern) or to --list-analysis FILE only"). So
  the token is wrong in the record and unreachable through the listing.
  **Trigger:** the first path that lists facts under a non-default analysis.
  E-1's T-KIND names the provenance (`measured` vs `authored`) that a fix
  would read.
- ~~**F-3**~~ `[rev3.1 m1]`: RETIRED at E-1. The query vocabulary's four
  spellings read `find_queries[]` (§3.7.1).
- **F-4.** `measure_sets.md` §4.2's `consulted` has the layer-invariance
  obligation of §3.7.3 and does not state it. That is for its next revision,
  beside §3.7.3a's render-point sentence.
- **F-5, the stamp reports the FINAL attempt only** `[rev3.1, found by the
  C-PERT prototype]`. `Job.find` is per attempt, so `<PREFIX>_FINDINGS` reads
  the final attempt's record. A compile whose earlier attempt consulted the
  byte-rate and whose final attempt did not stamps `""`, yet the artifact
  depends on that earlier read: the ladder's decision to retry, and the size a
  `_WHY` text quotes, both come from the earlier attempt. Witnesses, under
  `-e utf8 -fno-req-byte`: `(\p{Xwd})x` (`tests/uprops/
  size_ladder_prefilter_drop.rxt`) and `x(\p{Xwd})y` (`tests/utf8/
  wclass_illformed.rxt`). Attempt 0 builds the hybrid prefilter, asks the
  byte-rate and overflows the size cap; the final attempt drops the
  prefilter (`RX_ENGINE_SEL "size-cap-retry"`) and asks nothing. Under
  `--analysis weblog` the artifact's `RX_VM_PREFILTER_WHY` reads "hybrid
  1040437 > 1000000" where with no analysis it reads "hybrid 1040399 >
  1000000", with the stamp `""` in both. Under the `l1none` fixture attempt 0's
  ask REFUSES the compile, so these two are also the 1,907-vs-1,905 gap of
  §3.7.4a. C-PERT FAILS on exactly these two over the whole prototype run
  (`perturb_proto.out`). Q6 (§12) asks what the stamp should record; the
  leaning is the union over the compile's attempts.
- **F-6, a spec sentence that reads two ways** `[rev3.1 B1]`.
  `docs/spec/findings.md` 3a¶3 says a block all of whose code points drop "is
  refused at compile". The code refuses only when a reader asks (§3.7.4a).
  §3.3 rule 9 keeps the code's reading. The sentence should say "a compile
  that consults the byte-rate is refused". That is a wording fix to match
  shipped behaviour, not a contract change. FILED for the manager (doc
  findings are filed, not fixed in a design lane); B3b's findings.md hunk is
  a natural carrier.

#### 3.7.7 Checks (each against a source the subject does not share, unless labelled)

| id | checks | expectation from | population and reach |
|---|---|---|---|
| **G1-E1** zero-mover `[rev3.1 B1, m3]` | emit_sweep, every stream, over the arm × analysis product below, plus the bench patterns read-only: 0 movers; tokens, stderr and refusals identical (the refusal SET compared as keys) | the pre-E-1 binary | **Arms**: default, `-e utf8`, `--engine=vm`, and the deny arms `-fno-req-byte`, `-fno-req-byte -fno-req-run -fno-prefilter` (both encodings) and `--engine=vm -fno-req-byte -fno-req-run` (both encodings). **Analysis cells** for every arm: no analysis, `--analysis weblog`, a measured `-I` user bundle, and the `l1none` fixture (utf8 arms; it serves utf8 only). The deny arms are REQUIRED: the default arms hold 0 `""` artifacts (§3.7.4). **Floors**, literals measured at `2288ad1cb` (`analysiscount.out`): ≥ 1,900 `""` in `-fno-req-byte` byte; ≥ 5,300 `""` in the VM deny arm byte and utf8 (m3); and in the `l1none` cells, ≥ 1,900 / 3,200 / 5,300 compiles that SUCCEED with `""` in the three utf8 deny arms (§3.7.4a's bold cells, the compiles that refuse when asked and compile when not; B1's population) |
| **C-E1-1** object content | a trace-build record per attempt (`-DPCREC_CAND_TRACE`, a `KSRCTRACE` line: query, tag, state, source, bundle, digest, bytes, fidelity, and from B3b `consulted`), over fixtures: `-e byte`/`-e utf8` × {no `--analysis`, `weblog`, `log`, a user `-I DIR/default.rxt` byte-identical copy, a user `-I` bundle named `default` that declares a measured source, a user `-I` bundle `mine` that declares `source authored`, `include default` by name, a two-link `include` chain, `l1none`} | a HAND-WRITTEN expected (state, source, bundle, bytes, fidelity) table per fixture, and each digest recomputed in python from the fixture's rows (`tests/findings`' `bdig`/`res_fixtures.py`, which re-derive digests independently). The link-identity CROSS-CHECK (§3.2): every answer through `PCREC_FIND_STOP_DEFAULT` reads AUTHORED | 18 cells; every T-KIND row that can fire at E-1 (`no-shape` on `run-rarity`, `underivable-arrives`, `measured`, `authored`, `prior-none`) fires at least once, a reach floor per row. `underivable`, `authored-absent` and `absent` need a payload-carrying MEASURED-ONLY kind and are declared UNREACHED until B4 gives `run-rarity` a shape (then a user `-I` authored `bigram` bundle reaches `authored-absent`) |
| **C-E1-2** query completeness | the object lists every tag once, in vocabulary order | a hand-written list in the test (`byte-rate`, `run-rarity`), cross-read with findings.md 5¶2's query order | the `run-rarity` entry is ABSENT through `no-shape` until B4 |
| **C-E1-3** payload invariant | non-NULL iff PRESENT and source ∈ {AUTHORED, MEASURED}; a byte-rate payload sums to 1,000,000; PRIOR_NONE has bundle NULL, digest 0, bytes 0; MEASURED has bytes equal to the stanza's `bytes` row | the trace record, recomputed (the build's own assertion is the second, shared-source line) | every fixture of C-E1-1 |
| **C-E1-4** stamp/object AGREEMENT `[rev3.1 m2]` | wherever `_FINDINGS` has `byte-rate=B:D`, the object's byte-rate is PRESENT with bundle B, digest D; `byte-rate=none` ⇔ PRIOR_NONE; `""` with the object PRESENT is the OFFERED-NOT-ASKED cell (CONSULTED's own evidence); a compound fixture's parts carry equal objects | **SHARED SOURCE**: the stamp and the object both come from `find_derive_byte_rate_status`'s memo, so a wrong memo agrees with itself. This is an agreement check only. The independent line it leans on is C-E1-1's python digest | `multi.rxt` (findings §6 #22's fixture: `t_asks`, `t_quiet`) plus a compound split fixture |
| **C-E1-5** the `unmeasured` column `[rev3.1 M1]` | the rows marked `ARRIVES` are exactly the queries a pcrec reader asks | a grep of `src/` for the query accessors' callers outside `findings.c` (today: `pcrec_find_byte_rate`'s callers in `src/facts/req.c`, `src/facts/facts.c` and `src/gen/emit_dfa.c`), derived by the test, not read from the table | both rows of `find_queries[]` |
| **C-E1-6** the memo has no outside reader `[rev3.1 m6]` | `byte_rate_have`, `byte_rate_status`, `byte_rate_derived` and `byte_rate[]` are read nowhere outside `src/core/findings.c` | `tests/findings/structural_check.py`, which already polices the gate, gains the field list | the whole tree |
| **C-RP** the render point moves no byte `[rev3.1 M3]` | emit_sweep, G1-E1's arm × analysis product, the RP commit against its parent: 0 movers | the parent binary | lands with RP (§3.7.3a), before any OR |
| **C-CONS** layer invariance (owed at B3b) `[rev3.1 M4]` | the per-kind `consulted` bits, read DIRECTLY from the `KSRCTRACE` record's `consulted` field, are identical under `-fno-memfn-simd`, `-fmemfn-simd` at every live level, and every `--memfn=` deny; and `_FINDINGS` is identical across the same layers | the SIMD-off compile | the stamp half runs on the deny arms of G1-E1 crossed with `-fmemfn-simd`, where `""` exists; the default arms are blind to it, because pcrec's own ask masks the OR. **Floor**: at least one artifact per deny arm where the kit is the ONLY consumer (the trace shows `consulted` from the kit and no pcrec ask), counted at B3b's landing |
| **C-PERT** perturbation honesty `[rev3.1 X1]` | see below | the artifact's own bytes, under data that changed | see below |
| ASan/LSan | the object outlives `mf_art_end` and is freed with the attempt | — | `make asan` over `test-findings` and `test-memfn` |

**C-PERT, the perturbation check** `[rev3.1 X1]`. The stamp claims "these are
the kinds this artifact read". C-PERT tests the claim from outside, by changing
the data and watching the bytes. It reads neither pcrec's ask record nor the
kit's `consulted` report, so a reader that reads and does not report
(learnings §3: a control sharing a source with what it controls) cannot hide
from it.

- **The method.** For each kind with a payload shape (`find_queries[]` rows of
  payload version > 0; today `byte-rate`), compile every artifact of the
  population twice, under the SAME analysis name and stop, `-I DIR --analysis
  default`:
  - BASE: `DIR/default.rxt` is a verbatim copy of the store's.
  - PERT: the same file with the kind's data perturbed. For `byte-rate`, the
    256 `freq` rows' values reversed by rank (rarest ↔ commonest), plus one
    `cpfreq` block serving `utf8` (so under `-e utf8`, where pcrec's prior is
    `prior-none`, data is added, not perturbed).
  Keeping the name and the stop means only the DATA differs, so the digest is
  the only stamp text that can change, and its length is fixed.
- **The verdicts.** Per artifact, reading only the emitted bytes and the stamp
  text:
  - FAIL `moved`: BASE's stamp omits the kind, and the bytes outside the two
    stamp lines (`#define <P>_FINDINGS`, `.findings =`) differ;
  - FAIL `refusal`: BASE's stamp omits the kind, and exactly one side refuses;
  - FAIL `stamp`: BASE's stamp omits the kind and PERT's lists it (a
    consultation that depends on the data must have read the data first);
  - otherwise legal (`consulted-moved`, `consulted-same`, `quiet`).
- **The null control**, per artifact: BASE must equal a bare compile (no
  `-I`, no `--analysis`) BYTE FOR BYTE, the whole file. This proves the
  `-I`/`--analysis default` route itself moves nothing, so a FAIL is the
  data's doing.
- **The power control.** A consulted artifact that MOVES under PERT is one a
  dropped stamp item would turn red. Its count is the check's power, and it
  carries a floor per arm, so a perturbation too weak to move anything cannot
  read green.
- **Each kind's perturber is a row** of a declared table in the test (tag →
  perturber). A kind with a payload shape and no perturber FAILS the check, so
  a new kind cannot ship unperturbed.
- **Arms.** G1-E1's arms (the deny arms are where `""` exists, so they are
  where the check has teeth: at default every artifact is consulted by pcrec's
  own ask), each under `-fno-memfn-simd` and, from B3b, `-fmemfn-simd`.
- **The prototype**, run on main `2288ad1cb` over the full corpus argv stream
  in eight arms (`window_contract_rev31/perturb_proto.py`, output
  `perturb_proto.out`): **0 null-control failures** in any arm. **Power**
  (consulted artifacts that moved): 1,161 default byte, 707 default utf8, 557
  `-fno-req-byte` byte, 539 utf8, 263 / 279 in the `-fno-prefilter` arms;
  the VM deny arm is all `quiet` (5,337 / 5,367, nothing consulted). **FAILs:
  exactly 2**, both `moved`, both in `-fno-req-byte` utf8, the F-5 witnesses
  (§3.7.6).
- **Where it runs.** A fixed 1-in-16 slice of the population in `make
  test-findings` (with its own literal floors, measured at landing), and the
  full population in the E-1 census and at B3b's landing.
- **Its standing exception.** F-5's two witnesses FAIL today, by a defect the
  check exists to find. Until Q6 is ruled and fixed, they are a NAMED bucket,
  selected by an INDEPENDENT criterion: the artifact's own fallback stamp
  says an earlier attempt was discarded (`<PREFIX>_ENGINE_SEL` is
  `size-cap-retry` or another ladder token), never the findings record. The
  bucket carries a floor (≥ 2) and an exact-membership pin, so it cannot grow
  silently and goes red when F-5 is fixed.
- **Sabotage.** S1015 (B3b's: a kit row reads a kind and drops its
  `consulted` bit) and S1016 (E-1's: `pcrec_find_byte_rate` marks `asked` only
  when it derives, so after the eager offer no ask marks). Both are §3.7.8's.

#### 3.7.8 Sabotage (S991-S998 ALLOCATED by the manager; S1009-S1016 PROPOSED `[rev3.1]`)

| id | plant | detector | reach witness |
|---|---|---|---|
| S991 | the offer marks the query asked (`pcrec_find_offer` sets `byte_rate_asked`) | findings §4 "nothing asked" (`-fno-req-byte --pattern '^abc'` stamps `byte-rate=default:…` where `""` is expected) and §6 #22; G1-E1's deny arm | `-fno-req-byte '^abc'` compiles and builds the object (every attempt does) |
| S992 `[rev3.1 M2]` | provenance by NAME: AUTHORED iff the bundle is named `"default"` | C-E1-1's cell for a user `-I` bundle NAMED `default` that declares a measured source (expected MEASURED, got AUTHORED) | the `-I` fixture answers through `PCREC_FIND_STOP_DIR` |
| S993 | `prior-none` carries a uniform table as payload (D126 Q4's false confidence) | C-E1-3 | `-e utf8` with no `--analysis` |
| S994 | the object is built once per PROCESS (a static cache), not per attempt | C-E1-4 on `multi.rxt` extended with a target under a different `analysis` line | two targets in one invocation |
| S995 `[rev3.1 M1]` | byte-rate's `unmeasured` cell flipped to `ABSENT` | C-E1-1's `-e utf8` cells (expected PRESENT/prior-none, got ABSENT) and C-E1-5 | `-e utf8` with no `--analysis` |
| S996 `[rev3.1 m2]` | the provenance digest computed over the COUNTS, not the derived ppm. The plant site is the offer's own digest computation: `pcrec_find_offer` computes `digest` itself from the payload it returns (`pcrec_find_byte_rate_digest(ppm)`), and the plant feeds it the block's counts. A copy of `fr->byte_rate_digest` would make the plant undetectable | C-E1-4 (object digest ≠ stamp digest) and C-E1-1 (≠ the python recompute) | any byte compile that asks |
| S997 (B3b's) | pcrec does not OR the kit's per-kind `consulted` into the stamp | B3b's zero-mover emit_sweep (stamps drop to `""` where a moved pick was the only asker) and C-PERT | the five ported picks' population |
| S998 (B3b's) | a SIMD-only kit row sets `consulted` | C-CONS (the `KSRCTRACE` `consulted` field, compared directly) | `-fmemfn-simd` arm, deny arms |
| S1009 PROPOSED (E-1) `[rev3.1 B1]` | the offer derives through the RAISING path (the status split folded back) | G1-E1's `l1none` cells (a compile that succeeds today refuses), and, in `make test`, a new `tests/findings` §12 cell beside the existing "a block all of whose code points drop is refused" cell: the same fixture under `-fno-req-byte` COMPILES and stamps `""` | `-e utf8 -I L1 --analysis l1none --pattern '^abc' -fno-req-byte` |
| S1010 PROPOSED (E-1) `[rev3.1 B1]` | T-KIND's `underivable*` rows deleted, so an underivable block falls to `measured` with a NULL payload | C-E1-3 (payload invariant) and C-E1-1's `l1none` cell | `-e utf8 -I L1 --analysis l1none` on any pattern under a deny arm |
| S1011 PROPOSED (E-1) `[rev3.1 M1]` | the `authored` row loses its `unmeasured = ARRIVES` conjunct | C-E1-1's authored-`bigram` cell (expected ABSENT, got PRESENT/AUTHORED) | **UNREACHED until B4** gives `run-rarity` a shape; then a user `-I` bundle with an authored `bigram` block. Declared UNREACHED with that trigger |
| S1012 PROPOSED (E-1) `[rev3.1 M2]` | provenance by LINK: MEASURED iff the answering link is not the store's terminal (revision 3's rule) | C-E1-1's `-I DIR/default.rxt` copy cell and the `mine` (`source authored`) cell (expected AUTHORED, got MEASURED) | the `-I` fixtures |
| S1013 PROPOSED (E-1) `[rev3.1 M5]` | the object is built lazily, on the first kit call, instead of after `pcrec_find_resolve` | C-E1-1's ordering assertion: each attempt's `KSRCTRACE` build record comes immediately after its chain-resolution record and before any parse record | any compile under the trace build |
| S1014 PROPOSED (B3b) `[rev3.1 M3]` | the stamp is rendered before `mf_art_end` with the OR present | B3b's zero-mover emit_sweep and C-PERT on the kit-only population | the five ported picks under the deny arms, where the kit is the only consumer |
| S1015 PROPOSED (B3b) `[rev3.1 X1]` | a kit row that reads a kind drops its `consulted` bit | C-PERT (`moved`: the bytes change with the data while the stamp omits the kind) | the kit-only population of C-CONS's floor |
| S1016 PROPOSED (E-1) `[rev3.1 X1]` | `pcrec_find_byte_rate` marks `asked` only when it derives (tests `byte_rate_derived` where it should test `byte_rate_asked`), so after the eager offer no ask marks | C-PERT at the default arms (every consulted artifact's stamp drops to `""` while its bytes move: 1,161 byte, 707 utf8 in the prototype) and findings §4 | any default compile |

S991-S996 and S1009-S1013, S1016 land with E-1. S1014 lands with B3b (the
RP commit has no OR to plant against). S997, S998 and S1015 land with B3b.
Sixteen ids in all; the eight new ones are the manager's to allocate.

#### 3.7.9 D80 spec hunks

**E-1 carries NONE.** The object is the kit's input, and `docs/spec/` describes
no `memfn.h` struct. No stamp, flag, limit, listing, entry or diagnostic
changes, and no refusal moves (§3.7.4a). `findings_table.inc` gains fields; no
listing prints them. (F-6's wording fix to findings.md 3a¶3 is a doc finding,
FILED, not an E-1 obligation.)

**RP carries NONE.** The render point moves; no byte moves (C-RP).

**B3b carries these**, because the stamp's meaning becomes observable there:
- `findings.md` 5¶2: "One `query=bundle:digest` item per query the compile
  CONSULTED (a pcrec reader asked it, or a pcrec-memory-functions row read it),
  in the fixed query order…"
- 5¶4: "The empty string when nothing was consulted."
- a new 5¶10: "Every compile OFFERS the kit the analysis object (`byte-rate`
  always, with its provenance; other kinds when measured). An offer that no
  reader consults is not stamped, and an underivable block refuses the compile
  only when consulted. `<PREFIX>_MEASURES` follows the same rule
  (`measures.md`)."
- `match_api.md` 6.3.10¶11: "ASKED" → "CONSULTED (asked by a pcrec reader or
  read by a kit row)". In ¶10's example, `/* nothing asked */` →
  `/* nothing consulted */`. In the `rx_info` member row 28: "`""` when none was
  consulted".
- If Q6 is ruled for the union over attempts, its hunk ("consulted by any
  attempt of the compile") joins whichever commit lands it, with its own abi
  event (it moves F-5's two artifacts' stamps).

#### 3.7.10 What E-1 does not do

- **No kit edit, and no `MF_SITE_ABI` move.** B1 declared the slot, and E-1
  fills it. (`bytes` and `fidelity` must be in B1's declaration, §3.1.)
- **No kit row reads the object.** That begins at B3a, as a trace-only shadow
  that does not set `consulted`, and is routed at B3b.
- **No `run-rarity` payload.** That is B4's.
- **No `ks_stamp`.** That is [KNOW-SRC]'s; §3.7.3a fixes its call site.
- **No render-point move.** That is RP's, its own zero-mover commit.
- **No `req_rate_why` re-source** (F-2, latent).
- **No new caller-observable surface, and no new refusal.**
- **The order with [KNOW-SRC] is free.** If K0-K3 land first, E-1's
  `pcrec_find_offer` reads the record through `ksrc`'s analysis kind. If E-1
  lands first, K-steps migrate it at zero movers like the rest of the loader
  (`measure_sets.md` §9.7).

## 4. The kit's job: a chain of simple searches `[r4 R3]`

### 4.1 The ruling (D161 add. 5), quoted

> "essentially we are asking memfn to come up with a chain of 1-2 simple
> searches. 1 for a good header span, 2 for a good second span which then
> searches for the poorer first span. we could do 3+ chains if we provided
> 'fallback/overshoot to previous span' not just start of function. its not
> doing automata. its picking the best tools for various components.
> unbounded is automata and outside its pervue"

How a chain is built, which spans, which positions, which tool, whether to
verify an OPTIONAL span, and whether to search at all are the kit's (D161,
D161 add. 6). The contract states only what the chain reads and owes:

- **What it reads.** The spans, their intervals, and (under `spans_seq` =
  SEQ) every pairwise distance's tight hull (§2.3). The analysis object
  (§3).
- **What it owes.** The stream's four obligations (§2.4) and totality: every
  site renders (D162 ruling 2), including when no link pays.
- **Storage** belongs to the SITE, not to a link (§7, storage).

### 4.2 The 3+-link extension

The one extra fact Frank named, each span's distance to the PREVIOUS span
rather than only to the origin, is already delivered for every pair by the
sequence rule (§2.3). So a 3+-link chain needs NO new site field. How such a
chain is built and checked is the kit's. **Trigger (D77):** a real pattern
whose best 2-chain loses to a measured 3-chain twin. wingame §2.1 found 18 of
327 patterns with two or more bounded spans.

### 4.3 [KIT-VERIFY]'s two directions

`[rev3, D161 add. 10]` Both directions apply only to spans whose `byte_form` is
EXACT (§2.2). A SUPERSET span is a filter only.

**(1) pcrec → kit, "verify span k".** This is `need = REQUIRED` on span k
(§2.4 obligation 4). It names no method. pcrec marks a span REQUIRED where its
consumer would otherwise re-test it. Everything else stays OPTIONAL, so the
kit keeps the freedom to skip a dense span.

**(2) kit → pcrec, PROVEN FACTS** `[D161.8]`.

- **What it carries.** `mf_result.proven`: for each span `k`, a bitmask of
  that span's positions that hold at EVERY candidate the site yields. It is
  reported through `mf_defined` (STATIC, known at define time).
  - It is defined only for spans whose offset from the candidate is FIXED
    (`overshoot` 0; span 0 always is). For any other span the mask is 0 in v1
    (Q2, §12). A span with a runtime position would need a runtime
    `occurrence` out-hook: specified as a possibility here, not built.
  - REQUIRED spans' positions hold by obligation 4, so they are always in the
    mask; the mask's information is which OPTIONAL positions also hold.
  - The positions per span are bounded by a shape bound `MF_MAX_SPAN_POS`,
    derived from `PCREC_MAX_REQ_RUN_SCAN` (32) and asserted where pcrec
    builds a span, on `MF_RANK_MAX`'s precedent.
- **Layer invariance** (the floor rule's condition). The proof is the kit's
  statement for the SITE REQUEST (the site fields and its analysis object). It
  is the SAME under `-fno-memfn-simd`, `-fmemfn-simd` at every level, and every
  `--memfn=` deny: a form that does not test a proven position as part of its
  scan tests it anyway (the kit can test a span in any form). So pcrec's bytes,
  which depend on the proof, do not depend on the layer, and SIMD-on stays
  SIMD-off plus guarded text (D155 Q-R9-6, C18, RQ-3).
- **Exactness.** The kit must never over-claim. Under-claiming is always
  correct, and the claim it makes is the same in every layer.
- **How pcrec consumes it** (T-PROOF, §9). Frank's `foobar` example, with the
  sub-problem `foobar`:
  - the kit proves `fo`: pcrec either asks a span test from the kit for the
    rest (a VERIFY site over the unproven positions at the candidate) or
    starts its own engine past the proof (the DFA at `δ*(s0, "fo")` at
    `c + 2`), under the conditions below;
  - the kit proves `foobar`: when nothing else remains to check (no head
    before span 0, no tail after the site, no context predicate unproven, no
    capture asked beyond the whole match, the sub-problem is exactly the
    proven fixed string), pcrec knows the pattern matched at `(c, c + 6)` and
    stops. The stream is ascending and complete, so the first candidate is
    the leftmost match.
- **Consumption conditions** `[r4 E4]` (kept by D161 add. 8, pcrec-side):
  - **DFA rows**: only on a machine whose state after the proven bytes is a
    compile-time constant: the unseeded PLAIN view. A seeded or context-viewed
    machine (`\b`, `(?m)^`, `\G`, a lookbehind reading before the candidate)
    has a start state that depends on bytes before `c` (`emit_dfa.c:12398-12410`
    at the review's commit), so the row declines.
  - **VM row**: enters past leading instructions only where those
    instructions ARE the proven literal tests, open no capture group, skip no
    interleaved assertion, and change no meter (no step or WORK charge the
    unskipped path would make, D158).
  - **Report row**: only under the "nothing else remains" conjunction above.
  - Anything else: the proof is ignored, and the code is still correct.
- **Checks.**
  - **C-PROOF (layer invariance):** a test build renders every corpus site
    under SIMD off, every live SIMD level and every `--memfn=` deny, and
    compares `proven`; any difference fails. Its sabotage row: a proof bit set
    only by a SIMD row.
  - **G2:** for every generated site and subject, at every candidate, every
    proven position holds (the byte-loop oracle). This is a check on the
    kit's claim, not a statement of its method.
  - **pcrec's trace build** re-tests every proven position it consumes, at
    run time.
  - **A sabotage row:** a form that sets a proof bit it does not test.
- **Events.** `mf_result.proven` is a layout change (an `MF_SITE_ABI` bump)
  with no byte moved. pcrec's first CONSUMER of it moves bytes: a pcrec abi
  event plus a deny of its own (`-fno-kit-proof`, PROPOSED). Not built until
  [KIT-VERIFY]'s trigger, a measured consumer re-read cost on real cells.

**The R2 record** (review r4 R2, REJECTED by D161 add. 8). The panel argued
that `proven` makes pcrec's bytes depend on the kit's method (varying with
`-fmemfn-simd` and `--memfn=` denies, which would break C18/RQ-3 neutrality)
and that it is redundant because a REQUIRED span is proven by definition. It
proposed deleting direction (2). Frank's ruling:

> "the simd on/off difference isn't true. memfn can still test spans. also,
> even if it returned different responses, its still at compile time- the
> pcrec side would then emit the code to handle it. for foobar memfn could
> return only "fo" proven or "foobar" proven. if the first one, then pcrec
> would ask for a span test from memfn for the whole span or simply launch
> into a dfa or whatever. if memfn returns "foobar" as proven, pcrec can know
> the pattern is matched and stop".

The design follows from it: the proof is layer-invariant BY CONTRACT (the
kit tests a proven span in any form), checked by C-PROOF; it is not redundant
with REQUIRED, because it reports OPTIONAL positions the kit chose to prove
and lets pcrec skip work (or the whole engine) without asking for every span.
Q12.2's leaning (fixed offsets only) stands.

## 5. The pcrec-side producer

### 5.1 Today's derivations, read from `src/` (main `f3569b161`)

| derivation | function (file:line) | computes | becomes |
|---|---|---|---|
| necessary set + per-member max offset | `pcrec_req_walk` → `RbSet` (`src/facts/req.c:638`); facts `req_set`, `req_set_maxoff` | bytes every match contains; each member's max offset | one-position hull spans `{b}`; the producer adds `omin` |
| the necessary run + its max offset | `pcrec_req_walk` → `RbRun` (`req.c:638`); `req_whole_run`, `whole_maxoff` | the most informative contiguous run | a multi-position hull span; `omin` added |
| run window | `pcrec_req_window` (`req.c:667`) via `pcrec_find_run_scan_index` / `pcrec_find_run_window_start` (`src/core/findings.c`) | the scanned member and a truncation to ≤ 8 bytes, priced by the prior | a DECISION; moves to the kit |
| required byte | `pcrec_req_pick` (`req.c:709`) via `pcrec_find_set_pick` | which set member the `memchr` tests | DECISION → the kit |
| landmark K | `pcrec_fact_req_landmark_maxoff` (`req.c`, [REQ-HANDOFF-L1]) | the run window's K, else the req byte member's | `h_max`, the bounded head before span 0 (pcrec's, §2.1); a family member (§5.6) |
| set-leads | `req_set_leads_applies` (`src/gen/emit_dfa.c:7608`) | whether the set's pick leads the run | DECISION → the kit |
| landmark admission | `req_landmark_admits` (`emit_dfa.c:7810`) | re-entered handoff vs the start-byte row, priced by the prior | DECISION → the kit |
| G1 | `req_byte_dominated_by` (`emit_dfa.c:7554`) | whether the DFA prefilter makes the pre-check redundant | DECISION → the kit, once the PF and PRE sites are one site |
| k-set walk | `pcrec_kset_walk` (`src/facts/kset.c:226`, E3) | per fixed offset, the UNION over paths of the byte set every match carries | **stays its own fact** `[r4 E2]` (a family member); it feeds the offset-pinned union span the offset-skip site sends today, and C-SP1 |
| offset-k selection | `pcrec_prefix_ksets` / `model_cost` (`src/opt/prefix_k.c`) | which offsets to scan/verify | DECISION → the kit (D147 add. 4's M5 planner move) |
| run pin | `pcrec_run_pin` (`kset.c:298`) | the fixed offset at which the k-set spells the run window | a family member; a hull span with `overshoot` 0 where the run is on every path; its PICK goes to the kit |
| start set | `pcrec_start_set` (`src/facts/startset.c:141`, E2) | a superset of the first consumed byte, a UNION over paths | **stays its own fact** `[r4 E2]` (DFA hat, route); sent as its own one-position site (PF FIND), not inside a sequenced multi-span site (§8.1 iii) |
| widths | `pcrec_width_walk` (`kset.c:335`); `pcrec_minw`/`pcrec_cwmax` (`src/opt/mrl.c`) | byte width intervals | the per-item widths the prefix sums add (§5.2) |
| run rank | `pcrec_find_run_rank` (`findings.c`) → `ofs_pred_rank` (`emit_dfa.c:1181`) | RQ-2's ranking | `ofs_pred_rank` RETIRES at S3; `pcrec_find_run_rank` stays as the shadow's oracle until S4 (§6) |
| scan plan sent | `mf_pred.plan_hint`/`plan_pos` (`emit_dfa.c:1210-1228`) | pcrec's model's scan pick | RETIRES at S4 (kit arms read it) |

### 5.2 The producer

- **What.** One new CORE fact, `span_facts` (E2, on the lowered tree, so it
  reads the encoding, `-i` and `--ucp` by construction). Proposed owner
  `src/facts/spans.c`; no prior and no option read. It is a MEMBER of the
  position-pin fact family (§5.6), not a parallel producer `[r4 E2]`.
- **Scope (narrowed).** It produces HULL spans only: spans every path of the
  sub-problem carries. A union over paths at a fixed offset (`a?bcd`'s k-set
  `{a,b},{b,c},{c,d}`; `a*bc`'s start set) is NOT a hull span, and the
  producer does not claim it; those stay `start_set` and the k-set.
- **The walk** generalizes `rb_walk`'s per-subtree accumulators (head and
  tail runs to JOIN, `RbRun.off`) in two ways:
  - each subtree carries its spans as `(classes, omin, omax)`;
  - an alternation contributes its branches' common HULL span (the
    `rn_common_head/tail` rule, cubes at most `pos_set`).
- **The prefix-sum obligation** `[r4 E6]`. `omin_k`/`omax_k` are the sums of
  the minimum/maximum byte widths of the items before span k along the one
  flattened sequence the segment follows. They are NOT taken from a subtree's
  `maxw` (`rn_tail_off`'s shape) or from `pcrec_minw` applied to a prefix
  subtree, both of which can under- or over-estimate per span and break the
  tight hull (§2.3).
- **Output.** A list of SEGMENTS. A segment is the maximal stretch between
  unbounded items (an unbounded repeat or gap, a backreference, a call, a
  variable); it is the array of EVERY span whose distance to the segment's
  origin is bounded (D161 add. 9). The producer selects none of them: which
  to search is the kit's. Each segment holds:
  - all of its spans, sequential by construction (`spans_seq` = SEQ), with
    offsets from its first span (the origin);
  - its head: the width `[h_min, h_max]` of the bounded part before its first
    span (0 for a fixed prefix), pcrec's own.

  The output also holds the PRESENCE spans: necessary sets and runs whose
  offset is unbounded, as `req_set`/`req_whole_run` have today.
- **The declines** are `req.c`'s, each for its stated reason: a lookaround's
  body is never descended; min-0 repeats do not join; a repeat's head and
  tail never cross an iteration.

### 5.3 Its controls (none shares the producer's source)

| control | expectation from | checks |
|---|---|---|
| C-SP1 prefix classes | `pcrec_kset_walk` (an NFA walk, E3) | where segment 0 has a hull span at a fixed offset from the match start (head 0) and the k-set's position is fixed, the hull class ⊆ the k-set's class, with equality where the k-set position is on one path. **Non-vacuity** `[r4 E2]`: a literal floor on the number of compared positions (measured at build, K35), and a reported (not failed) count of k-set positions the producer has no span for: the union population, unlock (b)'s |
| C-SP2 first byte | `pcrec_start_set` | a head-0 segment's offset-0 class ⊆ start_set, with equality where no assertion precedes it and the start set is single-path. **Non-vacuity**: a floor on the number of artifacts with a head-0 span |
| C-SP3 run / set | `req_whole_run`, `req_set`, `*_maxoff` | the most informative span equals the whole run; for each set member `b`, `req_set_maxoff[b]` equals the MIN of `omax` over the spans that carry `b` `[r4 E8]` (`req_set_maxoff` is a min across factors). Until those facts retire into the producer, one reader per commit |
| C-SP4 pairwise distance | a direct walk of the items between two spans (wingame `spans.rel_from_items`, 152/152) | every real distance lies inside the sequence rule's tight hull, with ends reached. **Plants**: an `omin` under-estimate on one span (a per-span `pcrec_minw`), and a subtree-`maxw` `omax`; both must fire |
| C-SP5 soundness | libpcre2 10.46 answers | every match's bytes lie in each span's class at an offset inside `[omin, omax]`, over the corpus's `m` cells, with a planted off-by-one control |

**K35 (who counts).** A floor on the number of artifacts carrying a multi-span
segment, read off a stamp-free census. The trigger population is wingame §2.1's
18 of 327; the floor stays a measured literal.

### 5.4 Which ORIGIN pcrec hands the kit: T-CUT (first match)

| row | predicate | origin; sends ALL spans bounded to it | FINISH | deny (D46) `[r4 R10]` |
|---|---|---|---|---|
| `anchored` | `start_anchor` is BOT/GSTART | no window site | the attempt at the anchor | none (structural: nothing to choose) |
| `rev-inner` | [ENG-TACTICS]'s own gates G1-G4 admit an inner segment | origin = that segment's first span; all its bounded spans | RECOVER reverse walk, then forward. pcrec's | its own, filed with [ENG-TACTICS] (`-fno-rev-inner`, PROPOSED) |
| `segment-0` | segment 0 has a span | origin = segment 0's first span; all its bounded spans | from `c` (head 0) or from `max(search_from, c - h_max)` | the span SOURCES' existing denies (`-fno-start-set`, `-fno-offset-skip`, `-fno-run-prefilter`, `-fno-req-handoff`) remove their spans; the row is denied when every source is |
| `none` | always | nothing | the attempt loop / every byte | none (total) |

- **The table chooses the origin and nothing else** (D161 add. 9): it never
  selects among the spans bounded to that origin. **The table holds no prior.**
  `rev-inner` sits above `segment-0` only where
  its own admission passes. Frank's `a.*aaa.{2,5}zxq` is that row's case. Q1
  (§12) asks whether that is enough.
- **One site per segment.** Today segment 0's facts reach the kit as several
  sites chosen by several rows (the PF FIND, the run-pinned offset-skip, the
  K82/L1 handoff gate, set-leads). Under this contract the HULL spans are ONE
  window site carrying all of them. The offset-pinned union span (start set, k-set) stays its own
  single-span site until unlock (b).

### 5.4a Presence: SUPERSEDED as a separate site; T-WITHHOLD is what stays pcrec's `[rev3 C-6]`

Revision 2's T-PRES (`dominated` → `presence` → `none`) sent presence as its OWN
site beside the window site. D161 add. 14's clarification makes presence a span
class of the ONE request (§2.2), so:
- **`dominated` is the kit's.** It is r17b′'s row P2 (G1's question: are the
  presence span's bytes already tested by the scan), ported at B3a under the
  shadow comparator and routed at B3b.
- **`presence` stops being a site.** Every necessary-set member and the whole
  run are PRESENCE spans of the window site, unpicked (PR-5). The pick is the
  kit's.
- **What remains pcrec's is the sub-problem choice**: whether a presence span
  is SENT at all. That is one table:

**T-WITHHOLD (first match; D161 add. 4, Q-WR-4):**

| row | predicate | presence spans sent | deny |
|---|---|---|---|
| `one-attempt` | G2's linear one-attempt VM route (`req_route_one_attempt`) | none (withheld; today's text keeps its own pre-check decision) | none (structural) |
| `locate-whole` | LOCATE `whole` (the body decides presence) | none (withheld) | none (structural) |
| `asked` | today's asking rule holds: `req_set` is asked only where today asks (Q-WR-12, the `--emit-facts` `used` column) | every necessary-set member and the whole run, unpicked, each with its `need` (§2.3) | the sources' own (`-fno-req-byte`, `-fno-req-run`) remove their spans |
| `none` | always | none | none |

`a.*zxq` sends segment 0 (`a`) AND the `zxq` presence span in ONE site.
reqpos_2b's measured win (1.46 of 10.284) is the kit's to keep: its default rows
port today's pre-check (D1/P-rows, zero movers through B3b).

### 5.5 What stays pcrec's: the unbounded cuts

| cut | row |
|---|---|
| an unbounded head before the sent segment (`a.*` in Frank's example) | RECOVER `reverse-pass` / `landing` / `end-minus-width` |
| a BOUNDED head before span 0 (`h_max`, the K82 handoff's `c - K`) | FINISH's scan start (§2.1) |
| an end-pinned pattern | LOCATE `rev-end` |
| a landmark behind an unbounded gap | `rev-inner` ([ENG-TACTICS], filed) |
| no span at all | the attempt loop; the DFA stepping every byte |
| the context edge (`(?m)^` at `search_from`/0) | pcrec's edge attempt (§2.4) |
| a backreference's relaxed language | `locate_finish.md` §4.5 (filed) |
| the VM hybrid's retry policy (R4 `cand_rs_dense_applies`) | RETRY, the [ADAPTIVE-ARM] family (chunk 5) |
| unbounded-offset presence `[rev3]` | whether a PRESENCE span is sent is pcrec's (T-WITHHOLD); its pick and form are the kit's |

### 5.6 The position-pin fact family `[r4 E2]`

`span_facts` joins a family that answers one question, "which bytes or
anchors are pinned at which positions of every match", today in six members:

| member | owner | states |
|---|---|---|
| `start_set` | `src/facts/startset.c` | the union over paths at offset 0 |
| k-set | `src/facts/kset.c` (`pcrec_kset_walk`) | the union over paths at each fixed offset of the prefix |
| `run_pin` | `kset.c` (`pcrec_run_pin`) | the fixed offset of the run window inside the k-set |
| `end_pin` / `end_window` | `src/facts/endwin.c` | the whole-pattern end pins |
| compound's split facts (`pin_split`'s per-path has/must) | `compound.md` §B | the per-path anchor classes |
| landmark K | `req.c` | the max offset of the landmark from the attempt start |
| `span_facts` (new) | `src/facts/spans.c` | the hull spans with `[omin, omax]` from their segment's first span |

- **The unification is already proposed** in `match_split_pinonly.md` §4.3 /
  §9 U3 (the four pin members as projections of `pin_split`). `compound.md`
  superseded that note and does not re-file it; its own U3 is the public
  [EMIT-ENTRIES] request. This note carries the proposal forward and widens it
  to the six members above: ONE position-pin record per pattern, with each
  member a projection. **Trigger:** U3's own (4a landed, plus a reader that
  gains from the stronger facts) or S4's offset-k move, whichever first.
- **Until then** `span_facts` is specified AS a member: same tree level
  (lowered), same epoch, its CONTROLS are its siblings (§5.3), and no member
  re-derives another's question.

## 6. The retirement sequence

The rule (D162 add. 3 refinement): the frequency kind lands first, the kit's
own ranking second, the retirement third.

| step | what | movers | events |
|---|---|---|---|
| **S1** frequency kind = **main's E-1** `[rev3]` (§3.7) | the kit's B1 declares `mf_analysis` and its slot on `mf_art_begin` (NULL-tolerant); E-1, after B2, builds the object EAGERLY per attempt from `Job.find` through `find_queries[]` and fills that slot with no kit edit. The offer does not mark the query asked and never refuses (§3.7.1) | **0** in every arm, refusals included (CONSULTED, RULED D167 add. 2; §3.7.3, §3.7.4a) | no pcrec abi event, no `MF_SITE_ABI` move at E-1 (B1 took it, with `bytes`/`fidelity`), no D80 hunk; census = G1-E1 (§3.7.7) |
| **S2** kit ranking | the kit derives each RUN term's position order from `byte-rate` in its memo (§3.5), applying the D126 Q4 per-question NONE answers under `prior-none`. IMPLEMENT beside `rank_*` with a SHADOW comparator: the kit's order equals `pcrec_find_run_rank`'s for every site of every corpus compile, at `-e byte` and `-e utf8`. Then REPLACE: `vrun`'s KB reads the kit's order. `[rev3]` From REPLACE, `vrun` is a kit row that reads `byte-rate`, so the kit's per-kind `consulted` (§3.3 rule 8) is owed in that commit, unless B3b has already delivered it | 0 (same order, proven by the shadow); the stamp is 0-mover while pcrec still fills `rank_*` (it asks) | kit-only; no `MF_SITE_ABI` move; no pcrec abi event |
| **S3** retirement | see the file list below. `[rev3 C-11]` `mf_site.consumer` is REPLACED by `site_kind` (stated from B2, Q-WR-8), not dropped | 0, including the stamp: once pcrec stops calling `pcrec_find_run_rank` on the default compile, the kit's `consulted` must carry `byte-rate` wherever that call was the only asker (the deny arms; §3.7.4). G1 includes those arms | ONE `MF_SITE_ABI` bump (layout); no pcrec abi event; D80: none (internal) |
| **S4** the picks | `plan_hint`/`plan_pos` and the prior-reading decisions of §5.1 move into the kit with R-18's multi-span site. Each is implement-then-replace at zero movers, then its own form event. **The shadow retires here** `[r4 R5]`: with the picks moved, both NONE-rule spellings live in the kit, and `pcrec_find_run_rank` (plus its debug dump) is deleted | per form event | each a pcrec abi event when bytes move, with its own `--memfn=` deny. Stamps that report a pick (`REQ_BYTE`, `REQ_RUN`, `DFA_PREFILTER`'s offset form) become kit-attributed; their readers found by grep |

**Why the shadow lives to S4** `[r4 R5]`. Until S4, pcrec's own picks still
read the prior with D126 Q4's NONE rules, and from S2 the kit spells the same
rules for its ranking. Two spellings with nothing comparing them is R13's
shape. So S3 deletes the FIELDS and their filler but keeps
`pcrec_find_run_rank` reached only by the shadow comparator, which keeps
comparing the kit's order against it on every corpus compile until S4 moves
the picks.

**S3's file list** `[r4 R6]`, derived by grep at `76067df80` for `rank_n`,
`rank_pos`, `rank_ppm`, `MF_RANK_MAX`, `ppm_`, `cand_ppm`, `MF_PPM_FULL` and
the `consumer` setters; re-derived by the same grep at S3:

- `memfn/include/memfn.h` (the fields, `MF_RANK_MAX` and its
  `_Static_assert`, `MF_PPM_FULL`, `mf_site.consumer`);
- `memfn/src/compose.c` (the rank checks and the `consumer` range check),
  `memfn/src/vrun.c` (KB re-pointed at S2), `memfn/src/CLAUDE.md`;
- `memfn/tests/g2/g2_gen.c` and `memfn/tests/g2/g2_simd_gen.c` (the
  `consumer` mutator and out-of-enum case, the `ppm_*` and rank fields):
  **D27-BLINDED generators, so a BLINDED LANE (a cell, `scripts/mk_d27_cell.sh`)
  edits them**, from a goal statement of the retirement, never from this
  note's sources; `memfn/tests/run_g2_simd.py`;
- `tests/memfn/arm_fixtures.c` (`consumer`, `ppm_*`);
- `src/gen/memfn_sites.c` (two `consumer` setters, the `ppm_*` fills; its rank
  debug dump stays with the shadow until S4), `src/gen/emit_dfa.c`
  (`ofs_pred_rank`, three `consumer` setters, the `ppm_*` fills),
  `src/gen/emit_vm.c` (one `consumer` setter) — six `consumer` setters in
  `src/` in all; `src/core/internal.h` (one `ppm` declaration);
  `src/gen/CLAUDE.md`;
- `tests/memfn/run_rank.sh`, `tests/memfn/rank_check.py` and the Makefile's
  `test-memfn-rank` (re-aimed: the kit's order against its independent brute
  force, plus the shadow);
- sabotage rows S732-S737 (RQ-2), S750-S752, S754, S794 (vrun KB) — re-aimed or
  retired by `scripts/sabotage_anchors.py --step` over the edit set;
- `plan_hint`/`plan_pos` are NOT in S3: kit arms READ them (`vrun.c`,
  `precheck.c`, `ofsskip.c`, `compose.c`). They retire at S4.
- `[rev3 C-11]` the six `consumer` setters are deleted only because each
  builder already states `site_kind` (from B2). S3's grep checks that every
  builder that set `consumer` sets `site_kind`, so the fact is REPLACED and not
  lost.

- **Consumer price.** It was never built, so nothing is deleted. The text
  retires: setfind.md §2.2's W9 row is struck (§7); wingame §5.5 item 2 and
  §7's first question are annotated SUPERSEDED by D161 add. 6;
  [PRIOR-COST-UNIFY]'s operation-kind table keeps only its METERING plane.
- **The memo** stays in `mf_art` (§3.5).

## 7. The kit's proposed facts: ratified or rejected

| item | verdict | reason |
|---|---|---|
| STORAGE capability (`decl_point` + `mf_locals`, one handle per site, automatic per-call storage, G-S1/G-S2 invariance, stem `<fn>_pf` with `<stem>__*` reserved) | **RATIFIED** as built at `MF_SITE_ABI` 11 | A host CAPABILITY stated as a fact (D157). Dominance and invariance are checked. One handle per site is what lets a stateful stream (D155 add. 4.1) keep its state across candidates. Cross-call state stays out (chunk 5) |
| window fields W0-W2 (`window_stated`, `move_back`, `overshoot`; `omin` derived) | **RATIFIED**, extended to every span of a multi-span site, measured from span 0's start; span 0 states (0, 0). **Amendment**: `MF_MOVE_UNBOUNDED`/`MF_OVER_UNBOUNDED` change from "reserved for R-18" to PERMANENTLY refused | D161 add. 5. **A kit code change** `[r4 R7]`: `compose.c`'s window check exempts `MF_MOVE_UNBOUNDED` today; it becomes a named refusal at define with a G2 refusal case per sentinel. No layout or byte moves. `MF_SPAN_UNBOUNDED` (the proven range) stays legal (§2.3) |
| W3 (FIND's result is the window's beginning, never below `lo`, non-wrapping) | **RATIFIED** as the stream's next candidate (§2.4) | The stateless FIND is the stream one element at a time |
| W7 (FIND reads `preds` as further spans) | **RATIFIED**, with `spans_seq` (§2.3) | An `MF_SITE_ABI` meaning event (§8.2) |
| the SPAN-INDEX FIELD (setfind's W8: the reply names its span) | **REJECTED** | Every candidate is span 0's start (§2.4), so a span index carries nothing pcrec reads |
| W9 (consumer price) | **REJECTED** | D161 add. 6 |
| W10 (joint survival rate per span) | **MOVED** to the analysis kind `run-rarity` | A joint rate is a distribution fact (D162), present only when measured |
| N5 (shared per-width sub-blocks, stem `pcrec_mfk_`, guards `PCREC_MFK_W8_H` / `_V16_H` / `_V32_H`, no version, keyed by K80) | **RATIFIED** in the rev-2.3 form, plus one corollary | First-wins is correct per width because a sub-block's bytes are a function of its width within one abi; K80's valued guard already rejects a mixed-abi TU. The block is emitted scaffolding: its first appearance (R17-b) and every later byte move are pcrec abi events. **Corollary:** no emitted `<PREFIX>_<suffix>` may have a suffix beginning `mfk_`/`MFK_`, or `-p pcrec` would collide. None does today; a C-check over emitter strings holds it |
| N6 (refuse a prefix that, case-folded, is `pcrec_mfk` or begins `pcrec_mfk_`) | **RATIFIED** as built on `lane/r17b` | One check serves `-p`, a `.rxt` target's prefix and `pcrec_options.prefix`. It refuses inputs only (not an abi event), and is caller-observable, so it carries its spec hunks and a sabotage row |

## 8. Flexibility: what changes, and what is an event

### 8.1 The worked examples

**(i) A new analysis kind: `run-rarity`, when [FINDINGS] B4 lands.**
- **pcrec:** a `bigram` block that answers becomes one more `mf_akind`
  (`tag "run-rarity"`, `version 1`, `PRESENT`, `prov MEASURED`). Its payload
  type is added to `memfn.h` beside the list.
- **The stamp gains one entry** (S1's per-kind rule): a pcrec abi event on
  every artifact the bundle answers, with its D80 sentence.
- **No site change.** No existing struct changes. A kit row that ignores the
  tag renders the same bytes.
- **Later.** The day a kit row reads the kind and moves a byte, that is the
  kit's FORM event: its own `--memfn=` deny and a pcrec abi event in the same
  commit.

**(ii) A new site parameter: BRANCH spans.**
- **The case.** `(?:GET|POST) /x`: a span exists only on some paths (wingame
  §2.2, `alt-dropped` on 27/71 capability patterns).
- **pcrec:** the producer emits one span per branch and states `spans_seq` =
  NOT_SEQ, plus a new fact. One candidate is `mf_pred.alt_group`: spans in one
  group are ALTERNATIVES.
- **The kit:** every row's honours allowlist is re-read. A row that does not
  honour `alt_group` declines on a site that states it (K96).
- **Events.** One `MF_SITE_ABI` bump, landed in ONE commit on both sides. A
  pcrec abi event follows only if a byte moves.

**(iii) A derived fact pcrec also uses, against one it only forwards**
`[r4 E2]`.
- **The START SET.** pcrec uses it for its own route and DFA hat
  (`T = S ∩ E*`). It is a union over paths, so it is NOT a hull span and does
  not ride as span 0 of a sequenced multi-span site. It rides as its OWN
  single-span site (today's PF FIND), on every artifact the start table
  selects that row for. D162 add. 3's "send always" binds once a carrier
  exists for every site; for a multi-span site that carrier is unlock (b).
- **Kit-derived: the RUN RANKING.** pcrec computes it only to hand it over
  (and as S2-S4's shadow oracle), so the kit derives it. The same holds for a
  set's mass, a survivor estimate, and the choice of positions.
- **The test.** Does any pcrec DECISION read it? If yes, send it whenever a
  carrier exists. If no, it is the kit's.

### 8.2 Which change is which event

| change | `MF_VOCAB` | `MF_SITE_ABI` | pcrec abi | spec (D80) |
|---|---|---|---|---|
| a new analysis kind no row reads | no | no | YES on every artifact it is offered on (the per-kind stamp entry) | YES (the stamp's grammar gains the kind) |
| a kind's payload shape changes | no | no (its own `version`) | only if a row's bytes move | no |
| the `mf_analysis`/`mf_akind`/`mf_prov` layout changes `[r4 R9]` | no | YES (layout; the list's `list_v` moves only if the list's own shape does) | only if a byte moves | no |
| the per-site analysis slot is filled `[r4 R9]` (the RESERVED per-site fact, §3.3 rule 4; not the object) | no | YES | yes iff a byte moves | no |
| `[rev3]` the object's slot declared on `mf_art_begin` (the kit's B1) | no | YES (with B1's other art fields) | no | no |
| `[rev3]` E-1: pcrec fills the slot (CONSULTED) | no | no | **no** (the offer is not an ask) | no |
| `[rev3]` E-1 under the OFFERED alternative | no | no | YES on the `""` population (0 at default) | YES (§3.7.9) |
| `[rev3]` the kit's per-kind `consulted` joins the stamp (B3b, or S2's REPLACE if earlier) | no | YES (the `mf_art_end` output) | no iff the union of askers is preserved (S997) | YES (findings.md §5's CONSULTED wording) |
| S1: the object first built (revision 2's row; `[rev3]` superseded by the three E-1 rows above) | — | — | — | — |
| a kit row starts reading a kind or a field | no | no | yes iff a byte moves, same commit, own deny | only if a stamp's meaning moves |
| bundle or prior data regenerated | no | no | YES on every artifact that CONSULTS it (`[rev3]`: today, every default compile asks, §3.7.4); also wherever a row's bytes move | no |
| a new site field (fact) | no | YES (layout + meaning) | yes iff a byte moves | no |
| a new reading of an existing field: W7's `preds` on FIND, `need` binding the stream `[r4 R9]` | no | YES (meaning) | yes iff a byte moves | no |
| an enum re-numbered for an UNSTATED zero (`mf_need`) | no | YES (values) | no if every builder states it | no |
| a reserved value made refused (W1/W2 UNBOUNDED) `[r4 R7]` | no | no (no builder states it) | no | no |
| `mf_result.proven` added | no | YES (layout) | no (no consumer) | no |
| pcrec's first proof consumer | no | no | YES, own deny | YES (the deny) |
| a new op, handoff or term kind | YES | YES | yes iff a byte moves | no |
| a field retired (S3) | no | YES (layout) | no (zero movers) | no |
| a refused input (N6) | no | no | no | YES |
| the kit's shared sub-block's bytes | no | no | YES | no |

## 9. First-match tables, and the sibling-of-a-family lens

| table | owner | rows (in order) |
|---|---|---|
| T-CUT: which ORIGIN (§5.4); all bounded spans go with it | pcrec | `anchored` → `rev-inner` → `segment-0` → `none`; deny column per row |
| T-WITHHOLD `[rev3]`: whether presence spans are sent (§5.4a; supersedes T-PRES) | pcrec | `one-attempt` → `locate-whole` → `asked` → `none`; deny column per row |
| T-REPLY: reply type by op (§2.4) | contract | `[rev3]` FIND → STREAM (presence spans included); ALL_PRESENT's VERDICT row DELETED |
| T-NEED: a span's `need` (§4.3) | pcrec | `the FIND definition requires it` (today's single-span terms) → REQUIRED; `pcrec's consumer would re-test it and wants it verified` → REQUIRED; `else` → OPTIONAL. Never left UNSTATED |
| T-PROOF: consuming a proof (§4.3) | pcrec | `report` (the proof covers the whole sub-problem and nothing else remains) → `dfa-exact-prefix` (unseeded PLAIN machine, exact proven bytes) → `vm-literal-prefix` (no capture, no assertion skipped, no meter change) → `verify-rest` (a kit VERIFY site for the unproven positions) → `ignore`; one deny for the family, `-fno-kit-proof` (PROPOSED) |
| T-KIND: one kind's state (§3.2) `[rev3; rev3.1]` | pcrec | `no-shape` → `underivable-arrives` → `underivable` (a block answers, its derivation fails) → `measured` (the block declares a non-authored source) → `authored` (`source authored`, `unmeasured` ARRIVES) → `authored-absent` → `prior-none` (nothing answers, `unmeasured` ARRIVES) → `absent`. No row names a kind |
| `find_queries[]` `[rev3; rev3.1 m1]`: the query vocabulary's one home, and the kinds the object lists (§3.2) | pcrec | one row per [FINDINGS] query: tag, payload version, `unmeasured`; `find_derivs[]` indexes it |

T-MEMO is no longer a table `[r4 R10]`: its one row was a trigger. §3.5 holds
it as a placement with that trigger.

**Families this touches (the sibling-of-a-family lens):**

1. **The prior-cost family** ([PRIOR-COST-UNIFY], 10 members derived by call
   graph). This note splits it three ways: the window choices go to the kit
   (§5.1, §6 S4); the RETRY arm goes to [ADAPTIVE-ARM] (chunk 5); the metering
   kinds go to [EFFORT-BUDGET] (chunk 6). No member is left as a lone
   pcrec-side reader of the prior that chooses among spans.
2. **The start table's site-building rows.** PF FIND, `offset-set`,
   `run-pinned`, the handoff gate, `set-leads` and the req pre-check each
   build a kit site from one row of `cand_rows[]`. Under T-CUT and
   T-WITHHOLD `[rev3]` they become one window site per segment: hull spans plus
   the PRESENCE spans T-WITHHOLD sends. The union-span site stays separate until
   unlock (b). There is no separate presence site.
3. **"A pick sent as a fact"**: `plan_hint`/`plan_pos`, `rank_*`,
   `cand_ppm`, `ppm_*`, retired by one sequence (§6).
4. **The reverse walks** (RECOVER, `rev-end`, `rev-inner`): pcrec's unbounded
   cuts (§5.5), untouched.
5. **The kit's own row tables** (`pffind`, `precheck`, `fn_rows[]`, `arms`
   under `kit_walk`). A chain is a form of those tables, never a parallel
   planner beside them.
6. **The position-pin fact family** (§5.6), with `span_facts` as its newest
   member and one proposed unification.
7. **The knowledge-source family** `[rev3]` ([KNOW-SRC], `measure_sets.md` §9):
   the analysis object, measurement sets and [TABLE-JUDGE]'s picks. The
   SIBLING-OF-A-FAMILY check, member by member:

   | property | analysis object (this note) | measurement set (`measure_sets.md`) | verdict |
   |---|---|---|---|
   | reaches the kit | `mf_art_begin` slot (§3.7.2; revision 2 had `mf_site.analysis`) | `mf_art_begin` (R-MS1) | **aligned by this revision** |
   | the kit reports back | per-kind `consulted` at `mf_art_end` (§3.3 rule 8) | one `consulted` boolean at `mf_art_end` (R-MS2) | aligned: one bit per knowledge source; the object holds several sources (kinds). U1 (§13) makes them one out-channel shape |
   | the stamp's render point `[rev3.1 M3]` | after `mf_art_end`, through marks (§3.7.3a) | not stated | **aligned by this revision for both**; the sentence is an owed sibling edit to `measure_sets.md` §3.5/§4.2 |
   | stamp honesty against the bytes `[rev3.1 X1]` | C-PERT (§3.7.7) | not stated | the same perturbation shape applies to a measurement set (two sets differing in one row's value); filed for `measure_sets.md`'s next revision beside F-4 |
   | stamp meaning | CONSULTED (§3.7.3; RULED, D167 add. 2) | CONSULTED (§3.5) | **aligned, RULED** |
   | stamp item | `query=bundle:digest` / `query=none` (digest of what was consumed) | `id@rev:values_digest` (stamp-on-load) | different on purpose: a set has an immutable `id@rev` and a bundle has only its name and digest (`measure_sets.md` §3.5's own argument) |
   | provenance | per kind: `authored` / `prior-none` / `measured`, read from the block's own `provenance` stanza, with `bytes` and `fidelity` (§3.2, pending Q5) | per row: `measured` / `fitted` / `derived` / `null`, plus the set's `class` and `tier` | different vocabularies over different contents; both state "how derived" (D162 add. 3, D166), and both now read it from the data's own declaration |
   | evidence rule | rows needing evidence read only `measured` (§3.3 rule 7) | the envelope's safe direction belongs to the reader row (§6.2) | compatible |
   | layer invariance of `consulted` | stated (§3.3 rule 8, C-CONS) | NOT stated (F-4) | a gap in the sibling, filed for its next revision |
   | the stamp builder | `pcrec_find_stamp` today, `ks_stamp` at [KNOW-SRC] | `ks_stamp` | one builder, once [KNOW-SRC] lands; E-1 does not pre-empt it (§3.7.10) |
   | the query vocabulary | ONE home, `find_queries[]` (§3.7.1); F-3 retired at E-1 | the card table, closed (§7.2) | aligned; [KNOW-SRC]'s analysis kind reads `find_queries[]` and does not re-spell it |

## 10. The three standing questions

1. **Measurement regime: RELEVANT, and no number decides this note.**
   `[rev3]` Revision 3 adds one COUNT, not a timing: §3.7.4's stamp census
   (corpus argv stream, three default arms and five deny arms, this tree's
   binary on the Linux dev box). A count of stamp values does not depend on the
   box, compiler or libc. Different data would flip only the OFFERED
   alternative's mover population, not the design of record, which is
   zero-mover by construction. E-1's compile-time cost is unmeasured and
   bounded (§3.7.1). `[rev3.1]` Revision 3.1 adds two more COUNTS and one
   prototype run, same stream, main `2288ad1cb`, Linux dev box: the analysis-axis
   refusal census (§3.7.4a) and C-PERT's prototype (§3.7.7). Both are counts
   of stamp values, refusals and byte equality, so box, compiler and libc do
   not enter; a different corpus would move the floors, which is why they are
   literals measured at landing, not the design. The
   evidence it leans on is counts: wingame's survivors, regions and policy
   flips on the bench's 256 KiB throughput subjects; the R-17 timings in
   setfind §13; reqpos_2b's presence win (§5.4a). No consumer price exists any
   more. Every kit choice remains under its own regime rule (two-tier
   verdicts, D144 add. 4).
2. **Independent control: RELEVANT.**
   - The producer's five controls share no source with it, with non-vacuity
     floors and planted defects (§5.3).
   - The proof is held to C-PROOF's layer-invariance comparison, G2's
     byte-loop oracle and pcrec's trace-build re-test (§4.3).
   - The stream's obligations (COMPLETE, ASCENDING, span-0 starts, REQUIRED)
     are checked by G2 against the byte-loop oracle at every position of every
     generated subject; the edge is checked by pcrec's own differential with
     a `(?m)^` cell at `search_from` 0 and > 0.
   - The memo's order-independence is checked by rendering in two orders.
   - `[rev3]` E-1's checks (§3.7.7). The object's content is checked against a
     hand-written expectation table and digests recomputed in python, not
     against `--list-analysis`, which asks the same `pcrec_find_chain_answer`.
     G1-E1's zero-mover gate needs a DENY arm: the default arms hold no `""`
     artifact, so they cannot see the offer leak into the stamp (K35). The
     `absent` T-KIND row is declared UNREACHED until B4.
   - `[rev3.1]` The refusal set is compared as KEYS across the arm × analysis
     product, with floors on B1's population (§3.7.7 G1-E1).
   - `[rev3.1 X1]` The stamp itself is held to the BYTES by C-PERT, which reads
     neither pcrec's ask record nor the kit's report: the data is perturbed
     and the artifact's own bytes say whether anything read it. Its null
     control (the `-I`/`--analysis default` route moves nothing) and its power
     floor (consulted artifacts that move) keep it from reading green on a
     weak perturbation. C-E1-4 is labelled an AGREEMENT check: it shares the
     memo with what it checks.
   - S2's ranking is held to the shadow until S4, then to an independent
     brute force.
   - K35: a multi-span floor (§5.3). [MECH-REACH]: every sabotage row named
     here (memo order, proof over-claim, proof layer-dependence, sequence-rule
     under-estimate, C-SP1 vacuity) gets a witness that reaches its site.
3. **What moves when data is regenerated: RELEVANT.**
   - **A regeneration of the prior or a bundle moves the `<PREFIX>_FINDINGS`
     digest of every artifact that CONSULTS it** `[rev3]`. Today that is every
     default compile, because every default compile asks (§3.7.4), so in
     practice every default `-e byte` artifact. Each such regeneration is an
     abi event, as findings.md 5¶9 already says. Revision 2's "after S1, every
     artifact" held only under the OFFERED alternative, which is not taken
     (D167 add. 2).
   - The digest in each kind's provenance is the stamp's value, so "which data
     built this artifact" has one answer. `[rev3.1 F-5]` Except across
     attempts: a multi-attempt compile's stamp names only the final attempt's
     consults (Q6).
   - `[rev3.1 M2]` `findings_table.inc` gains the provenance fields; a
     regeneration that changes only a block's `provenance` (its `bytes`,
     `fidelity` or `source`) moves no emitted byte at E-1 (nothing reads the
     fields in pcrec), and from B3a may move a kit selection that reads
     `measured` as evidence, which is then an abi event in that commit.
   - D160's authored utf8 prior turns `-e utf8`'s kind from `prior-none` to
     `authored`, moving every utf8 artifact's stamp. S2's shadow covers
     `-e utf8` explicitly.
   - A proof is a function of the site request, which includes the analysis
     object; a regeneration that changes a proof moves pcrec's bytes, an abi
     event in the same commit.

## 11. The R-18 outline (facts only; main files it) `[rev3 C-7]`

Revision 3 changes this outline in step with the contract (C-7). The ledger
entry R-18 in `memfn/docs/requests.md` (main, single writer) is amended by the
text in Appendix A. That edit is main's to apply.

**R-18: THE WINDOW SEARCH (D161), the general category**

- **Customer.** D161 and add. 1-15; D162 and add. 1-4; chunk 3. It supersedes
  the per-shape interfaces of R-15 (the ASSIGN gate), R-17 (the set FIND) and
  the PF/OFS/PRE sites. Their forms and measurements carry over. R-21 (the one
  window request: single-byte FIND, presence, handoff) is R-18's first
  delivery, built as R17-b′'s B0-B3b.
- **Facts pcrec will state** (this note §2-§3):
  - a site is a bounded sub-problem whose origin is span 0's start. The origin
    is the one thing pcrec chooses (T-CUT). pcrec sends every span bounded to
    that origin, and the kit chooses which to search (D161 add. 9);
  - spans are `mf_pred`s with a CLASS (`BOUNDED`, `CONTEXT`, `PRESENCE`), a
    `byte_form` (EXACT or SUPERSET, D161 add. 10) and a `need` (the effort
    fact, C-14). A BOUNDED span states `move_back`/`overshoot`. A PRESENCE span
    states `omin ≥ 0` from the match start and no `omax`; set members are
    unpicked, with `member_order`. The site states `head_max`;
  - context predicates are not spans to be searched for (D161 add. 7), and the
    edge is pcrec's;
  - `spans_seq` states the sequence rule over BOUNDED spans (tri-state);
  - **presence is a span class of the one request, not a separate site** (D161
    add. 14's clarification; supersedes revision 2's "presence sites carry no
    window");
  - the consumer's `site_kind` (from B2, replacing `consumer` at S3), and
    `body` plus the START hook (R-19);
  - the analysis object, ONCE per art on `mf_art_begin` (§3.7.2; supersedes
    "`mf_site.analysis`"), with `byte-rate` always present and every kind's
    provenance.
- **Obligations on the reply:** ONE stream (COMPLETE, ASCENDING without
  repeats, span-0 starts, REQUIRED spans satisfied) with range-level binding of
  presence (EMPTY = NOMATCH, decided first, one verdict per activation, the K65
  give-up conversions preserved); the unconstrained reply as a range; the
  per-candidate cut as a PERMISSION; totality; and when [KIT-VERIFY] builds, a
  layer-invariant `proven` on EXACT spans only.
- **What the kit reports back:** at `mf_define`, the PROVEN facts (r17b′ §4.5:
  `proven0`, `scan_exists`, `includes`, `pres_kept`). At `mf_art_end`, a
  per-kind `consulted`, layer-invariant (§3.3 rule 8), due by the first routed
  row that reads a kind.
- **Facts pcrec will NOT state:** a consumer price, a span index, a scan
  position (`plan_hint` retires at S4), a ranking (`rank_*` retires at S3),
  per-site rates.
- **Deliverable.** The kit's method is its own. It serves every degenerate site
  at zero SIMD-off movers first. A degenerate site is one BOUNDED span of length
  1, a CONTEXT-only site, or a PRESENCE-only site. It then serves multi-span
  sites behind their own denies, and lands each SIMD-off byte move together with
  pcrec's abi event.
- **Capability pcrec provides:** storage as ratified (§7).
- **Trigger.** R-21's first delivery is built (R17-b′ B0-B3b, D167). The first
  multi-span BOUNDED consumer: the K82/L1 handoff's fused gate as a stream
  (§2.5), cells loglines/ipv6, ipv4, bounded/dotted4; then wingame's
  syslogbase-expanded and the refine witnesses.
- **Sequencing (main's).** E-1 (= S1, §3.7) lands after B2 and before B3a. S2-S3
  may land before the multi-span build. S4 rides it.
- **Sabotage ids.** S871-S880 (R-18's) stay R-18's multi-span rows. R-21's are
  S964-S980. E-1's are proposed at S991-S998 (§3.7.8).

## 12. Questions for Frank (discussion, each with a leaning)

1. **How pcrec picks the sub-problem when an inner segment beats segment 0.**
   ANSWERED by D161 add. 9: pcrec's only choice is the ORIGIN, and the kit
   picks the spans.
   - **The answer.** The origin is segment 0's start, or an inner segment's
     start under the rev-inner gates (G1-G4, where G3 is structural;
     rincensus), where pcrec recovers the head itself with its reverse walk
     (Frank's `a.*aaa.{2,5}zxq`). Given the origin, pcrec sends ALL spans
     whose distance to it is bounded, with the analysis object, and never
     pre-selects among them. The kit chooses which spans to search and how, and
     streams candidate origins (D161 add. 7). So pcrec prices no span, and the
     consumer-price problem (D161 add. 6) does not return one level up.
   - **What stays.** The unbounded-offset presence span (`zxq` beside segment
     0 in `a.*zxq`) is still sent, because it has no bounded distance to the
     origin. `[rev3]` It is now a PRESENCE span of the same site (§2.2,
     T-WITHHOLD), not its own site. "Send both origins and let the kit say
     which it can search" stays rejected: it is a capability query, the K0
     shape D146 retired.
2. **Proven facts only at fixed offsets (v1).** A leaning, not a question.
   - **The leaning.** Report proofs only for spans whose offset from the
     candidate is fixed (`overshoot` 0). Leave the runtime `occurrence`
     out-hook (which would cover `overshoot` > 0) until a VM per-start
     consumer is measured to re-read proven bytes.
   - **The alternative.** Specify the occurrence now: a runtime write per
     candidate on every site that states it, for a consumer nobody has timed.

(Revision 1's Q3, "`U` now or later", was deleted: D161 add. 7 removed `U`. The
number is reused below.)

3. **`[rev3]` What does `<PREFIX>_FINDINGS` mean once the kit receives the
   analysis: what was CONSULTED, or what was OFFERED?** **RULED: CONSULTED**
   (Frank, "q3: consulted", D167 add. 2), for `_FINDINGS` and `_MEASURES`
   alike. The design of record is §3.7.3. Revision 3's argument and the OFFERED
   build text are in that revision's git text (§3.7.5). The panel r4 then
   showed the ruling's "E-1 is zero-mover in every arm" needed a non-raising
   offer to be true (B1); revision 3.1 supplies it, so the ruling's stated
   consequences hold as ruled.
4. **`[rev3]` When does `--emit-facts`' `rate:builtin-prior` stop mislabelling
   a measured bundle (F-2)?** This is the manager's unless Frank wants it.
   - **The problem.** The token is written whenever ANY block answered, but the
     spec defines it as the shipped prior. `[rev3.1 m4]` It is LATENT: no CLI
     path lists facts under a non-default analysis today (`--analysis` with
     `--emit-facts` is refused).
   - **The forces.** E-1 creates the provenance that would name it correctly.
     Re-sourcing the token is a caller-visible listing change (a
     `facts_listing.md` hunk), but it becomes visible only when some path can
     list facts under `--analysis`.
   - **The leaning.** Trigger it on that path (the first path that lists facts
     under a non-default analysis), not on B3b alone. Spell it
     `rate:<provenance>` (`rate:authored`, `rate:measured(<bundle>)`,
     `rate:none(<enc>)->rightmost`). Until then, correct the spec sentence to
     say what the code does.
5. **`[rev3.1 M2]` May a kind's provenance be read from the answering block's
   own declared `provenance` stanza?**
   - **The problem.** D162 add. 3's manager reading names two provenances,
     "pcrec's prior vs measured from a [FINDINGS] bundle, and the bundle's
     identity when measured". Revision 3 implemented that literally, by the
     answering LINK: the store's `default` is the prior, and any other answer
     is measured. The panel showed two things. A byte-identical user copy of
     `default.rxt` named by `-I` then reads "measured", so a row that wants
     EVIDENCE would accept the authored prior as evidence (reproduced on main,
     `b1_witness.out`). And every data block already DECLARES how it was
     derived: a schema-validated `provenance` stanza with `source` (`authored`
     or an exemplar's name), `bytes` (required iff not authored) and an
     optional `fidelity` from a closed vocabulary.
   - **The forces.** Frank's ruling text is "do mark facts with how it was
     derived". The block's own stanza IS how it was derived, written by the
     person or tool that derived it and checked by the schema. Reading it is
     the general mechanism; a link test is a parallel one that can disagree
     with it. It also gives the evidence strength (`bytes`) for free, at no
     extra `MF_SITE_ABI` event while the layout is new. What changes: a user's
     bundle that declares `source authored` (the test fixtures `l1`/`l1none`
     do) becomes AUTHORED, not MEASURED. It is a guess by a person, and a row
     that wants evidence will no longer treat it as evidence. That is a change
     to the manager's reading of D162 add. 3, which only said "at least" two
     values, not to Frank's text. The cost: one more pre-parse field set in
     `findgen` and the runtime copy, and trusting a declared `source`. A
     mislabelled exemplar would read as measured, but the schema already ties
     `bytes` and `sha256` to that claim, which a link test does not check at
     all.
   - **The other way.** Keep link identity, and treat a user's authored
     block as measured. Then §3.6's evidence-strength fact must still be
     added, and the byte-identical-copy case must be explained away (a user
     who names `-I DIR/default.rxt` is asserting the data is theirs).
   - **The leaning.** Content-sourced, with link identity kept as a
     cross-check (C-E1-1: an answer through the store's terminal must read
     AUTHORED). §3.2 is written that way, marked pending this ruling. Link
     identity would change §3.2's `measured`/`authored` predicates and
     S992/S1012's cells, and nothing else.
6. **`[rev3.1 F-5]` What does the stamp record when a compile takes more than
   one attempt?**
   - **The problem.** `_FINDINGS` reads the FINAL attempt's record, because
     `Job.find` is per attempt. A compile whose earlier attempt consulted the
     byte-rate and whose final attempt did not stamps `""`. Its artifact still
     depends on the earlier read: the retry decision, and the size the
     `RX_VM_PREFILTER_WHY` text quotes, come from the earlier attempt. Two
     corpus artifacts, found by C-PERT's prototype (§3.7.6 F-5).
   - **The forces.** "Which data built this artifact" is the stamp's job, and
     an earlier attempt's read is part of that. The union over the compile's
     attempts answers it: the kinds ANY attempt consulted, with the FINAL
     attempt's bundle and digest (every attempt resolves the same chain, so
     they agree). It moves exactly the multi-attempt artifacts whose earlier
     attempt asked and whose final attempt did not (`""` →
     `byte-rate=…`), which is a pcrec abi event and a match_api/findings
     hunk. Leaving it costs a named exception bucket in C-PERT, and an
     `[ART-MGR]` cache keyed on the stamp would miss a dependence. A narrower
     fix would make the quoted sizes in `_WHY` texts stamp-free (they count
     the earlier attempt's own stamp bytes, which is how the bundle NAME
     leaks), but the ladder's DECISION would still depend on the earlier read.
   - **The leaning.** The union over attempts, landed as its own small abi
     event in the same series as RP (both touch the finishing pass), with
     C-PERT's bucket retired in that commit. Not part of E-1, which stays
     zero-mover.

## 13. Filed facts and unlocks (each with its trigger)

- **The per-site ACTIVATION fact** `[r4 R10]`. setfind §9.2's decline arm
  (D162 add. 1: decline on positive evidence of density WITH a state-losing
  call pattern) needs to know the site's call pattern: whether one search call
  sees many candidates (state carries) or each candidate is a new call
  (find-all under today's API). No slot exists. It would fill D162's reserved
  per-site slot. **Trigger:** the decline arm is built (a measured dense cell
  with a state-losing call pattern, D162 add. 1).
- ~~**The EVIDENCE-STRENGTH fact**~~ `[rev3.1 M2]`: BUILT (`mf_prov.bytes`,
  `fidelity`, §3.1). Its remaining half, a SAMPLE count for a kind whose
  exemplar is not a byte stream, stays filed (§3.6).
- **U1, one kit out-channel for the knowledge-source family** `[rev3.1, panel
  r4]`. One `mf_art_end` record of `consulted` keyed by (knowledge source,
  item), so `ks_stamp` reads one shape for the analysis object's per-kind bits
  and the measurement set's boolean. **Trigger:** the second kit output
  landing, whichever of B3b's per-kind bits and M0's R-MS2 lands second.
- **U2, content-sourced provenance** `[rev3.1, panel r4]`: mostly BUILT by M2
  (the stanza reaches the kit). The rest: `--list-analysis` shows the
  provenance (source, bytes, fidelity) per kind. **Trigger:** B3a, the first
  ported row reading `measured`.
- **U3, one stamp render point** `[rev3.1, panel r4]`: BUILT as RP (§3.7.3a).
  It also lets a future consumed-subset digest (`measure_sets.md` §10.4) be
  computed after every reader.
- **U4, an eager per-attempt object on `Job`** `[rev3.1, panel r4]`: the build
  point is BUILT (M5, §3.7.1). The rest: the same value feeds pcrec's own
  readers through one accessor, and the `byte_rate_*` record fields retire into
  it. **Trigger:** [KNOW-SRC]'s K-steps migrating the loader (§3.7.10).
- **U5, C-PERT for measurement sets** `[rev3.1 X1]`. The same perturbation
  shape (two sets differing in one row's value, same id) checks `_MEASURES`'s
  honesty against the bytes. **Trigger:** M0.
- **(a) End-origin spans**: spans measured back from a match END, for a
  kit-delegated reverse walk. **Trigger:** the first kit-delegated reverse
  walk, or [OPT-ENDWIN-ENC].
- **(b) Offset-pinned union spans with per-group `spans_seq`**: the start set
  and the k-set carried in the SAME site as hull spans, each group sequenced
  within itself. **Trigger:** S4's offset-k move into the kit.
- ~~**(c) Presence as a chain link**~~ `[rev3 C-8]`: STRUCK, and it is now the
  contract. Presence is a span class of the one request (§2.2), and the kit's
  chain may test it first, fuse it, or drop it where OPTIONAL. The trigger
  dissolves.
- **The position-pin family unification** (§5.6). **Trigger:** U3's own, or
  S4's offset-k move.

## 14. What a re-check should attack

1. **The edge rule (§2.4).** Is the edge set exactly `{search_from, 0}`? Look
   at `\G`, a context predicate at an offset other than -1 (none is built;
   say so if one could be), and `lo > search_from` on the stream's later
   calls.
2. **Span 0 as the origin (§2.1).** Does moving the origin from the match
   start to span 0's start lose anything a kit form could use, for a site whose
   head is bounded and narrow (`.?abc`)?
3. **Layer invariance of the proof (§4.3).** Can a form under a `--memfn=`
   deny be unable to test a position another form proves, so that the
   invariance forces a weaker proof everywhere? Is that the right trade?
4. **`dominated` (now the kit's P2, `[rev3]`).** Is it G1's predicate exactly,
   and does it read the window site's spans or the prefilter's language? The
   B3a shadow comparator answers this, pick by pick.
5. **S1's mover population.** ANSWERED `[rev3]` (§3.7.4): every default corpus
   compile already asks, so the `""` population is 0 at default. It exists only
   on deny arms. `[rev3.1]` The refusal population is ANSWERED too (§3.7.4a).
6. `[rev3]` **The offer/ask split (§3.7.1).** Can any path read `byte_rate_have`
   or the payload before an ask, so that the earlier derivation changes its
   answer? `[rev3.1 m6]` `req_rate_why` now reads the accessor's return, and
   C-E1-6 makes "no reader outside `findings.c`" a check rather than a grep.
7. `[rev3]` **The slot choice (§3.7.2).** Is there a site whose kit row would
   need a DIFFERENT analysis from its art's? A compound part is its own
   compile, so no. A future per-site override would be the reserved per-site
   slot, not the object.
8. `[rev3]` **C-CONS.** Can a kit row's knowledge filter (`needs` ∋ E) be
   evaluated only under one layer, so that `consulted` is layer-dependent by
   construction? r17b′'s W64 rows (B6) are the place to look.
9. `[rev3]` **The presence class (§2.2).** Is `omin` from the MATCH start sound
   for every origin the T-CUT table can choose, including `rev-inner`, where
   pcrec recovers the head? r17b′ §4.1 argues it for head-0 and the landmark
   origin only.
10. `[rev3.1]` **The non-raising split (§3.7.1).** Is there a path on which
    the eager offer's status memo is read by an asker of a DIFFERENT encoding
    or chain (none exists per attempt, but check retries and compound parts),
    or a raise reachable from the offer through a callee
    (`pcrec_find_normalize`, the chain walk)?
11. `[rev3.1]` **C-PERT's perturbation (§3.7.7).** Is rank reversal strong
    enough to move every reader that reads the byte-rate? A reader that reads
    only whether ONE byte's rate exceeds a threshold could be blind to a
    reversal that keeps that byte on the same side. The power floor bounds the
    aggregate, not each reader. Is a second perturber (a single-byte spike)
    owed?
12. `[rev3.1]` **The render-point marks (§3.7.3a).** Does any byte-count
    reader measure the artifact between the engine emitter and the finishing
    pass, so that a mark (one placeholder byte) where the stamp line was
    changes a size decision? The kit's own stamp mark already lives there, so
    the class exists; are the knowledge-stamp lines inside a region any
    decision view measures early?
13. `[rev3.1]` **F-5 (§3.7.6, Q6).** Are there multi-attempt shapes other than
    the size-cap retry whose earlier attempt reads the byte-rate (the K53 drop
    ladder, `[PF-DROP]`, `drop-compound`)? The prototype's population found
    two; its arms did not include the lowered-cap variants.

## Appendix A. The R-18 ledger amendment (C-7), for main to apply `[rev3]`

`memfn/docs/requests.md` has one writer, main. This lane does not edit it. The
text below is a dated amendment to append under R-18, replacing nothing above
it (the ledger is append-only in spirit):

> **R-18 amendment (2026-10-16, pcrec manager; window_contract.md revision 3,
> C-7).** Three bullets of R-18 are superseded:
> - "Presence sites carry no window (their own table)" → **presence is a span
>   class of the one window request** (D161 add. 14 and its clarification;
>   R-21). A PRESENCE span states `omin ≥ 0` from the match start, no `omax`,
>   a `need`, and, for a set member, its `member_order`. An EMPTY stream is
>   NOMATCH, decided before the first element, one verdict per activation, and
>   K65's give-up conversions are preserved (contract §2.2, §2.4 obligations
>   5-7).
> - "`mf_site.analysis`: the per-compile analysis object" → **the analysis
>   object is stated ONCE per art, in the `mf_art_begin` slot your B1
>   declares** (contract §3.7.2). From the first commit that routes a row
>   reading a kind (B3b, or S2's REPLACE if earlier), you return a per-kind
>   `consulted` at `mf_art_end`, the same in every layer (contract §3.3 rule
>   8). pcrec ORs it into `<PREFIX>_FINDINGS`.
> - "Serve every degenerate site (one span, length 1) at zero SIMD-off movers
>   first" → **every degenerate site: one BOUNDED span of length 1, a
>   CONTEXT-only site (MLINE), or a PRESENCE-only site**, at zero SIMD-off
>   movers first.
>
> Two facts are added: every span's `byte_form` (EXACT or SUPERSET, D161 add.
> 10; verify and proofs on EXACT only) and the span class enum
> (`UNSTATED`, `BOUNDED`, `CONTEXT`, `PRESENCE`). Main's E-1 fills the
> analysis slot after your B2 merges, with no kit edit. Under the contract's
> CONSULTED stamp rule it moves no byte.
