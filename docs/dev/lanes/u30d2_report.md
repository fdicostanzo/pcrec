# u30d2 — span_pick unit 3.0 design, rev 2 (review r12's rulings applied)

STATE: delivered. Lane u30d2 (opus), 2026-11-07, branch lane/memfn-u30d (from tip 2d189b302). Design only:
no code, no make, no timing, no queued job. OWED: none. No rulings file was named.

## Summary

This lane revised `docs/design/memfn/plan_frame.md` from rev 1 to REV 2. It applies review
`docs/dev/reviews/2026-11-07-r12-memfn-planframe1.md` (F1-F34) as the kit manager ruled it in that file's
"## Rulings" section, using the five critic files and `verify.md` in its sibling directory. The note's new
§R2 maps every finding id to the section it changed, and changed text is marked `[rev2 Fn]`.

- **Build tree: main a678d0a4e**, main's HEAD at this lane's start and the tree r12 cited. The worktree's code
  is identical to it under `memfn/`, `src/` and `tests/memfn/`. No code moved after r12, so no cite drifted
  because of code; the corrections are r12's own, plus two line cites the critics had slightly wrong (below).
- **The units are kept**: 3.0a kit-only, 3.0b the seam plus pcrec's asks in one MF_SITE_ABI commit. No finding
  forces a change. 3.0b grows from M to L (the rung list, `plan_test`, 19 sabotage rows, the D27 author).
- **Readiness**: F1-F5, F10 and F11 are in the text, so 3.0a's build can start on the kit manager's word
  (note §R2 "Readiness" names the section of each one).
- **The reply (3.0b)** now carries: `framed`, `frame_row`, `method` (T-FIND's deciding row, meaning unchanged
  per F1), `search` (an `mf_wsearch` enum: the pick, including a fused row's pick through `fn_rows` BODY, per
  F14), `stream` (`mf_wstream`, ONESHOT renamed RESTART per F24), `fused` (an `mf_wfused` enum NO/FN/ARM, never
  a C id, per F14), `plan_test[]` (the check's per-position test kind, per F12) and `nrung`/`rung[]` (the
  triple of each SIMD rung, per F13).
- **One new pcrec fact**, forced by F13's ruling: the framed ask states whether the define's file-scope sink
  has SIMD brackets (`fs`), because the kit admits a vrun rung only where it does (`ofsskip.c` :660). This is
  my reading of "the reply names the triple per rung"; §7 Q13 asks the kit manager to confirm it and says what
  to drop if a label was meant.

## Fixes by id

Every id r12 raised (F1-F34) has a ruling: FIX-NOW accepted, or DOC/PLAN as proposed. All 34 are applied.

