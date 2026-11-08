# plan_frame — span_pick unit 3.0, "the plan takes the frame" (design, rev 1)

**Status: PROPOSED, rev 1 (lane u30d1, 2026-11-07), over rev 0 (lane u30d, 2026-11-07). Design only: no
build go, no code, no make, no timing.** Rev 1 applies Frank's two rulings of 2026-11-07 (§R1). Changed
text is marked `[rev1]`. Read §R1 first, then §0, §2.5 (the triple) and §5 (the units).
It serves kit request R-35 item 2 (`memfn/docs/requests.md` :805, ruling (a)). It is the design of the
first stage-3 step in `span_pick.md` §Staging (:408). Its shape follows `span_cards.md`. Code cites
were re-checked by grep at this worktree (branch lane/memfn-u30d, tip a061437e5). Its code is byte-identical
to rev 0's tree (main 5c3b65fb3) and to main a678d0a4e under `memfn/`, `src/` and `tests/memfn/`: main's
only later commit touches `tests/fuzz/fuzz.py`. So every rev 0 cite stands, and the new ones are at the same
tree. `span_pick.md`'s own cites are older (2636dee99); where they have drifted, §10 gives the current line.

## R1. What rev 1 changed, by ruling

The rulings are recorded in the kit's journal, entry "11-07 ~23:00: RULED by Frank", and in its
`responses.md` notice "proposed decision entry", both on lane/memfn-k1107.

