# R17-b′ — the kit's first candidate-finder delivery: one table over (stop, form), one window request, zero movers first

**Revision 4.1 (2026-10-21), lane rev41, design only.** It applies Frank's three settled
answers to revision 4's three questions (§7.3), and nothing else:
1. **Q-R17P-26 (Frank):** a set site's form is chosen by its cover's TERM COUNT, a
   compile-time fact: V1 for at most 2 terms, the walk for 3 or more. There is no
   "unmeasured shape" case. R7, R7w, §1.9, §1.3a, §3.5 and §9.2a change (§R4.1).
2. **Q-R17P-27 (Frank): YES.** F2, the VM hat's one-byte set, defaults to V1 at B5 (not
   B4), with its g = 2 cells (V1 +38.3% slower) named EXPECTED losses up front.
3. **Q-R17P-28 (the kit manager's call):** P1 is recorded as fired on the letter and NOT
   built (it never fires on a default compile; D77).

Text marked `[rev4.1]` is new or changed in this revision. Superseded revision 4 text is
struck through (`~~...~~`) or carries a `[rev4.1]` note; nothing is silently deleted. The
rulings' text is in `memfn/docs/journal.md` (2026-10-21) and the two 2026-10-21 notices at
the end of `memfn/docs/responses.md`. Read §R4.1 first. Nothing under `src/`,
`memfn/src/`, `tests/` or `lib/` changes, no timing was run, and no measured constant
enters any source.

**Revision 4 (2026-10-20), lane rev4, design only.** It does three things, all for B4,
the routing commit:
1. It folds in the measured contradictions from the zen4-grid2 slot's reading
   (`docs/dev/lanes/grid2read_report.md`, merged onto this branch with its evidence
   under `r17b_prime/grid2read/`). Each changed row cites its measurement.
2. It states Frank's 2026-10-20 ruling (D169 on main) as B4's default: when landing
   predictability is unknown, the form is V1 (§1.9).
3. It restates B4's gates as they stand today, with the owed items (§3.1a).

Text marked `[rev4]` is new in this revision. Superseded rev 3 text is struck through
(`~~...~~`) or carries a `[rev4]` note pointing at what replaces it. Nothing is
silently deleted. Read §R4 first: it lists every changed row with its source. The
table B4 builds is §1.3a. Nothing under `src/`, `memfn/src/`, `tests/` or `lib/`
changes, no timing was run, and no measured constant enters any source.

**Revision 3 (2026-10-16), lane r17bp4, design only.** It applies the D6 panel on
revision 2 (`docs/dev/reviews/2026-10-16-r1-memfn-r17bp.md`: 70 ids, the kit manager's
dispositions binding), D167 and its addendum 1 (build GO; A7, A10, A11 ruled), the E-1
agreement with main, lane sweeparm's two emit_sweep arms, D163 addendum 7 with
`compound_entries.md` rev 2, and D165 with its addenda and `findall_iter.md`. Text marked
`[rev3]` is new or changed in this revision; read §0 and §R3 first. Revision 2
(2026-10-14, lane r17bp3, commit c90d65e53 on lane/memfn-r17) is marked `[rev2]`;
revision 1 is commit `830bbce39` (lane r17bp), and unmarked text is carried from it.
Nothing under `src/`, `memfn/src/`, `tests/` or `lib/` changes. No timing was run; no
measured constant enters any source. The compile-only instruments of revision 1 stay in
`r17b_prime/` (own CLAUDE.md).

`[rev2]` **The baseline is MAIN.** The kit branch carries R17-a (MF_SITE_ABI 11) and
R17-b (MF_SITE_ABI 12, pcrec abi 77 on that branch); main (abi 78, MF_SITE_ABI 10)
has neither, and the kit branch's merge into main was aborted at 17 conflicts
(winreq Q-WR-10). The R17-b′ BUILD is cut fresh from main, so every step below is
stated against main's code: R17-a's seam and R17-b's form are PORTED as steps of this
plan, not presumed (§3).

Labels: **MEASURED** (read from a row or a counter), **DERIVED** (follows from a
measured value or from the form's text), **INTERPRETATION** (my inference),
**PROPOSED** (this note's design, for review), **RULED** (a decision of record).

`[rev4]` For B4, read §R4, then §1.9 (the D169 default), §1.3a (the table B4 builds),
§3.1a (B4's gates and the owed items) and §9.2a (the expected losses B4 names before
it times anything). `[rev4.1]` Read §R4.1 before all of them: it says which rev 4 sentences
the three rulings replaced.

How to read it: §0 first, then §R3 (what revision 3 moved, by finding id) and §R2, then
§1 (the table) and §3 (the step plan). §4 is the contract (§4.5 is revision 3's
define-time query, the one contract change main reviews), §5 the measurements and the
grid2 slot.

---

## 0. Answers first `[rev2]` `[rev3]`

1. **Scope (§1.1).** One delivery covers every FIND site that searches for a match's
   START plus the presence pre-checks and handoffs that front it, all stated as ONE
   window request per search entry (D161 add. 14 and its clarification):
   - the set FIND sites (R-17): the DFA prefilter (`byte-class[-bounded]`), the DFA
     hat (`first-class-bounded`), the hybrid's inner prefilter, the VM hat
     (`first-class`, |S| = 1 included);
   - the one-byte stops (D161 add. 14): the DFA prefilter's `memchr[-bounded]`, the DFA
     hat's `first-memchr-bounded`, the hybrid's, and MLINE's `(?m)^` back FIND
     (Q-WR-2: in scope; `[rev3 A5]` a CONTEXT stop with no span 0);
   - the presence pre-checks (`REQ_BYTE`, `REQ_RUN`, set-leads, K65 set-rest, K66
     whole run) and the K82/L1 handoff (FIRST and the NEXT re-entry), merged with the
     find they front. `[rev3 A2]` `pcrec_emit_req_byte_check` has THREE callers (the
     DFA entry, the VM `_search_run`, and ENG_ATTEMPT's `attempt_entry`); all three are
     in scope.

   Out: OFS/run-pinned FUNCs (multi-position spans, R-18), the ADVANCE/VERIFY/
   MISMATCH sites, the compound route.

   `[rev3 A1, A3]` "One window request per search entry" is defined PER EMITTER (§2.1):
   one site per ACTIVATION of the function that holds it, its storage point above its
   first use, START = `search_from`. A VM hybrid holds TWO sites (presence-only in
   `_search_run`, find-only in the static `_prefilter`), because they are two
   functions with two activations.
2. **The table (§1).** `[rev3 D1]` `fd_rows[]` IS a `kit_table` walked by `kit_walk`
   (`memfn/src/kit.h`), with slots FIND and PRES: the kit's fourth table on its one walk,
   not a fourth walk. This is row_contracts.md §6 H1's trigger (a real table adopts the
   engine). `[rev3 D2]` Conditions are ONE comparator `(lhs, op, key)` plus boolean
   site facts; every threshold is a set KEY with its R-MS4 safe direction. `[rev3 D3]`
   PRES picks are chain-link attributes (`verify`, `proven_by`, `member`, `order`), not
   a private pick enum. `[rev3 C2]` Every row has a mandatory `basis`
   (MEASURED / DERIVED / UNMEASURED-DEFAULT); `[rev3 D11]` and a `refuted_by`.

   **23 rows designed** `[rev3]`: 17 in slot FIND, 6 in slot PRES. **19 are built by B4
   and LOCKED there**; F0 (NONE), F1 (a measured libc row), F2 (the VM hat's measured
   |S| = 1 move, D167 add. 1 A7) and P1 (the priced pre-scan) are added after lockdown
   as formal edits at B5. The no-data DEFAULT rows are Q-WR-1's, read as D167 add. 1
   rules it (A7: "2+ terms" means MEMBERS):
   - D1 (one member, not a VM attempt seek → the libc row);
   - `[rev3 A5]` D1c (no span 0, one context byte, i.e. MLINE → the libc back row);
   - `[rev3 A7, A17]` D1w (one member anywhere else → WALK: today's VM-hat rule, and
     `fd-d1`'s OFF arm);
   - ~~`[rev3 C3]` R7 (LINER V1) only where the cover's shape has a measured
     `kit.beta.V1` key, else R7w (WALK, today's form).~~ `[rev4.1]` R7 (LINER V1) where
     the cover has at most 2 TERMS; R7w (WALK, today's form) at 3 or more (Q-R17P-26,
     answered). The cover's term count is a compile-time fact, so no shape needs its own
     key first.

   Every default row is labelled UNMEASURED-DEFAULT in its `basis` column. PRES's
   default is KEEP (Q-WR-9). NONE is a row that never applies where span 0 is REQUIRED
   (the VM hat, the no-DFA VM route).

   `[rev4]` **After grid2: 21 rows designed, 15 FIND and 6 PRES; 17 built by B4.**
   - R1 is DELETED: there is no crossover interval, because V1 beats the walk at every
     N ≥ 8 (M9 contradicted).
   - R0 is RETIRED: under the slope token its class key never holds, and ~~R7's
     per-shape keys already send the losing r2 shapes to R7w~~ `[rev4.1]` R7's term-count
     rule sends every cover of 3 or more terms (the losing r2 shapes among them) to R7w.
   - F0 and F1 are NOT BUILT (D77): F0 has no customer and F1 has nothing to displace.
     Each stays designed with its trigger.
   - ~~F2 gains a density condition (Q-R17P-27). P1 waits on Q-R17P-28.~~ `[rev4.1]` F2
     (the VM hat at \|S\| = 1) moves to V1 at B5 with NO density condition; its g = 2 cells
     are named expected losses (Q-R17P-27, answered YES). P1 is recorded as fired on the
     letter and NOT built (Q-R17P-28, the kit manager's call).
   - The default when landing predictability is unknown is V1, not the walk (D169, §1.9).

   The rows B4 builds are §1.3a.
3. **The step plan (§3).** Nine build steps B0-B8 plus the evaluator's E-steps,
   in one order. `[rev3 B3, A9]` "Zero-mover" means ARTIFACT bytes (emit_sweep's
   streams 1-4) at SIMD-off AND SIMD-on (`[rev3 B1]` lane sweeparm's `-fmemfn-simd`
   arm, S981) and under `-fcomments` (`[rev3 B2]` sweeparm's arm, S982); the listing
   streams (5 `dumps`, 6 `facts`) move only by a DECLARED delta, checked both ways.

   | step | what | zero-mover? (artifacts) | pcrec abi |
   |---|---|---|---|
   | B0 | port R17-a's seam to main | yes, proven by B0's own run on main (`[rev3 B12]`) | none |
   | B1 | ST1 + R-19 + R-20 (kit half) + E3: facts, the define-time QUERY (`[rev3 A4]`), table, pick function, trace-only shadow | yes (nothing routed); a DECLARED `--list-axes` delta | none |
   | B2 | ST2: one-byte FIND rows routed; pcrec's readers switched to the query | yes (the default rows ARE today's rule) | none |
   | (main) | E-1 = window_contract S1, main's own step and abi event (`[rev3 B10, A15]`) | — | main's |
   | B3a/B3b | ST3: presence + handoff merged (B3a shadow, B3b routed), against main-after-E-1 | yes (five priced picks ported verbatim under a shadow); B3b a DECLARED registry delta | none |
   | — | **first delivery COMPLETE**; then grid2 → E4b → E5-E8 judge → LOCKDOWN | | |
   | B4 | R17-b′'s set-site ROUTING (V1 on measured shapes, ~~R0 WALK~~ `[rev4]` R7w WALK on the measured losing shapes, NO dispatch; `[rev4.1]` by TERM COUNT: V1 at ≤ 2 terms, WALK at ≥ 3), M0's stamp, the kit size rung | NO: the one censused mover | ONE event, ~~78~~ `[rev4]` 81 (main today) → next |
   | B5 | ST4: measured rows (~~libc, NONE,~~ the VM hat's \|S\| = 1, ~~priced pre-scan~~), one census each `[rev4]` (F0/F1 not built, §1.3a; ~~P1 per Q-R17P-28~~) `[rev4.1]` F2 is built here with no density condition (Q-R17P-27, YES); P1 is NOT built (Q-R17P-28: fired on the letter, never fires on a default compile, D77) | NO | one per default-moving row |
   | B6 | the W64 SIMD rows (CANDIDATE) | SIMD-off yes | none |
   | B7 | ST5: the libc class deny + three libc-free rows | yes at default | none |
   | B8 | ST6: the N-dispatch rows, if not already paid at B4 `[rev4]` (B4 pays none: T2/T3 fail on every twin, §2.5; B8 waits for [REGIME-TWIN]) | NO | one |

   `[rev3 B10]` **The KIT's steps carry no pcrec abi event through B3b; E-1 is main's**,
   placed between B2 and B3a (D167). The first delivery's window therefore contains one
   pcrec abi event, main's own. R17-b″ (D165 iterator) follows as B9 (§6), after E0,
   `findall_iter.md`'s revision, its panel and I1 (`[rev3 A6]`).
4. **The contract (§4).** One `mf_site` per search-entry activation holds span 0
   (`pred`) and PRESENCE spans (`preds[]`, a new span class with `omin` and no `omax`,
   C-1/C-2). Presence binds at RANGE level, once per activation: a REQUIRED presence
   span absent from `[start + omin, n)` (`omin` measured from the match start, `start`
   R-19's hook; `[rev3 A20]` an amendment to PR-6/C-1 main is asked for) makes the
   stream EMPTY, and EMPTY = NOMATCH, decided before the first element (C-3, G-1, G-2).
   An unconstrained reply is the range `[lo, n)`, legal iff span 0 is OPTIONAL or absent
   (G-4); the per-candidate cut `hi' = p − omin + head_max` is a PERMISSION exercised only
   by the iterator (Q-WR-6). `[rev3 A4]` **The read-back is a DEFINE-TIME QUERY**,
   `mf_ask`, made BEFORE row selection: pcrec hands it the site's facts and gets back the
   form CLASS (`exists`, `proven0`, `libc_free`, `includes`), never the form (D157); each
   pcrec reader maps to one class fact, and the K admission reads none (`[rev3 A11]`).
   The K65 obligation is a per-consumer table keyed by `need` (§4.6). The set arrives on
   `mf_art_begin` (`mf_measures`, R-MS1) and `consulted` comes back from `mf_art_end`
   (R-MS2); `[rev3]` per the E-1 agreement, B1 also declares `mf_analysis` on
   `mf_art_begin` (NULL-tolerant, read by no kit row before B3a), which main's E-1 fills
   after B2 merges with no kit edit.
5. **Measurements (§5).** 24 quantity families `[rev3 A6: M24]` keyed (owner.quantity,
   form, site kind, shape), relative to u = β_walk. grid1 holds 15 (M1-M15). ABSENT:
   the three dispatch charges (M16-M18), the one-byte libc and libc-free costs and their
   crossover (M19-M21), NONE's effort (M22), the pre-scan gate's quantities (M23) and the
   shared-body mode branch (M24). Each has a method card row under `kit-grid@2` (R-MS5).
   `[rev3 C4, C13]` The null floor is per REGIME (`eps.<subject>.<lenclass>`), not one
   pooled 3.1%.

   `[rev4]` **grid2 has RUN and has been read.** It measured M16-M23 (twin charges, the
   one-byte arms, NONE, the pre-scan probe) and re-timed M1-M15 on streamed subjects.
   M24 is the only family still ABSENT. Two of rev 3's constants are CONTRADICTED:
   - M9: no crossover was found;
   - M15: g\* is a predictability threshold, not a gap threshold.

   §5.2a gives each family's measured value with its source.
6. **zen4-grid2 (§5.4): ONE slot, ≈ 91 min required at 3.4 launches, ≈ 129 min at 5
   launches** `[rev3 C7]` (rev 2's required items: 87-124 min with the gate, C7's
   "88-113"; revision 3 adds 67 group-arms, +3.6 / +5.3 min), plus ~8-9 min optional and
   the quiet-gate waits. Revision 3 adds `[rev3 C3]` three
   cover shapes for R7's gate, `[rev3 C5]` N = 33..46 for the dispatch literal,
   `[rev3 A7]` the VM_ATTEMPT one-byte cell for F2, and `[rev3 C8]` NONE as an extra
   arm inside item 3's groups (item 4 deleted). Perf is never required (D166 add. 1);
   without counters every script prints the paranoid SUGGESTION (add. 1.1) and skips
   loudly. D167 ruled Q-R17P-9 (B): one streamed condition gives the constants and R_in.
   `[rev4]` It ran 3 launches (+2 by the rerun rules), 61 min required and 66.5 min with
   the optional passes. The gate was green, there were 0 answer mismatches, and one
   contaminated visit was re-timed clean by the harness's own requeue (grid2read §1-§2).
   A 2-minute re-time of two load-suspect cells is OWED (§3.1a).
7. **R17-b″'s seam (§6).** H rows (R3a, R3b, R4 and R8 under H), the form A3, the
   presence carry and Q-WR-6's cut-off as a permission. `[rev3 A6]` The find body's mode
   M is a PARAMETER (`MF_BODY_PARAM`, findall_iter §4.2). `[rev3 A10]` The carry is one
   position per REQUIRED span or per stream of a multi-stream form (8 B × k, declared per
   form); K5's 16 B pair-hit row retires only when a kit form is proven single-pass over
   its spans, and S is derived from the declared carried positions at the iterator's abi
   event ("S = 48 B" is withdrawn, D167 add. 1).
8. **Questions (§7).** Rev 1's Q-R17P-1..8 and rev 2's Q-R17P-9..14 are CLOSED with their
   rulings (D167). `[rev3]` Eleven new ones, Q-R17P-15..25, each with a recommendation;
   Q-R17P-15 (the define-time query's contract) is the one B2 waits on.
   `[rev4]` Three more, Q-R17P-26..28 (§7.3), each in plain words with a leaning. None of
   them re-asks what D169 answers. `[rev4.1]` All three are ANSWERED (Frank on 26 and 27,
   the kit manager on 28); each is marked in §7.3 with its answer and source.

---

## R4.1. What revision 4.1 changed, by section `[rev4.1]`

Sources: Q-R17P-26 and Q-R17P-27 are Frank's answers of 2026-10-21 (the journal entry of
that date and the two notices at the end of `memfn/docs/responses.md`); Q-R17P-28 is the
kit manager's call, recorded in the same entry. grid2read = `docs/dev/lanes/
grid2read_report.md`. Every number is rev 4's, unchanged; no new measurement.

| change | rev 4 | rev 4.1 | where |
|---|---|---|---|
| **R7 keys on TERM COUNT** (Q-R17P-26) | fires where the cover's shape has a measured saving key > eps; an unmeasured shape does not hold | fires where the cover has **at most 2 terms** (range + eq + cube terms, a compile-time fact the kit builds). The threshold is the derived key `kit.terms.V1max` = 2 (§5.2), drawn from the nine per-shape saving keys' signs; R7 reads that key, not the nine | §1.3a row 12, §1.3 row 16 note, §5.2 (the key), §5.2a M1-M5, §8.3 |
| **R7w loses its "no key" reason** | reached for two reasons: measured-loss and unmeasured | reached for ONE: the cover has **3 or more terms** (the three measured losers are 3, 4 and 4 terms; an untimed combination routes by its count) | §1.3a row 13 and notes, §1.3 row 17 note |
| §1.9 default table | a shape with NO measured key → WALK until Q-R17P-26 is ruled | the row is replaced: such a shape routes by its term count, like every other | §1.9 table |
| the 54 no-key sites | stay on R7w, pending Q-R17P-26 | route by term count. Their split between V1 and the walk is OWED to the REGENERATED mover manifest (§3.1a item 4); this revision does not compute it | §3.5, §9.2a, §3.1a item 4 |
| B4's acceptance | confirms the six winning shapes | also **confirms the rule on the shapes it moves**: a shape whose measured sign contradicts its term count is a FINDING, not a default | §9.2 item 2, §9.4 |
| **F2 defaults to V1 at B5** (Q-R17P-27: YES) | a density condition, still open | NO density condition. F2 fires on a default compile at **B5** (not B4, so B4 stays one change). Its g = 2 cells (V1 +38.3% slower) are named EXPECTED losses up front | §1.3a row 1, §1.9 table, §3.1 B5 row, §3.1a item 6, §3.4 floors, §9.2a |
| **P1 recorded, not built** (Q-R17P-28) | build OPEN | the trigger FIRED on the letter; P1 is NOT built (it never fires on a default compile; D77) | §1.4, §3.1 B5 item (d), §3.4 floors, §3.1 B5 row |
| §7.3 | three open questions | each marked ANSWERED with its answer and source; question text left in place | §7.3 |
| the row-edit log | rev 4 entries | rev 4.1 entries appended | `memfn/docs/finder_history.md`, §1.8 |

Unchanged by revision 4.1: every other row of §1.3a and §1.4, the contract (§4), the step
plan's order, the gates of §3.1a (D163 add. 8 MET; E8 and M0 owed) and the D169 text
itself. The rule is the OFF-layer one: the term count is the V1 form's own cost structure
(grid2 timed V1 against the walk). Whether the W64 form (B6) has the same break is B6's
measurement (§3.4).

---

## R4. What revision 4 changed, by row and source `[rev4]`

Sources: grid2read = `docs/dev/lanes/grid2read_report.md` (section numbers are that
report's); its keys = `r17b_prime/grid2read/keys.tsv` (270 PROPOSED rows in the finder's
spellings, not yet a set); D169 = Frank's 2026-10-20 ruling (main's decision log, quoted
in §1.9). Every number is Zen 4 7700X, gcc 15.2, streamed subjects, KIT tier
(D144 add. 4: the official verdict stays a bench run).

| row / item | rev 3 | rev 4 | source | where |
|---|---|---|---|---|
| **default under unknown predictability** | not stated; rev 3's routed set rows fell to the walk wherever a key was missing or a gap row fired | **V1** wherever no MEASURED row keeps the walk. ~~The one case the ruling does not settle is a cover SHAPE with no measured cost; it is Q-R17P-26, and until it is ruled that shape stays on R7w~~ `[rev4.1]` A cover shape with no timing routes by its TERM COUNT (Q-R17P-26, answered): V1 at ≤ 2 terms, the walk at ≥ 3 | D169; grid2read §3.5 and summary items 5-6; `[rev4.1]` Frank 2026-10-21 | §1.9 |
| R0 (≥ 2 RANGE terms → WALK) | routed at B4 on `kit.saving.V1.WALK.r2` ≤ eps | **RETIRED**. The class key is a MAX (+0.0121, set by (2,0,0)) and never ≤ `kit.eps.streamed.slope` (0.113%). The three losing r2 shapes ((2,0,1) −13.3%, (3,1,0) −41.3%, (3,0,1) −46.4%) reach WALK through ~~R7's own per-shape keys and~~ R7w `[rev4.1]` (their covers have 3, 4 and 4 terms, so R7's term-count rule sends them there). Its deny `fd-r0` retires with it | grid2read §3.2, §6 (R0 row), §7 item 2 | §1.3a, §3.4 |
| R7 (LINER) | fires where the shape's saving key is measured and > eps | ~~the same rule, with grid2's nine shape keys.~~ `[rev4.1]` Now keyed on the cover's TERM COUNT (≤ 2 → V1; §R4.1). The nine keys are the evidence: the rule fires, and the keys agree, on (1,0,0) +42.0%, (2,0,0) +1.2%, (0,1,1) +26.8%, (0,2,0) +39.0%, (0,0,1) +54.8% and (1,1,0) +21.1% (1-2 terms each). It does not fire on the three losing shapes (3, 4 and 4 terms). The (2,0,1) and (3,1,0) values are PROVISIONAL (from load-suspect cells), but their signs are not in doubt | grid2read §3.2 (an. 4, 4b, 4c), §6 | §1.3a |
| R7 at W16/W32 (B6) | W64 where built | W64 from N = 64 (the block). Below 64 B, V1 is the best form at both layers | grid2read §3.3, §6 (R7 at W16/W32) | §1.3a |
| R1 (short N → WALK) | an N-interval below `kit.xover.V1.WALK` (36 B, INTERPOLATED) | **DELETED**: V1 beats the walk at every measured N, from 8 B (−0.18 ns at 4.5× floor) to 1 MiB. N\* = 8 is the lowest measured point and NOT LOCATED. `kit.xover.V1.WALK.DFA_SCAN` = 8 B is recorded as an UPPER bound, and no row reads it | grid2read §3.3, §4 A2, §6 (R1 row) | §1.3a, §2.6 |
| R2 (W16/W32, N < block → V1) | `unpaid` = WALK | `unpaid` = UNSTATED (the row is dropped and its interval falls to the W64 terminal). WALK is the WORST form below the block: walk − V1 = +4.98 / +6.60 ns at N = 48 / 63. T1 fails at N = 8 and T2/T3 fail, so no B6 dispatch either until [REGIME-TWIN] | grid2read §3.3, §4 A9, §5, §6 (R2 row) | §1.3a, §2.5 |
| R5 (E measured ∧ g < g\* → WALK) | gap comparator on `kit.gstar` | its comparator becomes a STATED LANDING REGIME: E at MEASURED provenance says the landings are REGULAR, or the caller states it. g\* is not a gap threshold. On unpredictable landings V1 wins from g = 4. On regular landings V1 loses at g = 2 (+14.9%) and g = 8 (+34.9%) while the walk is cheap. The `kit.gstar` keys are kept with `u-shape` provenance, and no row reads them | grid2read §3.5, §4 A3, §6 (R5 row); D169 | §1.3a, §1.9 |
| R8 (B6: N ≥ L\* ∧ E.g ≥ g8 → W64) | two comparators | the E.g comparator is dropped: W64 beats V1 at every tested g, so g8 < 2 B is not located. `kit.xover.W64.WALK` = 64 B. At W16/W32 R8 then coincides with R7's W64 terminal; B6 decides whether to retire it | grid2read §3.5 (an. 6c2), §6 (R8 row) | §1.3a |
| D1 / D1c (one byte → LIBC) | UNMEASURED-DEFAULT | stands, now MEASURED on its side: LIBC is best-or-tied on 8-9 of 10 cells of every kind. Its regret at g = 2 is +69..+208%. `kit.xover.LIBC.WALK` 4.1-6.1 B (LOW confidence) | grid2read §3.7, §4 A10, §6 | §1.3a |
| D1w (VM hat \|S\| = 1 → WALK) | until F2 | stands until F2 (D169 names it) | grid2read §6 (D1w row); D169 | §1.3a, §1.9 |
| F0 (NONE) | built at B5 | **NOT BUILT** (D77). NONE never beats the walk beyond the floor except `o-bnd` at g = 2 (−7.0%), and it loses +185..+497% at g ≥ 32. `kit.gnone` = −1 (never) on three kinds, 2 B on DFA_SCAN.bounded. Trigger: a measured cell where NONE beats the pick at a gap a real workload has | grid2read §3.7, §4 A12, §6 (F0 row) | §1.3a |
| F1 (a measured libc-free row displacing D1) | built at B5 | **NOT BUILT** (D77). `kit.dom.<f>.LIBC.<kind>` = 0 for every libc-free form and kind: nothing displaces D1. Trigger: a kit form whose `dom` key becomes 1 | grid2read §3.7, §6 (F1 row) | §1.3a |
| F2 (VM hat \|S\| = 1 → V1) | saving > eps | the saving is +0.515, but V1 loses +38.3% at g = 2 (crossing ~4 B, INTERPOLATED(2, 8)). ~~The row needs a density condition: Q-R17P-27~~ `[rev4.1]` NO density condition: F2 defaults to V1 at B5, with the g = 2 cells named expected losses (Q-R17P-27, YES) | grid2read §3.7 (an. 8b), §6 (F2 row), §7 item 3; `[rev4.1]` Frank 2026-10-21 | §1.3a, §7.3 |
| P1 (priced pre-scan) | waits for Q-WR-9's trigger | the trigger FIRES ON THE LETTER: KEEP loses 1.47 / 1.54 ns (3.4-3.8%) on two TUG g8 early cells, and the same pre-check wins ×49..×112 on absent cells. ~~Whether to build it is Q-R17P-28~~ `[rev4.1]` Recorded as fired on the letter and NOT built (Q-R17P-28, the kit manager's call) | grid2read §3.8, §4 A13, §6 (P1 row) | §1.4, §7.3 |
| pay rule (§2.5) | T1-T3 "may pass at B4" | **measured: T2 and T3 FAIL on every twin; T1 holds for R2 only above N = 8.** B4 ships NO dispatch, and B8 waits for [REGIME-TWIN] | grid2read §3.6, §5 | §2.5 |
| eps token | 0.173% (grid1) | `kit.eps.streamed.slope` = 0.113%; the slope's own noise is 0.247% p90 | grid2read §3.1 | §5.2a |
| B4's gates | D163 add. 8, E8, M0 | D163 add. 8 MET (E1 on main); E8 and M0 still owed; the OWED re-time and attribution items added | decisions D163 add. 8, D169; plan [ENTRY-TABLE], [MEASURE-SET], [REGIME-EVAL] | §3.1a |
| B4's acceptance | predictions vs the walk | adds a pre-registered EXPECTED-LOSS list (regular landings), named before any timing | D169 | §9.2a |

Unchanged by revision 4: D2, the whole PRES slot except P1's status, the contract (§4),
the step plan's order, B0-B3b (all routed, zero-mover), and R3a/R3b/R4 (B9). Every row
edit above is logged in `memfn/docs/finder_history.md` in this commit (§1.8).

---

## R2. What revision 2 changed, by input `[rev2]`

| input | what it changed | where |
|---|---|---|
| main is the baseline (Q-WR-10) | R17-a and R17-b are PORTED steps (B0, B4), not presumed; MF_SITE_ABI renumbered from main's 10 | §3 |
| D161 add. 14 + clarification | scope adds the one-byte stops, MLINE, presence and handoff; ONE window request; EMPTY = NOMATCH; the K65 obligation | §1.1, §4 |
| D161 add. 15 (Q-WR-1/2/3/6/9) | default rows D1/R7; MLINE in scope, no NONE until measured; D158 single rule with the ST3 no-move posture; the cut-off as a permission; pre-scan default KEEP | §1.3, §1.4, §4.6, §6 |
| D161 add. 11/12/13 | one table over (stop, form) with slots; generic class only at M2; row edits free until lockdown, lockdown = B4 | §1, §3.3 |
| D161 add. 8/10 | proven facts as the read-back channel; verify/proof only on EXACT spans; rows that change a proven fact decide once per site, never per layer | §1.5, §4.5 |
| D166 + add. 1/1.1/2 | every threshold a set reference; latest set until M2; stale defaults carried; perf optional and the paranoid suggestion | §5 |
| R-19 | `mf_site.body`, the START hook (all FIND storage points and the PRE composite's entry) | §4.2 |
| R-20 (R-MS1..5) | `mf_measures` in, `consulted` out, `mf_form_hash`, the reader declarations (with the `--emit-facts` section `memfn`), method cards `kit-grid@N`; `--list-finder` WITHDRAWN | §4.7, §1.7, §5 |
| R-21 (PR-1..11, ST1-ST6, S964-S980) | every PR item placed in a step; the step plan; sabotage remapped | §3, §8.3 |
| winreq KW-1..13, C-1..16 | rows (KW-1/2/13), contract (C-items cited per piece) | §1, §4 |
| sbscope / pcscope | the consumer table; witnesses W1-W4 as sabotage witnesses; G-1..G-5; census | §4.6, §8.3 |
| regime_eval rev 2.2 | E3 = B1's table + denies + shadow; E4 agreement check; grid2's streamed fit cells; routing only after PASS (Q-REVAL-11) | §3, §5.4 |
| regime_tables rev 0.5 | R8 (needs E), R3 PROVISIONAL, A = set id and I = ISA as separate keys | §1.3 |
| finder_history.md | the table's row edits; this revision's edits logged there at build | §1.8 |
| measure_sets rev 2.1 | §1's TSV shape for the set; §2.4 staleness; §3.5 stamp spelling (`""` / `id@rev:digest16`); §4 channel; §10.1 M0 riding R17-b′ | §4.7, §5 |
| findall_iter.md | S is derived by a row sum (56 B today); the kit's row 32 → 40 | §6 |
| main's answers to rev 1 | Q-R17P-1..8 closed | §7.1 |

Rev 1 sections that SURVIVE with edits: the C shape (§1.2), the dispatch text and the
pay rule (§2), the size twins (§3.6), the G2 families (§8.2), acceptance (§9).
WITHDRAWN: `--list-finder` (R-MS4's listing replaces it), the `"none"` stamp spelling
(measure_sets §3.5), "the first set needs grid2 before anything ships" (the first
delivery reads no set, §3.2), the `FS_SPAN0`-only stop (the PRES slot adds presence
spans), SB1-SB12 as numbered in rev 1 (remapped to S911-S922 in §8.3).

---

## R3. What revision 3 changed, by finding id `[rev3]`

The panel record is `docs/dev/reviews/2026-10-16-r1-memfn-r17bp.md` (70 ids; the kit
manager's dispositions are binding). Every id below is applied; none is rejected. Rulings
that bind this revision: D167 (build GO; grid2 (B); Q-R17P-10..14) and D167 addendum 1
(A7 MEMBERS; A10 K5's retirement amended; A11 the landmark admission's input as a fact;
A4 noted for review here).

| id | what changed | where |
|---|---|---|
| A1 | the storage point is above the PRE use, START = `search_from` for the activation, the handoff's `c − K` a later use's argument; stated per emitter | §2.1 |
| A2 | `attempt_entry` is the third caller; ATTEMPT_PRED widened and renamed DFA_ATTEMPT (the DFA attempt loop: MLINE's seek and the attempt entry's presence); R-21 PR-3 amendment asked | §1.1, §2.1, §4.3, §4.6, Q-R17P-16 |
| A3 | a VM hybrid holds two sites: presence-only in `_search_run`, find-only in `_prefilter`; "decided first" across the call boundary stated | §1.1, §2.1, §4.4 |
| A4 | the read-back is the define-time query `mf_ask` (facts in, form CLASS out), made before row selection, landing at B1, read from B2 | §4.5, §3.1, §4.9, Q-R17P-15 |
| A5 | MLINE has no span 0; its stop is a one-byte CONTEXT predicate served by row D1c; D161 add. 7 kept | §1.3, §4.1, §4.6 |
| A6 | `MF_BODY_PARAM`; an M-reading row on a shared find part prices a runtime compare (M24); F4 rewritten; B9's dependencies E0 → findall_iter revision → its panel → I1 | §2.4, §5.2, §6, §3.1, §11 |
| A7 | RULED (D167 add. 1): MEMBERS. The VM hat at \|S\| = 1 stays WALK (D1w); its move is the measured B5 row F2 fed by grid2's one-byte cells (VM_ATTEMPT added) | §1.3, §3.1, §3.5, §5.4 |
| A8 | DELEG_SITES, C10's fixtures, C17's site manifest and MF_VOCAB listed as main-side requests at B2, B3a, B3b | §3.4, Q-R17P-18 |
| A9 | no `--emit-facts` section at B1 (R-20 schedules it at M0, B4); B1's `--list-axes` rows are a declared registry event | §1.7, §3.1, §3.4, §8.1 |
| A10 | RULED (D167 add. 1): one carried position per REQUIRED span or stream; K5 retires on a proven single-pass form; S derived, "48 B" withdrawn | §6, §7.1 |
| A11 | RULED (D167 add. 1): the admission reads the start set's prior mass, h and K; no read-back; a D157 exception until restated (zero movers, main-side, at B2) | §1.4, §4.5, §3.1, §7.1 |
| A12 | `S693_abi_not_bumped.sh:51` and match_api's K80 `#define PCREC_RX_ABI_H 78` added to the readers | §3.4 |
| A13 | `docs/design/start_table/sabotage_anchors.py` | §8.3 |
| A14 | the B4 tuning hunk names "a NEW section for bit 55 (its number given at B4)" and "§3's dial table", not a section number that does not exist yet | §3.4 |
| A15 | MF_SITE_ABI numbered relatively; E-1 placed in the plan as main's event; B3a/B3b zero-mover against main-after-E-1 | §0, §3.1, §4.9 |
| A16 | the ported sabotage ids listed exactly, S825 excluded | §8.3 |
| A17 | `no-fd-d1` renders WALK through D1w from B2 | §1.3, §3.4 |
| A18 | REQ_WHY reads pcrec's withholding reason first, then the link attributes; `order` expresses LEAD | §4.5 |
| A19 | `exists` stated as dependent on `proven0` (exists = 0 ⇒ `proven0` all-ones), kept as the class bit D167 add. 1's A4 note names, and self-checked | §4.5, Q-R17P-25 |
| A20 | `omin` from the match start is a question to main (PR-6, C-1), not a silent refinement | §4.1, Q-R17P-17 |
| A21 | R-19's builder list (`req_site_define`, MLINE, `attempt_entry`) is a question to main | §2.4, §11 F19, Q-R17P-16 |
| A22 | `site_kind` (stated, UNSTATED zero) separate from the row's applicability bitset; `FK_ANY` gone | §1.2 |
| A23 | relayed to main: requests.md R-21's "(pending)" line is stale | the record, the report |
| B1 | THE SIMD-on instrument is lane sweeparm's `-fmemfn-simd` arm (S981), delivered with B0 | §0, §3.1, §8.1 |
| B2 | THE `-fcomments` instrument is sweeparm's arm (S982); Q-R17P-12's "B2 zero-mover on every arm" rests on it | §3.1, §8.1, §7.1 |
| B3 | per step a DECLARED delta for streams 5 and 6, checked both ways; zero-mover means artifacts | §0, §3.1, §8.1 |
| B4 | the `cand_rows` readers (test-cand-oracle, inventory_check, the startset readers) per step; a declared trace delta | §3.4, §8.1 |
| B5 | the reverse plant (SN-1); a pcrec-side routed-record count with floors; disagreement witnesses per routed group | §1.6, §8.1, §8.3 |
| B6 | the shadow runs under the interim set and the synthetic sets; interval literals recorded; B1's picks are B4's committed predicted-mover manifest; the denominator from emitted C; a comparator plant (SN-6) | §1.6, §3.1, §3.2, §8.3 |
| B7 | `fd_rows[]` in rows.tsv / row_floors.tsv at B1; each deny classed DIFFER / ASSERT_ZERO / REFUSES; `run_axes.sh`'s sweep a request to main | §3.4, §8.2, Q-R17P-22 |
| B8 | resolved by D167 (Q-R17P-13) | §3.3, §7.1 |
| B9 | LOCKDOWN = a committed digest of `fd_rows[]`'s listing plus an edit check; rows lock when routed; finder_history logs edits at commit time (rev 2's and rev 3's logged in this commit) | §1.8, §3.3, `memfn/docs/finder_history.md` |
| B10 | "the KIT's steps carry no pcrec abi event; E-1 is main's" | §0, §3.1, §4.9 |
| B11 | S916's witness (1,1,0) with a set holding both shapes; S966 → B4; S968 UNREACHED until B5; S914/S915 UNREACHED until `__walk` is emitted; S920's detector an independent reader of the activation origin | §8.3 |
| B12 | "port, then gate": B0's claim is its own run on main | §3.1 |
| B13 | emit_sweep's DIFFER_PINS maintained per step; `PCREC_NO_REQ_SET_LEAD`'s fate asked | §3.4, Q-R17P-19 |
| B14 | R1/R2 applicability is row data (terminal ∈ {V1, W64}); planted (SN-5) | §1.3, §8.3 |
| B15 | a committed normalizer; "every kit deny at once == main modulo it" a B4 gate | §8.1 |
| B16 | B4's pre-move census is `r17b_movers.py`'s independent cover search; R0's population is an upper bound | §3.5, §8.3 |
| B17 | rwquest and the bench patterns in every B2/B3b/B4 sweep; `run_longprefix_sweep.sh` and `run_prefix_invariance.sh` | §8.1 |
| C1 | as B14; a synthetic set holding every derivable `xover` key at B4; the converter's derived-card list named | §1.3, §5.2, §8.1 |
| C2 | the `basis` column, the table self-check, a per-site default count in the facts section, a plant (SN-4) | §1.2-§1.4, §4.7, §8.3 |
| C3 | R7 gated on its shape's `kit.beta.V1` key, R7w (WALK) the fallback; grid2 item 3a adds three cover shapes | §1.3, §5.4 |
| C4 | the null floor per regime; T1-T3 as upper-bound tests in absolute units against the cell's own A/A | §2.5, §5.2 |
| C5 | grid2 item 2a adds N = 33..46; the literal is derived on the measured staircase or labelled INTERPOLATED | §2.6, §5.4 |
| C6 | predictions restated against MAIN's walk on named grid2 groups; bullet 3 corrected; §9.4 gains a floor and the Zen 1 bench regression | §9.2-§9.4 |
| C7 | 3.4 to 5 launches stated; a cross-launch spread trigger | §5.4 |
| C8 | NONE an extra arm inside item 3's groups; g_none INTERPOLATED; DFA_ATTEMPT (MLINE) NONE evidence-only | §5.4 |
| C9 | `cdisp_*` cards keyed `kind;layer;nforms` | §5.2 |
| C10 | moot: D167 ruled (B); in-sample by design stated | §5.4, §7.1 |
| C11 | the PRES constants carry `basis`; the B2/B3b gate also runs under the synthetic sets through the B1 lever | §1.4, §3.2, §8.1 |
| C12 | stated; a second official set waits for M1 (a question to main) | §5.5, Q-R17P-24 |
| C13 | M6 says it is the pooled F1+F3 figure; the regime-split values listed | §5.2 |
| D1 | `fd_rows[]` is a `kit_table` over `kit_walk`; ROWCON H1's trigger cited | §1.2, §1.5 |
| D2 | one comparator plus derived keys | §1.2, §1.3 |
| D3 | PRES picks as chain-link attributes | §1.2, §1.4 |
| D4 | declared reads and the ask/define order; a B1 undeclared-read / cycle trap (SN-3) | §4.5, §3.4, §8.3 |
| D5 | the helpers are member 4 of D163 add. 7's family; their layout follows the dial position passed as a fact; nothing fixed here | §2.2, §3.6, Q-R17P-21 |
| D6 | a per-row `routed` bit replaces `fd_route[]` | §1.6 |
| D7 | rows lock when routed | §1.8, §3.3 |
| D8 | R5/R6 one row (the layer's LINER form), R7/R7s one row; one sentence on sub-block spans | §1.3 |
| D9 | ties decline; integer scaled arithmetic under a static bound | §2.5 |
| D10 | per-pick floors on non-trivial sites; a planted disagreement per pick | §3.1, §8.3 |
| D11 | `refuted_by` per row, in the listing | §1.2, §1.7 |
| U1-U6 | recorded with their triggers; U1 and U3 proposed to main as plan rows; nothing scheduled | §11 |

Also re-read against main (the brief): D163 add. 7 and `compound_entries.md` rev 2 (the
find part's layout is the L-table's, §2.2, §6); D165 add. 1-2 and `findall_iter.md` (M a
parameter, internal batching in `_in` memory, S from declared rows, §6); E-1 (§3.1, §4.7).

---

## 1. The table: scope and rows

### 1.1 Scope `[rev2]` `[rev3: A2, A3]`

The first delivery covers every site at which an artifact asks "where can the next match
START", and the presence pre-checks and handoffs that front such a site. On main
(abi 78, MF_SITE_ABI 10) these are three DELEG_SITES rows (`PF`, `MLINE`, `PRE`) at
five kinds of consumer. Populations are artifact counts (one artifact can be in several
classes), from sbscope §7.1 (main `711cf603a`, `--features all`, default flags) and
pcscope §7 (main `4e6464777`, trace build); re-counted at each step's census.

| group | today's selection (pcrec row → kit row on main) | DELEG | consumer kind (§4.3) | corpus / bench / rwquest |
|---|---|---|---|---|
| one-byte DFA prefilter | `memchr`, `memchr-bounded` → `pf_memchr`, `pf_memchr_bounded` | PF | DFA_SCAN | 581 / 35 / 16 (with the DFA hat's one-byte row) |
| one-byte DFA hat | `first-memchr-bounded` → `pf_memchr_bounded` + pcrec's re-seed | PF | DFA_HAT | (in the row above) |
| one-byte hybrid prefilter | the same rows inside a VM hybrid | PF | HYB_PF | 626 / 8 / 18 |
| set DFA prefilter / DFA hat | `byte-class[-bounded]`, `first-class-bounded` → `pf_walk[_bounded]` | PF | DFA_SCAN / DFA_HAT | 764 / 102 / 29 |
| set hybrid prefilter | the same, inside a hybrid | PF | HYB_PF | 241 / 16 / 8 |
| VM hat, any \|S\| | `first-class` → `pf_walk` (a table walk even at \|S\| = 1, Q-R5) | PF | VM_ATTEMPT | 257 / 17 / 5 (of which \|S\| = 1: 112 / 8 / 1) |
| MLINE | `pred-memchr` → `pf_memchr_back` (LOOP_EXIT `on_miss`); `[rev3 A5]` no span 0, one context byte | MLINE | DFA_ATTEMPT `[rev3]` | 52 / 2 / 23 |
| presence: one byte | REQ admission `emitted` → `precheck` | PRE | the route's (DFA_SCAN, HYB_PF, VM_ATTEMPT or `[rev3 A2]` DFA_ATTEMPT) | 292 corpus default (160 give-up-exposed) |
| `[rev3 A2]` presence at the DFA attempt entry | `pcrec_emit_req_byte_check`'s third caller, `attempt_entry` (ENG_ATTEMPT, guarded `cand_finish_of(cx) != CAND_ROUTE_VM`) | PRE | DFA_ATTEMPT | not counted by pcscope; owed at B2's census (a pcrec-side reader of emitted C) |
| presence: run window / K66 whole run | `emitted` (+ K66) → `precheck` | PRE | " | 52 (12) / 4 (4) |
| presence: K65 set rest | `emitted` on a no-DFA route → `precheck`'s `rq_set` loop | PRE | VM_ATTEMPT | 67 (67) |
| presence: set-leads | `set-leads` (bit 45) → `precheck`'s pair arm | PRE | " | 5 (5) |
| handoff FIRST (K82/L1) | `req-use` `handoff` → `precheck_assign` / `precheck_assign_byte` | PRE | the route's | 225 entry-only + 117 re-entered (corpus default); rwquest 56 |
| handoff NEXT re-entry | `cand_rows` NEXT `handoff` → the PRE site's second use | PRE | DFA_SCAN | (in the row above) |

Not in this delivery, each with its reason:
- **OFS / run-pinned FUNCs** (`offset-set*`, `run-pinned*`; 349 / 69 / 38 DFA): a span
  over positions 0..k is a multi-position span, R-18's first consumer. Their BODY is
  already the kit's (`fn_rows[]`) and stays so.
- **ADVANCE, VERIFY, MISMATCH sites** (STAY, EDGE, VMSPAN, VMSTRIDE, VMRUN, N7): not
  start searches.
- **The compound route** (`REQ_WHY "compound"`, 48 corpus): its parts are compiled by the
  unchanged pipeline and inherit whatever this delivery does to each part (D163); the
  controller itself holds no search site.
- **Withheld presence** (Q-WR-4, ruled): the G2-declined linear one-attempt (268 corpus
  default) and LOCATE `whole` (166 of G1's "dominators") get NO presence span; pcrec's
  sub-problem choice (D161 add. 4), zero-mover either way.

`[rev2]` **What "one window request" means here.** Today a search entry asks the kit
twice: once at the entry (the PRE site's pre-check) and once in the loop (the PF/VM-hat
FIND). Under D161 add. 14's clarification it asks ONCE: one `mf_site` whose span 0 is the
candidate set and whose PRESENCE spans are the necessary bytes and runs, with several USES
(the entry use decides presence and may yield the first candidate; each loop use yields
the next; the handoff's re-entry is a further use). A site with no candidate set (a
no-DFA VM route without a VM hat) is presence-only; a site with no presence span is
find-only.

`[rev3 A1, A3]` **"One" is per ACTIVATION of the function that holds the site.** The
storage point (`mf_locals`) is that function's entry, above the first use, and START is
`search_from` for the whole activation (§2.1 gives each emitter's point). Where the entry
and the find are two functions with two activations, they are two sites:
- **a VM hybrid**: the presence pre-check runs in `<prefix>_search_run`
  (`emit_vm.c` ~13214, "ABOVE ... the prefilter entry"), the HYB_PF FIND in the static
  `<prefix>_prefilter`, which every VM retry calls again at `attempt_position` (fresh
  locals, its own `search_from`). So the hybrid holds a PRESENCE-ONLY site in
  `_search_run` and a FIND-ONLY site in `_prefilter`. C-3's "decided first" holds across
  the call: the presence verdict is returned before `_search_run` makes its first
  `_prefilter` call (today's order). Q-WR-6's carry (§6) belongs to the presence site,
  whose activation spans the whole call.
- every other entry (the DFA body, the VM hat's `_search_run`, `attempt_entry`, the
  rev-end relocate path) is one function, so one site per activation.

rev 1's F1 ("one stateful site per search path") stays true: a presence-only site keeps
no FIND state in a one-shot call, and under the iterator its carried positions are
declared rows of S (D165 item 4's sum rule, §6).

### 1.2 The C shape (PROPOSED; `memfn/src/finder.c`, `finder.h`) `[rev2: slot, kinds, I]` `[rev3: D1, D2, D3, C2, D6, D11, A22]`

`[rev3 D1]` **`fd_rows[]` is a `kit_table`** (`memfn/src/kit.h`: `kit_table`,
`kit_walk`, `kit_ask`), the kit's fourth table on its ONE walk beside the composer's
arms, the run compare's rows and `fn_rows[]`; its slots are FIND (0) and PRES (1),
`fn_rows[]`'s BODY/PREFIX precedent. The walk asks each row, in table order and only in
the asked slot, the DENY (`opt`, `no-<opt>` in the site's `--memfn=` string), then the
CONTRACT (the gate over the row's `uses`/`serves`), then the row's own predicate; the
MF_TRACE records and the per-row reach counters (ROWCON N4) come with it. This adoption is
row_contracts.md §6 H1's trigger ("a real table, kit or pcrec, wants to adopt it"): the
table adopts the kit's existing walk, so no general engine is built for it (H1 stays filed
for pcrec's tables, U3).

**Applicability is the GATE's, not a column the predicate re-tests** (`[rev3 D1, A22]`).
Four facts become `fields.def` gate fields, each with an UNSTATED zero class and a closed
class set, and each row's contract states which classes it serves:
- `site_kind` (§4.3): the fact pcrec STATES on the site (PR-3); `[rev3 A22]` there is no
  "ANY" kind: a row serving every kind lists every kind's class;
- `need` (REQUIRED / OPTIONAL) of the span the row decides;
- `body` (ONESHOT / PARAM, §2.4);
- `layer` (OFF / W16 / W32): the variant the walk is evaluating, a fact of the walk's
  input, not of the site.

```c
/* The knowledge keys (regime_tables.md §2, rev 0.5). A row's `needs` names the
 * keys its comparator reads. KN_COMPILE keys are known when the site is asked;
 * KN_N at the storage point; KN_H only inside an iterator body (R17-b''). */
enum { KN_P = 1u << 0, KN_E = 1u << 1, KN_A = 1u << 2,   /* A: the measurement SET */
       KN_I = 1u << 3,                                     /* I: ISA availability    */
       KN_M = 1u << 4,       /* the body's mode: a constant per entry, or the
                                MF_BODY_PARAM parameter (§2.4) [rev3 A6]          */
       KN_N = 1u << 5, KN_H = 1u << 6 };
#define KN_COMPILE (KN_P | KN_E | KN_A | KN_I)

enum { FD_FIND = 0, FD_PRES = 1 };   /* the kit_table slots                       */

/* A reference into the active measurement set (measure_sets.md §1.3: owner.quantity
 * then dimension tokens in the card's order). Resolved by the kit, never by pcrec. */
typedef struct { const char *quantity; uint8_t form, other, kind; const char *shape; } fd_ref;

/* [rev3 D2] ONE comparator. lhs OP key, where lhs is a site or iterator quantity or a
 * DERIVED key (measure_sets §1.6's closed registry: `kit.saving.<f>.<g>.<shape>`,
 * `kit.dom.<f>.LIBC.<kind>`, `kit.xover.<f>.<g>.<kind>`). Every threshold is a key, so
 * R-MS4's SAFE direction attaches to the key, once. */
typedef enum { FL_NONE = 0,                     /* no comparison: a facts-only row */
               FL_E_G, FL_N, FL_H_SPAN, FL_H_POP, FL_KEY } fd_lhs;
typedef enum { FO_LT = 1, FO_LE, FO_GT, FO_GE, FO_IN } fd_op; /* FO_IN: [key, key2) */
typedef struct { fd_lhs lhs; fd_ref lkey; fd_op op; fd_ref key, key2; } fd_cmp;

/* Boolean site facts a row requires (all must hold); the comparators are the only
 * numeric conditions. A comparator whose key is ABSENT from the active set does not
 * hold (§1.5 rule 3), which is how a row is gated on a key's presence ([rev3 C3]). */
enum { SF_ONE_MEMBER   = 1u << 0,  /* the stop is one byte                          */
       SF_CONTEXT_STOP = 1u << 1,  /* no span 0; one context predicate (MLINE) [A5] */
       SF_SEEK_ROLE    = 1u << 2,  /* the span is span 0 of a VM_ATTEMPT site       */
       SF_RUN_TERM     = 1u << 3,  /* span 0 is a RUN term (a handoff landmark)     */
       SF_PROVEN       = 1u << 4,  /* span 0's proven fact covers this span (P2)    */
       SF_E_MEASURED   = 1u << 5,  /* the frequency kind is at MEASURED provenance  */
       SF_TERMINAL_FAST = 1u << 6, /* the terminal pick is V1 or W64 (R1/R2,
                                      [rev3 B14, C1]; [rev4] R2 only)               */
       SF_E_REGULAR    = 1u << 7   /* [rev4] PROPOSED: the analysis object states, at
                                      MEASURED provenance, that the landings are
                                      REGULAR (or the caller does): R5 (§1.3a)      */ };

/* Slot FIND: a form; the kit's names, never pcrec's (D157). 0 is UNSTATED and the
 * table self-check refuses it. */
typedef enum { FF_UNSTATED = 0, FF_NONE, FF_LIBC, FF_WALK, FF_V1, FF_W64,
               FF_RUN, FF_A3 } fd_form;

/* [rev3 D3] Slot PRES: a pick is a set of CHAIN-LINK attributes (R-18's vocabulary,
 * winreq C-8): no private pick enum. */
typedef struct {
    uint8_t verify;     /* 1: the link is verified over [start + omin, n) (KEEP)     */
    uint8_t proven_by;  /* 1: span 0's proof stands for the link, no test (DROP)     */
    uint8_t member;     /* 0: every member; else 1 + the chosen member (PICK)        */
    uint8_t order;      /* the chain-order key: lower is tested first (LEAD)         */
} fd_link;

/* [rev3 C2] Every row states its basis; 0 is refused by the self-check. */
typedef enum { FB_UNSTATED = 0, FB_MEASURED, FB_DERIVED, FB_UNMEASURED_DEFAULT } fd_basis;

typedef struct {
    const char *id;          /* "R1": listed; cited by `evidence` and the record     */
    int         slot;        /* FD_FIND or FD_PRES                                    */
    uint8_t     needs;       /* KN_*                                                  */
    uint8_t     facts;       /* SF_*, all required                                    */
    fd_cmp      cmp[2];      /* a conjunction; lhs FL_NONE ends it (R8 has two)       */
    fd_form     pick;        /* slot FIND                                             */
    fd_form     unpaid;      /* the pick when a dispatch cannot pay (§2.5); FF_UNSTATED
                                here means the row is dropped and its interval falls
                                through                                               */
    fd_link     link;        /* slot PRES                                             */
    uint8_t     routed;      /* [rev3 D6] 1 once the step that routes the row has
                                landed; deleted at B4 when every row is 1 (§1.6)      */
    const char *opt;         /* memfn/src/options.def name, or NULL                   */
    fd_basis    basis;       /* [rev3 C2] mandatory                                   */
    const char *evidence;    /* listing text                                          */
    const char *refuted_by;  /* [rev3 D11] listing text: the measurement that would
                                flip the row (regime_tables §3's column)              */
    const gate_contract *ct; /* the row's uses/serves over site_kind, need, body,
                                layer and the hooks it renders (ROWCON)               */
} fd_row;
```

Notes on the shape:
- It is the house first-match idiom, not a planner (rev 1, kept). R7 is ONE row
  `[rev3 D8]`: its pick is "the layer's LINER form" (V1 at OFF; W64 at W16/W32 where the
  form is built and I offers it); at a SIMD layer with no W64 form the row does not apply
  and the variant adds nothing (the floor rule). R5 is likewise one row over the layer's
  LINER form's `g*` (rev 2's R5/R6 pair).
- **The self-check** `[rev3 C2]` runs at kit build (a `_Static_assert` where C allows it,
  else a test in `make test-memfn`): every row states `basis`, a non-PRES row states
  `pick`, a row whose comparator reads no set key (FL_NONE, or a site-only lhs against a
  literal) is `FB_UNMEASURED_DEFAULT` or `FB_DERIVED`, never `FB_MEASURED`; a row whose
  key is a derived one is `FB_DERIVED`; the last row of each slot reads nothing.
- R-18's priced argmin over candidate CHAINS becomes a second evaluator over the same
  link attributes (U2), not a new condition kind.

### 1.3 Slot FIND: the rows `[rev2]` `[rev3: A5, A7, A17, B14, C1, C2, C3, D2, D8]`

`[rev4]` **This table is revision 3's record. §1.3a supersedes it for B4.** The rows
grid2 changed are struck through below (R0, R1, R2's `unpaid`, R5's and R8's
comparators, the build of F0 and F1). Every other cell stands and is restated in §1.3a.

Evaluated per site and per layer variant, first match (§1.5). Keys name the quantity ids
of §5.2 (`kit.<quantity>.<tokens>`, measure_sets §1.3); "derived" keys come from §5.2's
derivation rows. The kinds column is the row's gate contract over `site_kind` (§1.2).
"Routed at" = the step whose commit sets the row's `routed` bit (§1.6); "built" rows are
source from B1 unless marked.

| # | id | needs | layers | kinds | facts ∧ comparators | pick | unpaid | deny | basis | routed at |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ~~F0 `none`~~ `[rev4]` not built | P,E,A | all | DFA_SCAN, DFA_HAT, HYB_PF (DFA_ATTEMPT only once its M22 key exists, Q-WR-2) | span 0 `need` OPTIONAL (gate) ∧ E measured ∧ E.g < `kit.gnone.<kind>.<shape>` (M22) | NONE | — | `fd-none` (PAIR) | MEASURED | B5 (built at B5) |
| 2 | ~~F1 `libc-m`~~ `[rev4]` not built | P,A | all | all | one member ∧ not the seek role ∧ `kit.dom.<f>.LIBC.<kind>` ≥ 1 (derived from M19-M21) | that form | — | `fd-libc-m` | DERIVED | B5 (built at B5) |
| 3 | `[rev3 A7]` F2 `vm-hat-1b` `[rev4.1]` no density condition, §1.3a row 1 | P,A | off | VM_ATTEMPT | one member ∧ the seek role ∧ `kit.saving.V1.WALK.VM_ATTEMPT.(0,1,0)` > `kit.eps.<regime>` (derived from grid2 item 3's VM_ATTEMPT cells) | V1 | — | `fd-vm-hat-1b` | DERIVED | B5 (built at B5) |
| 4 | ~~R0~~ `[rev4]` retired | P,A | off | all | cover's shape class r2 (≥ 2 RANGE terms) ∧ `kit.saving.V1.WALK.r2` ≤ `kit.eps.<regime>` (derived from M2, M3, M6) | WALK | — | `fd-r0` | DERIVED | B4 |
| 5 | R5 `[rev3 D8: R5 ∪ R6]` | P,E,A | all | all | ~~E measured ∧ E.g < `kit.gstar.<LINER(layer)>.<kind>` (M15); FRAGILE at OFF~~ `[rev4]` a stated REGULAR landing regime (§1.3a) | WALK | — | `fd-r5` | MEASURED | B4 (reachable with a measured bundle) |
| 6 | R8 | P,N,M,E,A | w16,w32 | all | body ONESHOT (gate) ∧ E measured ∧ N ≥ `kit.lstar.W64.<kind>` ~~∧ E.g ≥ `kit.g8.W64.<kind>`~~ `[rev4]` (E.g dropped) (gridread §6.3 D2; regime_tables rev 0.5) | W64 | V1 | `fd-r8` | MEASURED | B6 |
| 7 | R3a | H | w16,w32 | all | iterator ∧ H.span < `kit.h3a` | WALK | — | `fd-r3a` (B9) | MEASURED, PROVISIONAL | B9 |
| 8 | R3b | H | w16,w32 | all | iterator ∧ H.span in [`kit.h3a`, `kit.h3b`) | A3 | — | `fd-r3b` (B9) | MEASURED, PROVISIONAL | B9 |
| 9 | R4 | H,P | all | all | iterator ∧ H.pop says g < `kit.gstar.<form>.<kind>` | WALK for that block | — | `fd-r4` (B9) | MEASURED | B9 |
| 10 | ~~R1~~ `[rev4]` deleted | P,M,N,A | all | all | body ONESHOT ∧ `[rev3 B14, C1]` the terminal pick is V1 or W64 ∧ N < `kit.xover.<t>.WALK.<kind>` (M9; t = the terminal) | WALK | — (row dropped) | `fd-ndisp` | DERIVED | B4 or B8 (needs M16-M18 to pay) |
| 11 | R2 | P,M,N,A | w16,w32 | all | body ONESHOT ∧ the terminal is W64 ∧ N < `kit.block.W64` (M11) | V1 | ~~WALK~~ `[rev4]` — (row dropped) | `fd-ndisp` | DERIVED | B6 + B8 |
| 12 | D1 `default-1b` | P | all | all | one member ∧ not the seek role (Q-WR-1: today's count rule) | LIBC (forward; bounded for `end_back` 1) | — | `fd-d1` | UNMEASURED-DEFAULT | B2 |
| 13 | `[rev3 A5]` D1c `context-1b` | P | all | DFA_ATTEMPT | no span 0 ∧ one context predicate of one byte (MLINE's `{\n}` at −1) | LIBC back (`pf_memchr_back`, LOOP_EXIT) | — | none (B7's `libc` class deny reaches it) | UNMEASURED-DEFAULT | B2 |
| 14 | `[rev3 A7, A17]` D1w `walk-1b` | P | all | every kind but DFA_ATTEMPT | one member | WALK (the table walk over the one-member table) | — | none | UNMEASURED-DEFAULT | B2 |
| 15 | D2 `run` | P | all | all | span 0 is a RUN term (a handoff landmark longer than one byte) | RUN (the nested `fn_rows[]` walk; its BODY/PREFIX rows and their denies unchanged) | — | none (the nested table's denies) | UNMEASURED-DEFAULT (today's rule) | B3b |
| 16 | R7 `liner` `[rev3 C3, D8]` `[rev4.1]` superseded: keyed on the cover's TERM COUNT, §1.3a row 12 | P,A (+I at w16/w32) | all | all | `kit.saving.<LINER(layer)>.WALK.<shape>` > `kit.eps.<regime>` (M3/M4/M5 → derived; an ABSENT key, i.e. an unmeasured shape, does not hold) | the layer's LINER form: V1 at OFF; W64 at W16/W32 where it is BUILT and I offers it | — | none (the FORM denies `pf-terms-mask` at B4, `pf-terms-w32`/`-w16` at B6) | DERIVED | B4 (W64: B6) |
| 17 | `[rev3 C3]` R7w `walk-default` `[rev4.1]` reached only at ≥ 3 terms, §1.3a row 13 | P | off | all | always | WALK (main's form) | — | none | UNMEASURED-DEFAULT | B4 |

Notes:
- **Built when** `[rev2]` `[rev3]` (`[rev4]`: F0 and F1 are NOT built, §1.3a): rows 4-17 are source from B1 (the evaluator judges
  them; E3 retires the Python mirror). F0, F1 and F2 are DESIGNED here and BUILT at B5,
  after lockdown, each as a formal row addition with its replay delta and mover census
  (D161 add. 13): grid2 measures their quantities (M19-M22 and item 3's VM_ATTEMPT cells),
  so if they were source at B4 they would fire under grid2's default set and fold their
  movers into B4's census (F21).
- **Order.** Rows needing only compile-time keys and true become the TERMINAL pick;
  N-rows above the terminal become emitted dispatch intervals (rev 1 §1.2, kept, §1.5).
  F0/F1/F2 sit first because, when their data exists, they decide the form for every N.
  ~~R0 sits above R1 so that a WALK terminal swallows R1's WALK interval (merge).~~
  `[rev4]` Both rows are gone (§1.3a).
- **R1 and R2 apply only above a FAST terminal** `[rev3 B14, C1]`. `[rev4]` R1 is deleted; the condition
  stays on R2 (B6). Rev 2 kept one-byte
  sites zero-mover by the ABSENCE of `kit.xover.LIBC.WALK`; grid2 measures LIBC's and
  WALK's F and β, so a converter could derive that key and R1 would fire on one-byte
  sites at B4. The applicability is now ROW DATA (`SF_TERMINAL_FAST`: t ∈ {V1, W64}), so
  the one-byte and presence populations are 0 movers for ANY set; B4's check runs a
  synthetic set holding every derivable `xover` key (§8.1) and SN-5 plants the dropped
  condition (§8.3).
- **The default rows** (D149, `pcrec-no-silent-defaults`) are D1, D1c, D1w, D2, R7w (and
  PRES's P2-P4, P9): their `basis` is UNMEASURED-DEFAULT, printed in the listing and
  per site in the facts section (§1.7, §4.7). D1/D1c are replaced only by F1 firing on
  measured rows (a censused mover at B5), never edited in place; D1w on the VM hat only
  by F2.
- **D1 excludes the VM hat's seek** (span 0 of a VM_ATTEMPT site) because Q-R5 measured
  memchr per failed attempt at ×0.6 at 80% density; that is today's rule
  (`cand_derive`'s `use_memchr` plus the VM hat's table). `[rev3 A7]` Under D167 add. 1
  ("2+ terms" means MEMBERS) the VM hat at |S| = 1 stays on WALK: row D1w renders today's
  table walk there, zero-mover from B2. Its move to V1's one-term cover is F2, a MEASURED
  row at B5 fed by grid2's VM_ATTEMPT one-byte cells; B4's mover set no longer contains it.
  A PRESENCE span on a VM route is not a per-attempt seek (one FIND of its first
  occurrence per activation), so D1 applies to it and renders today's `memchr`. The
  exclusion is a predicate on the span's ROLE (`SF_SEEK_ROLE`), not on the route.
- **D1w is also `fd-d1`'s OFF arm** `[rev3 A17, B7]`: with D1 denied, a one-byte DFA or
  hybrid site falls to D1w and renders the table walk over its one-member table, a form
  main has (`pf_walk`), answer-identical, from B2. On a DFA_ATTEMPT site `fd-d1` does
  not reach anything: MLINE's row is D1c, which has no deny until B7 builds a libc-free
  back FIND (Q-WR-7).
- **MLINE has no span 0** `[rev3 A5]` (window_contract §2.5: "no span; one context
  predicate `{\n}` one byte before the origin"; D161 add. 7: context checks are not
  spans). Its stop is that context byte, which row D1c keys on directly, so D161 add. 7
  stands with no amendment. It has no NONE row (Q-WR-2: F0's DFA_ATTEMPT key is never
  written until a measurement is ruled in) and no libc-free row (the generic row never
  serves LOOP_EXIT, Q-R7-3).
- **R7 is gated on a measured key** `[rev3 C3]`. `[rev4.1]` Superseded: R7 is gated on the
  cover's TERM COUNT (≤ 2 terms), a compile-time fact; the measured keys are the evidence
  for that rule, not a gate each shape must pass first (§1.3a, §R4.1). The text below is
  revision 3's reasoning, kept. `[rev4]` grid2 measured item 3a's three shapes
  (all three win), so they route at B4. The losing r2 shapes take R7w (§1.3a). 52% of R17-b's byte V1 movers (320 of
  620; byte-vm 485 of 994) have a cover shape no grid1 group timed, and β(V1)/β(walk)
  depends on the shape (0.572 .. 1.410). So R7 fires only where its shape's saving key
  exists and exceeds the regime's null floor; every other set site falls to R7w, main's
  walk, zero-mover. grid2 item 3a times the three commonest unmeasured shapes
  ((0,2,0), (0,0,1), (1,1,0): 83% of the 320) so that B4 can route them; the rest stay
  WALK until a set holds them. B4's census reports movers split by shape measured / not
  (§3.5).
- **One row per layer family** `[rev3 D8]`: R5 and R7 read "the layer's LINER form"
  (V1 at OFF, W64 at W16/W32), so rev 2's R5/R6 and R7/R7s pairs are one row each.
  **Sub-block spans are owned once**: a SIMD helper never runs a span below its own block
  (its derived reach, vrun's `reach_w16`/`reach_w32`, hands the tail to the next rung
  inside the helper); R2 is the selector-level reading of the SAME fact, read from the
  same derived key `kit.block.W64` (M11), so the question "short span: use the lower
  rung" has one source.
- **NONE never applies where span 0 is REQUIRED**: the VM hat and the no-DFA VM route
  state span 0 REQUIRED (PR-4, §4.6), and F0's contract serves only the OPTIONAL class of
  `need` and excludes those kinds (C-12, C-13). An unconstrained reply there turns
  answers into `frames` give-ups (pcscope W3, GIVEUP1 F5).
- **Rows reading E read it only at MEASURED provenance** (D162 add. 3, C-15): R5, R8, F0
  (and P1). The frequency kind is always present after E-1 (D162 add. 2) but carries
  `prior-authored`/`prior-none` on a default compile, so these rows skip there.

### 1.3a Slot FIND at revision 4: the table B4 builds `[rev4]`

This is the one declared first-match table, evaluated as in §1.5. Row ids are kept from
revision 3 so that every citation, deny and sabotage row still resolves. The
"evidence" column is grid2read's section and key. Shapes are written (RANGE, EQ, CUBE)
term counts, as in grid2read §3.2; `kit.saving.V1.WALK.rXeYcZ` is the same shape as a
key.

| # | id | needs | layers | kinds | facts ∧ comparators | pick | unpaid | deny | basis | routed at | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | F2 `vm-hat-1b` | ~~P,E,A~~ `[rev4.1]` P,A | off | VM_ATTEMPT | one member ∧ the seek role ∧ `kit.saving.V1.WALK.VM_ATTEMPT.r0e1c0` > `kit.eps.streamed.slope` ∧ ~~a density condition, still open (Q-R17P-27)~~ `[rev4.1]` NO density condition (Q-R17P-27, YES): it fires on a default compile. E drops out of `needs` with the condition | V1 | — | `fd-vm-hat-1b` | MEASURED | B5 (built at B5, not B4) | §3.7 (an. 8b): saving +0.515; V1 at g = 2 is +38.3% slower, an EXPECTED loss named up front (§9.2a); V1 +33..+54% faster at g ≥ 8 (D169's landing trade) |
| 2 | R5 `regular` | P,E | **off** | all | `SF_E_REGULAR` (below): the analysis object states, at MEASURED provenance, that this site's landings are REGULAR; or the caller states it | WALK | — | `fd-r5` | MEASURED (the walk's win on regular landings) | B4 (no default compile reaches it: no analysis kind states a regime today) | §3.5: V1 +14.9% at g = 2 reg, +34.9% at g = 8 reg; S1/A1 NULL to −4.3% there, hence OFF only |
| 3 | R8 | P,N,M,A | w16, w32 | all | body ONESHOT (gate) ∧ N ≥ `kit.lstar.W64.<kind>` (64 B) | W64 | V1 | `fd-r8` | DERIVED | B6 | §3.5 (an. 6c2): W64 beats V1 at every tested g; §3.3: the block at 64 B |
| 4-6 | R3a, R3b, R4 | H(,P) | (as rev 3) | all | unchanged (§1.3 rows 7-9) | (as rev 3) | — | (B9) | MEASURED, PROVISIONAL | B9 | not timed by grid2 |
| 7 | R2 | P,M,N,A | w16, w32 | all | body ONESHOT ∧ the terminal is W64 ∧ N < `kit.block.W64` (64 B) | V1 | — (the row is dropped; its interval falls to the W64 terminal) | `fd-ndisp` | DERIVED | B6, only if a dispatch pays (it does not today, §2.5) | §3.3: V1 is best below 64 B at both layers; §5: T1 fails at N = 8, T2/T3 fail |
| 8 | D1 `default-1b` | P | all | all | one member ∧ not the seek role | LIBC (forward; bounded for `end_back` 1) | — | `fd-d1` | UNMEASURED-DEFAULT (the self-check's rule: it reads no key; grid2 now confirms the rule it encodes) | B2 (locked) | §3.7: LIBC best-or-tied on 8-9 of 10 cells of every kind |
| 9 | D1c `context-1b` | P | all | DFA_ATTEMPT | no span 0 ∧ one context predicate of one byte | LIBC back | — | none | UNMEASURED-DEFAULT | B2 (locked) | §3.7 (o-back: LIBC regret +208% at g = 2, best elsewhere) |
| 10 | D1w `walk-1b` | P | all | every kind but DFA_ATTEMPT | one member | WALK | — | none | UNMEASURED-DEFAULT | B2 (locked) | D169 keeps it until F2 |
| 11 | D2 `run` | P | all | all | span 0 is a RUN term | RUN | — | the nested table's | UNMEASURED-DEFAULT | B3b (locked) | not timed |
| 12 | R7 `liner` | P,A (+I at w16/w32) | all | all | ~~`kit.saving.<LINER(layer)>.WALK.<shape>` > `kit.eps.streamed.slope` (an ABSENT key does not hold)~~ `[rev4.1]` the cover's TERM COUNT ≤ 2 (range + eq + cube terms of the cover `pf_terms_mask` builds; a compile-time fact, so an untimed combination needs no key first). The threshold is the derived key `kit.terms.V1max` = 2 (§5.2; the sign change across grid2's nine timed shapes); an ABSENT key does not hold, so R7 falls to R7w | the layer's LINER form: V1 at OFF; W64 at W16/W32 where built (B6) | — | the FORM denies (`pf-terms-mask` at B4) | DERIVED `[rev4.1]` (the self-check's rule: R7 reads a derived key, `kit.terms.V1max`, drawn from nine MEASURED shapes) | B4 | §3.2 (the evidence the rule is drawn from; V1 vs the walk): saves for 1-2 terms: (1,0,0) +0.420, (0,0,1) +0.548, (2,0,0) +0.012, (0,1,1) +0.268, (0,2,0) +0.390, (1,1,0) +0.211; loses for 3 or more: (2,0,1) −0.133 (3 terms), (3,1,0) −0.413 (4), (3,0,1) −0.464 (4). `[rev4.1]` The rule is V1's (grid2 timed V1 against the walk); B6 decides the W64 form's own condition |
| 13 | R7w `walk-default` | P | off | all | always | WALK (main's form) | — | none | UNMEASURED-DEFAULT (it reads nothing; `[rev4.1]` it is reached for ONE reason, below) | B4 | `[rev4.1]` covers of 3 or more terms: the three measured losers, and any untimed combination by its count. ~~the three losing shapes (measured); shapes with no key (Q-R17P-26)~~ |

Notes on the rev 4 table:
- **Gone from the table.** R0 (retired), R1 (deleted), F0 and F1 (not built). §R4
  gives the measurement for each. Their ids are reserved; nothing reuses them.
- **Why R0 can go.** R0 was a CLASS guess made before the r2 shapes had their own
  keys: "≥ 2 RANGE terms → WALK, because a 3-term V1 is slower" (gridread L3). grid2
  measured the shapes one by one, and the class key turns out to be a MAX. One
  winning shape ((2,0,0), +1.2%) suppresses R0 for the three that lose. ~~R7's per-shape
  comparator already sends each losing shape to R7w and each winning one to V1~~
  `[rev4.1]` R7's term-count rule already sends each losing shape (3-4 terms) to R7w
  and each winning one (1-2 terms) to V1, so R0
  could only ever have done harm: holding on a class whose MAX is ≤ eps would force
  the walk onto a shape whose own key says V1 wins. The row, its deny `fd-r0` and its
  sabotage row S916 retire together at B4 (§3.4, §8.3). This removes a special case.
  It is not a new mechanism.
- ~~**R7w is reached for two reasons**, and the listing and the facts section give each
  site's reason:~~ `[rev4.1]` **R7w is reached for ONE reason** (Q-R17P-26, answered):
  the cover has **3 or more terms**. The listing and the facts section print the count
  beside the pick. The two rev 4 reasons, struck:
  - ~~**measured-loss**: the shape's key exists and is ≤ eps. This is D169's "a
    measured row keeps the walk";~~ now simply "3 or more terms": the three measured
    losers (3, 4 and 4 terms) are the evidence, and a measured row still keeps the walk
    by the same count;
  - ~~**unmeasured**: no key exists for the shape. Q-R17P-26 asks whether D169's V1
    default also covers this case.~~ gone: an untimed combination routes by its term
    count like any other, and needs no per-shape key first. If the cover search finds
    no cover at all (R17-b's K = 4), there is no V1 form to route to and the site keeps
    the walk it has today.
  - **How the rule is held honest.** B4's acceptance measurement confirms the rule on
    every shape it moves; a shape whose measured sign contradicts its term count (a
    3-term shape that wins, or a 2-term shape that loses) is a FINDING, reported with
    its cells, not a default to shrug off (§9.2 item 2, §9.4).
  The self-check needs no change: R7w reads nothing, so its `basis` stays
  UNMEASURED-DEFAULT. `[rev4.1]` R7's `basis` is DERIVED: it reads the derived key
  `kit.terms.V1max` (row 12), not a bare literal.
- **`SF_E_REGULAR` is a PROPOSED site fact, not built.** It says the landings are
  regular. Its home is the analysis object, as a new [FINDINGS] query kind (proposed
  `landing-regime`, values `regular` / `irregular`, UNSTATED zero) in `find_queries[]`,
  so the NEW-DATASET lens names its home and no second data channel is made.
  - **What it can read.** grid2 separates the regimes by the walk's branch misses
    per landing: 0.97-1.44 on irregular landings, 0.009 on regular ones
    (grid2read §3.5, F2 counters). A gap-distribution statistic that predicts that is
    the candidate.
  - **Build trigger.** Nothing builds it before a measured need (D77). The trigger is
    D169's revisit condition: a real, non-synthetic workload with dense regular
    landings over a large subject.
  - **At B4.** R5's row is source with its new condition and is unreachable on every
    default compile, because no kind states the regime. Its rows.tsv reach reason is
    `pending-site:landing-regime`.
  - **The caller-stated half** is an interface spelling and waits for [IFACE-PUSH].
- **R5 is OFF only.** On regular landings the wide forms are NULL against the walk
  (g = 2: S1 +0.6%, A1 +0.5%) or win (g = 8 regular: A1 −4.3%), so the walk is never
  the better form at W16/W32 (grid2read §3.5). Revision 3 applied R5 at every layer.
- **The `kit.gstar` keys stay in the set** (`u-shape` provenance, grid2read §6's R5
  row). No row reads them. They are shape-confounded and kept as evidence only.
- **No row reads `kit.xover.LIBC.WALK.*`.** grid2 measured those keys (4.1-6.1 B),
  which is exactly the hazard rev 3's C1 foresaw. With R1 deleted they have no
  reader. R2's fast-terminal condition still holds for B6, and SN-5 is re-aimed there
  (§8.3).

### 1.4 Slot PRES: the rows `[rev2]` `[rev3: D3, C2, C11, A11]`

Evaluated once per PRESENCE span of a site (§4.1), after slot FIND. P2 reads FIND's proven
fact (`proven0`), a declared cross-slot read (§4.5's read list, `cand_rows[]`'s `reads`
precedent). `[rev3 D3]` A pick is a set of CHAIN-LINK attributes (§1.2 `fd_link`), so
R-18's chain links consume the slot's output unchanged:

| rev 2's pick | link attributes | meaning |
|---|---|---|
| KEEP | `verify` = 1 | the link is verified over `[start + omin, n)` before the first element (§4.1) |
| DROP | `proven_by` = 1, `verify` = 0 | span 0's proof stands for the link; no test |
| PICK | `verify` = 1, `member` = 1 + i (or the run's window) | only the chosen member of a set, or the chosen window of a run, is verified |
| LEAD | `verify` = 1, `order` lower than the run's | an ORDER: this link is tested before the run |

| # | id | needs | kinds | condition | link | unpaid | deny | basis | routed at |
|---|---|---|---|---|---|---|---|---|---|
| 1 | P0 `required` | P | all | the span's `need` is REQUIRED (gate) | `verify` = 1, `member` = 0 (every member) and the WHOLE run (K65, K66), before the first element (G-1, G-2) | — | none: undeniable (a deny would let a budgeted engine give up where today answers, D158) | DERIVED (from the answer contract) | B3b |
| 2 | P1 `priced` | P,E,A,N,M | all | `need` OPTIONAL ∧ E measured ∧ the set has the gate's quantities (M23) | argmin {`verify` = 1, `verify` = 0} by expected cost | `verify` = 1 | `fd-pres-priced` (with the row) | MEASURED | B5, and only once Q-WR-9's trigger fires (a TUG cell measured losing for want of it); ~~built at B5~~ `[rev4.1]` NOT BUILT: the trigger fired on the letter and P1 is recorded, not built (Q-R17P-28) |
| 3 | P2 `dominated` (G1, ported) | P,E | all | `need` OPTIONAL ∧ span 0's `proven0` covers this span (identity; `run_verified`; or the density conjunct read from the frequency kind, prior included) | `proven_by` = 1 | — | `fd-pres-g1` | UNMEASURED-DEFAULT (the density conjunct's prior and its constant, `[rev3 C11]`) | B3b |
| 4 | P3 `pick` (ported) | P,E | all | `need` OPTIONAL ∧ the span is one member of a necessary set, or the window of a run | `member` = the rarest by the frequency kind, ties to the higher PATTERN ORDER (PR-7); the run's scan index / window start | — | `fd-pres-pick` (deny = keep every member) | UNMEASURED-DEFAULT (the prior's "rarest") | B3b |
| 5 | P4 `set-leads` (ported) | P,E | all | the set's pick is strictly rarer than the run's scan member | `order` before the run | — | `pres-set-lead` (replaces pcrec's `-fno-req-set-lead`, bit 45, in the SAME commit: KW-11, Q-WR-12) | UNMEASURED-DEFAULT ("strictly rarer" on the prior) | B3b |
| 6 | P9 `default` | P | all | always | `verify` = 1 (Q-WR-9: the total default) | — | none | UNMEASURED-DEFAULT | B3b |

Notes:
- **These are pcrec's priced picks, ported verbatim** (KW-8): the set pick (P3, with
  member order), the run scan index / window start (P3), set-leads (P4), G1 (P2:
  identity / `run_verified` / density). The fifth, the landmark admission
  (`req_landmark_admits`), is NOT a kit row: under framing (a) (Q-WR-5, ruled) it chooses
  the ORIGIN, which is pcrec's only choice (D161 add. 9; D167 Q-R17P-11). `[rev3 A11]`
  D167 add. 1 refines it: its input is restated as pcrec FACTS (the start set's PRIOR
  mass, h and K), with no read-back of the kit's form or of "what the displaced scan
  skips" (`emit_dfa.c` ~7920-7934 priced a kit method, contrary to D157). The arithmetic
  is unchanged and nothing moves; only names and comments change, main-side, at B2
  (§3.1). Until that commit it is recorded as a D157 exception. The kit computes it in
  the B3a shadow only, as evidence for framing (b) (Q-R17P-11).
- **The ported rows read the frequency kind at any provenance.** They are the total
  default reproducing today (D162 ruling 2), which is why ST3 needs E-1 first: with a
  NULL analysis they would read nothing and move bytes (pcscope §5). Only P1 is an
  evidence row (C-15). `[rev3 C11]` Their constants (G1's density conjunct, P4's
  "strictly rarer", P3's ties) are labelled UNMEASURED-DEFAULT in `basis`.
- **P1 is DESIGNED, not built** until Q-WR-9's trigger fires; it lands at B5 as a
  formal row addition. The locked PRES slot is P0, P2, P3, P4, P9.
  `[rev4]` grid2's probe fired the trigger ON THE LETTER (grid2read §3.8). KEEP loses
  1.47 / 1.54 ns per call (3.4-3.8% of a 25-46 ns call) on two TUG cells: g = 8, byte
  early. The same pre-check wins ×49..×112 when the byte is absent, and late cells are
  NULL. The operands are measured (`kit.gate.byte1.DFA_SCAN.early/late/absent` =
  +8.1 / 0 / −247,000 u·B). P1 reads E only at MEASURED provenance, so even if built it
  would never fire on a default compile. ~~Whether to build it at B5 is Q-R17P-28.~~
  `[rev4.1]` **Ruled (Q-R17P-28, the kit manager's call, 2026-10-21): the trigger is
  recorded as FIRED ON THE LETTER and P1 is NOT BUILT.** It never fires on a default
  compile (it reads E only at MEASURED provenance), so building it now would be work
  for a row only a measured bundle reaches (D77). P1 stays designed; rev 4's leaning
  names when to look again: a measured-bundle workload exists. The locked PRES slot is
  unchanged (P0, P2, P3, P4, P9), and B5 has no P1 item.
- **P0 before P2/P3.** A REQUIRED span is never dropped or narrowed (the applicability
  rule, KW-6/C-9): on a no-DFA route every member and the whole run are verified, which
  is K65 fix (a) and K66 as row data.
- **What the kit still owns under P0** is the FORM of each kept test: a kept presence
  span is a FIND of its first occurrence over `[start + omin, n)`, and that FIND's form
  comes from slot FIND's rows evaluated for the span's shape (D1 for one byte, D2 for a
  run). One form table, not a second one.

### 1.5 Evaluation: one table, two times (rev 1 §1.2, with three `[rev2]` rules) `[rev3: D1]`

`[rev3 D1]` Per site, per slot, per layer variant, the evaluation is `kit_walk` plus ONE
residual step:
- **the terminal**: `kit_walk(fd_table, slot, ...)` over the rows whose `needs` exclude
  N and H returns the first row whose deny, contract and predicate pass; its pick is the
  TERMINAL. A row whose `needs` are unavailable (E absent or prior-only for an evidence
  row, H outside an iterator, M unstated, a set key ABSENT) does not hold;
- **the residual (N-interval) step**: each row ABOVE the terminal that needs N is asked
  on its own (`kit_ask`, the same three tests); a holding N-row becomes an emitted
  dispatch interval; adjacent same-pick intervals merge; each interval must pay (§2.5) or
  take its `unpaid`; one surviving form means no dispatch at all.

`[rev2]` Three rules:
1. **Proven facts are decided once per site, at layer OFF.** A row whose pick changes
   what the site PROVES (F0 NONE proves nothing; LIBC proves byte b at offset 0; WALK and
   V1 prove S at offset 0; a PRES `proven_by` link removes a verdict) is decided at the
   OFF variant, and the W16/W32 variants inherit that decision. They may pick a different
   form only among forms with the same proven fact. DERIVED from D161 add. 8 (the proof is
   the site's statement, identical in every layer) and the floor rule (a SIMD-on artifact
   is the SIMD-off one plus guarded text, so pcrec's own text, which reads the proof,
   cannot differ by layer). `[rev3 A4]` It is also why the define-time query (§4.5) has
   one answer per site: it answers for the OFF decision.
2. **A span whose byte form is a SUPERSET** (D161 add. 10: a utf8 multi-byte class
   lowered to per-position byte sets) proves only the byte sets, never the class; its
   candidates are a filter and pcrec re-checks. No row of this delivery verifies a span.
3. **Totality.** NULL `mf_measures`, an unknown key, a NULL analysis and every absent
   kind make the reading rows skip; the last row of each slot reads nothing (`[rev3]` R7w
   at OFF, P9). At W16/W32 with no W64 form built, R7 does not apply and no row is chosen:
   the variant adds no text (the floor rule), so a SIMD-on artifact is byte-identical to
   SIMD-off until B6.

### 1.6 Routing state: a per-row `routed` bit until B4 `[rev2]` `[rev3: D6, B5, B6]`

The table is built whole at B1 (E3) and judged whole by [REGIME-EVAL]. It must not move a
byte before the judge (Q-REVAL-11; D167 Q-R17P-13: the judge gates B4 only). `[rev3 D6]`
Rev 2 reconciled the two with a temporary list `fd_route[]` of group predicates, which
restated the rows' own conditions in a second language (two statements of one
population). Revision 3 replaces it with ONE bit per row, `fd_row.routed`:
- **A site renders the table's pick iff the FIRST matching row (the terminal, and every
  interval row above it) is routed.** Otherwise it renders its pre-table form (main's kit
  rows, pcrec's encoding) and, in the MF_TRACE build only, writes the table's
  (site, slot, row, form, interval literals) record: zero bytes (regime_eval §5.3's
  trace-only shadow, r4ccore's I1 pattern).
- **The commit that routes a group sets its rows' bits** (the "routed at" column of §1.3
  and §1.4): D1, D1c, D1w at B2; D2 and the PRES rows at B3b; ~~R0, R1,~~ R5, R7, R7w at B4
  (R2, R8 at B6; ~~F0-F2~~ `[rev4]` ~~F2, P1 at B5 (F0, F1 not built)~~ `[rev4.1]` F2 at B5
  (F0, F1 not built; P1 recorded, not built); R3a, R3b, R4 at B9).
- At B4 every row is routed; the field is DELETED in B4's commit. It is
  implement-then-replace's switch written as data on the rows themselves.

`[rev3 B5]` **Routing at zero movers must be OBSERVABLE.** A routed row whose pick is
today's form is byte-identical by design, so neither emit_sweep nor G2 can tell
"routed and identical" from "never routed". Three things make it visible:
1. **a pcrec-side routed-record count**: in the trace build, pcrec counts the sites whose
   decision came from a routed row, per (site kind, row), read from pcrec's own trace
   records (the reader that consumed the kit's rendering), never from the kit's own
   counter; each routing step pins a floor per (kind, row) and checks it both ways (a
   count that falls is a row that stopped routing, one that rises past its population is
   a row routing early);
2. **disagreement witnesses** per routed group, where pcrec's old rule and the kit's row
   CAN differ, so a decision still taken by pcrec shows as a trace or stamp difference: a
   one-byte count boundary for D1 (`|S|` 1 vs 2, the VM-hat role vs a presence span), a
   G1-dominated and a G1-kept span for P2, a tie for P3's member order;
3. **the reverse plant** SN-1 (a row's `routed` bit left 0 after its step): detector,
   the count above (§8.3).

`[rev3 B6]` **The shadow is run where B4 will first exercise it.** At B1 the trace-build
shadow runs under the NULL set, the kit's interim TSV (Q-REVAL-10) and each synthetic
extreme set (`all-walk`, `all-v1`, `all-wide`, and one holding every derivable key),
through a trace/test-build-only lever (the B4 harness lever `measures=FILE`, built at B1
for the trace build only, §3.1). It records each dispatch's interval literals. B1's
shadow picks under the interim set are committed as B4's PREDICTED MOVER MANIFEST: B4's
movers-by-ID are held to it (a difference is explained or the manifest is wrong). The
shadow's denominator is a pcrec-side census of search-entry activations from emitted C
(the PF/MLINE/PRE site census of §3.5), not the shadow's own record count; and the
comparator itself is planted (SN-6).

### 1.7 The listings `[rev2: --list-finder WITHDRAWN]` `[rev3: A9, B3, C2, D11]`

Rev 1 proposed a new CLI flag `--list-finder`. Withdrawn: a new CLI surface waits for
[IFACE-PUSH] (memory `pcrec-iface-push-later`), and R-20's R-MS4 already carries the
same information through existing channels:
- **The rows**: `mf_finder_rows(size_t *n)` beside `mf_options()`, read by
  [LIST-TABLES]' census in its shape (measure_sets §5.4), with each row's `needs`, the
  keys it reads and, per threshold key, its SAFE direction (`max`/`min`/`none`, R-MS4;
  directions due at M2), `[rev3]` its `basis`, its `refuted_by` and its `routed` bit.
- **Per artifact**: the `--emit-facts` section `memfn` (measure_sets §4.5): per site,
  the slot, the row that fired, its pick, its `basis`, and for a dispatch the interval
  literals; `[rev3 C2]` plus a per-compile count of sites decided by an
  UNMEASURED-DEFAULT row, so a default is never read as measured (`consulted` stays one
  boolean, R-MS2). `[rev3 A9, B3]` It is NOT added at B1: R-20 schedules it with M0 (B4),
  where artifacts move anyway; adding it at B1 would move every `--emit-facts` output
  (facts_listing.md §3¶3: "no other section is printed") inside a step gated at zero.
  The D80 hunk (facts_listing.md §3) rides B4.
- **The set's provenance** is the set's own listing (`--list-measurements`, M0).

### 1.8 The row-edit log and LOCKDOWN `[rev3: B9, D7]`

D161 add. 13: until LOCKDOWN a row edit is free and logged in
`memfn/docs/finder_history.md`. `[rev3 B9]` An edit is logged in the COMMIT that makes it,
not later: revision 2's row edits (F0, F1, D1, D2, the PRES slot, R1's terminal-relative
key) and revision 3's (D1c, D1w, F2, R7w, R5 ∪ R6, R7 ∪ R7s, the comparator, the link
attributes, `basis`, `refuted_by`, R1/R2's fast-terminal condition) are logged in this
revision's commit. `[rev4]` So are revision 4's (R0 retired, R1 deleted, R2's `unpaid`, R5's
condition and layer, R8's E.g, F0/F1 not built, F2's open density condition). `[rev4.1]` So
are revision 4.1's (R7 re-keyed to the cover's term count, R7w's single reason, F2's
density condition dropped, P1 recorded and not built), logged in `memfn/docs/
finder_history.md` in the commit that makes them. regime_tables.md mirrors the FIND slot (main's mirror, updated by main
from the log); the PRES slot is not a regime row (it is not judged by [REGIME-EVAL]'s
grid) and needs no mirror there.

`[rev3 D7]` **A row locks when it is ROUTED**, not at B4: D1, D1c, D1w (B2), D2 and the
PRES rows (B3b) are byte-identity-gated from their routing commit, so an edit to one of
them is a mover and an abi event. The listing carries a `locked` column (= `routed`
until B4). B4 locks the rest.

`[rev3 B9]` **LOCKDOWN is a checkable state** (§3.3): a committed digest of `fd_rows[]`'s
listing (`mf_finder_rows`' canonical text) plus a check that fails on any digest change
not paired with a `finder_history.md` entry citing its ruling (after B4) or its free-edit
reason (before). The judged subset is named: [REGIME-EVAL] scores the FIND rows its replay
can score; the PRES rows, R3a, R3b and R4 are EXEMPT from the judge's verdict (unscorable
by replay, regime_eval F-5/F-7) and lock on their routing or on byte identity, not on a
judge PASS.

### 1.9 B4's default when landing predictability is unknown: V1 (D169) `[rev4]`

**What grid2 found.** Revision 3 expected the choice between V1 and the walk to be
decided by search length (R1's crossover, M9) or by candidate gap (R5's g\*, M15). It
is decided by neither (grid2read summary items 5-6, §3.3, §3.5):
- V1 beats the walk on a single call at every measured N from 8 B to 1 MiB;
- on find-all with UNPREDICTABLE landings, every form wins from g = 4. V1 is −23.7%
  at g = 4 on `dig` L = 64 KiB;
- on REGULAR landings V1 LOSES: +14.9% at g = 2, and +34.9% at g = 8 on `dig`
  L = 1 KiB. The walk is cheap there;
- the mechanism is branch prediction. The walk pays about one mispredict per
  irregular landing (0.97-1.44 misses, 4.2-5.4 ns each) and 0.009 per regular landing.
  The wide forms pay about 0.1.

Landing predictability is a property of the SUBJECT, unknown at compile time.

**The ruling (Frank, 2026-10-20; D169, gist as recorded):**
- Short candidate gaps tend to come with short subjects, so the total search time is
  small and the losses are small in absolute terms ("only a weirdo is using this to
  replace every e in a Gutenberg bible").
- Presume large gaps with large subjects, where throughput matters.
- All else being equal, the default is V1.
- The walk stays the default only where a MEASURED row keeps it: the VM hat (D1w),
  until F2.
- One-byte sites keep LIBC (D1).
- A measured or caller-stated regular regime may select the walk (R5's MEASURED-E
  path).
- Revisit when a real (non-synthetic) workload shows dense regular landings over a
  large subject.

**What it fixes in B4's table (§1.3a), row by row:**

| case | rev 3 | rev 4 under D169 |
|---|---|---|
| a set site whose cover has at most 2 terms (`[rev4.1]` was: whose shape has a measured V1 saving > eps) | R7 → V1, unless R1's short-N interval or R5's gap row took the walk | **V1**, with no length or gap row in front of it. R1 is deleted (no interval) and R5 no longer reads a gap |
| a set site whose cover has 3 or more terms (`[rev4.1]` was: whose shape has a measured V1 LOSS ((2,0,1), (3,1,0), (3,0,1))) | R0 → WALK (class rule) | **WALK** through R7w: the term count keeps it, and the three measured losers (3, 4 and 4 terms) are the evidence |
| ~~a set site whose shape has NO measured key~~ `[rev4.1]` a set site whose combination of terms nobody has timed | R7w → WALK | ~~**WALK** (R7w) until Q-R17P-26 is ruled. The ruling speaks of unknown PREDICTABILITY, and here the per-byte COST is unknown. The leaning is to keep the walk (§7.3)~~ **routes by its TERM COUNT** (Q-R17P-26, answered): V1 at ≤ 2, WALK at ≥ 3. The deciding fact is static, so "not timed" is not "unknown". A shape that contradicts the rule is a B4 finding (§9.2) |
| the VM hat at \|S\| = 1 | D1w → WALK | **WALK** (D1w) at B4, as the ruling names. `[rev4.1]` F2 moves it to **V1 at B5**, by default, with no density condition (Q-R17P-27, YES); its g = 2 cells are expected losses (§9.2a) |
| a one-byte site | D1 / D1c → LIBC | **LIBC**, as the ruling names |
| a site whose landings are known REGULAR | R5 on a gap threshold | **WALK** through R5 on a stated regime (`SF_E_REGULAR`). No default compile reaches it until such a kind exists |
| a W16/W32 variant (B6) | R7 → W64, R8 and R2 dispatch rows | W64 from the block. R2 is dropped (no dispatch pays) and R5 does not apply. The wide forms are NULL or better on regular landings, so the ruling's trade does not arise there |

**What the default costs, stated up front.** On a default compile, every set site whose
cover has at most 2 terms (`[rev4.1]`; rev 4 said "on a winning shape") renders V1 whatever
its subject's landings are. So a REGULAR-landing
subject loses against main's walk by the amounts above. Those cells are EXPECTED losses:
B4's acceptance names them before it times anything (§9.2a), and no B4 verdict counts
them against the routing.

**What it does not change:**
- B0-B3b (every routed row reproduces today);
- the PRES slot;
- the contract;
- the rule that a row reading E reads it only at MEASURED provenance (§1.3's last
  note).

---

## 2. The emitted N dispatch (rev 1 §2, carried; reached at B4 or B8)

Nothing in this section is emitted by the first delivery (B0-B3): the dispatch rows
R1/R2 need M16-M18 to pay (§2.5), and those are measured at the earliest in grid2.
`[rev4]` grid2 measured M16-M18, and the dispatch does not pay (§2.5's verdict), so B4 emits
none of this either. R1 is deleted. The text stays for B8 and the iterator. The
text is kept so the build has its shape, and so R-19's two facts have their reader.

### 2.1 Where it sits `[rev2: main's points]` `[rev3: A1, A2, A3]`

`[rev3 A1]` Rev 2 put the storage point at `unanch_scan`'s `scan_position` declaration and
at the VM hat's entry seek, and named the PRE composite's entry "the same site's first
use". On main the PRE use is emitted ABOVE both points (`fwd.from =
pcrec_emit_req_byte_check(...)` at `emit_dfa.c` ~11749, before `unanch_scan` at ~11756;
VM `emit_vm.c` ~13214, before the hat's seek at ~13477), and the DFA body had two STARTs
(`search_from` for the PRE use, `fwd->from` for the scan, the second computed by the
first). Revision 3 states, per emitter, ONE storage point above the first use and ONE
START per activation:

| emitter (main) | function holding the site | storage point (`mf_locals`) | START (R-19's hook) | uses, in order |
|---|---|---|---|---|
| DFA body, unanchored forward scan | `<p>_search` (DFA) | the entry, after `pcrec_emit_search_head` and the end-window clamp, ABOVE the PRE use | `search_from` | (1) the entry use (presence verdict; on a handoff route the landmark's first candidate `c`); (2) each loop use in `unanch_scan` (the next candidate from `scan_position`); (3) the handoff's NEXT re-entry |
| VM hat route | `<p>_search_run` (`pf_vm_emit_first_class`) | the entry, ABOVE the PRE use (`emit_vm.c` ~13214) | `search_from` | (1) the entry use (presence); (2) the hat's seek and each re-seek |
| `[rev3 A2]` DFA attempt (ENG_ATTEMPT) | `attempt_entry`'s function (`emit_dfa.c` ~12604) | the entry, ABOVE the PRE use (guarded `cand_finish_of(cx) != CAND_ROUTE_VM`) | `search_from` | (1) the entry use (presence); (2) MLINE's predecessor seek per attempt, where present (a context FIND, row D1c) |
| `[rev3 A3]` VM hybrid, presence | `<p>_search_run` | its entry, above the PRE use | `search_from` | (1) the entry use (presence only) |
| `[rev3 A3]` VM hybrid, find | the static `<p>_prefilter` | its entry (each call is an activation: every VM retry re-enters at `attempt_position`) | the prefilter's own `search_from` | (1) each FIND use in the inlined DFA body |
| rev-end relocate path | its own activation | its entry | its moved start | its FIND use |

- **The handoff's `c − K` is a USE's argument, never a second START.** On a handoff route
  the entry use yields the landmark candidate `c`; pcrec computes `max(lo, c − K)` and the
  utf8 round-up in its own text (window_contract §2.1) and passes it to the next use as
  `lo`. N = `n − start` is read once, at the storage point, from `search_from`.
- **The form byte** is written in the site struct's initializer at the storage point.
  The use stays where today's use is. `<stem>__next_candidate` is never the dispatch.
- **R-19 is asked for every builder above** (`[rev3 A21]`, Q-R17P-16): R-19 on main names
  the DFA forward scan, VM `_search_run`, the relocate start and `fwd->from`; it does not
  name `req_site_define`, MLINE or `attempt_entry`. Rev 2 assumed it did; revision 3 asks.
  Unstated, every N-row skips (§1.5).
- **The hybrid's two sites carry one window request between them.** The presence site is
  presence-only (`pred.nterm = 0`); the find site is find-only and its stream never
  re-verifies (§4.4). Population: rev 2's hybrid rows (626 / 8 / 18 one-byte; 241 / 16 / 8
  set), re-counted at B2/B3a.

### 2.2 The C text (rev 1 §2.2, unchanged except the start expression)

For one DFA prefilter site `rx_search_pf` (the stem and table of the emitted artifact
for `[0-9]+x`). Text marked `// R17-b` is R17-b's, ported at B4.

**(a) WALK + V1: a SIMD-off artifact with a paid dispatch.**

```c
/* define (file scope) */
struct rx_search_pf__c {
    const unsigned char *s;
    size_t n;
    size_t base, top;
    unsigned long long m;
    unsigned char f;            /* the form this activation runs: 0 WALK, 1 V1, 2 W64 */
};
/* rx_search_pf__mask, __member, __next_candidate: R17-b's text */
static inline size_t rx_search_pf__walk(const struct rx_search_pf__c *c, size_t lo,
                                        const unsigned char *t)
{
    while (lo < c->n && !t[c->s[lo]]) lo++;   /* pcrec's walk, bound read off the struct */
    return lo;
}
static inline unsigned char rx_search_pf__form__body(size_t n, size_t lo)
{
    size_t span = n - lo;       /* lo > n wraps high: the last row's pick, and the use's guard reads nothing */
    if (span < 36) return 0;    /* R1 -> WALK (the literal is the set's, §2.6) */
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

/* storage point; `search_from` is the START hook's text (R-19) */
    struct rx_search_pf__c rx_search_pf__c = { subject, subject_length, 0, 0, 0,
                                               rx_search_pf__form(subject_length, search_from) };
/* use (inside the attempt loop) */
            if (scan_position < rx_search_pf__c.n) scan_position = rx_search_pf__next(&rx_search_pf__c, scan_position, rx_can_begin_match);
```

**(b) WALK + V1 + A1 (SIMD-on, R2 paid)** is (a) plus guarded insertions only: the V32
sub-block, `__next_candidate__w32`, `__form__w32` (`span < 36` → 0, `span < 64` → 1,
else 2) and `__next__w32`, then the selector FUNCs `__form` and `__next` whose whole
bodies are the `#if` chain, one call per arm (D155 add. 1). The storage point and the
use are byte-identical to (a). **(c) WALK + A1 (R2 unpaid)** merges R2 into R1's WALK
interval. Rev 1 §2.2 has the full text of (b); it is unchanged and is not repeated.

**Single-form sites.** One surviving form means no field `f`, no `__form`, and
`__next__body` is that form alone. A V1-only site is R17-b's text routed through
`__next`; a WALK-only site at SIMD-off (R0) is either the walk-only scaffold or main's
bare walk, decided by T3 (§2.5). `[rev2]` A LIBC site (D1) and a NONE site (F0) never
carry a scaffold: neither has a SIMD arm in this design, so F5's reason for the scaffold
does not arise.

`[rev3 D5]` **The helpers' layout is not fixed here.** `__walk`, `__form`, `__form__body`,
`__next` and `__next__body` are written `static inline` above because that is what the
kit emits today, i.e. the layout of D163 add. 7's position `0` (`compound_entries.md`
§3.4 row L0, "as emitted"). They are member 4 of that note's inline/shared family (§3.1:
"the kit's FUNC helpers and D155 selector"), which stays the kit's (D157): pcrec can
pass the dial position as a FACT (that note's U8) and the kit lays out its own helpers
to the position's policy (all-shared at `−2`, shared-but-inner at `−1`, hot-inline at
`+1`, all-inline at `+2`), under the same hard rows (a single-caller helper is never
shared; L4). Nothing in this note pins a layout. Whether the kit's size-adding rows
(`pf-terms-mask`, `fd-ndisp`, `pf-terms-w*`, all `MF_SZ_ADDS`) belong in the dial's pinned
table or stay outside it (they are FORM denies the size ladder's `drop-kit-bytes` rung
reads, not layouts) is Q-R17P-21.

### 2.3 Why behind `__next` and not in the use (rev 1, kept)

Only the selector shape keeps the use identical in every layer (D155: no `#if` in a body).
The measured cost side (`r17b_prime/out/walk_helper_asm.out`): the walk moved into the
helper and reached through the struct changes the holding function by −3 to +14
instructions on six cells, none identical. That is C_scaffold (M18), measured, never
assumed free.

### 2.4 What N is, and what M is (rev 1, kept; `[rev2]` M is now a STATED fact; `[rev3 A6]` M is a PARAMETER)

- **N** = `n − start` at the storage point, once per activation. For one `_search` call
  it is the span the call may scan; inside a find-all loop over `_search` it is the
  REMAINING subject, so dense 1 MiB find-all stays LINER-picked and R17-b′ does not fix
  ALPHA's dense find-all rows (bounded prose1m all +599 µs; dfa-hat prose1m all/first
  +232/+234 µs). Those belong to E (R5) and to the iterator (R17-b″).
- **M** `[rev3 A6]`: rev 2's "M is fixed per entry BODY, so no row ever emits a compare on
  M" is FALSE under main's iterator design. `findall_iter.md` §4.2 makes M a PARAMETER of
  one shared `<p>__find` (`_search` passes ONESHOT, `next` passes ITER), and D163 add. 7's
  part-layout row decides whether that body is inlined (M a constant per call site, the
  dispatch on M folds to one arm) or shared (M one runtime branch per call). The body is
  shared at `−2`/`−1`, at `+1` when it ranks below `θ_hot`, and at EVERY position on the
  DFA attempt route, whose body holds a static label table (row L1; 233 of 4,243 corpus
  artifacts). So:
  - the fact is `mf_site.body` ∈ {UNSTATED = 0, `MF_BODY_ONESHOT`, `MF_BODY_PARAM`}
    with, for PARAM, a hook naming the C expression of the mode (findall_iter §4.2's
    REQUEST, filed by main as R-20 at R17-b″). Through B8 every builder states ONESHOT
    (there is no iterator); `MF_BODY_ITER` (rev 2's spelling) is withdrawn;
  - an M-reading row (R1, R2, R8) on a PARAM body whose find part is SHARED emits a
    runtime compare on the mode. That charge is a quantity, M24 `cmode_call` (§5.2), read
    by the pay rule beside C_disp_call: ABSENT, it fails T2 (§2.5), so on a shared PARAM
    body an M-reading row takes its `unpaid` until M24 is measured;
  - where the find part is inlined, the compare folds and M24 is not charged.
- **B9 waits on main's order** (D163 add. 7 Q4): E0 (the zero-mover `entry_rows[]`), then
  `findall_iter.md`'s short revision (the retry as `first-nonzero`, the find body's
  layout from the row, internal batching in `_in` memory), its D6 panel, then I1; and
  R-19's amended body fact (R-20). §3.1's B9 row lists them.

### 2.5 The pay rule (rev 1, kept: Q-R17P-3 stands as the kit's design, §7.1) `[rev3: C4, D9]`

Every quantity in walk-byte units from the active set; no call-length distribution is
assumed. For a dispatch row r with interval I_r = [a_r, b_r), pick p_r and alternative
a′_r (its `unpaid`, else the pick its interval would fall to), cost(f, N) the measured
single-call cost:

`[rev3 C4]` **The floor is regime-matched and absolute.** Rev 2 used one ε (M6, 3.1%, a
pooled F1+F3 p90) for every test; the single-call quantities T1-T3 read have their own,
much smaller A/A floor (F3 member-free p90 0.173%, EXT 0.382%; gridread). Each test now
reads the floor of the regime its operands were measured in, `floor(cell)` = the A/A
spread of that cell's own group in the set, in absolute u·B (D144 add. 1: an absolute
delta next to the noise floor measured the same way), and compares an UPPER BOUND, not a
point estimate:
- **T1 (pays where it fires):** min over measured N ∈ I_r of
  [cost(a′_r, N) − cost(p_r, N)] − floor > C_disp_call + floor(C_disp_call) (the saving's
  LOWER bound beats the charge's UPPER bound at every measured N in the interval).
- **T2 (nothing measurable where it does not fire):** C_disp_call + floor(C_disp_call)
  ≤ floor(f_next, b_r) (the charge's upper bound is inside the next form's own noise).
- **T3 (nothing measurable per use):** C_disp_use + floor(C_disp_use) ≤ floor(w_min) (and
  C_scaffold likewise against w_walk on a walk-only scaffold site); `[rev3 A6]` on a
  shared PARAM body, M24 is added to C_disp_call.

A row failing T1/T2 takes its `unpaid` pick or is dropped; a site failing T3 gets no
dispatch; an ABSENT C_disp_call, C_disp_use, C_scaffold or (where charged) M24 fails the
test it appears in.

`[rev3 D9]` **Arithmetic conventions** (the PCU convention, `prior_cost_unify.md` §2,
copied, not linked: the kit cannot link pcrec core): integer arithmetic on set values in
fixed-point u·B (`value_e6`), no division (each comparison is cross-multiplied into
scaled numerators), every operand under a static magnitude bound asserted when the set is
loaded (a value past the bound refuses the set, it is not clamped), and a TIE DECLINES
(a T1 tie does not pay; a T2/T3 tie passes, since equality is "not measurable"). The
arithmetic grid with planted off-by-ones (`prior_cost_unify/grid.py`'s shape) is the
pay rule's check (SN-9, §8.3).

`[rev4]` **The verdict on grid2's twins (grid2read §3.6, §5): NO dispatch at B4.** Rev 3's own
branch (the last sentence of this section) is taken. The measured charges, per
activation over dig member-free single calls at N ≤ 128:

| twin (path) | charge per call | T1 | T2 | T3 |
|---|---|---|---|---|
| tw0: WALK path through the WALK+V1 scaffold (OFF, 2 forms) | −0.08 (N = 8), +1.63..+2.44 ns; UPPER +2.44 | — | FAILS (+2.48 vs the next form's 0.010 ns floor at b = 64) | FAILS (slower beyond the NULL rule in 6 of 11 dense groups) |
| tw1: V1 path (OFF, 2 forms) | −0.14, +0.18..+0.74 ns; UPPER +0.74 | R2's interval [0, 64) fails at N = 8 (+0.14 vs +0.78); holds at 32-63 | FAILS (+0.78) | FAILS (8 of 11) |
| tw2: W64 path (W32, 3 forms) | −0.29..+0.32 ns; UPPER +0.32 | — | FAILS on the upper bound (within the floors at N ≥ 64) | FAILS (10 of 11) |

The charge is NOT proportional to uses (about 1-2 µs per pass at U = 2,000 and at
U = 32,000). The scaffold alone (sc0) is ≤ 0.05% of a 64 KiB call, but its short-call
cost was not measured, so M18 is a long-call bound only. Not measured: a W16 twin, the
V1/WALK path through a 3-form chain, and charges at DFA_HAT/HYB_PF/VM_ATTEMPT. These
are B8's inputs, owed to [REGIME-TWIN].

~~`[rev2]` With M16-M18 measured by grid2's TWINS (§5.4), T1-T3 may pass at B4; the BUILT
dispatch is then re-measured by [REGIME-TWIN] (E10) as the official dispatch term, and
the twin rows go STALE by their form hash (measure_sets §2.4) and are carried stale until
that re-measure.~~ If grid2's twins fail T1-T3, no dispatch ships at B4 and B8 waits for
[REGIME-TWIN]. `[rev4]` They failed (the table above): this branch is taken. When a
dispatch is first built (B8), [REGIME-TWIN] measures it as the official dispatch term.

### 2.6 The thresholds are literals from the set (rev 1, kept) `[rev3: C5]`

The literals in `__form__*` are resolved from the active set at compile time and written
as integer constants. A different set produces different literals, so a default-set change
moves bytes and is an abi event with its census (D162 ruling 1, D166 item 1,
measure_sets §3.6).

`[rev3 C5]` **The crossover literal is read off a measured staircase, or labelled.** V1's
per-activation cost is a staircase in N (8-byte blocks plus a tail; M8), and grid1's
V1 − walk delta swings from +3.2 ns at N = 32 to −23.8 ns at N = 48, so rev 2's 36 B
(M9) is an interpolation inside a 27 ns bracket. grid2 item 2a (§5.4) measures
N ∈ {33, 34, 36, 38, 40, 42, 44, 46}; the `xover` derivation then reads the literal as
the smallest measured N from which V1 − walk ≤ −floor at every measured point above it.
A literal that cannot be read that way (a set without the points) is labelled
`INTERPOLATED(lo, hi)` in its key's provenance and its row's `basis` is DERIVED, never
MEASURED.

`[rev4]` **Read off grid2's staircase, there is no literal to write** (grid2read §3.3).
V1 − walk is negative at every measured N:

| N | 8 | 32 | 33..46 | 48 | 63 | 64 | 65 | 128 |
|---|---|---|---|---|---|---|---|---|
| V1 − walk, ns | −0.18 | −2.87 | −2.15..−3.86 | −4.98 | −6.60 | −7.25 | −5.96 | −13.54 |

The floors are 0.00-0.06 ns, and at N = 8 the margin is 4.5× its floor. The rule above
therefore gives N\* = 8, the lowest measured point: the crossover is NOT LOCATED, and
8 B is an UPPER bound. grid1's 36 B is not reproduced. One explanation is that the
compiler's V1 text differs from grid1's V1 arm; that attribution is OWED (§3.1a). R1 is
deleted for want of an interval, so no `__form__*` literal exists at B4. The same reading
gives the block at 64 B for S1 and A1 (T(63) − T(64) = +25.3 ns S1, +14.4 ns A1; M11
CONFIRMED). Below 64 B, V1 is the best form at both layers.

---

## 3. The step plan `[rev2]` `[rev3]`

### 3.1 One ordered plan `[rev3: A4, A8, A9, A11, A15, B1-B3, B6, B7, B10, B12, D10]`

R-21's ST1-ST6, R-19, R-20 (R-MS1..5) and [REGIME-EVAL]'s E-steps, merged into one
order. Kit steps are B-steps; main's prerequisites and the evaluator's steps are listed
where they gate one.

`[rev3 B1, B2, B3]` **"Zero-mover" means ARTIFACT bytes**: byte-identical to the step's
base over emit_sweep's full population on streams 1-4, at SIMD-off AND SIMD-on and under
`-fcomments`. The SIMD-on and `-fcomments` claims are made by THE instruments lane
sweeparm delivers with B0 (emit_sweep's `-fmemfn-simd` and `-fcomments` arms with their
DIFFER_PINS floors, sabotage rows S981/S982); `tests/memfn/run_simd_floor.sh` (C18) stays
a necessary but not sufficient check (it compares ON vs OFF of one build, never old vs
new). The listing streams (5 `dumps`, which carries `--list-axes`; 6 `facts`) move only
by a DECLARED delta committed with the step (`listing_declared_C7.tsv` / `listing_diff.py`'s
precedent, `docs/design/start_table/`), checked in both directions (every declared line
moved, nothing undeclared moved).

`[rev3 A15, B10]` **The KIT's steps carry no pcrec abi event through B3b; E-1 is main's.**
MF_SITE_ABI is numbered relatively ("the next number at landing"): each kit row below is
one bump from whatever main holds then, and E-1 is main's own bump between B2 and B3a.

| step | content | R-items | zero-mover? (why) | pcrec abi | MF_SITE_ABI | depends on |
|---|---|---|---|---|---|---|
| **B0** | port R17-a's seam to main: W0-W2 on every forward FIND, `decl_point`, `mf_locals` (binding `s`/`n`), `mf_defined` (`reads_table`, `includes`), the storage refusals, the set FIND sites DEFINED at file scope; `[rev3 B1, B2]` sweeparm's emit_sweep arms land with it | (R-17's seam) | `[rev3 B12]` PORT, THEN GATE: the claim is B0's own emit_sweep run on main (every arm incl. SIMD-on and `-fcomments`), not the kit branch's slot24 measurement (main differs: R-15, abi 78) | none | next | — |
| **B1** | ST1: the facts, the query and the table, unrouted. `mf_site.body` (ONESHOT from every builder) + the START hook (R-19); `[rev3 A4]` the DEFINE-TIME QUERY `mf_ask` (§4.5) and its trace-build reader shadow (each pcrec reader computed from its own row AND from the query, asserted equal); `mf_measures` on `mf_art_begin` (NULL until M0) and `consulted` from `mf_art_end` (R-MS1, R-MS2); `[rev3]` `mf_analysis` declared on `mf_art_begin`, NULL-tolerant, read by no kit row before B3a (the E-1 agreement); `mf_form_hash` (R-MS3); the reader declarations (R-MS4 keys); method cards `kit-grid@1` (R-MS5); E3: `fd_rows[]` as a `kit_table` (§1.2-§1.4: the 19 rows of the locked table; F0, F1, F2, P1 wait for B5), every `routed` bit 0, the trace-only shadow, `[rev3 B6]` the trace/test-build `measures=` lever with the synthetic sets and the committed predicted-mover manifest; `[rev3 B7]` `fd_rows[]`'s rows in `tests/memfn/rows.tsv` / `row_floors.tsv` (reach reason `pending-site:<step>`); `[rev3 D4]` the declared read list and the undeclared-read / cycle trap; `[rev3 C2]` the table self-check | R-19, R-MS1..5, PR-9 (shadow) | yes: no row is routed; the shadow writes only to the MF_TRACE build's trace; the reader shadow is `#ifdef`-only. `[rev3 A9]` No `--emit-facts` section (it rides M0, B4). NOT zero for stream 5: five `--list-axes` rows (`fd-r0`, `fd-r5`, `fd-r8`, `fd-ndisp`, `fd-d1`), a DECLARED registry delta, the identity gate's registry stream re-pinned in the same commit | none | next | B0; E3b (oracle cell) runs beside |
| **B2** | ST2: one-byte FIND routed (D1, D1c, D1w `routed` = 1). PR-1 (the candidate set as a SET term at every count, one member included, plus the table offer), PR-2 (miss and move behaviour as hooks: `empty`/`on_miss`, the `n − 1` bound, a moved-candidate hook for the DFA hat's re-seed), PR-3's kind (`site_kind`, categorical, Q-WR-8; `[rev3 A2]` DFA_ATTEMPT), `need` re-numbered with an UNSTATED zero and stated by every builder, `[rev3 A4]` pcrec's readers SWITCHED to `mf_ask` (G1's memchr test, R4, `landing` L4; §4.5) and the reader shadow retired; `[rev3 A11]` main-side: the landmark admission's input restated as facts (names and comments only); kit: KW-1 (D1), KW-2, KW-3 (the kit writes the guard, post-test, wrapper and moved hook), KW-4; `[rev3 A8]` main-side requests at the step: C10 fixtures for the one-byte rows, C17 site-manifest columns for `site_kind` | PR-1, PR-2, PR-3 (kind), PR-4 (stated), PR-9 (one-byte), KW-1..4, KW-10 | yes: D1/D1c/D1w ARE today's rules, the kit renders today's guard/post-test text, stamp VALUES stay pcrec row identities (sbscope F7). The PF comment (PR-10) is NOT changed here (Q-R17P-12, ruled: it rides B4), proven by sweeparm's `-fcomments` arm | none | next | B1; Q-R17P-15 (the query's contract) |
| (main) | E-1 = window_contract S1: `mf_analysis` filled, with the frequency kind always present (`prior-authored`, `prior-none`, `measured`); no kit edit (the B1 declaration) | — | main's own (its stamp moves: `<PREFIX>_FINDINGS` means OFFERED) | **main's event** | main's bump | window_contract rev 3 (main's, incl. C-7, C-8); B2 merged |
| **B3a** | ST3 shadow: presence spans STATED (PR-5 unpicked, PR-6 offsets with `omin` = 0 as a sound under-estimate, PR-7 member order) on the merged site, PRES unrouted; the kit's ports of the five priced picks run in the trace build beside pcrec's and must agree on 100% of sites over corpus, bench and rwquest (KW-8), `[rev3 D10]` with a per-pick FLOOR on NON-TRIVIAL sites (where the pick differs from its family default, or the choice has ≥ 2 live alternatives) and a planted disagreement per pick the comparator must catch (SN-6); PR-11's control lands (the census over collapsed hybrids + a planted collapse that drops `rmin`); `[rev3 A8]` main-side requests: DELEG_SITES' PRE row merged into the FIND rows of its route as their ENTRY use, the site manifest's use points moved, C10 fixtures (Q-R17P-18) | PR-5, PR-6, PR-7, PR-11, KW-8 | yes against MAIN-AFTER-E-1 (`[rev3 A15]`: B3a's `--ref` is main after E-1; B0-B2 re-run against it once) | none | next (the presence class, `omin`) | E-1, B2 |
| **B3b** | ST3 route: PRES rows and D2 `routed` = 1; KW-5..7 (the presence class, G-1/G-2, the applicability rule, the PRE composite's several uses inside the one site); handoff framing (a) (Q-WR-5); presence withheld at G2's linear one-attempt and LOCATE `whole` (Q-WR-4); `-fno-req-set-lead` (bit 45) retired to `--memfn=no-pres-set-lead` in the same commit, with `--emit-facts`' `used`/`why` and the `--list-axes` `req-admit`/`req-use` rows re-sourced (Q-WR-12, KW-11); PR-8 checked (the verdict precedes the edge attempt, today's order); `[rev3 A8]` the new use kind (an MF_VOCAB event) if main takes Q-R17P-18's spelling | PR-4, PR-8, PR-9 (presence), KW-5..8, KW-11 | yes for artifacts: the routed rows are the ported picks, proven equal at B3a. NOT zero for stream 5: bit 45 and two `--list-axes` axes move, plus three kit rows; a DECLARED registry delta | none | (B3a's) | B3a |
| | **FIRST DELIVERY COMPLETE (B0-B3b).** | | | | | |
| (kit) | zen4-grid2: ONE slot (§5.4), GO by D167 (Q-R17P-9 (B)) | KW-12 | — | — | — | its prep lane (the harness extension) |
| (kit) | E4 evaluator build → E4b in-sample streamed replay on grid2 → E5 pre-registration → E6 site census → E7 judge (LEAN: two windows) → E8 results | — | — | — | — | B1, E3b; grid2 |
| (main) | [KNOW-SRC] K0-K3, then [MEASURE-SET] M0 (store, `ksgen`, the embed, the `measures` kind) | (R-MS1..5 consumed) | K0-K3 yes | M0's stamp rides B4 (measure_sets §3.6) | — | — |
| **B4** | THE ROUTING COMMIT and LOCKDOWN: ~~R0, R1,~~ R5, R7, R7w `routed` = 1 and the bit deleted (`[rev4]` R0 retired and R1 deleted, with `fd-r0` retired; R5 on its new condition, §1.3a); R7 (V1 = `pf_terms_mask` over `mask8_swar`, R17-b's form, ported: `terms.c`, the W8 shared sub-block, `needs_const_subject`, N6's reserved prefix) on set covers whose SHAPE is measured `[rev4]` with a saving > eps (six shapes, §1.3a), R7w (main's walk) on the rest; `[rev4.1]` ~~whose SHAPE is measured with a saving > eps (six shapes) / R7w on the rest~~ R7 on covers of at most 2 terms (the six measured winners are 1-2 terms, and an untimed 1-2 term combination routes with them), R7w on covers of 3 or more; ~~R0 → WALK on the r2 class; R1/R2 iff grid2's twins pay T1-T3;~~ `[rev4]` no dispatch (the twins fail T2/T3, §2.5); the D169 default (§1.9); the `drop-kit-bytes` size rung with its pcrec bit 55 (`-fno-kit-size-drop`, r17c); PR-10's method-neutral PF comment; M0's `<PREFIX>_MEASURES` + `rx_info.measures`; the `--emit-facts` section `memfn` (R-20, `[rev3 A9]`) | (R-17's move), ST6 if paid, PR-10 | **NO**: the one censused mover (R17-b's movers on measured shapes, less R0's population; `[rev3 A7]` the VM hat at \|S\| = 1 is NOT in it; §3.5; `[rev4]` the six winning shapes' sites, re-counted in §3.5; `[rev4.1]` plus the untimed 1-2 term covers, whose count is OWED to the regenerated manifest, §3.5) | **ONE event**, ~~78~~ `[rev4]` 81 (main today) → the next number at landing | next (R17-b's `needs_const_subject`, the W8 sub-block) | B3b; E8 PASS or PROVISIONAL PASS (Q-REVAL-11, D167); M0 (else the stamp is a second event); the default set committed; `[rev4]` D163 add. 8's controls (MET, §3.1a) and the OWED items of §3.1a |
| **B5** | ST4: measured rows, each its own censused commit and a FORMAL row addition (post-lockdown: a ruled diff with its replay delta): ~~(a) F1 (a measured libc row may displace D1, Q-WR-1); (b) F0 NONE where E is measured;~~ `[rev4]` (a), (b) NOT BUILT: grid2 found nothing for F1 to displace D1 with and no gap where NONE pays (D77, §1.3a); `[rev3 A7]` (c) F2, the VM hat at \|S\| = 1 → V1 where grid2's VM_ATTEMPT one-byte cells show the saving `[rev4]` (+0.515), ~~with a density condition (Q-R17P-27)~~ `[rev4.1]` with NO density condition: it fires on a default compile, and its g = 2 cells (V1 +38.3% slower) are named EXPECTED losses up front (Q-R17P-27, YES; §9.2a); ~~(d) P1, only once Q-WR-9's trigger fires `[rev4]` (fired on the letter; Q-R17P-28)~~ `[rev4.1]` (d) P1 is NOT built: the trigger fired on the letter and P1 is recorded, not built (Q-R17P-28; it never fires on a default compile, D77); (e) PR-6's true `omin`; (f) Q-WR-3's posture relaxed per measured cell (D158: give-up → answer allowed, direction-checked by GIVEUP1) | PR-4 (NONE), PR-6, KW-12, KW-13 | NO where a default compile moves; a row that fires only under a measured `--analysis` bundle moves no default byte | one per default-moving commit | per row | B4; the quantities in the default set |
| **B6** | the W64 rows (A1/S1, `pf-terms-w32`/`-w16`) as guarded selector arms over `__next`; R2 and R8 routed; CANDIDATE until a bench verdict (D144 add. 4) | (SIMD thread) | SIMD-off yes; SIMD-on moves (`MEMFN_FORMS` gains the PF site's token) | none (vrun's precedent) | — | B4 (F5: the scaffold exists) |
| **B7** | ST5: the libc class deny and the three libc-free rows (the OFS BODY, MLINE's back FIND, the exact compare outside `overlap`'s lengths), KW-9 | Q-WR-7 | yes at default (reachable only under the deny) | none | — | future work (Q-WR-7, ruled) |
| **B8** | ST6: the N-dispatch rows, if B4 did not ship them | ST6 | NO | one | — | B4; [REGIME-TWIN] E10 |
| B9 | R17-b″ (§6) | R-20 (`MF_BODY_PARAM`) | — | per its own plan | — | `[rev3 A6]` E0 (`entry_rows[]`, zero-mover) → `findall_iter.md`'s short revision → its D6 panel → I1 (D163 add. 7 Q4); D165's build |

### 3.1a B4's gates as they stand (2026-10-20) and the items OWED before it `[rev4]`

Rev 3 gated B4 on three things: D163 addendum 8's layout controls, E8 PASS (or
PROVISIONAL PASS), and M0. grid2 has run and B0-B3b are routed, so here is where each
gate stands.

| gate | state | evidence | what remains |
|---|---|---|---|
| **D163 add. 8**: part layout as caller-settable controls, with the dial's positions as presets over them | **MET** | D163 add. 8-12 (decision log); plan row [ENTRY-TABLE]: E0, E0c and E1 merged (E1 is the part-layout controls, merge 7c0a90479, abi 80; review r1-e1 fixed; [ATTR-TABLE] merged 7d3587441). In the tree: `src/core/part_layout.def` and `src/gen/part_layout.c` are on this branch's base (abi 81) | Nothing that blocks B4. B4's V1 form is R17-b's ported text: `__next_candidate` and the W8 sub-block, `static inline`, with no dispatch helpers (§2.5). That is position `0`'s "as emitted" layout (D163 add. 10), and every preset cell is still `†`. B4's census runs at position `0`, so no preset interacts with it. Q-R17P-21's leaning stands: kit FORMS stay outside the part-layout table, and tuning.md §3's one sentence rides B4's spec hunk (§3.4). E1′ (each preset cell by its own measured diff) and U8 (the dial position handed to the kit as a fact) are later work |
| **E8 PASS or PROVISIONAL PASS** ([REGIME-EVAL]'s judge) `[e8min, D170]`: the MINIMAL E8 (`e8min/plan.md`, prereg bf70e5dff; E4b and E14 leave this gate) | **NOT MET, window queued** (the struck text after this cell is rev 4's plan) | Plan row [REGIME-EVAL] is not started, and no kit journal entry records E3b, E4-E8 or the converter E14 as run. Their inputs exist: E3 is B1's table (on main), and grid2 is E4b's streamed in-sample source | E4, the evaluator build. E4b, the in-sample streamed replay on grid2, which fills §9.3's numbers. E14, the converter `set_to_measures.py`, which turns grid2read's `keys.tsv` into a set. E5, the pre-registration: it carries the evaluator-parameter digest owed since 2026-10-14 and, `[rev4]` new, §9.2a's expected-loss list. Then E6, the site census, E7, the judge (the LEAN plan's two quiet windows, regime_eval rev 2.2), and E8 |
| **M0** ([MEASURE-SET]'s first step) | **NOT MET** | Plan row [MEASURE-SET] is not started. [KNOW-SRC] K0-K3, its prerequisite, are done (plan, 2026-10-17) | M0 builds the store, `ksgen`'s measures kind, the embed, `<PREFIX>_MEASURES` and `rx_info.measures`, and `--list-measurements`. If M0 lands after B4, its stamp is a second abi event (§3.1 B4 row) |

**OWED before B4 is briefed** (from grid2read §8-§9, plus rev 4's own consequences):
1. `[b4prep-close]` **CLOSED** (job `520-kit-b4prep-f3rr` green; `r17b_prime/b4prep/f3rr.md`, raw `raw_F3rr.tsv`: no sign changed, V1 -13.7% on (2,0,1) and -41.3% on (3,1,0), all values MEASURED; keys.tsv not edited). **The quiet re-time of the two load-suspect F3 cells** (grid2read §8 item 1): `f3-word-eq`
   n1m and `f3-quad` n64k with their partners, about 2 minutes.
   - **Command.** It is quoted verbatim in grid2read §8. Run it in the slot directory
     `worktrees/memfn-slot/grid2`, with `RAW_TAG=F3rr` and its own `PASS_STATUS`, so
     nothing is overwritten.
   - **What it fixes.** The (2,0,1) and (3,1,0) key VALUES, word-eq's A1 β and its twin
     charges. The signs (both shapes lose 13% and 41%) are not in doubt, so B4's picks
     do not wait on it. The SET does: the converter must not write a PROVISIONAL value
     as MEASURED, so the re-time precedes E14.
   - **Who runs it.** A heavy run, so it goes through the box lock in a slot main
     grants.
2. `[b4prep]` **CLOSED** (`r17b_prime/b4prep/v1attr.md`: the V1 and walk texts and object code are byte-identical in grid1 and grid2 on all six shared cells, so the text does not explain M9). **The V1 attribution** (grid2read §9). The compiler's V1 text (what grid2 timed) may
   differ from grid1's hand-built V1 arm, which would explain why M9's 36 B crossover
   did not reproduce.
   - **The check.** A light text compare of the two V1 arms on grid2's member-free
     cells, recorded beside grid2read.
   - **Why it is owed.** B4 ships the compiler's text, so its decision rests on what
     grid2 measured either way. The attribution closes the record before §2.6's
     upper-bound reading is cited as evidence.
3. `[b4prep]` **CLOSED** (`r17b_prime/b4prep/walkcmp.md`: identical on ten cells but for the abi number and one unread stamp macro). **Main's walk against the slot's walk** (grid2read §9 item 2). grid2's `walk` arm was
   the kit compiler under `--memfn=no-pf-terms-mask`, while B4's baseline is MAIN's walk
   (§9.2 [rev3 C6]). Owed: a byte compare of the two walks' emitted text on grid2's
   cells, before B4's G1 reads the slot's walk as main's.
4. `[b4prep-close2]` **CLOSED, manifest re-run with the rc check and the POSCOV fields** (`r17b_prime/b4prep/predicted_movers_B4_rev41.tsv` now has columns `lookup poscov hull walk0`; columns 1-8 byte-identical to b4close's; the two term-rule exceptions are NOMS rows, discarded compound-part compiles, not the rule's picks; report "Closing 2"). `[b4prep-close]` (job `521-kit-b4prep-manifest` green; `r17b_prime/b4prep/predicted_movers_B4_rev41.tsv`, summary `manifest_summary.txt`: 1766 movers (byte 658, byte-vm 1108) against fdb2's 860, the 860 all kept, 906 new; the no-key split is in the report's Closing section; two DFA-kind sites disagree with the term rule, see the report). **B4's predicted-mover manifest, regenerated.** `r17b_prime/fdb2/predicted_movers_B4.tsv`
   (860 movers) predicts R7 on grid1's shapes only, under the interim set.
   - **Why it is stale.** Under rev 4, item 3a's three shapes route too, and R0's rows
     are gone. `[rev4.1]` Under the term-count rule the untimed 1-2 term covers route too,
     and every cover of 3 or more terms stays on the walk; the regenerated manifest is
     where the split of the 54 no-key sites between V1 and the walk is OWED.
   - **The fix.** The B1 shadow re-run under grid2's keys (the converter's output, or a
     test-build lever set built from `keys.tsv`) writes the new manifest, and B4's
     movers-by-ID are held to it (§1.6 [rev3 B6]).
5. `[b4prep]` **CLOSED as far as the kit can** (`r17b_prime/b4prep/expected_losses.md`: eleven cells listed, the relay question drafted for main, the bench's cells and one rule gap owed to main). **§9.2a's expected-loss list, filled.** The relay question to pcrec-bench and the
   pcrec-side selection rule both run before any B4 timing.
6. **Not owed by B4** (grid2read §8 item 2; owed to B6, B8 and [REGIME-TWIN]):
   - a W16 dispatch twin;
   - the V1/WALK path through a 3-form chain;
   - a member-free dfa-hat cell, since (0,1,1) is DERIVED;
   - dispatch charges at DFA_HAT/HYB_PF/VM_ATTEMPT;
   - a gap grid between 2 and 8 B. `[rev4.1]` ~~This one is also F2's density condition
     (Q-R17P-27)~~ F2 has no density condition now (Q-R17P-27, YES), so the grid no longer
     gates it; it still locates libc's crossover and would sharpen F2's expected loss;
   - hex-run/word-eq find-all timing.

### 3.1b B4' as landed (lane b4p, 2026-10-21; Frank's walk ruling, D169 addendum) `[rev4.2]`

B4 was the routing commit whose content was R7's V1 default. The ruling removed that content; what landed is the lockdown and the deletions the ruling made redundant, with NO pcrec artifact byte moved and NO abi event. R7w (always the walk) is the MEASURED default for every set FIND (E8's real-text verdict, `walk_vs_v1_record.md` §5). R7, R5 and R0 are WITHDRAWN (ids reserved, never reused); their denies `fd-r5` and `fd-r0` retire (the `memfn` floor 14 -> 12, a DECLARED stream-5 delta, `r17b_prime/b4p/`); S916 retires (a design-table id, never a file), S917 reads UNREACHED (no deciding row reads a set key), S922/S1079/S1105 are re-aimed at `fd_row_decides`. Every row decides (the `routed` bit and the listing's `routed`/`locked` columns are deleted); RPT, the REPORT row, stays held for its R-26.6 preview, the one gate left. The trace-only shadow, the `FDKEY` records and the POSCOV field retire; the expected-mover set is EMPTY. Re-open trigger for a wide form: plan row [MEMFN-REGIME]. R7w now USES `site_kind` and SERVES `table_ref` REF (its arm reads the offered table), so a site that states no kind, or offers no table, stays the composer's. Not built (out of scope): the V1 form port, the `drop-kit-bytes` rung and bit 55, `--emit-facts memfn`, PR-10's comment change. The row-edit log is `memfn/docs/finder_history.md`; the report `docs/dev/lanes/b4p_report.md`.

### 3.2 Why the first delivery needs no measurement set `[rev2]` `[rev3: C11, B6]`

Rev 1 said nothing could ship before grid2 (F8). With the routing bits of §1.6 that is
no longer so: through B3b every ROUTED row is decided by a row that reads no set value
(D1, D1c, D1w, D2, P0, P2-P4, P9). The set-reading rows are either unrouted (R0, R1, R2,
R5, R7 on set sites), or cannot apply where the routed rows apply (`[rev3 B14]` R1/R2
need a fast terminal, which one-byte and presence sites never have), or are not built
until B5 (F0, F1, F2, P1). So B0-B3b need no compiled-in set, no `mf_measures` value, and
no `<PREFIX>_MEASURES` stamp. The shadow and `regime_pick` read the kit's interim TSV in
D166's shape (regime_eval Q-REVAL-10) as a TEST input only.

`[rev3 C11]` Two caveats, now stated:
- the routed PRES rows read the frequency PRIOR and carry their own constants; their
  `basis` says so (UNMEASURED-DEFAULT, §1.4);
- first-match order puts R0-R2 above D1 (`[rev4]` R0 and R1 are gone; R2, R5 and R8 remain
  above D1), so "no routed row reads a set" depends on the
  routing rule (§1.6: a site renders the table's pick only if its first matching row is
  routed). That is CHECKED, not argued: the B2 and B3b byte-identity gates also run with
  the test-build lever's synthetic sets (`all-walk`, `all-v1`, `all-wide`, and the set
  holding every derivable key), and every artifact stays byte-identical (§8.1).

### 3.3 Lockdown, and where the judge sits `[rev3: B8, B9, D7]`

D161 add. 13 puts LOCKDOWN at "the table that passes [REGIME-EVAL]'s judge and ships with
R17-b′'s routing commit". In this plan that is B4. Q-REVAL-11 orders "R17-b′'s ROUTING
commit only after a PASS or PROVISIONAL PASS"; `[rev3 B8]` D167 (Q-R17P-13, confirmed by
Frank) rules that this gates the first commit whose picks MOVE a byte (B4): B2 and B3b
route only rows that reproduce today, gated by byte identity and the shadow comparator,
and may land while the judge runs. `[rev3 D7]` Those rows lock when they are routed
(§1.8). `[rev3 B9]` LOCKDOWN is the committed digest of the table's listing plus the edit
check (§1.8); at B4 the digest covers every built row. After B4, a row edit is FORMAL: a
ruled diff with its evidence, its replay delta and its mover census.

### 3.4 Per step: abi readers, spec hunks, denies and floors, checks, main-side requests `[rev3: A8, A12, A14, B4, B7, B13]`

**Abi readers, found BY GREP at B4 (and at every later default-moving step).** The floor
of the list, from rev 1 §5.2, measure_sets §3.6 and findall_iter.md's abi plan:
- the digit's readers: `PCREC_ARTIFACT_ABI` (`src/gen/emit_dfa.c:54` on main), match_api's
  K80 `#error` text `[rev3 A12]` and the K80 block's `#define PCREC_RX_ABI_H 78` line beside
  it, its "abi is N" sentence, §6.3's stamp table and §6's `rx_info` member table,
  `docs/dev/history/abi_changelog.md`, `run_codegen_tests.sh`'s `ABI_EXPECT`,
  `run_recursion_identity.sh`'s FILEPIN / `ABI_SUBJ`, the alpha scripts' normalizers,
  `[rev3 A12]` and the sabotage anchor `tests/mech/sabotages/S693_abi_not_bumped.sh`'s
  `SAB_BEFORE` (re-aimed at every bump by its own header);
- the byte-count readers (their text cites no digit, their values move): the
  `EMITTED_BYTES` rows of `tests/codegen/manifests/m5_stage1_stamps.tsv`,
  `run_resource_tests.sh`'s K59-PREMUL pin (`a{5,25000}`), the size-term and K59/K53
  rung witnesses, the cpset manifest, the size tripwires, `run_anchored_match.sh` §5's
  drop-rung caps, emit_sweep's lowsize/lowboth `VARIANT_PINS`; all re-measured at the SAME
  `-o` basename, never re-typed;
- the mover-by-ID manifests that read PF-site or VM-hat text: the startset VM manifests;
- then the suites that count (registry, codegen, rxtsource) and `make test-codegen`
  (D94 addendum).

**Spec hunks (D80), per step:**

| step | hunk |
|---|---|
| B0 | none (no caller-observable surface) |
| B1 | `registry.md` §6¶8a (the five `fd-*` rows) and §6¶8b (floor). `[rev3 A9]` No `facts_listing.md` hunk (the section rides B4) |
| B2 | none (no byte, stamp, listing or flag moves) |
| B3b | `tuning.md` §2.40 (bit 45 retired, reserved; the kit deny named), §2.29 and §2.41 (`req-admit`/`req-use`: which rows are now the kit's, and the listing's projection); `registry.md` §6 (those axes) and §6¶8a/8b; `lib/pcrec.h`'s bit-45 comment (Q-R17P-19); `facts_listing.md` (`used`/`why` re-sourced, values unchanged) |
| B4 | `match_api.md` §6.3 (`<PREFIX>_MEASURES`) and §6 (`rx_info.measures`, beside 6¶14), §1¶7 (the W8 sub-block guard), the abi sentence, the `RX_DFA_PREFILTER` method sentences made method-neutral (setfind §11.3); `tuning.md` §2.42¶2 (the VM hat seek), §2.43¶3a, `[rev3 A14]` a NEW section for bit 55 (numbered at B4, after §2.48) and §3's dial table (the `size` cells); `limits.md` §8.4 (the `drop-kit-bytes` rung); `registry.md` floor and the bit-55 row `[rev4]` (and the `fd-r0` row removed: the floor moves +1 −1); `cli.md` (N6's refused prefix; `--list-measurements` at M0); `docs/spec/measures.md` (new, M0); `[rev3 A9]` `facts_listing.md` §3 (the `memfn` section) |
| B5 | per row: `registry.md` (its deny), `measures.md` (new keys' cards) |
| B6 | `limits.md` §8.3¶3 (guarded bound), `match_api.md` §6.3.10¶4 (the PF token in `MEMFN_FORMS`), `registry.md` |
| B7 | `registry.md` and `tuning.md` §2.43 (the libc class deny) |

**Denies and the `memfn` floor** (`registry.md` §6¶8b; main's floor is 6; each commit
raises it by the rows it adds, so the numbers below assume this order). `[rev3 B7]` Each
deny is classed for the sweep (`tests/axes/run_axes.sh` gains the `--memfn=` arm, a
request to main, Q-R17P-22): DIFFER (moves bytes on a floor population), ASSERT_ZERO
(inert at default, with the step that flips it) or REFUSES (a named refusal):

| step | rows added to `options.def` | class at landing | floor |
|---|---|---|---|
| B1 | `fd-r0`, `fd-r5`, `fd-r8`, `fd-ndisp`, `fd-d1` `[rev3 D8: R5 ∪ R6]`: one per built row the evaluator can score (regime_eval §5.2) | ASSERT_ZERO (no row routed), except `fd-d1` from B2 | 6 → 11 |
| B2 | — (`fd-d1` flips) | `fd-d1`: DIFFER, floor = the one-byte DFA/hybrid population (its OFF arm is D1w, WALK, `[rev3 A17]`) | 11 |
| B3b | `fd-pres-g1`, `fd-pres-pick`, `pres-set-lead` | DIFFER (floors per pick, §3.1 B3a) | 11 → 14 |
| B4 | `pf-terms-mask` (the V1 FORM deny, R17-b's); ~~`fd-r0`/`fd-ndisp` flip~~ `[rev4]` `fd-r0` RETIRED with its row (§1.3a); `fd-ndisp` stays ASSERT_ZERO (no dispatch pays; R1 deleted, R2 is B6's); `fd-r5` stays ASSERT_ZERO (no default compile states a regime) | DIFFER (`pf-terms-mask`) | 14 → ~~15~~ `[rev4]` 14 (+1 −1) |
| B5 | ~~`fd-libc-m`, `fd-none` (PAIR: its force spelling is how a later slot times NONE),~~ `[rev3 A7]` `fd-vm-hat-1b`, ~~`fd-pres-priced` (`[rev4]` only if Q-R17P-28 builds P1)~~ `[rev4.1]` (`fd-pres-priced` is NOT added: P1 is not built, Q-R17P-28), each with its row | per row | +1 each, `[rev4.1]` so +1 at B5 (`fd-vm-hat-1b`) |
| B6 | `pf-terms-w32`, `pf-terms-w16` | DIFFER at SIMD-on | +2 |
| B7 | `libc` (the class deny) | REFUSES on DFA_ATTEMPT until its back row exists, else DIFFER | +1 |
| B9 | `fd-r3a`, `fd-r3b`, `fd-r4` | per row | +3 |

pcrec's own registry: bit 45 retires at B3b; bit 55 is taken at B4 (free on main: B3
took 56), leaving bits 57-63 (seven, above [IFACE-PUSH]'s ≤ 4 trigger). `[rev3 B13]`
emit_sweep's maintenance is part of each step: B3b removes bit 45's two DIFFER_PINS rows
(`(14, 0, "é{2}cat")`, `(16, 0, ...)`, both bases) and adds the three PRES denies' arms;
B1's five denies get ASSERT_ZERO arms, flipped to DIFFER with floors at their routing
step; B4 adds `pf-terms-mask`'s `[rev4]` and removes `fd-r0`'s arm with the row; so `--extra` never runs a kit deny without a floor.
Whether `PCREC_NO_REQ_SET_LEAD` stays in `lib/pcrec.h` as a reserved, ignored name is
Q-R17P-19.

**`fd_rows[]` in the kit's row-reach machinery** `[rev3 B7]`: B1 adds the table's rows to
`tests/memfn/rows.tsv` (the ROWCON/N4 manifest: "a row added to the kit adds its line
here in the same commit") with reach reason `pending-site:<routing step>`, and to
`row_floors.tsv`; each routing step flips its rows to `pcrec` with a census floor and a
witness.

**Checks per step (G1 = pcrec's gate, G2 = the kit's generated space):**

| step | G1 | G2 and other checks |
|---|---|---|
| B0 | emit_sweep full population, streams 1-4, every arm incl. SIMD-on and `-fcomments` (sweeparm), 0 movers, against MAIN | R17-a's refusal cases (window fields, storage) ported |
| B1 | emit_sweep 0 artifact movers; stream 5's DECLARED delta; the trace compare: new `fd` shadow records only (B1 retires none) | R-MS1's bar (every finder row run with NULL, with each key absent in turn, with the full set; no kit row reads a `pcrec.` key); R-MS2's bar; R-MS3's fixtures; the table self-check (`basis`, picks, last rows); the read-list trap (SN-3); the query/define agreement (§4.5); the blinded oracle E3b and, at E4, the agreement check (regime_pick vs the shadow on every FIT cell) |
| B2 | emit_sweep 0 artifact movers incl. `-e utf8`, `--engine=vm`, the start arms, SIMD-on, `-fcomments`, `[rev3 C11]` and under the lever's synthetic sets; `[rev3 B17]` plus rwquest's and the bench's patterns (`--patterns-file`) and the prefix sweeps; the routed-record floors (§1.6); `[rev3 B4]` a DECLARED trace delta: the `cand_rows[]` records G1, R4 and L4 retire or re-source (the readers now read `mf_ask`), with `make test-cand-oracle` ("every row reached", its 42 witnesses), `inventory_check` and the start-table `reads` DAG re-pinned in the same commit | KW-10's one-byte family: the count rule, NONE's answer identity at DFA consumers (shadow), NONE refused where `need` is REQUIRED, MLINE's generic shape (D1c); the reader shadow's last run before it retires |
| B3a | the five-pick shadow: 100% agreement, reported per pick, with per-pick floors on non-trivial sites (`[rev3 D10]`) | PR-11's control (shares no source with the req walk); SN-6's planted disagreements |
| B3b | as B2 (artifacts, synthetic sets, rwquest/bench, prefix sweeps); stream 5's DECLARED registry delta; `[rev3 B4]` the declared trace delta for `PRESENCE`/`NEXT`'s `req-admit`/`req-use` records, with the startset readers and test-cand-oracle re-pinned | KW-10's presence family (absent-at-end discovery, REQUIRED-all on proof routes, re-asked ranges with `omin` < 0); plants reaching NON-DFA routes only (a DFA-route-only green is vacuous) |
| B4 | G1 timing at both layers (§8.1) on the pcrec-side mover population; the mover census by ID (§3.5) held to B1's predicted manifest; `[rev3 B15]` every kit deny at once == main modulo the committed normalizer; `[rev3 C1]` the one-byte and presence populations 0 movers under the set holding every derivable `xover` key | G2's setfind family; `make test-memfn-sets` (§8.2); measure_sets §8.1 (answers under every committed set and the synthetic extremes, REACH floors per arm on generated boundary subjects) |

**Main-side requests, per step** `[rev3 A8]` (the kit files nothing on main; main files
the request, D78). The merge changes three things C10 and C17 read:

| step | DELEG_SITES (`src/gen/memfn_sites.def`) | C10 (`memfn_sites.c` fixtures) | C17 (`tests/memfn/site_manifest.tsv`) | MF_VOCAB |
|---|---|---|---|---|
| B2 | PF and MLINE rows unchanged (op `MF_OP_FIND`); the one-byte predicate becomes a SET term (PR-1) | a fixture per one-byte kind (DFA_SCAN, DFA_HAT, HYB_PF, VM_ATTEMPT-presence, DFA_ATTEMPT) | the `site_kind` column | no move |
| B3a | the PRE row (`MF_OP_ALL_PRESENT`, ON_MISS\|ASSIGN, `MF_USE_DISCARD`; SETREST and VERIFY ride it) merges into the FIND row of its route as that site's ENTRY use; a presence-only site (no-DFA VM, hybrid `_search_run`, `attempt_entry` without MLINE) keeps a FIND row with no span 0 | fixtures for the merged rows and a presence-only row | the PRE rows' use points (`req_site_define`, `pcrec_emit_req_byte_check`, `emit_req_reentry_use`) move under the merged sites | a new use kind (proposed `MF_USE_ENTRY`) is a vocabulary event; Q-R17P-18 |
| B3b | the merged rows routed | the ALL_PRESENT renderers (`precheck`, `precheck_assign`, `precheck_assign_byte`) as the ENTRY use's renderings (KW-7) | `delegated` on every merged row | — |

### 3.5 Which artifacts move at B4 (rev 1 §5.1, re-based on main) `[rev3: A7, C3, B16]`

Rev 1's census (`r17b_prime/out/census_shapes.out`) counted R17-b's movers on the kit
branch: 996 byte / 2,910 byte-vm artifacts, one stateful site each, of which R0's ≥ 2
RANGE population is 219 / 243 (mostly `\w`, shape (3,0,1)), and the one-member covers
(0,1,0) 157 / 1,673. `[rev4]` The bullets below are revision 3's prediction. Where they
name R0 or a dispatch, the `[rev4]` restatement at the end of this section supersedes them;
`[rev4.1]` so does it where they say the 54 sites "stay on R7w" or call a count an upper
bound set by a shape's saving key.
Against MAIN at B4 `[rev3]`:
- `[rev3 C3]` the set sites outside R0 move to V1 behind `__next` (plus the dispatch if
  paid) ONLY where their cover shape's saving key is in the default set and exceeds the
  regime floor (R7). Byte arm: of 620 candidate movers, 300 sit on grid1's measured
  shapes ((1,0,0) 285, (0,1,1) 15) and 266 on grid2 item 3a's three shapes ((0,2,0) 132,
  (0,0,1) 84, (1,1,0) 50); the other 54 stay on R7w (main's walk). byte-vm arm: of 994,
  509 sit on grid1's shapes; the share of the other 485 on item 3a's shapes is re-counted
  at B4. Each is an UPPER bound: a measured shape whose saving does not clear its floor
  stays WALK. B4's census reports movers split by shape measured / not measured;
- `[rev3 C4]` RESTATED at B2 (lane fdb2fix, the kit manager's ruling 2026-10-16): the
  R0/R7 floor is the regime the saving keys' operands were measured in, the `beta`
  slopes' streamed single-call regime, `kit.eps.streamed.slope` (0.173%), and not
  streamed find-all's `kit.eps.findall.l64k` (3.365%), which B1 had spelled. Under it
  the (2,0,0) cover's measured saving (1.385%) clears the floor, so R0 does not hold
  there and R7 picks V1: grid1's measured shapes predict **285 + 15 + 20** byte-arm
  site movers ((1,0,0), (0,1,1), (2,0,0)) and 495 + 25 + 23 on byte-vm; 860 (arm,
  pattern) movers in all (fdb1's B1 manifest read 817). The committed manifest B4 is
  held to is `r17b_prime/fdb2/predicted_movers_B4.tsv`; fdb1's is kept unedited as
  B1's record. The (2,0,0) sites are R0's population (≥ 2 RANGE terms), so they come
  out of the next bullet, not out of the 620;
- R0's sites stay byte-identical to main except the abi digit and the new stamp (bare
  walk), or take the walk-only scaffold if T3 passes (§2.5); `[rev3 C4]` except the
  (2,0,0) cover's 20 / 23 sites, which move to V1 (above);
- `[rev3 A7]` the VM hat at \|S\| = 1 (112 / 8 / 1) does NOT move at B4: D1w keeps
  main's table walk; F2 moves it at B5 on measurement;
- one-byte sites (D1, D1c), the one-member covers and presence (P-rows) do not move;
- every artifact moves by the abi digit and `<PREFIX>_MEASURES` (`""` where nothing
  consulted, measure_sets §3.5).

These counts are re-taken against main at B4 by a pcrec-side reader of the emitted C (the
census never reads the kit's `moved`). `[rev3 B16]` That reader is NOT
`census_shapes.py`, which reads the `<stem>__mask` R17-b emits (absent on main): B4's
pre-move census is `r17b_movers.py`'s independent cover search over main's artifacts
(its cover search shares no code with `terms.c`, checked at B4), and the post-move census
reads B4's own emitted masks. R0's firing population is itself an upper bound (R0 also
needs its saving key below the floor). The utf8 arms' split (964 / 2,907 R17-b movers)
was not re-run for R0.

`[rev4]` **The prediction restated under §1.3a.** No dispatch ships, so a mover is a set
site ~~whose shape's V1 saving key is > eps~~ `[rev4.1]` whose cover has at most 2 terms
(Q-R17P-26), and it moves from main's walk to V1 behind `__next` with no form byte.
- **Byte arm.** The six winning shapes (1-2 terms each) give (1,0,0) 285, (0,1,1) 15,
  (2,0,0) 20, (0,2,0) 132, (0,0,1) 84 and (1,1,0) 50: **586 site movers**, ~~an upper
  bound~~ `[rev4.1]` and now a FLOOR, since the rule has no saving-above-eps test left
  to fail them and adds the 1-2 term share of the untimed sites below. Rev 3
  counted 320 on grid1's shapes and held item 3a's 266 conditional on grid2. They stay
  on R7w (main's walk, zero-mover):
  - the r2 population's losing shapes, which is R0's 219 less (2,0,0)'s 20 (every
    cover with two or more RANGE terms other than (2,0,0) has at least 3 terms, so the
    term-count rule sends all of them to the walk without a per-shape key);
  - ~~the 54 sites on shapes with no key (pending Q-R17P-26).~~ `[rev4.1]` the 3-or-more
    term share of the **54 sites on untimed shapes**. The other share (1-2 terms) moves
    to V1 with the 586. The split of the 54 is OWED to the REGENERATED mover manifest
    (§3.1a item 4); this revision does not compute it, and no number here assumes it.
- **Byte-vm arm.** 495 + 25 + 23 on grid1's shapes. Item 3a's share of the other 485 is
  re-counted at B4 as before; `[rev4.1]` the rest of the 485 route by term count too, and
  their split is likewise OWED to the regenerated manifest.
- **Not movers.** The VM hat at |S| = 1, every one-byte site, every presence site, D2.
- **The manifest.** B4's census is held to the REGENERATED manifest (§3.1a item 4),
  never to fdb2's 860.
- **Size.** Each mover takes V1 alone: +256..+608 B per site over main (§3.6), with no
  dispatch increment.

### 3.6 Size (rev 1 §5.4, MEASURED on hand twins, SIZE ONLY; kept)

`gcc -O2 -c`, `.text` + `.rodata`/`.data`, use-branch twins, thresholds 36/64:

| cell | main (walk) | R17-b (V1) | WALK+V1 | WALK+A1 | WALK+V1+A1 |
|---|---|---|---|---|---|
| dig | 2,436 | 2,692 | 3,076 | 3,844 | 4,292 |
| bounded | 2,372 | 2,794 | 3,204 | 3,972 | 4,612 |
| dfa-hat | 4,196 | 4,708 | 5,028 | 5,860 | 6,564 |
| vm-hat | 1,358 | 1,966 | 2,382 | 3,758 | 4,718 |
| hex-run | 2,572 | 2,892 | 3,276 | 4,236 | 4,748 |
| vm-hat-1 | 1,423 | 1,871 | 2,287 | 3,535 | 4,367 |

V1 alone (B4 with no dispatch) is R17-b's +256..+608 B per site over main; a paid
dispatch adds +320..+416 B more; the SIMD-on forms are guarded (outside the caps,
counted by `SIMD_GUARDED_BYTES`). `pf-terms-mask` is `MF_SZ_ADDS`, so the size ladder's
`drop-kit-bytes` rung denies it on a cap refusal and the site takes the walk.
`[rev3 D5]` These are position `0`'s sizes (the helpers as emitted, `static inline`); the
size positions of D163 add. 7 would share them (§2.2), and their cells are the dial's,
measured by its own diffs, not here.

---

## 4. The contract: the one window request `[rev2]`

Every field below is a FACT (D157): pcrec states what is true of the sub-problem it
hands over, never a method. Spellings are PROPOSED; the layout is the kit's to finalize
(window_contract §3.1's convention). Each piece cites the winreq C-item it implements;
§4.8 maps all sixteen.

### 4.1 The site: span 0 and the PRESENCE spans (C-1, C-2, C-4, C-16) `[rev3: A1, A5, A20]`

One `mf_site` per search-entry ACTIVATION (§1.1, §2.1 `[rev3]`). It carries:
- **span 0** in `pred`: the candidate set as a SET term at every count, one member
  included, with the table offered (`table_name`, PR-1). A handoff landmark longer than
  one byte is a RUN term (D2). Absent on a presence-only site (`pred.nterm = 0`).
- **presence spans** in `preds[]`, each a new span class:

```c
typedef enum { MF_SPAN_UNSTATED = 0, MF_SPAN_BOUNDED, MF_SPAN_CONTEXT,
               MF_SPAN_PRESENCE } mf_span_class;       /* appended to mf_pred, B3a */
/* PRESENCE only:
 *   omin          the smallest offset, from the MATCH START, at which an occurrence
 *                 can begin; >= 0 (presence bytes lie inside [start, end): lookaround
 *                 bodies are never in the necessary set); 0 is a sound under-estimate
 *                 (PR-6) and is what B3a states; the true omin is B5's (PR-6 at ST4)
 *   member_order  for a one-byte span split from a necessary set: its position in
 *                 pattern order (PR-7), the fact the leftmost/rightmost tie reads
 *   window_stated 0 (a presence span has no omax: C-1)                              */
```

And on the site, one new fact, `head_max` (`h_max`): the largest distance from a match
start to span 0's start. It is 0 for a head-0 origin and K for the handoff's landmark
origin (PR-6's "K as h_max"); pcrec keeps `c − K` and the utf8 round-up in its own text
(window_contract §2.1). The kit needs it only for the per-candidate cut (§4.4).

- **Rules** (C-2): a PRESENCE span states `window_stated 0`, `omin ≥ 0` and a `need`;
  `move_back`/`overshoot` are not read for it; `MF_MOVE_UNBOUNDED` stays permanently
  refused for every class (D161 add. 5). The sequence rule (`spans_seq`) does not apply to
  presence spans: they carry no pairwise distance.
- **Unpicked** (PR-5): every necessary-set member is its own one-byte presence span, and
  the whole run is one span with its mask. The pick, the window and set-leads are the
  kit's rows (P3, P4), no longer pcrec's encoding. `req_set` is asked only where today
  asks (Q-WR-12).
- **Context predicates** stay as window_contract §2.2 and §2.5 have them `[rev3 A5]`:
  MLINE's `{\n}` one byte before the origin is a context PREDICATE, not a span (D161
  add. 7: "context checks are not spans"), never presence, and the edge stays pcrec's.
  MLINE's site has NO span 0 (`pred.nterm = 0`); its stop is the context byte, which slot
  FIND's row D1c decides. Rev 2 gave it "span 0 `need` OPTIONAL" in §4.6; withdrawn.
- **C-4** follows: no site keeps the ALL_PRESENT → VERDICT reply. ALL_PRESENT's
  renderers (`precheck`, `precheck_assign`, `precheck_assign_byte`) survive as the
  merged site's ENTRY-USE rendering at B3b (KW-7), not as a separate reply type.

`[rev2]` **Why `omin` is measured from the match start and not from span 0.**
`[rev3 A20]` This DEPARTS from main's filed contract: R-21 PR-6 says "offsets relative to
the chosen origin" and window_contract C-1 says "`omin ≥ −h_max` when the origin's head is
bounded". It is therefore a QUESTION to main (Q-R17P-17: amend PR-6 and C-1), not a
silent refinement; the reasoning for it:
Presence is a fact of the MATCH, and the binding is per ACTIVATION (§4.4): every match of
an activation begins at or after the activation's start (R-19's START hook), and every
presence byte lies inside the match. So the verdict window is `[start + omin, n)`, which
at `omin = 0` is exactly today's `[posvar, n)` (zero-mover), and is sound for a landmark
origin with no read before `start`. Measured from span 0, the same window would be
`[lo − h_max, n)`: wider than today's (a mover), and reading below the call's floor.

### 4.2 The facts R-19 and R-21 add to the site (PR-3, PR-4; C-11, C-14) `[rev3: A2, A6, A21]`

| fact | values | stated by | step | why |
|---|---|---|---|---|
| `body` (R-19) | `MF_BODY_ONESHOT`; `[rev3 A6]` `MF_BODY_PARAM` plus the mode-expression hook at R17-b″ (R-20; `MF_BODY_ITER` withdrawn); 0 = UNSTATED, N/M rows skip | every builder (§2.1's table: the DFA body, the VM hat's `_search_run`, `attempt_entry`, both hybrid sites, the relocate path; `[rev3 A21]` R-19's list amended, Q-R17P-16) | B1 | key M: R1/R2/R8's "one-shot"; the M24 charge on a shared PARAM body (§2.4) |
| START hook (R-19) | the text of the activation's origin at the storage point | the same builders | B1 | key N (`n − start`); the presence window (§4.1) |
| `site_kind` (PR-3, Q-WR-8) | §4.3's kinds; 0 = UNSTATED | every PF/MLINE/PRE builder | B2 | the rows' gate contracts (§1.2): D1 excludes the VM hat's seek role (Q-R5); F0 excludes the give-up-exposed kinds; g\* is per kind (R5) |
| `need` re-numbered (PR-4) | `{UNSTATED = 0, REQUIRED, OPTIONAL}`, stated on every span | every builder | B2 (stated), B3b (binds presence) | the EFFORT fact (C-14): REQUIRED exactly where dropping, narrowing or answering unconstrained could let a budgeted engine do more work on an input the denied build answers (D158) |
| `head_max` (PR-6) | bytes | the PRE builder; 0 elsewhere | B3a | §4.1 |

- **`consumer` is REPLACED, not dropped** (C-11, Q-WR-8 ruled): window_contract's S3
  retires `mf_site.consumer` (`MF_C_ENGINE` everywhere, unread) with `site_kind` as its
  replacement. Until S3 both exist and `consumer` stays `MF_C_ENGINE`.
- **What is NOT stated** (Q-WR-4, ruled): pcscope's three further consumer facts (one
  start, body decides presence, skipping barred) are not sent at B3; pcrec withholds
  presence on those sites instead. `use = DISCARD` already exists for the Q10 collapsed
  hybrid.

### 4.3 The consumer kinds `[rev3: A2]`

| `site_kind` | what consumes the candidates | budgeted? | sites |
|---|---|---|---|
| DFA_SCAN | a DFA body's forward scan (restart at the candidate) | no | PF, PRE on a DFA route |
| DFA_HAT | a seeded DFA scan that RE-SEEDS where the skip moved (`pf_emit_moved_reseed`) | no | `first-*-bounded` |
| HYB_PF | a VM hybrid's inner DFA prefilter (exact or count-collapsed) | the VM behind it is; the prefilter is not | PF inside a hybrid; PRE on a hybrid route |
| VM_ATTEMPT | the VM attempt loop (the hat's seek, and the entry of a no-DFA VM route) | YES (steps, frames, work per call) | VM hat; PRE on a no-DFA route |
| DFA_ATTEMPT `[rev3 A2]` (rev 2's ATTEMPT_PRED, widened) | ENG_ATTEMPT's attempt loop: MLINE's predecessor seek (a context FIND, row D1c) and the attempt entry's presence pre-check (`attempt_entry`, the third caller of `pcrec_emit_req_byte_check`) | no (a DFA attempt) | MLINE; PRE at the attempt entry |

`[rev3 A2]` The kind is the CONSUMER, so one kind covers both uses on an ENG_ATTEMPT entry:
nothing about the attempt loop is budgeted, so its presence is OPTIONAL (§4.6). R-21
PR-3's five kinds lack it; main is asked to rename ATTEMPT_PRED and add the third caller
(Q-R17P-16). Its population was not counted by pcscope and is owed at B2's census.

### 4.4 The reply: one stream, bound at range level (C-3, C-5, D161 add. 7 and 14) `[rev3: A3]`

- **The stream** (D161 add. 7): candidates are span 0's starts, COMPLETE, ASCENDING, no
  repeats; stateless (`result`) or stateful (`next_candidate(&state, lo)`), the same
  sequence.
- **Range-level binding (C-3 i).** If a REQUIRED presence span has no occurrence in
  `[start + omin, n)`, the stream is EMPTY.
- **EMPTY = NOMATCH** (D161 add. 14's clarification). On a site with a context
  predicate, NOMATCH for the covered positions; pcrec's edge attempt covers the rest
  (window_contract §2.4).
- **Decided first (C-3 ii, G-2).** EMPTY or the first element is returned only after every
  REQUIRED presence span is established over its whole window. Today's order already does
  this (the pre-check at the entry); the entry use renders it. `[rev3 A3]` On a VM hybrid
  the presence site in `_search_run` returns its verdict before `_search_run` calls the
  static `_prefilter` for the first time, so the find site's first element is never
  yielded before the verdict, across the call boundary.
- **One verdict per activation** `[rev2]`: later uses in the same activation (the loop's
  next candidate, the handoff's re-entry) yield candidates only and never re-verify.
  `[rev3 A3]` On a hybrid each `_prefilter` call is a new activation of a FIND-ONLY site,
  which has no verdict to repeat; the verdict is the `_search_run` site's, once.
  pcscope §3.2's re-asked-range rule (from `lo′ − h_max`) is the ITERATOR's, where a
  verdict is carried across calls (§6), not a one-shot rule.
- **Per-candidate use is a PERMISSION (C-3 iii, Q-WR-6).** A candidate `c` whose implied
  match start `c − h` cannot reach an occurrence (no occurrence in
  `[c − head_max + omin, n)`) begins no match; the kit MAY end the stream after the last
  occurrence `p` at `c > p − omin + head_max`. Never required; exercised only by the
  iterator (§6), after D165's build.
- **The unconstrained reply is a range (C-3 iv).** "Every position in `[lo, hi′]`" with
  `hi′ = n` is legal iff span 0 is OPTIONAL or absent (G-4): it is F0 NONE on a DFA
  consumer, and it is a presence-only site's reply (today's VM entry runs every position
  after the pre-check). The tighter `hi′ = p − omin + head_max` is the permission above.
  No output hook is added: in this delivery `hi′ = n` everywhere, so the consumer runs to
  `n` as today; a `result_hi` hook is FILED with its trigger (the iterator's cut).
- **The handoff (C-5, Q-WR-5 (a)).** Origin = the landmark: span 0 is the landmark
  (D1 for one byte, D2 for a run), presence is fused into the stream (an exhausted
  stream is the landmark's absence), and pcrec keeps `max(lo, c − K)`, the utf8 round-up
  and the re-entry. The re-entry is a further USE of the same site at `scan_position`
  (C-5's row in window_contract §2.5 is rewritten accordingly).

### 4.5 The define-time QUERY: facts in, the form CLASS out (PR-9, KW-4) `[rev3: A4, A11, A18, A19, D4]`

`[rev3 A4]` **Why rev 2's channel cannot work.** Rev 2 had the kit report the proven facts
"at `mf_define`" in `mf_result`. On main, `mf_result` is the out-parameter of
`mf_use`/`mf_emit` only (`mf_define` returns a handle), and the readers run during pcrec's
ROW SELECTION, before any site exists: `start_landing_applies` is a RECOVER row predicate,
`req_landmark_admits` a NEXT row predicate, G1 runs inside the admission
(`req_dominated_applies`), and the PF site itself is built only at its use
(`pcrec_emit_find` → `mf_emit`, inside the scan loop). A fact produced at define arrives
after the decision that needs it. D167 add. 1 (A4) notes the direction; this section is
the CONTRACT PROPOSAL main reviews (Q-R17P-15).

**The query** (PROPOSED; `memfn/include/memfn.h`):

```c
/* The form CLASS of a site: facts about the text the kit WOULD render for it, never
 * the text or the form's name (D157). Answers for the OFF variant (§1.5 rule 1),
 * which every layer inherits. */
#define MF_CLASS_V 1
typedef struct {
    uint8_t  v;            /* MF_CLASS_V, written by the kit                          */
    uint8_t  exists;       /* 1 iff a search text precedes the consumer at its use;
                              0 for NONE                                               */
    uint8_t  libc_free;    /* 1 iff the text calls no C-library function               */
    uint8_t  proven0[32];  /* bitset: every candidate's byte at offset 0 lies in it;
                              all ones = nothing proven                                */
    uint32_t includes;     /* MF_INC_* bits the text needs (MF_INC_STRING: <string.h>) */
    uint8_t  npres;        /* presence spans answered (0 before B3b)                   */
    mf_link  pres[MF_MAX_PRES]; /* per presence span: the chain-link attributes
                              (verify, proven_by, member, order; §1.4)                 */
} mf_class;

/* Ask the class of `site` under `def` (the define hooks the row contracts read) and
 * the art's state (denies, measures, analysis, layer). PURE: writes no text, defines
 * no handle, registers no helper, changes no art state (the MF_TRACE build records
 * one "ask" line). Returns 0, or exactly the refusal mf_define would return. */
int mf_ask(const mf_art *art, const mf_site *site, const mf_hooks *def, mf_class *out);
```

**Its rules:**
1. **Pure.** A site asked and never defined (a selection's rejected alternative) leaves
   nothing behind: no helpers to discard, no handle to use (D4's "what happens to a
   discarded site's helpers": nothing exists to discard).
2. **Agreement.** `mf_define` of the same site, under the same hooks and art state,
   renders text whose class EQUALS the ask's: `mf_defined` gains the `mf_class` it
   rendered, the trace build re-asks at define and asserts equality, and G2 asks then
   defines every generated site and compares. SN-2 plants a lying `exists` (§8.3).
3. **What it answers for.** The class of what will actually be RENDERED: before a row is
   routed (§1.6) that is the pre-table form, after it the table's pick. So a reader's
   value is today's until its group routes, and the switch of a reader at B2 is
   zero-mover by construction (proven by the B1 reader shadow, rule 6).
4. **The order** (`[rev3 D4]`). Every site whose class a selection reads is ASKED before
   that selection; sites are DEFINED where they are today (R17-a's points, §2.1). Asks
   are free of order among themselves (pure).
5. **Declared reads.** pcrec's selection DAG (`CandNode.reads`, stc5b's C5b mechanism)
   gains one edge kind, "reader → ask(site X)": X's description depends only on the
   FIRST slot's selection (the start set or the landmark), so each edge points from
   PRESENCE or RECOVER back to FIRST, never forward, and no cycle can close through the
   kit. The kit's own cross-slot read (PRES P2 → FIND's `proven0`) is declared in the
   kit's table. The trace build traps an undeclared read: an `mf_ask` issued while the
   selection that fixes the site's description is still open, or a reader reading a
   class field it did not declare (SN-3, §8.3).
6. **Steps.** The query and its trace-build reader SHADOW land at B1 (each reader
   computed from its own row AND from the class, asserted equal over emit_sweep's
   population); B2 switches the readers to the class and retires the shadow. So the
   query belongs IN B1 (a kit API addition, inside B1's MF_SITE_ABI bump, no pcrec byte),
   and B2 depends on it and on main's review (Q-R17P-15).

**pcrec's readers, each mapped to one class fact** (no reader receives a form name):

| reader (main) | reads today | reads after its step | from |
|---|---|---|---|
| G1 (`req_dominated_applies` → `req_byte_dominated_by`, `dfa_cand_scan`) | pcrec's own scan row and byte | `proven0` (and `exists`) of the start-search site, from the ask, B2; at B3b G1 IS the kit's row P2 (reading FIND's `proven0` inside the kit) and pcrec's reader retires | ask |
| R4 (`pcrec_dfa_cand_ppm`) | the scan's candidate set, and "no scan means 10^6" | `exists` = 0 ⇒ 10^6 (a5inv's deliberate branch, now on the fact); else the mass of `proven0` under pcrec's own prior | ask |
| `landing` L4 (`start_landing_applies`) | whether the NEXT block stores `landing_position` | `exists` (0 ⇒ L4 declines; sbscope §2's second option, chosen because it keeps no store on every byte) | ask |
| the handoff K admission (`req_landmark_admits`) | the displaced start-byte row's scan | `[rev3 A11]` NO kit fact: the start set's PRIOR mass, h and K, all pcrec's (D167 add. 1). It is the D157 exception rev 2 did not name, restated at B2 (main-side, zero movers) | — |
| `<string.h>` | whether `memchr` is emitted | `includes` from `mf_defined` (R17-a, B0): the include line is written after every site is defined, so the define result suffices; the class's `includes` equals it (rule 2) | define |
| the stamps (`REQ_WHY`, `REQ_HANDOFF`, `dfa_prefilter_name`, `REQ_BYTE`, `REQ_RUN`) | pcrec's rows | written after define, from `mf_defined`'s class. `[rev3 A18]` `REQ_WHY` reads pcrec's OWN withholding reason first (`one-attempt`, LOCATE `whole` under `dominated`, `compound`, `none`: no presence span is sent there), then the presence links (`proven_by` ⇒ `dominated`; `verify` with a lowered `order` ⇒ the set-leads' `emitted`; `verify` ⇒ `emitted`). The rest stay pcrec ROW identities with unchanged values (sbscope F7) | define |

`[rev3 A19]` **`exists` is not independent of `proven0`.** On this delivery's forms,
`exists` = 0 exactly when `proven0` is all ones (NONE proves nothing, and no form scans
the full byte set). It is kept as its own bit because L4's question is "is there a search
text at the use" (a store per landing), which `proven0` answers only through that
coincidence, and because D167 add. 1's A4 note names it in the query's vocabulary. The
trace build asserts `exists = 0 ⇒ proven0 = all ones` at every ask; if main prefers to
derive it, L4 reads `proven0` instead (Q-R17P-25).

The rename of the method-named count fact (`DFA_PF_MEMCHR`, `use_memchr` → the count it
is) rides B2 (PR-9).

### 4.6 The K65 obligation, per consumer (C-10, C-12, C-13, C-14; G-1..G-5) `[rev3: A2, A5]`

| consumer (§4.3), route | span 0 `need` | presence `need` | NONE (unconstrained) | what an EMPTY stream must preserve | give-up posture |
|---|---|---|---|---|---|
| DFA_SCAN, DFA body | OPTIONAL | OPTIONAL | legal (no budget) | nothing (the DFA proves absence itself) | — |
| DFA_HAT | OPTIONAL | OPTIONAL | legal | nothing | — |
| HYB_PF, exact or count-collapsed front | OPTIONAL | OPTIONAL: every DFA-scan front enforces the necessary set and run (W4; `nfa.c`'s `X{m,n} → X{min(m,1),}` keeps every `rmin ≥ 1` byte), held by PR-11's control | legal | nothing | — |
| DFA_ATTEMPT `[rev3 A2, A5]`: MLINE's seek | no span 0 (a context stop, row D1c) | — | answer-safe, but no row until measured (Q-WR-2) | — | — |
| DFA_ATTEMPT `[rev3 A2]`: the attempt entry's presence (`attempt_entry`) | — (or MLINE's context stop) | OPTIONAL (the DFA attempt is not budgeted) | — | nothing (the DFA attempt proves absence itself) | — |
| VM_ATTEMPT, VM hat, no DFA front | REQUIRED (D148 Q6; G-4; W3) | REQUIRED (K64, K65, K66; W1, W2) | NOT legal (F0 excludes the kind; the applicability rule refuses it besides) | every give-up → NOMATCH conversion the pre-check makes today (G-1): every member, the WHOLE run | through B3b: no move in either direction (Q-WR-3); from B5: D158 per measured cell (answer → give-up never; give-up → answer allowed, direction-checked by GIVEUP1) |
| VM_ATTEMPT, presence-only (no hat) | — | REQUIRED | the range `[lo, n)` (today's reply) | the same | the same |
| framed one-attempt VM (K64) | — | REQUIRED | — | the same | the same |
| linear one-attempt VM (G2) and LOCATE `whole` | — | WITHHELD (Q-WR-4) | — | — | — |

The witnesses (pcscope §2.3) become the reach witnesses of §8.3's plants: W1
(`(x?)([a-z]+)+Z.@\1`, `a`×31+`Zb`: nomatch today, give-up under `-fno-req-byte`), W2
(the same under `(?m)^`: the verdict must precede the edge attempt, PR-8), W3
(`(?=(?:a|b|x)*c)x`, `--engine=vm --backtrack-frames=8`: a match today, `frames` under
`-fno-start-set`), W4 (the collapsed-front control: NOMATCH with `@` untested).

### 4.7 The measurement set's channel (R-20: R-MS1..R-MS5) `[rev3: C2, E-1]`

- **In (R-MS1):** `mf_art_begin(..., const mf_measures *ms)`: the `kit.` rows of the set
  pcrec LOADED (key, `value_e6`, unit, source) plus the set's `id`, `rev`,
  `values_digest`, `class`, `tier`, `composite` (measure_sets §4.1). No `status` (a NULL
  row is not handed over), no `pcrec.` rows, no provenance columns. NULL = no set. Per
  compile, not per site (rev 1's Q-R17P-5, answered by R-MS1).
- **Out (R-MS2):** `consulted` from `mf_art_end`: true iff any kit row of this compile
  resolved a key, found or absent. pcrec ORs it with its own readers to decide whether
  `<PREFIX>_MEASURES` is `""` (measure_sets §3.5). Through B3b no ROUTED row reads a key,
  so `consulted` is false on every default compile (the shadow's reads are trace-only
  and do not set it). `[rev3 C2]` `consulted` stays one boolean per compile; what it
  cannot say (which sites were decided by a DEFAULT row) is said per site by the facts
  section's `basis` and its per-compile default count (§1.7), so an artifact stamped with
  a set never reads as "every selection came from it".
- `[rev3]` **The analysis object (the E-1 agreement with main):** B1 declares
  `mf_art_begin(..., const mf_analysis *an)`, NULL-tolerant and read by no kit row before
  B3a (the ported PRES picks are its first readers). Main's E-1 (window_contract S1, main's
  own abi event, main also owning window_contract rev 3 with C-7/C-8) fills it after B2
  merges, with no kit edit. Rev 2 placed the object on the site (`mf_site.analysis`,
  window_contract §6 S1's text); the agreement puts it on the art, once per compile, the
  same channel as `mf_measures` (window_contract rev 3 carries the change, main's).
- **Form hashes (R-MS3):** `mf_form_hash(form_id)` over the canonical instance with
  scaffolding normalized out, for every form a card names: `walk`, `V1`, `libc`, the
  one-byte libc-free forms, `none`, the dispatch twin, `W64`. `[rev2]` The `libc` form's
  hash covers the CALL text only; the library's own code is outside it, which is why the
  libc rows need a third dependency owner (§5.3, Q-R17P-14).
- **Reader declarations (R-MS4):** per `fd_rows[]` row, the keys it reads and per
  threshold key its SAFE direction (`max`/`min`/`none`: the side of its `unpaid` or
  conservative pick), as data in [LIST-TABLES]' census shape; per artifact, the
  `--emit-facts` section `memfn` (§1.7). Keys at B1 (M0's listing); directions at M2.
- **Method cards (R-MS5):** one card row per quantity of §5.2, in a section TSV in the
  kit tree, versioned `kit-grid@N` (grid1 = `@1`, grid2 = `@2`).

### 4.8 winreq's C-items, each mapped

| C | change | implemented by | step |
|---|---|---|---|
| C-1 | the PRESENCE class: `omin`, no `omax`, its own binding; "below the origin" split into necessary-before-origin and CONTEXT | §4.1 (`mf_span_class`; `omin` from the match start, `[rev3 A20]` an amendment asked of main, Q-R17P-17) | B3a |
| C-2 | presence carved out of "bounded only"; the unbounded sentinels and `window_stated 0` stay refused on window spans | §4.1 rules | B3a |
| C-3 | range binding; decided-first; per-candidate permission; the range form of an unconstrained reply | §4.4 | B3b |
| C-4 | delete "presence sites keep the VERDICT reply" | §4.1 | B3b |
| C-5 | the run pre-check row and the K82/L1 row rewritten (origin = landmark) | §4.4 | B3b |
| C-6 | T-PRES superseded: `dominated` is the kit's (P2), presence is not a separate site, `none` stays pcrec's sub-problem choice (Q-WR-4) | §1.4, §4.2 | B3b |
| C-7 | R-18's text and window_contract §11 changed in step | main's ledger edit | with window_contract rev 3 |
| C-8 | unlock (c) "presence as a chain link" becomes the contract | main's doc edit | with rev 3 |
| C-9 | the APPLICABILITY rule for REQUIRED spans | the rows' gate contracts over `need` and `site_kind` (`[rev3 D1]`) + P0's precedence (§1.3, §1.4) | B3b |
| C-10 | G-5's direction per consumer | §4.6's posture column (Q-WR-3) | B3b, B5 |
| C-11 | `consumer` replaced by the kind, not dropped | §4.2 | B2 (kind), S3 (retire) |
| C-12 | NONE's safety per consumer | §4.6 | B2 (stated), B5 (F0 reachable) |
| C-13 | the VM-route EXCLUSION | §4.6 rows 5-7 | B2/B3b |
| C-14 | the EFFORT fact is `need` | §4.2 | B2 |
| C-15 | an evidence-reading row reads only MEASURED provenance | §1.3 (F0, R5, R8), §1.4 (P1) | B1 |
| C-16 | member order and per-member offsets as span fields | §4.1 (`member_order`, `omin`) | B3a |

### 4.9 `MF_SITE_ABI`, by step `[rev3: A4, A15]`

`[rev3 A15]` Numbered RELATIVELY: each step below is the next number from whatever main
holds when it lands (main holds 10 today; the kit branch's 11 and 12 are not on main), and
main's E-1 takes its own bump between B2 and B3a.
- B0: R17-a's window fields and storage;
- B1: `body`, the START hook, `[rev3 A4]` `mf_ask` and `mf_class` (with `mf_defined`'s
  class member), and the art calls' `mf_measures`, `mf_analysis` (declared) and
  `consulted`, in ONE bump;
- B2: `site_kind` (DFA_ATTEMPT included), `need` re-numbered, the moved-candidate hook;
- (main) E-1: main's bump (its fill of `mf_analysis`; window_contract S1);
- B3a: the presence class, `omin`, `member_order`, `head_max`, the class's `pres` links
  (read at B3b), and the merged site's ENTRY use if main takes Q-R17P-18's spelling;
- B4: R17-b's `needs_const_subject` and the W8 sub-block.

Each kit bump is a kit contract event moving no pcrec byte except B4's.

---

## 5. Measurements (D166)

### 5.1 The unit and the key (rev 1 §3.1, re-spelled per measure_sets §1.3)

- **Unit u** = β_walk(PF, one RANGE term) = **0.1892 ns/B** on grid1 (MEASURED, gridread
  §2.1 F3), the set's `unit_key`. Costs are stored in u·B ("walk-bytes"), per-byte rates
  as ratios to u, crossovers in bytes; absolute ns is provenance only (`abs_ns_e6`).
- **Key** `[rev2]`: measure_sets §1.3's one canonical string, `kit.<quantity>.<tokens>`,
  the tokens in the order the quantity's card declares in `dims` (form; compared form;
  site kind; shape; length class, as each card needs). Rev 1's keys
  (`kit.beta.V1.ANY.r2e0c0`) are conforming (measure_sets §1.3.3). The SUBJECT condition
  is a card field (measure_sets §1.2's `subject`), so a streamed and a repeated
  measurement of one quantity are two cards, never one key with a tag.

### 5.2 Every quantity the table reads `[rev2: M19-M23 added; the card column]` `[rev3: M24; M6 per regime; C1, C5, C9, C13]`

"in grid1?" = the value exists in the one run grid1 (Zen 4 7700X, CPU 14, 2026-10-13,
read by `gridread.py` @ 540649453). Citations "§x" are to gridread_report.md.

| id | quantity | key dims (form / vs / kind / shape) | relative value (grid1) | absolute (provenance) | source | reader | in grid1? |
|---|---|---|---|---|---|---|---|
| M1 | β, the unit | walk / – / PF / (1,0,0) | 1.000 | 0.1892 ns/B | §2.1 F3 | all | yes |
| M2 | β walk by terms | walk / – / ANY / 2t, 3t, 4t | 0.992, 1.002, 0.999 | 0.1877, 0.1896, 0.1891 | §2.1 | R0 | yes |
| M3 | β V1 by shape | V1 / – / ANY / (1,0,0), (2,0,0), (2,0,1), (3,1,0), (0,1,1) | 0.572, 0.978, 1.132, 1.410, 0.731 | 0.1082, 0.1851, 0.2141, 0.2667, 0.1384 | §2.1; an. 2.3 | R0, T1 | yes |
| M4 | β S1 by shape | S1 / same five | 0.108, 0.177, 0.220, 0.285, 0.112 | 0.0205 … 0.0212 | §2.1; an. 2.3 | T1 (W16) | yes |
| M5 | β A1 by shape | A1 / same five | 0.056, 0.079, 0.101, 0.143, 0.057 | 0.0106 … 0.0107 | §2.1; an. 2.3 | T1 (W32) | yes |
| M6 | null floor ε, `[rev3 C4, C13]` PER REGIME: `kit.eps.<subject>.<lenclass>` | – / – / – / regime | `[rev3 C13]` rev 2's 0.031 was the POOLED F1+F3 "FRG" figure (3.090%), not F1's own p90 (3.365%); regime-split: F1 find-all p90 3.365% (median 0.195%), F3 member-free single calls 0.173%, EXT 0.382%; per-launch spread p90 6.96% | the A/A pairs of each regime's own groups | gridread analysis.txt lines 5-15 | R0, R7, F2 (`kit.eps` per regime); T1-T3 read each cell's own `floor(cell)` (§2.5) | yes (per regime) |
| M7 | single-call fixed part F, n ≥ 64 | walk, V1, S1, A1 / – / PF | 25.1, 22.1, 24.8, 26.3 u·B | 4.74, 4.18, 4.70, 4.98 ns | §2.2 | T1, T2 | yes |
| M8 | F at n = 48 (sub-block tail) | walk, V1, S1, A1 / – / PF | 25.6, 22.0, 129.7, 77.9 u·B | 4.84, 4.17, 24.54, 14.73 ns | §2.2 | T1, T2 | yes |
| M9 | single-call crossover | V1 / walk / ANY / member-free | 36 B (bracket 32-48), `[rev3 C5]` INTERPOLATED(32, 48) on grid1; grid2 item 2a measures N = 33..46 (§2.6) | | §4.3 interp., §4.4 | R1 | yes, as an interpolation |
| M10 | single-call crossover | S1, A1 / walk / ANY | 18 B, 20 B | interpolated | §4.3 | listed only | yes |
| M11 | block step | W64 / V1 / ANY | 64 B | DERIVED (W = 64), step MEASURED at n 63→64 | §4.4 | R2 | yes |
| M12 | single-call delta at N | V1 − walk / PF / N = 8, 32, 48, 63 | +12.2, +3.2, −23.8, −29.6 u·B | +2.3, +0.6, −4.5, −5.6 ns | §4.3, §4.4 | T1 | yes |
| M13 | c_cold per activation | V1, S1, A1 / walk / PF | +13.1, +15.3, +15.4 u·B | +2.47, +2.90, +2.91 ns | §2.4 | T1 checks | yes |
| M14 | per warm use, absolute | walk, V1, S1, A1 / – / PF | 8.8, 12.6, 11.7, 11.8 u·B | 1.67, 2.38, 2.22, 2.23 ns | §2.3 | T3 (w_min) | yes |
| M15 | g\* | V1, S1, A1 / walk / PF, DFA-hat, bounded | V1 10.8-16.7 / 3.0-3.3 / 21.5 B; S1 4.3-4.7 / 2.1-2.4 / 3.6-5.8; A1 4.2-4.4 / 2.1-2.3 / 2.4-3.0 | log2-interpolated | §4.1 | R5 (`[rev3 D8]` rev 2's R5 and R6), R4 (and R8's g8) | yes |
| M16 | dispatch charge per activation | dispatch / none / ANY | — | — | — | T1, T2 | **ABSENT** |
| M17 | dispatch charge per use | dispatch / none / ANY | — | — | — | T3 | **ABSENT** |
| M18 | scaffold charge per use | walk-in-helper / walk-inline / PF, VM_ATTEMPT | — | asm differs by −3..+14 insns (`r17b_prime/out/walk_helper_asm.out`) | — | T3 (R0 sites) | **ABSENT** |
| M19 `[rev2]` | libc one-byte F and β | LIBC / – / DFA_SCAN (fwd, bounded), DFA_HAT, HYB_PF, DFA_ATTEMPT (back; `[rev3 A2]` rev 2's ATTEMPT_PRED), `[rev3 A7]` VM_ATTEMPT / (0,1,0) | — | glibc F 3.24 ns (`linux_results.md`, method-mixed, not a set) | — | F1, D1's replacement | **ABSENT** |
| M20 `[rev2]` | libc-free one-byte F and β | V1 one-term, WALK at \|S\| = 1, the generic byte loop / – / the same kinds `[rev3 A7]` plus VM_ATTEMPT / (0,1,0) | — | — | — | F1, `[rev3]` F2 | **ABSENT** (grid1's sets are all ≥ 2 members or one RANGE term) |
| M21 `[rev2]` | one-byte dominance points | each libc-free form / LIBC / kind | — | DERIVED from M19, M20 | — | F1 | **ABSENT** |
| M22 `[rev2]` | NONE's gap threshold g_none | NONE / the next pick / DFA_SCAN, DFA_HAT, HYB_PF (DFA_ATTEMPT: measured only for Q-WR-2's decision) / shape | — | — | — | F0 | **ABSENT** |
| M23 `[rev2]` | the pre-scan gate: KEEP − DROP per presence shape, route and position (early, late, absent) | gate / – / DFA_SCAN, HYB_PF / one byte, set 2-4, run 2-8 | — | — | — | P1 | **ABSENT** (and P1 waits for Q-WR-9's trigger) |
| M24 `[rev3 A6]` | the mode branch on a SHARED PARAM find body, per call | dispatch / none / kind / layer | — | — | — | T2 (beside C_disp_call, §2.4-§2.5) | **ABSENT** (no PARAM body exists before R17-b″; measured at [REGIME-TWIN] or the iterator's parity slot) |

- **15 of 24 families exist in grid1; 9 are ABSENT** `[rev3]`: rev 1's three dispatch
  charges (M16-M18), the one-byte libc and libc-free costs and their crossover (M19-M21),
  NONE's effort (M22), the pre-scan gate (M23) and the shared-body mode branch (M24).
- `[rev3 C1]` **The converter's derived keys** (measure_sets §1.6's closed registry, the
  converter `set_to_measures.py`, regime_eval E14) are, exhaustively: `kit.saving.<f>.<g>.<shape>`
  (R0, R7, F2; from M2-M5 and M20), `kit.xover.<f>.<g>.<kind>` (R1; from M7, M8, M12 and,
  once grid2 measures them, M19/M20, which is exactly why R1's applicability is row data
  and not key absence), `kit.block.W64` (R2; M11), `kit.dom.<f>.LIBC.<kind>` (F1; M19-M21),
  `kit.lstar`/`kit.g8` (R8). B4's check runs a synthetic set holding every one of them.
  `[rev4.1]` One more, **`kit.terms.V1max`** (R7; Q-R17P-26): the largest cover term count
  n such that every timed shape of at most n terms has a V1 saving above the null floor and
  the next count up loses. Its value is **2**, derived from grid2read §3.2's nine shapes
  by the stated rule: 1-2 terms save (+42.0% (1,0,0), +54.8% (0,0,1), +1.2% (2,0,0),
  +26.8% (0,1,1), +39.0% (0,2,0), +21.1% (1,1,0)); 3 and 4 terms lose (-13.3% (2,0,1),
  -41.3% (3,1,0), -46.4% (3,0,1)). Provenance grid2read §3.2 (an. 4, 4b, 4c). Confidence:
  the (2,0,1) and (3,1,0) VALUES are PROVISIONAL (load-suspect cells, re-time OWED, §3.1a
  item 1) but their SIGNS are not in doubt, and the key reads only signs. The note has no
  key file of its own and grid2read's `keys.tsv` is pinned by its SHA256SUMS, so the key
  is stated here, in §5.2's list of derived keys, with the rule above as its derivation
  (a one-line reduction over the nine saving keys' signs; the converter adds it to the
  derived set at B4). R7's `basis` is DERIVED by the self-check's rule (§1.2). A re-time
  that flipped a sign would move the key, and that is a default-set change with its census
  (§10 item 3).
- **INTERPRETATION, recorded so the arm is built (not a value any row reads):** grid1's
  EXT arms put the DFA's own per-byte step at 0.1885 ns/B (armread), within 0.4% of u.
  So on a DFA consumer NONE costs about what WALK costs per byte, and its saving against
  WALK is only the per-landing exit and re-entry; against LIBC or V1 it loses on sparse
  text. That is why M22 is a GAP threshold (NONE pays below it) and why F0 needs E.

**The card each needs (R-MS5), `kit-grid@2`:**

| quantity | `dims` | `subject` | `lengths` | `deps` |
|---|---|---|---|---|
| `beta` (M1-M5, M19β, M20β) | form;kind;shape | streamed (Q-R17P-9) | the slope 64 KiB → 1 MiB, member-free single calls | `kit:form.<form>`; for LIBC also `libc:<name>@<ver>` (§5.3) |
| `eps` (M6) | `[rev3 C4]` subject;lenclass | per regime: streamed find-all, member-free single calls, EXT | each regime's own groups' A/A pairs | — |
| `f` (M7, M8, M19F, M20F) | form;kind;lenclass | fresh buffers, member-free | n ∈ {8, 32, 48, 63, 64, 1 Ki} | as `beta` |
| `xover` (M9, M10), `block` (M11), `delta` (M12), `dom` (M21) | form;vs;kind | derived (registry formula, measure_sets §1.6) | — | the inputs' `deps` |
| `ccold` (M13), `wuse` (M14) | form;kind | streamed find-all | L ∈ {32, 1 Ki, 64 Ki}; g grid | as `beta` |
| `gstar` (M15), `gnone` (M22) | form;kind;shape | streamed find-all | g ∈ {2, 4, 8, 16, 32, 64, 256, 4096, absent} | as `beta`, plus `kit:form.none` for M22 |
| `cdisp_call`, `cdisp_use`, `cscaffold` (M16-M18) | `[rev3 C9]` kind;layer;nforms (the OFF two-form chain and the W16/W32 three-form selector cost differently; R2 is W16/W32-only) | fresh buffers (call) / streamed (use) | M12's N points plus item 2a's N = 33..46; F1 dense groups | `kit:form.dispatch-twin` (stale when the BUILT dispatch differs: §2.5) |
| `cmode_call` (M24) `[rev3]` | kind;layer | fresh buffers | the short-call cell | `kit:form.dispatch-twin` |
| `gate` (M23) | shape;kind;position | streamed find-all | 64 Ki, 1 Mi | `kit:form.libc`, `libc:<name>@<ver>`, `pcrec:<probe>` (the consumer is pcrec's emitted DFA) |

### 5.2a What grid2 measured, family by family `[rev4]`

grid2read's values are kit-tier, Zen 4 and streamed (§3 of that report). Each carries
its regime, layer, floor and confidence in `keys.tsv`. u = β_walk(dig) = 0.1891 ns/B
(grid1 0.1892). This table reads them against §5.2's families and against what each
row of §1.3a needs.

| id | grid2 value (key) | vs rev 3 | read by | grid2read |
|---|---|---|---|---|
| M1-M5 | β by shape at OFF/W16/W32. V1 saves +0.420 (1,0,0), +0.012 (2,0,0), −0.133 (2,0,1) p, −0.413 (3,1,0) p, −0.464 (3,0,1), +0.390 (0,2,0), +0.548 (0,0,1), +0.211 (1,1,0), +0.268 (0,1,1) derived. S1/A1 save 69-89% / 84-94% (`kit.saving.<f>.WALK.<shape>`) | CONFIRMED to 0.1-3.3% on 11 comparable cells; three new shapes measured (item 3a) | R7, R7w `[rev4.1]` (as the EVIDENCE for the term-count rule; no row reads these keys) | §3.2 |
| M6 | `kit.eps.streamed.slope` 0.113% (the slope's own noise 0.247% p90); `kit.eps.findall.l64k` 1.316%; `kit.eps.streamed.short` 0.675% | regime split CONFIRMED; the slope token is smaller than grid1's 0.173% | R7, F2 | §3.1 |
| M7-M8 | F: walk 5.86, V1 4.38, S1 4.62, A1 5.35 ns (n ≥ 64); F at n = 48: S1 21.71, A1 12.87 ns | CONFIRMED (the walk +1.1 ns on streamed buffers) | (no row at B4) | §3.3 |
| M9 | no crossover: V1 − walk < 0 at every N ≥ 8; `kit.xover.V1.WALK.DFA_SCAN` = 8 B (UPPER bound) | **CONTRADICTED** | none (R1 deleted) | §3.3, §4 A2 |
| M10-M11 | S1/A1 vs walk cross at the block, N\* = 64; `kit.block.W64` = 64 B | M11 CONFIRMED | R2, R8 (B6) | §3.3 |
| M12 | V1 − walk −0.18 / −2.87 / −4.98 / −6.60 ns at N = 8 / 32 / 48 / 63 | sign reversed at N = 8 and 32 | T1 (none at B4) | §3.3 |
| M13-M14 | c_cold V1 +2.45, S1 +3.64, A1 +3.41 ns; warm use walk 1.60, V1 2.24 ns; NEW: per u-landing walk 4.26, V1 2.54, S1/A1 0.51 ns | V1 CONFIRMED; wide c_cold +17..+25% | (none at B4) | §3.4 |
| M15 | g\* is a PREDICTABILITY threshold: irregular landings → every form wins from g = 4; regular → V1 loses (+14.9% g = 2, +34.9% g = 8). `kit.gstar.*` keys are shape-confounded (LOW) | **CONTRADICTED** as a gap threshold | none (R5's condition changed; keys kept as evidence) | §3.5, §4 A3 |
| M16-M18 | charge per call: OFF.2 +2.44 ns (WALK path), +0.74 (V1 path); W32.3 +0.32; per use ≤ +0.59 / +0.35 ns; scaffold ≤ 5.8 ns on 64 KiB calls, short-call unmeasured | measured (were ABSENT); T2/T3 fail | the pay rule (§2.5) | §3.6, §5 |
| M19-M21 | LIBC F 4.27-5.82 ns, β 0.0073-0.0075 ns/B (the host's SIMD memchr); `kit.dom.<f>.LIBC.<kind>` = 0 everywhere; `kit.xover.LIBC.WALK` 4.1-6.1 B (LOW) | measured (were ABSENT) | D1/D1c stand; F1 not built | §3.7 |
| M22 | `kit.gnone` = −1 (never) on DFA_SCAN fwd, DFA_HAT, HYB_PF; 2 B on DFA_SCAN.bounded | measured (was ABSENT) | F0 not built | §3.7 |
| M23 | `kit.gate.byte1.DFA_SCAN.early/late/absent` = +8.1 / 0 / −247,000 u·B | measured (was ABSENT); Q-WR-9's trigger fires on the letter | P1 (Q-R17P-28, `[rev4.1]` recorded, not built) | §3.8 |
| M24 | — | still ABSENT (no PARAM body exists) | — | — |
| F2's cells | `kit.saving.V1.WALK.VM_ATTEMPT.r0e1c0` = +0.515; find-all at g = 2 +38.3% R, g ≥ 8 −33..−54% | measured | F2 (Q-R17P-27, `[rev4.1]` answered YES: no density condition) | §3.7 |

`p` = PROVISIONAL (a load-suspect source; the re-time is OWED, §3.1a item 1). Two
caveats from grid2read §6 carry into every row that reads these keys:
- **LIBC is not "SIMD-off" code.** LIBC's β is the host libc's ifunc-selected SIMD
  `memchr`, so the `libc-mismatch` flag (§5.3, Q-R17P-14 as D167 ruled it) matters most for these
  rows.
- **R0's class key is a MAX.** That is why R0 retires (§1.3a).

### 5.3 The libc rows' dependency owner `[rev2]`

measure_sets §2.4 has two dependency owners, `kit:` and `pcrec:`. The libc rows' measured
code includes the C library's `memchr`, which neither owns. D161 add. 14 names the
provenance `libc:<name>@<version>`; this note adds what it means for staleness:
- **The artifact runs against the CALLER's libc**, at run time, which pcrec cannot see
  at compile time. A `libc:` hash compared with the BUILD host's library (glibc's
  `gnu_get_libc_version()`, or `confstr(_CS_GNU_LIBC_VERSION)`) would stale a row on a
  box that is not where the artifact runs.
- **PROPOSED:** `libc:` deps are recorded as provenance in `deps`, and a mismatch with
  the build host's library is a SET-level listing flag `libc-mismatch`, exactly as
  measure_sets §2.4 treats `compiler-mismatch`, never row staleness. The kit-side half
  (the form hash of the CALL text) stays row staleness as for any form. Q-R17P-14 asks
  main, as measure_sets' owner, to take the third owner on these terms.

### 5.4 zen4-grid2: ONE slot spec `[rev2]` `[rev3: A7, C3, C5, C7, C8, C10]`

`[rev4]` **The slot RAN** (grid2read §1-§2), and this section is now its record:
- **Run.** Method `kit-grid@2`, CPU 14, 3 launches (+2 by the rerun rules), 61 min
  required, 66.5 min with the optional passes, COMPLETE.
- **Gate.** Green: 141 (cell, arm) pairs and 1,070 items, with 0 answer mismatches.
- **Rerun rules.** The cross-launch trigger fired in 28 of the 32 F1 reruns (and 23 of
  the 26 OB reruns), so the trigger revision 3 added was needed.
- **Contamination.** One visit (F3 `f3-dig` n64k, 45 rows) was re-timed clean by the
  requeue. Three load excursions the harness did not log were treated per arm, and
  two of them leave the (2,0,1) and (3,1,0) rows PROVISIONAL (re-time OWED, §3.1a).
- **Counters.** Available (`perf_event_paranoid` = 2), so F2 and F2S ran and no
  suggestion text was needed.

The estimate below overshot because 3 launches sufficed where it assumed 3.4-5.

GO by D167 (Q-R17P-9 (B): one streamed condition gives both the set's constants and
regime_eval's in-sample reference R_in; `[rev3 C10]` R_in is therefore in-sample by
design, and grid1's prototype figures stop being directly comparable). This section is
the slot SPEC; a separate lane extends the grid1 harness from it.

One run under D166's rule: one box (the Linux dev box, Zen 4 7700X, CPU 14 via
`taskset`, governor `performance`), one method version (`kit-grid@2`), gcc 15.2 `-O2`,
the grid1 harness (`docs/dev/lanes/grid1/`, arm contract `grid1/README.md`) with
rotated interleaving, 7 rounds per launch, the per-launch median, LAUNCHES 3 (+2 by the
pre-registered rerun rule), the quiet gate at every group boundary. Costs use
regime_eval §2.1's own formula: group-arms × launches × 0.95 s per launch.

`[rev3 C7]` **Launches.** Rev 2 costed 3.4 launches (3 plus the expected reruns); grid1
and spike1 both ran at 5 (grid1 F1: 4,407 s for 1,124 rows, 0.78 s per row-launch). The
estimate is therefore a RANGE, 3.4 to 5 launches, and the rerun rule gains a
CROSS-LAUNCH trigger: a group whose any arm's per-launch medians spread (max − min) by
more than the group's own A/A floor gets +2 launches (pre-registered beside the
within-launch walk/walk#b rule; gridread found the walk bimodal ACROSS launches on
repeated u-shape groups, which the within-launch rule cannot see).

| # | item | for | group-arms | wall at 3.4 launches | at 5 launches |
|---|---|---|---|---|---|
| 1 | the 149 fit groups (F1 141 + F3 8) re-timed STREAMED, every pickable arm at both layers plus `walk#b` and `walk#c` | R_in (E4b) and the set's M1-M15 | 149 × ~7 = 1,043 | 56.1 min | 82.6 min |
| 2 | dispatch TWINS: the WALK+V1 scaffold with `f` forced to each form against the single-form artifact (`mkvar.py` gains the variant): F3's member-free points, 20 dense F1 groups, 6 R0-shaped scaffold groups (hex-run, word-eq, `\w`) | M16, M17, M18 | 8×3 + 20×3 + 6×2 = 96 | 5.2 min | 7.6 min |
| 2a | `[rev3 C5]` the crossover staircase: member-free single calls at N ∈ {33, 34, 36, 38, 40, 42, 44, 46}, arms V1, walk, `walk#b` | M9 read off measured points (§2.6), M12 | 8 × 3 = 24 | 1.3 min | 1.9 min |
| 3 | one-byte arms (LIBC, WALK at \|S\| = 1, V1 one-term, the generic loop, `walk#b`) at five kinds (DFA_SCAN fwd, DFA_SCAN bounded, DFA_HAT, HYB_PF, DFA_ATTEMPT back), over 6 gaps {2, 8, 32, 256, 4096, absent} find-all streamed + 4 member-free lengths {8, 32, 64, 1 Mi}. DFA_ATTEMPT takes LIBC-back and a hand back-walk only | M19, M20 (M21 derived) | 50 × 5 = 250 | 13.5 min | 19.8 min |
| 3 (VM) | `[rev3 A7]` the same at VM_ATTEMPT (the VM hat's seek at \|S\| = 1): WALK, V1 one-term, LIBC (evidence only: Q-R5's per-attempt memchr), `walk#b`, over the same 6 gaps + 4 lengths | F2 (D167 add. 1 A7; Q-R17P-20) | 10 × 4 = 40 | 2.2 min | 3.2 min |
| 3 (NONE) | `[rev3 C8]` NONE as one EXTRA ARM inside item 3's gap groups (the use's FIND statement deleted by `mkvar.py`: the consumer walks), at DFA_SCAN fwd, DFA_SCAN bounded, DFA_HAT, HYB_PF and DFA_ATTEMPT (the last evidence-only: Q-WR-2 writes no key for it until a measurement is ruled in) | M22 | 5 × 6 = 30 | 1.6 min | 2.4 min |
| 3a | `[rev3 C3]` three unmeasured cover shapes (0,2,0), (0,0,1), (1,1,0) (83% of R17-b's 320 unmeasured byte V1 movers): V1 vs walk β, member-free, 64 KiB and 1 MiB, arms V1, walk, `walk#b` | M3 for those shapes (R7's keys) | 6 × 3 = 18 | 1.0 min | 1.4 min |
| 5 | build and the correctness gate first (`check.sh` legs R, L, C: every arm's answers and match lists equal the base's; the base equals libpcre2 10.46 through `tests/oracle/`'s local adapter); a pickable arm's answer failure FAILS the run | all | every arm | ~10 min (INTERPRETATION: grid1's gate scaled; not launch-scaled) | ~10 min |
| | **required** | | **1,501** | **≈ 91 min** | **≈ 129 min** |
| 6 | OPTIONAL: F2's perf pass on the K arms {walk, V1, A1} of every item-1 group (regime_eval §2.1 item 2) | CB corroboration (ungated) | | ~5 min | ~5 min |
| 7 | OPTIONAL: F2's streamed perf pass (hex-run, bounded, dfa-hat × 4 arms × prose/docs/code) | the panel's ask; no bar reads it | 36 rows × 0.6 s | < 1 min | < 1 min |
| 8 | OPTIONAL: a pre-scan TRIGGER PROBE: KEEP vs DROP (`-fno-req-byte`/`-fno-req-run` as the DROP arm) on DFA-route TUG cells with OPTIONAL presence | whether Q-WR-9's trigger fires (no row is built from it) | 36 | ~2 min | ~3 min |
| | **with the optional items** | | | **≈ 99 min** | **≈ 138 min**, plus quiet-gate waits |

- **Against rev 2.** Rev 2's required items were 1,434 group-arms (C7's count): 77.2 min
  at 3.4 launches and 113.5 at 5 (C7's "88-113" quotes the 3.4-launch figure WITH the
  10-minute gate and the 5-launch figure without it; with the gate both ends are 87 and
  124). Revision 3 adds 67 group-arms net (item 2a 24, item 3a 18, the VM_ATTEMPT cells
  40, the NONE arms 30, less rev 2's separate NONE item 4's 45): +3.6 min at 3.4 launches,
  +5.3 at 5.
- **NONE inside item 3's groups** `[rev3 C8]`: a separate NONE group compared NONE with
  the picks across groups (different times), against D166's same-run interleaving; as an
  arm of the same group it is interleaved with the arms it is judged against, and the
  group's `walk#b` gives its A/A. `g_none` is read on the six gaps {2, 8, 32, 256, 4096,
  absent}, a factor-4 to factor-16 grid, so its key is labelled `INTERPOLATED` in its
  provenance and F0's `basis` stays MEASURED only for the measured gap points.
- **Perf is never required** (D166 add. 1). Items 6-7 skip loudly when counters are
  unavailable (`F2_SKIPPED`, the set header's `counters skipped:perf_event_paranoid=N`),
  and nothing downstream changes. **The paranoid SUGGESTION** (D166 add. 1.1): when
  counters are unavailable, `slot.sh`, `time.sh` and `f2perf.sh` print, to the log and
  the pass's status file, the current `kernel.perf_event_paranoid` (`?` if unreadable),
  that 2 or lower enables the optional pass, what it adds (branch misses, the
  predictability diagnosis), and the commands (one-off `sudo sysctl
  kernel.perf_event_paranoid=2`; persistent `/etc/sysctl.d/99-perf.conf` with
  `kernel.perf_event_paranoid = 2`). The scripts never run `sysctl` or `sudo` and never
  write under `/etc`. `[rev2]` regime_eval §1.2 puts this change in E4; grid2 runs
  first, so it moves into grid2's PREP lane, with its check (the text appears when the
  probe is forced to fail; the skip reaches the provenance; no `sysctl`/`sudo` in the
  scripts). This box reads 2, so items 6-7 run here.
- **Prep (a lane, before the slot):** `mkvar.py`'s variants (dispatch scaffold with forced
  `f`, NONE, V1 one-term `[rev3]` incl. at the VM hat), the one-byte (five kinds plus
  VM_ATTEMPT) and NONE-arm cell manifests, `[rev3]` item 2a's N points and item 3a's
  shapes, the streamed subject generator for item 1 (the same generator E4 uses), the
  cross-launch rerun trigger, the suggestion text and its check. Nothing in prep moves
  pcrec bytes.
- **Outputs** stay in the kit's slot directory (gitignored); E4b reads the logs; the set
  file is written at M0 by the converter (`set_to_measures.py`, regime_eval E14), with
  each row's `deps` computed by R-MS3 then. A form changed between the slot and M0 makes
  its rows STALE, carried and flagged (D166 add. 2).
- **Option (A)** (rev 2's comparison) is moot: D167 ruled (B).

### 5.5 How the set reaches the build `[rev3: C12]`

- **B0-B3b read no set** (§3.2). The shadow and `regime_pick` read the kit's interim TSV
  (Q-REVAL-10) as a test input.
- **B4 reads the LATEST committed set** (D166 add. 2: the latest until M2). If grid2 and
  M0 both precede B4, that is `zen4-grid2`, and B4's census contains its selections: ONE
  abi event. grid1 is never embedded (a provisional design-time set).
- `[rev4]` Moot: grid2 has run, so B4 reads zen4-grid2 (the case above).
  ~~**If B4 precedes grid2** (not recommended), B4 reads grid1 through M0:~~ (kept as the record) R0 fires, R7
  fires only on grid1's measured shapes (`[rev3 C3]`), R1/R2 are unpaid (M16-M18 absent),
  and grid2's later landing is a default-set change, its own abi event with its
  `MOVERS.tsv` (measure_sets §3.6).
- **Zen 1 (F5)** gets its own set through a bench window. `[rev3 C12]` Selecting it for a
  Zen 1 target needs M1's `--measures=`. Until M2, a bare compile reads the LATEST
  committed set (D166 add. 2), so between a committed Zen 1 set and M1 EVERY bare compile,
  Zen 4 and arm64 included, would read Zen 1's literals; and until then every box reads
  Zen 4's (an arm64/Mac compile at B4 reads Zen 4 literals). Recommendation (Q-R17P-24):
  no second official set is committed before M1 lands. The generic envelope becomes the
  default only at M2 (D166 add. 2, D161 add. 12).

---

## 6. R17-b″'s seam: the iterator rows, A3, H, the presence carry, the cut-off `[rev2]` `[rev3: A6, A10]`

The D165 iterator (`rx_iter`, `<prefix>_next`, findall_iter.md) adds `[rev3 A6]` a
PARAMETERIZED find body: `<p>__find` takes the mode M, `_search` passes ONESHOT and
`next` passes ITER (findall_iter §4.2), stated as `mf_site.body = MF_BODY_PARAM` plus the
mode-expression hook (R-20 at R17-b″). Whether M folds is the part-layout row's decision
(D163 add. 7; `compound_entries.md` §3.4): inlined, M is a constant per call site; shared
(`−2`/`−1`, `+1` below `θ_hot`, and row L1's label-table body at every position), one
runtime branch per call, priced as M24 (§2.4). Nothing in the table is rebuilt; the
iterator makes rows reachable:

- **The H rows.** R3a, R3b and R4 (`needs ∋ KN_H`) are listed now and skipped in a one-shot
  body; in a `next` body H is available (the previous step's span; the block's popcount)
  and the same evaluation emits them, R3a/R3b as dispatch rows read at `next`'s entry, R4
  at the block's refill. R8 reads the step span L from H there instead of N. R3 stays
  PROVISIONAL (regime_tables rev 0.5) until F4/F7 measure the real iterator; their denies
  `fd-r3a`/`fd-r3b`/`fd-r4` are created then.
- **A3** is `__next_candidate__w32` over storage that persists in `rx_iter`'s buffer; the
  selector and per-form bodies are unchanged.
- **The presence carry** `[rev3 A10]`. A verdict "a REQUIRED presence span occurs at
  p ≥ start + omin" stays true for a later call while that call's `start ≤ p − omin`.
  Rev 2 kept ONE `size_t valid_until` (the minimum over REQUIRED spans of `p − omin`).
  That is correct but not LINEAR: on each expiry every REQUIRED span is re-verified over
  `[start + omin, n)`, so a FAR span is rescanned up to its occurrence at every expiry,
  quadratic in find-all with 2+ REQUIRED spans (67 corpus patterns on P0's no-DFA routes)
  or with a two-stream form, which is exactly K5's shape (walk_survey K5: the TWO-STREAM
  arm restarts both `memchr` streams per call; `pair-hits` carries two pending hits so the
  far stream is not rescanned). So the carry is one position PER REQUIRED SPAN, or per
  stream of a multi-stream form: 8 B × k, DECLARED per form as D165 item 6 allows (a
  form states its state need as it states `size`). Past a span's position the next call
  re-verifies that span only, from its carried position.
- **The per-candidate cut-off (Q-WR-6, a PERMISSION).** With the per-span carry,
  find-all scans each presence span once in total rather than once per call; the stream
  may also end at a candidate `c > p − omin + head_max` (§4.4). Exercised only after
  D165's build; never required.
- **K5's 16 B pair-hit row** `[rev3 A10]` (D167 add. 1, amending Q-R17P-10): it does NOT
  retire on the merge alone. It retires when a kit form is PROVEN single-pass over its
  spans (each span's stream advanced monotonically and never rescanned, checked by a
  per-span scan counter on a K5-shaped witness set), and in that same change.
- **The kit's state rows, and S.** The kit's FIND row stays `base`, `top` (`size_t`) and
  the u64 mask (24 B, D165 add. 1), plus the previous step span (8 B, H); the presence
  carry is 8 B per declared carried position; the form byte is RECOMPUTED at each `next`
  entry from N and H, not stored. S is DERIVED, not picked (D165 item 4): the maximum over
  artifacts of the sum of the declared rows held at once on a path (the kit's FIND row,
  its H row, its carried positions, pcrec's reseed hint, and K5's 16 B where it has not
  retired), re-derived at the iterator's own abi event. Rev 2's "S = 48 B" is WITHDRAWN as
  a fixed number. Zero-init writes the declared rows' bytes, never a memset of S (D165
  item 5 and its add. 1 reading). Internal batching (D165 add. 2) keeps its batch in the
  caller's `_in` memory, outside S.
- **Acceptance** carries F4 (the iterator reproduces A3's hand-edit win), F7 (H's
  observation cost against its regret), D165's named parity gate (dense tiny matches at
  parity or better; binding at positions `0`, `+1`, `+2`, D163 add. 7 Q3), and SW-16's
  plant (S979).
- **Order** (D163 add. 7 Q4): E0 → `findall_iter.md`'s short revision → its D6 panel → I1;
  R17-b″ (B9) follows I1.

---

## 7. Questions

### 7.1 Revision 1's Q-R17P-1..8: CLOSED `[rev2]`

| id | question | closed by | outcome |
|---|---|---|---|
| Q-R17P-1 | `MEMFN_FORMS` vs forms-per-site | main's acceptance of the kit's revised proposal (kit journal 2026-10-14); R-20 R-MS4 | forms-per-site go to `--emit-facts` (the section `memfn`); `MEMFN_FORMS` keeps its ruled SIMD-only meaning (match_api §6.3.10¶3-4, D147 add. 10) |
| Q-R17P-2 | the `<PREFIX>_MEASURES` stamp | measure_sets rev 2.1 §3.5-§3.6 | `""` when nothing consulted, else `id@rev:digest16` (stamp-on-load), mirrored in `rx_info.measures`, ONE abi event at M0 that rides R17-b′'s (B4); rev 1's `"none"` withdrawn |
| Q-R17P-3 | the pay rule | D161 add. 13 (rows are the kit's until lockdown) | STANDS as the kit's design (§2.5); [REGIME-TWIN] measures the dispatch it gates |
| Q-R17P-4 | the acceptance gate | Q-REVAL-1 and Q-REVAL-11 (ruled) | [REGIME-EVAL]'s loose pre-registered per-regime bars replace D162 add. 1's no-loss gate for the routing commit, which waits for PASS or PROVISIONAL PASS; the official verdict stays the bench on targeted hardware (D144 add. 4) |
| Q-R17P-5 | the set's channel | R-20 R-MS1 | per compile, on `mf_art_begin`; the analysis object stays as D162 placed it |
| Q-R17P-6 | [MEASURE-SET] phasing | measure_sets §10.1 | [KNOW-SRC] K0-K3 first; M0 rides R17-b′ with R-MS1/2/3/5; M1 (`--measures=`) at the first second set; `--list-finder` withdrawn |
| Q-R17P-7 | the first set needs a run | regime_eval §2.1 (grid2 is the kit's next slot); D166 add. 2 | zen4-grid2; refined by §3.2: the first delivery needs no set at all |
| Q-R17P-8 | site kind, and R1/R2's transfer | R-19 (gated), then R-21 Q-WR-8 (ungated for categorical kinds; `consumer` replaced at S3) | `site_kind` stated at B2 (§4.2); R1/R2's PF-measured crossover applies to every kind, labelled "measured on PF", until per-kind keys exist (a card edit) |

### 7.1b Revision 2's Q-R17P-9..14: CLOSED `[rev3]`

| id | question | closed by | outcome |
|---|---|---|---|
| Q-R17P-9 | grid2's fit condition | D167 item 2 (Frank) | (B): ONE streamed condition gives the constants and R_in; regime_tables §3's S0 row is re-derived on grid2 (§5.4) |
| Q-R17P-10 | S under the merge | D167, amended by D167 add. 1 A10 | K5's 16 B row retires only when a kit form is proven single-pass; S derived from declared carried positions; "48 B" withdrawn (§6) |
| Q-R17P-11 | the fifth priced pick | D167, refined by D167 add. 1 A11 | the landmark admission stays pcrec's, its input restated as facts (prior mass, h, K); a D157 exception until restated; computed in the B3a shadow as evidence for framing (b) (§1.4, §4.5) |
| Q-R17P-12 | the PF comment's `-fcomments` move | D167 | rides B4's commit; B2 zero-mover on every arm, proven by sweeparm's `-fcomments` arm (§3.1) |
| Q-R17P-13 | routing before the judge | D167 (Frank: "#3 agree") | the judge gates B4 only; B2/B3b may land while the judge runs (§3.3) |
| Q-R17P-14 | the `libc:` dependency owner | D167 | provenance in `deps` plus a SET-level `libc-mismatch` flag, never row staleness; main takes the third owner (§5.3) |

### 7.2 New questions, each with a recommendation `[rev3]`

**Q-R17P-15 (main). The define-time query's contract** (§4.5, A4; B2 depends on it).
`int mf_ask(const mf_art *art, const mf_site *site, const mf_hooks *def, mf_class *out)`:
pure, answering for what will be rendered, agreeing with `mf_define` by check, landing
in B1's MF_SITE_ABI bump with a trace-build reader shadow. Recommendation: accept as
specified; the alternative (growing `mf_defined` and defining sites earlier) would move
every define point, which R17-a measured to renumber handles (9 movers), and would still
need a no-emit path for a rejected alternative.

**Q-R17P-16 (main, R-21's and R-19's owner). The third caller and the builder list** (A2,
A21). Amend R-21 PR-3: ATTEMPT_PRED becomes DFA_ATTEMPT (the DFA attempt loop: MLINE's
seek and `attempt_entry`'s presence). Amend R-19's builder list to name
`req_site_define`, MLINE and `attempt_entry` beside the forward scan, `_search_run`, the
relocate path and `fwd->from`. Recommendation: both, filed together (one ledger edit).

**Q-R17P-17 (main, window_contract's owner). `omin` from the MATCH START** (A20, §4.1).
Amend PR-6 ("offsets relative to the chosen origin") and C-1 ("`omin ≥ −h_max`") so a
PRESENCE span's `omin` is measured from the match start, which keeps B3's window exactly
today's `[posvar, n)` and reads nothing below `start`. Recommendation: amend; the origin-
relative spelling stays for window spans (span 0's `move_back`/`overshoot`).

**Q-R17P-18 (main, DELEG_SITES' and C17's owner). The merge's site-table edits** (A8,
§3.4). At B3a the PRE row merges into the FIND row of its route as that site's ENTRY use;
presence-only sites keep a FIND row with no span 0; the use points move in
`site_manifest.tsv`; the ENTRY use is a new use kind (proposed `MF_USE_ENTRY`), an
MF_VOCAB event. Recommendation: accept the shape; the spelling is main's.

**Q-R17P-19 (main). `PCREC_NO_REQ_SET_LEAD` at B3b** (B13). Bit 45 retires to the kit's
`no-pres-set-lead`; the public constant is in `lib/pcrec.h`. Recommendation: keep the name
defined as a RESERVED, ignored bit with a comment naming the kit deny until [IFACE-PUSH]
(removing a public constant is a caller-visible break that push batches).

**Q-R17P-20 (main). Which kind feeds F2** (A7). D167 add. 1 says the VM hat's |S| = 1
move is fed by "grid2 item 3's one-byte arms (WALK vs V1 one-term at DFA_HAT)". The VM
hat's seek is a VM_ATTEMPT consumer, and C3 found item 3 measured it at no kind.
Recommendation: VM_ATTEMPT cells (added to item 3, §5.4); the DFA_HAT cells stay as the
DFA hat's own evidence. Main confirms or corrects the addendum's wording.

**Q-R17P-21 (main, the dial's owner). The kit's size-adding rows and the dial** (D5).
`pf-terms-mask`, `fd-ndisp`, `pf-terms-w*` are `MF_SZ_ADDS` FORM denies. Recommendation:
they stay OUTSIDE the part-layout table (they are forms, read by the size ladder's
`drop-kit-bytes` rung), and the kit's helpers follow the dial position passed as a fact
(`compound_entries.md` U8); one sentence in tuning.md §3 says so.

**Q-R17P-22 (main, `tests/axes/`'s owner). The `--memfn=` deny sweep** (B7).
`run_axes.sh` mentions `--memfn=` only in a comment; memfn/CLAUDE.md calls the `memfn`
section "the ONE enumeration point for `test-axes`". Recommendation: `run_axes.sh` gains a
`--memfn=` arm reading `--list-axes`' `memfn` section, each deny classed DIFFER /
ASSERT_ZERO / REFUSES (§3.4), landing with B1.

**Q-R17P-23 (main). A sabotage id block for revision 3's new plants** (§8.3: SN-1..SN-9).
Recommendation: a block of 10 (one spare), allocated before B1's lane is briefed.

**Q-R17P-24 (main, measure_sets' owner). The second official set and M1** (C12, §5.5).
Recommendation: no second official set (Zen 1's) is committed before M1's `--measures=`
lands, so a bare compile never silently reads another box's literals.

**Q-R17P-25 (main). `exists` as its own class bit** (A19, §4.5). Recommendation: keep it
(L4's question is "is there a search text", and D167 add. 1's A4 note names it), with the
trace-build implication check; deriving it from `proven0` is the fallback if main prefers
fewer bits.

### 7.3 Revision 4's questions, each with a leaning `[rev4]`

D169 answers the main question: when predictability is unknown, the form is V1. It also
covers D1, D1w and R5's path. These three are what it left open. `[rev4.1]` **All three
are now ANSWERED** (below, each with its answer and source). The question text is left in
place as asked; the "Leaning" lines are rev 4's and are superseded by the answers.

**Q-R17P-26 (Frank). A cover shape nobody has measured: V1 or the walk?**

> `[rev4.1]` **ANSWERED (Frank, 2026-10-21; source: `memfn/docs/journal.md` 2026-10-21 and
> the first 2026-10-21 notice at the end of `memfn/docs/responses.md`).** "A set site's
> form is chosen by its cover's TERM COUNT, a compile-time fact: V1 for at most 2 terms,
> the walk for 3 or more. That is grid2's measured trend over all nine timed shapes (V1
> +1..+55% at 1-2 terms, -13/-41/-46% at 3). An untimed combination routes by its term
> count and needs no per-shape key first. B4's acceptance measurement confirms the rule on
> the shapes it moves; a contradicting shape is a finding, not a default."
> Applied in: §1.3a rows 12-13, §1.9, §3.5, §9.2, §9.2a, §9.4. The question below framed
> the case as an unknown per-byte cost; the shape is a compile-time fact, so it is not
> unknown. (The three losers have 3, 4 and 4 terms; "3 or more" is the ruling's.)

- **The case.** D169 is about unknown landing PREDICTABILITY, where V1's
  worst case is a bounded loss on regular data (+15..+35%). A cover shape with no
  measured key is a different unknown: V1's per-byte COST is unknown on it.
- **Why it matters.** On measured multi-term shapes V1 is 13% to 46% SLOWER than the
  walk at every landing regime (grid2read §3.2: (2,0,1), (3,1,0), (3,0,1)).
- **Today's population.** 54 byte-arm sites on unmeasured shapes stay on main's walk
  through R7w (§3.5).
- **Leaning: keep the walk there (R7w)**, and measure a new shape before it routes, as
  item 3a did for three shapes. Reading D169 as "V1 there too" would ship an
  unmeasured loss that does not depend on the subject.

**Q-R17P-27 (Frank). The VM hat at |S| = 1 (F2): does it need measured data to move?**

> `[rev4.1]` **ANSWERED: YES, F2 defaults to V1 (Frank, 2026-10-21; source: the journal
> entry and the second 2026-10-21 notice in `memfn/docs/responses.md`).** "The VM hat's
> one-byte attempt search (F2) defaults to V1 at B5, not B4, with its dense g = 2 cells
> (V1 -38%) named as expected losses up front. It is D169's landing trade (V1 +33..+54%
> at g >= 8)." So F2 has no density condition and does not wait on the gap grid or on a
> density kind. Applied in: §1.3a row 1, §1.9, §3.1 (B5), §3.1a item 6, §3.4, §9.2a.
- **What grid2 found.** V1 saves +0.515 on the slope there, and wins 33-54% on
  find-all at g ≥ 8. It loses +38% at g = 2, with the crossing near 4 B (interpolated).
- **Two readings of D169.** It keeps the walk at the VM hat "until F2" without saying
  what F2's condition is. Either F2 fires on a default compile under the same
  presumption D169 makes for set sites (large gaps, accept the g = 2 loss as an
  expected loss), or F2 fires only when a measured analysis object says the gaps are
  ≥ ~4 B.
- **Leaning: the first.** The VM hat's trade is the same shape as the set sites'
  trade D169 accepted. Build F2 at B5 with no density condition on default compiles,
  list its g = 2 cells among the expected losses (§9.2a), and keep the R5-style regular
  regime as the way to the walk.
- **The alternative.** Wait for the gap grid between 2 and 8 B (§3.1a item 6) and for
  a density kind in the analysis object.

**Q-R17P-28 (Frank). The pre-scan trigger fired only on the letter: build P1?**

> `[rev4.1]` **ANSWERED: record P1 as fired on the letter, do NOT build it (the kit
> manager's call, 2026-10-21; source: the second 2026-10-21 notice in
> `memfn/docs/responses.md`: "P1 recorded as fired on the letter, not built (it never
> fires on a default compile; D77)").** Rev 4's leaning stands as the answer. Applied in:
> §1.4, §3.1 (B5 item (d)), §3.4, §8.3 (S978 UNREACHED).
- **The ruled trigger.** Q-WR-9 builds the priced pre-scan row P1 "when a TUG cell is
  measured losing for want of it".
- **What grid2 found.** It found two such cells, losing 1.5 ns per call (3.4-3.8%). On
  absent bytes the same pre-scan wins ×49-×112.
- **Why it matters little.** P1 reads E only at MEASURED provenance, so it would never
  fire on a default compile; it is work for a row that only a measured bundle reaches.
- **Leaning: record the trigger as fired but do not build P1 at B5.** Re-ask when a
  measured-bundle workload exists (D77, high-impact focus).

---

## 8. Denies, controls and sabotage

### 8.1 G1: pcrec's gate, by step `[rev2]` `[rev3: B1-B5, B15, B17, C1, C6, C11]`

- **B0-B3b** `[rev3]`: byte identity of ARTIFACTS (emit_sweep streams 1-4) over the full
  population, the start arms, `-e utf8`, `--engine=vm`, the lowsize/lowboth variants, at
  SIMD-off, at SIMD-on (`[rev3 B1]` sweeparm's `-fmemfn-simd` arm with its DIFFER_PINS
  floor, S981) and under `-fcomments` (`[rev3 B2]` sweeparm's arm, S982): 0 movers against
  the step's base (main; main-after-E-1 from B3a). `[rev3 B3]` Streams 5 and 6 move only
  by the step's DECLARED delta, checked both ways. `[rev3 B17]` The population includes
  rwquest's and the bench's patterns (`--patterns-file`, the patterns the delivery is
  justified by, §9.3) and the long-prefix and prefix-invariance runs
  (`run_longprefix_sweep.sh`, `run_prefix_invariance.sh`: the kit now writes stems from
  the prefix, K79/K80). `[rev3 C11]` B2 and B3b also run under the test-build lever's
  synthetic sets (`all-walk`, `all-v1`, `all-wide`, every-derivable-key): 0 movers, which
  checks the routing rule rather than arguing it. `[rev3 B4]` The trace compare admits
  exactly the step's DECLARED trace delta (new `fd` records at B1; the retired or
  re-sourced `cand_rows[]` records at B2 and B3b). `[rev3 B5]` The routed-record floors
  (§1.6) per (kind, row) from B2. No timing.
- **B4 (rev 1 §6.2, kept)**: the population is a pcrec-side artifact diff (the census
  reader extended), never the kit's `moved`. SIMD-off: default against
  `--memfn=no-pf-terms-mask` (the whole move against MAIN's walk, `[rev3 C6]` the baseline
  every prediction is stated against), ~~against `--memfn=no-fd-r0` (R0's own effect on its
  population), against `--memfn=no-fd-ndisp` (the dispatch's, if paid).~~ `[rev4]` R0 is
  retired and no dispatch is paid, so those two arms are gone; the expected-loss cells
  (§9.2a) are reported and not scored. Kit tier on the
  Linux dev box (D144 add. 1): taskset-pinned, A/A, layout-perturbed pairs (the I-148
  corrigendum's rule). Both layers reported. `[rev3 B15]` **Every kit deny at once ==
  main modulo a COMMITTED normalizer** (it strips the abi digit and the `<PREFIX>_MEASURES`
  line, and compares `-fcomments` text separately; the +27-byte precedent of
  `dialtrain_byteid.md` used one): the independent control for B4's census. `[rev3 C1]`
  The one-byte and presence populations are 0 movers under the synthetic set holding
  every derivable `xover` key.
- **B6:** `-fmemfn-simd` against `-fmemfn-simd --memfn=no-pf-terms-w32` (A1's effect) and
  against both W64 denies (the SIMD layer against the CURRENT scalar, D147).

### 8.2 G2 and the every-set answer test (rev 1 §6.3-§6.4, kept; `[rev2]` families added)

- **Thresholds and spans** (B4): generated sets × synthetic thresholds N1 ∈ {0, 1, 7, 8,
  35, 36, 63, 64, 65, SIZE_MAX} × (n, start) incl. `n − start` ∈ {N1−1, N1, N1+1} and
  `start > n`; every answer against the byte loop; the chosen form against an INDEPENDENT
  evaluation of the declared rows (the G2 script parses the set file and the listing
  itself, never the kit's resolver). D27-blinded, as before.
- **W64 candidate sequences** (B6): setfind §12.2's `lo` sequences at W = 64, guard
  pages, ASan, UBSan.
- **Form-independence of the cache** (B4): a test build flips `f` between uses; answers
  stay equal.
- `[rev2]` **One-byte family** (B2, KW-10): the count rule (D1, D1w at the seek role, D1c
  for a context stop); NONE's answer identity at DFA consumers (through the shadow until
  B5); NONE refused where `need` is REQUIRED; MLINE's generic shape. `[rev3 A5, A17]`
  `fd-d1` renders D1w's WALK on DFA and hybrid one-byte sites (answers identical) and
  does not reach a DFA_ATTEMPT site.
- `[rev3 A4]` **The query family** (B1): for every generated site, `mf_ask` then
  `mf_define`; the classes agree; `mf_ask` leaves the art unchanged (a second define of
  the same site after an ask is byte-identical to one without); `exists = 0 ⇒ proven0`
  all ones.
- `[rev2]` **Presence family** (B3b, KW-10): absent-at-end discovered lazily; REQUIRED-all
  on proof routes; EMPTY before the first element; re-asked ranges with `omin` ≥ 0 at a
  raised `start`; plants reach NON-DFA routes only.
- **`make test-memfn-sets`** (B4, in TEST_SECTIONS): the R17-b mover population 1 in 8
  plus every `.rxt` cell for those patterns, compiled under every committed set and the
  synthetic extremes `all-walk` (N1 = SIZE_MAX), `all-v1` (N1 = 0, R0 off), `all-wide`
  (N1 = N2 = 0) and measure_sets §8.1's dispatch-carrying set, reached through the harness
  lever (`build/pcrec-harness --harness=measures=FILE`) until M1. The answer arm runs the
  harness's oracle-verified expectations (a per-form corpus differential); the structural
  arm checks each artifact's `__form__*` literals against an independent parser of the set
  file, the stamp names the loaded set, and a REACH floor per dispatch arm is met on
  generated boundary subjects (measure_sets F7: 97.8% of corpus subjects are under 36 B).

### 8.3 Sabotage, by step `[rev2]` `[rev3: A13, A16, B5, B6, B11, B14, B16, C2, C3, D4, D9, D10]`

Ids: S911-S922 (R17-b′, allocated; R-19's rows are inside it) and S964-S980 (R-21's
SW-1..SW-17, allocated). pcrec-side [MEASURE-SET] rows are S943-S963 (main's). S981/S982
are lane sweeparm's (the two emit_sweep arms, delivered with B0). `[rev3]` Revision 3's
new plants SN-1..SN-9 need ids (Q-R17P-23: a block of 10). Ports carry their own,
`[rev3 A16]` listed exactly (from `lane/memfn-r17`'s tree): at B0 R17-a's S846-S849; at B4
R-17's r17d rows S820-S824 and S826-S843 (the V1 forms, covers and storage), R17-b's
S850-S854 and R17-c's S867-S870 (the size rung). S825 is MAIN's own row
(`S825_span_match_exported.sh`, [LOSS-REVIEW]) and is not a port. All are re-aimed by
`[rev3 A13]` `docs/design/start_table/sabotage_anchors.py --step NAME=A..B` at each build. Main's rows anchored on
pcrec's encoding (`cand_derive`, `find_site`, the pre-check and handoff sites:
S266/S288/S294, S457-S477, S800-S814 among them) are re-aimed or re-run by the same tool
at B2 and B3b; the list is derived there, not counted here. Every presence plant must
reach a route with NO DFA scan in front, or it reads green vacuously.

| id | plant | detector | step | reach witness |
|---|---|---|---|---|
| S911 | a dispatch literal off by one | §8.2's structural arm; G2's form-choice check | B4/B8 | a paid dispatch site; UNREACHED (declared) while no set pays |
| S912 | the dispatch compare inverted | the same | B4/B8 | the same |
| S913 | the form byte never written (always 0) | the REACH floor per arm; the trace | B4/B8 | the same |
| S914 | the bounded walk arm ignores `end_back` | answers (G2, corpus bounded cells); ASan over-read | B4 | `[rev3 B11]` needs `__walk` emitted (a paid dispatch or a T3-passing walk-only scaffold): UNREACHED (declared) until either exists |
| S915 | the walk arm passed the wrong table (`start_bytes` vs `can_begin_match`) | answers on dfa-hat cells | B4 | `[rev3 B11]` as S914: UNREACHED until `__walk` is emitted |
| ~~S916~~ `[rev4]` RETIRED with R0 at B4 (its plant has no row to act on; declared retired in the sabotage index, the S919 precedent) | R0 counts EQ terms as RANGE | movers by ID against `[rev3 B16]` `r17b_movers.py`'s independent cover search | B4 | `[rev3 B11]` a (1,1,0)-shaped cover (one RANGE plus an EQ: the plant puts it in r2, the truth does not), under a synthetic set holding the saving keys of BOTH (1,1,0) and the r2 class, so the row's skip cannot hide the plant |
| S917 | an ABSENT set key read as 0 | the totality test (the key removed ⇒ the next row/R7) | B1 (regime_pick, shadow), B4 | ~~R0's key~~ `[rev4]` ~~R7's key on a winning shape (removed ⇒ R7w)~~ `[rev4.1]` a key-reading row (R5's regime fact; R8 at B6): R7 reads no key now, so its plant is SN-8 |
| S918 | the pay rule ignores C_disp | the per-set expected-emission manifest | B4/B8 | a set with a failing C_disp |
| S919 | `body` UNSTATED read as ONESHOT | G2: N/M rows must skip (an oracle case; the trace) | B1 | a builder with `body` 0 (a G2 site) |
| S920 | the START hook's text replaced by `0` | `[rev3 B11]` an INDEPENDENT reader of the activation origin in the emitted C (the variable the entry's guard reads, located by pcrec's own emitted-text census), compared with `__form(`'s argument; not the builder's stated start (a shared source) | B4 (read; `__form(` emitted only with a paid dispatch, UNREACHED until then) | a relocate-path site (start ≠ 0) |
| S921 | the shadow call emits a byte | emit_sweep's 1-in-8 sample at SIMD-off | B1 | every FIND site |
| S922 | `[rev3 D6]` a row's `routed` bit set before its step (R7's at B2) | emit_sweep: V1 movers appear; the routed-record count rises past its floor | B2 | a one-RANGE-term set site (`[0-9]+x`) |
| S964 | SW-1 K65-narrow: a REQUIRED set answered by one member on a no-DFA route | give-up (W1) | B3b | W1 |
| S965 | SW-2 K66-window: a REQUIRED run answered by its window | give-up | B3b | K66's regression (`k66_precheck_whole_run.rxt`) |
| S966 | SW-3 decided-late: a candidate yielded before every REQUIRED span is verified | give-up (G-2) | `[rev3 B11]` B4 (the VM hat's FIND routes at B4; at B3b the merged site holds no hat span 0 that could yield early) | W1 with the VM hat |
| S967 | SW-4 edge-first: the edge attempt emitted before the verdict | give-up (W2) | B3b | W2 |
| S968 | SW-5 an unconstrained reply where span 0 is REQUIRED (NONE at VM_ATTEMPT) | give-up (W3, GIVEUP1 F5) | `[rev3 B11]` B5 (F0, the only row that can pick NONE, is built at B5): UNREACHED (declared) until then | W3 |
| S969 | SW-6 `omin` mis-signed | answers | B5 (UNREACHED while every `omin` is 0, declared) | a true-`omin` site |
| S970 | SW-7 the unbounded one-byte row loses its `pos ≥ n` guard | ASan over-read | B2 | a `(NULL, 0)` subject on `memchr` PF |
| S971 | SW-8 the bounded row loses the `n − 1` clamp / wrapper | ASan | B2 | a `memchr-bounded` site |
| S972 | SW-9 the DFA hat's re-seed after a moved skip dropped | lost match (ssedge's mutants) | B2 | `first-memchr-bounded` |
| S973 | SW-10 the VM hat at \|S\| = 1 rendered with memchr per attempt | structural census only, declared (perf-only, Q-R5) | B2 (D1w routes the hat's \|S\| = 1 seek, `[rev3 A7]`) | `(x[a-z]+)y\1` |
| S974 | SW-11 the read-back says "scan present" when NONE was chosen | give-up (K65) via G1 on a proof-only route | B5 (UNREACHED until F0 fires) | a NONE site beside a REQUIRED span |
| S975 | SW-12 `MEMFN_LIBC` omits a libc symbol the text still calls | C11 `nm -u` | B2 | any LIBC site |
| S976 | SW-13 the libc row used under a stale `libc:` key | the `libc-mismatch` listing flag (§5.3) | B5 | F1's keys |
| S977 | SW-14 MLINE's stream opens at the edge, reading `s[start − 1]` at offset 0 | ASan | B2 | a `(?m)^` site at `search_from` 0 |
| S978 | SW-15 the pre-scan row prices from a `prior-*` kind as if measured | the listing / per-set manifest | B5 (at Q-WR-9's trigger) `[rev4.1]` UNREACHED, declared: P1 is not built (Q-R17P-28) | P1 |
| S979 | SW-16 a carried presence verdict not invalidated when `start > valid_until` | answers | B9 (R17-b″) | an iterator over a late occurrence |
| S980 | SW-17 member order swapped in a tie (PR-7) | the B3a shadow comparator, not answers | B3a | a tie between two set members |
| `[rev3]` SN-1 (B5) | a row's `routed` bit left 0 after its routing step (the REVERSE of S922) | the pcrec-side routed-record count per (kind, row) falls below its floor (§1.6); byte identity cannot see it | B2, B3b, B4 | each routed group's disagreement witness (§1.6) |
| `[rev3]` SN-2 (A4) | `mf_ask` reports `exists` = 1 where the rendered form is NONE (or a wrong `proven0`) | the query/define agreement check (§4.5 rule 2); G2's query family | B1 (trace), B2 | a site whose terminal differs between two rows' readings (a NONE site under the synthetic set that makes F0 fire, in the test build) |
| `[rev3]` SN-3 (D4) | G1's reader asks the start site before FIRST's selection is closed (or reads `pres` it did not declare) | the trace-build undeclared-read / open-selection trap | B1 | any G1-admitted artifact (`req-admit` "dominated") |
| `[rev3]` SN-4 (C2) | a row's `basis` left UNSTATED, or a key-free row marked MEASURED | the table self-check (kit build) | B1 | the table itself (every build) |
| `[rev3]` SN-5 (B14, C1) | ~~R1's~~ `[rev4]` R2's fast-terminal condition dropped | B4's every-derivable-key synthetic set: one-byte movers appear `[rev4]` (at a W16/W32 variant from B6; R1 is deleted) | ~~B4~~ `[rev4]` B6 | a one-byte DFA_SCAN site (`a+b` shape) under that set |
| `[rev3]` SN-6 (B6, D10) | the five-pick comparator returns "agree" always (or one pick's port drops its tie rule) | the planted disagreement per pick (a site where port and pcrec must differ under the plant); the per-pick floor on non-trivial sites | B3a | per pick: a set with two equally rare members (P3), a G1-kept span (P2), a strictly-rarer set (P4) |
| `[rev3]` SN-7 (B9) | a row edit after a routing step with no `finder_history.md` entry | the lockdown digest check | B2 onward | any routed row |
| `[rev3]` SN-8 (C3) `[rev4.1]` re-aimed | ~~R7 fires without its shape's saving key (the comparator's absent-key rule inverted)~~ R7's term-count comparator inverted or off by one (fires at 3 terms, or declines at 2) | B4's census by TERM COUNT: a mover on a cover of 3 or more terms, or a 1-2 term site left on the walk; and the shape-sign check (a measured shape whose sign contradicts its count is a finding) | B4 | a (0,3,0)-shaped cover (3 terms, not among grid2's nine shapes) |
| `[rev3]` SN-9 (D9) | the pay rule's tie direction flipped (a T1 tie pays) | the arithmetic grid with planted off-by-ones | B1 (regime_pick, shadow), B4 | a synthetic set whose saving equals the charge exactly |

`[rev4]` No new sabotage id is needed by revision 4. R5's new condition is unreachable on
every compile until a landing-regime kind exists; its plant (an UNSTATED regime read as
REGULAR) takes an id with that kind, declared UNREACHED until then.

Rev 1's SB6 (the W64 tail read), SB11 (the SIMD-on use differs; C18 already detects it)
and SB12 (w32 routes `f == 1` to W64) move to B6, which requests its own ids; SB10 (the
stamp names the wrong set) is [MEASURE-SET]'s (S943-S963).

---

## 9. Acceptance

### 9.1 The first delivery (B0-B3b) `[rev2]` `[rev3]`

Accepted on structure, not on timing: 0 ARTIFACT movers at SIMD-off, SIMD-on and under
`-fcomments` over the full population incl. rwquest, the bench and the synthetic sets
(§8.1), the listing streams moving only by their declared deltas, the reader shadow's
equality (B1-B2), the five-pick shadow at 100% with its per-pick floors (B3a), the
routed-record floors (B2, B3b), the G2 families green (the query family included), every
sabotage row of B0-B3b DETECTED solo (or UNREACHED with its derivation), `make test`
green through `scripts/perfrun`.

### 9.2 B4, the routing commit `[rev3: C6]`

`[rev3 C6]` **The baseline is MAIN's walk** (the current best scalar layer on main, D147),
never R17-b (the kit branch's V1-everywhere, not on main). A cell's comparison is
"B4's pick against `--memfn=no-pf-terms-mask` (main's walk)", in absolute u·B, against the
cell's own A/A floor (§2.5's `floor(cell)`).
1. ~~[REGIME-EVAL]'s pre-registered bars (G0-G4 per layer and shipped filter) PASS or
   PROVISIONAL PASS on the judge populations (J1 open, J2a), the table's listing hash
   recorded (regime_eval §5.2); the hash IS the LOCKDOWN digest (§1.8).~~
   `[e8min, D170]` **The kit-tier bar is the MINIMAL E8** (`r17b_prime/e8min/plan.md`, prereg
   `e8min/prereg.md` at bf70e5dff): G0 counts, G1 against always-walk, G3, §9.4's per-cell rule
   against the EL/SS list, and item 2's term-count check, read by `e8min/verdict.py` on J1 (the
   real users' patterns) in one quiet window. It bars TIMING only. B4's correctness gates are
   unchanged: 0 answer movers, the identity sweeps, mech for every new or moved anchor, and make test.
2. G1 at both layers on the mover population: ~~R0 cells NULL against the walk;~~ R7 cells
   (measured shapes only) not worse than the walk beyond the floor on the regime their
   key was measured in `[rev4]` (the member-free slope regime), the EXPECTED-LOSS cells of
   §9.2a excepted; every dispatch interval holds against its neighbour (if paid);
   the dispatch charge NULL on LINER and TUG cells.
   `[rev4.1]` **B4's measurement also CONFIRMS THE TERM-COUNT RULE on every shape B4
   moves.** R7 now routes by count (≤ 2 terms), so "measured shapes only" widens to every
   shape the rule sends to V1, including combinations grid2 never timed. For each such
   shape the G1 cells are read for a V1 saving beyond the floor against the walk. A moved
   shape that CONTRADICTS the rule (a 1-2 term cover whose V1 does not save, or loses)
   is a FINDING, not a default: it is reported with its cells and its term count. A loss
   beyond the floor on an unlisted cell is already §9.4's refutation of B4.
3. The named residual (bounded dense find-all, dfa-hat on prose (F7), dig on digits,
   vm-hat prose1m) is a STATED LOSS against the walk, shipped under Q-REVAL-1's ruling
   (the regime bars replace D162 add. 1's no-loss gate, Q-R17P-4) and bounded by the
   judge's ~~G2/~~G3 caps `[e8min, D170: G2 dropped with E4b]`: REPORTED per cell, and B4 fails if a cap fails. R5 would route those
   cells to the walk, but it reads E at MEASURED provenance only, so on a default compile
   it does not fire; that is the reason the loss ships, said here rather than left implicit.
4. The official verdict is a bench run on the targeted hardware (D144 add. 4).

### 9.2a The expected losses, named before B4 times anything `[rev4]`

D169 asks B4's own measurement to name its regular-landing cells as EXPECTED losses up
front. The rule below is pre-registered: it is committed with E5's pre-registration
(§3.1a) and before any B4 timing, and no timing result may edit the list afterwards.

**The rule.** A cell is an EXPECTED LOSS iff both hold:
1. its site is a B4 mover at OFF (§1.3a: R7 → V1 on a cover of at most 2 terms;
   `[rev4.1]` rev 4 said "on one of the six winning shapes", and the 54 sites on untimed
   shapes now join by term count, their list OWED to the regenerated manifest);
2. its subject's landings for that site's candidate set are REGULAR with a mean gap
   ≤ 8 B.

The 8 B bound comes from grid2's measured losing region: V1 is +14.9% at g = 2 and
+34.9% at g = 8 on regular landings. Irregular cells at the same gaps win.
- **"Regular" is read off a counter, never the pattern.** It is the walk's branch
  misses per landing on that cell (`perf`, as grid2's F2 pass read them). grid2
  measured two clusters, 0.009 (regular) and 0.97-1.44 (irregular). The list's
  boundary is **0.1 misses per landing**. That value is labelled
  `UNMEASURED DEFAULT: between two measured clusters` (D149).
- **No counters.** Where counters are unavailable, the cell is selected by the gap
  sequence itself: the landing positions the walk reports, with one gap value
  covering most landings. The cell is then marked `selected-without-counters`.
- **Regular cells with a mean gap above 8 B** were not measured by grid2. They are
  WATCH cells: reported, not expected, not scored.
- `[b4prep-close]` **The SHORT-SUBJECT class** (kit manager, confirmed by main,
  2026-10-21; D169's reasoning). A second class of EXPECTED LOSS: a B4 mover at OFF
  (condition 1) whose call length L is at most 64 B, at any gap and any landing
  regularity. The regular-landing rule above stays as written. Registered under it,
  before any B4 timing, are the three grid2 losses it was written for (the rows are in
  `r17b_prime/b4prep/expected_losses.md` section 3b): **SS1** dfa-hat (0,1,1) L = 32 g = 2
  (+41.3%, also EL5 under the regular class), **SS2** dfa-hat (0,1,1) L = 32 at g >= 16
  (+8.5% / +13.3% / +11.3% / +9.3% / +8.7% at g = 16 / 32 / 64 / 256 / inf), **SS3** dig
  (1,0,0) L = 32 g = 16 (+2.6%). The 2x FINDING line holds for this class too; a loss
  outside the listed classes still refutes B4 (§9.4).
- ~~**If Q-R17P-27 builds F2 without a density condition**, the VM hat's g = 2 cells
  join the list at B5 by the same rule (grid2: +38.3%).~~ `[rev4.1]` **Q-R17P-27 is
  answered YES: F2 is built at B5 without a density condition, so the VM hat's g = 2
  cells (grid2: V1 +38.3% slower; the ruling writes it "V1 -38%") are EXPECTED LOSSES,
  named here up front.** They join this list by the same rule. B4 does not move the VM
  hat, so they are scored at B5, not against B4. D169's landing trade pays for them: V1
  is 33-54% faster at g ≥ 8.

**Known cells, pcrec side** (the list starts from these; the B4 acceptance lane adds
the bench's):
- grid2's own regular-landing groups: `dig` g = 2 regular and g = 8 regular, and the
  dense `reg` find-all groups (grid2read §3.5, an. 6b-6d);
- `dfa-hat` L = 32, where V1 is never faster (grid2read §3.5);
- `bounded`, which crosses at ~64 B (grid2read §3.5, LOW);
- rev 3 §9.2 item 3's named residual: bounded dense find-all, dfa-hat on prose (F7),
  dig on digits, vm-hat prose1m;
- real text by counts only (F2S, not timed): `bounded` on prose V1 +16.7% cycles
  (grid2read §3.9).

**The bench's cells.** The bench owns its subjects, and pcrec does not reverse-engineer
its ledgers. A relay question therefore goes to pcrec-bench through main: *which cells
of the sets B4 will be judged on have a set-FIND site (a byte-class prefilter, DFA hat or
hybrid prefilter) whose subject has dense regular landings, a mean gap ≤ 8 B with one
dominant gap?* Its answer, filtered by the rule, completes the list.

**How the list is used.**
- At G1 and at the bench verdict, each expected-loss cell is REPORTED with its
  absolute delta against main's walk and its floor. It is not counted against B4.
- A listed cell that loses MORE than twice grid2's measured magnitude for its gap
  (`UNMEASURED DEFAULT: 2x`) is a FINDING. So is a listed cell that wins. Either way it is reported.
- An UNLISTED cell that loses beyond its floor refutes B4 (§9.4).
- **D169's revisit trigger.** Any listed cell on a REAL subject of ≥ 64 KiB is reported
  separately as a candidate to revisit the ruling.

### 9.3 Predictions `[rev3: C6]`

Rev 2 carried rev 1's grid1 figures (the S0 replay on repeated 64 KiB) with "re-stated on
grid2 at B4" and no restated number; under Q-R17P-9 (B) grid1's figures are not
comparable. `[rev3 C6]` Each prediction is now an INEQUALITY on named grid2 groups, at a
named layer, with the NULL rule; its NUMBERS are E4b's in-sample streamed replay on grid2,
filled in before E5's pre-registration, and the judge (held-out) is what can refute them:
- ~~**R0**: for the hex-run and word-eq find-all groups at OFF, |pick − walk| ≤
  max(A/A, floor) at every L in the group (R0 makes them NULL).~~ `[rev4]` Withdrawn: R0 is
  retired, and grid2 timed no hex-run/word-eq find-all group (grid2read §4 P1).
- **R7 on measured shapes**: for the (1,0,0) and (0,1,1) groups and item 3a's three
  shapes at OFF, pick − walk ≤ −floor at every L ≥ the shape's measured crossover (V1
  saves where its key says it does).
  `[rev4]` grid2 gives the in-sample numbers, with E4b's replay still the formal
  source:
  - the member-free slope savings of §5.2a;
  - on `dig` find-all with irregular landings, V1 at −9.7..−40.6% across g = 4..∞
    (L = 64 KiB);
  - (2,0,0) at +1.2%, which is 10.7× the slope token and 4.9× the slope's own noise.

  Because no length row exists, the "crossover" is every L ≥ 8 for single calls.
  Regular-landing cells are excluded by §9.2a, not predicted.
  `[rev4.1]` The prediction now covers EVERY cover of at most 2 terms (the rule's
  population), with numbers only for the six timed shapes; an untimed 1-2 term shape has
  the rule's sign as its prediction and B4's confirmation (§9.2 item 2) as its test.
  Covers of 3 or more terms are zero-mover (R7w), so they carry no timing prediction.
- ~~**R1, if paid**: for bounded short find-all at OFF, pick − walk ≤ −floor below the
  dispatch literal, and |pick − V1| ≤ floor above it.~~ `[rev4]` Withdrawn: R1 is deleted.
- **Regret on the grid** (`[rev4]` R0 and R1 are gone: R7 alone changes find-all grid
  rows, and only R2 at B6 would change single-call rows): R0 and R7 change find-all grid rows (R0 turns hex-run and
  word-eq to NULL); R1 and R2 change only single-call rows. `[rev3 C6]` Rev 2's
  "R0, R1, R2 change no find-all grid row" contradicted its own first bullet and is
  withdrawn.
- dfa-hat prose contradicts R5 (g = 10.2 B above every g\*, yet it loses: near-hit depth,
  F7): predicted to stay a residual loss (§9.2 item 3).
- `[rev2]` The one-byte and presence steps carry no timing prediction: they move nothing.
  Their value is coverage: with D161 add. 14, 170 of 172 compiled rwquest questions have a
  start-search site under one window request (sbscope §7), against ~42 for the set-FIND
  table alone.
- **No SIMD-on prediction at B4** (SIMD-on = SIMD-off until B6, so "both layers reported"
  is trivially met there); B6 carries its own: each W64 interval ≤ −floor against V1 at
  W16/W32.

### 9.4 What refutes it `[rev3: C6]`

- An artifact byte moved at B0-B3b, a listing stream moved outside its declared delta, or
  the five-pick shadow disagreeing anywhere.
- A K65 conversion lost: W1 or W2 gives up where main answers.
- ~~An R0 cell not NULL against the walk;~~ an R7 cell worse than the walk beyond
  max(A/A, floor) `[rev4]` that is NOT on §9.2a's pre-registered expected-loss list; a dispatch interval losing to its neighbour beyond the floor; a
  non-NULL dispatch charge on a cell the dispatch does not help. `[rev3 C6]` Every
  comparison has its floor (D144 add. 1); rev 2's "any cell worse than R17-b" had none.
- At SIMD-on, a W64 interval losing to V1 beyond the floor (D147's check).
- `[rev4.1]` **A shape that contradicts the term-count rule** is a FINDING (§9.2 item 2),
  reported rather than defaulted. It refutes B4 only through the bullet above: a moved
  cell losing beyond the floor and not on §9.2a's list.
- `[rev3 C6]` **A bench regression on Zen 1 at SIMD-off beyond the floor.** The SIMD-off
  rows are portable C that ship to Zen 1 and arm64 with Zen 4's literals until those boxes
  have their own sets (§5.5), and the bench box (ubuntubudu, Zen 1) gives the official
  verdict (D144 add. 4). Rev 2's "on Zen 1 the crossovers move: that refutes nothing" is
  withdrawn: it pre-excused the case that matters.

---

## 10. Standing design questions (docs/design/CLAUDE.md) `[rev3]`

1. **The measurement regime: RELEVANT** (from B4 on; B0-B3b read no measurement).
   - Every value B4 reads is one Zen 4 run (7700X, CPU 14, gcc 15.2 `-O2`, governor
     performance), `kit-grid@2`, streamed subjects under Q-R17P-9 (B); member-free single
     calls for F, crossovers and the dispatch twins; find-all passes for g\*, c_cold, the
     per-use cost and g_none.
   - Regimes that would flip a decision: Zen 1's 2×128 AVX2 moves every W64 row (F5, its
     own set); fresh irregular landings move g\* down 2-4× (gridread §5.3); single calls
     with landings move R1's crossover past 32 B (§4.3); near-hit text flips V1 against
     the grid (F7); repeated against streamed subjects moves the walk's branch misses from
     150-250 to 0.4-22 per KiB (gridread F2), which is why Q-R17P-9 fits on streamed cells.
   - The libc rows are measured against the build box's glibc while the artifact runs on
     the caller's library (§5.3): a different libc can flip F1, so the set says which one
     it measured.
   - NONE's effort depends on the consumer's own per-byte step (≈ u for the DFA on this
     box, INTERPRETATION): a box where the DFA step differs from the walk moves g_none.
   - The dispatch charges are twins until [REGIME-TWIN] measures the built dispatch
     (§2.5).
   - `[rev3 C4]` Each null floor is its OWN regime's (single-call member-free 0.17%,
     find-all 3.4%, EXT 0.38%), so a decision is never tested against another regime's
     noise; `[rev3 C7]` the slot's walk is bimodal across launches on repeated groups,
     which the cross-launch rerun trigger catches.
   - `[rev3 A6]` A shared find body charges a mode branch per call (M24), unmeasured: an
     M-reading row on a shared PARAM body does not pay until it is measured.
   - `[rev3 C3]` R7 is measured per cover SHAPE (β(V1)/β(walk) spans 0.57-1.41 across
     five shapes); ~~an unmeasured shape takes the walk.~~ `[rev4.1]` the shape sets V1's
     cost, but the deciding fact is its TERM COUNT, known at compile time, and the
     measured trend over nine shapes is monotone in it; an untimed combination routes
     by its count (Q-R17P-26).
   - `[rev4]` **Landing PREDICTABILITY is the regime axis that flips V1 against the
     walk** (grid2read §3.5). Length does not flip it, and gap alone does not. The
     default presumes irregular landings on large subjects (D169), so a regular-landing
     subject is a regime that flips the decision. B4 names those cells up front
     (§9.2a), and R5 takes the walk once a measured or stated regime says so.
     grid2's values are one box and one streamed condition; Zen 1 (F5) may move every
     shape key.
2. **The independent control: RELEVANT.**
   - **B0-B3b:** byte identity by emit_sweep (pcrec's tool, sharing nothing with the
     kit's renderers); the five-pick shadow compares the kit's PORTS against pcrec's own
     functions (subject: the port; expectation: pcrec's code); the reader shadow compares
     each pcrec reader fed by its own row with the same reader fed by the kit's query;
     PR-11's census of collapsed hybrids shares no source with the req walk. `[rev3]`
     SIMD-on and `-fcomments` identity are emit_sweep arms (sweeparm), not C18's
     ON-vs-OFF compare of one build.
   - `[rev3 B5]` **Routing**: zero-mover routing is made observable by a pcrec-side
     routed-record count (pcrec's own trace, never the kit's counter) and per-group
     disagreement witnesses; the reverse plant SN-1 tests it.
   - `[rev3 A4]` **The query** is checked against `mf_define`'s rendered class (two code
     paths over one site), and by G2 over generated sites.
   - **The table's semantics** are checked against the D27-blinded oracle (E3b,
     regime_eval §5.4), never against itself; the E4 agreement check proves only the
     plumbing and says so.
   - **Answers**: G2 against the byte loop over a generated space; `test-memfn-sets`
     against the harness's libpcre2/python-verified expectations, with extreme sets that
     force each form so a wrong form cannot hide behind a dispatch.
   - **Populations** (K35): counted by pcrec-side readers of emitted C (`[rev3 B16]`
     `r17b_movers.py`'s independent cover search before B4, `census_shapes.py` on B4's own
     masks after; sbscope's and pcscope's censuses), each step re-counting its own; never
     the kit's `moved`. `[rev3 B6, D10]` The shadow's denominator is the pcrec-side
     activation census, and each ported pick has a floor on NON-TRIVIAL sites.
   - **Reach** ([MECH-REACH]): every plant in §8.3 names a witness that reaches its site;
     presence plants reach NON-DFA routes (W1-W3), since a DFA-route-only green is
     vacuous; rows whose site is unreachable before a step are declared UNREACHED with
     the step that reaches them.
   - `[rev4]` **The expected-loss list** (§9.2a) is selected by a counter (the walk's
     branch misses per landing) or by the subject's gap sequence, and is committed
     before B4 times anything. It is never chosen from B4's own timing, which is the
     outcome it excuses.
   - **The unavoidable shared source** is the measured numbers' own truth: controlled by
     per-group A/A floors, the NULL rule and the held-out judge, not by this design.
3. **What moves when the data is regenerated: RELEVANT.**
   - **Through B3b, nothing:** no ROUTED row reads a measurement; the PRES picks read
     the frequency kind, so a FINDINGS bundle change moves them exactly as it moves
     today's pcrec picks, censused by [KNOW-SRC]'s one tool.
   - `[rev4]` **From B4, under §1.3a:** ~~a new default set can flip a shape's R7 verdict
     either way (the six winning and three losing keys), and a newly measured shape
     moves its sites from R7w to V1.~~ `[rev4.1]` R7 reads no key now, so a regenerated
     default set moves R7's verdicts only through `kit.terms.V1max` (derived from the nine
     saving keys' signs); a regenerated set whose signs keep the same sign change moves
     nothing, and one that flips a sign moves that key, a default-moving event with its census. A landing-regime kind, when built, moves R5's
     sites to the walk: a default-moving event with its census. There are no dispatch
     literals and no R0 verdicts any more.
   - **From B4:** a new DEFAULT set moves the dispatch literals, R0's verdict per shape,
     `[rev3 C3]` which shapes R7 routes (a newly measured shape moves its sites from the
     walk to V1; `[rev4.1]` no longer: R7 routes by term count), and `<PREFIX>_MEASURES` on every consulting artifact: an abi event with its
     `MOVERS.tsv` in the same commit (D162 ruling 1, measure_sets §3.6). A new non-default
     set moves nothing. A kit form-body change stales its rows, carried and flagged
     (D166 add. 2). A libc version change is a set-level flag (§5.3).
   - **Spec (D80):** every step's hunks are in §3.4, including the registry events at B1
     (`[rev3 A9]` five `--list-axes` rows) and B3b (bit 45 retired), which move no artifact
     byte and are DECLARED listing deltas.
   - `[rev3 B9]` **The table itself** is data whose regeneration is checked: its listing
     digest is LOCKDOWN's pin, and a digest change without its `finder_history.md` entry
     fails.

---

## 11. Findings `[rev3]`

Rev 1's, as they stand now:
- **F1. One stateful site per artifact, corpus-wide** (996 byte / 2,910 byte-vm R17-b
  movers). `[rev2]` The merge keeps it: presence and find are one site (§1.1).
  `[rev3 A3]` On a VM hybrid the presence-only site holds no FIND state in a one-shot
  call; under the iterator its carried positions are declared rows of S (§6).
- **F2. The scaffold is not free in code** (−3..+14 instructions, 0 of 6 identical):
  C_scaffold is M18, measured, never assumed.
- **F3. Forms-per-site in `MEMFN_FORMS` conflicted with the ruled spec.** RESOLVED
  (Q-R17P-1): `--emit-facts`.
- **F4.** `[rev3 A6]` REWRITTEN: **M is the find body's mode, a constant per entry where
  the find part is inlined and a runtime PARAMETER where it is shared** (findall_iter
  §4.2, D163 add. 7). Rev 1 and rev 2 said "M is fixed per entry body, so no row ever
  emits a compare on M"; a shared body pays one branch per call (M24, §2.4).
- **F5. A SIMD W64 arm can be added only where the SIMD-off text routes through
  `__next`.** Unchanged.
- **F6. R0 keyed by exact shape would miss `\w`** (179 of 219). Unchanged.
- **F7. ALPHA's residual is not all E's** (dfa-hat prose: near-hit depth). Unchanged.
- **F8. D166's one-run rule makes the dispatch impossible on grid1 data.** `[rev2]` Its
  consequence is narrowed by F10.
- **F9. Two R17-b statements hold only at SIMD-off.** Unchanged.

`[rev2]` New:
- **F10. The first delivery needs no measurement set** (§3.2). With a routing state per
  group, every routed row through B3b reads no set value, so B0-B3b ship before grid2,
  M0 and the judge.
- **F11. Presence `omin` measured from the MATCH START** (not from span 0) is what makes
  B3's window exactly today's `[posvar, n)` and keeps every read at or after the
  activation's start; measured from span 0 the window would widen to `[lo − h_max, n)`,
  a mover. It refines C-1 and is why PR-6's "0 is a sound under-estimate" holds for a
  landmark origin too (§4.1).
- **F12. Proven facts are decided once per site, at layer OFF** (§1.5 rule 1): D161
  add. 8 plus the floor rule. NONE is the first row it constrains.
- **F13. R1 must read the crossover against the TERMINAL pick.** Rev 1 read V1-vs-walk
  regardless, which would have attached a dispatch to one-byte LIBC sites the moment grid2
  paid the set sites; read against the terminal, the missing `LIBC`/`WALK` key keeps them
  zero-mover with no special case (§1.3). `[rev3 B14, C1]` Superseded in part: key
  ABSENCE is a property of a data file, and grid2 measures that key's inputs; R1/R2 now
  apply only above a FAST terminal (V1, W64), as row data.
- **F14. KW-8's fifth pick is an ORIGIN choice** under framing (a), so the kit ports four
  picks and shadows the fifth (Q-R17P-11). `[rev3 A11]` Its input must also be pcrec's
  own facts (D167 add. 1).
- **F15. Q-WR-11's "no `-fcomments` byte move" cannot hold if the comment's text
  changes**; the change rides B4 (Q-R17P-12).
- **F16. findall_iter's S table lists a pcrec K5 pair-hit row** that loses its owner under
  the merge. `[rev3 A10]` It does not retire on the merge alone: one carried position is
  not linear with 2+ REQUIRED spans; "S = 48 B" withdrawn (§6, D167 add. 1).
- **F17. `libc:` provenance cannot be row staleness**: the run-time library is the
  caller's (§5.3, Q-R17P-14).
- **F18. regime_eval puts the paranoid suggestion in E4, but grid2 runs before E4**; it
  moves into grid2's prep (§5.4).
- **F19. R-19's three FIND storage points omit the PRE composite's entry**
  (`pcrec_emit_req_byte_check`), which the merge needs as the site's first use; winreq
  §1.1 asked. `[rev3 A21]` Rev 2 ASSUMED R-19's "every builder" covered it, MLINE and
  `attempt_entry`; revision 3 ASKS (Q-R17P-16).
- **F20. One-byte sites are zero-mover against BOTH branches, set sites only against
  main**: the kit branch's R17-b already moved the set sites (its abi 77), so the
  baseline of every census in this plan is main (Q-WR-10).
- **F21. A row whose quantities grid2 measures cannot be source at B4 unless its movers
  are B4's.** grid2 measures M19-M22 so that F0/F1 can be judged; if those rows were
  source when grid2 becomes the default set, they would fire at B4 and fold one-byte and
  NONE movers into the routing commit's census. So F0, F1 and P1 are built at B5, after
  lockdown, as formal additions (§1.3). `[rev3 A7]` F2 (the VM hat's |S| = 1) joins
  them for the same reason.

`[rev3]` New (from the panel, each with its finding id):
- **F22. A fact a selection reads must exist before the selection** (A4). The kit's
  read-back at define arrived after every reader's decision; the define-time query
  (§4.5) moves it before, pure, so a rejected alternative leaves nothing behind.
- **F23. "One site per search entry" is one site per ACTIVATION** (A1, A3): the storage
  point must dominate the first use, and two functions with two activations (the VM
  hybrid) hold two sites.
- **F24. Zero-mover routing is unobservable by byte identity** (B5): routed-and-identical
  and never-routed are the same bytes, so routing needs its own count and its reverse
  plant.
- **F25. A default selected by data absence is a latent mover** (C1, C3): R1 on one-byte
  sites and R7 on unmeasured shapes; both became row data (a fast-terminal condition, a
  measured-key comparator with a WALK fallback). `[rev4.1]` R7's half is re-ruled: the
  comparator is the cover's term count, which exists for every shape, so there is no
  absent datum left to be a default (F32).
- **F26. `fd_rows[]` was the kit's fourth table with a fourth walk** (D1): it now adopts
  `kit_walk`, the first table to do so after the kit's own three, and its applicability
  moves into the gate.

`[rev4]` New (from grid2, each with its grid2read section):
- **F27. Neither length nor gap decides V1 against the walk; landing predictability
  does** (§3.3, §3.5). A compile-time table cannot see predictability. So the default is
  a ruling (D169), and a regular regime reaches the walk only through a stated fact (R5,
  `SF_E_REGULAR`).
- **F28. A class key that is a MAX suppresses its own losing members** (§7 item 2). R0's
  r2 key took the class's best saving, and three losing shapes hid behind one winner.
  Per-shape keys make the class row redundant, and R0 retires (§1.3a).
- **F29. An `unpaid` fallback must be the next-best form, not a habitual one** (§6, R2
  row). R2's `unpaid` WALK was the worst form below the block. Dropping the row lets the
  interval fall to the terminal.
- **F30. A row keyed on a slope ignores density** (§7 item 3). F2's saving is a
  member-free slope, while the VM hat's g = 2 find-all loses 38%. A slope key can say a
  form is faster per byte, and never that it is faster per landing. `[rev4.1]` Ruled
  (Q-R17P-27): F2 ships without a density condition and the g = 2 loss is named an
  expected one (§9.2a).
- **F31. A one-byte "SIMD-off" row is the host libc's SIMD** (§7 item 5). LIBC's β is the
  ifunc-selected `memchr`, so LIBC rows are the ones where `libc-mismatch` matters most.
- `[rev4.1]` **F32. "Not timed" is not "unknown" when the deciding fact is static and the
  measured trend is monotone in it** (Q-R17P-26). Rev 4 treated an untimed cover shape as
  an open cost and kept it on the walk; the shape is a compile-time fact the kit builds,
  and nine timed shapes order by its term count, so the shape routes by count. The check
  before relaying a lane's "unmeasured" question is whether the deciding fact is known at
  compile time.

`[rev3]` **Unlocks recorded from critic D** (none scheduled; U1 and U3 proposed to main as
plan rows with their triggers):

| id | general form | trigger |
|---|---|---|
| U1 | a form LADDER per layer (WALK < V1 < W64, S1 apart) with per-step keys, generating R0, R1, R2, R5, R7 | the first form beyond {WALK, V1, W64, S1} reaching CANDIDATE, or a Zen 1 set ranking forms differently |
| U2 | the first-match rows as the compiled form of a priced argmin; one evaluator (`costmodel.py --price`) | an R-18 chain build with ≥ 3 links, or E7 showing the estimator's regret ≤ the rows' out of sample |
| U3 | one table library across kit and pcrec (`kit_walk` + gate + trace + reach floors + declared-reads trap, adopted by `cand_rows[]`, `fit_rungs[]`, `entry_rows[]`) | ROWCON H1's own; `entry_rows[]` (E0) as the first pcrec adopter |
| U4 | one runtime-arm family: N-dispatch rows, H rows, reseed adaptive rows, one emission pattern and pay rule | B8/B9, or [ADAPTIVE-ARM]'s build |
| U5 | the decision record (`--emit-facts` `memfn`) for every kit table | the first ask about a non-finder kit form |
| U6 | table-derived artifact size for the size ladder (obscure; note only) | re-emits dominating an oversized compile (K67 class) |

---

## 12. Charter vs committed `[rev2]`

| brief item | where | status |
|---|---|---|
| Read BOILERPLATE, memfn/CLAUDE.md; design against MAIN | §0 preamble, §3 (B0 ports R17-a; MF_SITE_ABI from main's 10) | done |
| Fold R-19, R-20 (R-MS1..5), R-21 (PR-1..11, ST1-ST6, S964-S980) | §3.1 (every PR item placed), §4.2, §4.7, §8.3 | done |
| Fold D161 add. 11-15 (incl. Q-WR-1/2/3/6/9), add. 8/10, D166 + add. 1/1.1/2, [KNOW-SRC], D157, D162, D165 (+ add. 1), D147, D76/D94, D80 | §R2 maps each to its section | done |
| Fold winreq (lists, ids, Q-WR answers), sbscope/pcscope (facts, W1-W4, G-1..G-5, census), regime_eval rev 2.2 (E3/E4, grid2 needs, F2, the suggestion), finder_history, regime_tables rev 0.5, measure_sets rev 2.1, window_contract | §1, §3, §4, §5, §8 | done |
| 1. Scope and rows: set FIND, one-byte stops, presence + handoffs; R0-R8 + the libc row with `libc:` deps, libc-free one-byte forms, MLINE, NONE where safe, the pre-scan row; the Q-WR-1 defaults; each row's needs/condition/pick/unpaid/deny | §1.1, §1.3 (15 FIND rows), §1.4 (6 PRES rows), §5.3 | done (21 rows designed; 18 locked at B4, F0/F1/P1 formal additions at B5) |
| 2. The step plan: ST1-ST6, R-19, R-20, E3/E4 in one order; per step zero-mover status and why, abi event with readers by grep, spec hunks, denies and floor pins, G1/G2/sabotage, dependencies (E-1, D165, [KNOW-SRC]); first delivery zero-mover with the five-pick shadow; movers later, each censused | §3.1-§3.5 | done |
| 3. The contract: presence class, range binding, EMPTY = NOMATCH, the unconstrained reply as a range, the proven-facts channel with the six readers mapped and no per-form read-back, the K65 obligation per consumer, C-items cited | §4.1-§4.8 | done |
| 4. Measurements keyed (quantity, form, site kind), relative, present vs ABSENT, method cards; ONE grid2 slot spec with wall time incl. regime_eval's streamed cells, the optional F2 pass and the paranoid suggestion | §5.1-§5.5 (23 families, 8 ABSENT; ≈ 88 min required, ≈ 96 with optional) | done |
| 5. R17-b″'s seam: iterator rows, A3, H, presence carry, the cut-off (S = 40 B kit row) | §6 | done (S's total raised as Q-R17P-10) |
| 6. Only NEW questions (Q-R17P-9..); rev 1's closed with rulings | §7.1 (eight closed), §7.2 (six new) | done |
| 7. Standing questions answered; this checklist | §10, §12 | done |
| `[rev2]` markers, change log, memfn/CLAUDE.md + r17b_prime/CLAUDE.md, the lane report | §R2; `docs/design/memfn/CLAUDE.md`; `r17b_prime/CLAUDE.md`; `docs/dev/lanes/r17bp3_report.md` | done |
| DESIGN ONLY: no `src/`/`memfn/src/` change, no measured constants in source, no timing | nothing under `src/`, `memfn/`, `tests/`, `lib/` changed | done |

`[rev3]` **Revision 3's brief (lane r17bp4, 2026-10-16):**

| brief item | where | status |
|---|---|---|
| Read BOILERPLATE, memfn/CLAUDE.md, docs/design/CLAUDE.md; scope mandate (worktree only) | — | done |
| (1) the panel record with a by-id completeness table, critic B's (and C's) header count corrected, its index entry | `docs/dev/reviews/2026-10-16-r1-memfn-r17bp.md`, `docs/dev/reviews/CLAUDE.md` | done (70 of 70 ids dispositioned; B 1/9/7, C 6/7) |
| (2) fold every accepted finding per dispositions.md, `[rev3]` markers, §R3 by id | §R3 and throughout | done |
| D167 + addendum 1 (A7 MEMBERS, A10 K5, A11 the landmark input as a fact) | §1.3, §1.4, §3.1, §4.5, §6, §7.1b | done |
| The E-1 agreement (B1 declares `mf_analysis` on `mf_art_begin`, NULL-tolerant, unread before B3a; main fills it after B2, no kit edit) | §0 item 4, §3.1, §4.7, §4.9 | done |
| Sweeparm's `-fmemfn-simd` / `-fcomments` arms (S981/S982) as THE instruments | §0, §3.1, §8.1 | done |
| Re-read §2.1, §6 and B9 against D163 add. 7 / compound_entries rev 2 and D165 + addenda / findall_iter | §2.1, §2.2, §2.4, §6, §3.1 B9 | done |
| A4: the define-time query designed concretely (signature, when called, readers, B-step), as a contract proposal | §4.5, Q-R17P-15 | done (lands in B1; B2 depends on it) |
| grid2 additions (C3 shapes, C5 N = 33..46, C7 launches, C8 NONE arms) as the slot spec | §5.4 | done (≈ 91-129 min required) |
| Keep §12 updated; the first delivery stays B0-B3b zero-mover | §12, §3.1 | done |
| Report with new questions Q-R17P-15.. and a charter checklist | `docs/dev/lanes/r17bp4_report.md` | done |
| DESIGN ONLY: no code, no timing, no `make` beyond a light docs check | nothing under `src/`, `memfn/src`, `tests/`, `lib/` changed | done |

`[rev4]` **Revision 4's brief (lane rev4, 2026-10-20):**

| brief item | where | status |
|---|---|---|
| Read BOILERPLATE and memfn/CLAUDE.md; worktree `worktrees/rev4` from `lane/memfn-b4`; merge `lane/grid2read` alone, both sides kept on conflict | the merge commit (two index files, both sides kept) | done |
| (1) fold grid2's contradictions into B4's table, each row change citing its measurement: R0, R7 incl. W16/W32, R5, R1, R2, R8, D1/D1c, D1w, F0, F1, F2, P1, the pay rule | §R4, §1.3a, §1.4, §2.5, §2.6, §5.2a | done |
| M9 contradicted: R1 dropped, the crossover recorded as an upper bound | §1.3a, §2.6 | done |
| M15 contradicted: predictability, not gap | §1.3a (R5), §1.9, §5.2a | done |
| no dispatch at B4; R2's unpaid not WALK; F0/F1 not built (D77); ~~F2 needs a density condition~~ `[rev4.1]` F2 has no density condition (Q-R17P-27 answered) | §2.5, §1.3a, Q-R17P-27 | done |
| (2) D169 as B4's default, with its exceptions; B4's measurement names its regular-landing cells as EXPECTED losses up front | §1.9, §9.2a | done |
| (3) B4's gates now: D163 add. 8 (met or what remains), E8 PASS, M0; OWED: the re-time and the V1-text attribution | §3.1a | done |
| house shape: rev 4 header, §R4 by row and source, superseded text struck or noted, a first-match row table, plain words, no line-number citations | header, §R4, §1.3 strikes, §1.3a | done |
| CLAUDE.md entries (memfn/CLAUDE.md's r17b_prime line, r17b_prime/CLAUDE.md, the lanes index); finder_history.md logged | those files | done |
| report `docs/dev/lanes/rev4_report.md` with row-by-row changes, open questions with leanings, checklist | that file | done |
| DESIGN ONLY: no build, no make test, no timing | nothing under `src/`, `memfn/src`, `tests/`, `lib/` changed | done |

`[rev4.1]` **Revision 4.1's brief (lane rev41, 2026-10-21):**

| brief item | where | status |
|---|---|---|
| Read BOILERPLATE and memfn/CLAUDE.md; worktree `worktrees/rev41` from `lane/memfn-b4`; docs only (no make, no compile, no timing) | — | done |
| Read the rulings first: `memfn/docs/journal.md` 2026-10-21 and the two 2026-10-21 notices in `memfn/docs/responses.md` | §7.3 (each answer quotes its source) | done |
| (1) Q-R17P-26: a set site's form by its cover's TERM COUNT (V1 at ≤ 2, WALK at ≥ 3); apply everywhere it lands | §R4.1, §0, §1.3 notes, §1.3a rows 12-13 and notes, §1.9, §3.1 (B4 row), §3.1a item 4, §3.5, §8.3 (SN-8, S917), §9.2, §9.2a, §9.3, §9.4, §10, §11 (F25, F32) | done |
| R7 keys on term count; per-shape keys kept as the evidence | §1.3a row 12, §5.2a | done |
| R7w keeps only the 3+ term case ("no key" reason gone) | §1.3a row 13 and notes | done |
| the 54 no-key sites route by term count; their split OWED to the regenerated manifest, not computed | §3.5, §3.1a item 4, §9.2a | done (not computed, as instructed) |
| B4's acceptance confirms the rule on the shapes it moves; a contradicting shape is a finding | §9.2 item 2, §9.4 | done |
| The row table stays a declared first-match table | §1.3a | done |
| (2) Q-R17P-27 YES: F2 defaults to V1 at B5 (not B4), g = 2 cells named expected losses; replace "density condition, still open" wherever it appears | §0 item 2, §1.3a row 1, §1.3 row 3 note, §1.8, §3.1 (B5 row), §3.1a item 6, §7.3, §9.2a, §11 (F30), the §5.2a "F2's cells" row | done |
| (3) Q-R17P-28: P1 recorded as fired on the letter and NOT built; update the P1 rows and B5 item (d) | §0 item 2 and table, §R4 (P1 row), §1.4, §3.1 (B5 item (d)), §3.4 (floors), §5.2a (M23), §8.3 (S978) | done |
| each §7.3 question marked ANSWERED with the answer and its source; question text left in place | §7.3 | done |
| a rev 4.1 header line and a §R4.1 change list near the top (change → section); changed rows marked `[rev4.1]` | the header, §R4.1 | done |
| superseded rev 4 text struck through or replaced with a note, never silently deleted | throughout (`~~...~~` + `[rev4.1]`) | done |
| no line-number citations (cite by section) | whole file | done |
| CLAUDE.md entries: `docs/design/memfn/CLAUDE.md`, `docs/design/memfn/r17b_prime/CLAUDE.md`; the lanes index; `memfn/docs/finder_history.md` | those files | done |
| report `docs/dev/lanes/rev41_report.md` (each edit → section, charter-vs-delivered checklist) | that file | done |
| DESIGN ONLY: nothing under `src/`, `memfn/src/`, `tests/`, `lib/` changed | — | done |
