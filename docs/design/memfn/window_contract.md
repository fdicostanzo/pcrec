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
leaning; Q3-Q5 are new and in discussion form. Q3 (what the `_FINDINGS` stamp
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
   the stream covers the positions after it `[r4 E1]`. Presence sites keep the
   VERDICT reply. Because every candidate has one meaning, the reply needs no
   span index (§7).
3. **The ANALYSIS object** (D162) is a versioned list of kinds keyed by the
   [FINDINGS] query name (`byte-rate`, later `run-rarity`). Each kind is
   PRESENT or explicitly ABSENT and carries a PROVENANCE: `prior-authored`,
   `prior-none` or `measured`, plus the bundle identity and the same digest
   the `<PREFIX>_FINDINGS` stamp reports. Every enum has an UNSTATED zero
   `[r4 R4]`. `byte-rate` is always present. Under `-e utf8` today it is
   `prior-none` with no table (§3.2). The kit is encoding-blind (D147 add. 14),
   so `cpfreq` is never sent.
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
   lands first (S1, a pcrec abi event `[r4 R1]`), then the kit's own ranking,
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

## 1. Inputs, and what is already built

**Binding rulings** (read in full; not re-opened):
- D146 (delegation) and D147 (layers);
- D155 add. 3/4/4.1 (composable body pieces; per-width primitives; a STATEFUL
  FIND's body contract is `next_candidate(&state, lo)`);
- D157 (facts, never method);
- D161 + add. 1-8 (add. 7: the stream; add. 8: proven facts kept);
- D162 + add. 1-4.

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

A site's reply is one of two TYPES, keyed on its op:

| op | reply | meaning |
|---|---|---|
| FIND (a window site) | STREAM of candidates `[D161.7]`. Stateless: each FIND call returns the next candidate `≥ lo` (W3's `result`). Stateful: `next_candidate(&state, lo)` (D155 add. 4.1, R-17's forms). Both deliver the same sequence | see the obligations below |
| ALL_PRESENT (a presence site) | VERDICT (and, under ASSIGN, the leftmost hit of `preds[ret_pred]`, unchanged) | Every REQUIRED predicate occurs somewhere in `[lo, hi)`. No window fields: such spans state `window_stated` 0, which R17-a already requires on non-FIND sites |

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
- **A bounded span's presence is part of FIND.** An exhausted stream has
  proved that no covered position carries all spans. So the pre-check the
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
| run pre-check (unbounded offset) | the run, as a presence predicate | none (`window_stated` 0) | VERDICT |
| K82/L1 handoff | span 0 = the landmark; head `[0, K]` is pcrec's | 0 / 0 | today: a VERDICT plus pcrec's `c - K`. At R-18: a stream; pcrec keeps `c - K` |

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
    const char *bundle;     /* MEASURED: the answering bundle; PRIOR: "default" */
    uint64_t    digest;     /* what was consumed: pcrec_find_byte_rate_digest,
                               the value `<PREFIX>_FINDINGS` reports; 0 under
                               PRIOR_NONE                                      */
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

The site reaches the object as `mf_site.analysis`, appended last (D162 ruling
1). NULL is "none stated" and is legal only for a stand-alone K3 caller.

### 3.2 The kinds today, and their provenance

| tag | when present | provenance | payload |
|---|---|---|---|
| `byte-rate` | ALWAYS (D162 add. 2) | `measured` (bundle, digest) when a `--analysis` block answers; `prior-authored` ("default", digest) under `-e byte`, which is `default.rxt`'s unigram block; `prior-none` under any encoding no shipped block serves, which today is `-e utf8` | `uint32_t ppm[256]`, summing to 1,000,000 (`pcrec_find_normalize`'s rule). NULL under `prior-none` |
| `run-rarity` | when a bundle's `bigram` block answers ([FINDINGS] B4, not landed) | `measured` only | B4's shape; the kit sees the kind only once a row reads it |

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
3. **One object per compile attempt.** pcrec builds it from `Job.find`, which
   is per attempt, at the first site ask. Every site of one `mf_art` states
   the SAME pointer. The kit refuses a site whose pointer differs from the
   art's first, and NULL counts as a pointer value: an art whose sites mix
   NULL and non-NULL is refused `[r4 R9]`.
4. **The per-site slot stays RESERVED** (D162 ruling 1). No field is added
   until a measured case needs a fact the kit cannot derive. Filling it is an
   `MF_SITE_ABI` event (§8.2).
5. **Totality.** Every kit selection is TOTAL when the object, or any kind in
   it, is absent or `prior-none` (D162 ruling 2).
6. **Lifetime.** The object lives in pcrec's arena until the attempt ends,
   which outlives `mf_art_end`.

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

### 5.4a Whether a PRESENCE site rides beside it: T-PRES (first match) `[r4 E3]`

Presence is no longer a T-CUT row, so it is not exclusive with a window site.

| row | predicate | sends | deny |
|---|---|---|---|
| `dominated` | the window site's spans include the presence span's bytes at a bounded offset (G1's question) | nothing | `-fno-req-byte`/`-fno-req-run` (the sources' own) |
| `presence` | a presence span exists | a PRESENCE site (VERDICT), run before the window site | `-fno-req-byte`/`-fno-req-run` |
| `none` | always | nothing | none |

`a.*zxq` now sends segment 0 (`a`) AND the `zxq` presence site, which keeps
reqpos_2b's measured win (1.46 of 10.284). Whether presence becomes the
chain's zero-cost first link is unlock (c).

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
| unbounded-offset presence | the PRESENCE site's existence is pcrec's (T-PRES); its FORM is the kit's |

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
| **S1** frequency kind | `mf_analysis` in `memfn.h`; `mf_site.analysis` appended last; pcrec builds the object per attempt from `Job.find` and states it on every site; the kit's one-object check (§3.3 rule 3) | **every artifact whose `<PREFIX>_FINDINGS` is `""` today** `[r4 R1]`: building the object sets `byte_rate_asked`, so `pcrec_find_stamp` stops returning `""` and the stamp and `rx_info.findings` move to `byte-rate=default:<digest>` (`-e byte`) or `byte-rate=none` (`-e utf8`). Census owed: an `emit_sweep` compare over the corpus and bench, both encodings | `MF_SITE_ABI` bump (layout); a **pcrec abi event** (readers found by grep, the byte-count class included); **D80 hunk**: `docs/spec/findings.md` §5 and the stamp sentences in `docs/spec/match_api.md` — the stamp now means the kinds OFFERED to the kit, one entry per kind this pcrec knows, provenance-coded (today's `byte-rate=` spelling is the single-kind case). Consequence: after S1 every regeneration of the default prior moves every artifact's stamp digest, an abi event each time (§10.3) |
| **S2** kit ranking | the kit derives each RUN term's position order from `byte-rate` in its memo (§3.5), applying the D126 Q4 per-question NONE answers under `prior-none`. IMPLEMENT beside `rank_*` with a SHADOW comparator: the kit's order equals `pcrec_find_run_rank`'s for every site of every corpus compile, at `-e byte` and `-e utf8`. Then REPLACE: `vrun`'s KB reads the kit's order | 0 (same order, proven by the shadow) | kit-only; no `MF_SITE_ABI` move; no pcrec abi event |
| **S3** retirement | see the file list below | 0 | ONE `MF_SITE_ABI` bump (layout); no pcrec abi event; D80: none (internal) |
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
| the per-site analysis slot is filled `[r4 R9]` | no | YES | yes iff a byte moves | no |
| S1: the object first built | no | YES | YES (the stamp moves from `""`) | YES |
| a kit row starts reading a kind or a field | no | no | yes iff a byte moves, same commit, own deny | only if a stamp's meaning moves |
| bundle or prior data regenerated | no | no | YES after S1 (every artifact's stamp digest); also wherever a row reads it | no |
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
| T-PRES: whether a presence site rides beside it (§5.4a) | pcrec | `dominated` → `presence` → `none`; deny column per row |
| T-REPLY: reply type by op (§2.4) | contract | FIND → STREAM; ALL_PRESENT → VERDICT; others unchanged |
| T-NEED: a span's `need` (§4.3) | pcrec | `the FIND definition requires it` (today's single-span terms) → REQUIRED; `pcrec's consumer would re-test it and wants it verified` → REQUIRED; `else` → OPTIONAL. Never left UNSTATED |
| T-PROOF: consuming a proof (§4.3) | pcrec | `report` (the proof covers the whole sub-problem and nothing else remains) → `dfa-exact-prefix` (unseeded PLAIN machine, exact proven bytes) → `vm-literal-prefix` (no capture, no assertion skipped, no meter change) → `verify-rest` (a kit VERIFY site for the unproven positions) → `ignore`; one deny for the family, `-fno-kit-proof` (PROPOSED) |
| T-KIND: one kind's state (§3.2) | pcrec | `a --analysis block answers` → PRESENT/measured; `a shipped block serves this encoding` → PRESENT/prior-authored; `the kind is byte-rate` → PRESENT/prior-none; `else` → ABSENT |

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

