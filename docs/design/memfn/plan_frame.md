# plan_frame — span_pick unit 3.0, "the plan takes the frame" (design, rev 0)

**Status: PROPOSED, rev 0 (lane u30d, 2026-11-07). Design only: no build go, no code, no make, no timing.**
It serves kit request R-35 item 2 (`memfn/docs/requests.md` :805, ruling (a)). It is the design of the
first stage-3 step in `span_pick.md` §Staging (:408). Its shape follows `span_cards.md`. Code cites
were checked by grep at this worktree (branch lane/memfn-u30d, cut from main 5c3b65fb3).
`span_pick.md`'s own cites are older (2636dee99); where they have drifted, §10 gives the current line.

Read §0 first, then §2 (what crosses the seam) and §5 (the units).

## 0. The decisions, one line each

| # | question | decision | where |
|---|---|---|---|
| 1 | what pcrec states at phase 1 | the FRAME of the site the reply's NEXT rows define, stated on the ask's site itself (form, op, handoff, empty, use, body, decl_point, site_kind, `pred.fn_ref`) plus that define's hooks and its call kind. Today only the DFA prefilter's ask has NEXT readers; for it the frame is the offset-skip block's (FUNC/RETURN, kind UNSTATED). The run window's ask states NO frame | §2.1 |
| 2 | what the call takes | `mf_wdecide(art, site, def, call, out)`. `def` is the define hooks. `call` is a new fact `mf_wcall`: UNSTATED (refused), NONE (decision only), DEFINE (as `mf_define`), EMIT (as `mf_emit`: the phase set DEFINE and USE) | §2.2 |
| 3 | what the reply grows | appended LAST: `framed`, `frame_row` (T-FRAME's row), `method` (T-FIND's deciding row), `renderer` (the renderer row), `resume` (`mf_wresume`: NEXT or SHIFT). Each is a kit row id or an enum, never C text. The decision fields are unchanged and stay frame-independent in 3.0 | §2.3 |
| 4 | the asker fact | RETIRED. It is replaced by ONE declared renderer table keyed by (frame row, pick). A T-FIND row holds only where the asking frame has a renderer row for its pick (review 2026-11-05-r2 F5/F9; plan row [SP1E-RENDERER-TABLE]). `SF_ASKER_PAIR` (bit 15) and `fd_stop.renders_pair` are deleted | §2.4 |
| 5 | the numbers | one MF_SITE_ABI event (the next number at landing; 25 at this tree). MF_CLASS_V does NOT move: no finder row moves ahead of the PRES rows, and `mf_class` gains no member | §3 |
| 6 | the split | the kit owns the renderer table, the plan function and the seam. pcrec owns five asks (§4.2), all facts and checks | §4 |
| 7 | units | TWO. **3.0a** is kit-only, with no seam move: the renderer table, the asker's retirement, and one internal plan function that computes the frame part. **3.0b** is the seam plus pcrec's asks, in ONE commit: the MF_SITE_ABI event | §5 |
| 8 | left to row 1 | every priced row and every frame-DEPENDENT decision. Row 1 also needs a CONTROLLED candidate set: the inline one-member finder is a new method with its own card, before row 1. The only thing 3.0 must carry for it is the `renderer` field | §6 |

## 1. Goals

Ranked; a higher goal wins a conflict (`docs/dev/guide/architecture.md`).

