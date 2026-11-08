# Review 2026-11-07 r12 — memfn-planframe1 (design): plan_frame.md rev 1, span_pick unit 3.0

DRAFT by the round's coordinator. Dispositions are PROPOSED; the kit manager rules them (R-35).

## Subject

- `docs/design/memfn/plan_frame.md` rev 1 at **9c60a76bd** (branch lane/memfn-u30d, tip 35ad9c443 adds
  only the lane report). Unit 3.0 "the plan takes the frame", for kit request R-35.
- Build tree: main **a678d0a4e** (merge-base 5c3b65fb3; a678d0a4e touches only `tests/fuzz/fuzz.py`). The
  review tree was built there once; every cite was checked there.
- Rulings frozen at main c90d33f54 (decisions.md, plan.md). Re-diffed when the critics returned and at
  hand-back: no FREEZE DRIFT.
- **FREEZE NOTE.** Frank's 2026-11-07 composition ruling has one record: kit branch lane/memfn-k1107
  (`memfn/docs/journal.md` :3636-3638 there, `responses.md` :3262 there). It is not on main and not a D-row
  (the design's Q10 asks main to file it). The record reads "RULED by Frank (to the kit, directly), 'Yes':"
  followed by the kit's TRIPLE reading. So the owner's "Yes" answered a message that contained the triple,
  but his own quoted sentence names two pieces (bears on F8).

## Lenses as run

| lens (id) | model | its one question | why chosen |
|---|---|---|---|
| premise + goals (PREM) | opus | is every "today the code does X" and every reader-by-grep list true at a678d0a4e? | a new mechanism resting on many claims about today's code; the goals lens folded in |
| soundness: the split (SPLIT) | opus | does Table B's split, applied literally, reproduce today's text byte for byte, and does the renderable-set rule pick today's rows? | an answer-identity claim BY PROOF (zero movers) |
| soundness / check adequacy (SAB) | opus | does each proposed sabotage row and Goal check go red when sabotaged and stay green when correct; what is unplanted? | 14 sabotage rows and five goal checks were proposed |
| slot tracing + ruling check (SLOT) | opus | does every new fact have ONE table, and do the rulings agree? also the two standing questions | new tables (support, Table S, three renderer tables), rulings relied on |
| seam round trip + owner criteria (SEAM) | opus | could the seam's traffic round-trip as text, and does the design serve the owner's stated criteria? | a planner/kit seam event, and three owner statements quoted as criteria |
| verifier | sonnet | re-derive 20 CONFIRMED findings that would change the design | §6 of the skill |

Cost and overlap (D153) was folded into SEAM. No readiness lens was run: this is rev 1's first round.

## Which lens caught what

- Byte or answer identity of the split (F1-F5): SPLIT, with PREM and SAB finding F1, F2 and F3 on their own.
- Selection and slot structure (F8-F11, F18-F20, F24): SLOT, with SEAM on F8 and SPLIT on F9.
- Seam and owner criteria (F12-F17): SEAM.
- Witness adequacy (F21, F28-F34): SAB. F21 was also found by SLOT.
- Reader-list completeness and stated premises (F6, F7, F25-F27): PREM.

Overlaps: F1 = SPLIT-1 + PREM-2 + SAB-3. F2 = SPLIT-2 + PREM-4. F3 = SPLIT-5 + PREM-4 (tail) + SAB-8.
F7 = PREM-3 + SAB-2. F8 = SLOT-4 + SEAM-6. F9 = SLOT-3 + SPLIT-6. F14 = SEAM-4 + PREM-7 (last item).
F21 = SLOT-8 + SAB-7.

## Findings, with PROPOSED dispositions

"Answer" means the unit as written, if built literally, would change an answer, refuse a compile, or
turn a correct build's witness red. The verifier's verdict is in brackets ([V: HOLDS] etc.;
[not re-verified] means the finding is a design argument the verifier was not asked to re-derive).

### Answer-level (the split and the plan function as written)

- **F1** (SPLIT-1, PREM-2, SAB-3) [V: HOLDS]. §2.4's formhash row says `wf_plan_brow` will "return the
  composed search renderer row, or B-fn's fused id". Today it returns T-FIND's DECIDING row
  (`window.c` :2817-2820). The renderer row comes from `wf_plan_bren` (:2824-2827). `formhash.c`'s `pair`
  entry pins row "PAIR" and refuses on a mismatch (:511). Built as written, the CORRECT build refuses `pair`:
  Goal 1's hash identity and check C go red, sabotage (A) can no longer be told apart from the correct
  build, and FDROUTE's `row=` moves (`compose.c` :1153). **FIX-NOW**: the accessor keeps returning
  T-FIND's row (= `method`), and the renderer or fused id is `wf_plan_bren`'s successor. Also state that B-fn
  is reachable only because the (E-find, PAIR) search row exists (SAB-3's side note).
- **F2** (SPLIT-2, PREM-4) [V: HOLDS; seen on `a[Xx].b`]. E-find's loop has a fifth piece that is keyed on
  the row: B-pair's frontier declaration `ofs_pair_decl`, written after `wf_cand` and before `wf_raise`
  (`window.c` :2731-2735). §2.6.4's four columns do not carry it. A literal composition either leaves `_ha`
  undeclared or re-declares it inside HEAD. **FIX-NOW**: the search renderer row gets a loop-state
  ("before the loop") slot, ordered before RAISE. The stream renderer gets the same slot, which a MASK
  stream's `m` will need.
- **F3** (SPLIT-5, PREM-4 tail, SAB-8) [V: HOLDS]. The floor is a different skeleton: `for (; COND; C++)
  if TEST` (`wf_floor_expr` :2314-2327). Its bound comes from the CHECK (`wf_test`), not the search head, and
  its resume is hard-wired. So "one composing loop writer" would move the floor's bytes. If the floor is not
  table-driven, sabotage rows (N) and (L-floor) stay green (SAME). **FIX-NOW**: per-frame SKELETON rows; the
  bound and RAISE are named as the frame's pieces; every composing frame takes NEXT from its stream renderer
  row, and a missing row refuses; (N) gains its reach control (`g2_win_gen.c` :689-690).
- **F4** (SPLIT-3) [V: HOLDS as a conditional]. `fd_holds`/`fd_decide` (finder.c :498-533) also walk slot
  PRES, whose rows have pick FF_UNSTATED. An unscoped renderability gate "beside :503" would decline every
  pre-check decision. **FIX-NOW**: scope the gate to slot FIND, and add a PRES witness to REACH equality.
- **F5** (SPLIT-4) [V: HOLDS]. §2.6.4's libc and include union is wrong. B-walk writes no memchr
  (`wf_brows[B_WALK].libc` 0), and today's value is `libc || w->nrun`: the CHECK's run compares count. Read
  literally, a B-walk or B-hors site with a run term flips `libc_free` and `includes` in the reply class.
  Witness: `--memfn=no-fd-d1 abcdef`. **FIX-NOW**: take the union over all three pieces, with the values
  for each piece.

### Design: structure of the triple and its tables

- **F6** (PREM-1) [V: HOLDS]. `tests/memfn/renderer_rows.tsv` and `rows_check.py` §R (FDROUTE `ren=`,
  `trace_format.md` :170-182) form a hand pin of (T-FIND row, renderer row, frame) that 3.0a re-keys. They
  are missing from §2.4, §3 and §5, and Goal 4's "no other list" is false while the pin exists.
  **FIX-NOW**: list them with a disposition, and restate Goal 4 as "one table plus its named pin".
- **F7** (PREM-3, SAB-2) [V: HOLDS]. `select_arm`'s refusal (`compose.c` :312-325, not :262-268) also
  serves `?need` and an arm's own decline. Sabotage rows (B) and (C) are LOUD only through it, and with the
  branch removed or falling through to `kit_walk` they become SAME. **FIX-NOW**: keep the branch as (B)/(C)'s
  observation point; (B) names its arm as absent; (C) asserts the refusal message.
- **F8** (SLOT-4, SEAM-6) [not re-verified: argument from the design's text]. In 3.0, `stream` is a pure
  function of `method` (SHIFT iff D-hors), and every built pick has exactly one stream. S-mask never holds,
  the italic support rows describe forms that do not exist, and MASK has no producer. The only argument for
  carrying it now is "a second MF_SITE_ABI event later". Before 1.0 such an event is ritual, not avoidance
  (memory pcrec-abi-changes-pre-release), and D77 says to wait. SLOT also asks whether the stream is a
  third piece or a property of the search: the owner's sentence names two pieces, but his "Yes" was given to
  the triple reading (FREEZE NOTE). **PROPOSED**: FIX-NOW for the D77 trim: drop S-mask's code and the italic
  support rows from 3.0 (move them to a NOTE or to the finder unit's design); keep the built support rows,
  the two built stream renderer rows and the enum with MASK declared. Q8 becomes an explicit cost call. The
  kit manager confirms with Frank, in plain words, that his "Yes" covered the stream as a separately chosen
  piece; a few words settle it.
- **F9** (SLOT-3, SPLIT-6) [not re-verified: latent, no 3.0 pick moves]. Three rules answer "this frame
  renders stream X" (the renderable set, Table S's rows, and §2.5.4 rule 2), and they disagree for any
  search that supports two streams. Choosing by row order there would be an unmeasured CHOICE change
  (D186). **FIX-NOW**: one rule. Table S's input is support(pick) INTERSECT the frame's renderable streams;
  exactly one stream -> that stream; none -> refuse; two or more -> refuse until a row with evidence
  exists. Trigger for the evidence row: the first search with two streams on one frame.
- **F10** (SLOT-1) [V: HOLDS]. The composer's PF arms appear as SEARCH renderer rows with stream S-caller
  (§2.6.1-2.6.2) AND as FUSED rows (§2.6.3), and `fused` = `form_id` on every E-func/E-stmt ask. Two slots
  answer one question, and on the composer `fused` can never be "". **FIX-NOW**: pick one home. The
  recommendation is to compose them (fused ""), which is what §2.6.1 already says.
- **F11** (SLOT-2) [not re-verified: text]. The renderer tables are keyed by {E-find, E-generic, composer},
  but "composer" is not a T-FRAME row, so the reply's `frame_row` cannot look a row up (and E-func/E-stmt
  have no stream row). **FIX-NOW**: key the tables by T-FRAME's ids, and name the non-plan FIND sites as
  arms[]'s exception.
- **F18** (SLOT-5) [V: HOLDS]. `hors_facts` runs only when `st` is set, so the composer's HORS stays filtered
  by an absent fact as well. "PAIR and HORS are then filtered by one mechanism" is false for HORS, and its
  new branch has no witness. **DOC**: withdraw the claim and name the residue with F5's second-half trigger.
- **F19** (SLOT-6) [SUSPECTED]. "The positions the search proved" has three homes: C-stop, `d_hors_head`'s
  text-time `skip`, and vrun's TRIM. On D-hors the reply's `plan[]` may list a probed position that the
  rendered test skips. **PLAN**: a PROVES column on the search piece, read by C-stop. Trigger: Q9's unit or
  the first search whose proven positions differ from the stop. Confirming it is a G2 hors-site compare.
- **F20** (SLOT-7) [not re-verified]. `decider_census.tsv` has no `answers` value for the stream question,
  and the check renderer rows and fused rows get no census rows. **FIX-NOW**: name the question in
  span_pick's amendment, or fold it into T-FIND per F8; give the check and fused rows census rows (EXC).
- **F24** (SLOT-11) [not re-verified: grep]. `MF_WSTREAM_ONESHOT` sits beside `MF_BODY_ONESHOT` (`memfn.h`
  :413), and one ask states body ONESHOT and answers stream ONESHOT with different meanings. **FIX-NOW
  (XS)**: rename the stream value to RESTART, the owner's own "one-shot restart" (kit manager's call).

### Design: the seam and the owner's criteria

- **F12** (SEAM-1) [V: HOLDS]. `window.c` :1314 sets `w->table[i]` from `def->table_name`'s stated-ness.
  The reply has no member for the per-position test kind, so two framed asks that differ only in that
  stated-ness get EQUAL replies but render different checks (T-VERIFY's C-table vs C-own). Goal 2 breaks,
  and the agreement check (same hooks) cannot see it. **FIX-NOW**: add a per-plan-position test-kind member
  to the check group (same seam event), or name T-SETTEST's piece and its member; add a G2 population that
  varies `table_name`.
- **F13** (SEAM-2) [V: HOLDS; `foo[Xx]bar` with `-fmemfn-simd`]. Under the SIMD layer the artifact runs
  (vector search, MASK, trimmed check), while the reply says (PAIR, ONESHOT, fused). That confounds §6's
  STREAM and CHECK comparisons, and MASK IS produced today. **FIX-NOW (doc)**: §6 adds the layer and target to
  every FIXED column; §2.3 says `stream`/`fused` describe the OFF variant. General form: the reply names
  the rung's triple. Trigger: row 1 compares a SIMD-on cell, or the first MASK producer lands.
- **F14** (SEAM-4, PREM-7 last) [V: PARTLY; the value settled]. On the only production framed ask (ASK-1,
  E-func) the reply is (E-func, "", ONESHOT, "ofsskip"). `fused` is "ofsskip" for BOTH fn-pair and fn-memchr
  (`ofsskip.c` :910-911, `compose.c` :1310), so the reply cannot name the search there, and `stream` there is
  S-oneshot's "no search" fallback, a presumed value. **FIX-NOW**: cross the fused row's FACTS (the pick it
  implements, PAIR or LIBC, through `fn_rows` BODY) rather than a C arm name, or state the gap in §2.3/§6
  with its trigger (OFS states a kind). Kit manager's choice; it is the same 3.0b event either way.
- **F15** (SEAM-5) [not re-verified: argument]. §6's comparisons do not each vary ONE piece. STOP also
  varies the check (C-stop, C-pin follow the stop). CHECK (B-pair vs B-fn) also varies the call boundary and
  the SIMD rungs, and its example uses two patterns. SEARCH (libc vs the inline finder) bundles three
  variables. HORS cannot be a single-piece SEARCH cell. **FIX-NOW (doc)**: restate the FIXED columns, rename
  the CHECK row "RENDERER: fused function vs inline composition", and use one site under a lever.
- **F16** (SEAM-3) [not re-verified]. `def` crosses as pointers, callbacks and C text, and the gates
  classify the text by C grammar (`gate.c` :86-297, :618-653; MF_MISS_N compared by ADDRESS). §2.8's
  "facts reused unchanged by a Rust emitter" is false for T-FRAME's legacy contracts. **DOC + PLAN**: §2.2
  names the ask's round-trip projection (stated-ness, class enum, miss token); add a same-class-different-
  text fixture as Goal 3's claim; §2.8 moves the classifiers to the spellings layer. Build trigger: [IR-FORM].
- **F17** (SEAM-7) [not re-verified]. The FACT tables carry C-isms: the LIBC pick and its basis, measure sets
  taken on glibc, and the hook classifiers. **DOC**: §2.8 gains a column "what is C-specific in it today".

### Witnesses and checks

- **F21** (SLOT-8, SAB-7) [not re-verified: against the ruling text]. The support pin is independent for
  LIBC only. The ruling says only "libc memchr is one-shot only". The WALK/PAIR/HORS rows come from the same
  reading as the table, and the MASK cells move no byte. **FIX-NOW**: label each pin row's source; give the
  derived rows a basis witness (no block state across a rejection, read from text); narrow Goal 4's claim.
- **F28** (SAB-1) [V: HOLDS]. `decider_census.py`'s backstop spellings do not match a `.pick ==` loop or the
  `.holds(` walk, so sabotage (D), planted as a copy of today's lists, is SAME. **FIX-NOW**: one named lookup
  accessor plus backstop shapes for the row-walk idiom; plant (D) as a copy of `fd_renderer`'s loop.
- **F29** (SAB-4) [SUSPECTED]. If the define side of the agreement check is computed by `reply_of` or the
  shared plan function, sabotage (E) is SAME (a control that shares its source). **FIX-NOW**: state that
  the define-side operand is read from what the define STORED (`site_rec`, `wf_plan` members, `mf_defined`),
  as rule 2's `r->cls` is; add a plant inside the plan function's frame part.
- **F30** (SAB-5) [V: HOLDS]. Goal 2's per-stream floors of 1 are aggregate across frames and K35-weak.
  **FIX-NOW**: tally (frame_row, stream) cells, floor each at its measured count less ~10%, assert impossible
  cells are 0, and cross-check `stream == SHIFT` iff the text holds `_sh[256]`; give MASK-0 a live plant.
- **F31** (SAB-6) [V: HOLDS]. `mf_defined` exposes neither E-find's T-FIND row nor a B-fn bit, so on E-find
  `fused`, `method` and `frame_row` have no independent observer (three green plants named). **FIX-NOW**: G2
  classifies each E-find site's text and asserts `fused`/`method`/`frame_row` against it; the id-resolution
  check asserts exact emptiness.
- **F32** (SAB-9) [V: HOLDS]. `pur_diff` and the control print are hand lists, and (H) proves only that
  `stream` is in them. **FIX-NOW**: `memcmp` the whole `mf_wreply` (`reply_of` memsets it), or one plant per
  new member.
- **F33** (SAB-10) [V: HOLDS]. No row varies `call`, so UNSTATED's refusal, NONE's zero frame part and
  EMIT's DEFINE|USE gate are unwitnessed. **FIX-NOW**: three fixtures plus their plants.
- **F34** (SAB-11) [V: HOLDS]. The purity fixture's hooks state 4 of the 6 callbacks the counting hook
  names. **FIX-NOW**: state all six, each a counter.

### Reader lists, rulings, cites

- **F25** (PREM-5) [V: (c) HOLDS]. The reader lists are incomplete: (a) asker readers in `span_cards.md`
  :865, `span_pick.md` :45/:51/:369/:408, `window_site.md` :336, `trace_format.md` :178-183 and `kit.h`
  :559-560; (b) the historical MF_SITE_ABI class has about 150 hits, not 8 (the disposition holds, but it
  is stated as a closed census); (c) plan row [SEAM-READER-CENSUS]'s trigger is "the next MF_SITE_ABI layout
  event", which 3.0b is, and the design does not name it; (d) the `memfn.h` :1483-1486 comment.
  **FIX-NOW (doc)**; (c) is for main to rule (does 3.0b fire it?).
- **F26** (PREM-6) [V: HOLDS]. `mf_wdecide` keeps its `wf_dec` off the art's arena "because the ask is
  pure", but the frame part's code allocates from the arena, and no purity check sees arena growth.
  **FIX-NOW**: the shared plan function takes an allocator, or the rule is restated and an arena-growth
  check is added.
- **F22** (SLOT-9) [not re-verified]. R-35 (a) names `site_kind` as stated per frame at phase 1; ASK-1 states
  it UNSTATED. That may be right, but it narrows a ruled item silently. **DOC**: §4.2 says so and why, and
  main confirms.
- **F23** (SLOT-10) [not re-verified]. Q10's D186 home is sound, but the addendum must quote the owner's
  own sentence as the ruling and record the triple as the kit's reading. Ruling (2) (row 1 waits) has no home
  on main. **DOC (main's)**.
- **F27** (PREM-7) [checked by PREM]. Cite nits: the layer is set at `finder.c` :650, not :647 (and §10
  inherits the error); `PURITY_FLOOR` is at :132; "exactly `wf_b_render`'s next column" holds for
  B-pair..B-hors only, since B-fn has none and the floor's is in `wf_floor_expr`; vrun's `if (m) return i +
  ctz(m)` is a ONESHOT-shaped answer when the trim leaves no compare. **DOC**.

## Readiness (coordinator's overall view, not a lens verdict)

**Not ready; ready after a rev 2 with the listed text fixes and a narrow re-check.** None of the findings
says the direction is wrong. F1-F5 are answer-level: built as written, the split or the plan function
would change bytes, refuse compiles, or turn the correct build's witnesses red. Each fix is a sentence or a
column. F8-F12 and F14 change what crosses the seam or how it is keyed, and must be settled before 3.0b
freezes MF_SITE_ABI. The kit manager could let 3.0a's split commit start once F1-F5 and F10/F11 are in the
text. The witness findings (F21, F28-F34) are 3.0a/3.0b test-plan text.

Recommended: a D27 spec-first test author for 3.0b's seam contract (`mf_wdecide` + `mf_wcall` +
`mf_wreply`'s frame part), written from §2.2-§2.3 alone. The launcher decides.

## PROBED-AND-HELD (consolidated; case counts in each critic file)

- The selection identity of the renderable set over every (frame, T-FIND row) today, plus Table S
  reproducing the `next` column (SPLIT: 6/6 rows; composer x 6 rows; E-find x 5 picks).
- The D-hors probe-miss respell is byte-identical (SPLIT on 4 hors witnesses, SLOT, SEAM, PREM by reading).
- Variable naming is independent of the row, the split of `hl` vs `hors_table` is order-free, the shift
  table's define position holds, and B-fn's text is unchanged (SPLIT, about 30 compiles).
- The two phase-1 askers; ASK-1's values = `ofs_site_define`'s; the plan face calls no hook (11 call sites);
  the decision is frame-free today; F5's three facts; the symbolic MF_SITE_ABI and MF_CLASS_V readers are
  complete; the `mf_wdecide` caller list is complete; no spec or guide hunk is owed (PREM, about 60 cites).
- D80, D76/D94, D153 overlap low (one extra contact: `finder.c` :176's FLD_policy macro, U2), D157, and
  [SP1E-RENDERER-TABLE] in substance (SLOT, SEAM).
- Sabotage rows A, C, F, G, H (for `stream`), I, K, L (E-find) and M (LIBC) reach and go red (SAB, 14 rows
  plus 5 goal checks reasoned).
- The equal-reply search: 5 of 7 pairs are distinguished by the reply (SEAM).

## By-id completeness

PREM-1..7 -> F6, F7, F25, F26, F27, F2/F3 (PREM-4), F1 (PREM-2), F14 (PREM-7 last). SPLIT-1..6 -> F1, F2,
F4, F5, F3, F9. SAB-1..11 -> F28, F7, F1, F29, F30, F31, F21, F3, F32, F33, F34. SLOT-1..11 -> F10, F11, F9,
F8, F18, F19, F20, F21, F22, F23, F24. SEAM-1..7 -> F12, F13, F16, F14, F15, F8, F17. All 42 raw findings
map to F1-F34; none was dropped.

## Lessons for the guide (proposed)

- A design that SPLITS an existing row table should list every per-row branch in the consuming function
  (`if (w->bren == B_PAIR)`), not only the table's columns. Three critics found the same uncolumned piece
  (F2), and the floor's different skeleton (F3).
- A design that re-labels what an accessor returns must grep the accessor's readers. F1 would have turned
  the correct build red; three critics found it independently.
- "Written from the ruling's text" pins: check which rows the ruling's text actually states (F21).

## Files

Critic texts, `verify.md`, COMMON and the verifier brief: `review/` beside this file.

## Rulings (kit manager, 2026-11-07)

- Every PROPOSED FIX-NOW is ACCEPTED: F1-F7, F8 (the D77 trim), F9-F15, F20, F21, F24-F26 and F28-F34. DOC and PLAN items are accepted as proposed. They go to rev 2, on lane/memfn-u30d.
- F8, the owner's ruling: Frank's "Yes" was given to the explicit three-piece question ("Adopt search, stream, check as composed pieces"). The stream IS a separately chosen piece in the direction. 3.0 still builds no unbuilt stream (D77): MASK is declared in the enum; the S-mask code and the italic support rows go to a NOTE carried to the finder unit. The ruling's record goes to main as a proposed D-entry (memfn/docs/responses.md, 067aca4df), which answers the FREEZE NOTE.
- F13: accepted. The reply names the triple per rung; §6's FIXED columns name the layer and target.
- F14: the fused row's reply crosses its FACTS (the pick it implements, PAIR or LIBC, through fn_rows BODY), never a C arm name.
- D27 spec-first author for 3.0b's seam contract: ACCEPTED, at 3.0b's build.
- Process change (quote a ruling held only in a denied ledger verbatim in COMMON, with a ready plain-grep exclude string): ACCEPTED for the critic skill.