## 10. The three standing questions

1. **Measurement regime: RELEVANT, and no number decides this note.** The
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
   - S2's ranking is held to the shadow until S4, then to an independent
     brute force.
   - K35: a multi-span floor (§5.3). [MECH-REACH]: every sabotage row named
     here (memo order, proof over-claim, proof layer-dependence, sequence-rule
     under-estimate, C-SP1 vacuity) gets a witness that reaches its site.
3. **What moves when data is regenerated: RELEVANT.**
   - **After S1 every regeneration of the prior or a bundle moves every
     artifact's `<PREFIX>_FINDINGS` digest** `[r4 R1]`: an abi event each
     time, beyond any kit row that reads the kind.
   - The digest in each kind's provenance is the stamp's value, so "which data
     built this artifact" has one answer.
   - D160's authored utf8 prior turns `-e utf8`'s kind from `prior-none` to
     `prior-authored`, moving every utf8 artifact's stamp. S2's shadow covers
     `-e utf8` explicitly.
   - A proof is a function of the site request, which includes the analysis
     object; a regeneration that changes a proof moves pcrec's bytes, an abi
     event in the same commit.

## 11. The R-18 outline (facts only; main files it)

**R-18: THE WINDOW SEARCH (D161), the general category**

- **Customer.** D161 and add. 1-8; chunk 3. It supersedes the per-shape
  interfaces of R-15 (the ASSIGN gate), R-17 (the set FIND) and the PF/OFS/
  PRE sites. Their forms and measurements carry over.