| # | goal (who benefits) | measurable form |
|---|---|---|
| 1 | **No emitted byte moves** (every user; `span_pick.md` Goal 2's stage-3 cell for a unit change, D186) | `scripts/emit_sweep.py` byte-identical against each unit's NAMED base commit on EVERY arm: default, each `--memfn=no-X` deny, `--engine=vm`, both SIMD layers. Stamps are included. The input is the corpus plus `span_pick.md` §Staging's three `--patterns-file` inputs. `*_movers.txt` unchanged. No pcrec abi number moves. **No card's form hash moves**: `arm_fixtures --hash` prints the same hash for every form id at base and HEAD, and `finder_check.py` check C's stale count over zen4-grid3@1's recorded `kit:form.<id>=<hash>` deps stays 0 (§9 Q3) |
| 2 | **The reply is the define's** (row 1's lane; pcrec's NEXT readers) | for every FRAMED ask, every reply field (the decision and the frame part) equals what the define of the same site, hooks and call selects. Held by two trace-build checks: the kit's at every window-site define (§5, 3.0b) and pcrec's at the offset-skip define (ASK-3). Each check runs on two populations: the corpus, and the G2 window generator's framed asks in EVERY frame G2 renders. G2's own tally floors each frame row (E-func, E-stmt, E-find, E-generic) at >= 1 framed ask (K35) |
| 3 | **The plan face stays pure and writes nothing** (the next editor; D186 add. 2; memory `pcrec-plan-as-text-seam`) | 1d's purity harness, extended to framed asks interleaved with defines, compares every new field. Table E and B rows join `purity_rows.tsv`'s reach table. A COUNTING HOOK asserts that a framed ask makes **0** hook callback calls (`fn_name`, `table_name`, `member`, `note`, `note_tag`, `on_cand`): the plan reads only whether a hook is stated, its `miss` token and its text's class, never a callback |
| 4 | **One mechanism for "this frame renders this pick"** (the next editor; memory `pcrec-general-mechanisms-not-special-cases`) | `decider_census.tsv` names ONE renderer table for T-FRAME's renderer question. A backstop grep finds no `renders_pair` or `SF_ASKER_PAIR` in `memfn/`, `src/` or `tests/`, outside history (the journal, `finder_history.md`, lane reports). The renderability check has a WITNESS: removing it makes the composer pick PAIR on a two-member stop, and the compile is refused (§5 row C) |
| 5 | **What 3.0 adds is facts, not C** (Frank 2026-11-07: "we will eventually output code as either C or Rust") | every member 3.0 adds to `memfn.h` is an enum or a row-id string drawn from a kit table, never text an emitter pastes. A check asserts each reply id resolves in its table's listing: `method` in `mf_finder_rows`; `frame_row` and `renderer` in the renderer table's and Table E's ids |

**Non-goals.** Any priced row, and any decision change: KEY, M and TIE stay frame-independent. A consumer
kind on OFS sites (its own trigger). Presence joining the call. A frame for pre-check parts (§7 Q1).
Target and layer as plan inputs: they are art facts (target seam K0-U3), and T-FIND stays the OFF variant's
(`finder.c` :647, §1.5 rule 1). Serializing the hook callbacks ([IR-FORM]). The composer stating an
`fd_stop` (F5's second half, §2.4).

## 2. What crosses the seam

### 2.1 What pcrec states at phase 1, per NEXT row's frame

Today two pcrec callers make the phase-1 ask (`grep -rn mf_wdecide src`). Every other window scenario
makes no phase-1 ask. Those are the PF find, the VM hat's seek, MLINE, LMHIT and the cover/REPORT site.
For them the define, and `mf_ask` before it, IS the plan call, and it already carries the frame, the
hooks and the phase set (`find_site`, `emit_dfa.c` :6922-6936; `pcrec_cover_site`, `known.c` :488-496;
`cand_ask`, `emit_dfa.c` :8352). pcrec states nothing new for them.

| phase-1 ask | NEXT rows that read its reply | the site those rows define | what pcrec states at phase 1 (3.0b) |
|---|---|---|---|
| the DFA prefilter, `window_reply_ask` (`emit_dfa.c` :7604-7616, asked at :4792) | `run-pinned-bounded`, `run-pinned`, `offset-set-bounded`, `offset-set` (:10471-10500), by the key map `next_keys` (:7298-7306, :7317-7321); also `ofs_test_of` (:7402-7412: the block's comment and the OFFSETS stamp) and `dfa_form_derive`'s RE-SEED refusal (:13002) | the offset-skip block, `ofs_site_define` (:7622-7642) | **form** FUNC, **op** FIND, **handoff** RETURN, **empty** MISS, **use** POSITION, **body** ONESHOT, **site_kind** UNSTATED (0: OFS sites state no kind, `span_pick.md` :131's named exception), **decl_point** 0, **on_miss_leaves** 0, **pred.fn_ref** 1; the window statement `ofs_window_of` with floor SUBJECT (unchanged); **def** = {`fn_name` stated, `table_name` stated, `miss` MF_MISS_N, `comment_tier` NONESSENTIAL}; **call** DEFINE. These are exactly the values the block's define states |
| the same ask | the rows below the offset rows (`handoff-reentry`, `first-*`, `memchr*`, `byte-class*`), reached where no key holds | each defines its OWN PF site (`pf_site_of`, :7131-7146) over its own statement (`pf_window_of` with its own set and offer) | nothing: these rows read no reply field. Their define is their plan call. §7 Q2 covers a priced row on this choice |
| the run window, `req_run_member` (`emit_dfa.c` :1058-1076) | none: the reply's reader is the run member (the part's scan, the `@idx`/REQ stamps, `req_set_leads_own`) | the pre-check's FUNC part, whose frame the KIT derives at the composite's define (`wf_part_site`, `window.c` :1984-2007, inside `wf_parts_prepare` :2031) | **call** NONE (decision only); `def` NULL. Its site's frame fields are not read |

**Why only the offset rows' frame.** The decision is frame-independent through 3.0. So any frame gives the
same decision, and the frame part is the one new answer. Only the offset rows render the asked statement:
the rows below define a different site. "Per NEXT row" therefore means one framed ask for the four offset
rows, which share one frame. The hooks `u` pointer may differ from the define's: the plan face never calls
a hook (Goal 3), so `u` is never dereferenced at phase 1 (`UnanchStart` holds no `DfaForm` yet).

### 2.2 What the call takes

```
typedef enum { MF_WCALL_UNSTATED = 0, MF_WCALL_NONE, MF_WCALL_DEFINE, MF_WCALL_EMIT } mf_wcall;
int mf_wdecide(const mf_art *, const mf_site *site, const mf_hooks *def, uint8_t call, mf_wreply *out);
```

- **UNSTATED** is refused (-1). There is no presumed value (memory `pcrec-no-silent-defaults`).
- **NONE**: the decision only, as today. The site's frame fields and `def` are not read (`wf_check(site, 0)`,
  as `window.c` :1226 does now). The reply's frame part is zero: `framed` 0, empty ids, `resume` 0.
- **DEFINE / EMIT**: the frame is the site's own fields. `wf_check(site, 1)` applies. Table E's walk runs
  under the gate phases the define would read: DEFINE, or DEFINE|USE for EMIT, as `mf_emit` does
  (`compose.c` :255-258, :1320-1325). `def` is the define hooks, or for EMIT the one-call hooks. The call
  returns -1 exactly where that define would refuse: `mf_ask`'s rule 1 (`compose.c` :1002-1042), for
  example a REPORT site that E-find does not render under `no-window-search`. The art's denies and
  `--memfn=` options apply, as at the define.
- The phase set crosses as a fact about the CALL, not as the kit's internal `MF_PH_*` bits: `memfn.h`
  exports no `MF_PH_` name (`grep MF_PH_ memfn/include/memfn.h`: none).
- **Purity** (D186 add. 2): the reply is a function of the site's facts (window and frame), the
  hooks' stated-ness and classes, the call, the art's denies/options, the measure set and the handed
  rates. It sets no art state, defines no handle and writes no text or trace record. Reach stays counted
  on the define (`span_pick.md` breaker (c)). Nothing is cached: the define recomputes the plan.

### 2.3 What the reply grows

Appended LAST to `mf_wreply` (`memfn.h` :1467-1482), because initializers are positional:

| member | type | value on a framed ask |
|---|---|---|
| `framed` | `uint8_t` | 1 (0 on NONE) |
| `frame_row` | `char[12]` | T-FRAME's row: `E-func`, `E-stmt`, `E-find` or `E-generic` (`window.c` :1616-1621) |
| `method` | `char[8]` (= `mf_result.row`'s width) | T-FIND's deciding row id (`D-hors`, `D1`, `D1c`, `D1w`, `PAIR`, `R7w`): on E-find, the window walk's row (`wf_find_decide`'s `brow`); on E-func/E-stmt, the composer's routed row where one decides (the value `mf_result.row` reports, `compose.c` :1316); `""` where no T-FIND row decides (E-generic has no find; a legacy frame that walks, e.g. E-func, where `fn_rows` BODY decides: the named exception, until OFS states a kind) |
| `renderer` | `char[48]` (= `mf_result.form_id`'s width) | the renderer row: on E-find, the B row (`B-fn`, `B-pair`, `B-memchr`, `B-walk`, `B-hors`, `window.c` :1802-1817); on the other rows, the arm the text is written by (the value `mf_result.form_id` reports) |
| `resume` | `uint8_t`, `mf_wresume` {NONE = 0, NEXT, SHIFT} | how the text moves past a candidate its plan rejects: SHIFT iff the method is D-hors (its shift table over the window), else NEXT (`c + 1`); NONE on an unframed ask |

`path` is unchanged. It names the decision path, and `+hors` stays a define-trace suffix (`window.c`
:1944-1945); `renderer` now carries that fact in the reply. The decision fields (`alt` .. `path`) are
frame-independent in 3.0, and the purity harness asserts it: a NONE ask and a framed ask of one site
answer equal decision fields.

**Who reads the new fields (D77).** 3.0 has two named readers: the two agreement checks (Goal 2) and
G2's per-frame tally. Row 1 and the trace come later. No artifact text or stamp reads them, so no byte moves.

### 2.4 The asker fact's retirement

**Today.** T-FIND (`fd_find`, `finder.c` :640-679) has two askers. The composer asks with `st` NULL; the
window family asks with `st` set and `renders_pair` the literal 1 (`window.c` :1840). The PAIR row's facts
include `SF_ASKER_PAIR` (`finder.c` :105-106, :289, set at :656). Review 2026-11-05-r2 F5 (:96-102) showed
the fact equals `st != NULL` and its false branch has no witness. It also showed D-hors is filtered only
by an ABSENT fact: the composer states no window. F9 (:124-130) named the general form: one renderer
table keyed by (frame row, pick, layer); a frame renders a pick iff a row exists. Its unlock (b), "3.0's
reply triple becomes a lookup", has 3.0 as its trigger. So does plan row [SP1E-RENDERER-TABLE]
(`plan.md` :835-839).

**3.0a.** ONE declared renderer table, `(frame row, pick) -> first-match renderer rows`:

- frame row `E-find`: today's `wf_brows` (B-fn and B-pair for PAIR, keyed by `b_fn_holds`; B-memchr for
  LIBC and LIBC_BACK; B-walk for WALK; B-hors for HORS);
- frame row `composer` (the arms that render E-stmt's translated site and every non-plan FIND site):
  today's `fd_renderers` (`compose.c` :272-292: LIBC by `end_back`, LIBC_BACK, WALK by `end_back`);
- layer: one wildcard column, as declared today (no row is layer-keyed; the SIMD rungs stay `fn_rows`
  PREFIX and vrun's KA/KB, the named exceptions with their census rule).

T-FIND's input carries the asking frame's RENDERABLE SET: the picks the table has a row for under that
frame. `fd_decide`'s row gate (beside `finder.c` :503) declines a row whose pick is not in the set. This
replaces `SF_ASKER_PAIR`, which is deleted; bit 15 is retired and never reused, like bits 6-8, 12 and 13.
It also replaces `renders_pair`, which is deleted. PAIR and HORS are then filtered by one mechanism, and
the composer's refusal of an unrenderable routed pick (`compose.c` :262-268) becomes unreachable by
construction rather than by absent facts. The false branch gains a witness: `find_facts` states
SF_TWO_MEMBER on a composer site's two-member set at offset 0 (`finder.c` :555, :567-574), so with the
check removed the composer would pick PAIR and refuse (§5 row C).

`fn_rows` BODY, the third member F9 names, stays a named exception. Its trigger is "pcrec states a kind
on OFS sites". F6's one renderer-row struct is folded in where the table's rows need it. The composer
stating an `fd_stop` (F5's second half: one question shape) is NOT in 3.0. A RUN span needs a field
`fd_stop` lacks, and its trigger is the compose `arms[]` named exception's ("a kit request adds an arm").

**Every reader of the asker fact, found by grep** (`git grep -n 'asker\|renders_pair\|SF_ASKER_PAIR'`
outside history, lane reports and reviews):

| reader | disposition |
|---|---|
| `memfn/src/finder.c` :37-38, :105-106, :217-222, :289, :594-618, :656 | the bit and its setter deleted; the PAIR row's facts become `SF_SPAN0 \| SF_TWO_MEMBER`; comments restated ("the frame renders PAIR"); the renderability check added at the row gate |
| `memfn/src/kit.h` :531-556 (`fd_form`'s "each asker renders", `fd_stop.renders_pair`, `fd_find`'s comment) | `renders_pair` deleted; `fd_stop` (and the composer's path) gain the renderable set; comments restated |
| `memfn/src/window.c` :37 (header), :1840 (`.renders_pair = 1`) | deleted: E-find's renderable set comes from the table |
| `memfn/src/compose.c` :262-292 (`fd_renderers`, `fd_renderer`) | moved into the one table (its composer rows) |
| `memfn/src/formhash.c` :272, :446 (comments) | reworded ("E-find renders PAIR"); the code at :472 reads `wf_plan_brow` and stays valid if the accessor stays |
| `memfn/src/CLAUDE.md` :9 ("for both askers"), :15 ("holds on the asker fact `SF_ASKER_PAIR`"; "each asker renders the pick by its own renderer rows"), :41 (Table B's renderer rows) | restated |
| `tests/memfn/decider_census.tsv` :24 (`fd_find`'s note), :29 (`fd_renderer` -> the table), :66-67 (`wf_find_decide`, `wf_prepare`: "at text time" -> the plan) | rows edited by 3.0a; `decider_census.py`'s backstop re-run |
| `memfn/docs/finder_history.md` | a dated row for the PAIR row's facts edit (§1.8: every row edit is logged) |
| `docs/design/memfn/span_pick.md` :109, :135, :420 | the named exception retires: amendment §8 (the note's own next revision) |
| `docs/dev/plan.md` :835-839 [SP1E-RENDERER-TABLE] | closed by 3.0a (main's edit) |
| NOT readers | lane reports and review records (history); `docs/design/stream/roadmap.md` :90/:121/:128/:716 (the R12 "asker" there is pcrec's start-table hand asker, a different thing) |

## 3. The number events and their same-commit package (readers by grep, D76/D94)

**MF_SITE_ABI**: 24 -> the next free number at landing of 3.0b (25 at this tree). The target seam's
U2/U3 is also a kit seam event. Whichever lands second takes the next number and re-baselines (§5).
Readers (`git grep -n MF_SITE_ABI`), by class:

| class | readers | disposition |
|---|---|---|
| the definition and its history | `memfn/include/memfn.h` :39-204 | a new entry: "`mf_wdecide` takes the frame (the site's frame fields, the define hooks, `mf_wcall`); `mf_wreply` gains `framed`, `frame_row`, `method`, `renderer`, `resume`, appended LAST; `mf_wcall` and `mf_wresume` added. No MF_VOCAB or MF_CLASS_V move; no pcrec byte moved" |
| prose that states the CURRENT number | `memfn/include/CLAUDE.md` :4 ("`MF_SITE_ABI` 24 (24: ...)") | becomes the new number with its one-line entry |
| symbolic readers (they move with the macro) | `src/gen/memfn_sites.c` :455; `memfn/src/compose.c` :1011, :1067-1069; `window.c` :1226, :1419; `presence.c` :124; `formhash.c` :381; `memfn/tests/g2/g2_gen.c` :923, :2259, :2294, :3754, :3790, :3834, :4200, :4430-4431; `g2_simd_gen.c` :334; `g2_win_gen.c` :630, :737, :793, :837; `tests/memfn/arm_fixtures.c` :238; `mass_check.c` :258; `proof_check.c` :156; `proven_check.c` :63 | recompile only |
| historical `MF_SITE_ABI n` (n <= 24): comments, refusal texts, sabotage anchors | `compose.c` :588, :624, :776, :820, :908; `fields.def`; S1089 (:24-26), S2903 (:13-14, anchors on `compose.c` :908's text) | unchanged: each names the event that introduced its rule, and every anchor's text stays byte-identical |
| literal pins | none: G2 is symbolic (`MF_SITE_ABI + 1`), and the `site abi %u, kit abi %u` refusal is asserted by kind only (`G2M6_REPORT.md` :131, :243) | the grep is re-run at landing |
| the ledgers | `memfn/docs/journal.md`, `memfn/docs/responses.md` ([responses] R-35 3.0b) | entries in the same commit |

**MF_CLASS_V**: stays 8. It moves on an `mf_class` layout change or on a finder-row index shift ahead of
the PRES rows (`memfn.h` :1080-1098). 3.0 adds, removes and reorders no finder row (PAIR's FACTS change,
not its index) and adds no `mf_class` member. Its readers stay as they are: `memfn.h` :1080,
`window.c` :2790, `compose.c` :390, :1029, `proof_check.c` :408, `arm_fixtures.c` :386,
`memfn/include/CLAUDE.md` :4, `memfn/src/CLAUDE.md` :11. All are symbolic or prose. Putting the frame
part into `mf_class` instead would move it; that is REJECTED. The class answers what the text proves
(D157), and the frame part reports a selection.

**Same-commit package of 3.0b** (beyond the table above): pcrec's ASK-1..ASK-5 (§4.2). The callers
`arm_fixtures.c` :2271, :2278, :2305, :2323 and `g2_win_gen.c` :742, :797, :855 (build breaks).
`pur_diff` (`arm_fixtures.c` :2204-2220) and the control print (:2330-2335) gain the new fields.
`run_finder.sh` :133's `PURITY_FLOOR` 1157 is an EXACT literal, re-pinned to the new count with its
reason. `purity_rows.tsv` gains the Table E and B rows (REACH or UNREACHED with a reason, its own id check
re-run). `g2_win.h` :44-53's reply copy grows. `memfn/docs/trace_format.md` :102-113 ("`mf_wdecide` ...
writes none" stays true; the frame part is named). The comments that teach "the decision reads no frame
fact" are restated: `memfn.h` :556-558 ("read by phase 2 only"), :1435-1441 ("never a frame fact"),
`window.c` :49, :1225, `emit_dfa.c` :7598-7603. Also `memfn/include/CLAUDE.md` and `memfn/src/CLAUDE.md`.
**No pcrec abi bump** (no byte moves). **No `docs/spec/` hunk** (D80 not triggered: no spec file names
`mf_wdecide`, `mf_wreply` or the asker, `git grep` over `docs/spec` and `docs/guide`).

## 4. The split

### 4.1 Kit-side edits (the kit's lanes; `memfn/` and the kit's tests)

3.0a: the renderer table and the renderable set (§2.4); one internal PLAN FUNCTION that computes the
decision and, given a frame, T-FRAME's row, T-FIND's row, the renderer row and the resume. Both
`wf_prepare` (the define and `mf_ask`, `window.c` :1892) and `mf_wdecide` read it. The census rows, the
finder history row, the CLAUDE.md lines, and 3.0a's tests (§5).
3.0b: the seam (§2.2, §2.3), `reply_of`'s frame part, the MF_TRACE agreement check at `define_sel`
(beside rule 2's re-ask, `compose.c` :1180-1200), the harness and G2 edits, the ledgers.

### 4.2 pcrec-side asks for main to file (facts and checks, never the kit's method, D157)

R-35 ruling (a) puts these hunks in the kit's 3.0b package. Main reviews them, and the unit's code round
covers both sides.

| # | ask | the exact facts |
|---|---|---|
| ASK-1 | the DFA prefilter's phase-1 ask states the frame of the site its offset rows define | on the ask's site: form FUNC, op FIND, handoff RETURN, empty MISS, use POSITION, body ONESHOT, site_kind UNSTATED (0), decl_point 0, on_miss_leaves 0, `pred.fn_ref` 1; the window statement `ofs_window_of` and floor SUBJECT, as today; define hooks `fn_name` and `table_name` STATED, `miss` MF_MISS_N, `comment_tier` NONESSENTIAL (other members unstated, as at the define); call DEFINE. Each value equals `ofs_site_define`'s (`emit_dfa.c` :7622-7642), checked by ASK-3 |
| ASK-2 | the run window's ask states no frame | call NONE, `def` NULL (`req_run_member`, `emit_dfa.c` :1058-1076); unchanged otherwise |
| ASK-3 | the offset-skip block's define holds the reply it was planned by | in a pcrec trace build (the `PCREC_CAND_TRACE` precedent `cand_asked_hold`, `emit_dfa.c` :7066-7085): at `ofs_site_define`, re-ask `mf_wdecide` with the define's own site, hooks and call DEFINE. EVERY reply field (decision and frame part) must equal `UnanchStart.wr`; a difference fails the compile as a named invariant ("asked-plan-differs") |
| ASK-4 | ASK-3 runs and reaches its site | name the suite whose trace build runs over DFA prefilter sites (candidates: `tests/codegen/run_cand_oracle.sh` :90, `run_fallback_table.sh` :143), and prove reach with a pcrec-side sabotage row (§5 row F) |
| ASK-5 | the comments that teach the frame-free ask are restated | `emit_dfa.c` :7598-7603 ("the decision reads no frame fact, so one ask serves every NEXT row"), and `UnanchStart`'s `wr` comment (:4630-4636): the ask states the offset rows' frame; the rows below define their own site |

**Not asked**: a consumer kind on OFS sites; a frame for pre-check parts (§7 Q1); any frame on the
define-only scenarios (they have one already); any NEXT-row change; any stamp, CLI or spec change.

## 5. Build plan: two units

`[span_cards.md rev1 COST-4]`'s rule applies. Each unit names its BASE commit (main's tip at branch time)
in its first commit; every identity witness compares against it. After any byte-moving lander on main,
an unlanded unit re-merges main, takes a new named base and re-runs its witnesses. **Sabotage ids are the
kit's, taken at BUILD time from the top of the free range** and recorded in the unit's first commit. The
highest kit id at this tree is **S2981** (lane k0's S2975-S2981, `memfn/docs/journal.md` :3598, :3613), so
the next free is expected at S2982. Rows below are lettered. Heavy runs are boxqueue jobs, with no timing
and no window.

| unit | content | witness | heavy runs | sabotage rows (why each goes red) |
|---|---|---|---|---|
| **3.0a** the renderer table and the plan's frame part, kit-internal | §2.4's table and renderable set; `SF_ASKER_PAIR` and `renders_pair` deleted; the internal plan function (decision, then per frame: T-FRAME row, T-FIND row, renderer row, resume) read by `wf_prepare`; the census rows (§2.4), the finder history row, the CLAUDE.md lines. No seam, no pcrec edit | emit_sweep byte-identical on every arm against its base (Goal 1); G2 green (`run_g2_win.sh`, the finder G2); every form id's hash unchanged (`arm_fixtures --hash`, base vs HEAD) and check C's stale count 0; REACH EQUALITY (`MFTRACE REACH`, chosen and asked per row, base vs HEAD); `decider_census.py` green with its backstop; the Goal 4 grep empty | `make test` (normal, boxqueue); emit_sweep per arm | (A) E-find's PAIR renderer rows dropped from the table: formhash's `pair` instance (an E-find window site over `{X,x}`, `formhash.c` :444-473) no longer reaches T-FIND's PAIR, so `check_hash` refuses the id (`finder_check.py` via `run_finder.sh`). (B) the composer frame declared to render PAIR: T-FIND picks PAIR on a composer two-member stop, no composer arm renders it, and `select_arm` refuses. G2's composer sets with two members, and the corpus compile, go red. (C) the renderability check removed at the row gate: the same refusal as (B). This is F5's missing false-branch witness. (D) a second renderer list planted in an unlisted function: `decider_census.py`'s backstop is red |
| **3.0b** the seam, with pcrec's asks, ONE commit | §2.2-§2.3; `reply_of`'s frame part; the kit's MF_TRACE agreement at every window-site define (the plan re-asked with the define's site, hooks and call; every field compared); ASK-1..ASK-5; the purity harness (framed asks interleaved with defines, `pur_diff` over the new fields, the COUNTING HOOK, `PURITY_FLOOR` re-pinned, `purity_rows.tsv`'s E and B rows); G2's window generator asks framed in the frame each site is defined in, holds the reply's frame part to `mf_defined` (`form_id` = `renderer` on non-E-find rows, `row` = `method` where the composer routes), and floors each frame row >= 1; the reply-id resolution check (Goal 5); §3's package | as 3.0a, plus the two agreement checks green on the corpus and on G2; purity green at its new count; the counting hook at 0 | `make test` (normal, boxqueue); emit_sweep per arm; the ASK-4 suite | (E) `reply_of` writes the frame row of another walk (plant: always `E-generic`): the kit's MF_TRACE agreement check at the define is red (`run_finder.sh` and G2's MF_TRACE kit, `mk_mftrace_lib.sh`). (F) pcrec-side: ASK-1's ask states STMT/ASSIGN: E-stmt is not E-func, so ASK-3's check is red on every DFA prefilter site (the ASK-4 suite). (G) the plan face calls `table_name` once: the counting hook reads 1 (`arm_fixtures --purity`). (H) the renderer row's choice keyed on `art->nsites` (B-fn iff `nsites > 0`, 1d's plant pattern): purity is red, and its control print moves (the plant is reached). This also proves `pur_diff` compares `renderer`. (I) a framed ask walks Table E without the art's denies: the fixture "framed ask on a REPORT site under `no-window-search` answers -1, as `mf_define` refuses" is red (`arm_fixtures`). (J) a reply `method` filled from the renderer column: the id-resolution check is red (Goal 5) |

**Separability.** 3.0a lands and reverts alone: it moves no seam and touches no pcrec file. 3.0b needs
3.0a, because the frame part comes from 3.0a's plan function, so reverting 3.0a after 3.0b takes 3.0b
with it. 3.0b cannot be split: the signature change breaks pcrec's build without ASK-1/ASK-2. The
MF_SITE_ABI event, its callers and its checks are one commit (memfn/CLAUDE.md's same-commit rule).

**Concurrency and remodel overlap (D153).** The target seam's U2 edits `formhash.c`'s entry table and the
`FLD_policy` gate field. 3.0a edits `finder.c`, `window.c`, `compose.c` and `kit.h`, plus comments only in
`formhash.c`. The overlap is low: the later lander re-merges and re-runs the hash witness. The two
MF_SITE_ABI events take numbers in landing order. Opt rows on `window.c`, `finder.c` or `compose.c` wait
for 3.0b, as stage 1's did.

**Size.** 3.0a: S-M (one table, one input, one function split; no text moves). 3.0b: M (seam, about 12
readers, two checks, the harness growth).

## 6. What 3.0 leaves to row 1

**Left wholly to row 1** (`span_pick.md` :409-410): every T-PICK row. Any frame-DEPENDENT decision
(KEY and M meeting in T-PICK). With it the rule for unframed asks: a row that makes the decision read the
frame must decline on NONE asks, or define their answer. Otherwise `req_run_member`'s member and the
part's define could disagree, and ASK-2's existing loud check (`emit_dfa.c` :1071-1074) would fire.
Also row 1's: the method-level tie row (R19); verify priced over T-VERIFY's step list (R21); finder_check
L's digest masking (`[sp1g review F5]`); the DEFAULTS reader; the pre-check-part statement (§The pick 7);
M2; the movers census. 3.0 builds nothing for them beyond the frame part.

**The controlled candidate set** (Frank 2026-11-07: "speed compare should remove variables. Apples to
apples"). smp20's watched comparison today (`span_pick/smp20.out`, `memfn/docs/ideas.md` :780-785) sets
`{X,x}`@0 by PAIR (two streams, an inline loop) against `'/'`@1 by libc memchr (one stream, a call). These
differ in position and density, stream count, inline vs call, and own code vs libc, all at once. Row 1
needs:

1. **A new method first: an inline one-member finder at pair speed** (pair's machinery with one member,
   or SWAR has-byte; ideas.md :782-783). It is a T-FIND row, an E-find renderer row and its card (memory
   `pcrec-new-method-needs-measurement-card`). It is its own unit BEFORE row 1, triggered by the census0
   decomposition ideas.md names (:785). Without it, '/' has no inline candidate, and no pair in the set
   differs only in position.
2. **The candidate set as a grid over (position, method)**, restricted to the asking frame's renderable
   picks. 3.0a's renderer table is exactly that restriction. So each comparison the trace prints differs
   on ONE axis, or names both. For smp20 that gives four cells: `{X,x}`@0 PAIR, `{X,x}`@0 walk, `'/'`@1
   libc, `'/'`@1 inline-one.
3. **Evidence arms forced cell by cell** for the 588-style run, by test-only levers (`mf_lever`, R-30; no
   public deny for a lever, memory `pcrec-flag-follows-caller-effect`), so the per-axis effect is measured,
   not inferred.

**What 3.0's reply must carry for them: the `renderer` field, and nothing more.** Two candidates can share
a method and differ in C (B-fn's `ofsskip__body` vs B-pair's inline loop: smp05 vs pr09, `span_pick.md`
:114). So a record that names only the method cannot hold the C fixed. Adding `renderer` later would be
a second MF_SITE_ABI event, which is why 3.0b carries it. The candidates' prices and the grid belong to
the kit's trace, not the reply: the reply carries no price until whole-artifact pricing (`span_pick.md`
:84, rev5 C1).

## 7. Open questions (plain words, each with a recommendation)

| # | for | question | recommendation |
|---|---|---|---|
| Q1 | main | The run-window ask (`req_run_member`) only wants the run member. Should it state no frame, or the pre-check part's frame (FUNC/RETURN with the pre-check's kind)? | **No frame, for now.** The kit derives the part's frame itself (`wf_part_site`). If pcrec stated it too, there would be a second copy of that derivation. Revisit when a priced row applies on pre-check parts (`span_pick.md` §The pick 7) |
| Q2 | main, kit manager | Under the DFA prefilter, a PARKED reply sends the search to rows that define a DIFFERENT site (the PF find), whose frame the ask does not state. A priced choice between PARKED and RESEED by method cost would need both frames | **Leave it in 3.0.** OFS sites are not priced before they state a kind (`span_pick.md` :131), and that trigger also covers this. File a plan row: "the prefilter ask states each outcome's frame", trigger "pcrec states a kind on OFS sites" |
| Q3 | main | Should 3.0a merge the two renderer lists into ONE table, or keep two lists and only derive the renderable set from each? | **One table.** It is review r2's F9 general form and plan row [SP1E-RENDERER-TABLE]'s trigger is 3.0. It deletes a parallel list, and its benefit is the simplification itself (memory `pcrec-simplification-is-a-benefit`) |
| Q4 | kit manager | Should the reply's new fields be strings or enums? | **Row-id strings** for `frame_row`, `method` and `renderer`, as `path` and `mf_result.row` are: they are the kit's own names, they read as text when serialized, and they contain no C. `resume` is an enum (two values with a meaning) |
| Q5 | main | `span_pick.md` :86 says the frame (engine, target, layer) becomes a per-call input "from unit 3.0". Is that still meant? | **Read it as T-FRAME's frame** (form, handoff, kind, hooks, call). Target and layer are art facts under the target seam (K0-U3), and T-FIND keeps deciding on the OFF variant (`finder.c` :647). Amend :86 (§8) |
| Q6 | Frank | Should row 1 wait until the inline one-member finder exists, so that its first priced comparison is like-for-like? | **Yes.** Build that finder and its card as its own unit right after the census0 decomposition. Then open row 1 with the controlled grid of §6. Otherwise row 1's first verdict would again mix method, call style and position |

## 8. Amendments this design makes to other documents (each lands with its unit)

| document | amendment | unit |
|---|---|---|
| `span_pick.md` :109, :114, :135, :420, :423 | T-FIND and T-FRAME are asked at PLAN time on framed asks; the asker fact's named exception retires; N11's "plan-time at 3.0" is done | 3.0b (the note's own revision, by the kit) |
| `span_pick.md` :86 | the per-call frame is T-FRAME's; target/layer stay art facts (Q5) | 3.0b |
| `window_site.md` §0 and §2.4 ("the decision reads no frame fact") | a framed ask states the NEXT rows' frame; the decision itself is still frame-free in 3.0 | 3.0b |
| `docs/dev/plan.md` [SP1E-RENDERER-TABLE] | closed (main) | 3.0a |
| `memfn.h`, `memfn/include/CLAUDE.md`, `memfn/src/CLAUDE.md`, `trace_format.md`, `decider_census.tsv`, `finder_history.md` | §2.4 and §3 | 3.0a / 3.0b |

## 9. The three standing questions (docs/design/CLAUDE.md)

**Q1, the measurement regime: NOT RELEVANT.** 3.0 reads and produces no measured number. Its witnesses
are compile-only: artifact diffs, hashes and checks. The cards stay unread until row 1.

**Q2, the independent control: RELEVANT.**
- Byte identity is checked against the NAMED BASE's artifacts, diffed pcrec-side (emit_sweep), never
  against the kit's `moved` (K35).
- The kit's agreement check compares the plan call with the define's selection. The two share code by
  design, so it is a TRIPWIRE against a later divergence (a quiet-only branch, a cache). It is not the
  identity control.
- pcrec's check (ASK-3) compares two pcrec statements of one frame through the kit. Its subject is
  pcrec's statement, which the kit cannot make equal for it.
- Populations are counted by their owners: the corpus's DFA prefilter sites by ASK-4's suite, and the
  per-frame-row framed asks by G2's own tally with a floor per row (the corpus alone frames only E-func).
- Every sabotage row names the check that sees it and why that check can see it (§5). Reach is shown by
  a control (H) or by a corpus site the plant moves (A, B, C, F).

**Q3, what moves when data is regenerated: RELEVANT, narrowly.** 3.0 adds no table, stamp or generated
file, and re-measuring a set moves nothing (no reader). One existing reader of the TEXT does move with
3.0's code: the cards' recorded form hashes (zen4-grid3@1 rows' `kit:form.<id>=<hash>`). A hash that
moved would make cards stale. Goal 1 therefore requires every form id's hash unchanged, and check C's
stale count 0. A byte move would be an abi event (D76/D94), and 3.0 has none.

## STATE AT HANDOFF

Rev 0, lane u30d. Cites checked by grep at this worktree (main 5c3b65fb3 + the deliver file). No make, no
timing, no code. Not a build go: 3.0a and 3.0b each need the kit manager's ruling on §7 and a design
critic round, and R-35's build GO covers stage 3 (Frank 2026-11-06). OWED: none.
