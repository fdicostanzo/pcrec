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

**Status: PROPOSED, revision 3.** Q1 (§12) is ANSWERED by D161 add. 9; Q2 is a
leaning; Q3-Q4 are new and in discussion form. Q3 (what the `_FINDINGS` stamp
means) decides whether E-1 is an abi event. The R-18 ledger edit (§11, Appendix
A) is main's to apply.

The contract carries FACTS only, never the kit's method (D157). Every
selection below is an ordered first-match table (memory
`pcrec-decisions-as-first-match-tables`). Revision-2 changes are tagged
`[r4 ID]` or `[D161.7]`/`[D161.8]` where they land.

## §R3. What revision 3 changed (input → section, disposition)

| input | where | disposition |
|---|---|---|
| E-1 (r17b′ §3.1 row "(main) E-1"; D167's consequences) | **§3.7 (new)** | The build step, stated in full: the object, where it is built, the slot it fills, the stamp, the census, the readers, the spec hunks, the checks and the sabotage |
| the per-site slot vs the kit's per-`mf_art_begin` slot | §3.1, §3.3 rule 3, §3.7.2 | **The object rides `mf_art_begin`**, not `mf_site.analysis`. One object per art, stated once. Rule 3's same-pointer check and its NULL-mixing refusal dissolve, because nothing can differ. Reasons in §3.7.2 |
| rev 2 open question 5 (S1's mover population) | §3.7.4, §14 item 5 | **MEASURED** (`window_contract_rev3/`). At default flags the population is EMPTY: 0 of 5,336 byte, 0 of 5,364 utf8 and 0 of 5,337 `--engine=vm` corpus artifacts stamp `""` today. Every default compile already asks, by findings §6.4 rule 1. The `""` population is entirely in the deny arms: 1,973 of 5,336 under `-fno-req-byte`, and every artifact under `--engine=vm -fno-req-byte -fno-req-run` |
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
   PRESENT or explicitly ABSENT and carries a PROVENANCE: `prior-authored`,
   `prior-none` or `measured`, plus the bundle identity and the same digest
   the `<PREFIX>_FINDINGS` stamp reports. Every enum has an UNSTATED zero
   `[r4 R4]`. `byte-rate` is always present. Under `-e utf8` today it is
   `prior-none` with no table (§3.2). The kit is encoding-blind (D147 add. 14),
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
   lands first (S1 = main's E-1, §3.7; ZERO-MOVER under this revision's stamp
   rule, an abi event under the OFFERED alternative), then the kit's own ranking,
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
   query vocabulary. `byte-rate` is ALWAYS present: measured, prior-authored or
   prior-none. pcrec hands it to the slot the kit's B1 declares on
   `mf_art_begin`, with no kit edit, after B2 merges.
   - **The stamp.** `<PREFIX>_FINDINGS` keeps meaning CONSULTED, the [KNOW-SRC]
     family's one rule. Building the object is an OFFER, and an offer is not
     an ask. So E-1 moves no byte in any arm: it is not a pcrec abi event and
     not a D80 event.
   - **What the stamp gains later.** The kit's per-kind `consulted` joins the
     stamp at the first commit that ROUTES a kit row reading a kind (B3b). That
     commit carries the findings.md §5 hunk.
   - **The alternative.** Under OFFERED, E-1 is an abi event. Its movers are
     exactly the deny-arm artifacts that stamp `""` today, and at default flags
     there are none (§3.7.4-§3.7.5).

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
               MF_PROV_PRIOR_AUTHORED, MF_PROV_PRIOR_NONE,
               MF_PROV_MEASURED } mf_prov_source;
typedef enum { MF_KIND_UNSTATED = 0,      /* refused at define              */
               MF_KIND_PRESENT, MF_KIND_ABSENT } mf_kind_state;
typedef struct {
    uint8_t     source;     /* mf_prov_source                                  */
    const char *bundle;     /* MEASURED: the answering bundle's name;
                               PRIOR_AUTHORED: "default"; PRIOR_NONE: NULL
                               (stated, checked at build) [rev3]               */
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

**The payload invariant** `[r4 R4]`, checked at define: `payload` is non-NULL
iff `present == MF_KIND_PRESENT` and `prov.source` is `PRIOR_AUTHORED` or
`MEASURED`. So `byte-rate` under `-e utf8` today reads `PRESENT`,
`PRIOR_NONE`, `payload == NULL`, and that combination is stated, not
accidental. An `ABSENT` kind has `source == MF_PROV_UNSTATED` and no payload.

`[rev3]` **The object reaches the kit on `mf_art_begin`**, in the slot the kit's
B1 declares (NULL-tolerant; no kit row reads it before B3a). Revision 2's
`mf_site.analysis` is WITHDRAWN (§3.7.2 gives the reasons). NULL is "none
stated", legal for a stand-alone K3 caller and for every pcrec compile before
E-1 lands.

### 3.2 The kinds table, and provenance `[rev3: one table, an `arrives` column]`

The object is built from ONE pcrec-side table, `find_kinds[]`, whose rows are
the [FINDINGS] query vocabulary (`findings.c`'s derivation table, third column).
Each row has a tag, a payload version (`0` = pcrec carries no payload for the
kind yet), and an `arrives` column. No row names a kind in a predicate.

| tag | payload version | `arrives` | payload |
|---|---|---|---|
| `byte-rate` | 1 | `ALWAYS` (D162 add. 2: the frequency kind always arrives) | `uint32_t ppm[256]`, summing to 1,000,000 (`pcrec_find_normalize`'s rule); NULL under `prior-none` |
| `run-rarity` | 0 until [FINDINGS] B4 lands its shape | `MEASURED-ONLY` (D162 add. 2: other kinds are present only when measured) | none yet; B4's shape |

**T-KIND, one kind's state (first match, the same rows for every kind):**

| row | predicate | `present` | `prov.source` (bundle, digest) |
|---|---|---|---|
| `no-shape` | the row's payload version is 0 | ABSENT | UNSTATED |
| `measured` | a block answers the query along the chain, and the answering LINK is not the store's `default` bundle | PRESENT | MEASURED (the link's bundle, the kind's digest) |
| `prior-authored` | a block answers, and the answering link IS the store's `default` bundle, by identity: its blocks are the store's own, reached as the chain terminal (`PCREC_FIND_STOP_DEFAULT`) or by name from the store (`PCREC_FIND_STOP_STORE`) | PRESENT | PRIOR_AUTHORED (`"default"`, the kind's digest) |
| `prior-none` | nothing answers, and `arrives` is `ALWAYS` | PRESENT | PRIOR_NONE (NULL, 0) |
| `absent` | else | ABSENT | UNSTATED |

- **Provenance by identity, not by name.** A user's `-I DIR/default.rxt` that
  answers is user data, so it is `measured`. A spelling test on the name
  `"default"` would call it the authored prior. Sabotage row P-2 (§3.7.8)
  plants exactly that.
- **Today's cells.** Under `-e byte` with no `--analysis`, `byte-rate` is
  `prior-authored`. Under `-e utf8` with no `--analysis`, it is `prior-none`:
  `default.rxt` declares `serves byte-rate when byte` only. Naming `weblog` or
  `log` makes it `measured` under both encodings (`cpfreq` via `encode-utf8`
  under utf8). `log`'s provenance line says `fidelity synthesized`, so it is
  `measured` from a synthesized corpus. Saying so is the evidence-strength
  fact's job (§3.6), not the source enum's.

- **Why `prior-none` carries no table.** pcrec's own answer with no data is
  per question kind (D126 Q4): MASS is cardinality, PICK ties to its
  reader's rightmost, and COMPARE is false. A uniform table would answer
  COMPARE "true" for every pair, which is a density claim no data supports
  (the "false confidence" of D162 add. 2). So the kind ARRIVES, honouring
  D162 add. 2, and its provenance states that pcrec's prior here is the
  no-information answer. When D160's authored utf8 prior lands, the utf8 kind
  becomes `prior-authored` with a table.
- **Evidence.** A row that needs EVIDENCE (D162 add. 1's decline on positive
  density) reads only `measured` (D162 add. 3). How MUCH evidence is a filed
  fact (§3.6).
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
   from `Job.find`, which is per attempt, when the attempt's art begins
   (`pcrec_memfn_art`, before `mf_art_begin`). It is stated ONCE, on
   `mf_art_begin`. Revision 2's same-pointer check and its NULL-mixing refusal
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
7. **Evidence reads MEASURED only** `[rev3 C-15]`. A row that reads a kind as
   EVIDENCE reads it only under `measured` provenance. This covers a priced
   pre-scan, D162 add. 1's density decline, and r17b′'s F0, R5, R6, R8 and P1.
   Under a `prior-*` provenance such a row selects the total default (D162 add.
   3; D161 add. 15 Q-WR-9: the pre-scan's default is KEEP).
8. **What the kit reports back** `[rev3]` (§3.7.3). From the first commit that
   ROUTES a kit row reading a kind, the kit returns, at `mf_art_end`, a
   per-kind `consulted` bit: true iff a kit row of this art read that kind.
   This is R-MS2's boolean per knowledge source, at the analysis object's grain
   of one bit per kind, never per key. It is LAYER-INVARIANT: the same under
   `-fno-memfn-simd`, `-fmemfn-simd` at every level and every `--memfn=` deny,
   by the same rule as `proven` (§4.3). The check is C-CONS (§3.7.7).

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

- **Evidence strength** (`mf_prov`): how much data a `measured` kind rests on
  (the exemplar's byte count, or its sample count). Today `measured` from a
  64-byte exemplar and from a 1 GiB one read the same. **Trigger:** the first
  kit row that reads `measured` provenance as EVIDENCE (D162 add. 1's decline
  on positive density). It would be a new `mf_prov` field, an `MF_SITE_ABI`
  layout event.

### 3.7 E-1: main's build step (window_contract S1) `[rev3]`

E-1 is r17b′ §3.1's "(main) E-1" row. pcrec builds `mf_analysis` with the
frequency kind ALWAYS present (`prior-authored`, `prior-none` or `measured`)
and states it to the kit. D167 makes it buildable now. It lands AFTER the kit's
B2 merges and BEFORE B3a, whose five ported picks read it (KW-8: "a NULL
analysis would move bytes").

#### 3.7.1 What E-1 builds

| piece | where | what |
|---|---|---|
| the kinds table | `src/core/findings.c` (beside the derivation vocabulary it is keyed by) | `find_kinds[]`, the §3.2 rows: tag, payload version, `arrives`. ONE table. Its tags are checked against the vocabulary's query column at build (a `_Static_assert`-shaped count plus a startup self-check in the test build), so the query list does not gain a fifth spelling (F-3) |
| the OFFER accessor | `src/core/findings.c` / `.h` | `pcrec_find_offer(Ctx *, size_t kind, PcrecFindOffer *)`: evaluates T-KIND for one row and returns `{present, source, bundle, digest, payload}`. It DERIVES through the same memoized derivation the readers use (`find_derive_byte_rate` for `byte-rate`) and does NOT mark the query asked. The record gains `bool byte_rate_derived` (the memo) beside `byte_rate_asked` (the consumption mark). `pcrec_find_byte_rate` sets both, `pcrec_find_offer` sets only the first. This split is the whole difference between E-1 being zero-mover and being an abi event (§3.7.3) |
| the object builder | `src/gen/memfn_sites.c` (the pcrec↔kit adapter, the one file that includes `memfn.h` for art state) | in `pcrec_memfn_art`, before `mf_art_begin`: one `mf_akind` per `find_kinds[]` row, mapped `PcrecFind*` → `MF_PROV_*`/`MF_KIND_*`. It asserts the payload invariant (§3.1) and passes the object in B1's slot. `src/core` never includes `memfn.h` |
| nothing else | — | no emitter text, no stamp code, no flag, no listing. `pcrec_find_stamp` is UNCHANGED at E-1. Its generalization over the kinds table belongs to [KNOW-SRC]'s `ks_stamp` (`measure_sets.md` §9.2 part 5), so it is not built twice |

**Every artifact builds it.** `pcrec_memfn_art` runs on every attempt, because
the prologue's `pcrec_memfn_flush_helpers` and the stamp pass's
`pcrec_memfn_stamps_render` both call it. So every artifact's art carries the
object, including artifacts with no kit site. That is D162's "pcrec should send
what it has", stated once per art.

**Compile cost.** At default flags every compile already derives `byte-rate`
(§3.7.4), so the offer adds no derivation. It adds one derivation per attempt
only on the deny arms that ask nothing today: one normalization of 256 counts
(`pcrec_find_normalize`) over the pre-parsed store. The parse itself was moved
out of compile time by [FINDINGS] B1. This is UNMEASURED but bounded by that
arithmetic. The E-1 census run reports compile time beside its byte compare,
with no gate on it.

**Compound artifacts.** Each part is its own compile (`part_compile`) with its
own `Job`, record and art, under the parent's analysis and encoding. So each
part builds an object of equal content. C-E1-4's compound fixture checks the
equality.

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

#### 3.7.3 The stamp: CONSULTED, the [KNOW-SRC] family's one rule

**The conflict the family check finds.** Revision 2's R1 disposition made
`<PREFIX>_FINDINGS` mean OFFERED: building the object sets `byte_rate_asked`,
so the stamp lists every kind offered and is never empty. Its sibling
`<PREFIX>_MEASURES` (`measure_sets.md` §3.5, two days later, panel-reviewed)
means CONSULTED: empty when no pcrec reader asked and the kit returned
`consulted = false`, and explicitly "follows the `_FINDINGS` meanings
(findings.md 5¶4)". [KNOW-SRC] (§9.2 part 5) builds ONE stamp grammar for the
family: "EMPTY = nothing asked; otherwise the kind's item text". Its census tool
attributes analysis movers from "the (query, bundle) pairs it ASKED" (§9.3).
Under OFFERED, the two siblings would carry two rules in one module, which is
the parallel-mechanism shape [KNOW-SRC] exists to remove.

**This revision's design of record: CONSULTED, for both siblings.**
- **The rule.** A kind's item appears in `<PREFIX>_FINDINGS` iff the kind was
  consulted: a pcrec reader asked it (`pcrec_find_byte_rate`, as today), OR a
  kit row read it (§3.3 rule 8's per-kind `consulted`). The item's text is
  today's (`query=bundle:digest`, or `query=none` where nothing answered).
- **The offer is not an ask.** Building the object is an offer (§3.7.1's
  `pcrec_find_offer`) and does not set `byte_rate_asked`.
- **So E-1 moves NO byte.** It is not a pcrec abi event, it moves no byte-count
  reader, and it carries no D80 hunk. The object is an internal kit channel,
  and nothing caller-observable changes (§3.7.9).
- **When the stamp's meaning becomes observable.** The kit's per-kind
  `consulted` joins the stamp at the first commit that ROUTES a kit row reading
  a kind. In r17b′'s plan that is **B3b**: the five ported picks route there
  and pcrec's own pick readers retire. That commit is zero-mover in the stamp
  iff, on every artifact, (kit consulted ∪ pcrec asked) equals today's pcrec
  asked set. Its emit_sweep compare proves that, and S989 (§3.7.8) plants the
  OR's loss. That commit carries the findings.md §5 / match_api hunk of
  §3.7.9. S2's kit ranking, if it routes earlier than B3b, takes the same
  obligation at its own commit.

**Why CONSULTED and not OFFERED** (the argument; Q3 asks Frank to confirm):
- **One rule for the family.** `ks_stamp` exists once, and the census tool's
  attribution works for both kinds.
- **The stamp keeps answering "which data built this artifact".** findings.md
  5¶9's "moves the digest of every artifact that CONSUMED it" stays true. Under
  OFFERED a regeneration of the default prior moves every byte artifact's stamp
  whether or not anything read it. Revision 2 §10.3 accepted that, and
  [ART-MGR]'s cache would over-invalidate on it.
- **The per-compile isolation check keeps its witness.** findings §6 #22 and
  S314 detect a consumption record leaking across compiles by a second target
  that asks NOTHING and must stamp `""`. Under OFFERED nothing stamps `""`
  (§3.7.4), so #22 and S314 lose their witness, and S314 would ship UNREACHED
  or need a new detector.
- **E-1 lands at zero movers in every arm, deny arms included.**

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

The OFFERED alternative's event is stated exactly in §3.7.5, so a contrary
ruling builds from this note with no further design.

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

#### 3.7.5 The OFFERED alternative, exactly (if Q3 rules against this revision)

- **The event.** E-1 IS a pcrec abi event (78 → the next number at landing,
  never a literal in a brief). It carries the identity re-pin and the D80
  hunks of §3.7.9 (OFFERED column).
- **The stamp change.** `""` disappears. The stamp lists one item per PRESENT
  kind in the fixed query order: `byte-rate=<bundle>:<digest>`, or
  `byte-rate=none` under `prior-none`. ABSENT kinds are not listed. That way a
  kind's later arrival moves only the artifacts it is present on, not every
  artifact. Today's item spellings are kept, so no artifact whose stamp is
  non-empty today moves.
- **The movers.** Exactly the `""` population (§3.7.4): 0 at default; the
  deny-arm artifacts otherwise. Each mover grows by the item text twice (macro
  plus `rx_info` initializer): +2×34 bytes under `-e byte` (`byte-rate=default:`
  + 16 hex digits) and +2×14 under `-e utf8` (`byte-rate=none`). Both lines are
  written by the engine emitter (`emit_dfa.c:3048`, `:3348`), before the size
  caps measure the artifact (`compile.c`'s cap check runs after the stamp pass
  at `:2971`, from `:2995`), and both count as CODE bytes. So a deny-arm artifact within 68 bytes of either cap
  (`PCREC_MAX_EMIT_BYTES`, `PCREC_MAX_EMIT_CODE_BYTES`) can change its ladder
  decision. The census must record every `*_WHY`/ladder token and refusal, as
  `knowledge_census.sh` does (`measure_sets.md` §9.3), not only the stamp line.
  The corpus's closest artifact sits 75 bytes under the total cap
  (`tests/utf8/axis12_scripts.rxt:296`, `opt_dial_design.md` §6.2a) at its
  default arm, which does not move.
- **The census owed.** emit_sweep over its full population, every stream, at
  default, `-e utf8`, `--engine=vm` and the deny arms of §3.7.4. Compare with a
  named-lines gate (whole file minus the `_FINDINGS` line and the `.findings =`
  initializer): 0 movers, and the stamp movers equal the `""` set by ID.
  Tokens and refusals are identical. The bench patterns are compiled
  read-only.
- **The re-aims.** findings §4's "nothing asked" cell and §6 #22 must be
  re-aimed, since no compile stamps `""`. The per-compile isolation check
  needs a new detector: a second target under a DIFFERENT analysis or encoding
  must not carry the first's item. S314's anchor
  (`if (!fr->byte_rate_asked) return "";`) and its REACH (`_FINDINGS ""`) are
  re-aimed by `scripts/sabotage_anchors.py --step`, or the row is retired.
- **The sibling.** `<PREFIX>_MEASURES` would also move to OFFERED, for one
  [KNOW-SRC] rule, and that reopens `measure_sets.md` §3.5. After M0 every
  default-set change would then move every artifact.

#### 3.7.6 Readers, found by grep (`063b4a4b4`)

**Readers of the stamp's VALUE and of the consumption record** (grep
`FINDINGS`, `byte_rate_asked`, `byte_rate_have`, `\.findings`, `byte-rate=`,
`nothing asked`):

| reader | what it reads | E-1 (CONSULTED) | OFFERED |
|---|---|---|---|
| `src/core/findings.c:373-381` `pcrec_find_stamp`; `:390-398` the accessor | `byte_rate_asked` | unchanged; the record gains `byte_rate_derived` (§3.7.1) | `asked` is set by the build; `""` unreachable |
| `src/core/findings.h:94-104` (the record), `:185-190` ("the empty string when nothing was asked") | the record's comment | `byte_rate_derived` added, comment unchanged | comment changes |
| `src/gen/emit_dfa.c:3038-3049` (the stamp and its comment), `:3348` (the initializer) | the stamp text | unchanged | comment changes |
| `src/facts/req.c:651-654` `req_rate_why` | `byte_rate_have` DIRECTLY, not through the accessor | unchanged: both its callers ask first (`:669`, `:712`), so `have` is set by then, and E-1's earlier derivation cannot flip it. See F-2 | same |
| `tests/findings/run_findings_tests.sh:19-22`, `:141-166` (§4 incl. `check_stamp "nothing asked" ""`), `:392-403` (§6 #22, `_FINDINGS ""` on `t_quiet.c`) | the stamp, `""` included | unchanged; they become E-1's own detectors (§3.7.7) | re-aimed |
| `tests/mech/sabotages/S314_findings_record_outlives_compile.sh` (`SAB_BEFORE` = the `return "";` line; `SAB_REACH` greps `_FINDINGS ""`) | the anchor and a `""` witness | unchanged | re-aimed or retired |
| `tests/resource/run_resource_tests.sh:665-669`; `tests/codegen/run_cpset_structure.sh:772` | byte counts (+55 macro, +56 initializer) | unchanged | re-measured at the same `-o` basename |
| `tests/codegen/run_encoding_checks.sh:599-606`, `:642`, `:1506-1508` | utf8 side `== byte-rate=none`, byte side `!= none` | unchanged (holds: every default utf8 compile asks) | unchanged |
| `tests/codegen/run_recursion_identity.sh:1135-1140` | the (B) pin's named-lines narrative | unchanged | re-pin (abi event) |
| `docs/spec/findings.md` §5¶1-¶9; `docs/spec/match_api.md` 6.3.10¶10-¶11, the `rx_info` row 28 (`:1287`), 6¶14, the stamp-class table (`:2467`) | the stamp's meaning | unchanged at E-1; B3b's hunk (§3.7.9) | E-1's hunk |
| `docs/design/measure_sets.md` §3.5, §9.2 part 5, §9.3, §9.5 | the sibling's statement of the shared rule | consistent | reopened |
| `lib/pcrec.h:1582` | "built under it" | unchanged | unchanged |

**Readers of the abi NUMBER** (OFFERED only; grep `78` beside `abi`/`ABI`):
`src/gen/emit_dfa.c:54` `PCREC_ARTIFACT_ABI`; `docs/spec/match_api.md:169`
(the K80 `#error` text) and its "abi is N" sentence;
`docs/dev/history/abi_changelog.md`; `tests/codegen/run_codegen_tests.sh:3149`
`ABI_EXPECT`; `tests/codegen/run_recursion_identity.sh:1251` FILEPIN;
`tests/mech/sabotages/S693_abi_not_bumped.sh:51`. The rest of the reader list
is re-derived by grep at landing (D94): the byte-count class (r17b′ §3.4's
list), the alpha normalizers, then the registry, codegen and rxtsource suites
and `make test-codegen`. At E-1 under CONSULTED none of these moves.

**Findings from the grep:**
- **F-2.** `req_rate_why` (`req.c:651-654`) writes `rate:builtin-prior` iff
  `byte_rate_have`, which is true for ANY answering block, `--analysis weblog`
  included. `docs/spec/facts_listing.md` 4.1.3¶4 defines `rate:builtin-prior`
  as "the shipped byte-frequency prior". This was read from the code, not run.
  E-1's T-KIND now names the provenance (`measured` vs `prior-authored`).
  Re-sourcing the `why` token from it is a caller-visible `--emit-facts` change
  and is FILED, not done in E-1. Trigger: the first listing consumer that reads
  the token, or [IFACE-PUSH].
- **F-3.** The query vocabulary is spelled four times:
  - `findings.c:190` (the derivation table's third column);
  - `rxt_find.c:326` (`queries[]`);
  - `findings_dump.c:39` (`FIND_QUERIES[]`);
  - `rxt_source.c:617` (an error text naming "(byte-rate, run-rarity)").

  E-1's `find_kinds[]` would make a fifth unless it is keyed by the first.
  §3.7.1 keys it so. Unifying the other three is filed under [KNOW-SRC]
  (its analysis kind owns the vocabulary).
- **F-4.** `measure_sets.md` §4.2's `consulted` has the layer-invariance
  obligation of §3.7.3 and does not state it. That is for its next revision.

#### 3.7.7 Checks (each against a source the subject does not share)

| id | checks | expectation from | population and reach |
|---|---|---|---|
| **G1-E1** zero-mover | emit_sweep, every stream, at default, `-e utf8`, `--engine=vm`, AND the deny arms `-fno-req-byte` and `-fno-req-byte -fno-req-run -fno-prefilter` (both encodings), plus the bench patterns read-only: 0 movers, tokens and refusals identical | the pre-E-1 binary | the deny arms are REQUIRED: the default arms hold 0 `""` artifacts (§3.7.4), so they cannot see an offer leaking into the stamp (K35). A floor: ≥ 1,900 `""` artifacts in the `-fno-req-byte` arm, measured, a literal |
| **C-E1-1** object content | a trace-build record per attempt (`-DPCREC_CAND_TRACE`, a `KSRCTRACE` line: kind, tag, state, source, bundle, digest), over fixtures: `-e byte`/`-e utf8` × {no `--analysis`, `weblog`, `log`, a user `-I DIR/default.rxt`, `include default` by name, a two-link `include` chain} | a HAND-WRITTEN expected (state, source, bundle) table per fixture, and each digest recomputed in python from the fixture's rows (`tests/findings`' `bdig`/`res_fixtures.py`, which already re-derive digests independently) | 12 cells; every T-KIND row that can fire at E-1 (`no-shape` on `run-rarity`, `measured`, `prior-authored`, `prior-none`) fires at least once, a reach floor per row; `absent` cannot fire until B4 gives `run-rarity` a shape, and is declared UNREACHED |
| **C-E1-2** kinds completeness | the object lists every tag once, in vocabulary order | a hand-written list in the test (`byte-rate`, `run-rarity`), cross-read with findings.md 5¶2's query order | the `run-rarity` entry is ABSENT through `no-shape` until B4 |
| **C-E1-3** payload invariant | non-NULL iff PRESENT and source ∈ {PRIOR_AUTHORED, MEASURED}; a byte-rate payload sums to 1,000,000; PRIOR_NONE has bundle NULL and digest 0 | the trace record, recomputed (the build's own assertion is the second, shared-source line) | every fixture of C-E1-1 |
| **C-E1-4** stamp/object agreement | wherever `_FINDINGS` has `byte-rate=B:D`, the object's byte-rate is PRESENT with bundle B, digest D; `byte-rate=none` ⇔ PRIOR_NONE; `""` with the object PRESENT is the OFFERED-NOT-ASKED cell (CONSULTED's own evidence); a compound fixture's parts carry equal objects | two derivations of one record, read through two outputs (stamp text, trace) | `multi.rxt` (findings §6 #22's fixture: `t_asks`, `t_quiet`) plus a compound split fixture |
| **C-CONS** (owed at B3b) | `consulted` per kind and `_FINDINGS` are byte-identical under `-fno-memfn-simd`, `-fmemfn-simd` at every live level, and every `--memfn=` deny | the SIMD-off compile | emit_sweep's `-fmemfn-simd` arm (S981-S982's) |
| ASan/LSan | the object outlives `mf_art_end` and is freed with the attempt | — | `make asan` over `test-findings` and `test-memfn` |

#### 3.7.8 Sabotage (ids PROPOSED from `worktrees/.mgr/sabotage_ids.txt`'s next free, S983; the manager allocates)

| proposed id | plant | detector | reach witness |
|---|---|---|---|
| S983 | the offer marks the query asked (`pcrec_find_offer` sets `byte_rate_asked`) | findings §4 "nothing asked" (`-fno-req-byte --pattern '^abc'` stamps `byte-rate=default:…` where `""` is expected) and §6 #22; G1-E1's deny arm | `-fno-req-byte '^abc'` compiles and builds the object (every art does) |
| S984 | provenance by NAME: `prior-authored` iff the bundle is named `"default"` | C-E1-1's `-I DIR/default.rxt` cell (expected MEASURED) | the `-I` fixture answers through `PCREC_FIND_STOP_DIR` |
| S985 | `prior-none` carries a uniform table as payload (D126 Q4's false confidence) | C-E1-3 | `-e utf8` with no `--analysis` |
| S986 | the object is built once per PROCESS (a static cache), not per attempt | C-E1-4 on `multi.rxt` extended with a target under a different `analysis` line | two targets in one invocation |
| S987 | byte-rate's `arrives` cell flipped to `MEASURED-ONLY` | C-E1-1's `-e utf8` cells (expected PRESENT/prior-none, got ABSENT) | `-e utf8` with no `--analysis` |
| S988 | the provenance digest computed over the COUNTS, not the derived ppm | C-E1-4 (object digest ≠ stamp digest) | any byte compile that asks |
| S989 (B3b's) | pcrec does not OR the kit's per-kind `consulted` into the stamp | B3b's zero-mover emit_sweep (stamps drop to `""` where a moved pick was the only asker) | the five ported picks' population |
| S990 (B3b's) | a SIMD-only kit row sets `consulted` | C-CONS | `-fmemfn-simd` arm |

S983-S988 land with E-1; S989-S990 land with B3b. Eight ids in all.

#### 3.7.9 D80 spec hunks

**Under CONSULTED (this revision): E-1 carries NONE.** The object is the kit's
input, and `docs/spec/` describes no `memfn.h` struct. No stamp, flag, limit,
listing, entry or diagnostic changes. The stamp's meaning does change at
**B3b**, which carries these hunks:
- `findings.md` 5¶2: "One `query=bundle:digest` item per query the compile
  CONSULTED (a pcrec reader asked it, or a pcrec-memory-functions row read it),
  in the fixed query order…"
- 5¶4: "The empty string when nothing was consulted."
- a new 5¶10: "Every compile OFFERS the kit the analysis object (`byte-rate`
  always, with its provenance; other kinds when measured). An offer that no
  reader consults is not stamped. `<PREFIX>_MEASURES` follows the same rule
  (`measures.md`)."
- `match_api.md` 6.3.10¶11: "ASKED" → "CONSULTED (asked by a pcrec reader or
  read by a kit row)". In ¶10's example, `/* nothing asked */` →
  `/* nothing consulted */`. In the `rx_info` member row 28: "`""` when none was
  consulted".

**Under OFFERED: E-1 carries all of these:**
- `findings.md` 5¶2: "One item per kind the compile OFFERED the kit and found
  PRESENT, in the fixed query order; `byte-rate` is present on every compile,
  so the stamp is never empty."
- 5¶3: "`query=none` for a present kind with no table (`prior-none`: `-e utf8`
  with no `--analysis`)."
- 5¶4: deleted.
- 5¶9: "A change to the shipped data moves the digest of every `-e byte`
  artifact that names no other analysis."
- `match_api.md` 6.3.10¶10: the `""` example line is deleted.
- 6.3.10¶11: rewritten as 5¶2.
- the `rx_info` row 28: "never `""`".
- the abi sentence and the abi change-log line.

#### 3.7.10 What E-1 does not do

- **No kit edit, and no `MF_SITE_ABI` move.** B1 declared the slot, and E-1
  fills it.
- **No kit row reads the object.** That begins at B3a, as a trace-only shadow
  that does not set `consulted`, and is routed at B3b.
- **No `run-rarity` payload.** That is B4's.
- **No `ks_stamp`.** That is [KNOW-SRC]'s.
- **No `req_rate_why` re-source** (F-2).
- **No new caller-observable surface.**
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
| **S1** frequency kind = **main's E-1** `[rev3]` (§3.7) | the kit's B1 declares `mf_analysis` and its slot on `mf_art_begin` (NULL-tolerant); E-1, after B2, builds the object per attempt from `Job.find` through `find_kinds[]` and fills that slot with no kit edit. The offer does not mark the query asked (§3.7.1) | **0** in every arm (CONSULTED, §3.7.3). Under the OFFERED alternative: exactly the `""` population, which is 0 at default flags and up to every artifact on the deny arms (§3.7.4) | CONSULTED: no pcrec abi event, no `MF_SITE_ABI` move at E-1 (B1 took it), no D80 hunk; census = G1-E1 (§3.7.7). OFFERED: §3.7.5's abi event, hunks and re-aims |
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
| `[rev3]` the kit's per-kind `consulted` joins the stamp (B3b, or S2's REPLACE if earlier) | no | YES (the `mf_art_end` output) | no iff the union of askers is preserved (S989) | YES (findings.md §5's CONSULTED wording) |
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
| T-KIND: one kind's state (§3.2) `[rev3]` | pcrec | `no-shape` → `measured` (a non-default LINK answers) → `prior-authored` (the store's `default` bundle answers, by identity) → `prior-none` (nothing answers and the row's `arrives` is ALWAYS) → `absent`. No row names a kind |
| `find_kinds[]` `[rev3]`: the kinds the object lists (§3.2) | pcrec | one row per [FINDINGS] query: tag, payload version, `arrives` |

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
   build a kit site from one row of `cand_rows[]`. Under T-CUT and T-PRES they
   become one window site of hull spans per segment, the union-span site
   (until unlock (b)), and at most one PRESENCE site.
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
   | the kit reports back | per-kind `consulted` at `mf_art_end` (§3.3 rule 8) | one `consulted` boolean at `mf_art_end` (R-MS2) | aligned: one bit per knowledge source; the object holds several sources (kinds) |
   | stamp meaning | CONSULTED (§3.7.3; revision 2 had OFFERED) | CONSULTED (§3.5) | **aligned by this revision**; the OFFERED alternative would split them (Q3) |
   | stamp item | `query=bundle:digest` / `query=none` (digest of what was consumed) | `id@rev:values_digest` (stamp-on-load) | different on purpose: a set has an immutable `id@rev` and a bundle has only its name and digest (`measure_sets.md` §3.5's own argument) |
   | provenance | per kind: `prior-authored` / `prior-none` / `measured` | per row: `measured` / `fitted` / `derived` / `null`, plus the set's `class` and `tier` | different vocabularies over different contents; both state "how derived" (D162 add. 3, D166) |
   | evidence rule | rows needing evidence read only `measured` (§3.3 rule 7) | the envelope's safe direction belongs to the reader row (§6.2) | compatible |
   | layer invariance of `consulted` | stated (§3.3 rule 8, C-CONS) | NOT stated (F-4) | a gap in the sibling, filed for its next revision |
   | the stamp builder | `pcrec_find_stamp` today, `ks_stamp` at [KNOW-SRC] | `ks_stamp` | one builder, once [KNOW-SRC] lands; E-1 does not pre-empt it (§3.7.10) |
   | the query vocabulary | spelled four times today (F-3); `find_kinds[]` keyed by `findings.c`'s table | the card table, closed (§7.2) | F-3 filed under [KNOW-SRC]'s analysis kind |

## 10. The three standing questions

1. **Measurement regime: RELEVANT, and no number decides this note.**
   `[rev3]` Revision 3 adds one COUNT, not a timing: §3.7.4's stamp census
   (corpus argv stream, three default arms and five deny arms, this tree's
   binary on the Linux dev box). A count of stamp values does not depend on the
   box, compiler or libc. Different data would flip only the OFFERED
   alternative's mover population, not the design of record, which is
   zero-mover by construction. E-1's compile-time cost is unmeasured and
   bounded (§3.7.1). The
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
     artifact" holds only under the OFFERED alternative, where the deny-arm
     artifacts move too.
   - The digest in each kind's provenance is the stamp's value, so "which data
     built this artifact" has one answer.
   - D160's authored utf8 prior turns `-e utf8`'s kind from `prior-none` to
     `prior-authored`, moving every utf8 artifact's stamp. S2's shadow covers
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
  S964-S980. E-1's are proposed at S983-S990 (§3.7.8).

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
   - **What stays.** T-PRES (§5.4a) still sends the unbounded-offset presence
     span (`zxq` beside segment 0 in `a.*zxq`) as its own site, because it has
     no bounded distance to the origin. "Send both origins and let the kit say
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
   analysis: what was CONSULTED, or what was OFFERED?** This is Frank's: it is
   the meaning of a caller-visible stamp, and it decides whether E-1 is an abi
   event.
   - **The problem.** Revision 2 accepted the panel's R1 by redefining the stamp
     as OFFERED, the kinds handed to the kit. Two days later
     `measure_sets.md` defined its sibling `<PREFIX>_MEASURES` as CONSULTED,
     explicitly "following the `_FINDINGS` meanings". [KNOW-SRC] then built
     ONE stamp grammar for both. The two notes now disagree, and one module
     cannot hold both rules without a per-kind special case.
   - **The forces.** CONSULTED keeps the stamp's job ("which data built this
     artifact"). It keeps one rule for the family, it keeps the per-compile
     isolation check's `""` witness (S314, findings §6 #22), and it lands E-1
     at zero movers. It costs a per-kind `consulted` bit from the kit, owed at
     B3b, which must be layer-invariant. OFFERED needs nothing back from the
     kit and can never under-report a kit read. But it makes E-1 an abi event
     on the deny arms, retires a working check, and forks [KNOW-SRC] unless
     `<PREFIX>_MEASURES` follows it.
   - **The measured fact that lowers the stakes.** At default flags the two
     readings give the SAME stamp on every corpus artifact: every default
     compile already asks (§3.7.4). They differ only on deny arms, and from
     B3b on what the kit reads.
   - **The leaning.** CONSULTED, for both siblings (§3.7.3). If Frank prefers
     OFFERED, §3.7.5 is the build text, and `measure_sets.md` §3.5 is reopened
     in the same ruling so the family keeps one rule.
4. **`[rev3]` When does `--emit-facts`' `rate:builtin-prior` stop mislabelling
   a measured bundle (F-2)?** This is the manager's unless Frank wants it.
   - **The problem.** The token is written whenever ANY block answered, but the
     spec defines it as the shipped prior.
   - **The forces.** E-1 creates the provenance that would name it correctly.
     Re-sourcing the token is a caller-visible listing change (a
     `facts_listing.md` hunk) and moves `--emit-facts` output under
     `--analysis`, which is emit_sweep's stream 6.
   - **The leaning.** Do it in B3b's commit, which already carries the
     findings-stamp hunks and re-sources `--emit-facts`' `used`/`why` (r17b′
     §3.4). Spell it `rate:<provenance>` (`rate:prior-authored`,
     `rate:measured(<bundle>)`, `rate:none(<enc>)->rightmost`). Until then,
     correct the spec sentence to say what the code does.

## 13. Filed facts and unlocks (each with its trigger)

- **The per-site ACTIVATION fact** `[r4 R10]`. setfind §9.2's decline arm
  (D162 add. 1: decline on positive evidence of density WITH a state-losing
  call pattern) needs to know the site's call pattern: whether one search call
  sees many candidates (state carries) or each candidate is a new call
  (find-all under today's API). No slot exists. It would fill D162's reserved
  per-site slot. **Trigger:** the decline arm is built (a measured dense cell
  with a state-losing call pattern, D162 add. 1).
- **The EVIDENCE-STRENGTH fact** (§3.6). **Trigger:** the first kit row that
  reads `measured` provenance as evidence.
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
4. **T-PRES's `dominated` row.** Is it G1's predicate exactly, and does it
   read the window site's spans or the prefilter's language?
5. **S1's mover population.** ANSWERED `[rev3]` (§3.7.4): every default corpus
   compile already asks, so the `""` population is 0 at default. It exists only
   on deny arms, and it is the whole of the OFFERED event's movers.
6. `[rev3]` **The offer/ask split (§3.7.1).** Can any path read `byte_rate_have`
   or the payload before an ask, so that the earlier derivation changes its
   answer? `req_rate_why` reads `have` directly, and its two callers ask first
   (§3.7.6). Is there a third? A grep found none, so attack with a reader added
   since.
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