| ruling or brief item | what rev 1 changed | where |
|---|---|---|
| Frank 2026-11-07: "Candidate search and candidate validation are two different primitive pieces that are composed." The kit manager reads this as a TRIPLE: (search, candidate stream, check) | 3.0's plan is the triple. SEARCH is T-FIND's method (with Table A's stop). The CANDIDATE STREAM is how the text moves past a candidate the check rejects: `ONESHOT`, `MASK` or `SHIFT`. The CHECK is T-VERIFY's plan (Table C). Each is a fact table. The C renderer composes them inline | §0 rows 3, 4a; §2.5 |
| brief 1: shape the reply as the triple | rev 0's `resume` (`mf_wresume` NONE/NEXT/SHIFT) becomes `stream` (`mf_wstream`: NONE, ONESHOT, MASK, SHIFT). `method` stays the search. The check is the reply's existing T-VERIFY group (`nplan` .. `run_len`); 3.0 names that group "the check" and adds no member for it. A declared table says which streams each search supports | §2.3, §2.5.2 |
| brief 2: split Table B, byte-identical | Table B splits into a SEARCH renderer table keyed by (frame row, pick), which is rev 0's renderer table kept as it was, a STREAM renderer table keyed by (frame row, stream), and a CHECK renderer row per composing frame. B-fn becomes a FUSED row, matched before composition. The split moves zero bytes: every text is the same spellings in the same order. The witnesses are rev 0's | §2.6 |
| brief 3: vrun and vany | vrun's rows are (vector search, MASK, a run compare trimmed by what the mask proved), today fused under fn-pair. They are re-expressed in a later zero-mover unit, not in 3.0. vany is a bare vector search consumed ONESHOT. It enters as a search piece only in the unit that routes it (D77) | §2.7 |
| brief 4: keep facts apart from C | the triple's tables (T-FIND, the support table, Table S, T-VERIFY) are facts. The renderer tables are the C emitter's, and a Rust emitter would replace only them. Rev 0's reply member `renderer` (a C renderer's id) is REPLACED by `fused`, the id of a renderer that renders the whole triple as one piece; it is empty where the triple is composed | §2.3, §2.8; Q7 |
| brief 5 / Frank 2026-11-07: row 1 waits for an inline one-member finder and its measurement card | rev 0's Q6 is answered (yes) and dropped. §6 is restated: row 1 waits. It names the controlled comparisons row 1 runs, each varying ONE piece. Row 1 is not designed here | §6, §7 |
| brief 6: cites, asks, units, sabotage, questions | cites re-checked (above, and the report's table). The pcrec-side asks keep their facts; only ASK-3's field list changes. 3.0a gains the split, Table S and the support table, so its size is now M. Sabotage rows K-N are added to 3.0a and A, H, J are restated. The next free kit id is S2982 (by grep: S2981, lane k0, is the highest on any branch). Q4 is restated; Q7-Q10 are new | §4.2, §5, §7 |

## 0. The decisions, one line each

| # | question | decision | where |
|---|---|---|---|
| 1 | what pcrec states at phase 1 | the FRAME of the site the reply's NEXT rows define, stated on the ask's site itself (form, op, handoff, empty, use, body, decl_point, site_kind, `pred.fn_ref`), plus that define's hooks and its call kind. Today only the DFA prefilter's ask has NEXT readers, and for it the frame is the offset-skip block's (FUNC/RETURN, kind UNSTATED). The run window's ask states NO frame | §2.1 |
| 2 | what the call takes | `mf_wdecide(art, site, def, call, out)`. `def` is the define hooks. `call` is a new fact, `mf_wcall`: UNSTATED (refused), NONE (decision only), DEFINE (as `mf_define`) or EMIT (as `mf_emit`: the phase set DEFINE and USE) | §2.2 |
| 3 | what the reply grows `[rev1]` | appended LAST: `framed`, `frame_row` (T-FRAME's row), `method` (the SEARCH: T-FIND's deciding row), `stream` (`mf_wstream`: ONESHOT, MASK or SHIFT) and `fused` (the id of a renderer that renders the whole triple as one piece, else empty). The CHECK is the reply's existing T-VERIFY group. Each new member is a kit row id or an enum, never C text. The decision fields are unchanged and stay frame-independent in 3.0 | §2.3 |
| 4 | the asker fact | RETIRED, replaced by ONE declared SEARCH renderer table keyed by (frame row, pick). A T-FIND row holds only where the asking frame can render its pick, and `[rev1]` one of its supported streams (review 2026-11-05-r2 F5/F9; plan row [SP1E-RENDERER-TABLE]). `SF_ASKER_PAIR` (bit 15) and `fd_stop.renders_pair` are deleted | §2.4 |
| 4a | the triple `[rev1]` | three fact tables composed by the renderer: T-FIND (search), the SUPPORT table plus Table S (stream, first match: SHIFT where the search supports only SHIFT, MASK where it supports MASK and the frame renders MASK, else ONESHOT), and T-VERIFY (check). The renderer tables (search, stream, check) are Table B split, and the split moves zero bytes | §2.5, §2.6 |
| 5 | the numbers | one MF_SITE_ABI event (the next number at landing; 25 at this tree). MF_CLASS_V does NOT move: no finder row moves ahead of the PRES rows, and `mf_class` gains no member | §3 |
| 6 | the split | the kit owns the fact tables, the renderer tables, the plan function and the seam. pcrec owns five asks (§4.2), all facts and checks | §4 |
| 7 | units | TWO. **3.0a** is kit-only, with no seam move: the triple's tables, Table B's split, the asker's retirement, and one internal plan function that computes the frame part. **3.0b** is the seam plus pcrec's asks, in ONE commit: the MF_SITE_ABI event | §5 |
| 8 | left to row 1 `[rev1]` | every priced row and every frame-DEPENDENT decision. RULED (Frank 2026-11-07): row 1 WAITS for the inline one-member finder and its card. Row 1's comparisons each vary ONE piece of the triple. 3.0 carries the triple in the reply; nothing else is built for row 1 | §6 |

## 1. Goals

Ranked; a higher goal wins a conflict (`docs/dev/guide/architecture.md`).

| # | goal (who benefits) | measurable form |
|---|---|---|
| 1 | **No emitted byte moves** (every user; `span_pick.md` Goal 2's stage-3 cell for a unit change, D186) | `scripts/emit_sweep.py` byte-identical against each unit's NAMED base commit on EVERY arm: default, each `--memfn=no-X` deny, `--engine=vm`, both SIMD layers. Stamps are included. The input is the corpus plus `span_pick.md` §Staging's three `--patterns-file` inputs. `*_movers.txt` unchanged. No pcrec abi number moves. **No card's form hash moves**: `arm_fixtures --hash` prints the same hash for every form id at base and HEAD, and `finder_check.py` check C's stale count over zen4-grid3@1's recorded `kit:form.<id>=<hash>` deps stays 0 (§9 Q3). `[rev1]` This covers Table B's split (§2.6): the split is a refactor with zero movers |
| 2 | **The reply is the define's** (row 1's lane; pcrec's NEXT readers) | for every FRAMED ask, every reply field (the decision and the frame part) equals what the define of the same site, hooks and call selects. Two trace-build checks hold it: the kit's at every window-site define (§5, 3.0b) and pcrec's at the offset-skip define (ASK-3). Each check runs on two populations: the corpus, and the G2 window generator's framed asks in EVERY frame G2 renders. G2's own tally floors each frame row (E-func, E-stmt, E-find, E-generic) at >= 1 framed ask, and `[rev1]` each produced stream (ONESHOT, SHIFT) at >= 1 (K35) |
| 3 | **The plan face stays pure and writes nothing** (the next editor; D186 add. 2; memory `pcrec-plan-as-text-seam`) | 1d's purity harness, extended to framed asks interleaved with defines, compares every new field. Table E and B rows, and `[rev1]` Table S's rows, join `purity_rows.tsv`'s reach table. A COUNTING HOOK asserts that a framed ask makes **0** hook callback calls (`fn_name`, `table_name`, `member`, `note`, `note_tag`, `on_cand`): the plan reads only whether a hook is stated, its `miss` token and its text's class, never a callback |
| 4 | **One mechanism for "this frame renders this piece"** `[rev1]` (the next editor; memory `pcrec-general-mechanisms-not-special-cases`) | `decider_census.tsv` names ONE search renderer table, ONE stream renderer table and ONE support table, and no other list answers those questions. A backstop grep finds no `renders_pair` or `SF_ASKER_PAIR` in `memfn/`, `src/` or `tests/`, outside history (the journal, `finder_history.md`, lane reports). The renderability check has a WITNESS: removing it makes the composer pick PAIR on a two-member stop, and the compile is refused (§5 row C). The support table equals a pin written from the ruling's text (§5 row M) |
| 5 | **What 3.0 adds is facts, not C** (Frank 2026-11-07: "we will eventually output code as either C or Rust") | every member 3.0 adds to `memfn.h` is an enum or a row-id string drawn from a kit table, never text an emitter pastes. A check asserts each reply id resolves in its table's listing: `method` in `mf_finder_rows`, `frame_row` in Table E's ids, `[rev1]` `fused` in the fused renderers' ids (the composer arms' form ids and `fn_rows`'), and `stream` in `mf_wstream`'s range. In 3.0 no reply carries MASK (it has no producer yet), and G2's tally asserts a MASK count of 0 |

**Non-goals.** Any priced row, and any decision change: KEY, M and TIE stay frame-independent. A consumer
kind on OFS sites (its own trigger). Presence joining the call. A frame for pre-check parts (§7 Q1).
Target and layer as plan inputs: they are art facts (target seam K0-U3), and T-FIND stays the OFF variant's
(`finder.c` :647, §1.5 rule 1). Serializing the hook callbacks ([IR-FORM]). The composer stating an
`fd_stop` (F5's second half, §2.4). `[rev1]` Any MASK producer, vrun's re-expression, and routing vany
(§2.7). Re-expressing the composer's fused arms as compositions (§2.6).

## 2. What crosses the seam

### 2.1 What pcrec states at phase 1, per NEXT row's frame

Unchanged from rev 0. Today two pcrec callers make the phase-1 ask (`grep -rn mf_wdecide src`). No other
window scenario makes a phase-1 ask: not the PF find, the VM hat's seek, MLINE, LMHIT or the cover/REPORT
site. For those the define, and `mf_ask` before it, IS the plan call, and it already carries the frame, the
hooks and the phase set (`find_site`, `emit_dfa.c` :6922-6936; `pcrec_cover_site`, `known.c` :488-496;
`cand_ask`, `emit_dfa.c` :8352). pcrec states nothing new for them.

| phase-1 ask | NEXT rows that read its reply | the site those rows define | what pcrec states at phase 1 (3.0b) |
|---|---|---|---|
| the DFA prefilter, `window_reply_ask` (`emit_dfa.c` :7604-7616, asked at :4792) | `run-pinned-bounded`, `run-pinned`, `offset-set-bounded`, `offset-set` (:10471-10500), by the key map `next_keys` (:7298-7306, :7317-7321); also `ofs_test_of` (:7402-7412: the block's comment and the OFFSETS stamp) and `dfa_form_derive`'s RE-SEED refusal (:13002) | the offset-skip block, `ofs_site_define` (:7622-7642) | **form** FUNC, **op** FIND, **handoff** RETURN, **empty** MISS, **use** POSITION, **body** ONESHOT, **site_kind** UNSTATED (0: OFS sites state no kind, `span_pick.md` :131's named exception), **decl_point** 0, **on_miss_leaves** 0, **pred.fn_ref** 1; the window statement `ofs_window_of` with floor SUBJECT (unchanged); **def** = {`fn_name` stated, `table_name` stated, `miss` MF_MISS_N, `comment_tier` NONESSENTIAL}; **call** DEFINE. These are exactly the values the block's define states |
| the same ask | the rows below the offset rows (`handoff-reentry`, `first-*`, `memchr*`, `byte-class*`), reached where no key holds | each defines its OWN PF site (`pf_site_of`, :7131-7146) over its own statement (`pf_window_of` with its own set and offer) | nothing: these rows read no reply field. Their define is their plan call. §7 Q2 covers a priced row on this choice |
| the run window, `req_run_member` (`emit_dfa.c` :1058-1076) | none: the reply's reader is the run member (the part's scan, the `@idx`/REQ stamps, `req_set_leads_own`) | the pre-check's FUNC part, whose frame the KIT derives at the composite's define (`wf_part_site`, `window.c` :1984-2007, inside `wf_parts_prepare` :2031) | **call** NONE (decision only); `def` NULL. Its site's frame fields are not read |

(The `body` value ONESHOT above is `mf_site.body`, the site's call shape. It is not the candidate stream
`MF_WSTREAM_ONESHOT` of §2.5, although the spelling is alike. `[rev1]`)

**Why only the offset rows' frame.** The decision is frame-independent through 3.0. So any frame gives the
same decision, and the frame part is the one new answer. Only the offset rows render the asked statement:
the rows below define a different site. "Per NEXT row" therefore means one framed ask for the four offset
rows, which share one frame. The hooks' `u` pointer may differ from the define's: the plan face never calls
a hook (Goal 3), so `u` is never dereferenced at phase 1 (`UnanchStart` holds no `DfaForm` yet).

### 2.2 What the call takes

Unchanged from rev 0.

```
typedef enum { MF_WCALL_UNSTATED = 0, MF_WCALL_NONE, MF_WCALL_DEFINE, MF_WCALL_EMIT } mf_wcall;
int mf_wdecide(const mf_art *, const mf_site *site, const mf_hooks *def, uint8_t call, mf_wreply *out);
```

- **UNSTATED** is refused (-1). There is no presumed value (memory `pcrec-no-silent-defaults`).
- **NONE**: the decision only, as today. The site's frame fields and `def` are not read (`wf_check(site, 0)`,
  as `window.c` :1226 does now). The reply's frame part is zero: `framed` 0, empty ids, `stream`
  MF_WSTREAM_NONE `[rev1]`.
- **DEFINE / EMIT**: the frame is the site's own fields, and `wf_check(site, 1)` applies. Table E's walk runs
  under the gate phases the define would read: DEFINE, or DEFINE|USE for EMIT, as `mf_emit` does
  (`compose.c` :255-258, :1320-1325). `def` is the define hooks, or for EMIT the one-call hooks. The call
  returns -1 exactly where that define would refuse: `mf_ask`'s rule 1 (`compose.c` :1002-1042). One example
  is a REPORT site that E-find does not render under `no-window-search`. The art's denies and `--memfn=`
  options apply, as at the define.
- The phase set crosses as a fact about the CALL, not as the kit's internal `MF_PH_*` bits: `memfn.h`
  exports no `MF_PH_` name (`grep MF_PH_ memfn/include/memfn.h`: none).
- **Purity** (D186 add. 2): the reply is a function of the site's facts (window and frame), the
  hooks' stated-ness and classes, the call, the art's denies/options, the measure set and the handed
  rates. It sets no art state, defines no handle and writes no text or trace record. Reach stays counted
  on the define (`span_pick.md` breaker (c)). Nothing is cached: the define recomputes the plan.

### 2.3 What the reply grows `[rev1]`

Appended LAST to `mf_wreply` (`memfn.h` :1467-1482), because initializers are positional:

| member | type | value on a framed ask |
|---|---|---|
| `framed` | `uint8_t` | 1 (0 on NONE) |
| `frame_row` | `char[12]` | T-FRAME's row: `E-func`, `E-stmt`, `E-find` or `E-generic` (`window.c` :1616-1621) |
| `method` | `char[8]` (= `mf_result.row`'s width) | **the SEARCH**: T-FIND's deciding row id (`D-hors`, `D1`, `D1c`, `D1w`, `PAIR`, `R7w`). On E-find it is the window walk's row (`wf_find_decide`'s `brow`). On E-func/E-stmt it is the composer's routed row where one decides (the value `mf_result.row` reports, `compose.c` :1316). It is `""` where no T-FIND row decides: E-generic has no find, and a legacy frame can walk with no T-FIND row, e.g. E-func where `fn_rows` BODY decides (the named exception, until OFS states a kind) |
| `stream` | `uint8_t`, `mf_wstream` {`MF_WSTREAM_NONE` = 0, `MF_WSTREAM_ONESHOT`, `MF_WSTREAM_MASK`, `MF_WSTREAM_SHIFT`} | **the CANDIDATE STREAM**: Table S's pick (§2.5.3). In 3.0 it is SHIFT iff the search is D-hors, else ONESHOT. NONE on an unframed ask. MASK is declared but has no producer in 3.0 (Goal 5; Q8) |
| `fused` | `char[48]` (= `mf_result.form_id`'s width) | the id of a FUSED renderer: one that renders search, stream and check as one piece, so the triple's pieces are not separately composed (§2.6.3). On E-func/E-stmt it is the arm the text is written by (the value `mf_result.form_id` reports). On E-find under B-fn it is the offset-skip function's form id, the same value E-func reports for that function. It is `""` where the family composes the triple: E-find's other rows, and E-generic |

**The check's members.** The CHECK is T-VERIFY's plan (Table C, `window.c` :1051-1092; `c_plan` :1096). The
reply already carries it in its decision group: `nplan`, `plan[]`, `plan_term[]`, `pinned`, `run_stated`,
`run_member`, `run_lo` and `run_len` (`memfn.h` :1467-1482). 3.0 adds no member for it. `memfn.h`'s comment
names that group "the check" so that a serialized reply reads as (`method`, `stream`, check). Because the
check is frame-independent in 3.0, a framed ask and a NONE ask of one site answer the same check.

**Rev 0's `renderer` is replaced.** On E-find it named a Table B row (`B-pair`, `B-memchr`, ...), which is
a C spelling. Rev 1 does not cross that id. On a composed frame, (`frame_row`, `method`, `stream`, check)
determine the renderer rows through the renderer tables (§2.6). On a fused frame, `fused` names the one
piece that renders the whole triple. Rev 0 named B-fn vs B-pair (smp05 vs pr09) as the case a
method-only record cannot tell apart, and the reply still tells them apart: B-fn has `fused` set and B-pair
has it empty (§6). The renderer rows themselves stay visible in the kit's trace (MFTRACE), which belongs to
the emitter.

`path` is unchanged. It names the decision path, and `+hors` stays a define-trace suffix (`window.c`
:1944-1945). The decision fields (`alt` .. `path`) are frame-independent in 3.0, and the purity harness
asserts it: a NONE ask and a framed ask of one site answer equal decision fields.

**Who reads the new fields (D77).** 3.0 has two named readers: the two agreement checks (Goal 2) and
G2's per-frame and per-stream tally. Row 1 and the trace come later. No artifact text or stamp reads them, so
no byte moves. pcrec reads none of them in 3.0 (§4.2).

### 2.4 The asker fact's retirement

**Today.** T-FIND (`fd_find`, `finder.c` :640-679) has two askers. The composer asks with `st` NULL. The
window family asks with `st` set and `renders_pair` the literal 1 (`window.c` :1840). The PAIR row's facts
include `SF_ASKER_PAIR` (`finder.c` :105-106, :289, set at :656). Review 2026-11-05-r2 F5 (:96-102) showed
the fact equals `st != NULL` and that its false branch has no witness. It also showed that D-hors is
filtered only by an ABSENT fact: the composer states no window. F9 (:124-130) named the general form: one
renderer table keyed by (frame row, pick, layer), where a frame renders a pick iff a row exists. Its unlock
(b), "3.0's reply triple becomes a lookup", has 3.0 as its trigger. So does plan row
[SP1E-RENDERER-TABLE] (`plan.md` :835-839).

**3.0a.** ONE declared SEARCH renderer table, `(frame row, pick) -> first-match search renderer rows`
`[rev1: it is §2.6's search renderer table, kept exactly as rev 0 keyed it]`:

- frame row `E-find`: today's `wf_brows` less B-fn (B-pair for PAIR; B-memchr for LIBC and LIBC_BACK;
  B-walk for WALK; B-hors for HORS). `[rev1]` B-fn moves to the FUSED rows, which are matched first (§2.6.3);
- frame row `composer` (the arms that render E-stmt's translated site and every non-plan FIND site):
  today's `fd_renderers` (`compose.c` :272-292: LIBC by `end_back`, LIBC_BACK, WALK by `end_back`);
- layer: one wildcard column, as declared today. No row is layer-keyed: the SIMD rungs stay `fn_rows`
  PREFIX and vrun's KA/KB, the named exceptions with their census rule (§2.7).

T-FIND's input carries the asking frame's RENDERABLE SET. `[rev1]` A pick is in it iff the search renderer
table has a row for (frame, pick) AND the stream renderer table (§2.6.2) has a row for one of the streams
the support table (§2.5.2) admits for that pick. `fd_decide`'s row gate (beside `finder.c` :503) declines
a row whose pick is not in the set. This replaces `SF_ASKER_PAIR`, which is deleted; bit 15 is retired and
never reused, like bits 6-8, 12 and 13. It also replaces `renders_pair`, which is deleted. PAIR and HORS
are then filtered by one mechanism. The composer's refusal of an unrenderable routed pick
(`compose.c` :262-268) becomes unreachable by construction rather than by absent facts. The false branch
gains a witness: `find_facts` states SF_TWO_MEMBER on a composer site's two-member set at offset 0
(`finder.c` :555, :567-574), so with the check removed the composer would pick PAIR and refuse (§5 row C).

`fn_rows` BODY, the third member F9 names, stays a named exception. Its trigger is "pcrec states a kind
on OFS sites". F6's one renderer-row struct is folded in where the table's rows need it. The composer
stating an `fd_stop` (F5's second half: one question shape) is NOT in 3.0. A RUN span needs a field
`fd_stop` lacks, and its trigger is the compose `arms[]` named exception's ("a kit request adds an arm").

**Every reader of the asker fact, found by grep** (`git grep -n 'asker\|renders_pair\|SF_ASKER_PAIR'`
outside history, lane reports and reviews; re-run at this tree, unchanged):

| reader | disposition |
|---|---|
| `memfn/src/finder.c` :37-38, :105-106, :217-222, :289, :594-618, :656 | the bit and its setter deleted; the PAIR row's facts become `SF_SPAN0 \| SF_TWO_MEMBER`; comments restated ("the frame renders PAIR"); the renderability check added at the row gate |
| `memfn/src/kit.h` :531-556 (`fd_form`'s "each asker renders", `fd_stop.renders_pair`, `fd_find`'s comment) | `renders_pair` deleted; `fd_stop` (and the composer's path) gain the renderable set; comments restated |
| `memfn/src/window.c` :37 (header), :1840 (`.renders_pair = 1`) | deleted: E-find's renderable set comes from the tables |
| `memfn/src/compose.c` :262-292 (`fd_renderers`, `fd_renderer`) | moved into the one search renderer table (its composer rows) |
| `memfn/src/formhash.c` :272, :446 (comments) | reworded ("E-find renders PAIR"); the code at :472 reads `wf_plan_brow` and stays valid if the accessor stays (`[rev1]` it returns the composed search renderer row, or B-fn's fused id: §2.6.3) |
| `memfn/src/CLAUDE.md` :9 ("for both askers"), :15 ("holds on the asker fact `SF_ASKER_PAIR`"; "each asker renders the pick by its own renderer rows"), :21 and :41 (Table B's renderer rows) | restated (`[rev1]` :21 and :41 also name the split: search, stream and check renderer tables, and the fused rows) |
| `tests/memfn/decider_census.tsv` :24 (`fd_find`'s note), :29 (`fd_renderer` -> the table), :66-67 (`wf_find_decide`, `wf_prepare`: "at text time" -> the plan) | rows edited by 3.0a; `[rev1]` rows added for the support table, Table S and the stream renderer table; `decider_census.py`'s backstop re-run |
| `memfn/docs/finder_history.md` | a dated row for the PAIR row's facts edit (§1.8: every row edit is logged) |
| `docs/design/memfn/span_pick.md` :109, :135, :420 | the named exception retires: amendment §8 (the note's own next revision) |
| `docs/dev/plan.md` :835-839 [SP1E-RENDERER-TABLE] | closed by 3.0a (main's edit) |
| NOT readers | lane reports and review records (history); `docs/design/stream/roadmap.md` :90/:121/:128/:716 (the R12 "asker" there is pcrec's start-table hand asker, a different thing) |

### 2.5 The triple: search, candidate stream, check `[rev1]`

A site's find-then-verify plan is three pieces, each answered by its own FACT table, and composed:

| piece | its table (facts) | it answers | in the reply |
|---|---|---|---|
| SEARCH | T-FIND (`fd_rows[]`, `finder.c` :257-307; its pick `fd_form`, `kit.h` :538-539), over Table A's stop | where the next candidate is: a position, or a block's lane mask | `method` |
| CANDIDATE STREAM | the SUPPORT table (§2.5.2) and Table S (§2.5.3), new in 3.0a | how the text moves past a candidate the check rejects | `stream` |
| CHECK | T-VERIFY (Table C, `wf_crows`, `window.c` :1051-1092, every holding row applying in order) | whether a candidate is a match: member test, bound, run compares | the T-VERIFY group (§2.3) |

#### 2.5.1 The three streams

- **ONESHOT**: the search returns one candidate position c, and after a rejection the next search starts
  at c + 1. This is today's `C++` (`resume_next`, `window.c` :2308-2311). libc `memchr` can only be this.
- **MASK**: the search produces a block's lane mask, and after a rejection the text takes the mask's next
  set lane without reloading the block. Only when the mask is empty does the next block load. This is
  vrun.c's inline loop today (`while (m) { cand = i + ctz(m); ...; m &= m - 1; }`, `vrun.c` :317-329).
- **SHIFT**: the text moves by the skip table's shift of a probed byte (D-hors: `C += SH[B]`,
  `d_hors_next`, `window.c` :2671-2674). It applies both after a probe miss and after a rejection.

#### 2.5.2 Which streams each search supports (the SUPPORT table)

A declared table; its basis column is the fact that admits each stream. For the built picks it is exactly
what today's text does. The rows below the line are NOT T-FIND rows in 3.0: they state the vocabulary's
support so that a later unit adds its row and nothing else (§2.7).

| search (T-FIND pick, rows) | candidate it produces | ONESHOT | MASK | SHIFT | basis |
|---|---|---|---|---|---|
| LIBC (D1) | a position | yes | no | no | libc returns one position, and no block state survives the call |
| LIBC_BACK (D1c) | a position | yes | no | no | the same, for a stop below the candidate |
| WALK (R7w, D1w) | a position | yes | no | no | a byte loop stops at one position |
| PAIR (PAIR) | a position | yes | no | no | two `memchr` streams. Their frontiers (`ha`, `hb`, `ofs_pair_text`, `ofsskip.c` :283) are the SEARCH's own state, kept across restarts. They are not a candidate stream: the restart is still c + 1 |
| HORS (D-hors) | a position and its probed byte | no | no | yes | the shift table over the window is its stream; at c + 1 it would be a walk with a probe |
| *vector block search (vrun's KA/KB compare; vany's any-of)* | *a block's lane mask* | *yes (the lowest lane)* | *yes* | *no* | *not a T-FIND row in 3.0 (§2.7)* |
| *word-at-a-time search (SWAR has-byte; a candidate form of the inline one-member finder)* | *a word's byte mask* | *yes* | *yes* | *no* | *unbuilt (§6)* |

The unbuilt picks (`FF_V1`, `FF_W64`, `FF_A3`, `FF_NONE`) have no row. They are not renderable, as today.

#### 2.5.3 Table S, the stream pick (first match, kit-internal, 3.0a)

| row | holds | stream |
|---|---|---|
| S-shift | the search's support is {SHIFT} | SHIFT |
| S-mask | the search supports MASK, and the frame has a MASK stream renderer row | MASK (no frame has one in 3.0, so the row never holds; its reach is UNREACHED with that reason in `purity_rows.tsv`) |
| S-oneshot | the search supports ONESHOT, or there is no search (E-generic: the floor's candidate loop) | ONESHOT |

Table S's input is the pick and the frame only. It reads no measurement and no price, so it is a rule,
not a priced row. When a search supports two streams, which one is cheaper is row 1's question (§6),
answered by a priced row over this table. **Today's selection, reproduced**: D-hors -> SHIFT; every other
pick, and the floor -> ONESHOT. That is exactly `wf_b_render`'s `next` column (`window.c` :2696-2707), so
the stream pick moves no byte.

#### 2.5.4 Composition

A triple holds on a frame iff:

1. T-FIND picks a search the frame can render (the renderable set, §2.4);
2. the support table admits the stream Table S picks, and the frame has a stream renderer row for it;
3. T-VERIFY's plan is rendered by the frame's check renderer.

Any search composes with any stream it supports and with any check. No pair of pieces is special-cased.
The text is rendered INLINE: the composing renderer writes the search, the check and the stream into
one candidate loop, with no call boundary between them (§2.6).

### 2.6 Table B splits into a search renderer and a stream renderer `[rev1]`

**Today** Table B is three parallel arrays over one index, `B_FN .. B_HORS` (`window.c` :1794):

- `wf_brows` (:1795-1819): `holds`, `libc`, `path`, `prepare`;
- `wf_b_find` (:2576-2579): each row's find text (`wf_b_pair` :2562, `wf_b_memchr` :2532, `wf_b_walk` :2549);
- `wf_b_render` (:2696-2711): `head` (the find and the bound, or D-hors's probe: `find_head` :2662,
  `d_hors_head` :2642), `next` (the resume: `resume_next` or `d_hors_next`) and `define` (file-scope
  text: `d_hors_define` :2677, the shift table).

E-find's loop (`wf_find_expr`, :2718-2748) writes `for (;;) { HEAD; if TEST { F = 1; break; } NEXT; }`.
Here HEAD is `wf_b_render[].head`, TEST is `wf_test_to` (:2244, :2741) and NEXT is `wf_b_render[].next`. So
the search and the stream are FUSED in one row. The stream is implied by the search pick and never chosen:
B-walk carries the resume c + 1, B-hors the shift.

#### 2.6.1 The search renderer table, keyed (frame row, pick)

It is §2.4's table: rev 0's renderer table keyed by (frame row, pick), PRESERVED. Its E-find rows take
`wf_brows`' `holds`, `libc` and `path` columns, `wf_b_find`'s text, and the search half of `head`:

| frame row | pick | search renderer row | its text |
|---|---|---|---|
| E-find | PAIR | B-pair | `wf_b_pair` + the bound (`find_head`) |
| E-find | LIBC, LIBC_BACK | B-memchr | `wf_b_memchr` + the bound |
| E-find | WALK | B-walk | `wf_b_walk` + the bound |
| E-find | HORS | B-hors | the bound, then the probe of the window's last position into B (`d_hors_head` less its resume text, which it now takes from the stream renderer); `prepare` sets `hl` (the probe's offset) |
| composer | LIBC (by `end_back`), LIBC_BACK, WALK (by `end_back`) | `fd_renderers`' arms | the PF arms (`pffind.c`): a search only; the caller restarts and checks |

#### 2.6.2 The stream renderer table, keyed (frame row, stream)

| frame row | stream | stream renderer row | its text |
|---|---|---|---|
| E-find, E-generic | ONESHOT | S-oneshot | `resume_next`: `C++` |
| E-find | SHIFT | S-shift | `d_hors_next`: `C += SH[B]`, used at the rejection and inside the search head's probe miss; its prepare is `hors_table` (`sh`), and its file-scope text is `d_hors_define` (the 256-byte table) |
| composer | ONESHOT | S-caller | no text: the caller's NEXT loop restarts at c + 1 |

The CHECK renderer is one row per composing frame in 3.0: E-find's `wf_test_to` less the position the
search proved (`skip`: C-stop's or the probe's), and E-generic's `wf_test` (:2274). It is keyed by frame
row only, because every composing frame renders T-VERIFY's plan one way today. A second check spelling
(vrun's mask-trimmed compare, §2.7) becomes its second row.

#### 2.6.3 The fused rows

Some renderers render the whole triple as ONE piece. The composition matches them FIRST, and the reply
names each one in `fused`:

| frame row | fused row | holds | its triple |
|---|---|---|---|
| E-find | B-fn | `b_fn_holds` (`window.c` :1773-1786): pick PAIR, the plan IS the offset-skip function's predicate, and `fn_rows` BODY takes fn-pair | (PAIR, ONESHOT, the function's predicate test), rendered inside `<prefix>_mf<handle>_ofsskip` (`wf_find_fn` :2621, `wf_find_define` :2753), which E-find's expression calls |
| E-func, E-stmt | the composer's arm (`select_arm`, `compose.c` :294; `fn_rows`, `ofsskip.c` :418-425) | the composer's walk | each arm's own fused text: the offset-skip function (fn-pair, fn-memchr), the pre-check composite, the PF arms, the generic row |

Re-expressing a fused row as a composition is a later unit with zero movers each. Its trigger is "a second
user of the row's pieces", as F9's census rule states it. vrun is the first candidate (§2.7). B-fn's
reconciliation with `fn_rows` BODY is KEPT (span_pick §The tables, T-FRAME), as today.

#### 2.6.4 Why the split moves zero bytes, and the witnesses that show it

The composition writes the same spellings in the same order as today:

| row today | head (search renderer) | test (check renderer) | next (stream renderer) | file scope |
|---|---|---|---|---|
| B-pair | `wf_b_pair` + bound, as `find_head` | `wf_test_to` | `resume_next` | none |
| B-memchr | `wf_b_memchr` + bound | `wf_test_to` | `resume_next` | none |
| B-walk | `wf_b_walk` + bound | `wf_test_to` | `resume_next` | none |
| B-hors | bound + probe; its miss text is `{ ` + S-shift's text + `; continue; } ` | `wf_test_to` less the probe | `d_hors_next` | `d_hors_define` |
| B-fn | fused: unchanged | | | `ofs_fn_define_at` |
| floor (E-generic) | none | `wf_test` | `resume_next` (`wf_floor_expr` :2314-2327) | none |

The only spelling that moves between functions is D-hors's probe-miss resume. Today `d_hors_head` writes
`)) { %s += %s[%s]; continue; } ` with (C, SH, B) (`window.c` :2653). `d_hors_next` writes
`%s += %s[%s]` with the same three names (:2673). So the probe miss written as `)) { `, then S-shift's text,
then `; continue; } ` is the same byte string. The shift table's define stays in the same place in the
define order: one file-scope text per site, after the run compares' word loads (`wf_find_define` :2763-2764).
The include and libc facts (`wf_find_prepare` :1877-1880) become the union of the pieces' facts, which
gives today's values: B-hors's probe and S-shift write no `memchr`, and the other search rows do.

**Witnesses** (rev 0's, unchanged, now also covering the split): `scripts/emit_sweep.py` byte-identical on
every arm against 3.0a's named base. Every form id's hash is unchanged (`arm_fixtures --hash`, base vs HEAD),
and check C's stale count is 0 (`formhash.c` :296's `pair` instance is E-find's PAIR text). G2 is green
(`run_g2_win.sh` with its `EFIND_FLOORS` census: libc, walk, hors, pair, fn and the rest each at or above
its floor; the finder G2). REACH EQUALITY holds (`MFTRACE REACH`, chosen and asked per row, base vs HEAD,
with the B rows' reach now counted under the search renderer rows and S-oneshot/S-shift). `decider_census.py`
is green with its backstop. No `*_movers.txt` moves.

### 2.7 vrun and vany as compositions `[rev1]`

**vrun.** Its rows `vrun-w16`/`vrun-w32` (`vrun.c`) are PREFIX rungs of the offset-skip function, OVER
fn-pair (`vrun_over`, :406), on the SIMD layer only. Each helper is the triple, hand-composed:

- SEARCH: a vector block compare at KA (and KB where the ranking gives one): one unaligned load, an AND,
  a compare and a movemask per block (`cmask`, `vrun_render` :337-403). It produces a lane mask;
- STREAM: MASK. Each set lane is taken lowest first, and the next block loads only when the mask is empty
  (`vrun_verify` :310-329);
- CHECK: the BODY's run compare less the positions the mask proved (VERIFY TRIM, `run_cmp_render_trim`), or
  the padded compare on the main path (`run_cmp_render_pad`). This is T-VERIFY's C-stop rule ("minus what
  the search proved") applied to the search's proven positions, with runcmp.c's rows.

The re-expression makes those three pieces rows: a vector search renderer row, the S-mask stream renderer
row, and the trimmed check as the check renderer's second row, all under the offset-skip function's frame
at the SIMD layer. **Not in 3.0.** Its reasons:

1. The reply is the OFF variant's (T-FIND decides on it, `finder.c` :647), so no reply reader sees vrun's
   triple;
2. it needs a frame row for the function's PREFIX slot, which the composer's fused arms do not have yet;
3. the target seam's U2+U3 (`target_seam_units.md`) moves vrun's admission into per-target arts.
   Re-expressing vrun before that remodel would re-touch the same lines (D153).

It is its own zero-mover unit (Q9), and it is byte-identical either way: the emitted helper text is the
same pieces in the same order. Until then vrun stays the named exception it is today (the SIMD rungs,
§2.4's layer column).

**vany.** `vany.c` is a bare SEARCH: a vector any-of compare over 2-3 bytes, whose lowest set lane is the
answer (`vany.c` :167, :174). Its loop has no check and no rejection, so a site that used it would compose
it ONESHOT with the caller's check, or MASK with the family's check once a MASK renderer exists. It is NOT
ROUTED (`vany.c` :16-22: no row, no deny, no pcrec caller). It enters as a search piece, meaning a T-FIND
row, a search renderer row and its card under `kit-kernels@1`, only in the unit that routes it. Routing is
triggered by a measured win in row 1's search comparison (§6), and the unit that routes it moves bytes.
**Not in 3.0** (D77: it would route new sites).

### 2.8 Facts apart from C spellings `[rev1]`

| layer | tables | what a Rust emitter would do |
|---|---|---|
| FACTS (the plan) | T-FRAME (Table E), Table A (stop), T-FIND (search), the support table, Table S (stream), T-VERIFY (Table C: check), Table M, the TIE table | reuse unchanged |
| C SPELLINGS (the renderer) | the search renderer table, the stream renderer table, the check renderer rows, the fused rows' text, `ofs_pair_text`, runcmp.c's spellings | replace with its own rows, keyed the same way |

The reply crosses only the FACTS layer's ids (`frame_row`, `method`, `stream`, the T-VERIFY group). The one
exception is `fused`: it names a fused renderer because that renderer's pieces are not yet separate facts.
`fused` empties as the fused rows are re-expressed, and once all are re-expressed it is always `""`.

## 3. The number events and their same-commit package (readers by grep, D76/D94)

**MF_SITE_ABI**: 24 -> the next free number at landing of 3.0b (25 at this tree). The target seam's
U2/U3 is also a kit seam event, and whichever lands second takes the next number and re-baselines (§5).
Readers (`git grep -n MF_SITE_ABI`, re-run at this tree, unchanged), by class:

| class | readers | disposition |
|---|---|---|
| the definition and its history | `memfn/include/memfn.h` :39-204 | a new entry `[rev1]`: "`mf_wdecide` takes the frame (the site's frame fields, the define hooks, `mf_wcall`); `mf_wreply` gains `framed`, `frame_row`, `method` (the search), `stream` (`mf_wstream`) and `fused`, appended LAST; its T-VERIFY group is named the check; `mf_wcall` and `mf_wstream` added. No MF_VOCAB or MF_CLASS_V move; no pcrec byte moved" |
| prose that states the CURRENT number | `memfn/include/CLAUDE.md` :4 ("`MF_SITE_ABI` 24 (24: ...)") | becomes the new number with its one-line entry |
| symbolic readers (they move with the macro) | `src/gen/memfn_sites.c` :455; `memfn/src/compose.c` :1011, :1067-1069; `window.c` :1226, :1419; `presence.c` :124; `formhash.c` :381; `memfn/tests/g2/g2_gen.c` :923, :2259, :2294, :3754, :3790, :3834, :4200, :4430-4431; `g2_simd_gen.c` :334; `g2_win_gen.c` :630, :737, :793, :837; `tests/memfn/arm_fixtures.c` :238; `mass_check.c` :258; `proof_check.c` :156; `proven_check.c` :63 | recompile only |
| historical `MF_SITE_ABI n` (n <= 24): comments, refusal texts, sabotage anchors | `compose.c` :588, :624, :776, :820, :908; `fields.def`; S1089 (:24-26), S2903 (:13-14, anchored on `compose.c` :908's text) | unchanged: each names the event that introduced its rule, and every anchor's text stays byte-identical |
| literal pins | none: G2 is symbolic (`MF_SITE_ABI + 1`), and the `site abi %u, kit abi %u` refusal is asserted by kind only (`G2M6_REPORT.md` :131, :243) | the grep is re-run at landing |
| the ledgers | `memfn/docs/journal.md`, `memfn/docs/responses.md` ([responses] R-35 3.0b) | entries in the same commit |

**MF_CLASS_V**: stays 8. It moves on an `mf_class` layout change, or on a finder-row index shift ahead of
the PRES rows (`memfn.h` :1080-1098). 3.0 adds, removes and reorders no finder row (PAIR's FACTS change,
not its index), and it adds no `mf_class` member. `[rev1]` The support table and Table S are new tables,
not finder rows. Their ids are not in `mf_finder_rows`, so no index moves. MF_CLASS_V's readers stay as
they are: `memfn.h` :1080, `window.c` :2790, `compose.c` :390, :1029, `proof_check.c` :408,
`arm_fixtures.c` :386, `memfn/include/CLAUDE.md` :4, `memfn/src/CLAUDE.md` :11. All are symbolic or
prose. Putting the frame part into `mf_class` instead would move it, and that is REJECTED. The class
answers what the text proves (D157), and the frame part reports a selection.

**Same-commit package of 3.0b** (beyond the table above): pcrec's ASK-1..ASK-5 (§4.2). The callers
`arm_fixtures.c` :2271, :2278, :2305, :2323 and `g2_win_gen.c` :742, :797, :855 (build breaks).
`pur_diff` (`arm_fixtures.c` :2204-2220) and the control print (:2330-2335) gain the new fields.
`run_finder.sh` :133's `PURITY_FLOOR` 1157 is an EXACT literal, re-pinned to the new count with its
reason. `purity_rows.tsv` gains the Table E, B and `[rev1]` S rows (REACH, or UNREACHED with a reason; its
own id check re-run). `g2_win.h` :44-53's reply copy grows. `memfn/docs/trace_format.md` :102-113 is
updated: "`mf_wdecide` ... writes none" stays true, and the frame part is named, `[rev1]` with the triple's
three pieces. The comments that teach "the decision reads no frame fact" are restated: `memfn.h` :556-558
("read by phase 2 only"), :1435-1441 ("never a frame fact"), `window.c` :49, :1225, and `emit_dfa.c`
:7598-7603. Also `memfn/include/CLAUDE.md` and `memfn/src/CLAUDE.md`.
**No pcrec abi bump** (no byte moves). **No `docs/spec/` hunk**: D80 is not triggered, since no spec file
names `mf_wdecide`, `mf_wreply` or the asker (`git grep` over `docs/spec` and `docs/guide`, re-run: none).

## 4. The split

### 4.1 Kit-side edits (the kit's lanes; `memfn/` and the kit's tests)

3.0a: the search renderer table and the renderable set (§2.4). `[rev1]` The support table, Table S, the
stream renderer table, the check renderer rows and the fused rows (§2.5, §2.6), which are Table B's split.
One internal PLAN FUNCTION that computes the decision and, given a frame, T-FRAME's row, T-FIND's row,
Table S's stream and the fused id. Both `wf_prepare` (the define and `mf_ask`, `window.c` :1892) and
`mf_wdecide` read it. The census rows, the finder history row, the CLAUDE.md lines, and 3.0a's tests
(§5), including `[rev1]` the support pin.
3.0b: the seam (§2.2, §2.3), `reply_of`'s frame part, the MF_TRACE agreement check at `define_sel`
(beside rule 2's re-ask, `compose.c` :1180-1200), the harness and G2 edits, and the ledgers.

### 4.2 pcrec-side asks for main to file (facts and checks, never the kit's method, D157)

R-35 ruling (a) puts these hunks in the kit's 3.0b package. Main reviews them, and the unit's code round
covers both sides. `[rev1]` The triple changes no fact pcrec states. pcrec states the frame, the hooks and
the call; it never states a search, a stream or a check, and it reads none of them in 3.0. Only ASK-3's
field list changes.

| # | ask | the exact facts |
|---|---|---|
| ASK-1 | the DFA prefilter's phase-1 ask states the frame of the site its offset rows define | on the ask's site: form FUNC, op FIND, handoff RETURN, empty MISS, use POSITION, body ONESHOT, site_kind UNSTATED (0), decl_point 0, on_miss_leaves 0, `pred.fn_ref` 1; the window statement `ofs_window_of` and floor SUBJECT, as today; define hooks `fn_name` and `table_name` STATED, `miss` MF_MISS_N, `comment_tier` NONESSENTIAL (other members unstated, as at the define); call DEFINE. Each value equals `ofs_site_define`'s (`emit_dfa.c` :7622-7642), and ASK-3 checks it |
| ASK-2 | the run window's ask states no frame | call NONE, `def` NULL (`req_run_member`, `emit_dfa.c` :1058-1076); otherwise unchanged |
| ASK-3 | the offset-skip block's define holds the reply it was planned by | in a pcrec trace build (the `PCREC_CAND_TRACE` precedent `cand_asked_hold`, `emit_dfa.c` :7066-7085): at `ofs_site_define`, re-ask `mf_wdecide` with the define's own site, hooks and call DEFINE. EVERY reply field must equal `UnanchStart.wr`: the decision group (the check's included) and `[rev1]` `framed`, `frame_row`, `method`, `stream` and `fused`. A difference fails the compile as a named invariant ("asked-plan-differs"). pcrec compares the fields as opaque values and interprets none |
| ASK-4 | ASK-3 runs and reaches its site | name the suite whose trace build runs over DFA prefilter sites (candidates: `tests/codegen/run_cand_oracle.sh` :90, `run_fallback_table.sh` :143), and prove reach with a pcrec-side sabotage row (§5 row F) |
| ASK-5 | the comments that teach the frame-free ask are restated | `emit_dfa.c` :7598-7603 ("the decision reads no frame fact, so one ask serves every NEXT row"), and `UnanchStart`'s `wr` comment (:4630-4636): the ask states the offset rows' frame, and the rows below define their own site |

**Not asked**: a consumer kind on OFS sites; a frame for pre-check parts (§7 Q1); any frame on the
define-only scenarios (they have one already); any NEXT-row change; any stamp, CLI or spec change;
`[rev1]` any pcrec reader of `stream`, `method` or `fused`. **For main, not an ask of code**: the kit asked
main to file Frank's ruling as a decision entry (`responses.md`, lane/memfn-k1107, "proposed decision
entry"). See §7 Q10.

## 5. Build plan: two units

`[span_cards.md rev1 COST-4]`'s rule applies. Each unit names its BASE commit (main's tip at branch time)
in its first commit, and every identity witness compares against it. After any byte-moving lander on main,
an unlanded unit re-merges main, takes a new named base and re-runs its witnesses. **Sabotage ids are the
kit's, taken at BUILD time from the top of the free range** and recorded in the unit's first commit. The
highest kit id on any branch at this tree is **S2981** (lane k0's S2975-S2981: `memfn/docs/journal.md`
:3598, :3613; the files are on lane/memfn-k0, `tests/mech/sabotages/`). `git grep` over every local branch
finds no S2982 or above outside this lane's own text, so the next free is S2982. `[rev1]` There are 14 rows;
if 3.0a lands first they are expected as S2982-S2989 for 3.0a's A-D and K-N, then S2990-S2995 for 3.0b's
E-J. Rows below are lettered. Heavy runs are boxqueue jobs, with no timing and no window.

| unit | content | witness | heavy runs | sabotage rows (why each goes red) |
|---|---|---|---|---|
| **3.0a** the triple's tables, Table B's split and the plan's frame part, kit-internal | §2.4's search renderer table and renderable set; `SF_ASKER_PAIR` and `renders_pair` deleted; `[rev1]` §2.5's support table and Table S, §2.6's stream renderer table, check renderer rows and fused rows (Table B's split; `wf_brows`, `wf_b_find` and `wf_b_render` retire into them); a support pin `tests/memfn/stream_support.tsv`, written from the ruling's text (memchr ONESHOT only; D-hors SHIFT only; PAIR and WALK ONESHOT only) and checked against the support table; the internal plan function (decision, then per frame: T-FRAME row, T-FIND row, stream, fused id) read by `wf_prepare`; the census rows (§2.4), the finder history row, the CLAUDE.md lines. No seam, no pcrec edit | emit_sweep byte-identical on every arm against its base (Goal 1, §2.6.4); G2 green (`run_g2_win.sh`, the finder G2); every form id's hash unchanged (`arm_fixtures --hash`, base vs HEAD) and check C's stale count 0; REACH EQUALITY (`MFTRACE REACH`, chosen and asked per row, base vs HEAD); `decider_census.py` green with its backstop; the Goal 4 grep empty; the support pin green | `make test` (normal, boxqueue); emit_sweep per arm | (A) `[rev1]` E-find's PAIR search renderer row dropped from the table: formhash's `pair` instance (an E-find window site over `{X,x}`, `formhash.c` :444-473) no longer reaches T-FIND's PAIR, so `check_hash` refuses the id (`finder_check.py` via `run_finder.sh`). (B) the composer frame declared to render PAIR: T-FIND picks PAIR on a composer two-member stop, no composer arm renders it, and `select_arm` refuses. G2's composer sets with two members, and the corpus compile, go red. (C) the renderability check removed at the row gate: the same refusal as (B). This is F5's missing false-branch witness. (D) a second renderer list planted in an unlisted function: `decider_census.py`'s backstop is red. `[rev1]` (K) the support table's SHIFT entry for HORS removed: no stream admits D-hors, so E-find's renderable set drops HORS and T-FIND never picks it. G2's hors census goes below its floor (`run_g2_win.sh` `EFIND_FLOORS` hors:110), and its control "a dense window renders no D-hors table" fails (`g2_win_gen.c` :694). (L) S-oneshot's text planted as `C += 2`: E-find and the floor skip candidates, and G2's window answers are red against its reference (`run_g2_win.sh`). Reach is the corpus's every non-HORS E-find and floor site. (M) the support table admits MASK for LIBC: the support pin is red (it is written from the ruling, not from the table). (N) E-generic's S-oneshot stream renderer row deleted: the floor has no stream, every floor site is refused, and G2 and the corpus compile go red |
| **3.0b** the seam, with pcrec's asks, ONE commit | §2.2-§2.3; `reply_of`'s frame part; the kit's MF_TRACE agreement at every window-site define (the plan re-asked with the define's site, hooks and call; every field compared); ASK-1..ASK-5; the purity harness (framed asks interleaved with defines, `pur_diff` over the new fields, the COUNTING HOOK, `PURITY_FLOOR` re-pinned, `purity_rows.tsv`'s E, B and S rows); G2's window generator asks framed in the frame each site is defined in, holds the reply's frame part to `mf_defined` (`form_id` = `fused` on E-func/E-stmt, `row` = `method` where the composer routes), and floors each frame row and each produced stream at >= 1, with MASK at 0; the reply-id resolution check (Goal 5); §3's package | as 3.0a, plus the two agreement checks green on the corpus and on G2; purity green at its new count; the counting hook at 0 | `make test` (normal, boxqueue); emit_sweep per arm; the ASK-4 suite | (E) `reply_of` writes the frame row of another walk (plant: always `E-generic`): the kit's MF_TRACE agreement check at the define is red (`run_finder.sh` and G2's MF_TRACE kit, `mk_mftrace_lib.sh`). (F) pcrec-side: ASK-1's ask states STMT/ASSIGN. E-stmt is not E-func, so ASK-3's check is red on every DFA prefilter site (the ASK-4 suite). (G) the plan face calls `table_name` once: the counting hook reads 1 (`arm_fixtures --purity`). (H) `[rev1]` the reply's `stream` keyed on `art->nsites` (SHIFT iff `nsites > 0`, 1d's plant pattern): purity is red, and its control print moves (the plant is reached). This also proves `pur_diff` compares `stream`. (I) a framed ask walks Table E without the art's denies: the fixture "framed ask on a REPORT site under `no-window-search` answers -1, as `mf_define` refuses" is red (`arm_fixtures`). (J) `[rev1]` a reply's `method` filled from the `fused` column: the id-resolution check is red (Goal 5) |

**Separability.** 3.0a lands and reverts alone: it moves no seam and touches no pcrec file. 3.0b needs
3.0a, because the frame part comes from 3.0a's plan function, so reverting 3.0a after 3.0b takes 3.0b
with it. 3.0b cannot be split: the signature change breaks pcrec's build without ASK-1/ASK-2. The
MF_SITE_ABI event, its callers and its checks are one commit (memfn/CLAUDE.md's same-commit rule).
`[rev1]` Inside 3.0a, the split (§2.6) and the asker's retirement (§2.4) can be two commits: the split
first, since it alone carries the byte-identity witness, then the renderable set over the split tables.
Both are in one unit because the renderable set reads the stream renderer table.

**Concurrency and remodel overlap (D153).** The target seam's U2 edits `formhash.c`'s entry table and the
`FLD_policy` gate field. 3.0a edits `finder.c`, `window.c`, `compose.c` and `kit.h`, and only comments in
`formhash.c`. The overlap is low: the later lander re-merges and re-runs the hash witness. The two
MF_SITE_ABI events take numbers in landing order. Opt rows on `window.c`, `finder.c` or `compose.c` wait
for 3.0b, as stage 1's did. `[rev1]` 3.0a does not touch `vrun.c` (§2.7), so the target seam's U2+U3
edits to vrun's admission do not overlap it.

**Size.** `[rev1]` 3.0a: M (one table rekeyed, Table B split into three tables plus fused rows, one new fact
table and Table S, one function split; no text moves). 3.0b: M (the seam, about 12 readers, two checks, the
harness growth).

## 6. What 3.0 leaves to row 1 `[rev1]`

**Left wholly to row 1** (`span_pick.md` :409-410): every T-PICK row, and any frame-DEPENDENT decision
(KEY and M meeting in T-PICK). With it goes the rule for unframed asks: a row that makes the decision read
the frame must decline on NONE asks, or define their answer. Otherwise `req_run_member`'s member and the
part's define could disagree, and ASK-2's existing loud check (`emit_dfa.c` :1071-1074) would fire.
Also row 1's: the method-level tie row (R19); verify priced over T-VERIFY's step list (R21); finder_check
L's digest masking (`[sp1g review F5]`); the DEFAULTS reader; the pre-check-part statement (§The pick 7);
M2; the movers census; `[rev1]` a priced stream choice wherever a search supports two streams (a priced
row over Table S). 3.0 builds nothing for them beyond the frame part.

**RULED (Frank, 2026-11-07): row 1 waits for an inline one-member finder and its measurement card.** This
answers rev 0's Q6. The finder is a new SEARCH piece: a T-FIND row, a search renderer row and its card
(memory `pcrec-new-method-needs-measurement-card`), in its own unit before row 1. The census0
decomposition `memfn/docs/ideas.md` :785 names is the trigger for that unit's design. Its supported
streams follow from the support table: if its form is word-at-a-time or vector, it supports ONESHOT and
MASK, and that unit then builds the first MASK stream renderer row. This note does not design the finder.

**Why the triple is the control** (Frank 2026-11-07: "speed compare should remove variables. Apples to
apples"). smp20's watched comparison (`span_pick/smp20.out`, `memfn/docs/ideas.md` :780-785) sets
`{X,x}`@0 by PAIR against `'/'`@1 by libc memchr. As triples these are (PAIR, ONESHOT, plan at @0) and
(LIBC, ONESHOT, plan at @1): the search differs, and so do the stop position and set. Within the search,
inline vs call and own code vs libc also differ, all at once. With the triple in the reply and the trace,
every comparison names which pieces differ.

**The controlled comparisons row 1 runs.** Each varies ONE piece; the site, the frame, the stop and the
other two pieces are fixed. The cells are forced by test-only levers (`mf_lever`, R-30; no public deny
for a lever, memory `pcrec-flag-follows-caller-effect`), so each effect is measured, not inferred.

| comparison | varied | fixed | example cells (smp20's sites) |
|---|---|---|---|
| SEARCH | the search | stream ONESHOT, the check (T-VERIFY's plan), frame, stop | `'/'`@1: libc memchr vs the inline one-member finder vs walk. `{X,x}`@0: PAIR vs walk |
| STREAM | the stream | the search (one that supports both streams: the inline one-member finder if it is word or vector), the check, frame, stop | `'/'`@1: inline one-member ONESHOT vs MASK |
| CHECK (where available) | the check renderer, composed vs fused | (PAIR, ONESHOT), T-VERIFY's plan, stop | B-pair vs B-fn (smp05 vs pr09, `span_pick.md` :114) |
| STOP (Table A's question, not the triple's) | the stop position and set | the triple | `{X,x}`@0 vs `'/'`@1, each under the same search (walk, the one search both stops admit) |

**What 3.0's reply must carry for them: the triple, and `fused`.** `method`, `stream` and the check let a
record name each piece. `fused` tells a fused renderer from a composed one with the same three pieces (the
CHECK row above). Rev 0 argued that adding a field later is a second MF_SITE_ABI event, and that holds for
`stream` too, which is why 3.0b carries it although only one value depends on more than the search. The
candidates' prices and the grid belong to the kit's trace, not the reply: the reply carries no price until
whole-artifact pricing (`span_pick.md` :84, rev5 C1).

## 7. Open questions (plain words, each with a recommendation)

| # | for | question | recommendation |
|---|---|---|---|
| Q1 | main | The run-window ask (`req_run_member`) only wants the run member. Should it state no frame, or the pre-check part's frame (FUNC/RETURN with the pre-check's kind)? | **No frame, for now.** The kit derives the part's frame itself (`wf_part_site`). If pcrec stated it too, there would be a second copy of that derivation. Revisit when a priced row applies on pre-check parts (`span_pick.md` §The pick 7) |
| Q2 | main, kit manager | Under the DFA prefilter, a PARKED reply sends the search to rows that define a DIFFERENT site (the PF find), whose frame the ask does not state. A priced choice between PARKED and RESEED by method cost would need both frames | **Leave it in 3.0.** OFS sites are not priced before they state a kind (`span_pick.md` :131), and that trigger also covers this. File a plan row: "the prefilter ask states each outcome's frame", trigger "pcrec states a kind on OFS sites" |
| Q3 | main | Should 3.0a merge the two renderer lists into ONE table, or keep two lists and only derive the renderable set from each? | **One table.** It is review r2's F9 general form, and plan row [SP1E-RENDERER-TABLE]'s trigger is 3.0. It deletes a parallel list, and its benefit is the simplification itself (memory `pcrec-simplification-is-a-benefit`). `[rev1]` Under the triple it is the SEARCH renderer table |
| Q4 | kit manager | `[rev1]` Should the reply's new fields be strings or enums? | **Row-id strings** for `frame_row`, `method` and `fused`, as `path` and `mf_result.row` are: they are the kit's own names, they read as text when serialized, and they contain no C. **`stream` an enum** (`mf_wstream`): it is a closed vocabulary with a meaning a reader can act on, as `mf_wresume` was in rev 0 |
| Q5 | main | `span_pick.md` :86 says the frame (engine, target, layer) becomes a per-call input "from unit 3.0". Is that still meant? | **Read it as T-FRAME's frame** (form, handoff, kind, hooks, call). Target and layer are art facts under the target seam (K0-U3), and T-FIND keeps deciding on the OFF variant (`finder.c` :647). Amend :86 (§8) |
| ~~Q6~~ | Frank | Should row 1 wait for the inline one-member finder? | **ANSWERED, yes** (Frank 2026-11-07, to the kit). Dropped; §6 restates it |
| Q7 | kit manager | `[rev1]` Rev 0's reply named the C renderer row (`renderer`). Should rev 1 drop it for `fused`, which names a renderer only where it renders the whole triple as one piece? | **Yes.** On a composed frame the triple's facts decide the renderer rows, so a renderer id there would be a C spelling crossing the seam (Frank: "C or Rust"). `fused` keeps the one difference the facts cannot yet express, B-fn vs B-pair, and it empties as fused rows are re-expressed |
| Q8 | kit manager | `[rev1]` Should `mf_wstream` declare MASK now, though nothing in 3.0 produces it? | **Yes.** It is in the ruled vocabulary. Adding it later would be a second seam event, and the first MASK producer (the inline one-member finder, or vrun's re-expression) is already named. A declared value with no producer is asserted unproduced (G2's MASK count 0), so it is not a silent default. Table S's S-mask row is UNREACHED with that reason |
| Q9 | kit manager | `[rev1]` When is vrun re-expressed as (vector search, MASK, trimmed check)? | **Its own zero-mover unit, after the target seam's U2+U3** (which moves vrun's admission; D153), and after the first MASK stream renderer exists (the inline one-member finder's unit, if its form is a word or vector mask). That gives S-mask a second user, which is the census rule's trigger. Not in 3.0 |
| Q10 | main | `[rev1]` The kit asked main to file Frank's ruling ("candidate search and candidate validation are two different primitive pieces that are composed") as a decision entry. A new D-entry, or an addendum? | **An addendum to D186** (optimizations are unit changes or choice changes). Search, stream and check are UNITS, and a composition (which search with which stream) is a CHOICE, so the ruling says how D186's units compose for find-then-verify. Main's call |

## 8. Amendments this design makes to other documents (each lands with its unit)

| document | amendment | unit |
|---|---|---|
| `span_pick.md` :109, :114, :135, :420, :423 | T-FIND and T-FRAME are asked at PLAN time on framed asks; the asker fact's named exception retires; N11's "plan-time at 3.0" is done; `[rev1]` the find-then-verify plan is the triple (search, stream, check), and T-FIND is its search piece | 3.0b (the note's own revision, by the kit) |
| `span_pick.md` :86 | the per-call frame is T-FRAME's; target/layer stay art facts (Q5) | 3.0b |
| `window_site.md` §0 and §2.4 ("the decision reads no frame fact"; `[rev1]` its "resume" row) | a framed ask states the NEXT rows' frame; the decision itself is still frame-free in 3.0; `[rev1]` the resume is the candidate stream, a piece chosen by Table S | 3.0b |
| `docs/dev/plan.md` [SP1E-RENDERER-TABLE] | closed (main) | 3.0a |
| `docs/dev/decisions.md` D186 | `[rev1]` an addendum recording the ruling (main; Q10) | main's, any time |
| `memfn.h`, `memfn/include/CLAUDE.md`, `memfn/src/CLAUDE.md`, `trace_format.md`, `decider_census.tsv`, `finder_history.md` | §2.4, §2.6 and §3 | 3.0a / 3.0b |

## 9. The three standing questions (docs/design/CLAUDE.md)

**Q1, the measurement regime: NOT RELEVANT.** 3.0 reads and produces no measured number. Its witnesses
are compile-only: artifact diffs, hashes and checks. The cards stay unread until row 1. `[rev1]` Table S is
a rule over the pick and the frame and reads no measurement. The stream comparison that would read one is
row 1's (§6).

**Q2, the independent control: RELEVANT.**
- Byte identity is checked against the NAMED BASE's artifacts, diffed pcrec-side (emit_sweep), never
  against the kit's `moved` (K35). This includes Table B's split (§2.6.4).
- The kit's agreement check compares the plan call with the define's selection. The two share code by
  design, so it is a TRIPWIRE against a later divergence (a quiet-only branch, a cache), not the
  identity control.
- pcrec's check (ASK-3) compares two pcrec statements of one frame through the kit. Its subject is
  pcrec's statement, which the kit cannot make equal on pcrec's behalf.
- `[rev1]` The support table is checked against a pin written from the RULING's text (memchr one-shot
  only, and so on), not derived from the table, so the pin and the table do not share a source (§5 row M).
- Populations are counted by their owners: the corpus's DFA prefilter sites by ASK-4's suite, and the
  per-frame-row and `[rev1]` per-stream framed asks by G2's own tally, with a floor per row and per
  produced stream (the corpus alone frames only E-func).
- Every sabotage row names the check that sees it and why that check can see it (§5). Reach is shown by
  a control (H) or by a corpus or G2 site the plant moves (A, B, C, F, K, L, N).

**Q3, what moves when data is regenerated: RELEVANT, narrowly.** 3.0 adds no stamp or generated file,
and re-measuring a set moves nothing (no reader). `[rev1]` The support table and Table S are hand-declared
rule tables, not regenerated data. One existing reader of the TEXT does move with 3.0's code: the cards'
recorded form hashes (zen4-grid3@1 rows' `kit:form.<id>=<hash>`). A hash that moved would make cards
stale. Goal 1 therefore requires every form id's hash unchanged, and check C's stale count 0, across the
split too. A byte move would be an abi event (D76/D94), and 3.0 has none.

## 10. span_pick.md cites that drifted

Unchanged from rev 0 (lane u30d's report table): `span_pick.md` :86's inner cites `window.c` :1061 is now
`memfn/src/window.c` :1225, and `finder.c` :934 (layer) is now `finder.c` :647. Its :49-50's
`emit_dfa.c` :7600-7602 is now `src/gen/emit_dfa.c` :7598-7603, and `finder.c` :938 (`SF_WINDOW_STOP`)
is now `finder.c` :656 (`SF_ASKER_PAIR`).

## STATE AT HANDOFF

Rev 1, lane u30d1. Cites re-checked by grep at this worktree (tip a061437e5; code identical to main
a678d0a4e under `memfn/`, `src/`, `tests/memfn/`). No make, no timing, no code. Not a build go: 3.0a and
3.0b each need the kit manager's ruling on §7 and a design critic round, and R-35's build GO covers stage 3
(Frank 2026-11-06). OWED: none.