| id | ruling | where it landed in plan_frame.md rev 2 |
|---|---|---|
| F1 | FIX-NOW | §2.4 reader table (formhash row: `wf_plan_brow` keeps T-FIND's row; `wf_plan_bren`'s successor keeps today's ids); §2.4 "B-fn's dependency"; §2.6.3; §5 row (A) |
| F2 | FIX-NOW | §2.6 (the four per-row branches listed); §2.6.0 skeleton; §2.6.1/§2.6.2 loop-state column; §2.6.4 table; §5 row (P) |
| F3 | FIX-NOW | §2.6.0 (new: per-frame skeleton rows; bound and RAISE are the frame's; NEXT from the stream row, missing row refuses); §2.6.4 floor row; §5 rows (L), (N) with reach control `g2_win_gen.c` :689-690 |
| F4 | FIX-NOW | §2.4 "The renderable set" (gate in `fd_holds`, slot FIND only); §2.6.4 witnesses and Goal 1 (PRES rows in REACH equality); §5 row (O) |
| F5 | FIX-NOW | §2.6.4 "The libc and include facts" (OR over three pieces, per-piece values, witness `--memfn=no-fd-d1 abcdef`); §2.6.4 table `libc` column; §5 row (Q) |
| F6 | FIX-NOW | §2.4 reader table (`renderer_rows.tsv`, `rows_check.py` §R, `trace_format.md` FDROUTE); Goal 4 ("one table plus its named pin"); §7 Q3; §8 row; §9 Q3 |
| F7 | FIX-NOW | §2.4 "The composer's refusal is KEPT"; reader table compose.c row; §5 rows (B) (arm absent, refusal names PAIR) and (C) (asserted by message) |
| F8 | FIX-NOW (D77 trim), owner ruled the stream a separate piece | §R1 row 1 (the "Yes" answered the three-piece question); §2.5 intro; §2.5.2 (built rows only); §2.5.3 (no S-mask row); §2.5.5 (new NOTE carried to the finder unit); §6; §7 ~~Q8~~ |
| F9 | FIX-NOW | §2.5.3 (one rule: ST-one, ST-none, ST-many); §2.4 renderable set defined by Table S; §2.5.4; §6 left-to-row-1 list; §5 row (R) |
| F10 | FIX-NOW | §2.3 `fused` row and the "who decides" table (PF arms NO); §2.6.3 (fused rows = B-fn and the offset-skip arm; other arms ARM) |
| F11 | FIX-NOW | §2.4 table keyed by T-FRAME ids (E-stmt for the composer; non-window FIND sites as arms[]'s exception); §2.6.1, §2.6.2 and check rows keyed E-find/E-stmt/E-generic; §2.3 "Rev 0's renderer" |
| F12 | FIX-NOW | §2.3 `plan_test` member and "The check's members"; §2.6.3 residue on fused frames; Goal 2 population; §5 row (AB) |
| F13 | FIX-NOW, ruled "the reply names the triple per rung" | §2.3 `nrung`/`rung[]`; §2.2 `fs`; §2.1 and ASK-1 (`fs`); §2.7; Goal 5 (MASK only in rungs); §5 concurrency (U2+U3 overlap) and rows (W), (AE); §6 FIXED columns name layer and target; §7 Q13 |
| F14 | FIX-NOW, ruled "cross the facts" | §2.3 `search` and `fused` (enum), the "who decides" table; §2.6.3 declared triples; §2.8; §7 Q4, ~~Q7~~ |
| F15 | FIX-NOW (doc) | §6 table restated (FIXED columns, a "what else moves" column, RENDERER row with one site under a lever, SEARCH bundle and HORS limit, STOP's check) |
| F16 | DOC + PLAN | §2.2 "The round-trip projection"; Goal 3 fixture; §2.8 classifiers in the spellings layer; §5 row (AD); build trigger [IR-FORM] |
| F17 | DOC | §2.8 column "what is C-specific in it today" |
| F18 | DOC | §2.4 "HORS keeps a second filter" (rev 1's claim withdrawn; trigger F5's second half) |
| F19 | PLAN | §2.3 "Known residue"; §2.6.2 last paragraph; §7 Q9 (PROVES column, trigger and the confirming G2 compare) |
| F20 | FIX-NOW | §2.4 census row (T-STREAM, check and skeleton rows, fused rows as EXC); §8 span_pick §The tables row |
| F21 | FIX-NOW | §2.5.2 source column; §5 3.0a content (pin with a SOURCE column), rows (M), (R); Goal 4 narrowed; §9 Q2 |
| F22 | DOC | §4.2 ASK-1 note; §0 row 1; §7 Q12 |
| F23 | DOC (main's) | §7 Q10 (quotes the sentence and the "Yes"; ruling (2)'s home); §8 D186 row |
| F24 | FIX-NOW (XS) | §2.1 parenthesis, §2.3, §2.5.1 (`MF_WSTREAM_RESTART`) |
| F25 | FIX-NOW (doc) | §2.4 reader table ((a) rows added); §3 historical class stated as a class of 304 lines ((b)); §3 [SEAM-READER-CENSUS] paragraph and §7 Q11 ((c)); §3 package `memfn.h` :1483-1486 ((d)); §8 rows |
| F26 | FIX-NOW | §2.2 "Allocation" (the plan function takes its allocator); §4.1; Goal 3 (0 arena growth); §5 row (AC) |
| F27 | DOC | Non-goals and §7 Q5 (`finder.c` :650); §10; §3 (`PURITY_FLOOR` :132, read at :138); §2.5.3 (B-fn has no `next`; floor resume :2324); §2.5.1 and §2.7 (vrun's trim-empty case) |
| F28 | FIX-NOW | §2.4 "One accessor per table"; Goal 4; §4.1; §5 row (D) (planted as a copy of `fd_renderer`'s loop) |
| F29 | FIX-NOW | Goal 2; §4.1 (site_rec records the BODY row and rendered rungs); §5 3.0b content (define side from what the define stored); row (E2); §9 Q2 |
| F30 | FIX-NOW | Goal 2 (cells, floors, impossible cells, `_sh[256]`); §5 3.0b content; row (X); §9 Q2 |
| F31 | FIX-NOW | Goal 2 (text classes); Goal 5 (exact emptiness); §5 3.0b content; rows (Y), (Z), (AA); §9 Q2 |
| F32 | FIX-NOW | Goal 3; §3 package (`memcmp`, hex dump); §4.2 ASK-3 (whole reply); §5 row (H) |
| F33 | FIX-NOW | §5 3.0b content and rows (S), (T), (U) |
| F34 | FIX-NOW | Goal 3 (six stated callbacks plus a counting sink); §5 rows (G), (V), (W) |

Rulings beyond the findings: the D27 spec-first author for 3.0b's seam contract is named in §0 row 7 and in
§5's 3.0b content. The process change for the critic skill is not this note's (it is on the branch already,
5fd23b2bd).

Not applied: none.

## What changed from rev 1

- **§R2 added** (finding -> section -> one line), with the unit-split statement and the readiness list.
- **The seam (§2.2, §2.3)**: `mf_wdecide` gains `fs` (the define's file-scope sink, read for its bracket
  stated-ness only). The reply gains `search`, `plan_test` and `nrung`/`rung[]`; `fused` becomes an enum;
  ONESHOT becomes RESTART. A "who decides each value" table covers every frame and renderer. The round-trip
  projection and the allocator rule are stated.
- **The triple (§2.5)**: the support table holds built searches only, each row with its source (ruling text or
  derived basis), plus the floor's "no search" row and VECTOR for the rungs. Table S is one rule over an
  intersection. The unbuilt items move to a NOTE (§2.5.5).
- **The split (§2.6)**: new §2.6.0 skeleton rows; loop-state slots; the four per-row branches listed; the
  tables keyed by T-FRAME ids; fused rows narrowed to B-fn and the offset-skip arm; the libc union over three
  pieces.
- **The asker's retirement (§2.4)**: the gate is scoped to slot FIND; `select_arm`'s refusal is kept; the
  HORS claim is withdrawn; B-fn's dependency is named; one accessor per table; the reader table is completed
  (the pin, trace_format, span_cards, span_pick, window_site, kit.h).
- **§3**: the historical MF_SITE_ABI readers are stated as a class; [SEAM-READER-CENSUS] is named; the
  purity diff becomes a `memcmp`.
- **§5**: 31 sabotage rows (rev 1 had 14): 3.0a A-D and K-R, 3.0b E, E2, F-J, S-Z and AA-AE, with expected ids
  S2982-S3012. The D27 author. 3.0b is now L. The overlap with the target seam's U2+U3 now includes the rung
  list.
- **§6**: every comparison names its fixed pieces, layer and target, and what else moves.
- **§7**: Q6-Q8 are dropped as answered and Q4 is answered in part. Q11 ([SEAM-READER-CENSUS]), Q12 (ASK-1's
  `site_kind`) and Q13 (reading F13 as a rung list) are new. Q9 gains the PROVES column, and Q10 gains the
  quotes and ruling (2).
- **§8**: span_pick's T-STREAM question; span_cards :865; renderer_rows/trace_format; [SEAM-READER-CENSUS].
- `docs/design/memfn/CLAUDE.md`'s plan_frame line now names rev 2.

## Cites checked at the build tree

Checked by grep or sed at main a678d0a4e (the main checkout, HEAD a678d0a4e, `git log a678d0a4e..HEAD`
empty). `git diff --stat a678d0a4e 2d189b302` lists no file under `memfn/src`, `memfn/include`,
`memfn/tests`, `src` or `tests/memfn`, so the worktree's code is the same.

| cite | what it holds at a678d0a4e | status |
|---|---|---|
| `window.c` :2817-2820 `wf_plan_brow`, :2824-2827 `wf_plan_bren` | T-FIND's row; Table B's row id | HOLDS (F1) |
| `formhash.c` :296 (`pair` entry row "PAIR"), :472, :511; `compose.c` :1153-1156 (FDROUTE) | as r12 | HOLDS |
| `window.c` :2729-2737 (`if (w->bren == B_PAIR) ofs_pair_decl`), :2723, :1868-1873, :2760-2762 | the four per-row branches | HOLDS (F2) |
| `ofsskip.c` :275-279 `ofs_pair_decl`, :283 `ofs_pair_text` | as cited | HOLDS |
| `window.c` :2314-2327 `wf_floor_expr`, :2324 its `resume_next`; :2274 `wf_test` | the floor's skeleton | HOLDS (F3, F27) |
| `finder.c` :499-511 `fd_holds`, :313-336 PRES rows, :650 layer, :655-656, :660-668 `?need`, :586-592 `fd_scope` | as cited | HOLDS (F4, F27) |
| `window.c` :1879-1880 (`libc \|\| w->nrun`), :1812 (B-walk libc 0), :2794-2795 | as cited | HOLDS (F5) |
| `tests/memfn/renderer_rows.tsv` :1-12; `rows_check.py` :751-789 (:765 frame E-find or composer); `trace_format.md` :168-183 | as cited | HOLDS (F6) |
| `compose.c` :272-292, :285-291 `fd_renderer`, :294 `select_arm`, :317-325 refusal, :320-322 `kit_ask` | the refusal is :317-325, not rev 1's :262-268 (a comment) | CORRECTED (F7, PREM-3) |
| `compose.c` :134-147 `arms[]`; `ofsskip.c` :418-425 `fn_rows`, :482-493 `ofs_fn_serves`, :655-690 `fn_define`, :660 brackets, :406-416 `prefix_holds`, :910 `ofsskip_arm`; `vrun.c` :406-445 | new rev 2 cites (F10, F13, F14) | CHECKED |
| `memfn_sites.c` :430-431 (every pcrec sink states `simd_open`/`simd_close`); `emit_dfa.c` :7622-7642 | new (ASK-1's `fs`) | CHECKED |
| `window.c` :1314 (`w->table[i]` from `def->table_name`), :2155-2170 `wf_member_of`; C-table/C-own rows | the rows are at :1087-1089 (r12's SEAM-1 said :1086-1088) | CORRECTED (my finding) |
| C-pin, C-stop, C-member rows | at `window.c` :1078, :1082, :1062 (r12's SEAM-5 cited :1080-1081, which are C-pin's text lines) | CORRECTED (my finding) |
| `window.c` :1229-1232 (heap, "not the art's arena"), :1900-1906, :1846, :1673 | as cited | HOLDS (F26) |
| `run_finder.sh` :132 `PURITY_FLOOR=1157`, read at :138 | as cited | CORRECTED (F27, was :133) |
| `memfn.h` :413 `mf_body`, :1467-1482 `mf_wreply`, :1483-1486 `mf_wdecide`'s comment, :556-558, :1435-1441; `kit.h` :538-539, :557-561, :622 `MF_NLEVEL` | as cited | HOLDS |
| `vrun.c` :310-329 `vrun_verify`, :313-315 trim-empty `if (m) return` | as cited | HOLDS (F27) |
| `decider_census.py` :58-61 (LIVE/BYPASS shapes) | as cited | HOLDS (F28) |
| `memfn/tests/run_g2_win.sh` :82 `EFIND_FLOORS`; `g2_win_gen.c` :689-690, :693-694, :998 | the script is `memfn/tests/run_g2_win.sh` | HOLDS |
| `arm_fixtures.c` :2204-2220 `pur_diff`, :2234-2237 `pur_define`'s hooks (4 of 6), :2328-2336 control print | as cited | HOLDS (F32, F34) |
| `plan.md` :835 [SP1E-RENDERER-TABLE], :1844 [SEAM-READER-CENSUS] | as cited | HOLDS (F25) |
| `span_cards.md` :865; `span_pick.md` :45, :51, :86, :109, :114, :131, :135, :369, :408, :420, :423; `window_site.md` :336 | as cited | HOLDS (F25) |
| `git grep -n MF_SITE_ABI` outside ledgers, design notes and history | 304 lines; the symbolic class matches §3's list | HOLDS (F25 (b)) |
| next free sabotage id | S2982 (`git grep` over every local branch: S2980, S2981 the highest) | HOLDS |
| F8's record | 067aca4df on lane/memfn-k1107 only (not on main) | HOLDS |

Every other rev 1 cite stands: r12's PREM lens re-checked about 60 of them at this tree (r12 PROBED-AND-HELD),
and the code has not moved since.

## pcrec-side asks for main

The asks are still facts and checks (D157). pcrec states the frame, the hooks, the sink's bracket
stated-ness and the call, and it reads none of the new fields.

- **ASK-1 (changed)**: the DFA prefilter's phase-1 ask states the offset-skip block's frame (unchanged), and
  now also `fs`: a sink that states `simd_open` and `simd_close`, as `pcrec_memfn_define`'s sinks do
  (`memfn_sites.c` :430-431). The kit calls none of its callbacks. `site_kind` stays UNSTATED: this narrows
  R-35 (a), and §7 Q12 asks main to confirm.
- **ASK-2 (changed slightly)**: call NONE, `def` and `fs` NULL.
- **ASK-3 (simplified)**: at `ofs_site_define`, in a trace build, re-ask and compare the WHOLE reply byte for
  byte (`memcmp`) with `UnanchStart.wr`. pcrec interprets no field.
- **ASK-4 (one addition)**: one run of the named suite is at the SIMD layer, so the rung list is compared too.
- **ASK-5**: unchanged.
- **For main, not code**: file the owner's ruling as a D186 addendum (Q10), rule [SEAM-READER-CENSUS] (Q11),
  and confirm ASK-1's `site_kind` reading (Q12).

## Open questions

Each one has a plain-words recommendation in the note's §7.

- **Q13 (kit manager, new)**: does "the reply names the triple per rung" mean a rung LIST in 3.0b, which needs
  the `fs` sink fact? Or does it mean a label ("this triple is the OFF rung's"), with the list waiting for the
  target seam's U2+U3? Recommendation: the list, in 3.0b. If a label was meant, drop `nrung`, `rung[]`, `fs`
  and rows W and AE; the rest of 3.0b stays as it is.
- **Q11 (main, new)**: does 3.0b fire [SEAM-READER-CENSUS]? Recommendation: narrowly. 3.0b's own members name
  their readers in the same commit, and the census of every other seam member stays the row's own work.
- **Q12 (main, new)**: confirm that `site_kind` is UNSTATED on the prefilter's ask. Recommendation: yes. Stating
  a kind moves bytes, so it belongs to row 1 or later, under the exception's trigger.
- **Q10 (main, restated)**: a D186 addendum. It quotes the owner's sentence and his "Yes" to the three-piece
  question, records the ST-many evidence rule, and gives ruling (2) its home.
- **Q9 (kit manager, extended)**: when vrun is re-expressed, and when the PROVES column lands.
- Q1, Q2, Q3 and Q5 (main) stand. Q4 is answered in part. Q6, Q7 and Q8 are answered and dropped.

## Charter-vs-committed checklist

| brief item | committed |
|---|---|
| read BOILERPLATE, memfn/CLAUDE.md, memfn/src/CLAUDE.md, docs/design/CLAUDE.md | done |
| revise plan_frame.md rev 1 -> rev 2 from r12 and its critic files; its Rulings binding | done: every accepted id applied (Fixes by id) |
| 1. apply every accepted finding; "R2. What revision 2 changed" in span_cards.md's style | §R2: an id / ruled / section / what-changed table |
| 2. mark changed text `[rev2 Fn]` inline | done throughout |
| 3. re-check every cite at the build tree, naming its sha | main a678d0a4e (header, §R2 and "Cites checked"); code unmoved since r12; two critic line cites corrected |
| 4. keep the two-unit split or say why not; name the findings needed before 3.0a's build | kept, with reasons (§R2 "Unit split"); readiness list F1-F5, F10, F11 with sections (§R2 "Readiness") |
| 5. update the pcrec-side asks (facts, D157) and §7: drop answered, add new with recommendations | §4.2 (ASK-1 `fs` and the `site_kind` note, ASK-3 whole reply, ASK-4 SIMD run); §7 drops Q6-Q8 and adds Q11-Q13 |
| do NOT design row 1 or the inline finder; keep §6's statement correct per F13/F15 | §6 restates the comparisons only; the finder inherits §2.5.5's NOTE |
| F8, F13, F14 and the D27 author as ruled | §2.5.5, §2.3/§2.7, §2.3/§2.6.3, §0 row 7/§5 |
| deliver: note plus this report with the deliver file's sections; history-index line; journal nothing | committed on lane/memfn-u30d; history line in `docs/dev/history/claude_md/docs__dev__lanes.md`; no journal entry |
| design CLAUDE.md rev line kept in step | `docs/design/memfn/CLAUDE.md` names rev 2 |
| lanecheck DONE | run before the handback |

## STATE AT HANDOFF

Delivered on lane/memfn-u30d. A design note and a report only: no code, no make, no box job.
OWED: none.
A fresh agent resumes from plan_frame.md §R2 and this report. Open: §7 Q13 for the kit manager (it decides
whether the rung list and `fs` stay in 3.0b), and Q10-Q12 for main.
