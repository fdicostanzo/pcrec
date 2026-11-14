# plan_frame — span_pick unit 3.0, "the plan takes the frame" (design, rev 2.2)

**Status: PROPOSED, rev 2.2 (lane u30d4, 2026-11-07) over rev 2.1 (lane u30d3), rev 2 (lane u30d2), rev 1 (lane u30d1)
and rev 0 (lane u30d), all 2026-11-07. Design only: no build go, no code, no make, no timing.** Rev 2.2 applies
re-check review `docs/dev/reviews/2026-11-07-r13-memfn-planframe2.md` (r13) as the kit manager ruled it (its
"## Rulings" section); its text is marked `[rev2.2 Rn]` and replaces any older text it contradicts. **Read §R2.2
first.** `[s1d]` Lane s1design (2026-11-12) re-based §5 3.0b on main 35bee4da9, after K38-2 landed: read §5 3.0b's
re-base block before 3.0b's text (ASK-2 void, ASK-6 new, MF_SITE_ABI 28, 3.0b's sabotage ids renumbered). `[r1s1]` Lane s1fix (2026-11-12) applied re-check review
`docs/dev/reviews/2026-11-12-r1-memfn-s1.md` as the kit manager ruled it (its "Rulings" section: all as proposed): its
text is marked `[r1s1 S1-n]` and replaces any older text it contradicts, `[s1d]` text included. Its cites were read
at main 35bee4da9 (no file 3.0b reads moved between 35bee4da9 and 781275381). `[r2s1]` Lane s1fix2 (2026-11-12)
applied re-check review `docs/dev/reviews/2026-11-12-r2-memfn-s1b.md` as the kit manager ruled it (its "Rulings"
section: FIX-NOW R30B-1..6, R30B-8, R30B-9; PLAN R30B-7, which rewords §7 Q16): its text is marked `[r2s1 R30B-n]` and
replaces any older text it contradicts, `[r1s1]` text included. Its cites were read at main 0f1d54089 (nothing under
`src/`, `memfn/`, `tests/`, the Makefile or `docs/dev/lanes/r33_sim/` moved since 522faf600, the review's tree). `[d27fix]` Lane d27fix (2026-11-13) applied the D27 author's findings on 3.0b's seam contract (F1-F5, A1-A7, `tests/memfn/d27_frame/`) as the kit manager ruled them: its text, in §2.2-§2.3 and §4.1, is marked `[d27fix Fn]`/`[d27fix An]` and replaces any older text it contradicts. Rev 2.1 applies ONE ruling, the kit manager's on rev 2's Q13 (last section of review r12), and is marked `[rev2.1 Q13]`; see R2.1. Rev 2 applies review
`docs/dev/reviews/2026-11-07-r12-memfn-planframe1.md` (r12) as the kit manager ruled it (its "## Rulings"
section). Text changed in rev 2 is marked `[rev2 Fn]` and replaces any `[rev1]` or unmarked text it
contradicts. Rev 1's changes are marked `[rev1]` (§R1). After §R2.2, read §R2, then §0, §2.3 (the reply), §2.5
(the triple) and §5 (the units).
It serves kit request R-35 item 2 (`memfn/docs/requests.md` :805, ruling (a)). It is the design of the
first stage-3 step in `span_pick.md` §Staging (:408). Its shape follows `span_cards.md`. `[rev2]` **Build
tree: main a678d0a4e** (main's HEAD at this lane's start; the same tree review r12 cited). The worktree's
code is byte-identical to it under `memfn/`, `src/` and `tests/memfn/` (`git diff a678d0a4e 2d189b302`
touches only docs and `tests/fuzz/fuzz.py`). Every cite in this note was re-checked there; none moved after
r12, and the corrections below are r12's own (F27, PREM-3) plus the new cites rev 2 adds. `[rev2.2]` Main's HEAD
at rev 2.2's start is still **a678d0a4e**; every cite rev 2.2 adds or touches was re-read there (`git show
a678d0a4e:<file>`), and r13's critics checked about 85 more at the same tree.
`span_pick.md`'s own cites are older (2636dee99); where they have drifted, §10 gives the current line.

## R2.2. What revision 2.2 changed (review r13, as the kit manager ruled it)

Every FIX-NOW of r13 is accepted (R1-R11, R15-R19, R21, R25-R27), every DOC item as proposed (R12-R14, R22-R24,
R28); R20 is NOTED (no text owed; §5 3.0b keeps it as an optional control). The unit split is unchanged. Choices r13
left open are §7 Q14-Q15, each with a recommendation; the text follows the recommendation until the kit manager rules.
`[r1s1 S1-6]` Both are RULED (kit journal, 11-07 ~23:10): Q14 accepted (row AF, 3.0b 19 rows); Q15 accepted except
(3), "left to break", REJECTED (a kit-owned successor probe, §5 3.0b).

| id | section | one line |
|---|---|---|
| R1 | Goal 2, §4.1 (the field map), §5 3.0b (agreement, E2), §9 Q2 | NARROW, as ruled: the FRAME part is compared against the stored record through a per-frame field map; the decision group is re-derived through `decide`, its independent controls the purity harness and ASK-3. No stored decision copy |
| R2 | §0 row 3, §2.3 (`plan_test`, new `stop_test`), §3, §5 3.0b (G2 class, AB), §6, §7 Q14 | a separate `stop_test` member beside `plan_test[]`; TABLE = hook stated AND the covering span offers this set; the define side matched by OFFSET; the G2 marker is the hook's own spelling `g2w_t<id>_<ref>[`; AB's population as ruled |
| R3 | §0 row 4, §2.4 (the renderable set), §2.5.3 (ST-many), §5 (R) | the gate holds on ST-one or ST-many; ST-many then REFUSES by a named refusal row (the `?need` shape); (R) asserts that refusal |
| R4 | §2.4 (one accessor), §5 (D) | the backstop shapes are narrowed to the renderer tables' names plus `ren_find(`; `.pick ==`, `->pick ==`, `].holds(` are not shapes; expected HITS and MEMBER_COUNT stated |
| R5 | §2.6.4 (witnesses), §5 3.0a | the new tables print no REACH in 3.0a (plain first-match arrays, like Table B); REACH equality covers what `reach_print` prints |
| R6 | §3 (package), Goal 3 | `run_purity_reach.sh`'s population gains one pattern per new table; the tables live in `window.c`, which its plant path rebuilds; the script and two harness descriptions listed |
| R7 | §2.5.2, §5 3.0a (content, witnesses) | the support pin's reader (`rows_check.py` §S), columns, kit print (`arm_fixtures --streams`), verbatim RULING cells, basis witnesses at landing time |
| R8 | §4.1, §5 3.0a/3.0b (content, separability), §2.4, §2.3 | `fused`, `plan_test`/`stop_test`, the reply ids, E-func's `search` (the `fn_rows` pick column), the composer arm walk and the allocator move to 3.0b beside their readers |
| R9 | §5 3.0a and 3.0b (content) | the sabotage re-aims named: S686 (moves to 3.0b with the pick column); G2's S1423, S1427, S1428, S1543 kept verbatim or re-aimed |
| R10 | §2.4 (reader table), §8, §7 Q15 | `renderer_rows.tsv` gains a 6th column `fused`; FDROUTE prints `frame=` so §R holds (frame, row, ren) triples (recommended, Q15) |
| R11 | §5 (B), (C), (R) | the host: a `rows_check.py` §R invariant "no witness compile's refusal names a T-FIND row or Table S's refusal", over `renderer_rows.tsv`'s witness lines |
| R12 | §5 (separability) | 3.0a's two commits: commit 1 = §2.5.2-§2.5.3 + §2.6; commit 2 = §2.4; each commit's sabotage rows listed |
| R13 | §2.6.2, §5 (L), (N) | (L)'s reach excludes B-fn sites; §2.6.2 declares two S-restart rows with one text |
| R14 | §2.4 (reader table), §8 | the retired names' other readers listed; Table B's two `_Static_assert`s get successors |
| R15 | §2.6.0 | the skeleton row states its RENDER order apart from its text order (the floor renders the check first) |
| R16 | §2.2, §5 (I) | the deny mechanism is the site's `opts` string; (I) plants Table E's walk with the site's `opts` cleared, plus a T-FIND-deny fixture |
| R17 | Goal 2, §5 (F) | (F) asserts the failure names ASK-3's invariant; Goal 2 states the two checks as a chain |
| R18 | §2.2, §2.3 (contract lines, observable meanings) | `call` out of range, `def` per call, `*out` on -1, the frame fields NONE ignores and the refusals DEFINE/EMIT add; each value's observable meaning moved from §5 into §2.3 |
| R19 | Goal 2, §5 3.0b (witnesses), §7 Q15 | "G2 (OFF layer only)"; the corpus carrier of the kit agreement is `reach_equal.py` with `-fmemfn-simd` among its arms, a boxqueue job (recommended, Q15) |
| R21 | §2.2 (projection), §5 (AD) | the `miss`/`n` relation named; AD's population is STMT/ASSIGN and STMT/ON_MISS sites under EMIT, renamed relation-preservingly, plus one relation-breaking case |
| R22 | §5 (header, size), §R2.1 note | 3.0b has 18 sabotage rows (S2994-S3011), the note 30. `[r1s1 S1-6]` 19 with (AF) (Q14 RULED), renumbered: §5 3.0b's re-base block |
| R23 | §3 | `docs/dev/lanes/r33_sim/probe.c` :94 named (a study left to break; recommended, Q15). `[r1s1 S1-6]` Q15 (3) RULED the other way: a successor probe, §5 3.0b's probe item |
| R24 | §2.3, §2.6.3, §5, Goal 5, §9 | "fact column" singular; "top-level" wording gone; the offset-skip arm's RESTART lives in the fused-rows table's stream column |
| R25 | §2.3 (`search`), §2.5.2, §2.5.5, §7 (RUNG-LIST) | VECTOR and its support row carried to §2.5.5's NOTE and RUNG-LIST; not declared in 3.0 |
| R26 | §5 3.0b (G2 impossible cells) | E-stmt (and E-func) allow RESTART or NONE; NONE iff `fused` ARM |
| R27 | §2.3, §5 3.0b (purity) | the decision-equality comparator is `memcmp(a, b, offsetof(mf_wreply, framed))` |
| R28 | §7 (RUNG-LIST), §6, §R2 F13 note | RUNG-LIST's trigger restated: "row 1 compares a SIMD-on cell, or the first MASK stream RENDERER ROW lands" |

## R2.1. What revision 2.1 changed

| ruling | section changed | what changed |
|---|---|---|
| Q13: F13 is a LABEL, not a rung list (r12, "Ruling on rev 2's Q13") | R2 (F13, F34), §0, §1, §2.1-§2.3, §2.7, §3, §4, §5 (rows W and AE retired), §6, §7 (Q13 ANSWERED, plan row RUNG-LIST), §9 | `nrung`/`rung[]`, `mf_wrung`, `mf_wcheck`, `MF_WRUNG_MAX`, the `fs` argument and the sink counter are gone; F13 keeps its doc text; §2.3 states the gap (under `-fmemfn-simd` the artifact may run vrun's VECTOR/MASK/TRIM while the reply names the OFF triple); the rung list is a PLAN row with its trigger. 3.0b stays L; its sabotage rows are 17 (was 19), the note's rows 29 (was 31) `[rev2.2 R22]` (miscounted: rev 2 never counted E2, so they were 18 and 30) |

## R2. What revision 2 changed, by finding (review r12)

Every id of r12 is answered here. The kit manager ruled every FIX-NOW accepted, DOC and PLAN as proposed,
F8 as the D77 trim with the stream a separately chosen piece, F13 as "the reply names the triple per rung" (`[rev2.1 Q13]` narrowed to a label, R2.1),
F14 as "the fused row's reply crosses its facts", and a D27 spec-first author for 3.0b's seam contract.

| id | ruled | section changed | what changed |
|---|---|---|---|
| F1 | FIX-NOW | §2.4 (reader table, formhash row), §2.6.3 | `wf_plan_brow` keeps returning T-FIND's deciding row (= `method`); the renderer or fused row id is `wf_plan_bren`'s successor, with today's id strings. B-fn is reachable only because the (E-find, PAIR) search row exists: named, with its trigger |
| F2 | FIX-NOW | §2.6.1, §2.6.2, §2.6.4 | a LOOP-STATE slot ("before the loop") on search and stream renderer rows, ordered before RAISE; B-pair's `ofs_pair_decl` is its one 3.0 value |
| F3 | FIX-NOW | §2.6.0 (new), §2.6.4, §5 (N) | per-frame SKELETON rows; the bound and RAISE are the frame's pieces; every composing frame, the floor included, takes NEXT from its stream renderer row, and a missing row refuses; (N) gains its reach control |
| F4 | FIX-NOW | §2.4, §5 (O), Goal 1 | the renderability gate is scoped to slot FIND (`fd_holds`, `r->slot == FD_FIND`); a PRES population joins REACH equality |
| F5 | FIX-NOW | §2.6.4 | the libc and include union is over all three pieces, with each piece's value (B-walk 0; the check's `nrun`); witness `--memfn=no-fd-d1 abcdef`; plant (Q) |
| F6 | FIX-NOW | §2.4 (reader table), Goal 4, §8 | `renderer_rows.tsv`, `rows_check.py` §R and `trace_format.md` FDROUTE listed with a disposition; Goal 4 is "one table plus its named pin" |
| F7 | FIX-NOW | §2.4, §5 (B), (C) | `select_arm`'s routed refusal (`compose.c` :317-325) is KEPT as (B)/(C)'s observation point; (B) names its arm absent; (C) asserts the refusal names PAIR |
| F8 | FIX-NOW (D77 trim), owner ruled | §R2 note, §2.5.2, §2.5.3, §2.5.5 (new), §7 Q8 | the stream IS a separately chosen piece (Frank's "Yes" to the three-piece question). MASK is declared in `mf_wstream`; the S-mask row's code and the unbuilt support rows move to a NOTE carried to the finder unit (§2.5.5) |
| F9 | FIX-NOW | §2.5.3, §2.4 | ONE rule: Table S's input is support(search) INTERSECT the frame's streams; one -> it, none -> not renderable, two or more -> refused until an evidence row. The renderable set is defined by Table S |
| F10 | FIX-NOW | §2.3, §2.6.1, §2.6.3 | the composer's PF arms are COMPOSED (`fused` NO); the fused rows are B-fn and the offset-skip arm only; the other composer arms are arms[]'s exception (`fused` ARM) |
| F11 | FIX-NOW | §2.4, §2.6.1, §2.6.2 | the renderer tables are keyed by T-FRAME's ids (E-find, E-stmt, E-generic); the non-window FIND sites read E-stmt's rows as arms[]'s named exception |
| F12 | FIX-NOW | §2.3 (`plan_test`), §5 (AB), Goal 2 | the check group gains a per-plan-position test kind (`plan_test`: OWN or TABLE, T-VERIFY step 6), in the frame part; a G2 population varies `table_name` stated-ness. `[rev2.2 R2]` Plus `stop_test` for the stop, which C-stop removes from `plan[]` |
| F13 | FIX-NOW, ruled "the reply names the triple per rung"; `[rev2.1 Q13]` ruled a LABEL | §2.3 (the OFF-variant statement and the stated gap), §6 | `search`/`stream`/`fused`/the check describe the OFF (scalar) variant; §6's FIXED columns name layer and target; the gap is stated: under `-fmemfn-simd` the artifact may run vrun's (VECTOR, MASK, TRIM) while the reply names the OFF triple. The rung list (`rung[]`, `fs`, rows W and AE) is plan row RUNG-LIST, trigger "row 1 compares a SIMD-on cell, or the first MASK producer lands" (`[rev2.2 R28]` restated: "... or the first MASK stream RENDERER ROW lands", §7) |
| F14 | FIX-NOW, ruled "cross the facts" | §2.3 (`search`, `fused`), §2.6.3 | `fused` is an enum about the piece boundary, never a C arm name; a fused row crosses its pick through `search` (fn-pair PAIR, fn-memchr LIBC, read through `fn_rows` BODY); `method` stays T-FIND's row |
| F15 | FIX-NOW (doc) | §6 | each comparison's FIXED columns restated; CHECK renamed "RENDERER: fused function vs inline composition", one site under a lever; SEARCH and STOP state what else moves; HORS's limit stated |
| F16 | DOC + PLAN | §2.2 (round-trip projection), §2.8, §5 (AD) | the ask's round-trip projection named; a same-class-different-text fixture; the C classifiers move to the spellings layer; build trigger [IR-FORM] |
| F17 | DOC | §2.8 | a column "what is C-specific in it today" |
| F18 | DOC | §2.4 | "PAIR and HORS are then filtered by one mechanism" withdrawn; the HORS residue named with F5's second-half trigger |
| F19 | PLAN | §2.3 (check note), §2.6.2, §7 Q9 | a PROVES column on the search piece, read by C-stop: trigger Q9's unit or the first search whose proven positions differ from the stop |
| F20 | FIX-NOW | §2.4 (census rows), §8 | span_pick names the stream question (T-STREAM: the support table and Table S); census rows for the check renderer rows and the fused rows (EXC) |
| F21 | FIX-NOW | §2.5.2, §5 (M), (R), Goal 4, §9 | each support pin row labelled with its source; the derived rows get a basis witness read from base's text; Goal 4's claim narrowed |
| F22 | DOC | §4.2 (ASK-1 note), §7 Q12 | ASK-1's `site_kind` UNSTATED narrows R-35 (a); said, with why; main confirms |
| F23 | DOC (main's) | §7 Q10, §8 | the addendum quotes the owner's sentence and his "Yes" to the three-piece question; ruling (2) gets its home |
| F24 | FIX-NOW (XS) | §2.3, §2.5 | `MF_WSTREAM_ONESHOT` renamed `MF_WSTREAM_RESTART` (the owner's "one-shot restart") |
| F25 | FIX-NOW (doc) | §2.4, §3, §4.2, §7 Q11 | reader lists completed (span_cards :865, span_pick :45/:51/:369/:408, window_site :336, trace_format :178-183, kit.h :557-561, memfn.h :1483-1486); the historical MF_SITE_ABI class stated as a class; [SEAM-READER-CENSUS] named for main |
| F26 | FIX-NOW | §2.2 (Purity), §4.1, §5 (AC) | the plan function takes an allocator; the purity harness asserts 0 arena growth across a framed ask |
| F27 | DOC | §1, §2.5.1, §2.5.3, §2.7, §3, §10 | layer at `finder.c` :650; `PURITY_FLOOR` at :132; B-fn has no `next` column and the floor's resume is `wf_floor_expr` :2324; vrun's trim-empty case `if (m) return` |
| F28 | FIX-NOW | §2.4, §5 (D) | one named lookup accessor per renderer table; backstop shapes for the row-walk idiom; (D) planted as a copy of `fd_renderer`'s loop |
| F29 | FIX-NOW | §5 3.0b (agreement), (E2) | the agreement's define-side operand is read from what the define STORED, never via `reply_of` or the plan function; a plant inside the plan function's frame part. `[rev2.2 R1]` Narrowed: the FRAME part only (field map, §4.1); the decision group is re-derived through `decide` |
| F30 | FIX-NOW | Goal 2, §5 3.0b, (X) | G2 tallies (frame_row, stream) cells, floored at measured less ~10%, impossible cells 0, `stream == SHIFT` iff `_sh[256]`; a live MASK plant |
| F31 | FIX-NOW | Goal 2, Goal 5, §5 (Y), (Z), (AA) | G2 classifies each E-find site's text and asserts `fused`, `method`, `search`, `frame_row`; the id check asserts exact emptiness |
| F32 | FIX-NOW | Goal 3, §3, §5 (H) | `pur_diff` is a `memcmp` of the whole `mf_wreply`; the control print a hex dump |
| F33 | FIX-NOW | §5 (S), (T), (U) | three `mf_wcall` fixtures (UNSTATED, NONE, EMIT) and their plants |
| F34 | FIX-NOW | Goal 3, §5 (G), (V) | the counting fixture states all six callbacks, each a counter `[rev2.1 Q13]` (no counting sink: `fs` is gone) |

**Unit split** `[rev2]`: kept (3.0a kit-only, 3.0b the seam plus pcrec's asks). No finding forces a change:
every fix is a column, a rule or a check inside one of the two units. F12's `plan_test`
grows 3.0b (now L; `[rev2.1 Q13]` the rung list is not in it), and F2-F5/F9-F11 grow 3.0a's text, not its scope.

**Readiness** `[rev2]`: r12's coordinator let 3.0a's build start once F1-F5, F10 and F11 are in the text.
They are: F1 §2.4/§2.6.3, F2 §2.6.1-§2.6.4, F3 §2.6.0/§2.6.4, F4 §2.4, F5 §2.6.4, F10 §2.3/§2.6.3, F11
§2.4/§2.6.1-§2.6.2. 3.0a also builds F6, F7, F9, F20, F21 and F28, which are in the text too. F8, F12-F14,
F16 and F29-F34 must be settled before 3.0b freezes MF_SITE_ABI; their text is here, and `[rev2.1 Q13]` §7 Q13 is ANSWERED:
no open kit question remains on them.

## R1. What rev 1 changed, by ruling

The rulings are recorded in the kit's journal, entry "11-07 ~23:00: RULED by Frank", and in its
`responses.md` notice "proposed decision entry", both on lane/memfn-k1107 (067aca4df).

| ruling or brief item | what rev 1 changed | where |
|---|---|---|
| Frank 2026-11-07: "Candidate search and candidate validation are two different primitive pieces that are composed." `[rev2 F8]` His "Yes" answered the explicit three-piece question ("Adopt search, stream, check as composed pieces"), so the TRIPLE is the owner's (r12 Rulings) | 3.0's plan is the triple. SEARCH is T-FIND's method (with Table A's stop). The CANDIDATE STREAM is how the text moves past a candidate the check rejects: `RESTART` `[rev2 F24]`, `MASK` or `SHIFT`. The CHECK is T-VERIFY's plan (Table C). Each is a fact table. The C renderer composes them inline | §0 rows 3, 4a; §2.5 |
| brief 1: shape the reply as the triple | rev 0's `resume` (`mf_wresume` NONE/NEXT/SHIFT) becomes `stream` (`mf_wstream`). `method` stays the search's deciding row. The check is the reply's existing T-VERIFY group (`nplan` .. `run_len`) `[rev2 F12]` plus `plan_test`. A declared table says which streams each search supports | §2.3, §2.5.2 |
| brief 2: split Table B, byte-identical | Table B splits into a SEARCH renderer table, a STREAM renderer table and CHECK renderer rows, `[rev2 F3]` under per-frame skeleton rows. B-fn becomes a FUSED row. The split moves zero bytes | §2.6 |
| brief 3: vrun and vany | vrun's rows are (vector search, MASK, a run compare trimmed by what the mask proved), fused under fn-pair; re-expressed in a later zero-mover unit. `[rev2.1 Q13]` 3.0b's reply does NOT list vrun's triple (the gap, §2.3). vany enters as a search piece only in the unit that routes it (D77) | §2.7 |
| brief 4: keep facts apart from C | the triple's tables are facts; the renderer tables are the C emitter's. Rev 0's reply member `renderer` is REPLACED by `fused`, `[rev2 F14]` an enum about the piece boundary, never a C id | §2.3, §2.8 |
| brief 5 / Frank 2026-11-07: row 1 waits for an inline one-member finder and its measurement card | rev 0's Q6 is answered (yes) and dropped. §6 is restated: row 1 waits | §6, §7 |
| brief 6: cites, asks, units, sabotage, questions | cites re-checked; ASK-3's field list changes; 3.0a gains the split; sabotage K-N; Q7-Q10 | §4.2, §5, §7 |

## 0. The decisions, one line each

| # | question | decision | where |
|---|---|---|---|
| 1 | what pcrec states at phase 1 | the FRAME of the site the reply's NEXT rows define, stated on the ask's site itself (form, op, handoff, empty, use, body, decl_point, site_kind, `pred.fn_ref`), plus that define's hooks and its call kind. Today only the DFA prefilter's ask has NEXT readers; for it the frame is the offset-skip block's (FUNC/RETURN, kind UNSTATED, `[rev2 F22]` a narrowing of R-35 (a), §4.2). The run window's ask states NO frame. `[r1s1 S1-6]` At 35bee4da9 there is no run-window ask (ASK-2 VOID); the `@` table's cover-row ask (ASK-6) states no frame (call NONE, `def` NULL) and its refusal is loud (§4.2; the general form is §7 Q16) | §2.1 |
| 2 | what the call takes `[rev2.1 Q13]` | `mf_wdecide(art, site, def, call, out)`. `def` is the define hooks, read for stated-ness only. `call` is `mf_wcall`: UNSTATED (refused), NONE (decision only), DEFINE (as `mf_define`) or EMIT (as `mf_emit`: DEFINE and USE) | §2.2 |
| 3 | what the reply grows `[rev2 F12-F14, F24]` | appended LAST: `framed`, `frame_row` (T-FRAME's row), `method` (T-FIND's deciding row), `search` (`mf_wsearch`: the SEARCH piece), `stream` (`mf_wstream`: RESTART, MASK or SHIFT), `fused` (`mf_wfused`: NO, FN or ARM), `plan_test[]` (the check's per-position test kind) and `[rev2.2 R2]`
`stop_test` (the stop's test kind). Each new member is an enum or a kit row id, never C text. The decision fields are unchanged and stay frame-independent | §2.3 |
| 4 | the asker fact | RETIRED, replaced by ONE declared SEARCH renderer table keyed by (T-FRAME row, pick) `[rev2 F11]`. A T-FIND row holds only where the asking frame can render its pick, `[rev2 F9]` that is, where Table S answers at least one stream for it, `[rev2 F4]` checked for slot FIND only; `[rev2.2 R3]` where it answers two or more (ST-many), the decision is REFUSED by name, never passed to the next row. `SF_ASKER_PAIR` (bit 15) and `fd_stop.renders_pair` are deleted | §2.4 |
| 4a | the triple | three fact tables: T-FIND (search), the SUPPORT table plus Table S (stream; `[rev2 F9]` one rule: the intersection of the search's support and the frame's streams), and T-VERIFY (check). The renderer tables (search, stream, check, `[rev2 F3]` under per-frame skeletons) are Table B split, and the split moves zero bytes | §2.5, §2.6 |
| 5 | the numbers | one MF_SITE_ABI event (the next number at landing; 25 at this tree). MF_CLASS_V does NOT move | §3 |
| 6 | the split | the kit owns the fact tables, the renderer tables, the plan function and the seam. pcrec owns five asks (§4.2), all facts and checks | §4 |
| 7 | units | TWO, `[rev2]` kept. **3.0a** is kit-only, with no seam move, `[rev2.2 R8]` and builds only what the define renders. **3.0b** is the seam plus pcrec's asks, in ONE commit: the MF_SITE_ABI event, with the frame-part outputs only the reply reads. A D27 spec-first author writes 3.0b's seam-contract tests at its build `[rev2]` | §5 |
| 8 | left to row 1 | every priced row and every frame-DEPENDENT decision. RULED (Frank 2026-11-07): row 1 WAITS for the inline one-member finder and its card. `[rev2 F15]` Row 1's comparisons state every fixed piece, layer and target included | §6 |

## 1. Goals

Ranked; a higher goal wins a conflict (`docs/dev/guide/architecture.md`).

| # | goal (who benefits) | measurable form |
|---|---|---|
| 1 | **No emitted byte moves** (every user; `span_pick.md` Goal 2's stage-3 cell for a unit change, D186) | `scripts/emit_sweep.py` byte-identical against each unit's NAMED base commit on EVERY arm: default, each `--memfn=no-X` deny, `--engine=vm`, both SIMD layers. Stamps are included. The input is the corpus plus `span_pick.md` §Staging's three `--patterns-file` inputs. `*_movers.txt` unchanged. No pcrec abi number moves. **No card's form hash moves**: `arm_fixtures --hash` prints the same hash for every form id at base and HEAD, and `finder_check.py` check C's stale count over zen4-grid3@1's recorded `kit:form.<id>=<hash>` deps stays 0 (§9 Q3). This covers Table B's split (§2.6). `[rev2 F4]` REACH equality covers slot PRES's rows too |
| 2 | **The reply is the define's** (row 1's lane; pcrec's NEXT readers) | for every FRAMED ask, every reply field equals what the define of the same site, hooks and call selected. `[rev2.2 R1]` The FRAME part is held to what the define STORED (never recomputed through the plan function), by §4.1's per-frame field map; the decision group is held by re-deriving it through `decide` at the define, and its independent controls are the purity harness and ASK-3. `[rev2.2 R17]` Two trace-build checks form a CHAIN: the kit's at every window-site define (§5, 3.0b: re-ask == stored record and re-derived decision) and pcrec's at the offset-skip define (ASK-3: pcrec's phase-1 ask == the define's re-ask, both through the plan function, so ASK-3 holds pcrec's INPUT, not the record). `[rev2.2 R19]` The kit's check runs on the corpus (its carrier is `reach_equal.py`, both layers, §5 3.0b) and on G2's framed asks in every frame G2 renders, at the OFF layer only (G2 has no SIMD window population). `[rev2 F30, F31]` G2 tallies (frame_row, stream) CELLS, each produced cell floored at its measured count less ~10%, impossible cells asserted 0; it classifies each E-find site's TEXT and holds `fused`, `method`, `search` and `stream` to it (`_sh[256]` iff SHIFT, an `_ofsskip` call iff FN); `[rev2 F12]` `[rev2.2 R2]` a population varying `table_name` stated-ness holds `plan_test` and `stop_test` to the text by the hook's own spelling (`g2w_t<id>_<ref>[`, matched by offset, §2.3) |
| 3 | **The plan face stays pure and writes nothing** (the next editor; D186 add. 2; memory `pcrec-plan-as-text-seam`) | 1d's purity harness, extended to framed asks interleaved with defines, `[rev2 F32]` compares the WHOLE reply (`memcmp`; `reply_of` zeroes it). Table E, B and S rows join `purity_rows.tsv`'s reach table `[rev2.2 R6]` (its population grows by one pattern per table, §3). A COUNTING HOOK `[rev2 F34]` whose fixture STATES all six callbacks (`fn_name`, `table_name`, `member`, `note`, `note_tag`, `on_cand`), each a counter, asserts a framed ask makes **0** calls. `[rev2 F26]` The fixture's arena counts its allocations and a framed ask adds 0; `[r1s1 S1-5]` its population includes
one framed ask whose T-FIND picks PAIR and one REFUSED framed ask, each counted (§2.2's allocation readers). `[r1s1 S1-7]`
"A function of the facts" includes the art's test-only lever set: `mf_lever` is the plan face's second art-state writer
beside `mf_define` (§2.2 Purity). `[rev2 F16]` A same-class-different-text fixture: each hook text replaced by another of the same class (`gate.c`'s classes) leaves the reply unchanged |
| 4 | **One mechanism for "this frame renders this piece"** (the next editor; memory `pcrec-general-mechanisms-not-special-cases`) | `decider_census.tsv` names ONE search renderer table, ONE stream renderer table, ONE support table and Table S, and `[rev2 F6]` no other list answers those questions except their NAMED PIN, `tests/memfn/renderer_rows.tsv`. `[rev2 F28]` Every renderer lookup goes through its table's one named accessor, and the census backstop knows `[rev2.2 R4]` the renderer tables' names and the accessor's spelling (§2.4). A backstop grep finds no `renders_pair` or `SF_ASKER_PAIR` in `memfn/`, `src/` or `tests/`, outside history. The renderability check has a WITNESS (§5 row C). `[rev2 F21]` The support table's LIBC and LIBC_BACK rows equal the ruling's text; its other rows equal their stated basis, held by base's text (§5 rows M, R) |
| 5 | **What 3.0 adds is facts, not C** (Frank 2026-11-07: "we will eventually output code as either C or Rust") | every member 3.0 adds to `memfn.h` is an enum or a row-id string drawn from a kit table, never text an emitter pastes, `[rev2 F14]` and never a C arm or renderer id. A check asserts each id resolves: `method` in `mf_finder_rows`, `frame_row` in Table E's ids, and every enum in its range. `[rev2 F31]` It asserts emptiness EXACTLY: `method == ""` iff no T-FIND row decided; `search == NONE` iff the frame has no search or is ARM; `[rev2.2 R24]` MASK appears in no reply in 3.0 `[rev2.1 Q13]` (vrun's rungs are unreported): G2 asserts a MASK count of 0. `[rev2.2 R25]` `mf_wsearch` declares no VECTOR in 3.0 (§2.5.5) |

**Non-goals.** Any priced row, and any decision change: KEY, M and TIE stay frame-independent. A consumer
kind on OFS sites (its own trigger). Presence joining the call. A frame for pre-check parts (§7 Q1).
Target and layer as plan INPUTS: they are art facts (target seam K0-U3), and T-FIND stays the OFF variant's
(`finder.c` :650 `[rev2 F27]`, §1.5 rule 1). `[rev2.1 Q13]` The reply does not report the SIMD rungs the define will
render (the gap, §2.3), and does not choose them. Serializing the hook callbacks ([IR-FORM]). The composer stating an
`fd_stop` (F5's second half, §2.4). Any MASK producer, vrun's re-expression, and routing vany (§2.7).
Re-expressing the composer's fused arms as compositions (§2.6). `[rev2 F19]` A PROVES column on the search
piece (§7 Q9).

## 2. What crosses the seam

### 2.1 What pcrec states at phase 1, per NEXT row's frame

Unchanged from rev 0 `[rev2.1 Q13]`. Today two pcrec callers make the phase-1 ask (`grep -rn
mf_wdecide src`: `emit_dfa.c` :1068, :7610). No other window scenario makes a phase-1 ask: not the PF find,
the VM hat's seek, MLINE, LMHIT or the cover/REPORT site. For those the define, and `mf_ask` before it, IS
the plan call, and it already carries the frame, the hooks and the phase set (`find_site`, `emit_dfa.c`
:6922-6936; `pcrec_cover_site`, `known.c` :488-496; `cand_ask`, `emit_dfa.c` :8352). pcrec states nothing new
for them.
`[r1s1 S1-6]` **At 35bee4da9 this paragraph is out of date.** The two callers are `window_reply_ask` (`emit_dfa.c`
:7614, ASK-1) and `req_run_at` (:16077, ASK-6), and ASK-6 IS a phase-1 ask on the cover/REPORT site: K38-2 added
it to read the `@` table's cover row (`has_stop`/`stop`). It states no frame (call NONE, `def` NULL), although
pcrec itself defines that site (`emit_cover`); §4.2 makes its refusal loud and §7 Q16 holds the general form. Every
line number in §2.1-§2.3 is a678d0a4e's; their 35bee4da9 values are the "§2.1-§2.3" rows of §5 3.0b's re-base table.

| phase-1 ask | NEXT rows that read its reply | the site those rows define | what pcrec states at phase 1 (3.0b) |
|---|---|---|---|
| the DFA prefilter, `window_reply_ask` (`emit_dfa.c` :7604-7616, asked at :4792) | `run-pinned-bounded`, `run-pinned`, `offset-set-bounded`, `offset-set` (:10471-10500), by the key map `next_keys` (:7298-7306, :7317-7321); also `ofs_test_of` (:7402-7412) and `dfa_form_derive`'s RE-SEED refusal (:13002) | the offset-skip block, `ofs_site_define` (:7622-7642) | **form** FUNC, **op** FIND, **handoff** RETURN, **empty** MISS, **use** POSITION, **body** ONESHOT, **site_kind** UNSTATED (0: OFS sites state no kind, `span_pick.md` :131's named exception; `[rev2 F22]` §4.2), **decl_point** 0, **on_miss_leaves** 0, **pred.fn_ref** 1; the window statement `ofs_window_of` with floor SUBJECT (unchanged); **def** = {`fn_name` stated, `table_name` stated, `miss` MF_MISS_N, `comment_tier` NONESSENTIAL}; **call** DEFINE. These are exactly the values the block's define states |
| the same ask | the rows below the offset rows (`handoff-reentry`, `first-*`, `memchr*`, `byte-class*`), reached where no key holds | each defines its OWN PF site (`pf_site_of`, :7131-7146) | nothing: these rows read no reply field. Their define is their plan call. §7 Q2 |
| `[s1d]` VOID at 35bee4da9 (ASK-2; its successor in pcrec's caller list is `req_run_at`, ASK-6, §4.2). Was: the run window, `req_run_member` (`emit_dfa.c` :1058-1076) | none: the reply's reader is the run member | the pre-check's FUNC part, whose frame the KIT derives (`wf_part_site`, `window.c` :1984-2007, inside `wf_parts_prepare` :2031) | **call** NONE (decision only); `def` NULL |

(The `body` value ONESHOT above is `mf_site.body`, the site's call shape (`memfn.h` :413). `[rev2 F24]` The
candidate stream's value is `MF_WSTREAM_RESTART`, so the two vocabularies no longer share a spelling.)

**Why only the offset rows' frame.** The decision is frame-independent through 3.0. So any frame gives the
same decision, and the frame part is the one new answer. Only the offset rows render the asked statement.
"Per NEXT row" therefore means one framed ask for the four offset rows, which share one frame. The hooks'
`u` pointer may differ from the define's: the plan face never calls a hook callback
(Goal 3), so neither is dereferenced at phase 1.

### 2.2 What the call takes `[rev2 F16, F26]` `[rev2.1 Q13]`

```
typedef enum { MF_WCALL_UNSTATED = 0, MF_WCALL_NONE, MF_WCALL_DEFINE, MF_WCALL_EMIT } mf_wcall;
int mf_wdecide(const mf_art *, const mf_site *site, const mf_hooks *def, uint8_t call,
               mf_wreply *out);
```

- **UNSTATED** is refused (-1). There is no presumed value (memory `pcrec-no-silent-defaults`).
- **NONE**: the decision only, as today. The site's frame fields, and `def` are not read (`wf_check(site,
  0)`, as `window.c` :1226 does now). The reply's frame part is zero: `framed` 0, empty ids, every enum NONE.
- **DEFINE / EMIT**: the frame is the site's own fields, and `wf_check(site, 1)` applies. Table E's walk runs
  under the gate phases the define would read: DEFINE, or DEFINE|USE for EMIT, as `mf_emit` does
  (`compose.c` :255-258, :1320-1325). `def` is the define hooks, or for EMIT the one-call hooks. The call returns -1
  exactly where that define would refuse: `mf_ask`'s rule 1 (`compose.c` :1002-1042). The art's denies and
  `--memfn=` options apply, as at the define. `[rev2.2 R16]` The mechanism is the SITE's `opts` string: Table E's walk
  passes denies 0 (`kit_walk(&wf_etable, 0, ...)`, `window.c` :1917; `wf_etable`'s deny is NULL), and `walk_row`
  reads a row's option through `kit_opt_denied(in->s->opts, t->opt(i))` (`compose.c` :170-171), so `no-window-search`
  (E-find's option) and T-FIND's `fd-*` options reach the walks only through the site's `opts`.
- The phase set crosses as a fact about the CALL, not as the kit's internal `MF_PH_*` bits (`grep MF_PH_
  memfn/include/memfn.h`: none).
- **Contract lines** `[rev2.2 R18]` (what a D27 author tests from this section alone):
  1. `call` above `MF_WCALL_EMIT` (4..255; the parameter is a bare `uint8_t`) is refused (-1), as UNSTATED is.
  2. `def` under DEFINE/EMIT is read exactly as the define reads its hooks: NULL is the define's NULL (every hook
     unstated), and the call answers -1 exactly where `mf_define`/`mf_emit` with that `def` would refuse. Under
     NONE `def` is not read and may hold any value (`[r1s1 S1-6]` pcrec's ASK-6 passes NULL; ASK-2 is VOID).
     `[d27fix A1]` "Would refuse" means a refusal the call's own inputs decide: one caused by a SINK capability
     (the `mf_sink` the define or emit writes to, which the ask does not take) is excluded, and the ask assumes a
     full sink. `[d27fix F2, F3]` Under EMIT it includes `mf_emit`'s USE half: a `decl_point` 1 site (`mf_emit`
     places no `mf_locals` between its define and its use, so it always refuses one), and the refusals a row's
     use makes at its own text, beyond the gate's re-check the walk already applies under DEFINE|USE: today one,
     a NOP ASSIGN site whose hooks state `result_decl` ("a NOP ASSIGN cannot declare its result"), on the rows
     whose statement frame refuses it (E-find, the floor, the `generic` row).
  3. `*out` is zeroed WHOLE (padding included) before anything else, on every return, -1 included (today's first
     statement of `mf_wdecide`, `window.c` :1224, `[r1s1 S1-6]` :1281 at 35bee4da9). A reply is therefore comparable by `memcmp`, which ASK-3 and
     the agreement rely on.
  4. The FRAME FIELDS are the site's `op`, `reverse`, `form`, `handoff`, `empty`, `use`, `body`, `site_kind`,
     `decl_point`, `on_miss_leaves`, `pred.fn_ref` and `opts` (§2.1's values plus the two the frame half of
     `wf_check` and the walks read). NONE reads none of them: two NONE asks differing only in frame fields (and
     `def`) answer byte-equal replies. DEFINE/EMIT add these refusals (the frame half of `wf_check`): a site that is
     not a forward FIND (`op`, `reverse`); a frame other than FUNC/RETURN, STMT/ASSIGN or STMT/ON_MISS (the three
     Table E renders); `empty`, `use`, `body` (ONESHOT only), `site_kind`, `decl_point` or `on_miss_leaves` out of
     its range (`decl_point` 0 or 1; under EMIT 0 only, line 2 `[d27fix F3]`), or `on_miss_leaves` on a non-STMT site; and every refusal of the define's own walk (`mf_ask`'s rule
     1). The observable meaning of each reply value is §2.3's last column.
- **Purity** (D186 add. 2): the reply is a function of the site's facts (window and frame), the hooks'
  stated-ness and text classes, the call, the art's denies/options (`[d27fix A5]` not its layer: the reply describes
  the OFF variant, §2.3's stated gap; the D27 author measured 0 differences over 13.3k layer pairs), `[r1s1 S1-7]` the art's test-only lever
  set (`art->levers`, a member apart from the options, written by `mf_lever`, R-30: the plan face's SECOND art-state
  writer beside `mf_define`; at 35bee4da9 `decide` reads it at `window.c` :664, `a_mass_choose`, which moves the in-run
  STOP, the field ASK-6 reads, and at :938, `run_member`; the plan function's Table E walk and the define read it at
  :1563, `translate`, reached through `e_legacy_holds`, :1623; G2's k3_inrun window sites already state it,
  `g2_win_gen.c` :895-898, :939, :1130), the
  measure set and the handed rates. It sets no art state, defines no handle and writes no text or trace
  record. `[r2s1 R30B-8]` **One fenced exception, a defect path:** a FRAMED ask (DEFINE/EMIT) walks Table E, whose
  E-func and E-stmt rows reach `translate` through `e_legacy_holds` (`window.c` :1623), and `translate`'s two
  internal-invariant failures (:1566, the run ranking lost a position; :1576, the ranking's first position is not
  the run member) call `kit_fail`, which writes the art's sticky `err` (`compose.c` :77-86). Such a plan call
  POISONS THE ART, as the define on the same facts would. It is FENCED as breaker (a) is (pcrec fails the compile on
  any refusal, so no later reply from that art reaches an artifact; the purity header, `arm_fixtures.c` :2096-2099,
  asserts the fence, not purity). `[d27fix F1, A3]` Such an ask answers -1, never 0 with the art's error set (its
  last step turns a set error into a refusal; `memfn.h`'s -1 causes list the poisoned art). The one green reach the
  D27 author found (a verify-NO run under the lever `run-tie-left`: the member keeps the stretch row's tie, the
  ranking took the art's) is closed: a PINNED run's ranking takes its member's tie (`member_opts`, `window.c`), so
  the lever moves the ranking exactly where it moves the member, K38-1's RQ-2 ruling. A NONE ask (`decide` only) never reaches `translate`. So the contract's "-1
  exactly where that define would refuse" holds, and the art-state writers a D27 author may assume are `mf_define`,
  `mf_lever` and this fenced defect path; no green input reaches the last. Reach stays counted on the define (`span_pick.md` breaker (c)). Nothing is cached: the define
  recomputes the plan. `[rev2 F26]` **Allocation**: today `mf_wdecide` keeps its `wf_dec` on the C heap
  "because the ask is pure" (`window.c` :1229-1232), while the code that computes the frame part allocates
  from the art's arena (`wf_prepare` :1900-1906, `wf_find_decide` :1846, `build_runs` :1673-1683). So the
  shared plan function (§4.1) TAKES ITS ALLOCATOR: the define passes the art's arena, and `mf_wdecide` a heap
  allocator whose blocks it frees before it returns. The purity harness checks it (Goal 3: 0 arena growth).
  `[rev2.2 R8]` The parameter lands in 3.0b with its reader (`mf_wdecide`'s frame part) and row (AC); 3.0a's plan
  function keeps the arena the define already uses. `[r1s1 S1-5]` **Its readers at 35bee4da9** (each allocates from
  `art->a` DIRECTLY today, so the parameter replaces `art->a` at each): inside the plan function `wf_plan_site`,
  `wf_find_decide` (`window.c` :2245-2248, `fx->fn` on every PAIR pick, quiet or not) and `why_room` (:2303-2308, on
  every refusal); on the define side, `build_runs` (:1742-1754, through `wf_find_prepare`, under `build`).
  `wf_prepare`'s own allocations (:2411-2417) stay the art's arena. Goal 3's counting arena reaches the first two
  through its PAIR-picking and refused framed asks (§5 row AC).
- **The round-trip projection** `[rev2 F16]` (memory `pcrec-plan-as-text-seam`). What the plan reads of the
  ask, and so what a text form of it must carry, is: the site's facts; the art's facts (denies, `--memfn=`
  options, layer, measure set, rates); per hook, whether it is stated and the CLASS of its text (`gate.c`'s
  classifiers: identifier, the literal `0`, the miss token, the `&&`/postfix/statement shapes, :86-297 and
  :618-653), with `miss` as a TOKEN (today `MF_MISS_N` is compared by address, `gate.c` :648-653, which no
  text form keeps); `[rev2.2 R21]` and one CROSS-HOOK relation: `miss`'s class is MISS_N when `miss` is the N
  token OR its text equals `n`'s (`cl_miss`, `gate.c` :651-656), so a text form carries "miss is the N token, or
  equals `n`" as a fact, not two independent classes; and the call. Goal 3's counting hook proves no
  callback is called; the same-class-different-text fixture (§5 row AD) proves no gate reads text beyond its
  class. No serializer is built (D77); its trigger is [IR-FORM]'s kit planner/emitter member.

### 2.3 What the reply grows `[rev2 F10, F12, F14, F24]` `[rev2.1 Q13]`

Appended LAST to `mf_wreply` (`memfn.h` :1467-1482), because initializers are positional:

| member | type | value on a framed ask |
|---|---|---|
| `framed` | `uint8_t` | 1 (0 on NONE) |
| `frame_row` | `char[12]` | T-FRAME's row: `E-func`, `E-stmt`, `E-find` or `E-generic` (`window.c` :1616-1621) |
| `method` | `char[8]` (= `mf_result.row`'s width) | T-FIND's DECIDING row id (`D-hors`, `D1`, `D1c`, `D1w`, `PAIR`, `R7w`): on E-find the window walk's row (`wf_find_decide`'s `brow`, the value `wf_plan_brow` returns), on E-stmt the composer's routed row (`mf_result.row`, `compose.c` :1316). `""` where no T-FIND row decides: E-generic; E-func, where `fn_rows` BODY decides (OFS is FUNC, outside `fd_scope`'s STMT-only scope, `finder.c` :586-592); a composer walk that reaches a PF arm with no deciding row; an ARM frame |
| `search` `[rev2 F14]` | `uint8_t`, `mf_wsearch` {`NONE` = 0, `LIBC`, `LIBC_BACK`, `WALK`, `PAIR`, `HORS`} `[rev2.2 R25]` (no VECTOR: §2.5.5) | **the SEARCH piece**: the pick that renders the find. Where T-FIND decides, its pick. On a FUSED row, the pick the row declares it implements: B-fn PAIR; E-func's offset-skip function PAIR for `fn-pair` and LIBC for `fn-memchr`, read through `fn_rows` BODY's quiet walk (`ofs_fn_serves`, `ofsskip.c` :482-493). On a PF arm the composer's walk reached with no deciding row, the pick of the search renderer row naming that arm. NONE on E-generic (no search) and on ARM. `[rev2.2 R25]` vrun's vector block search has no value in 3.0 (it is unreported: the gap below; RUNG-LIST declares it) |
| `stream` | `uint8_t`, `mf_wstream` {`MF_WSTREAM_NONE` = 0, `MF_WSTREAM_RESTART` `[rev2 F24]`, `MF_WSTREAM_MASK`, `MF_WSTREAM_SHIFT`} | **the CANDIDATE STREAM**: Table S's answer for (search, frame) (§2.5.3), or a fused row's declared stream. In 3.0 it is `[rev2.2 R24]` SHIFT iff `search` is HORS, RESTART where a search or the floor renders, NONE on an unframed ask and on ARM. MASK is declared and occurs in no reply in 3.0 |
| `fused` `[rev2 F14]` | `uint8_t`, `mf_wfused` {`NONE` = 0, `NO`, `FN`, `ARM`} | **how the pieces are joined**, a fact about the piece boundary, never a C id: NO where the frame composes the triple (E-find's composed rows, E-generic, `[rev2 F10]` E-stmt's PF arms); FN where one function renders search, stream and check (B-fn, and E-func's offset-skip arm); ARM where a composer arm the triple does not yet describe renders the site (the pre-check composites, `runcmp`, `mismatch_inplace` `[d27fix A6]`, `generic`: arms[]'s named exception, with `search` and `stream` NONE). The C arm and renderer ids stay in MFTRACE (FDROUTE `ren=`, `mf_result.form_id`), which belong to the emitter |
| `plan_test` `[rev2 F12]` | `uint8_t[MF_WPLAN_MAX]`, `mf_wtest` {`NONE` = 0, `OWN`, `TABLE`}, aligned with `plan[]` | the CHECK's per-position test kind, T-VERIFY step 6 (`wf_crows` C-table/C-own, `window.c` :1087-1089). `[rev2.2 R2]` **TABLE iff the define hooks state `table_name` AND the alternative's span covering `plan[i]` offers a table whose set is the set tested there** (`offer_at`, `window.c` :1281-1290, read at :1314: `w->table[i] = def && def->table_name ? offer_at(...) : 0`) **AND the text tests the position alone** `[d27fix F4]`; OWN otherwise (a stated hook with no offer is OWN). A position E-find tests inside a RUN COMPARE (C-run's compare, `grp`: two or more adjacent plan positions sharing one `plan_term`, every one core, each set one byte or a one-bit two-byte cube) answers OWN: one compare of the stretch's bytes reads no table, and the reply follows the text (the kit manager's F4 ruling). A shared `plan_term` alone is not such a compare (a position failing C-run's conditions is tested alone), and the floor (E-generic) tests every position alone. The define's own list is indexed over its tested positions (`off[]`: the plan PLUS the stop when C-stop removed it, sorted, `window.c` :1300-1306), not over `plan[]`, so the define side is matched by OFFSET: `plan_test[i]` is the define's entry whose `off` equals `plan[i]`. Answered where the family renders T-VERIFY's plan (E-find's composed rows, E-generic); NONE past `nplan`, on fused, E-stmt and ARM frames (their set test is the fused function's or the caller's: the residue, §2.6.3) |
| `stop_test` `[rev2.2 R2]` | `uint8_t`, `mf_wtest` | the STOP's test kind. C-stop removes the stop's offset from `plan[]` (`wf_crows` step 4, `window.c` :1082; `c_stop`'s `plan_drop`, :999-1002, except inside a pinned stretch), but the define still decides how the stop is tested: B-walk's find tests it through `wf_member(rc, b, stop_ix)` (:2553 -> `wf_member_of`, :2159-2166, which reads `w->table[stop_ix]`; `[r2s1 R30B-9]` at 0f1d54089: `wf_crows` table :1112, `c_stop` :1054-1056, B-walk's stop test :3124, `wf_member_of` :2709). `[r2s1 R30B-9]` B-walk's FIND is the one search whose find member-tests the stop; where the stop's offset STAYS in `plan[]` (the pinned-stretch exception above), the text can also read the stop's marker through the candidate test (`wf_test_to`, :2797, which member-tests every plan position through `wf_pos_test`) or through B-hors's probe (`d_hors_head`, :3217, when `hl` is the stop's offset). Those reads change nothing below: the rule is by OFFSET, so TABLE there is still the offer at the stop. TABLE iff the hook is stated AND the span covering the stop's offset offers the stop's set (C-table's rule, matched by the stop's OFFSET; `[d27fix F4]` not `plan_test`'s run-compare clause: the find tests the stop, whatever compare its offset also sits in); OWN otherwise. Answered on E-find's composed rows wherever the window has a stop; NONE where it has none (`stop_ix` -1), on E-generic (the floor) whether or not its window has a stop `[d27fix A2]`, and on fused, E-stmt and ARM frames. What it reports on searches that test the stop by its bytes (B-pair, B-memchr) or probe another position (B-hors) is §7 Q14 |

**The observable meaning of each value** `[rev2.2 R18]` (moved here from §5's G2 text classes, so a D27 author
holds the reply to the define's OUTPUT, never to the kit's code). "The text" is the define's artifact text for that
site; "the result" is `mf_defined`'s `mf_result`.

| member | value | what the define's output shows |
|---|---|---|
| `framed` | 1 / 0 | 1 iff `call` is DEFINE or EMIT and the call returned 0 |
| `frame_row` | E-find / E-generic | the result's `form_id` is `window-search` / `wf-floor` |
| `frame_row` | E-func / E-stmt | the site states FUNC/RETURN / STMT (ASSIGN or ON_MISS), and the result's `form_id` is a composer arm's |
| `fused` | FN | on E-find (B-fn), the text calls the site's offset-skip function (`<prefix>_mf<handle>_ofsskip`); on E-func, the text defines and calls the FUNC site's own function, `<fn_name>` and its body `<fn_name>__body` (`fn_name`'s text for the site's `fn_ref`) `[d27fix F5]` |
| `fused` | ARM | the result's `form_id` is a composer arm other than a PF arm and the offset-skip arm (a pre-check composite, `runcmp`, `mismatch_inplace` `[d27fix A6]`, `generic`) |
| `fused` | NO | otherwise, on a framed ask |
| `search` | PAIR / HORS / LIBC or LIBC_BACK / WALK / NONE | the find's text holds the two `memchr` frontiers / the 256-byte shift table `_sh[256]` / one `memchr` (LIBC and LIBC_BACK told apart by `method`, D1 vs D1c) / a byte walk / none of them |
| `stream` | SHIFT / RESTART / NONE | the text advances by `_sh[...]` / by one position (`C++`), or the caller's loop restarts (E-stmt) / no search loop (ARM, unframed) |
| `method` | a row id | it resolves in `mf_finder_rows`, and on a composed E-find row that row's pick is `search`; the kit trace's FDROUTE `row=` prints it (`trace_format.md`) |
| `plan_test[i]`, `stop_test` | TABLE / OWN | the text reads the offered table through the hook's own spelling (`table_name`'s text for that offset's ref, then `[`) / tests that offset against the kit's own set, or inside a run compare, which reads no table `[d27fix F4]`; except the one position the HORS skip verifies (D-hors's probe offset: the text drops it from the candidate test and its probe reads that offset's offer, `[d27fix A4]` §2.3's residue), Q14's byte-tested stops, and a stop's offset inside a pinned run compare, whose `plan_test` is the compare's OWN while a find that member-tests the stop reads its offer for `stop_test`. `[d27fix A7]` `stop_test`'s text is checked only on WALK searches (B-walk member-tests the stop); on the others it is held by its rule column (Q14) |

**Who decides each value in 3.0** `[rev2 F10, F14]` `[rev2.1 Q13]` (the define stores the same: `[rev2.2 R1]` §4.1's field map):

| frame | rendered by | `method` | `search` | `stream` | `fused`  |
|---|---|---|---|---|--- |
| E-find | B-pair, B-memchr, B-walk, B-hors | T-FIND's row | its pick | Table S: RESTART, or SHIFT for HORS | NO  |
| E-find | B-fn | `PAIR` | PAIR | RESTART | FN  |
| E-generic | the floor | `""` | NONE | RESTART | NO  |
| E-func | the offset-skip arm | `""` | PAIR (`fn-pair`) or LIBC (`fn-memchr`) | RESTART | FN  |
| E-stmt | a PF arm | T-FIND's row, or `""` | its pick | RESTART (S-caller) | NO  |
| E-func, E-stmt | any other composer arm | `""` | NONE | NONE | ARM  |

**The stated gap** `[rev2.1 Q13]` (kit manager's ruling, r12 "Ruling on rev 2's Q13"). `search`, `stream`, the check and `fused` describe the OFF (scalar) variant of the site: the text the artifact has without `-fmemfn-simd`. Under `-fmemfn-simd` the artifact may run vrun's (VECTOR, MASK, TRIM) while the reply names the OFF triple (for `foo[Xx]bar`: PAIR, RESTART, the plan). The reply does not say which, and the ask carries no sink fact to tell. §6's FIXED columns name the layer and the target, so a record is read at its layer. The list of rungs is plan row RUNG-LIST (§7), with its trigger.

**The check's members.** The CHECK is T-VERIFY's plan (Table C, `window.c` :1051-1092; `c_plan` :1096). The
reply carries it in its decision group (`nplan`, `plan[]`, `plan_term[]`, `pinned`, `run_stated`,
`run_member`, `run_lo`, `run_len`) `[rev2 F12]` and, in the frame part, `plan_test[]` `[rev2.2 R2]` and `stop_test`. `memfn.h`'s comment
names those members "the check", so a serialized reply reads as (`search`, `stream`, check). The
decision group is frame-independent; `plan_test` and `stop_test` read the define hooks, so they are frame-part members.
`[rev2 F19]` **Known residue**: on a D-hors site the search head drops the probed position from the test at
TEXT time (`d_hors_head`'s `skip`, `window.c` :2655), while `plan[]` still lists it, so the reply's check is
the plan before the search's proof. The PROVES column (§7 Q9) is its fix.

**Rev 0's `renderer` is replaced.** On a composed frame, (`frame_row`, `search`, `stream`, check) determine
the renderer rows through the renderer tables (§2.6), keyed by the reply's own ids `[rev2 F11]`. On a fused
frame, `fused` FN says one function renders the triple, and `search` names its pick. B-fn and B-pair are told
apart (`fused` FN vs NO), as rev 0 required (§6).

`path` is unchanged. The decision fields (`alt` .. `path`) are frame-independent in 3.0, and the purity
harness asserts it: a NONE ask and a framed ask of one site answer equal decision fields. `[rev2.2 R27]` Its
comparator is `memcmp(a, b, offsetof(mf_wreply, framed))`, the decision-group prefix: valid because the frame part
is appended LAST and every reply is zeroed whole first (contract line 3, §2.2). The whole-reply `memcmp` (F32)
stays for same-call compares; a NONE and a framed reply differ in the frame part by construction.

**Who reads the new fields (D77).** 3.0 has two named readers: the two agreement checks (Goal 2) and G2's
tallies and text classes, `[rev2.2 R8]` both 3.0b's; so the fields and the plan-function outputs that fill them
land in 3.0b (§4.1). Row 1 and the trace come later. No artifact text or stamp reads them, so no byte
moves. pcrec reads none of them in 3.0 (§4.2).

### 2.4 The asker fact's retirement

**Today.** T-FIND (`fd_find`, `finder.c` :640-679) has two askers. The composer asks with `st` NULL. The
window family asks with `st` set and `renders_pair` the literal 1 (`window.c` :1840). The PAIR row's facts
include `SF_ASKER_PAIR` (`finder.c` :105-106, :289, set at :656). Review 2026-11-05-r2 F5 (:96-102) showed
the fact equals `st != NULL` and that its false branch has no witness. F9 (:124-130) named the general form:
one renderer table where a frame renders a pick iff a row exists. Its trigger is 3.0, and so is plan row
[SP1E-RENDERER-TABLE] (`plan.md` :835).

**3.0a.** ONE declared SEARCH renderer table, `(T-FRAME row, pick) -> first-match search renderer rows`
(§2.6.1). `[rev2 F11]` It is keyed by T-FRAME's ids, so the reply's `frame_row` and `search` look its row up:

- frame row `E-find`: today's `wf_brows` less B-fn (B-pair for PAIR; B-memchr for LIBC and LIBC_BACK;
  B-walk for WALK; B-hors for HORS). B-fn is a FUSED row, matched first (§2.6.3);
- frame row `E-stmt`: today's `fd_renderers` (`compose.c` :272-292: LIBC by `end_back`, LIBC_BACK, WALK by
  `end_back`). `[rev2 F11]` The composer's FIND sites that are not window sites (no T-FRAME walk, never
  asked by `mf_wdecide`) read the same rows: that is compose `arms[]`'s named exception, with its trigger
  ("a kit request adds an arm");
- E-func and E-generic have no search renderer row (E-func renders through its fused arm; E-generic has no
  search);
- layer: one wildcard column, as declared today. No row is layer-keyed: the SIMD rungs stay `fn_rows`
  PREFIX and vrun's KA/KB, the named exceptions with their census rule (§2.7).

`[rev2 F9]` **The renderable set.** A pick is renderable on a frame iff the search renderer table has a row
for (frame, pick) AND Table S (§2.5.3) answers `[rev2.2 R3]` ST-one or ST-many for (pick, frame), that is, at
least one stream. It is ONE function, read by T-FIND's gate and by the composition, so the two cannot disagree.
`[rev2.2 R3]` **ST-many refuses AFTER the gate.** The gate is a 0/1 predicate inside `kit_walk` (`fd_holds`,
`finder.c` :499-511): a 0 is a DECLINE and the walk goes on to the next row, so a gate that read "exactly one"
would turn ST-many into a silent move to the next T-FIND row (PAIR -> R7w, B-walk), the unmeasured choice change
(D186) ST-many exists to stop. So the gate holds on ST-one or ST-many (ST-none declines, as before), and on
ST-many `fd_find` then returns 0 with `*row` a NAMED refusal (the `?need` shape, `finder.c` :659-668; kit.h
:557-568: "a caller that must tell the refusal from 'no row' reads `*row`"; the spelling is the build's, e.g.
`?stream`). The composer observes it through `select_arm`'s kept refusal (below); the window family gains the
same read in `wf_find_decide`, which today reads only the return (`window.c` :1842), and refuses the define with
a message naming Table S's refusal. `[rev2 F4]` The gate sits in
`fd_holds` (`finder.c` :499-511) and applies to slot FIND only (`r->slot == FD_FIND`): `fd_holds` and
`fd_decide` also walk slot PRES, whose rows P0-P9 have pick `FF_UNSTATED` (`finder.c` :313-336), and an
unscoped gate would decline every pre-check decision. This replaces `SF_ASKER_PAIR`, which is deleted; bit
15 is retired and never reused, like bits 6-8, 12 and 13. It also replaces `renders_pair`, which is
deleted. The false branch gains a witness: `find_facts` states SF_TWO_MEMBER on a composer site's
two-member set at offset 0 (`finder.c` :555, :567-574), so with the check removed the composer would pick
PAIR and refuse (§5 row C).

`[rev2 F7]` **The composer's refusal is KEPT.** `select_arm`'s routed refusal (`compose.c` :317-325: a
deciding row whose pick has no renderer arm returns NULL, "no fall-back to the walk below") stays. The PAIR
sub-case becomes unreachable, but the same branch serves the `?need` refusal (`finder.c` :660-668: a row
named with no pick) and an arm that declines its own gate (`kit_ask`, :320-322). It is also the observation
point of sabotage rows (B) and (C): a build that deleted it, or let an unmatched pick fall through to
`kit_walk`, would turn (C) into the walk's bytes, SAME.

`[rev2 F18]` **HORS keeps a second filter.** `hors_facts` runs only when `st` is set (`finder.c` :655), so
the composer, which states no `fd_stop`, never states D-hors's window facts (`SF_HORS_WINDOW`,
`SF_HORS_DENSE`). On the composer HORS is therefore excluded by that absent fact AND by the renderable set
(no E-stmt HORS row); the new branch is dead behind the old one and has no witness. Rev 1's "PAIR and HORS
are then filtered by one mechanism" is WITHDRAWN: it holds for PAIR only. The residue closes with F5's
second half (the composer states an `fd_stop`), trigger "a kit request adds an arm".

`[rev2 F1]` **B-fn's dependency.** The renderable set reads the SEARCH renderer table only, so B-fn (a fused
row) is reachable only because B-pair's (E-find, PAIR) row exists. A unit that deletes B-pair while B-fn
stays must first enter fused rows' picks into the renderable set. That is its trigger; 3.0 changes no row.

`fn_rows` BODY, the third member F9 names, stays a named exception: it chooses PAIR or LIBC for the
offset-skip function outside T-FIND. Its trigger is "pcrec states a kind on OFS sites". `[rev2 F14]` Its
choice now crosses the seam as a fact (`search`), `[rev2.2 R8]` from 3.0b, which adds the pick column it is read
through. The composer stating an `fd_stop` (F5's second half) is
NOT in 3.0: a RUN span needs a field `fd_stop` lacks.

`[rev2 F28]` **One accessor per table.** Every renderer lookup (search, stream, check, fused) goes through
its table's one named lookup function (`ren_find(` in the kit, one per table or one over all of them; the
name is the build's), never an open-coded loop. `decider_census.py`'s backstop (:58-61) gains that spelling
as a LIVE shape: today's lists are spelled with none of its shapes (`fd_renderer`, `compose.c` :285-291; Table B's
walk, `window.c` :1850-1851), so a planted twin copied from them is green. `[rev2.2 R4]` **The shapes are
NARROWED to the renderer tables' names**: the backstop gains `ren_find(` (LIVE) and, per renderer table, its
array name followed by `[` (LIVE; the names are the build's, one `ren_` family). The row-walk idioms `.pick ==`,
`->pick ==` and `].holds(` are NOT shapes: `].holds(` is the idiom of EVERY declared table, and at a678d0a4e
they hit 9 lines in no census member (the `kit_walk` adapters `fn_row_holds`, `ofsskip.c` :440, `a_holds`,
`window.c` :726, `m_holds` :791, `e_holds` :1625; Table C's walk in `c_plan` :1102; `b_pair_holds` ..
`b_hors_holds` :1785-1792), each a check-B FAIL whatever HITS says (r13 V-1). **Expected after 3.0a**: MEMBER_COUNT
52 + 7 = 59 (the support table, Table S, the stream renderer table, the check renderer rows, the skeleton rows,
the fused rows, and `ren_find`; the search renderer table takes `fd_renderer`'s row, tsv :29, so it adds none),
moved with the map in the same commit as the script requires; HITS = 36 less the hit lines 3.0a deletes plus
every line holding `ren_find(` or a renderer table's name, re-pinned to the build's exact count with each new hit
line inside a member (a build that declares the tables differently re-derives both numbers from its map, never
leaving slack).

**Every reader of the asker fact, found by grep** (`git grep -n 'asker\|renders_pair\|SF_ASKER_PAIR'`
outside history, lane reports and reviews; re-run at a678d0a4e, `[rev2 F6, F25]` completed):

| reader | disposition |
|---|---|
| `memfn/src/finder.c` :37-38, :105-106, :217-222, :289, :594-618, :656 | the bit and its setter deleted; the PAIR row's facts become `SF_SPAN0 \| SF_TWO_MEMBER`; comments restated ("the frame renders PAIR"); the renderability check added in `fd_holds`, slot FIND only |
| `memfn/src/kit.h` :531-556 (`fd_form`'s "each asker renders", `fd_stop.renders_pair`), `[rev2 F25]` :557-561 (`fd_find`'s "for one of two askers") | `renders_pair` deleted; `fd_stop` (and the composer's path) gain the renderable set; comments restated |
| `memfn/src/window.c` :37 (header), :1840 (`.renders_pair = 1`) | deleted: E-find's renderable set comes from the tables |
| `memfn/src/compose.c` :262-292 (`fd_renderers`, `fd_renderer`) | moved into the one search renderer table (its E-stmt rows); `[rev2 F7]` `select_arm`'s refusal :317-325 kept |
| `memfn/src/formhash.c` :272, :446 (comments), :472 (`*row = wf_plan_brow(...)`), :511 | `[rev2 F1]` comments reworded ("E-find renders PAIR"); the code stays: `wf_plan_brow` keeps returning T-FIND's DECIDING row (`window.c` :2817-2820), which the `pair` entry pins as `"PAIR"` (:296) and :511 compares. The renderer or fused row id is `wf_plan_bren`'s successor (:2824-2827), returning today's strings (`B-fn`, `B-pair`, `B-memchr`, `B-walk`, `B-hors`), so FDROUTE's `row=` and `ren=` (`compose.c` :1153-1156) print the same bytes |
| `[rev2 F6]` `tests/memfn/renderer_rows.tsv` (header :1-12: "the renderer row is the asker's own"; the pairs `PAIR B-fn E-find`, `PAIR B-pair E-find`, `D-hors B-hors E-find`, ...) and `tests/memfn/rows_check.py` §R (:751-789; :765 requires frame E-find or `composer`) | KEPT as the search renderer table's NAMED PIN (hand-written from the tables, held to every traced FDROUTE pair): re-keyed (frame, method row, renderer row) with frame values `E-find` and `E-stmt` (:765 follows), B-fn's line marked FUSED, header restated. The `ren=` values do not change, so no witness compile moves. `[rev2.2 R10]` FUSED is a 6th column `fused` (YES/NO), and the loader reads `read_tsv(..., 6)` (:756; :157-158 refuse any other count). FDROUTE prints `frame=<T-FRAME id>` (`compose.c` :1153-1156 print none today), so §R holds (frame, row, ren) TRIPLES and the frame column is checked against an observation, not only for membership (:765); `trace_format.md`'s FDROUTE line moves with it (a trace line, no emitted byte). Recommended over "the frame column is documentation the check does not hold" (§7 Q15) |
| `[rev2 F6, F25]` `memfn/docs/trace_format.md` :168-177 (FDROUTE's key "frame row, method row, renderer row") and :178-183 (the composer's D-hors PRED_FALSE record: "it states no stop") | :168-177 restated with the split's names `[rev2.2 R10]` and FDROUTE's new `frame=` key; :178-183 STAYS TRUE (F18's residue) and gains one clause naming it |
| `memfn/src/CLAUDE.md` :9, :15, :21, `[rev2.2 R14]` :26 (`compose.c`'s line naming `fd_renderers`), :41 | restated: the split's tables, the fused rows, the renderable set |
| `[rev2.2 R14]` `tests/memfn/CLAUDE.md` :37 (renderer_rows.tsv's role: "(method row, renderer row) pairs") | restated: (frame, method row, renderer row, fused) and the traced triple |
| `[rev2.2 R14]` comments naming the retired arrays: `window.c` :39, :1264, :1533, :2484, :2692, :2815 (`wf_brows`, `wf_b_render`); `compose.c` :1151 (`fd_renderers`); `rows_check.py` :103 (docstring); `decider_census.py` :74 (MEMBER_COUNT's history naming `fd_renderer`, which gains its 3.0a line) | restated with the split's names |
| `[rev2.2 R14]` Table B's two `_Static_assert`s (`window.c` :2708-2711: every Table B row has its text and its find slot) | retire with `wf_b_render`/`wf_b_find`; each new renderer table gets its successor (its row count equals its id enum's), in the same commit |
| `[rev2.2 R14]` `docs/design/memfn/units_inventory.md` :56 (`wf_b_render` B-hors), :111 (`wf_brows` :1699, `b_fn_holds` :1672, already-stale cites) | a dated note at 3.0a: the rows now live in the split's tables (the inventory is a TRIAL record; its cites are restated, not its findings) |
| `[rev2.2 R14]` `docs/design/memfn/window_site.md` :272, :340, :342 (`wf_brows`, `wf_b_render`, "B's renderers on E-find's text") | restated with §8's window_site amendment, beside :336 |
| `tests/memfn/decider_census.tsv` :24 (`fd_find`'s note), :29 (`fd_renderer` -> the table), :66-67 (`wf_find_decide`, `wf_prepare`) | rows edited by 3.0a; rows added for the support table and Table S (`answers` T-STREAM, `[rev2 F20]` the new question, §8), the stream renderer table, `[rev2 F20]` the check renderer rows and the skeleton rows (T-FRAME), and the fused rows (EXC: naming `arms[]` and `fn_rows` BODY, which they are); `decider_census.py`'s backstop re-pinned (F28) |
| `memfn/docs/finder_history.md` | a dated row for the PAIR row's facts edit |
| `docs/design/memfn/span_pick.md` :109, :135, :420, `[rev2 F25]` :45, :51, :369, :408 | the named exception retires: amendment §8 |
| `[rev2 F25]` `docs/design/memfn/span_cards.md` :865 (the `pair` card's facts cite `kit.h` `fd_stop.renders_pair`) | the card's fact restated: "E-find's search renderer table has (E-find, PAIR)" (§8); the card's hash does not move (Goal 1) |
| `[rev2 F25]` `docs/design/memfn/window_site.md` :336 ("the one walk of both T-FIND askers") | restated with §8's window_site amendment |
| `docs/dev/plan.md` :835 [SP1E-RENDERER-TABLE] | closed by 3.0a (main's edit) |
| NOT readers | lane reports and review records (history); `src/gen/emit_dfa.c`'s 57 `asker` hits (the stream start table's FINISH/RECOVER asker), `src/facts/facts.c` :115, `docs/design/stream/roadmap.md`, `start_landing.md`, patfacts, decisions.md D184: a different "asker" |

### 2.5 The triple: search, candidate stream, check

A site's find-then-verify plan is three pieces, each answered by its own FACT table, and composed. `[rev2
F8]` The owner ruled the stream a separately chosen piece (§R1 row 1).

| piece | its table (facts) | it answers | in the reply |
|---|---|---|---|
| SEARCH | T-FIND (`fd_rows[]`, `finder.c` :257-307; its pick `fd_form`, `kit.h` :538-539), over Table A's stop; on a fused row, the row's declared pick | where the next candidate is: a position, or a block's lane mask | `search` (and `method`, its deciding row) |
| CANDIDATE STREAM | the SUPPORT table (§2.5.2) and Table S (§2.5.3), new in 3.0a | how the text moves past a candidate the check rejects | `stream` |
| CHECK | T-VERIFY (Table C, `wf_crows`, `window.c` :1051-1092, every holding row applying in order) | whether a candidate is a match: member test, bound, run compares | the T-VERIFY group and `plan_test` (§2.3) |

`[rev2.1 Q13]` A SIMD rung is a whole triple of its own (§2.7); the reply does not list it (the gap, §2.3).

#### 2.5.1 The three streams

- **RESTART** `[rev2 F24]`: the search returns one candidate position c, and after a rejection the next
  search starts at c + 1. This is today's `C++` (`resume_next`, `window.c` :2308-2311). libc `memchr` can
  only be this.
- **MASK**: the search produces a block's lane mask, and after a rejection the text takes the mask's next
  set lane without reloading the block. Only when the mask is empty does the next block load. This is
  vrun.c's loop (`while (m) { cand = i + ctz(m); ...; m &= m - 1; }`, `vrun.c` :317-329). `[rev2 F27]` Where
  the trim leaves no compare, the lowest lane IS the answer (`if (m) return i + ctz(m);`, :313-315): the
  MASK stream with an empty check.
- **SHIFT**: the text moves by the skip table's shift of a probed byte (D-hors: `C += SH[B]`,
  `d_hors_next`, `window.c` :2671-2674). It applies both after a probe miss and after a rejection.

#### 2.5.2 Which streams each search supports (the SUPPORT table) `[rev2 F8, F21]`

A declared table of BUILT searches only: the text each row describes exists at a678d0a4e. Each row names
the SOURCE of its stream cell, which is also what the support pin (§5 rows M, R) holds it to.

| search (`mf_wsearch`; T-FIND rows) | candidate it produces | RESTART | MASK | SHIFT | source and basis |
|---|---|---|---|---|---|
| LIBC (D1) | a position | yes | no | no | RULING TEXT: "libc memchr supplies only one-shot" (`responses.md`, lane/memfn-k1107, 067aca4df) |
| LIBC_BACK (D1c) | a position | yes | no | no | RULING TEXT (the same: `memchr` below the candidate, `pf_memchr_back`) |
| WALK (R7w, D1w) | a position | yes | no | no | DERIVED: a byte loop stops at one position. Basis witness: base's text of every B-walk and PF walk site resumes `C++` and declares no mask variable |
| PAIR (PAIR) | a position | yes | no | no | DERIVED: the frontiers (`ha`, `hb`, `ofs_pair_text`, `ofsskip.c` :283) are the SEARCH's own state, declared before the loop (§2.6.1's loop-state slot) and kept across restarts; the restart is still c + 1. Basis witness: base's B-pair and `fn-pair` text resumes `C++` |
| HORS (D-hors) | a position and its probed byte | no | no | yes | DERIVED: the shift table over the window is its stream. Basis witness: a site's text holds `_sh[256]` iff its search is HORS (`g2_win_gen.c` :998's class) |
| no search (the floor) | every position | yes | no | no | DERIVED: the floor tests each position in turn. Basis witness: `wf_floor_expr`'s `C++` (`window.c` :2324) |

`[rev2.2 R25]` Rev 2's VECTOR row (vrun's block compare: MASK only, derived from `vrun_verify`, `vrun.c` :310-329)
is REMOVED with `mf_wsearch`'s VECTOR value: with the rung list gone nothing produces VECTOR, no T-FIND row picks
it and no check could witness its cell (D77). Both are carried to §2.5.5's NOTE and plan row RUNG-LIST.

The unbuilt picks (`FF_V1`, `FF_W64`, `FF_A3`, `FF_NONE`) have no row. They are not renderable, as today.

**The support pin** `[rev2.2 R7]`. `tests/memfn/stream_support.tsv`, read by a new section S of
`tests/memfn/rows_check.py` (beside §R). Columns: `search` (an `mf_wsearch` name, or `floor`), `RESTART`, `MASK`,
`SHIFT` (each `yes`/`no`), `source` (`RULING` or `DERIVED`) and `basis` (for RULING: the ruling's sentence quoted
VERBATIM, with its ledger file and the commit as provenance, `memfn/docs/responses.md` 067aca4df; for DERIVED: the basis sentence
of the table above). The kit's table is C data, so a new `arm_fixtures --streams` mode prints it (one line per
row, the same columns less `source`/`basis`); §S compares each pin CELL to the printed table, and for RULING rows
the cell is the one the quoted sentence states, so the expectation is the ruling's text, never the table read
twice. §S is red on a missing or extra row, a cell that differs, or a RULING row whose quote is absent from the
working-tree ledger file the row names (a missing file is red too; the commit is never looked up). The DERIVED rows' basis witnesses are LANDING-TIME witnesses of 3.0a, recorded in its
report (base is gone after landing): over emit_sweep's BASE artifacts, joined to each site's FDROUTE `ren=` in a
trace build, every B-walk, B-pair, B-memchr and floor site resumes `C++` and declares no mask variable, and
`_sh[256]` appears iff `ren=B-hors`. The standing per-site join is 3.0b's G2 text classes (they read `search`, a
3.0b member).

#### 2.5.3 Table S, the stream pick (kit-internal, 3.0a) `[rev2 F8, F9]`

ONE rule. Its input is S = support(search) INTERSECT streams(frame), where streams(frame) is the set of
streams the frame's stream renderer rows render (§2.6.2) or, on a fused row, the stream it declares.

| row | holds | answer |
|---|---|---|
| ST-one | S has exactly one stream | that stream |
| ST-none | S is empty | no stream: the pick is NOT renderable on this frame (T-FIND's gate declines it; a fused row whose declared stream its search does not support is refused at its define) |
| ST-many | S has two or more streams | REFUSED until a row with evidence exists (D186: which stream is a CHOICE change and needs per-regime evidence; row 1's priced row, §6). Trigger: the first search with two streams on one frame. No 3.0 input reaches it. `[rev2.2 R3]` The refusal is raised AFTER T-FIND's gate (which holds on ST-many), by a named refusal row, never as a decline (§2.4) |

Table S reads no measurement and no price. **Today's selection, reproduced**: every built search supports
one stream, so ST-one answers every built (search, frame): HORS -> SHIFT on E-find; every other pick, and
the floor -> RESTART. `[rev2 F27]` That is `wf_b_render`'s `next` column for B-pair .. B-hors (`window.c`
:2703-2706); B-fn has no `next` (the function's own loop, RESTART by its declared stream), and the floor's
resume is `wf_floor_expr` :2324. The stream pick moves no byte.

#### 2.5.4 Composition

A triple holds on a frame iff:

1. T-FIND (or a fused row) gives a search the frame can render (the renderable set, §2.4);
2. Table S answers exactly one stream for it on that frame (`[rev2.2 R3]` two or more is the named ST-many
   refusal, never a fall-through), and the frame has that stream's renderer row
   (by construction: streams(frame) is read from those rows);
3. T-VERIFY's plan is rendered by the frame's check renderer row.

Any search composes with any stream it supports and with any check. No pair of pieces is special-cased.
The text is rendered INLINE by the frame's skeleton row (§2.6.0), with no call boundary between the pieces.

#### 2.5.5 NOTE carried to the inline one-member finder's unit (not built in 3.0) `[rev2 F8]`

D77: 3.0 builds no stream and no search ahead of its producer. These rev 1 items are carried, unbuilt, to
the finder unit's design (§6), which builds the first MASK stream renderer row:

- **S-mask**, rev 1's Table S row "the search supports MASK, and the frame has a MASK stream renderer row":
  under the one rule (§2.5.3) it is not a row at all. A search that supports MASK and RESTART on a frame that
  renders both reaches ST-many, so the finder unit needs an EVIDENCE row (or row 1's priced row) to choose.
- **The vector block search** `[rev2.2 R25]`: `mf_wsearch`'s VECTOR value and its support row (MASK, from
  `vrun_verify`, `vrun.c` :310-329), removed from 3.0; they enter with their first producer (RUNG-LIST, or the
  finder unit if its form is vector) together with a basis witness (vrun's text holds `m &= m - 1`) and a
  "VECTOR count 0 until then" assertion. VECTOR also admits RESTART (the lowest lane only, vany's use, `vany.c`
  :167, :174).
- **The word-at-a-time search** (SWAR has-byte; a candidate form of the inline one-member finder): a word's
  byte mask, admitting RESTART and MASK.
- **A MASK stream renderer row's loop state** (`m`), which takes §2.6.2's loop-state slot.

### 2.6 Table B splits into search, stream and check renderers

**Today** Table B is three parallel arrays over one index, `B_FN .. B_HORS` (`window.c` :1794):

- `wf_brows` (:1795-1819): `holds`, `libc`, `path`, `prepare`;
- `wf_b_find` (:2576-2579): each row's find text (`wf_b_pair` :2562, `wf_b_memchr` :2532, `wf_b_walk` :2549);
- `wf_b_render` (:2696-2711): `head` (`find_head` :2662, `d_hors_head` :2642), `next` (`resume_next` or
  `d_hors_next`) and `define` (`d_hors_define` :2677).

`[rev2 F2]` **And four per-row branches in its consumers**, which no column carries today (r12's lesson: a
split lists every branch, not only the columns): `wf_find_prepare`'s B-fn early return (`window.c`
:1868-1873: the translated site, libc 1, `<string.h>`); `wf_find_expr`'s B-fn call (:2723) and B-pair's
frontier declaration (:2731-2735: `ofs_pair_decl`, written after `wf_cand` and before `wf_raise`); and
`wf_find_define`'s B-fn function (:2760-2762).

E-find's loop (`wf_find_expr`, :2718-2748) writes `open; cand; [B-pair's declaration]; raise; for (;;) {
HEAD; if TEST { F = 1; break; } NEXT; } close`. So the search and the stream are FUSED in one row: B-walk
carries the resume c + 1, B-hors the shift.

#### 2.6.0 The frame skeleton rows `[rev2 F3]`

The loop's SHAPE is the frame's, not a search's. One skeleton row per composing frame, keyed by T-FRAME id:

| frame row | skeleton (pieces in order) | the bound (frame piece) | the lower half (frame piece) |
|---|---|---|---|
| E-find | `wf_open`; `wf_cand`; search row's loop state; stream row's loop state; RAISE; `for (;;) { ` HEAD `if ` TEST ` { F = 1; break; } ` NEXT `; } `; `wf_close` | `wf_bound`'s text, PLACED by the search row: after the find (`find_head` :2662-2668), or before the probe (`d_hors_head`) | RAISE before the loop (`wf_raise`, lower 0) |
| E-generic | `wf_open`; `wf_cand`; `for (; ` BOUND `; ` NEXT `) if ` TEST ` { F = 1; break; } `; `wf_close` (`wf_floor_expr`, :2314-2327) | the CHECK row's `cond` (`wf_test` calls `wf_bound` into it, :2274-2279), in the for header | inside the test (lower 1); no RAISE |
| E-stmt | none: the PF arm's text is a search, and the loop is pcrec's (the caller's) | the arm's | the arm's |

`[rev2.2 R15]` **Render order is not text order.** Each skeleton row states both. E-find renders in text order
(`wf_open(rc, &b, 1, wf_find_reads_fl(w))`, `window.c` :2729: its flags do not depend on the pieces). E-generic
RENDERS the check first: `wf_floor_expr` calls `wf_test(rc, &t, &cond)` (:2320), which also writes the bound and
sets `rc->used` (`wf_member_of` sets PARAM_S, :2166, :2169; the bound sets PARAM_FL, :2205, :2230), and only then `wf_open(rc,
&e, rc->used & PARAM_S, rc->used & PARAM_FL)` (:2321), then `wf_cand`, the `for` header and NEXT. A skeleton
writer that rendered the floor in text order would write `wf_open` with `used` 0 and drop its parameters (emit_sweep
would catch it). F2's "loop state before RAISE" is an ordering of TEXT and stays.

Fused rows (B-fn, the offset-skip arm) keep their own text whole. Every composing frame, E-generic
included, takes NEXT from the stream renderer row Table S's answer names; a (frame, stream) with no row
REFUSES (rule 2 of §2.5.4). Today `wf_floor_expr` calls `resume_next` directly; under 3.0a it reads its
stream row, so sabotage rows (L) and (N) reach the floor (§5).

#### 2.6.1 The search renderer table, keyed (T-FRAME row, pick) `[rev2 F2, F11]`

It is §2.4's table. Its E-find rows take `wf_brows`' `holds`, `libc` and `path` columns, `wf_b_find`'s text,
the search half of `head`, and `[rev2 F2]` a LOOP-STATE slot written before the frame's RAISE:

| frame row | pick | search renderer row | loop state (before the loop) | its text |
|---|---|---|---|---|
| E-find | PAIR | B-pair | `ofs_pair_decl` (`ofsskip.c` :275-279: `size_t HA = 0, HB = 0, WA = 128, WB = 128;`) | `wf_b_pair` + the bound (`find_head`) |
| E-find | LIBC, LIBC_BACK | B-memchr | none | `wf_b_memchr` + the bound |
| E-find | WALK | B-walk | none | `wf_b_walk` + the bound |
| E-find | HORS | B-hors | none | the bound, then the probe of the window's last position into B (`d_hors_head` less its resume text, which it takes from the stream renderer); `prepare` sets `hl` (the probe's offset) |
| E-stmt | LIBC (by `end_back`), LIBC_BACK, WALK (by `end_back`) | `fd_renderers`' arms | none | the PF arms (`pffind.c`): a search only; the caller restarts and checks |

#### 2.6.2 The stream renderer table, keyed (T-FRAME row, stream) `[rev2 F2, F11, F24]`

| frame row | stream | stream renderer row | loop state | its text |
|---|---|---|---|---|
| E-find | RESTART | S-restart | none | `resume_next`: `C++` |
| E-generic | RESTART | S-restart (`[rev2.2 R13]` a second row with the same text) | none | `resume_next`: `C++`, in the for header |
| E-find | SHIFT | S-shift | none | `d_hors_next`: `C += SH[B]`, used at the rejection and inside the search head's probe miss; its prepare is `hors_table` (`sh`), and its file-scope text is `d_hors_define` (the 256-byte table) |
| E-stmt | RESTART | S-caller | none | no text: the caller's NEXT loop restarts at c + 1 |

`[rev2.2 R13]` The table holds ONE ROW PER (frame, stream): E-find's and E-generic's S-restart are two rows that
share one text (`resume_next`), so sabotage (N) can delete E-generic's alone and (L) can plant the shared text.
The loop-state slot is empty on every 3.0 stream row; a MASK row's `m` will use it (§2.5.5).

The CHECK renderer is one row per composing frame in 3.0 `[rev2 F11]`: E-find's C-find (`wf_test_to` less
the position the search proved: `skip`, C-stop's or the probe's), E-generic's C-floor (`wf_test` :2274,
which also writes the bound, §2.6.0), and E-stmt's C-caller (no text: pcrec checks). It is keyed by frame
row only. `[code review r1 s30a F4]` C-caller is not built as a row: no frame renders or reads a check on
E-stmt (nor does 3.0b's field map, §4.1), so a row there would be a declared cell with no reader. A second check spelling (vrun's mask-trimmed compare, §2.7) becomes its second row. `[rev2 F19]`
Which positions a search proves has three homes today (C-stop, `d_hors_head`'s `skip`, vrun's TRIM); the
PROVES column unifies them at its trigger (§7 Q9).

#### 2.6.3 The fused rows `[rev2 F1, F10, F14]`

Some renderers render the whole triple as ONE piece. The composition matches them FIRST. The reply says
`fused` FN and crosses each row's FACTS (its pick and stream), never its id:

`[rev2.2 R24]` The fused-rows table has one column per piece; its `stream` column is the HOME of each fused row's
declared stream (the offset-skip arm's RESTART included: `fn_rows` gains only BODY's pick, in 3.0b).

| frame row | fused row | holds | declared search | declared stream | check |
|---|---|---|---|---|---|
| E-find | B-fn | `b_fn_holds` (`window.c` :1773-1786): pick PAIR, the plan IS the offset-skip function's predicate, and `fn_rows` BODY takes fn-pair | PAIR | RESTART | the function's predicate test, inside `<prefix>_mf<handle>_ofsskip` (`wf_find_fn` :2621, `wf_find_define` :2753); at the SIMD layer, its PREFIX rungs run too (unreported: §2.3's gap) |
| E-func | the offset-skip arm (`ofsskip`, `ofsskip.c` :910) | the composer's walk reaches it | `fn_rows` BODY's row's pick: PAIR (`fn-pair`) or LIBC (`fn-memchr`) | RESTART | the predicate test; at the SIMD layer, the PREFIX rungs over `fn-pair` (`vrun_over`) run too (unreported) |

`[rev2 F10]` The composer's PF arms are NOT fused rows: they are E-stmt's search renderer rows, composed with
S-caller and C-caller (`fused` NO). The composer's other arms (pre-check composites, `runcmp`,
`mismatch_inplace`, `generic`) are arms[]'s named exception (`fused` ARM), with its trigger. Their set
test, and the fused rows', is their own, so `plan_test` `[rev2.2 R2]` and `stop_test` are NONE there `[rev2 F12]`: two E-func asks that
differ only in `table_name` stated-ness may answer equal replies while the function's table parameters
differ. That residue closes when a fused row is re-expressed.

Re-expressing a fused row as a composition is a later unit with zero movers each. Its trigger is "a second
user of the row's pieces", as F9's census rule states it. vrun is the first candidate (§2.7). B-fn's
reconciliation with `fn_rows` BODY is KEPT (span_pick §The tables, T-FRAME), as today. `[rev2 F1]` The id
`B-fn` stays the FDROUTE `ren=` value (`wf_plan_bren`'s successor); it is the emitter's, not the reply's.

#### 2.6.4 Why the split moves zero bytes, and the witnesses that show it `[rev2 F2, F3, F5]`

The composition writes the same spellings in the same order as today:

| row today | loop state | head (search renderer) | test (check renderer) | next (stream renderer) | file scope | `libc` |
|---|---|---|---|---|---|---|
| B-pair | `ofs_pair_decl`, before RAISE | `wf_b_pair` + bound, as `find_head` | C-find | S-restart | none | 1 |
| B-memchr | none | `wf_b_memchr` + bound | C-find | S-restart | none | 1 |
| B-walk | none | `wf_b_walk` + bound | C-find | S-restart | none | 0 |
| B-hors | none | bound + probe; its miss text is `)) { ` + S-shift's text + `; continue; } ` | C-find less the probe | S-shift | `d_hors_define` | 0 |
| B-fn | fused: unchanged | | | | `ofs_fn_define_at` (after the run compare's word loads) | 1 |
| floor (E-generic) | none | none (E-generic's skeleton) | C-floor, also the bound | S-restart, in the for header | none | its own, unchanged |

The only spelling that moves between functions is D-hors's probe-miss resume. Today `d_hors_head` writes
`)) { %s += %s[%s]; continue; } ` with (C, SH, B) (`window.c` :2653). `d_hors_next` writes `%s += %s[%s]`
with the same three names (:2673). So the probe miss written as `)) { `, then S-shift's text, then `;
continue; } ` is the same byte string. The shift table's define stays one file-scope text per site, after
the run compares' word loads (`wf_find_define` :2763-2764). `[rev2 F2]` B-pair's declaration keeps its place
(after `wf_cand`, before `wf_raise`) as the search row's loop state.

`[rev2 F5]` **The libc and include facts** (`wf_find_prepare` :1879-1880) become the OR over ALL THREE
pieces: the search row's `libc` (B-pair 1, B-memchr 1, B-walk 0, B-hors 0), the stream row's (S-restart 0,
S-shift 0) and the check's (1 iff `nrun > 0`: the run compares' `memcmp` row and `memcpy` word loads,
runcmp.c). The fused B-fn is 1 (:1868-1873). `includes` is `MF_INC_STRING_H` iff `libc`. That is today's
`brows.libc || w->nrun` exactly. Rev 1's "the other search rows do" was wrong for B-walk, and a union over
two pieces would flip `libc_free` and `includes` (`wf_plan_class`, :2794-2795) on a B-walk or B-hors site
with a run term. Witness: `build/pcrec -p rx --memfn=no-fd-d1 --pattern abcdef` (B-walk plus `rx_w4` run
compares); plant (Q).

**Witnesses** (rev 0's, now also covering the split): `scripts/emit_sweep.py` byte-identical on every arm
against 3.0a's named base. Every form id's hash is unchanged (`arm_fixtures --hash`, base vs HEAD), and check
C's stale count is 0 (`formhash.c` :296's `pair` instance is E-find's PAIR text). G2 is green
(`memfn/tests/run_g2_win.sh` with its `EFIND_FLOORS` census, :82: libc, walk, hors, pair, fn and the rest each
at or above its floor; the finder G2). REACH EQUALITY holds (`MFTRACE REACH`, chosen and asked per row, base
vs HEAD), `[rev2 F4]` including slot PRES's rows P0-P9 over the pre-check composites' sites. `[rev2.2 R5]` It
covers what `reach_print` prints: the four `kit_walk` contracts arms, runcmp, fn and fd (`gate.c` :882-908; not
Tables A, M or E, r13 V-3). **3.0a's new tables print no REACH**: they are plain first-match arrays read through
`ren_find`, as Table B's open loop is today (`window.c` :1850-1851), so `reach_equal.py` sees no new row (it is
red on ANY row present at HEAD and absent at base, :237-240, and has no "new row" declaration). Their reach is
shown by byte identity and by the sabotage rows that plant them (K, L, N, P, Q, R). `decider_census.py` is green with its
re-pinned backstop. `rows_check.py` §R is green over the re-keyed pin. No `*_movers.txt` moves.

### 2.7 vrun and vany as compositions `[rev2 F27]` `[rev2.1 Q13]`

**vrun.** Its rows `vrun-w16`/`vrun-w32` (`vrun.c`; `fn_rows` PREFIX, `ofsskip.c` :423-424) are PREFIX rungs
of the offset-skip function, OVER fn-pair (`vrun_over`, `vrun.c` :406), on the SIMD layer only. Each helper is the
triple, hand-composed:

- SEARCH: VECTOR, a vector block compare at KA (and KB where the ranking gives one): one unaligned load, an
  AND, a compare and a movemask per block (`cmask`, `vrun_render` :337-403). It produces a lane mask;
- STREAM: MASK. Each set lane is taken lowest first, and the next block loads only when the mask is empty
  (`vrun_verify` :310-329), `[rev2 F27]` or, where the trim leaves no compare, the lowest lane is the answer
  (:313-315);
- CHECK: TRIM, the BODY's run compare less the positions the mask proved (`run_cmp_render_trim`), or the
  padded compare on the main path (`run_cmp_render_pad`). This is T-VERIFY's C-stop rule ("minus what the
  search proved") applied to the search's proven positions.

`[rev2.1 Q13]` **3.0b does NOT name vrun's triple in the reply.** The kit manager ruled F13 a label (r12, "Ruling on rev 2's Q13"): the reply's triple is the OFF variant's and §2.3 states the gap. The list (`rung[]`: `vrun-w32`/`vrun-w16`, VECTOR, MASK, TRIM; the three fact columns (search, stream, check) on each PREFIX row in `fn_rows`; the file-scope sink's bracket fact) is plan row RUNG-LIST (§7). Nothing in 3.0 reads the PREFIX facts, so none is declared (D77). `vrun.c` is not edited and no text moves.

The re-expression makes those three pieces composed rows: a vector search renderer row, a MASK stream
renderer row and the trimmed check as the check renderer's second row. **Not in 3.0.** Its reasons:

1. it needs a frame row for the function's PREFIX slot, which the composer's fused arms do not have yet;
2. the target seam's U2+U3 (`target_seam_units.md`) moves vrun's admission into per-target arts.
   Re-expressing vrun before that remodel would re-touch the same lines (D153);
3. no second user of the MASK row exists yet (the census rule's trigger).

It is its own zero-mover unit (Q9). Until then vrun stays the named exception it is today (the SIMD rungs,
§2.4's layer column), unreported (§2.3's gap).

**vany.** `vany.c` is a bare SEARCH: a vector any-of compare over 2-3 bytes, whose lowest set lane is the
answer (`vany.c` :167, :174). It is NOT ROUTED (`vany.c` :16-22: no row, no deny, no pcrec caller). It enters
as a search piece, meaning a T-FIND row, a search renderer row and its card under `kit-kernels@1`, only in the
unit that routes it, triggered by a measured win in row 1's search comparison (§6). **Not in 3.0** (D77).

### 2.8 Facts apart from C spellings `[rev2 F16, F17]`

| layer | tables | what a Rust emitter would do | what is C-specific in it today `[rev2 F17]` |
|---|---|---|---|
| FACTS (the plan) | T-FRAME (Table E), Table A (stop), T-FIND (search), the support table, Table S (stream), T-VERIFY (Table C: check), Table M, the TIE table | reuse the keys and the row logic; re-measure; map LIBC to its own library search | the LIBC/LIBC_BACK picks and their basis (a C library call boundary: "no block state survives the call"; Rust's `memchr` crate is itself vectorised, so its support may differ); the measure sets (taken on C artifacts and glibc); T-FRAME's legacy contracts and E-func's, which read hook text CLASSES; C-table's "pcrec's name" via a C callback |
| C SPELLINGS (the renderer) | the skeleton rows, the search renderer table, the stream renderer table, the check renderer rows, the fused rows' text, `ofs_pair_text`, runcmp.c's spellings, `[rev2 F16]` the hook-text CLASSIFIERS (`gate.c` :86-297, :618-653) | replace with its own rows, keyed the same way; state hook CLASSES, not C text | all of it, by definition |

The reply crosses only the FACTS layer's ids and enums (`frame_row`, `method`, `search`, `stream`, `fused`,
the check). `[rev2 F14]` Rev 1's exception (`fused` naming a C renderer) is gone: `fused` is a fact
about the piece boundary. `[rev2 F16]` The classifiers move to the spellings layer in this table only (no
code moves in 3.0); in a Rust world pcrec would state the class (§2.2's projection), and the gates would
read the class. Build trigger: [IR-FORM].

## 3. The number events and their same-commit package (readers by grep, D76/D94)

**MF_SITE_ABI**: 24 -> the next free number at landing of 3.0b (25 at this tree). `[s1d]` 27 at 35bee4da9, so 28
if 3.0b lands next; every cite in this section that 3.0b reads is re-based in §5 3.0b's re-base table. The target seam's
U2/U3 is also a kit seam event, and whichever lands second takes the next number and re-baselines (§5).
Readers (`git grep -n MF_SITE_ABI`, re-run at a678d0a4e), by class `[rev2 F25]`:

| class | readers | disposition |
|---|---|---|
| the definition and its history | `memfn/include/memfn.h` :39-204 | a new entry `[rev2]` `[rev2.1 Q13]`: "`mf_wdecide` takes the frame (the site's frame fields, the define hooks, `mf_wcall`); `mf_wreply` gains `framed`, `frame_row`, `method`, `search`, `stream`, `fused`, `plan_test` and `stop_test` `[rev2.2 R2]`, appended LAST; its T-VERIFY group, `plan_test` and `stop_test` are named the check; `mf_wcall`, `mf_wsearch`, `mf_wstream`, `mf_wfused`, `mf_wtest` added. No MF_VOCAB or MF_CLASS_V move; no pcrec byte moved" |
| prose that states the CURRENT number | `memfn/include/CLAUDE.md` :4 ("`MF_SITE_ABI` 24 (24: ...)") | becomes the new number with its one-line entry. (`memfn/docs/wake.md` :22's "MF_SITE_ABI 23" is the kit's per-session file, rewritten by the kit manager, not a 3.0 edit) |
| symbolic readers (they move with the macro) | `src/gen/memfn_sites.c` :455; `memfn/src/compose.c` :1011, :1067-1069; `window.c` :1226, :1419; `presence.c` :124; `formhash.c` :381; `memfn/tests/g2/g2_gen.c` :923, :2259, :2294, :3754, :3790, :3834, :4200, :4430-4431; `g2_simd_gen.c` :334; `g2_win_gen.c` :630, :737, :793, :837; `tests/memfn/arm_fixtures.c` :238; `mass_check.c` :258; `proof_check.c` :156; `proven_check.c` :63 | recompile only (complete: PREM re-ran it, 0 missing) |
| `[rev2 F25]` historical `MF_SITE_ABI n` (n <= 24): every other hit | a CLASS, not a closed list: 304 lines at a678d0a4e outside the ledgers, design notes and history (`git grep -n MF_SITE_ABI` with those excluded), in about 50 files: comments, refusal texts (e.g. `compose.c` :588, :624, :776, :820, :908), `fields.def`, kit.h, gate.c, generic.c, G2 sources and reports, `tests/memfn/pins/`, `site_manifest.tsv`, run scripts, and the sabotage headers. Only S1089 (:24-26) and S2903 (:13-14, anchored on `compose.c` :908's text) anchor on such a text | unchanged: each names the event that introduced its rule; the grep is re-run at landing and every anchor's text stays byte-identical |
| literal pins | none: G2 is symbolic (`MF_SITE_ABI + 1`), and the `site abi %u, kit abi %u` refusal is asserted by kind only (`G2M6_REPORT.md` :131, :243) | the grep is re-run at landing |
| the ledgers | `memfn/docs/journal.md`, `memfn/docs/responses.md` ([responses] R-35 3.0b) | entries in the same commit |

`[rev2 F25]` **A plan row whose trigger this is**: [SEAM-READER-CENSUS] (`plan.md` :1844, "every mf_* seam
member has a kit reader or a listed trigger", trigger "the next MF_SITE_ABI layout event"). 3.0b IS a layout
event. Whether it fires the row is main's call (§7 Q11); every member 3.0b adds already names its reader
(§2.3 "Who reads the new fields").

**MF_CLASS_V**: stays 8. It moves on an `mf_class` layout change, or on a finder-row index shift ahead of
the PRES rows (`memfn.h` :1080-1098). 3.0 adds, removes and reorders no finder row (PAIR's FACTS change,
not its index), and it adds no `mf_class` member. The support table and Table S are not finder rows. MF_CLASS_V's readers stay as they are: `memfn.h` :1080,
`window.c` :2790, `compose.c` :390, :1029, `proof_check.c` :408, `arm_fixtures.c` :386,
`memfn/include/CLAUDE.md` :4, `memfn/src/CLAUDE.md` :11. All are symbolic or prose. Putting the frame part
into `mf_class` instead would move it, and that is REJECTED: the class answers what the text proves (D157),
and the frame part reports a selection.

**Same-commit package of 3.0b** (beyond the table above): pcrec's ASK-1..ASK-5 (§4.2). The callers
`arm_fixtures.c` :2271, :2278, :2305, :2323 and `g2_win_gen.c` :742, :797, :855 (build breaks). `[rev2.2 R23]` A
fourth caller, outside both trees' builds but built by kit box-queue jobs (`240-kit-r33-sweep.sh`,
`241-kit-r33-rp.sh`, via its `build.sh`): `docs/dev/lanes/r33_sim/probe.c` :94 (`pcrec_mf_wdecide(art, s, &r)`,
three arguments). It is a lane STUDY (its CLAUDE.md: "nothing here is built or run by make"; lane files are
historical after merge; `span_pick.md` :378, unit 1g's reader row, already lists it as "lane evidence", not a
reader), so it is LEFT TO BREAK, named here and in the 3.0b report: a re-run of those jobs edits
it to call NONE, `def` NULL (recommended over editing a historical lane file in the seam commit, §7 Q15).
`[r1s1 S1-6]` **Superseded at 35bee4da9.** pcrec's asks are ASK-1 and ASK-3..ASK-6 (ASK-2 VOID), and the callers
the signature change breaks are the list in §5 3.0b's re-base block (`arm_fixtures.c` :2313, :2320, :2347, :2365;
`g2_win_gen.c` :817, :877, :941; `run_decide_check.c` :207). The probe is NOT left to break (§7 Q15 (3) RULED): its
successor is §5 3.0b's probe item, an out-of-build seam reader with its own compile-only check.
`[rev2.2 R27]` `pur_diff` keeps one more comparator, the decision-group prefix
`memcmp(a, b, offsetof(mf_wreply, framed))`, for the NONE-vs-framed equality (§2.3).
`[rev2 F32]` `pur_diff` (`arm_fixtures.c` :2204-2220) becomes a `memcmp` of the whole `mf_wreply`, naming the
first differing field only after a mismatch; the control print (:2328-2336) becomes a hex dump of the struct.
`[rev2 F27]` `run_finder.sh` :132's `PURITY_FLOOR` 1157 is an EXACT literal (read at :138), re-pinned to the
new count with its reason. `purity_rows.tsv` gains the Table E, B, S and skeleton rows (REACH,
or UNREACHED with a reason; its own id check re-run). `[rev2.2 R6]` **Its population and plant path**:
`tests/memfn/run_purity_reach.sh` :27-37 takes the population from `window.c` by three patterns (`WF_CT_A(`,
`WF_CT_M(`, `{ N, "C-`) and requires `purity_rows.tsv`'s ids to EQUAL it (`cmp`); a new id outside the patterns is
red, and marking it `+` would exempt it (K35). So the script gains one extraction pattern per new table: `WF_CT_E(`
for Table E, and each 3.0a table's row-declaration spelling (the build's: one row macro or id prefix per table:
skeleton, search, stream, check, fused, support, Table S). The 3.0a tables are declared in `window.c` (the file Table
B splits from), so the plant path, which rebuilds `window.c` only (:41-74, "a plant rebuilds window.c only"),
reaches them; a table the build declares in another file extends the plant path to that file in the same commit.
Readers of the harness description move with it: `run_purity_reach.sh` itself, `tests/memfn/CLAUDE.md` :43 ("THE
PURITY HARNESS (11 sites ...", "each Table A/M/T-VERIFY row"), and `run_finder.sh` :121-131's header. `g2_win.h` :44-53's reply copy grows.
`memfn/docs/trace_format.md` :102-113 is updated: "`mf_wdecide` ... writes none" stays true, and the frame
part is named, with the triple's three pieces. The comments that teach "the decision reads no frame
fact" are restated: `memfn.h` :556-558 ("read by phase 2 only"), :1435-1441 ("never a frame fact"), `[rev2
F25]` :1483-1486 (`mf_wdecide`'s own comment: three arguments), `window.c` :49, :1225, and `emit_dfa.c`
:7598-7603. Also `memfn/include/CLAUDE.md` and `memfn/src/CLAUDE.md`.
**No pcrec abi bump** (no byte moves). **No `docs/spec/` hunk**: D80 is not triggered, since no spec file
names `mf_wdecide`, `mf_wreply` or the asker (`git grep` over `docs/spec` and `docs/guide`, re-run: none).

## 4. The split

### 4.1 Kit-side edits (the kit's lanes; `memfn/` and the kit's tests)

3.0a: the search renderer table and the renderable set (§2.4). The support table, Table S, `[rev2 F3]` the
skeleton rows, the stream renderer table, the check renderer rows and the fused rows (§2.5, §2.6), which are
Table B's split. `[rev2 F28]` One named lookup accessor per renderer table. One internal PLAN FUNCTION
that computes the decision and, given a frame, `[rev2.2 R8]` WHAT THE DEFINE RENDERS: T-FRAME's row, T-FIND's
row and pick, the search renderer row, Table S's stream and its stream renderer row, and the check renderer row,
each stored in `wf_plan` where the define renders from it (the stream row beside `bren`'s successor). `wf_prepare`
(the define and `mf_ask`, `window.c` :1892) reads all of it; `mf_wdecide` reads its decision half only. The census
rows, the finder history row, the CLAUDE.md lines, the re-keyed `renderer_rows.tsv` and 3.0a's tests (§5),
including the support pin.
3.0b: the seam (§2.2, §2.3), `reply_of`'s frame part, `[rev2.2 R8]` the plan-function outputs only the reply
reads (`fused`, `plan_test`, `stop_test`, the reply ids `frame_row`/`method`, E-func's `search` and E-stmt's
reverse map from arm to pick, which needs the composer's arm walk, `select_arm`, `compose.c` :295-327, as a
second caller beside `kit_legacy_serves`, :333-339), `[rev2 F14]` the fact column on `fn_rows` (each BODY row's
pick: fn-pair PAIR, fn-memchr LIBC), `[rev2 F26]` the plan function's allocator parameter, `[rev2 F29]` the
define's own record of what it rendered (`site_rec` gains the fused function's BODY row, beside `r->arm`,
`r->fd_row` and `r->wplan`), the MF_TRACE agreement check at `define_sel` (beside rule 2's re-ask, `compose.c`
:1180-1200), the harness and G2 edits, and the ledgers.

**The agreement's two halves** `[rev2.2 R1]` (the kit manager's ruling: NARROW). `[d27fix F2, F3]` The re-ask is
the framed ask's DEFINE half under the define's phases: under `mf_emit` it leaves out the use half's refusals
(§2.2 contract line 2), which `mf_emit` makes after the define, at its use, so a site whose use refuses still
agrees at its define. The define-side reply is assembled, zeroed whole first, from two sources:

- **The FRAME part, from the STORED record**, by the field map below, never through `reply_of` or the plan
  function. This is what F29 and row E2 are about: a frame-part fault in the plan function that moves no text is
  red, because this side does not share its source.
- **The decision group, by RE-DERIVING it**: `decide` run on the stored site with the define's hooks and call,
  projected by `reply_of`'s decision half. It shares the plan function's source by construction, so here the
  agreement is a TRIPWIRE against the two calls diverging (a quiet-only branch, a cache, the heap allocator vs
  the arena). Its INDEPENDENT CONTROLS are named: the purity harness (a reply asked on a fresh art equals one asked
  between interleaved defines, whole-reply `memcmp`: the decision is a function of the facts only) and ASK-3
  (pcrec's phase-1 statement equals the define's, §4.2). As rule 2's re-ask re-runs `select_arm` rather than
  storing a second class (`compose.c` :1180-1186), there is NO stored decision copy in `site_rec`: a record
  nothing reads but the check is not built. A decision fault the plan function makes at both calls moves the
  define's TEXT (the define renders from that decision), so Goal 1's emit_sweep sees it.

The per-frame FIELD MAP (stored members at a678d0a4e: `site_rec`, `kit.h` :239-270; `struct wf_plan`,
`window.c` :1242-1274; `wf_prepare` stores `*plan` on E-find and E-generic only, :1947-1950, so `wplan` is NULL on
E-func and E-stmt, whose stored `site` is the translated legacy site; marked NEW where 3.0a or 3.0b adds the
member):

| reply field | E-find (`wplan->row` is `wf_find_arm`) | E-generic (`wplan->row` is `wf_floor_arm`) | E-func (`wplan` NULL, stored site FUNC/RETURN) | E-stmt (`wplan` NULL, stored site STMT) |
|---|---|---|---|---|
| `framed` | 1 | 1 | 1 | 1 |
| `frame_row` | `E-find`, from `wplan->row` | `E-generic`, from `wplan->row` | `E-func`, from `wplan == NULL` and the stored site's `form` | `E-stmt`, the same way |
| `method` | `wplan->brow` (T-FIND's row; `""` if none) | `""` | `""` | `r->fd_row` (`""` if none) |
| `search` | `wplan->pick` as `mf_wsearch`; PAIR where the stored renderer row is B-fn | NONE | the stored BODY row's pick (NEW `site_rec` member; NEW `fn_rows` column) where `r->arm` is the offset-skip arm; NONE on any other arm | the pick of the search renderer row naming `r->arm` (`fd_renderers`' map, `compose.c` :277-283) on a PF arm; NONE on any other arm |
| `stream` | the stored stream renderer row's stream (NEW `wf_plan` member, 3.0a); B-fn: the fused-rows table's `stream` | the stored stream renderer row's stream | the fused-rows table's `stream` (RESTART) on the offset-skip arm; NONE on any other arm | RESTART (S-caller) on a PF arm; NONE on any other arm |
| `fused` | FN iff the stored renderer row is B-fn, else NO | NO | FN on the offset-skip arm, else ARM | NO on a PF arm, else ARM |
| `plan_test[i]` | TABLE iff `wplan->table[k] != 0` for the `k` with `wplan->off[k] == plan[i]` (matched by OFFSET; `plan[]` from the re-derived decision) | the same | NONE | NONE |
| `stop_test` | TABLE iff `wplan->table[wplan->stop_ix] != 0`, when `stop_ix >= 0`; else NONE | NONE (`stop_ix` -1) | NONE | NONE |

### 4.2 pcrec-side asks for main to file (facts and checks, never the kit's method, D157)

R-35 ruling (a) puts these hunks in the kit's 3.0b package. Main reviews them, and the unit's code round
covers both sides. The triple changes no fact pcrec states. pcrec states the frame, the hooks
and the call; it never states a search, a stream or a check, and it reads none
of them in 3.0.

| # | ask | the exact facts |
|---|---|---|
| ASK-1 | the DFA prefilter's phase-1 ask states the frame of the site its offset rows define | on the ask's site: form FUNC, op FIND, handoff RETURN, empty MISS, use POSITION, body ONESHOT, site_kind UNSTATED (0), decl_point 0, on_miss_leaves 0, `pred.fn_ref` 1; the window statement `ofs_window_of` and floor SUBJECT, as today; define hooks `fn_name` and `table_name` STATED, `miss` MF_MISS_N, `comment_tier` NONESSENTIAL (other members unstated, as at the define); call DEFINE. Each value equals `ofs_site_define`'s (`emit_dfa.c` :7622-7642), and ASK-3 checks it. `[rev2 F22]` **`site_kind` is NOT stated in 3.0**, although R-35 (a) names "form, handoff and site_kind stated per frame at phase 1": OFS sites state no kind today (`span_pick.md` :131's named exception), and stating one is a decision-moving fact (it lets T-FIND decide OFS sites, which moves bytes), row 1's or later. This narrows ruling (a); main confirms (§7 Q12) |
| ASK-2 | `[s1d]` **VOID** (K38-2 deleted `req_run_member`; §5 3.0b's re-base block). Was: the run window's ask states no frame | call NONE, `def` NULL (`req_run_member`, `emit_dfa.c` :1058-1076); otherwise unchanged |
| ASK-3 | the offset-skip block's define holds the reply it was planned by | in a pcrec trace build (the `PCREC_CAND_TRACE` precedent `cand_asked_hold`, `emit_dfa.c` :7066-7085): at `ofs_site_define`, re-ask `mf_wdecide` with the define's own site, hooks, and call DEFINE. `[rev2 F32]` The WHOLE reply must equal `UnanchStart.wr`, byte for byte (`memcmp`; the kit zeroes every reply before it fills it). A difference fails the compile as a named invariant ("asked-plan-differs"). pcrec interprets no field |
| ASK-4 | ASK-3 runs and reaches its site | name the suite whose trace build runs over DFA prefilter sites (candidates: `tests/codegen/run_cand_oracle.sh` :90, `run_fallback_table.sh` :143), and prove reach with a pcrec-side sabotage row (§5 row F). |
| ASK-6 `[s1d]` | the `@` table's cover-row ask states no frame (K38-2's new caller) | call NONE, `def` NULL (`req_run_at`, `emit_dfa.c` :16077; it reads `has_stop` and `stop` only); otherwise unchanged. `[r1s1 S1-2]` **Its refusal becomes LOUD** (a pcrec same-commit hunk of 3.0b; **main approves it at the GO**): today a refused ask falls through to `at = -1` with no diagnostic (:16068-16079), unlike ASK-1's (:7614-7617), and 3.0b adds a refusal on exactly this call (row S: call 0 answers -1). `[r2s1 R30B-4]` **Corrected:** 3.0b adds a refusal of `call` 0 (UNSTATED, row S), which this call meets only if its hunk leaves `call` unstated; ASK-6 asks NONE (1), which is not refused. The hunk fails the compile, as ASK-1's `pcrec_ctx_fail` does, when `mf_wdecide` returns -1; a reply with `has_stop` 0 keeps today's `at = -1`. A green build moves no byte. `[r2s1 R30B-5]` **Where the fail goes:** `pcrec_ctx_fail` longjmps (`src/core/compile.c` :20-40), and the cover branch runs inside `req_run_at`'s `PCREC_CAND_TRACE` save (`pcrec_cand_trace_quiet++` and `cand_eval_base`, `emit_dfa.c` :16062-16066), which only `done:` restores (:16095-16099); the compile's recovery calls `pcrec_cand_eval_reset` (:10899-10903), which does not reset `pcrec_cand_trace_quiet`. So the hunk RECORDS the refusal inside the branch and calls `pcrec_ctx_fail` after `done:`'s restore, never inside the branch (there it would leave a trace build's thread quiet for its later compiles). The leak is a pre-existing class (other quiet regions, e.g. :11057-11063 and :11222-11373, enclose walks that may longjmp); its general fix, resetting `pcrec_cand_trace_quiet` in `pcrec_cand_eval_reset`, is a note for main, not 3.0b's. `[r2s1 R30B-3]` **Its plant** (a check added by a fix names a control that reds without it): **ASK-6 passes `call` 0** (UNSTATED) where it should pass NONE. The kit refuses (row S's rule), and the loud hunk turns that into the compile's internal-error text on every cover-routed pattern (`foo[0-9]{4}bar`, `abcdef`, `a{6}b`). The row asserts that TEXT (it names ASK-6's refusal), as row (F) asserts ASK-3's: with the loud hunk deleted, the same plant drops the cover `@` silently (emit_sweep sees a byte move, but no compile fails), so the asserted text reds only through the new check. Main chooses its form at the GO: sabotage row (AG) (recommended: a mech row re-runs at every matrix; 3.0b then has 20 rows), or a control run once at the build and recorded in its report. **Its reach witness** is emit_sweep's byte identity over cover-routed `<PREFIX>_REQ_RUN` `@` stamps (at 35bee4da9 `foo[0-9]{4}bar` emits `RX_REQ_RUN "626172@0"` with `RX_DFA_SCAN "cover"`; `abcdef` and `a{6}b` route `cover` too): the literal `@` checkers deny the cover route (`reqcube_check.py`'s `COVER_DENY`, `run_prechecks.sh`'s), and `run_encoding_checks.sh` normalizes `@` away, so emit_sweep is the one check that sees a dropped cover `@`. The general form (the ask states the cover define's frame, one trace-build compare holds it to the define) is §7 Q16 |
| ASK-5 | the comments that teach the frame-free ask are restated | `emit_dfa.c` :7598-7603 ("the decision reads no frame fact, so one ask serves every NEXT row"), and `UnanchStart`'s `wr` comment (:4630-4636): the ask states the offset rows' frame, and the rows below define their own site |

**Not asked**: a consumer kind on OFS sites (`[rev2 F22]` above); a frame for pre-check parts (§7 Q1); any
frame on the define-only scenarios (they have one already); any NEXT-row change; any stamp, CLI or spec
change; any pcrec reader of `search`, `stream`, `method`, `fused` or `plan_test`. **For main, not an
ask of code**: file the owner's ruling as a decision entry (`responses.md` 067aca4df, "proposed decision
entry"; §7 Q10), and rule [SEAM-READER-CENSUS] (§7 Q11) and ASK-1's `site_kind` reading (§7 Q12).

## 5. Build plan: two units

`[span_cards.md rev1 COST-4]`'s rule applies. Each unit names its BASE commit (main's tip at branch time)
in its first commit, and every identity witness compares against it. After any byte-moving lander on main,
an unlanded unit re-merges main, takes a new named base and re-runs its witnesses. **Sabotage ids are the
kit's, taken at BUILD time from the top of the free range** and recorded in the unit's first commit. The
highest kit id on any local branch at a678d0a4e is **S2981** (lane k0's S2975-S2981, lane/memfn-k0); `git
grep` over every local branch finds no S2982 or above, so the next free is S2982. `[rev2]` `[rev2.2 R22]` There
are 30 rows; if 3.0a lands first they are expected as S2982-S2993 for 3.0a's 12 rows (A-D, K-R), then
S2994-S3011 for 3.0b's 18 (E, E2, F-J, S-V, X-AD; W and AE retired `[rev2.1 Q13]`, letters not reused; rev 2 and
rev 2.1 never counted E2). §7 Q14 may add one row (AF) to 3.0b (`[r1s1 S1-6]` it did: Q14 RULED). Rows below are lettered. `[s1d]` 3.0a
took its rows in the S2982-S2993 range as expected, but S2994-S3012 are now all taken on main (the target
seam's U2 lanes S2994-S3004, K38-1 S3005-S3006, K38-2a S3007-S3012), so 3.0b's 19 rows (Q14 RULED: AF
added) are renumbered: §5 3.0b's re-base block gives the expected ids. Heavy runs are boxqueue jobs, with no timing and
no window.

**3.0a** — the triple's tables, Table B's split and the plan's frame part, kit-internal.

- **Content**: §2.4's search renderer table and renderable set (slot FIND only); `SF_ASKER_PAIR` and
  `renders_pair` deleted; `select_arm`'s refusal kept; §2.5's support table and Table S (ST-one, ST-none,
  ST-many); §2.6's skeleton rows, search and stream renderer tables with their loop-state slots, check
  renderer rows and fused rows (`wf_brows`, `wf_b_find`, `wf_b_render` and the four per-row branches retire
  into them; `wf_floor_expr` reads its stream row); one lookup accessor per table; the support pin
  `tests/memfn/stream_support.tsv`, `rows_check.py` §S and `arm_fixtures --streams` (§2.5.2), each pin row with
  its SOURCE column (ruling text for LIBC and LIBC_BACK, derived basis for the rest); the internal plan function
  `[rev2.2 R8]` computing what the define renders (§4.1; no `fused`, `plan_test`, `stop_test`, reply ids,
  `fn_rows` pick column or allocator parameter: those are 3.0b's); the census rows and narrowed backstop shapes
  (§2.4), the finder history row, `renderer_rows.tsv` re-keyed with its `fused` column and FDROUTE's `frame=`
  (§2.4), the CLAUDE.md lines and the reader-table restatements (§2.4, R14), Table B's `_Static_assert`
  successors. No seam, no pcrec edit.
- **Sabotage re-aims** `[rev2.2 R9]` (an anchor is a reader of the source text, D94): G2's in-script plants in
  `memfn/tests/run_g2_win.sh` anchor on lines the split restructures: S1423 (:122, `d_hors_head`'s bound line),
  S1427 (:134, `wf_b_walk`'s `wf_member` line), S1428 (:138, `wf_b_pair`'s `two(...)`), S1543 (:159, `wf_raise`'s
  else branch). Each is KEPT VERBATIM where the split moves its line whole into a renderer row, or RE-AIMED in the
  same commit to the line's new text, and the commit lists which. S686 (`tests/mech/sabotages/
  S686_fn_rows_body_order_swapped.sh`, SAB_BEFORE the two `fn_rows` BODY lines verbatim, `ofsskip.c` :419-420)
  moves with the pick column to 3.0b (below).
- **Witnesses**: emit_sweep byte-identical on every arm against its base (Goal 1, §2.6.4); G2 green
  (`run_g2_win.sh`, the finder G2); every form id's hash unchanged and check C's stale count 0; REACH
  EQUALITY, PRES rows included (`[rev2.2 R5]` the new tables print no REACH, §2.6.4); `decider_census.py` green
  with its narrowed backstop and re-pinned HITS/MEMBER_COUNT; `rows_check.py` §R green over (frame, row, ren)
  triples, and §S green; the Goal 4 grep empty; the support pin's derived rows held to base's text by the
  landing-time basis witnesses, recorded in the report (§2.5.2).
- **Heavy runs**: `make test` (normal, boxqueue); emit_sweep per arm.
- **Sabotage rows** (why each goes red):
  - (A) E-find's PAIR search renderer row dropped: formhash's `pair` instance (an E-find window site over
    `{X,x}`, `formhash.c` :444-473) no longer reaches T-FIND's PAIR (`wf_plan_brow` returns `R7w`), so
    `check_hash` refuses the id (:511; `finder_check.py` via `run_finder.sh`). `[rev2 F1]` It is red only
    because `wf_plan_brow` keeps meaning T-FIND's row. (In the product B-pair stops would go to B-walk, and
    B-fn sites would decline too, §2.4's dependency: emit_sweep and G2's fn:48 floor also go red.)
  - (B) `[rev2 F7]` an (E-stmt, PAIR) search renderer row declared with NO arm. `[code review r1 s30a F8]`
    **MEASURED a SILENT MOVE, not a refusal** (this paragraph's earlier text predicted `select_arm`'s refusal
    and "the refusal names row PAIR"; the build does not do that): T-FIND picks PAIR on a composer two-member
    stop, `select_arm` finds no arm and declines, so Table E's legacy-first order sees the composer cannot
    serve the plan's translation, declines E-stmt, and E-find renders the stop as B-pair (a correct, different
    text: `foo|bar\d` moves from (E-stmt, R7w, pf_walk) to (E-find, PAIR, B-pair), rc 0). The DETECTOR is
    `rows_check.py` §R's TRIPLE SET over `renderer_rows.tsv`'s witness lines (the witness prints a triple other
    than its declared one), not a refusal message. Host: §R's in-script plant table (§P, S2983), since no mech
    arm runs `rows_check.py` (a `memfnrows` arm is a plan row). (An arm-bearing plant would render another
    arm's text under PAIR's name: not this row.)
  - (C) the renderability check removed from `fd_holds`. `[code review r1 s30a F8]` **MEASURED a SILENT MOVE**,
    byte-identical to (B)'s: with the gate gone Table E's legacy-first ask declines E-stmt for the same reason,
    and the stop renders as E-find B-pair. F5's false-branch witness is therefore §R's triple compare, not a
    refusal message; detected and hosted as (B) is (§P, S2984). Measured for both (lane s30arev, by hand):
    9 of 60 (pattern, arm) compiles move silently, none refused; inside `rows_check.py` the arm fixture
    `mismatch_inplace` is refused by pcrec under either plant ("the memfn kit's text calls <string.h>
    functions the prologue did not include"), a LOUD side effect off the witness set. `select_arm`'s refusal is kept (§2.4), but the
    legacy-first order above it means no witness reaches it.
  - (D) `[rev2 F28]` `[rev2.2 R4]` a second renderer list planted in an unlisted function, as a COPY of the one
    accessor's loop (holding the search renderer table's name): `decider_census.py`'s narrowed backstop is red.
    (A twin that copies the rows under a NEW name holds no shape: the census's stated limit, "a decider spelled
    in no BACKSTOP shape", `decider_census.py` :38-41.)
  - (K) the support table's SHIFT cell for HORS removed: Table S answers ST-none for HORS on E-find, the
    renderable set drops it and T-FIND never picks it. G2's hors census goes below its floor (`EFIND_FLOORS`
    hors:110), and its control "a dense window renders no D-hors table" fails (`g2_win_gen.c` :693-694).
  - (L) S-restart's text planted as `C += 2`: E-find and `[rev2 F3]` the floor skip candidates, and G2's
    window answers are red against `g2_win_ref.c`. Reach: every non-HORS `[rev2.2 R13]` non-B-fn E-find site (B-fn
    is fused: its function's own loop, `wf_find_expr` :2723 returns before any NEXT) and every floor site (the
    floor reads its stream row, §2.6.0); the plant is S-restart's shared text, so both rows of §2.6.2 carry it.
  - (M) `[rev2 F21]` the support table admits MASK for LIBC: the pin's LIBC row (source: a ruled line) is
    red `[rev2.2 R7]` in `rows_check.py` §S, against `arm_fixtures --streams`' print (this is the ONLY place it
    shows: no 3.0 frame renders MASK, so no text, hash or census moves; MEASURED SAME on every artifact).
    `[code review r1 s30a F14]` Its source is "libc memchr supplies only one-shot", a line of the KIT's notice
    that D190 files among the owner's decision (the owner's own words are the other sentence D190 quotes), so
    this control is a ruled line, not the table read twice, but it shares an author with the table; the pin
    labels it `RULING (D190, kit-stated line)`. Host: §R/§S's in-script plant table (§P, S2988).
  - (N) E-generic's S-restart stream renderer row deleted (`[rev2.2 R13]` E-find's row stays: two rows, one text,
    §2.6.2): the floor has no stream and every floor site is
    REFUSED (§2.6.0). `[rev2 F3]` Reach control: G2's "no-window-search: a DFA_SCAN site not on the floor"
    (`g2_win_gen.c` :689-690) goes red, as do the corpus compile and G2's floor census.
  - (O) `[rev2 F4]` the renderability gate unscoped (applied to slot PRES too): every PRES row (pick
    `FF_UNSTATED`) declines, every pre-check link decision falls to no terminal, and REACH equality on P0-P9
    and emit_sweep on the pre-check composites go red.
  - (P) `[rev2 F2]` B-pair's loop-state slot emptied: `_ha` is undeclared, and the gcc compile of every B-pair
    site (G2's pair:316 census, `a[Xx].b`) fails.
  - (Q) `[rev2 F5]` the libc union taken over the search and stream pieces only: on `--memfn=no-fd-d1 abcdef`
    (B-walk with run compares) `libc` reads 0 and `wf_plan_class` reports `libc_free` 1. `[code review r1 s30a
    F9]` **UNDETECTED, MEASURED** (S2992, `SAB_EXPECT=UNDETECTED`): no byte moves (pcrec's artifact includes
    `<string.h>` itself and its `RX_MEMFN_LIBC` stamp reads `none` both ways), so emit_sweep cannot be red; only
    the trace's ASK `libc_free` moves, and no check reads it (`arm_fixtures --query`'s independent libc reading
    greps `memchr(`/`memcmp(` alone, and the run compare loads words by `memcpy`). The detector this paragraph
    first named does not exist; closing it needs an independent libc reading that counts `memcpy(` over a
    B-walk fixture with a run term.
  - (R) `[rev2 F9, F21]` the support table's PAIR row admits SHIFT as well: on E-find Table S's intersection is
    {RESTART, SHIFT}, ST-many refuses, and every B-pair site is refused (G2's pair census and the corpus go
    red). This also witnesses the two-stream rule and a derived row's basis. `[rev2.2 R3]` The refusal is the
    named ST-many refusal raised after the gate (§2.4), so (R) asserts it by §R's invariant (its message names
    Table S's refusal on the B-pair witness line), never a silent move to B-walk; a build whose gate read
    "exactly one" would move B-pair sites to B-walk with no refusal, and (R) would then be red on the wrong
    observation (emit_sweep, formhash's `pair`), which the invariant's message tells apart. §S is also red (the
    pin's PAIR row says no SHIFT). `[code review r1 s30a F1]` **RE-MODELLED, MEASURED a SILENT MOVE** (lane
    s30arev): the refusal is raised only where Table E answers E-find (after its walk), and Table E's
    legacy-first order then serves the site elsewhere, so no compile is refused and this paragraph's "every
    B-pair site is refused" and "never a silent move" no longer describe the build. `foo|bar\d` (E-stmt) does
    not move; `(?:(?!a)z|w)` moves from B-pair to E-stmt's bounded walk; `(?:(?i:abs)|(?i:ab)S)` (B-fn) and the
    STMT site `a[Xx].b -p rx` move to another form; 12 of 60 hand (pattern, arm) compiles move, rc 0 on all.
    Detectors: formhash's `pair` (tests/memfn/run_finder.sh, the mech row S2993's suite, re-aimed from the
    corpus harness, whose answers a correct other text leaves green), §R's triples on the B-pair and B-fn
    witness lines, and §S.

**3.0b** — the seam, with pcrec's asks, ONE commit.

- `[s1d]` **Re-base on main 35bee4da9** (lane s1design, 2026-11-12; design only). K38-1, K38-2a and K38-2 (main
  7c16349d7) landed after this note's tree, a678d0a4e. Every cite in 3.0b's text was re-read at 35bee4da9; a cite
  that moved is rewritten in place and marked `[s1d]`, and the cites 3.0b reads in §3, §4.1 and §4.2 are in the
  table below. `[r1s1 S1-6]` That held for §3-§5 only: §2.1-§2.3 (3.0b's Content, the D27 author's source) kept
  a678d0a4e's line numbers. Their 35bee4da9 values are now the table's "§2.1-§2.3" rows, and the stale sentences
  (§0 row 1, §2.1's caller paragraph, §2.2 contract line 2, §3's package, §6 ¶1, §7 Q1/Q14/Q15, STATE AT HANDOFF)
  carry a `[r1s1 S1-6]` clause in place. Every prior ruling stands. What moved under 3.0b:
  - **ASK-2 is VOID.** K38-2 deleted its subject: `req_run_member` and its loud check (a678d0a4e's `emit_dfa.c`
    :1058-1076 and :1071-1074) are gone. pcrec no longer cuts a run window. The kit derives the pre-check's one
    run part itself (`window.c` `derive_run_part`) and answers the run decision in `mf_class.run`
    (span_runs_sheet.md §2.2-§2.3). No pcrec ask states a run window, so there is nothing to frame. §2.1's third
    row, §4.2's ASK-2 row and §7 Q1 have no subject left. §6's "ASK-2's existing loud check" no longer exists:
    the unframed-ask rule for row 1 now applies to ASK-6 below.
  - **ASK-6 (new; the letter-style rule: ASK-2 is not reused): the `@` table's cover-row ask states no frame.**
    K38-2 added a pcrec phase-1 caller. `req_run_at` (`emit_dfa.c` :16077, the `<PREFIX>_REQ_RUN` `@` table's
    cover row, commit 2c3b2097e) asks `mf_wdecide` on the cover site (`pcrec_cover_site`) and reads `has_stop`
    and `stop`, the decision group only. Under 3.0b it asks with call NONE and `def` NULL. §2.3's NONE-vs-framed
    equality of the decision group (`[rev2.2 R27]`) leaves `stop` unchanged, so no pcrec byte moves. The same
    function's second reader (`us.wr.run_stated`/`run_member`, :16089-16092; `[r1s1 S1-9]` it also reads
    `us.wr_stated` and `us.wr.pinned`, :16089) and `ofs_test_of`'s
    `run_lo`/`run_len` (:7400-7402) read ASK-1's reply's decision group and are untouched. pcrec's phase-1
    callers are therefore `window_reply_ask` (:7614, ASK-1) and `req_run_at` (:16077, ASK-6). The signature
    change breaks both, so ASK-6 is in the one commit, as ASK-2 was. `[r1s1 S1-2]` §7 Q1's "no frame" does NOT
    cover ASK-6: Q1's reason was that the KIT derives the run part's frame, while the cover site's frame is pcrec's
    (`pcrec_cover_site`, `known.c` :484-509; `emit_cover`, `emit_dfa.c` :14249-14251, defines it with a `stem`, and
    `req_run_at` rebuilds it with `stem` NULL). So 3.0b (a) makes ASK-6's refusal loud, in pcrec's same-commit hunks
    (§4.2's ASK-6 row; main approves it at the GO), and (b) names emit_sweep's cover-route `@` as ASK-6's reach
    witness. The general form is §7 Q16, for main and the kit manager.
  - **Kit-side callers the signature change breaks** (same commit; NONE unless the test asks framed):
    `arm_fixtures.c` :2313, :2320, :2347, :2365; `g2_win_gen.c` :817, :877, :941; NEW since a678d0a4e:
    `tests/memfn/run_decide_check.c` :207 (`wreply`, K38-1; it reads the run fields only, so NONE).
    `docs/dev/lanes/r33_sim/probe.c` :94 is unchanged; see the probe item below. Readers that copy the
    reply (no call): `g2_win_gen.c` :947-948 (`[r1s1 S1-9]` the field-by-field copy into `g2w_reply` is :942-949,
    `alt`..`path`; the frame part's copy is appended after :949), `g2_win_run.c` :99-103, and `g2_win.h` :44-53, the
    copy that grows.
  - **`mf_wreply`'s layout did not move.** K38-2's PLAN item K7 (b) gave the RUN reply one spelling,
    `mf_run_reply`, which is `mf_class.run`'s type. `mf_wreply` keeps `run_stated`..`run_len` and has `path`
    last (`memfn.h` :1583-1598). The frame part is still appended after `path`, and `[rev2.2 R27]`'s
    `offsetof(mf_wreply, framed)` stands.
  - **The decision reads one art fact now.** K38-2a's test-only lever `run-tie-left` is read inside
    `decide` (`kit_run_opts_of(d->art, ...)`, `window.c` :938, :1563). `mf_wdecide` stays pure on a given art.
    The agreement's two halves read the same art, so it holds under the lever. The purity harness's arts
    state no lever, so its "a function of the facts only" now reads "of the facts and the art's lever set".
    Open question (report): add `--harness=run-tie-left` to `reach_equal.py`'s `--arms`.
    `[r1s1 S1-7]` **Cites corrected.** `decide` reads the lever at `window.c` :664 (`a_mass_choose`, Table A's
    choose: it moves the in-run STOP, the field ASK-6 reads) and :938 (`run_member`, through `c_plan`). :1563 is
    `translate`, which `decide` does not reach: the plan function's Table E walk reaches it through
    `e_legacy_holds` (:1623), and so does the define (`wf_prepare`). "One art fact" also undercounts (`decide`
    already read `kit_byte_rate(art)`): the lever makes `mf_lever` the plan face's second art-state WRITER beside
    `mf_define`, stated in §2.2 Purity and Goal 3. G2's k3_inrun window sites already state the lever
    (`g2_win_gen.c` :895-898, :939, :1130): they are the existing lever population, carried by the traced
    window-family pass below (row E's carriers).
    `[r1s1 S1-8]` **The open question is answered NO.** The lever's population is G2's k3_inrun sites (S1-7). A
    `--harness=run-tie-left` arm in `reach_equal.py` would red `tests/compound/run_lever_fence.sh` (c) unless its
    `ALLOW` grew, and it would be vacuous unless the carrier ran `build/pcrec-harness` (plain pcrec refuses
    `--harness=`, so both sides fail every compile). Were the answer ever yes, it states that `ALLOW` growth and the
    harness binary as `--bin`/`--ref-bin`.
  - **MF_SITE_ABI is 27** (25 U2, 26 review r5 X-1, 27 K38-2). If 3.0b lands next it takes **28**. The number is
    the next one at landing, never a literal. **MF_CLASS_V is 9** (K38-2 added `mf_class.run`). 3.0b still does
    not move it.
  - **Sabotage ids** (19 rows: the 18 below plus (AF), §7 Q14 RULED by the kit manager in r13's
    "Rulings on rev 2.2's Q14 and Q15"). The expected S2994-S3012 are taken, see §5's header. K38-2 itself
    took S3040-S3042 and S3060-S3064 from its reserved S3040-S3069 (`[r1s1 S1-6]` and more inside that range: at
    35bee4da9 K38-2 and its fix lanes hold S3040-S3048, S3059-S3064 and S3069; all are below S3078). The highest id on any local branch is S3077
    (lane/rpfix, S3074-S3077, unmerged), and S3070-S3073 are s1fix's reservation. So the 19 rows are
    expected as **S3078-S3096**, in letter order E, E2, F, G, H, I, J, S, T, U, V, X, Y, Z, AA, AB, AC, AD, AF.
    `[r1s1 S1-16]` That expectation holds if 3.0b takes its ids first. If K38-3 lands (or takes its ids) first,
    3.0b's 19 are expected AFTER K38-3's, from the top of the free range then.
    `[r2s1 R30B-3]` If main takes ASK-6's plant as row (AG) (§4.2's ASK-6 row), the rows are 20 and (AG) follows
    (AF): S3078-S3097 on the same expectation.
    The build re-takes them from the top of the free range (the manager's reservation ledger first) and records
    them in its first commit.
  - **3.0a's landing moved cites that 3.0b reads.** `fd_renderers` is gone into `window.c`'s search renderer
    table. `site_rec` already stores the E-stmt search renderer row (`fd_ren`, `kit.h` :242-273), and `select_arm`
    already returns it (`*ren`, `compose.c` :264-297; `kit_legacy_serves` :310-316). So §4.1's E-stmt `search`
    reads `r->fd_ren`'s pick, and the "E-stmt's arm-to-pick map" below needs no second walk.
    `struct wf_plan` (`window.c` :1299-1331, `[r1s1 S1-9]` the struct runs :1299-1341; the members named are at
    :1326-1329) stores `srch`/`fused`/`strm`/`chk`, and the field map's "NEW `wf_plan`
    member, 3.0a" is `strm`. The plan function is `wf_plan_site` (:2321), called from `wf_prepare` (:2403, :2420).
  - **No `wf_part_site`/`wf_parts_prepare` edit.** span_runs_sheet.md §5 Order's contact was ASK-2's row (§2.1)
    only. K38-1 has landed, so 3.0b is the second lander and this re-base is its rebase. The one remaining
    touch is `wf_parts_prepare`'s call of `wf_prepare` (`window.c` :2595). It is unchanged if the allocator
    parameter (`[rev2 F26]`) stays on `wf_plan_site`, with `wf_prepare` passing the art's arena (recommended).
  - **The probe (§7 Q15 (3), RULED in r13: "left to break" REJECTED).** 3.0b adds a successor probe beside the
    census instrument under `docs/design/memfn/span_pick/`, built by its own `build.sh` on the new signature,
    and points the census jobs at it. §3's "LEFT TO BREAK" sentence is superseded by that ruling.
    `[r1s1 S1-3]` **The successor, specified** (the kit's repair: `r33_sim` is the kit's R-33 evidence):
    - **It is broken already.** `r33_sim/probe.c` :36-40 wraps `pcrec_mf_art_begin` with SIX parameters
      (`ar, prefix, policy, denies, ms, an`, a678d0a4e's arity); U2 made it FIVE (`memfn.h` :1425-1426 at 35bee4da9:
      `a, prefix, denies, ms, an`). It compiles clean because its `__wrap_`/`__real_` prototypes are its own, and at
      run time (SysV x86-64, reasoned, not run) it reads its rate-source argument `an` from an unset register and
      drops deny bits 32-63 on the way through. The successor is written against 35bee4da9's (the build tree's)
      `mf_art_begin` arity and 3.0b's `mf_wdecide`.
    - **The jobs.** The in-tree jobs that build the probe are `docs/dev/lanes/r33_sim/240-kit-r33-sweep.sh` and
      `241-kit-r33-rp.sh` (both `bash "$SIM/build.sh" "$TREE" "$S/tb"`, `TREE` a lane worktree, then
      `collect.py --probe "$S/tb/pcrec-r33"`). `span_pick/CLAUDE.md`'s Re-run section names job 240 (the sweep's
      re-maker) and job 488 (S2f's byte-for-byte re-make); J0's job 440 re-made it too. 440 and 488 are boxqueue
      job files, not tree files. 3.0b adds two successor job scripts beside the probe (copies of 240 and 241 whose
      `SIM` points at the successor's directory and whose `TREE` is a stated argument, not a lane worktree), and
      `span_pick/CLAUDE.md`'s Re-run section names them in place of 240; the queue's 440/488 are re-queued from them
      by whoever next re-makes the sweep.
    - **The call: NONE**, `def` NULL (recommended and taken: the JSONL stays byte-equal, which job 488's
      byte-for-byte compare needs). The `wr` object keeps exactly today's keys: `rc`, then on rc 0 `alt`, `reseed`,
      `has_stop`, `stop`, `stop_set`, `plan` (`[off, term]` pairs), `pinned`, `run_stated`, `run_member`, `run_lo`,
      `run_len`, `path`; every other record the probe prints is unchanged. A DEFINE ask (the frame part, which
      census0 could read) is a later census question, not 3.0b's.
    - **A compile-only prototype check.** The successor's wrappers declare their parameter lists by
      `__typeof__(pcrec_mf_art_begin)` (and likewise `pcrec_mf_define`/`pcrec_mf_emit`), so a seam move fails its
      build, not its data; and `tests/memfn/run_link_checks.sh` (C15/C16, which already compiles every `memfn/src`
      file) gains one `gcc -fsyntax-only` line over the successor probe, so the next MF_SITE_ABI event reds a
      checked build instead of a census run. §3's reader list names the probe as this out-of-build caller.
    - **`collect.py`'s home.** `collect.py` (the probe's record parser) is COPIED beside the successor, so the
      kit-owned probe does not lean on a historical lane file; `r33_sim/` stays as the lane left it (historical).
      `[r2s1 R30B-6]` **The whole job set moves, not `collect.py` alone.** Jobs 240 and 241 call three files from
      `$SIM`: `build.sh` (240/241 :28), `collect.py` (:29) and `sim.py` (240 :32, 241 :31). `build.sh` IS the probe's
      build: it links `"$here/probe.c"` (`r33_sim/build.sh` :8, :12) with the `--wrap` set, so a copied job whose
      `SIM` points at the successor finds no `build.sh` there, and one whose `SIM` stays at `r33_sim` compiles the
      OLD, broken probe. So the successor directory holds four files: the successor `probe.c`, a copy of `build.sh`
      (its `here` then names the successor's `probe.c`), `collect.py` and `sim.py`. Both Python files import the
      standard library only (`sim.py` reads its argument files and the `.rates.json` beside them, which `collect.py`
      writes), so nothing else under `r33_sim/` is read. The successor jobs keep the originals' `|| exit 1` after each
      step, so a missing file fails the job loudly rather than reading the old directory.
    - **PLAN (main's):** check whether any census sweep run since U2's landing used the broken probe; if one did,
      its per-art rate tables are suspect and the census outputs built on it (`census0.out`, `census0_cards.out`)
      are re-made from the successor.
  - **The §3 / §4 cites 3.0b reads, at 35bee4da9:**

    | where | a678d0a4e | 35bee4da9 |
    |---|---|---|
    | `[r1s1 S1-6]` §2.1 the callers | `emit_dfa.c` :1068, :7610 | :7614 (ASK-1) and :16077 (ASK-6, `req_run_at` :16050) |
    | `[r1s1 S1-6]` §2.1 row 1 | `window_reply_ask` :7604-7616, asked at :4792; `next_keys` :7298-7306, :7317-7321; offset rows :10471-10500; `ofs_test_of` :7402-7412; `pf_site_of` :7131-7146; `ofs_site_define` :7622-7642 | :7608-7620, asked at :4743; :7277, read :7297-7299; :10537-10563; :7381; :7109; :7626-7646 |
    | `[r1s1 S1-6]` §2.1 define-only scenarios | `find_site` :6922-6936; `pcrec_cover_site` `known.c` :488-496; `cand_ask` :8352 | :6878; `known.c` :484-509; :8344 |
    | `[r1s1 S1-6]` §2.2 | `mf_wdecide`'s memset `window.c` :1224; `wf_check(site, 0)` :1226; heap comment :1229-1232; `walk_row`'s option read `compose.c` :170-171; `cl_miss` `gate.c` :648-656 | :1281; :1284; :1286-1287; :171; :673-679 |
    | `[r1s1 S1-6]` §2.2 allocation | `wf_find_decide` :1846; `build_runs` :1673-1683; `wf_prepare` :1900-1906 | :2245-2248 (in `wf_find_decide` :2222); :1742-1754; :2411-2417 (and `why_room` :2303-2308, S1-5) |
    | `[r1s1 S1-6]` §2.3 | `mf_wreply` `memfn.h` :1467-1482; T-FRAME ids `window.c` :1616-1621; `mf_result.row` `compose.c` :1316; `offer_at` :1281-1290, read :1314; `wf_crows` :1051-1092; `c_stop` :999-1002; `c_plan` :1096; B-walk's stop test :2553; `wf_member_of` :2159-2166; `d_hors_head` :2642-2656; `ofs_fn_serves` `ofsskip.c` :482-493 | :1583-1598; :1671-1672, names :2189-2190; :1296, :1357; :1345, read :1378; table :1112; :1054; :1153; :3124; :2709; :3217; :477 |
    | §3 the definition | `memfn.h` :39-204 | :39-243 (entries 25-27 added) |
    | §3 current-number prose | `memfn/include/CLAUDE.md` :4 "24" | :4 still reads `MF_SITE_ABI` 25 and `MF_CLASS_V` 8: STALE (the values are 27 and 9). 3.0b's line rewrites it to the new number and 9 |
    | §3 symbolic readers | as listed | `memfn_sites.c` :459; `compose.c` :1036, :1093-1095; `window.c` :1283, :1483; `presence.c` :271; `formhash.c` :383; `g2_gen.c` :935, :2271, :2306, :3806, :3842, :3886, :4252, :4482-4483; `g2_simd_gen.c` :340; `g2_win_gen.c` :702, :812, :873, :922; `arm_fixtures.c` :247; `mass_check.c` :267; `proof_check.c` :164; `proven_check.c` :63; NEW files `g2_pres_gen.c`, `tests/memfn/policy_check.c`, `tests/memfn/run_decide_check.c` (recompile only) |
    | §3 historical class | 304 lines, 71 files | 354 lines in 79 files (same grep, ledgers, `docs/design`, history, lanes and reviews excluded). S2903's anchor (`compose.c` :898's text) and S1089's are unchanged |
    | §3 MF_CLASS_V readers | `memfn.h` :1080 ... | `memfn.h` :1155, `window.c` :3352, `compose.c` :367, :1054, `proof_check.c` :415, `arm_fixtures.c` :417, plus the two CLAUDE.md lines |
    | §3 `pur_diff`, control print | `arm_fixtures.c` :2204-2220, :2328-2336 | :2246-2262, :2370-2378 |
    | §3 `PURITY_FLOOR` | `run_finder.sh` :132 (read :138), header :121-131 | :158 (read :164), header :147-157; still 1157 |
    | §3 harness description | `tests/memfn/CLAUDE.md` :43 | :45 (`run_purity_reach.sh` :27-37, :41-74, `g2_win.h` :44-53, `trace_format.md` :102-113 unchanged) |
    | §3 comments restated | `memfn.h` :556-558, :1435-1441, :1483-1486; `window.c` :49, :1225; `emit_dfa.c` :7598-7603 | `memfn.h` :605-607, :1551-1557, :1599-1602; `window.c` :51, :1282; `emit_dfa.c` :7602-7607 |
    | §3 [SEAM-READER-CENSUS] | `plan.md` :1844 | the row [SEAM-READER-CENSUS], unchanged (STATE:not-started) |
    | §4.1 stored members | `kit.h` :239-270; `window.c` :1242-1274, `wf_prepare` :1892, stores :1947-1950 | `kit.h` :242-273; `window.c` :1299-1331, :2403, :2424-2427 |
    | §4.1 rule 2's re-ask; the arm walk | `compose.c` :1180-1200; :295-327, :333-339; :277-283 | :1221-1241 (it re-asks through `ask_sel`); `select_arm` :264-297, `kit_legacy_serves` :310-316; `fd_renderers` deleted (3.0a) |
    | §4.2 ASK-1, ASK-3, ASK-5 | `ofs_site_define` :7622-7642; `cand_asked_hold` :7066-7085; `wr` comment :4630-4636 | :7626-7646; :7044-7063; :4582-4588. ASK-5's restatement of the `wr` comment also names `req_run_at` among its readers (K38-2) |
    | §4.2 ASK-4 suites | `run_cand_oracle.sh` :90, `run_fallback_table.sh` :143 | unchanged |

- **Content**: §2.2-§2.3; `reply_of`'s frame part; the define's record of what it rendered (§4.1); the kit's
  MF_TRACE agreement at every window-site define: the plan re-asked with the define's site, hooks and
  call, every field compared (`memcmp` of the whole reply) `[rev2 F29]` `[rev2.2 R1]` against a define-side reply
  whose FRAME part is built from what the define STORED by §4.1's field map (never through `reply_of` or the
  plan function) and whose decision group is re-derived through `decide` (§4.1, "The agreement's two halves"),
  as rule 2's re-ask re-runs `select_arm` against the stored `r->cls` (`compose.c` :1180-1186; `[s1d]` :1221-1227, through `ask_sel`); `[rev2.2 R8]` the
  frame-part outputs moved from 3.0a (`fused`, `plan_test`, `stop_test`, the reply ids, E-func's `search` with
  the `fn_rows` pick column, E-stmt's arm-to-pick map, the allocator) and S686's re-aim onto the BODY lines' new
  text `[rev2.2 R9]`; ASK-1..ASK-5 (`[s1d]` ASK-2 VOID; ASK-6 added, see the re-base block); the purity harness (framed
  asks interleaved with defines, the whole-reply `memcmp`, the hex-dump control print, the counting hook over
  six stated callbacks, the counting arena, the same-class-different-text fixture,
  `PURITY_FLOOR` re-pinned, `purity_rows.tsv`'s rows; `[r1s1 S1-5]` the counting arena's population adds one framed
  ask whose T-FIND picks PAIR, reaching `wf_find_decide`'s allocation, and one REFUSED framed ask, reaching
  `why_room` (row (I)'s REPORT site under `no-window-search` already builds one), each COUNTED, a count of 0 a named
  failure: at 35bee4da9 no purity site reaches either (every `table=fd` reach reads `asked=0`, and all 89 Table E
  selections are chosen); `[r1s1 S1-1]` **a TRACED purity pass**: `run_finder.sh` also runs `"$WORK/fxt" --purity`,
  the MF_TRACE fixture driver it already builds, beside the plain `fx` run, so the kit's agreement check runs at
  every purity define (at 35bee4da9 a traced `--purity` passes 1157 checks and carries 89 whole-site window
  defines, 81 E-func and 8 E-generic); `[r2s1 R30B-1]` **the traced pass's rule and its counted population**: it is
  held to the plain pass's rule (rc 0, or a `FAIL` line; and `checks passed == PURITY_FLOOR`, the same driver, so
  the same floor, `run_finder.sh`'s plain purity block), and it COUNTS its whole-site window defines per frame from
  its own MFTRACE stderr: the `MFTRACE END table=wfE ... phase=define chosen=<row>` lines (`trace_format.md`'s END
  record; that count gave 81 `chosen=E-func` and 8 `chosen=E-generic` at 35bee4da9). The two counts are pinned
  EXACT at the build's measured values (a fixture population, as `PURITY_FLOOR` is; 3.0b's framed asks move them,
  so the build pins them after its harness growth), and an E-func count of 0 is a named failure ("E and E2 have no
  traced carrier"), never a re-pin. **Its control:** a change that takes the purity sites off E-func WITHOUT a
  refusal (the K35 shape the count exists for). The purity checks compare an art with a fresh art on the same
  facts, so a selection that moves on both sides moves no check, and `checks passed` is unchanged; only the E-func
  count reds. The build plants it as Table E's E-func row declined (`wf_erows[E_FUNC]`'s `holds` answering 0,
  `window.c` :1687) and records the result; if that plant makes the purity defines REFUSE (the sticky err then reds
  purity itself, which is not this control), it uses a fixture edit that states the purity sites' frame as
  STMT/ASSIGN instead, and names which in its report. And **a
  TRACED window-family pass**: `run_g2.sh` runs `run_g2_win.sh` once
  more against `libpcrec_mftrace.a` (`mk_mftrace_lib.sh`, which `run_g2.sh` already builds for its rows half;
  `[r2s1 R30B-2]` **corrected**: the MAKEFILE builds it, `$(BUILD_DIR)/libpcrec_mftrace.a` through
  `mk_mftrace_lib.sh`, a prerequisite of `test-memfn-g2` and `test-memfn-g2-full`; `run_g2.sh` only reads it and
  exits 2 when it is missing, so a run outside make, and the pass's own `--plant` path, build it themselves), its
  plant path's `kit_objs` compiling `-DMF_TRACE` for that pass, so G2's E-find, E-generic, E-stmt and k3_inrun
  lever sites carry the agreement; its runtime is measured at the build and stated in the report, and if it does
  not fit `make test-memfn-g2`'s budget it runs in `make test-memfn-g2-full` only, the traced purity pass staying
  E/E2's standing carrier; `[r2s1 R30B-2]` **run green first**: no MF_TRACE kit has defined G2's window family before
  (`run_g2.sh` :1038 runs it against the plain library), so the kit's EXISTING traced checks (rule 2's re-ask,
  `compose.c` :1221-1241, and the other MF_TRACE-only checks) meet G2's window sites for the first time in this pass.
  The build runs the pass on its base tree BEFORE 3.0b's own agreement is added; a red from a pre-3.0b traced check
  is a finding, filed and dispositioned before the pass is claimed as a carrier of (E)/(E2); `[r1s1 S1-2]` ASK-6's loud refusal (§4.2, main approves at the GO); the `mf_wcall` fixtures `[rev2 F33]`; G2's window
  generator asking framed in the frame each site is defined in, with the (frame_row, stream) cell tally
  (floors at measured less ~10%, impossible cells 0: `[rev2.2 R26]` SHIFT outside E-find; on E-generic anything
  but RESTART; on E-func and E-stmt anything but RESTART (a fused row or a PF arm) or NONE (ARM); MASK anywhere
  `[rev2.2 R24]`; and on every framed ask `stream` NONE iff `fused` ARM, so §2.3's ARM rule and the tally
  cannot answer one cell twice), the text classes per E-find site (§2.3's observable meanings `[rev2.2 R18]`:
  `fused` FN iff the text calls `_ofsskip`; `search`/`method` against the text: PAIR iff the two `memchr`
  frontiers, HORS iff `_sh[256]`, LIBC/LIBC_BACK iff one `memchr`, WALK iff a walk; `frame_row` E-find iff
  `form_id` "window-search", E-generic iff "wf-floor"), `[rev2.2 R2]` the `table_name` population for
  `plan_test` and `stop_test`: the marker is the hook's OWN spelling, `g2w_t<id>_<ref>[` (`h_table_name`,
  `g2_win_gen.c` :569-574; G2 already searches it, :1065; `[s1d]` :641-646 and :1152), matched to each tested OFFSET through the ref G2
  itself offered there (TABLE iff that ref's marker is read, OWN iff not, with §2.3's exceptions); the
  population includes a site whose stop lies BELOW a TABLE plan position (where the define's `off[]` and
  `plan[]` indices differ) and a stated hook with NO offer (OWN expected); `[r1s1 S1-4]` beside those two named
  members the class PRINTS and FLOORS a third, "B-walk sites whose stop marker is read" (row AF's population: 24 at
  seed 20261022 / 1500 sites at 35bee4da9, every one reached; floored at the measured count less ~10%, like G2's
  other cells, a count of 0 a named failure), so a generator change cannot empty AF's population behind the whole
  class's floor, which AB's sites alone can fill; the reply-id resolution check with
  exact emptiness (Goal 5); §3's package. `[rev2.2 R20]` Optional (noted, r13 R20): a reached-ask control beside
  the counting hook's 0, rc 0 and `framed` 1 with the expected `frame_row` once per frame. **A D27 spec-first author** `[rev2]`
  (accepted in r12's rulings) writes the seam-contract tests (`mf_wdecide`, `mf_wcall`, `mf_wreply`'s frame
  part) from §2.2-§2.3 alone, in a cell, at 3.0b's build; the build lane's tests do not replace them.
- **Witnesses**: as 3.0a, plus the two agreement checks green on the corpus and on G2 (`[r1s1 S1-1]` the kit's
  check runs only in an MF_TRACE kit: on G2 through the TRACED window-family pass above, since G2's standing window
  family links the PLAIN library, `run_g2.sh` :1038 `LIB="$plainlib"`, `run_g2_win.sh` :294; and on the fixtures
  through the traced `fxt --purity` pass) `[rev2.2 R19]` (OFF layer
  only: G2's window generator is MF_P_PORTABLE_ONLY throughout, `g2_win_gen.c` :639 .. :1042 (`[s1d]` U2 retired that
  bit: every G2 window art now states the portable target, `g2_art_begin`, `g2_win_gen.c` :111-118), and `g2_simd_gen.c`
  states no window facts, so G2 has no SIMD window population). The kit agreement's CORPUS carrier is named:
  `make test` builds the kit without MF_TRACE, so it is `tests/memfn/reach_equal.py` (the one corpus compile
  through an `-DMF_TRACE` pcrec) with `--arms` including the default and `-fmemfn-simd`, a boxqueue job; its red is
  a change in the set of failing patterns per arm (an agreement failure refuses that compile). This is the one
  population where the SIMD gap (§2.3) lives; it is recommended over "the SIMD agreement unchecked until
  RUNG-LIST" (§7 Q15). Purity green at its new count; the counting hook and the arena at 0; the D27 author's tests
  green. `[r1s1 S1-2]` ASK-6's reach: emit_sweep byte-identical on the cover-routed `<PREFIX>_REQ_RUN` `@` stamps
  (a refused or `has_stop`-0 ASK-6 drops the `@`, a byte move); under 3.0b a refusal also fails the compile.
  `[r2s1 R30B-3]` The loud refusal's own plant (`call` 0, §4.2's ASK-6 row) is red by the compile's internal-error
  text naming ASK-6's refusal, as row (AG) or as a once-run control (main's choice at the GO).
  `[r2s1 R30B-1]` The traced purity pass green by the plain pass's rule, with its E-func and E-generic define counts
  at their pins (E-func never 0). `[r2s1 R30B-2]` The traced window-family pass shown green on the base tree first.
- **Heavy runs**: `make test` (normal, boxqueue); emit_sweep per arm; the ASK-4 suite; `[rev2.2 R19]`
  `reach_equal.py` under the MF_TRACE kit, both layers (boxqueue).
- **Sabotage rows**:
  - (E) `reply_of` writes the frame row of another walk (plant: always `E-generic`): the kit's MF_TRACE
    agreement at the define is red (`run_finder.sh` and G2's MF_TRACE kit, `mk_mftrace_lib.sh`). `[r1s1 S1-1]`
    **Detector corrected**: at 35bee4da9 neither named carrier runs a window-family define through an MF_TRACE kit
    (the window family links the plain library; `run_finder.sh` runs `--purity` on the plain `fx`, :159, and its
    traced `fxt` defines only pre-check PARTS). The row's detector is the traced `"$WORK/fxt" --purity` pass
    (§5 3.0b Content: its 81 E-func defines are red under the plant), with the traced window-family pass as G2's
    second carrier. (E2) inherits both. `[r2s1 R30B-1]` The pass's counted E-func population (§5 3.0b Content)
    keeps this detector from emptying silently: a fixture change that takes the purity sites off E-func reds the
    count, not this row.
  - (E2) `[rev2 F29]` the plan function's frame part reports `E-generic` where E-func renders (a fault that
    moves no text): the agreement is red, because its define side's FRAME part is the stored record (`[rev2.2 R1]`
    §4.1's map: E-func's `frame_row` from `wplan == NULL` and the stored FUNC site). (If it were SAME, the frame
    part's define side would share the plan function's source: the build must show it red.) The plant lands in
    the plan function's frame-part half; a plant in its decision half is not this row's (that half is re-derived
    on both sides, and emit_sweep sees a consistent decision fault).
  - (F) pcrec-side: ASK-1's ask states STMT/ASSIGN. E-stmt is not E-func, so ASK-3's check is red on every DFA
    prefilter site the ASK-4 suite compiles (`[rev2.2 R19]` held: `run_cand_oracle.sh`'s witness lines cover all
    four offset rows). `[rev2.2 R17]` The row asserts the failure TEXT names ASK-3's invariant
    ("asked-plan-differs"), not "the suite is red": a STMT/ASSIGN framed ask may instead be refused at phase 1,
    which `window_reply_ask` turns into its own internal error (`emit_dfa.c` :7610-7613, `[s1d]` :7614-7617, "refused the window
    family's phase-1 ask"), and that red proves nothing about ASK-3's reach.
  - (G) the plan face calls `table_name` once: the counting hook reads 1 (`arm_fixtures --purity`).
  - (H) `[rev2 F32]` the reply's `fused` keyed on `art->nsites` (FN iff `nsites > 0`, 1d's plant pattern):
    purity is red and its hex-dump control moves. With the whole-reply `memcmp`, one plant covers every member
    present and future.
  - (I) `[rev2.2 R16]` a framed ask walks with the SITE's `opts` cleared (the plan function's walks get a site
    copy that drops `opts`; the art's denies mask is already 0 on Table E's walk, §2.2, so rev 2.1's "without the
    art's denies" planted nothing): the fixture "framed ask on a REPORT site under `no-window-search` answers -1,
    as `mf_define` refuses" is red (`arm_fixtures`). The same plant reddens a second fixture on a T-FIND deny,
    `--memfn=no-fd-d1`: the framed ask's `method`/`search` equal the define's (T-FIND's table reads `fd-*` from
    the same `opts`, `fd_opt`, `finder.c` :514-516, `[s1d]` :521-523).
  - (J) a reply's `method` filled from `search`'s spelling (e.g. `PAIR` where T-FIND's row was `R7w`'s walk):
    the id-resolution and text-class checks are red.
  - (S) `[rev2 F33]` UNSTATED treated as NONE: the fixture "call 0 answers -1" is red.
  - (T) `[rev2 F33]` NONE answers a frame part (`framed` 1): the fixture comparing NONE's frame part to zero
    (`memcmp`) is red.
  - (U) `[rev2 F33]` EMIT walks Table E under DEFINE only: the fixture on a site where `mf_emit` and
    `mf_define` select different rows (the gate's DEFINE|USE declining a row whose use-time fields the hooks
    fail, `compose.c` :255-258, `[s1d]` :255-261, `select_arm`'s comment) answers `mf_define`'s row and is red.
  - (V) `[rev2 F34]` the plan face calls `member` (or `on_cand`): the counting hook, now stating all six, reads
    1.
  - (X) `[rev2 F30]` `reply_of` writes MASK `[rev2.2 R24]` for one frame: G2's impossible-cell assertion (MASK 0) is
    red, which shows the tally reads the field.
  - (Y) `[rev2 F31]` E-find's `method` reported `R7w` for a PAIR stop: both ids resolve, the bytes are SAME,
    and G2's text class (the two `memchr` frontiers) is red.
  - (Z) `[rev2 F31]` `fused` left NO on B-fn: G2's class (the text calls `_ofsskip`) is red.
  - (AA) `[rev2 F31]` `frame_row` swapped E-find <-> E-generic on REPORT sites: G2's `form_id` class is red.
  - (AB) `[rev2 F12]` `plan_test` always OWN: G2's `table_name` population `[rev2.2 R2]` (the hook's own marker
    `g2w_t<id>_<ref>[` matched by offset; the stop-below-a-TABLE-position site and the stated-hook-no-offer site
    included) is red. `stop_test` has no plant of its own among the 18 (§7 Q14). `[r1s1 S1-6]` Its plant is (AF).
  - (AF) `[s1d]` (§7 Q14, RULED in r13: "add sabotage row AF (3.0b becomes 19 rows)"; the row text is Q14's)
    `stop_test` always OWN while `plan_test` is right: G2's `table_name` class is red on its B-walk sites whose
    stop alone is offered (the one search that member-tests the stop through the table, §7 Q14). `[r1s1 S1-4]` Its
    population is the counted, floored G2 tally "B-walk sites whose stop marker is read" (24 at 35bee4da9, §5 3.0b
    Content); 3 non-B-walk E-find sites also read the stop's marker, so AF's red is not B-walk-only.
    `[r2s1 R30B-9]` **Their path and the class rule there.** B-walk's FIND is the one search whose find member-tests
    the stop (Q14's premise, which is about the find and stands). A non-B-walk E-find text reads the stop's marker
    only where the stop's offset stays in `plan[]` (inside a pinned stretch: `c_stop` drops it otherwise, `window.c`
    :1054-1056), through the candidate test (`wf_test_to`, :2797, member-testing every plan position) or B-hors's
    probe (`d_hors_head`, :3217, when `hl` is the stop's offset). G2's class asserts there what it asserts
    everywhere: by OFFSET, `stop_test` TABLE iff the hook's marker for the ref G2 offered at the stop's offset is
    read, OWN iff not. So a correct build is green there and AF's plant (`stop_test` OWN) is red there too. The 3
    sites' search and their stop-in-`plan[]` state were not recomputed in this text pass (no G2 run under the
    evening hold); the build's first G2 run prints them, and the report records which path each takes. If any of
    them reads the marker by another path, that is a finding against §2.3, not a re-pin.
  - (AC) `[rev2 F26]` `mf_wdecide` hands the plan function the art's arena: the counting arena reads > 0.
    `[r1s1 S1-5]` Its population includes the PAIR-picking framed ask and the refused framed ask (§5 3.0b Content),
    each counted, so a build that threads the parameter but leaves `wf_find_decide`'s or `why_room`'s allocation on
    `art->a` is red here too, not only the hand-off.
  - (AD) `[rev2 F16]` a gate reads a hook's text beyond its class (e.g. compares `n`'s spelling): the
    same-class-different-text fixture is red. `[rev2.2 R21]` Its POPULATION is STMT/ASSIGN and STMT/ON_MISS sites
    asked with call EMIT (the window rows read the text hooks at USE only, `wf_floor_uses`, `window.c`
    :2838-2846, `[s1d]` :3409-3417; the purity harness's 11 FUNC/RETURN DEFINE sites state no text hook, so they vary nothing), with
    every text hook stated (`s`, `n`, `lo`, `floor`, `result`, `on_miss`, `miss`), each replaced by a same-class
    text RELATION-PRESERVINGLY (`n` -> `len` renames any `miss` equal to it too; `result` -> `r2`; a `miss` token
    vs a `((size_t)-1)` text), plus the `MF_MISS_N` by-address case (`gate.c` :648-653, `[s1d]` :673-678) and ONE case where the
    rename breaks the `miss`/`n` relation and the class DOES move (asserted as a class move, where the fixture
    then permits the reply to differ), so a correct build is not red on a legitimate class change.
  - (AG) `[r2s1 R30B-3]` (main's choice at the GO: this row, or the same plant as a once-run control) pcrec-side:
    ASK-6 (`req_run_at`'s cover-row ask) passes `call` 0 (UNSTATED) where it should pass NONE. The kit refuses
    (row S's rule), and 3.0b's loud hunk fails every cover-routed compile (`foo[0-9]{4}bar`, `abcdef`, `a{6}b`).
    The row asserts the failure TEXT names ASK-6's refusal, as row (F) asserts ASK-3's, not "the suite is red":
    without the loud hunk the same plant drops the cover `@` with no failed compile, so only the new check makes
    this text. Its suite is one that compiles a cover-routed pattern (the build names it; a mech row's suite
    must run on the sabotaged tree's `build/pcrec`).

**Separability.** 3.0a lands and reverts alone: it moves no seam and touches no pcrec file. 3.0b needs
3.0a, because the frame part comes from 3.0a's plan function, so reverting 3.0a after 3.0b takes 3.0b
with it. 3.0b cannot be split: the signature change breaks pcrec's build without ASK-1/ASK-2 (`[s1d]`
ASK-1/ASK-6: ASK-2's caller is gone, `req_run_at` is the new one). The
MF_SITE_ABI event, its callers and its checks are one commit (memfn/CLAUDE.md's same-commit rule).
`[rev2.2 R8]` The separability is exact because 3.0a ships no computed-but-unread output: everything its plan
function computes, the define renders. Inside 3.0a, the split (§2.6) and the asker's retirement (§2.4) can be
two commits (or one). `[rev2.2 R12]` **Commit 1** = §2.5.2-§2.5.3 + §2.6: the support table, Table S, and the
skeleton, search, stream, check and fused rows (the split reads Table S to pick E-find's and the floor's stream
row, so Table S is commit 1's); `SF_ASKER_PAIR`, `renders_pair` and `fd_renderers` stay untouched. Its sabotage
rows: (L), (N), (P), (Q). **Commit 2** = §2.4: the renderable set in `fd_holds` (slot FIND), the ST-many refusal,
the E-stmt rows moved into the search renderer table, the deletions. Its rows: (A), (B), (C), (D), (K), (M), (O),
(R). Byte identity and REACH equality re-run on BOTH commits. Both are in one unit because the renderable set
reads Table S, which reads the stream renderer table.

**Concurrency and remodel overlap (D153).** The target seam's U2 edits `formhash.c`'s entry table and the
`FLD_policy` gate field, and retires `MF_P_PORTABLE_ONLY` readers including `finder.c` :176's contract
macro (a 3.0a file: one extra contact, r12 PROBED). 3.0a edits `finder.c`, `window.c`, `compose.c`
and `kit.h` (`[rev2.2 R8]` `ofsskip.c`'s `fn_rows` fact column is now 3.0b's), and only comments in `formhash.c`. The overlap is low:
the later lander re-merges and re-runs the hash witness. `[rev2.1 Q13]` The rung list is not in 3.0b, so it adds no overlap; plan row RUNG-LIST (§7) names U2+U3 as the place its admission fact will come from. Either way the second lander takes the next MF_SITE_ABI number and
re-baselines. Opt rows on `window.c`, `finder.c`, `compose.c` or `ofsskip.c` wait for 3.0b, as stage 1's did.
`[s1d]` Both seam events have now landed ahead of 3.0b: U2 (MF_SITE_ABI 25, then 26) and K38-2 (27). 3.0b is the
second lander against each, so it takes the next number (28 at 35bee4da9) and its base is main's tip at
branch time. With 3.0a landed, the next lander after 3.0b on these files is span_runs_sheet.md's K38-3, which
touches none of them. `[r1s1 S1-16]` Disjoint CODE files, not disjoint files: both units add mech rows and so both
regenerate `tests/ci/cloud_mech_shards.tsv` (generated by `cloud_units_plan.py mech`; K38-2's `[k382cm]` FATE note
records the skew a stale table caused), both append to the kit ledgers (`memfn/docs/journal.md`, `responses.md`),
and both edit `memfn/tests/CLAUDE.md`. Whichever lands second regenerates the shard table and rebases those three
hands; 3.0b's expected ids follow K38-3's if K38-3 takes its ids first (the re-base block's ids bullet).
3.0a does not touch `vrun.c` (§2.7).

**Size.** 3.0a: M (one table rekeyed, Table B split into skeleton, search, stream and check rows plus fused
rows, one new fact table and Table S, one function split; no text moves; `[rev2.2 R8]` smaller than rev 2.1's:
the `fn_rows` column and the reply-only outputs moved to 3.0b). 3.0b: `[rev2]` L (the seam with `plan_test`
`[rev2.2]` and `stop_test`, the reply-only plan outputs and the `fn_rows` fact column, about 14 readers, two
checks with §4.1's field map, the harness growth, `[rev2.2 R22]` 18 sabotage rows (`[s1d]` 19 with (AF), Q14 RULED), the D27 author's tests; `[s1d]` plus ASK-6 and the
successor probe, minus ASK-2; `[r1s1 S1-1..S1-5]` plus ASK-6's loud refusal, the traced purity and window-family
passes, two counted arena cases, AF's floored tally and the specified probe with its compile-only check;
`[r2s1]` plus the traced purity pass's pinned per-frame counts, ASK-6's plant (row (AG) or a control), and the
successor's four-file job set).

## 6. What 3.0 leaves to row 1 `[rev2 F15]` `[rev2.1 Q13]`

**Left wholly to row 1** (`span_pick.md` :409-410): every T-PICK row, and any frame-DEPENDENT decision
(KEY and M meeting in T-PICK). With it goes the rule for unframed asks: a row that makes the decision read
the frame must decline on NONE asks, or define their answer. Otherwise `req_run_member`'s member and the
part's define could disagree, and ASK-2's existing loud check (`emit_dfa.c` :1071-1074) would fire.
`[r1s1 S1-6, S1-2]` **At 35bee4da9 that check is gone** (K38-2 deleted `req_run_member`), and the rule's NONE ask
is now ASK-6, which maps `stop` into the `<PREFIX>_REQ_RUN` `@` stamp (match_api.md §6.3.7). Under 3.0b a refused
ASK-6 fails the compile (§4.2), and emit_sweep's byte identity holds the `@` while no byte moves on purpose. Once
row 1 moves bytes on purpose, a frame-dependent row that declines a NONE ask leaves `has_stop` 0 and drops the
`@` with no refusal, and the literal `@` checkers deny the cover route; so row 1's first frame-dependent row is
§7 Q16's trigger, and its general form (the ask states the define's frame, one trace-build compare) is the
detector.
Also row 1's: the method-level tie row (R19); verify priced over T-VERIFY's step list (R21); finder_check
L's digest masking (`[sp1g review F5]`); the DEFAULTS reader; the pre-check-part statement (§The pick 7);
M2; the movers census; a stream choice wherever a search supports two streams on one frame (Table S's
ST-many, `[rev2 F9]`, needs that evidence row). 3.0 builds nothing for them beyond the frame part.

**RULED (Frank, 2026-11-07): row 1 waits for an inline one-member finder and its measurement card.** The
finder is a new SEARCH piece: a T-FIND row, a search renderer row and its card (memory
`pcrec-new-method-needs-measurement-card`), in its own unit before row 1. The census0 decomposition
`memfn/docs/ideas.md` :785 names is the trigger for that unit's design. It inherits §2.5.5's NOTE: if its
form is word-at-a-time or vector, it supports RESTART and MASK, that unit builds the first MASK stream
renderer row, and it must bring the evidence row ST-many needs. This note does not design the finder.

**Why the triple is the control** (Frank 2026-11-07: "speed compare should remove variables. Apples to
apples"). smp20's watched comparison (`span_pick/smp20.out`, `memfn/docs/ideas.md` :780-785) sets
`{X,x}`@0 by PAIR against `'/'`@1 by libc memchr. As triples these are (PAIR, RESTART, plan at @0) and
(LIBC, RESTART, plan at @1): the search differs, and so do the stop position, the set and the check that
follows the stop. Within the search, inline vs call and own code vs libc also differ, all at once. With the
triple in the reply and the trace, every comparison names which pieces differ.

**The controlled comparisons row 1 runs.** `[rev2 F15]` Each states every FIXED piece, the
layer and the target included, and names whatever else necessarily moves with the varied piece. The cells
are forced by test-only levers (`mf_lever`, R-30; no public deny for a lever, memory
`pcrec-flag-follows-caller-effect`), so each effect is measured, not inferred. `[rev2.1 Q13]` A SIMD-on cell is NOT
compared before plan row RUNG-LIST: the reply names the OFF triple only (the gap, §2.3), and that row's
trigger is `[rev2.2 R28]` "row 1 compares a SIMD-on cell, or the first MASK stream RENDERER ROW lands".

| comparison | varied | fixed | example cells | what else moves (stated in the record) |
|---|---|---|---|---|
| SEARCH | the search | the stream (RESTART), the check (T-VERIFY's plan), the frame, the stop, the site, layer OFF, target generic | `'/'`@1: the inline one-member finder vs walk (ONE variable) | libc memchr vs either of them also varies the call boundary and own code vs the library: a BUNDLE of three, named as one. HORS can never be a single-piece SEARCH cell: its support is {SHIFT} only and its stop is the probe of the window's last position (`d_hors_head`, `window.c` :2642), so search, stream and stop move together |
| STREAM | the stream | the search (one that supports both streams: the inline one-member finder if it is word or vector), the check, the frame, the stop, the site, layer, target | `'/'`@1: the inline one-member finder RESTART vs MASK | SUSPECTED: under MASK the check may become the mask-trimmed one (§2.7's TRIM); for a one-member stop it reduces to C-stop. Confirmed in the finder's unit when it designs its MASK row |
| RENDERER: fused function vs inline composition `[rev2 F15]` | the renderer: the check's spelling AND the call boundary (two variables, named as such) | the triple (PAIR, RESTART, plan), the stop, ONE site, layer OFF (at the SIMD layer only B-fn gets vrun rungs), target generic | ONE B-fn site, B-fn vs B-pair forced by a test-only lever (not rev 1's smp05 vs pr09, which are two patterns) | the search text is shared (`ofs_pair_text`), so nothing else |
| STOP (Table A's question, not the triple's) | the stop position and set | the search and the stream, the frame, layer, target | `{X,x}`@0 vs `'/'`@1, each under walk (the one search both stops admit) | the CHECK follows the stop (C-pin and C-stop, `window.c` :1078, :1082) and so does the run member (C-member, :1062): the record names the stop and the check as the two differing pieces |

**What 3.0's reply must carry for them**: the triple, `fused`, and `plan_test` `[rev2.2 R2]` with `stop_test`. `search`, `stream`
and the check let a record name each piece; `fused` tells a fused renderer from a composed one with the same
three pieces (the RENDERER row); `[rev2.1 Q13]` a SIMD-on cell's pieces are NOT told from the OFF cell's (the gap, §2.3; r12 F13: under
`-fmemfn-simd`, `foo[Xx]bar`'s artifact runs VECTOR/MASK/TRIM while the OFF triple says PAIR/RESTART);
`plan_test` and `stop_test` tell two checks over one plan apart (r12 F12, r13 R2: the stop too). The candidates' prices and the grid belong to the
kit's trace, not the reply: the reply carries no price until whole-artifact pricing (`span_pick.md` :84, rev5
C1).

## 7. Open questions (plain words, each with a recommendation)

`[rev2]` Rev 1's Q6, Q7 and Q8 are answered and dropped. Q4 is answered in part. Q11-Q13 are new. `[rev2.2]` Q14
and Q15 are new: choices r13's fixes force that its rulings did not make. `[r1s1 S1-6, S1-2]` Q14 and Q15 are
RULED; Q1's subject is void; Q16 is new (review 2026-11-12 r1 memfn-s1, S1-2). `[r2s1 R30B-7]` Q16 is reworded over
the ask kinds (review 2026-11-12 r2 memfn-s1b, PLAN): the reworded row follows the original, which it supersedes.

| # | for | question | recommendation |
|---|---|---|---|
| Q1 | main | The run-window ask (`req_run_member`) only wants the run member. Should it state no frame, or the pre-check part's frame (FUNC/RETURN with the pre-check's kind)? | **No frame, for now.** The kit derives the part's frame itself (`wf_part_site`). If pcrec stated it too, there would be a second copy of that derivation. Revisit when a priced row applies on pre-check parts (`span_pick.md` §The pick 7). `[r1s1 S1-6]` **Its subject is VOID at 35bee4da9** (K38-2 deleted `req_run_member`; ASK-2 VOID). The non-goal it backs stays true: pre-check parts are framed by the kit (`wf_parts_prepare` -> `wf_part_site`). Its answer does NOT cover ASK-6, whose site's frame is pcrec's own (`pcrec_cover_site`): that is Q16 |
| Q2 | main, kit manager | Under the DFA prefilter, a PARKED reply sends the search to rows that define a DIFFERENT site (the PF find), whose frame the ask does not state. A priced choice between PARKED and RESEED by method cost would need both frames | **Leave it in 3.0.** OFS sites are not priced before they state a kind (`span_pick.md` :131), and that trigger also covers this. File a plan row: "the prefilter ask states each outcome's frame", trigger "pcrec states a kind on OFS sites" |
| Q3 | main | Should 3.0a merge the two renderer lists into ONE table, or keep two lists and only derive the renderable set from each? | **One table.** It is review r2's F9 general form, and plan row [SP1E-RENDERER-TABLE]'s trigger is 3.0. It deletes a parallel list (memory `pcrec-simplification-is-a-benefit`). Under the triple it is the SEARCH renderer table, `[rev2 F6]` with `renderer_rows.tsv` as its named pin |
| Q4 | kit manager | Should the reply's new fields be strings or enums? | `[rev2 F14]` **Answered in part by the F14 ruling**: `fused` is an enum, never a C id. Remaining recommendation, unchanged: **row-id strings** for `frame_row` and `method` (the kit's own row names, as `path` and `mf_result.row` are), and **enums** for `search`, `stream`, `fused` and `plan_test` (closed vocabularies a reader can act on) |
| Q5 | main | `span_pick.md` :86 says the frame (engine, target, layer) becomes a per-call input "from unit 3.0". Is that still meant? | **Read it as T-FRAME's frame** (form, handoff, kind, hooks, call). Target and layer are art facts under the target seam (K0-U3), and T-FIND keeps deciding on the OFF variant (`finder.c` :650). `[rev2.1 Q13]` The reply does not take the layer as an input (the gap, §2.3). Amend :86 (§8) |
| ~~Q6~~ | Frank | Should row 1 wait for the inline one-member finder? | **ANSWERED, yes** (Frank 2026-11-07, to the kit) |
| ~~Q7~~ | kit manager | Should rev 1 drop rev 0's `renderer` for `fused`? | **ANSWERED** (r12 F14 ruling): yes, and `fused` crosses facts (an enum, the pick in `search`), never a C id |
| ~~Q8~~ | kit manager | Should `mf_wstream` declare MASK now? | **ANSWERED** (r12 F8 ruling): yes, declared in the enum; S-mask's code and the unbuilt rows go to §2.5.5's NOTE. `[rev2.1 Q13]` MASK has no reply producer in 3.0 (vrun's rungs are unreported, plan row RUNG-LIST) |
| Q9 | kit manager | When is vrun re-expressed as (vector search, MASK, trimmed check), and when does the PROVES column land? | **Its own zero-mover unit, after the target seam's U2+U3** (D153) and after the first MASK stream renderer exists (the inline one-member finder's unit, if its form is a word or vector mask): that gives the MASK row a second user, the census rule's trigger. `[rev2 F19]` The same unit, or the first search whose proven positions differ from "the stop", adds the PROVES column (the positions and sets a search piece proves, a fact read by C-stop) so the check renderer reads the plan only. To confirm the residue before then: a G2 hors-site compare of `plan[]` against the rendered `wf_test_to` terms |
| Q10 | main | `[rev2 F23]` The kit asked main to file the owner's ruling as a decision entry (`responses.md` 067aca4df). A new D-entry, or an addendum? | **An addendum to D186** (optimizations are unit changes or choice changes). It QUOTES the owner: his sentence "Candidate search and candidate validation are two different primitive pieces that are composed", and his "Yes" to the kit's explicit question "Adopt search, stream, check as composed pieces" (r12 Rulings). It records the triple as ruled on that "Yes". It says that under D186 a stream choice between two supported streams is a CHOICE change needing per-regime evidence (§2.5.3's ST-many). And it gives ruling (2) its home ("row 1 waits for the inline one-member finder and its card, so its first priced comparison is like-for-like"), or main puts (2) in `span_pick.md` §Staging. Main's call |
| Q11 | main | `[rev2 F25]` 3.0b is an MF_SITE_ABI layout event, which is [SEAM-READER-CENSUS]'s trigger ("every mf_* seam member has a kit reader or a listed trigger"). Does 3.0b fire that row? | **Fire it narrowly**: 3.0b's own new members each name their reader in the same commit (§2.3), which the row asks of them. The census of every OTHER seam member stays the row's own Boonies-weight work, not 3.0b's. Main edits the row's trigger to "the next layout event after 3.0b" |
| Q12 | main | `[rev2 F22]` R-35 ruling (a) names "form, handoff and site_kind stated per frame at phase 1". ASK-1 states `site_kind` UNSTATED for the DFA prefilter's ask. Is that the intended reading? | **Yes, confirm it.** OFS sites state no kind today (`span_pick.md` :131's named exception). Stating one would let T-FIND decide those sites, which moves bytes, so it belongs with row 1 or later, under the exception's own trigger ("pcrec states a kind on OFS sites") |
| ~~Q13~~ | kit manager | `[rev2.1 Q13]` Is F13 a rung LIST in 3.0b (needing the `fs` fact) or a LABEL? | **ANSWERED** (r12, "Ruling on rev 2's Q13"): a LABEL. The list is plan row RUNG-LIST, below |
| Q14 | kit manager | `[rev2.2 R2]` `stop_test` (ruled: TABLE = hook stated AND the covering span offers this set, matched by offset) reports the define's OFFER at the stop. Only B-walk's find tests the stop through a member test that reads the table (`window.c` :2553); B-pair and B-memchr test the stop by its bytes (`shape` over `w->set[stop_ix]`, :2536; `two`, :2566), and B-hors probes `hl`, which may not be the stop (:2642-2656). `[r2s1 R30B-9]` (At 0f1d54089: B-walk's stop test :3124, `shape` :3107, `two` :3137, `d_hors_head` :3217. "Only B-walk" is about the FIND's stop test: where the stop's offset stays in `plan[]`, inside a pinned stretch, the candidate test `wf_test_to` and `d_hors_head` can also read its marker; §2.3's `stop_test` and row (AF) state the path and the class rule there.) There a TABLE `stop_test` names a table the text never reads. Should `stop_test` stay the offer fact everywhere, or be NONE where the search does not member-test the stop? And should it get its own sabotage row? | **Keep the offer fact, as ruled**: it is what the define stores (`w->table[stop_ix]`), it matches `plan_test`'s definition (which has the same exception at a position the search proved), and it needs no per-renderer rule. G2's class asserts the marker only where the rendered text member-tests the position (B-walk's stop, C-find's positions less the proven one) and asserts no marker for an OWN position. **Add row (AF)**, "`stop_test` always OWN while `plan_test` is right": red on G2's B-walk sites whose stop alone is offered. It makes 3.0b 19 rows (S2994-S3012); ids are taken at build time anyway. `[r1s1 S1-6]` **RULED** (kit journal, 11-07 ~23:10: "Q14 accepted (sabotage row AF; 3.0b 19 rows)"). S2994-S3012 are taken: expected S3078-S3096 (§5 3.0b's re-base block) |
| Q15 | kit manager | `[rev2.2 R10, R19, R23]` Three fixes offered two forms and r13 named no preference. The text follows the first form of each. (1) `renderer_rows.tsv`'s frame column: FDROUTE prints `frame=` (a trace-format move, `trace_format.md`), or the column is stated as documentation only. (2) The SIMD-layer agreement: carried by `reach_equal.py` with `-fmemfn-simd` (a boxqueue job), or stated unchecked until RUNG-LIST. (3) `r33_sim/probe.c`: left to break (a lane study, named in the report), or edited in the seam commit | **(1) print `frame=`**: a column held against nothing is a check that cannot fail (learnings §3); the trace line is not an emitted byte. **(2) name the carrier**: the agreement at the SIMD layer is cheap to run, and that is where the gap lives. **(3) leave it to break**: lane files are historical after merge, and `span_pick.md` :378 already calls it lane evidence. `[r1s1 S1-6]` **RULED** (kit journal, 11-07 ~23:10): "Q15 accepted except probe.c 'left to break', REJECTED: census jobs build r33_sim/probe.c, so 3.0b adds a kit-owned successor probe under span_pick/". (1) and (2) stand; (3) is §5 3.0b's probe item |
| Q16 `[r1s1 S1-2]` | main, kit manager | pcrec makes a phase-1 ask on a site pcrec ITSELF defines in two places: the offset-skip block (ASK-1, which states the define's frame and is held to it by ASK-3's trace-build compare) and the cover/REPORT site (ASK-6, which asks NONE; its refusal is loud from 3.0b on, but nothing compares its `stop` with the cover define's). Should the general form be ruled: "every pcrec phase-1 ask on a site pcrec also defines states that define's frame (and hooks), and one trace-build compare (ASK-3's form) holds the ask to the define"? It retires §6's per-ask special case | **Yes, as a PLAN row now, built at its trigger**: row 1's first frame-dependent row, or the next new pcrec `mf_wdecide` caller (K38-2 added ASK-6 without a design pass). Take it inside 3.0b only if its cost is ASK-1's (one argument list for ASK-6, with the define's `stem`, and ASK-3's compare extended to `emit_cover`'s define); otherwise the plan row, with 3.0b's loud refusal and emit_sweep's `@` witness holding until the trigger |
| Q16 `[r2s1 R30B-7]` (REWORDED, the PLAN ruling: it supersedes the row above) | main, kit manager | pcrec makes PURE asks of the kit, of two kinds (`mf_ask` and `mf_wdecide`), on sites pcrec itself DEFINES, and their answers reach emitted bytes. There are four. Three are already loud on -1 and held to the define: (1) ASK-1, `mf_wdecide` on the offset-skip site, loud (`emit_dfa.c` :7614-7617) and held by ASK-3's trace-build compare (3.0b); (2) `req_pres_ask`, `mf_ask` on the pre-check presence site, which feeds the same `@` stamp through `req_run_at`'s first branch, loud (:8749-8759) and held by the trace build's compare of the ask's run reply with the define's (the `MemfnPre` comment, :1267-1278); (3) `cand_ask`, `mf_ask` on the PF/MLINE sites, loud (:8356-8357) and held by `cand_asked_hold` (:7047-7062). The fourth, (4) ASK-6, `mf_wdecide` on the cover site, asks NONE, is loud only from 3.0b on, and nothing compares its `stop` with the cover define's. The kit's contract comment already states the family rule, "every pcrec caller turns -1 into pcrec_ctx_fail" (`window.c` :1275-1278), which ASK-6 falsifies until 3.0b (that comment is a reader of 3.0b's ASK-6 hunk). Should the general form be ruled over the ask KINDS: "every pcrec pure ask (`mf_ask` or `mf_wdecide`) on a site pcrec also defines states that define's frame and hooks, is loud on -1, and is held to the define by one trace-build compare"? It retires §6's per-ask rule | **Yes, as a PLAN row now** (ASK-DEFINE-FRAME below): the row is "bring the fourth member in", not a new mechanism, since members (1)-(3) are built. **Trigger: the next new pcrec ask of EITHER kind** (`mf_ask` or `mf_wdecide`; K38-2 added ASK-6 without a design pass), or row 1's first frame-dependent row. 3.0b's part stays as ruled: ASK-6's loud refusal with its plant (§4.2), and emit_sweep's `@` witness. Take the frame and the compare inside 3.0b only if the cost is ASK-1's (one argument list for ASK-6 with the define's `stem`, and ASK-3's compare extended to `emit_cover`'s define) |

**Plan rows proposed** `[rev2.1 Q13]` (for main to file in `docs/dev/plan.md`; the note had no plan-rows section, so this is it). Q2 and Q9 also name rows; this one is new. `[rev2.2 R25, R28]` Its content gains VECTOR (the value and its support row, carried from 3.0), and its trigger is the kit manager's restatement, verbatim.

| row | content | trigger |
|---|---|---|
| RUNG-LIST | the reply lists the SIMD rungs the define will render: `nrung`/`rung[]` (row id, search VECTOR, stream MASK, check TRIM, widest first), the three fact columns on `fn_rows` PREFIX, and the one pcrec fact it needs, whether the define's file-scope sink states `simd_open`/`simd_close` (`fs`), unless U2+U3 has moved vrun's admission into per-target arts by then (then each target art's reply is one rung and no sink fact is asked). `[rev2.2 R25]` It declares `mf_wsearch`'s VECTOR and the support table's VECTOR row (MASK; basis witness: vrun's text holds `m &= m - 1`), both removed from 3.0. Rev 2 designed it in full (u30d2, `45f3a337f`); D77 defers it | `[rev2.2 R28]` row 1 compares a SIMD-on cell, or the first MASK stream RENDERER ROW lands |
| `[r1s1 S1-2]` ASK-DEFINE-FRAME (§7 Q16; name main's) `[r2s1 R30B-7]` SUPERSEDED by the next row | every pcrec phase-1 ask on a site pcrec also defines states that define's frame and hooks, and one trace-build compare (ASK-3's form) holds the ask to the define: ASK-6 gains the cover define's frame (call DEFINE, the define's `stem`), ASK-3's compare extends to `emit_cover`'s define; §6's per-ask loud-check rule retires | row 1's first frame-dependent row, or the next new pcrec `mf_wdecide` caller |
| `[r2s1 R30B-7]` ASK-DEFINE-FRAME (§7 Q16 as reworded; name main's) | every pcrec PURE ask (`mf_ask` or `mf_wdecide`) on a site pcrec also defines states that define's frame and hooks, is loud on -1 (`pcrec_ctx_fail`), and is held to the define by one trace-build compare. Built members: ASK-1 (+ ASK-3, 3.0b), `req_pres_ask` (the trace build's run compare), `cand_ask` (`cand_asked_hold`). The row brings in the fourth, ASK-6: it gains the cover define's frame (call DEFINE, the define's `stem`) and ASK-3's compare extends to `emit_cover`'s define; §6's per-ask loud-check rule retires into it, and `window.c`'s "every pcrec caller turns -1 into pcrec_ctx_fail" becomes a checked statement. **Note for main:** file it as one plan row over both ask kinds (not an `mf_wdecide`-only row), citing the three built members | the next new pcrec ask of either kind, or row 1's first frame-dependent row |

## 8. Amendments this design makes to other documents (each lands with its unit)

| document | amendment | unit |
|---|---|---|
| `span_pick.md` :109, :114, :135, :420, :423, `[rev2 F25]` :45, :51, :369, :408 | T-FIND and T-FRAME are asked at PLAN time on framed asks; the asker fact's named exception retires (the staging diagram's "with the asker fact" and :51's `SF_WINDOW_STOP` sentence restated); N11's "plan-time at 3.0" is done; the find-then-verify plan is the triple (search, stream, check), and T-FIND is its search piece | 3.0b (the note's own revision, by the kit) |
| `span_pick.md` §The tables `[rev2 F20]` | a new question table, **T-STREAM** ("how the text moves past a rejected candidate": the support table and Table S), the `answers` value the census needs; the check renderer and skeleton rows filed under T-FRAME; the fused rows under the named exceptions (`arms[]`, `fn_rows` BODY) | 3.0a |
| `span_pick.md` :86 | the per-call frame is T-FRAME's; target/layer stay art facts (Q5) | 3.0b |
| `window_site.md` §0 and §2.4 ("the decision reads no frame fact"; its "resume" row), `[rev2 F25]` :336, `[rev2.2 R14]` :272, :340, :342 (`wf_brows`, `wf_b_render`: restated with the split's table names, 3.0a's part) | a framed ask states the NEXT rows' frame; the decision itself is still frame-free in 3.0; the resume is the candidate stream, a piece chosen by Table S; :336's "both T-FIND askers" becomes "the one walk, gated by the frame's renderable set" | 3.0b |
| `[rev2 F25]` `span_cards.md` :865 | the `pair` card's fact: "E-find's search renderer table has (E-find, PAIR)" in place of `fd_stop.renders_pair` | 3.0a |
| `[rev2 F6]` `tests/memfn/renderer_rows.tsv` header, `memfn/docs/trace_format.md` :168-183 | the pin re-keyed by T-FRAME ids, B-fn marked fused `[rev2.2 R10]` (a 6th column); FDROUTE's key restated, with its new `frame=` key; the composer's D-hors record names F18's residue | 3.0a |
| `[rev2.2 R14]` `docs/design/memfn/units_inventory.md` :56, :111; `tests/memfn/CLAUDE.md` :37, :43; `memfn/src/CLAUDE.md` :26 | the retired names restated (§2.4's reader table); :43 with the purity population (§3, 3.0b) | 3.0a (:43: 3.0b) |
| `docs/dev/plan.md` [SP1E-RENDERER-TABLE] | closed (main) | 3.0a |
| `docs/dev/plan.md` [SEAM-READER-CENSUS] | its trigger restated per Q11 (main) | 3.0b |
| `docs/dev/decisions.md` D186 | an addendum recording the ruling and ruling (2) (main; Q10) | main's, any time |
| `memfn.h`, `memfn/include/CLAUDE.md`, `memfn/src/CLAUDE.md`, `trace_format.md`, `decider_census.tsv`, `finder_history.md` | §2.4, §2.6 and §3 | 3.0a / 3.0b |

## 9. The three standing questions (docs/design/CLAUDE.md)

**Q1, the measurement regime: NOT RELEVANT.** 3.0 reads and produces no measured number. Its witnesses
are compile-only: artifact diffs, hashes and checks. The cards stay unread until row 1. Table S is a rule
over the search's support and the frame's streams and reads no measurement. The stream comparison that
would read one is row 1's (§6).

**Q2, the independent control: RELEVANT.**
- Byte identity is checked against the NAMED BASE's artifacts, diffed pcrec-side (emit_sweep), never
  against the kit's `moved` (K35). This includes Table B's split (§2.6.4).
- `[rev2 F29]` `[rev2.2 R1]` The kit's agreement check compares the plan call's FRAME part with what the define
  STORED (`site_rec`, `wf_plan`, by §4.1's per-frame field map), never with a recomputation through `reply_of` or
  the plan function; row E2 shows a frame-part fault that moves no text is red there. Its DECISION group is
  re-derived through `decide`, so for it the check shares the subject's source and is a TRIPWIRE against the two
  calls diverging (a quiet-only branch, a cache, the allocator), not the identity control. The decision group's
  independent controls are the purity harness (fresh art vs interleaved defines) and ASK-3 below, and a decision
  fault common to both calls moves the define's text (emit_sweep, against the named base). No stored decision copy
  is built: it would be a record only the check reads (ruled).
- pcrec's check (ASK-3) compares two pcrec statements of one frame through the kit. Its subject is pcrec's
  statement, which the kit cannot make equal on pcrec's behalf. `[rev2.2 R17]` Both its sides go through the plan
  function, so it holds pcrec's INPUT, not the stored record; with the kit's check it forms a chain (kit: re-ask ==
  stored; ASK-3: phase-1 == re-ask). Row F asserts ASK-3's own message, so its red shows ASK-3 reached the site.
- `[rev2.2 R11]` The refusal-naming rows (B), (C), (R) are detected by a standing `rows_check.py` §R invariant's
  message over named witness lines, not by any red.
- `[rev2 F21]` The support pin's LIBC and LIBC_BACK rows are written from the RULING's text ("libc memchr
  supplies only one-shot"), so for them the pin and the table do not share a source (§5 row M). Its WALK,
  PAIR, HORS and no-search rows `[rev2.2 R25]` (VECTOR's is removed, §2.5.2) share the table's reading; their
  independent control is base's emitted TEXT (the resume spelling `C++`, `_sh[256]`, the absence of a mask
  variable), read by `[rev2.2 R7]` the landing-time basis witnesses (3.0a, over base's artifacts joined to FDROUTE)
  and, standing, by 3.0b's G2 text classes (§2.5.2, §5 row R). The pin's reader is `rows_check.py` §S, comparing
  each cell to the kit table's print (`arm_fixtures --streams`), never the table to itself.
- `[rev2 F31]` On E-find, `fused`, `method`, `search` and `frame_row` are held to each site's TEXT by G2's
  classes, which do not read the plan (as `ef_hors` already reads `_sh[256]`, `g2_win_gen.c` :998); `[rev2.2 R2]`
  `plan_test` and `stop_test` by the hook's own marker `g2w_t<id>_<ref>[`, matched by offset through G2's own
  offers. `[rev2.2 R19]` All of G2's classes are OFF-layer only; the SIMD layer's agreement rides `reach_equal.py`.
- Populations are counted by their owners: the corpus's DFA prefilter sites by ASK-4's suite; `[rev2 F30]`
  the (frame_row, stream) cells by G2's own tally, each floored at its measured count less ~10% with the
  impossible cells at 0 (the corpus alone frames only E-func); `[rev2 F12]` the `table_name`
  population by G2 at its own floor.
- Every sabotage row names the check that sees it and why that check can see it (§5). Reach is shown by a
  control (H, N) or by a corpus or G2 site the plant moves (A, B, C, F, K, L, O, P, R, Y-AA). `[rev2.2 R9]`
  Existing sabotage anchors on lines 3.0 edits (S686; G2's S1423, S1427, S1428, S1543) are kept verbatim or
  re-aimed in the same commit, so a setup failure is never read as DETECTED.

**Q3, what moves when data is regenerated: RELEVANT, narrowly.** 3.0 adds no stamp or generated file,
and re-measuring a set moves nothing (no reader). The support table, Table S and the `fn_rows` fact column `[rev2.2 R24]` (BODY rows' pick)
are hand-declared rule tables, not regenerated data; `renderer_rows.tsv` and `stream_support.tsv` are
hand-written pins. One existing reader of the TEXT does move with 3.0's code: the cards' recorded form hashes
(zen4-grid3@1 rows' `kit:form.<id>=<hash>`). A hash that moved would make cards stale. Goal 1 therefore
requires every form id's hash unchanged, and check C's stale count 0, across the split too. A byte move would
be an abi event (D76/D94), and 3.0 has none.

## 10. span_pick.md cites that drifted

`span_pick.md` :86's inner cites: `window.c` :1061 is now `memfn/src/window.c` :1225, and `finder.c` :934
(layer) is now `finder.c` :650 `[rev2 F27]` (rev 0 and rev 1 said :647, which is `q.site = s;`). Its :49-50's
`emit_dfa.c` :7600-7602 is now `src/gen/emit_dfa.c` :7598-7603, and its :51's `finder.c` :938
(`SF_WINDOW_STOP`) is now `finder.c` :656 (`SF_ASKER_PAIR`).

## STATE AT HANDOFF

`[r2s1]` Lane s1fix2 (2026-11-12): review 2026-11-12 r2 memfn-s1b's FIX-NOW R30B-1..6, R30B-8, R30B-9 and PLAN
R30B-7 applied as the kit manager ruled them (all as proposed); this note carries R30B-1..9, and
`span_runs_sheet.md` §5's K38-3 row carries RK383-1..6. Cites added were read at main 0f1d54089 (the review's
522faf600 for every file 3.0b reads). For main at the GO: ASK-6's hunk (the review's precondition), its plant's
form (row (AG), recommended, or a once-run control: R30B-3), and Q16 as reworded with its plan row
ASK-DEFINE-FRAME. 3.0b's readiness per the review: READY after this text pass, no third round. OWED: none.

`[r1s1]` Lane s1fix (2026-11-12): review 2026-11-12 r1 memfn-s1's FIX-NOW S1-1..S1-7, S1-10..S1-16 and DOC S1-8,
S1-9 applied as the kit manager ruled them (all as proposed); this note carries S1-1..S1-9 and S1-16, and
`span_runs_sheet.md` §5 carries S1-10..S1-16. Cites added were read at main 35bee4da9 (unchanged at 781275381 for
every file 3.0b reads). Q14 and Q15 are RULED (the paragraph below predates that); Q16 is new, for main and the kit
manager; main's PLAN item: the census sweeps since U2 (§5 3.0b's probe item). 3.0b's readiness per the review:
READY after this text pass. OWED: none.

`[rev2.2]` Rev 2.2, lane u30d4: review r13's accepted ids R1-R19, R21-R28 applied as the kit manager ruled them
(R20 NOTED, kept as an optional control); every cite rev 2.2 adds or touches re-read at main **a678d0a4e** (main's
HEAD at this lane's start, unchanged since r13). Readiness per r13's rulings: 3.0a may build without another round
once the kit manager checks the by-id table (§R2.2); 3.0b gets its D27 author at its build, and r13 recommends a
one-critic readiness look at R1/R2's text before it. Open for the kit manager: Q14 (`stop_test` on byte-tested stops;
row AF) and Q15 (three either/or forms, text follows the recommended one); for main: Q10-Q12 as before.
Rev 2.1, lane u30d3 (one ruling, Q13; no cite was re-derived: the rung list's removal adds none). Rev 2, lane u30d2. Cites re-checked by grep at main a678d0a4e (main's HEAD at this lane's start; the
worktree's code is identical to it under `memfn/`, `src/`, `tests/memfn/`). No make, no timing, no code. Not
a build go: 3.0a may start on the kit manager's word once rev 2 is accepted (r12's readiness note; the
listed findings are in the text, §R2); 3.0b needs main's Q11/Q12 (`[rev2.1 Q13]` Q13 is answered). R-35's build GO
covers stage 3 (Frank 2026-11-06). OWED: none. No rulings file was named.