- **Facts pcrec will state** (this note §2-§3):
  - a site is a bounded sub-problem whose origin is span 0's start, the one
    thing pcrec chooses; it sends every span bounded to that origin and the
    kit chooses which to search (D161 add. 9);
  - spans are `mf_pred`s with stated `move_back`/`overshoot` and `need`;
  - context predicates (negative offsets) are not spans;
  - `spans_seq` states the sequence rule (tri-state);
  - presence sites carry no window;
  - `mf_site.analysis` (S1, possibly landed first).
- **Obligations on the reply:** the stream (COMPLETE, ASCENDING without
  repeats, span-0 starts, REQUIRED spans satisfied); totality; an exhausted
  stream means no covered candidate; and, when [KIT-VERIFY] builds, a
  layer-invariant `proven`.
- **Facts pcrec will NOT state:** a consumer price, a span index, a scan
  position (`plan_hint` retires), a ranking (`rank_*` retires), per-site
  rates.
- **Deliverable.** The kit's method is its own. It must serve every degenerate
  site at zero SIMD-off movers first, then multi-span sites behind their own
  denies, and land each SIMD-off byte move together with pcrec's abi event.
- **Capability pcrec provides:** storage as ratified (§7).
- **Trigger.** This note, ratified. R-17's PF routing event merged. The first
  multi-span consumer: the K82/L1 handoff's fused gate re-routed as a stream
  (§2.4), cells loglines/ipv6, ipv4, bounded/dotted4; then wingame's
  syslogbase-expanded and the refine witnesses.
- **Sequencing (main's).** S1-S3 (§6) may land before the R-18 build. S4
  rides it.
- **Sabotage ids.** Main allocates at filing (consult `requests.md`'s
  reserved ranges).

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

(Revision 1's Q3, "`U` now or later", is deleted: D161 add. 7 removed `U`.)

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
- **(c) Presence as a chain link**: T-PRES's presence site becomes a
  zero-cost first link of the window chain. **Trigger:** the first
  `a.*zxq`-shaped bench cell with both a window site and a presence site.
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
5. **S1's mover population.** Is "every artifact with `""` today" the whole
   population, or do some artifacts already ask?
