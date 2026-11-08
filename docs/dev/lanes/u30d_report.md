# u30d — span_pick unit 3.0 design ("the plan takes the frame")

STATE: delivered. Lane u30d (opus), 2026-11-07, branch lane/memfn-u30d off lane/memfn-k1107 (= main
5c3b65fb3). Design only: no code, no make, no timing, no queued job. OWED: none.

## Summary

This lane wrote `docs/design/memfn/plan_frame.md` rev 0, the design of span_pick stage 3's first unit
for kit request R-35 item 2. Its main decisions:

- **The ask states the frame.** The phase-1 ask states the frame of the site its NEXT rows define. Today
  only the DFA prefilter's ask has NEXT readers. For it the frame is the offset-skip block's: FUNC/RETURN,
  kind UNSTATED, its define hooks, call DEFINE. The run window's ask states no frame (call NONE).
- **The new call.** `mf_wdecide(art, site, def, call, out)` takes a new fact, `mf_wcall`: UNSTATED
  (refused), NONE, DEFINE or EMIT. EMIT carries the phase set.
- **The reply grows.** Appended last: `framed`, `frame_row`, `method`, `renderer` and `resume`. Each is a
  kit row id or an enum, never C text. The decision stays frame-independent in 3.0.
- **The asker fact retires.** `SF_ASKER_PAIR` and `renders_pair` are replaced by ONE declared renderer
  table keyed by (frame row, pick). A T-FIND row holds only where the asking frame renders its pick. This
  is review 2026-11-05-r2 F5/F9 and plan row [SP1E-RENDERER-TABLE]. The check gains a witness that does
  not exist today: the composer's two-member stops.
- **The numbers.** One MF_SITE_ABI event (the next number at landing; 25 here). MF_CLASS_V does not move.
- **Two units.** 3.0a is kit-only (the renderer table and the plan's frame part). 3.0b is the seam plus
  pcrec's five asks, in one commit. The next free kit sabotage id is S2982 (highest in use S2981, lane k0).
- **Row 1.** Its controlled candidate set needs a new inline one-member finder, with its card, BEFORE
  row 1. The only thing 3.0's reply must carry for that is `renderer`.

## The design note

`docs/design/memfn/plan_frame.md` (rev 0), with a line in `docs/design/memfn/CLAUDE.md`. Sections:

- §0 decisions
- §1 goals (five, ranked; byte-identical first, the form hashes included)
- §2 what crosses the seam (§2.1 per NEXT row; §2.2 the call; §2.3 the reply; §2.4 the asker fact's
  retirement, with every reader and its disposition)
- §3 the MF_SITE_ABI / MF_CLASS_V readers by class, and the same-commit package
- §4 the kit/pcrec split and the pcrec asks
- §5 the two units with witness, sabotage rows A-J, heavy runs and separability
- §6 what is left to row 1, and its controlled candidates
- §7 six questions
- §8 amendments to other documents
- §9 the standing questions (Q1 not relevant; Q2 relevant; Q3 relevant, narrowly: the cards' form hashes)

## Cites checked at the build tree

Checked by grep/sed at worktree u30d (main 5c3b65fb3 + the deliver-file commit a22b4fb00):

| cite | at this tree |
|---|---|
| span_pick.md unit 3.0 staging row | `docs/design/memfn/span_pick.md:408` |
| span_pick.md N11 row | `span_pick.md:423` |
| span_pick.md frame at plan time | `span_pick.md:49-52` |
| span_pick.md reply grows at 3.0 | `span_pick.md:77` |
| span_pick.md axes, frame per call from 3.0 | `span_pick.md:86`. Its inner cites drifted: window.c :1061 is now `memfn/src/window.c:1225`, and finder.c :934 (layer) is now `memfn/src/finder.c:647` |
| span_pick.md asker named exception | `span_pick.md:135` |
| span_pick.md watched witness, 3.0 row | `span_pick.md:341` |
| span_pick.md compose/emit_dfa cites in :49-50 | `memfn/src/compose.c:255-258` (unchanged); emit_dfa.c :7600-7602 is now `src/gen/emit_dfa.c:7598-7603`; finder.c :938 (`SF_WINDOW_STOP`) is now `finder.c:656` (`SF_ASKER_PAIR`) |
| R-35 and ruling (a) | `memfn/docs/requests.md:805` |
| MF_SITE_ABI definition, 24 | `memfn/include/memfn.h:39` |
| MF_CLASS_V, 8 | `memfn.h:1080` |
| frame "read by phase 2 only" | `memfn.h:556-558` |
| phase-1 reply comment, "never a frame fact" | `memfn.h:1435-1441` |
| `mf_wreply` struct | `memfn.h:1467-1482` |
| `mf_wdecide` declaration | `memfn.h:1487-1488` |
| `mf_form` has no UNSTATED zero | `memfn.h:261-266` |
| `mf_wdecide` body | `memfn/src/window.c:1222-1238` |
| `decide` | `window.c:1149` |
| `reply_of` | `window.c:1191` |
| Table E `wf_erows` | `window.c:1616-1621` |
| `wf_brows` | `window.c:1802-1817` |
| `wf_find_decide` | `window.c:1826` |
| `renders_pair = 1` | `window.c:1840` |
| `wf_prepare` | `window.c:1892` |
| `+hors` suffix | `window.c:1944-1945` |
| `wf_part_site` | `window.c:1984-2007` |
| `wf_parts_prepare` | `window.c:2031` |
| SF_ASKER_PAIR | `memfn/src/finder.c:105-106` |
| PAIR row | `finder.c:289` |
| the setter | `finder.c:656` |
| row gate | `finder.c:503` |
| `set_facts` SF_TWO_MEMBER | `finder.c:555` |
| `find_facts` | `finder.c:567-574` |
| `fd_find` | `finder.c:640` |
| layer OFF | `finder.c:647` |
| `fd_stop.renders_pair` | `memfn/src/kit.h:546-556` |
| gphases comment | `compose.c:255-258` |
| renderer comment | `compose.c:262-270` |
| `fd_renderers` | `compose.c:277` |
| `fd_renderer` | `compose.c:285` |
| `select_arm` | `compose.c:294` |
| `ask_sel` | `compose.c:1007` |
| `mf_ask` | `compose.c:1044` |
| rule 2 re-ask | `compose.c:1187` |
| `mf_define` | `compose.c:1211` |
| `mf_defined` row | `compose.c:1316` |
| `mf_emit` DEFINE\|USE | `compose.c:1325` |
| formhash comments | `memfn/src/formhash.c:272`, `formhash.c:446` |
| formhash plan accessor | `formhash.c:472` |
| `req_run_member` | `src/gen/emit_dfa.c:1058` |
| its ask | `emit_dfa.c:1068` |
| its loud check | `emit_dfa.c:1071` |
| `UnanchStart.wr` comment | `emit_dfa.c:4630-4636` |
| ask point | `emit_dfa.c:4792` |
| `find_site` frame | `emit_dfa.c:6922-6936` |
| `cand_asked_hold` | `emit_dfa.c:7066` |
| `pf_site_of` | `emit_dfa.c:7131` |
| `next_keys` | `emit_dfa.c:7298-7306` |
| `next_key_holds` | `emit_dfa.c:7317-7321` |
| `ofs_test_of` | `emit_dfa.c:7402-7412` |
| `window_reply_ask` | `emit_dfa.c:7604-7616` |
| `ofs_site_define` | `emit_dfa.c:7622-7642` |
| `cand_ask` | `emit_dfa.c:8352` |
| offset rows | `emit_dfa.c:10471-10500` |
| RE-SEED refusal | `emit_dfa.c:13002` |
| cover site | `src/gen/known.c:488-496` |
| `pcrec_memfn_site` abi | `src/gen/memfn_sites.c:455` |
| purity harness | `tests/memfn/arm_fixtures.c:2036` |
| `pur_diff` | `arm_fixtures.c:2204` |
| its calls | `arm_fixtures.c:2271`, `:2278`, `:2305`, `:2323` |
| control print | `arm_fixtures.c:2334` |
| PURITY_FLOOR 1157 | `tests/memfn/run_finder.sh:133` |
| purity reach table | `tests/memfn/purity_rows.tsv:1-9` |
| census rows | `tests/memfn/decider_census.tsv:24`, `:29`, `:66-67` |
| G2 reply copy | `memfn/tests/g2/g2_win.h:44-53` |
| G2 calls | `memfn/tests/g2/g2_win_gen.c:742`, `:797`, `:855` |
| trace format | `memfn/docs/trace_format.md:102-113` |
| memfn/src CLAUDE.md asker lines | `memfn/src/CLAUDE.md:9`, `:15`, `:41` |
| include CLAUDE.md number | `memfn/include/CLAUDE.md:4` |
| [SP1E-RENDERER-TABLE] | `docs/dev/plan.md:835-839` |
| review F5, F6, F9 | `docs/dev/reviews/2026-11-05-r2-memfn-sp1e.md:96-102`, `:105-111`, `:124-130` |
| ideas, apples and oranges | `memfn/docs/ideas.md:780-785` |
| k0 sabotage ids S2975-S2981 | `memfn/docs/journal.md:3598`, `:3613` |
| S2903 anchor | `tests/mech/sabotages/S2903_kit_accepts_unstated_noise.sh:13` on `compose.c:908` |
| literal-pin search | `git grep` for `MF_SITE_ABI` with a number, and for `kit abi`, over tests, memfn/tests and scripts: none (`memfn/tests/G2M6_REPORT.md:131`, `:243` assert by kind) |
| no spec reader | `git grep mf_wdecide\|mf_wreply\|renders_pair\|SF_ASKER_PAIR -- docs/spec docs/guide`: none |

## pcrec-side asks for main

All are facts and checks (D157), to travel in the kit's 3.0b package under R-35 ruling (a):

1. **ASK-1.** The DFA prefilter's phase-1 ask (`window_reply_ask`) states the offset-skip block's frame:
   form FUNC, op FIND, handoff RETURN, empty MISS, use POSITION, body ONESHOT, site_kind UNSTATED,
   decl_point 0, on_miss_leaves 0, `pred.fn_ref` 1. Its hooks are `fn_name` and `table_name` stated,
   `miss` MF_MISS_N, `comment_tier` NONESSENTIAL, with call DEFINE. These are the same values
   `ofs_site_define` states.
2. **ASK-2.** The run window's ask (`req_run_member`) states call NONE, `def` NULL.
3. **ASK-3.** In a `PCREC_CAND_TRACE` build, `ofs_site_define` re-asks with its own site, hooks and
   DEFINE. Every reply field must equal `UnanchStart.wr`, else the compile fails as the named invariant
   "asked-plan-differs".
4. **ASK-4.** Name the suite whose trace build runs ASK-3 over DFA prefilter sites (`run_cand_oracle.sh`
   or `run_fallback_table.sh`), and prove reach with a pcrec-side sabotage row: the ask stating
   STMT/ASSIGN goes red.
5. **ASK-5.** Restate the comments `emit_dfa.c:7598-7603` and `:4630-4636`. The ask states the offset
   rows' frame; the rows below define their own site.

## Open questions

Each has a recommendation in the note's §7:

- **Q1 (main).** Should the run-window ask state no frame, or the part's frame? Recommendation: no frame
  for now.
- **Q2 (main, kit manager).** A PARKED reply goes to a different site whose frame the ask does not state.
  Recommendation: leave it in 3.0, and file a plan row triggered by "OFS states a kind".
- **Q3 (main).** One renderer table, or two lists? Recommendation: one.
- **Q4 (kit manager).** Strings or enums for the reply's new fields? Recommendation: row-id strings, with
  `resume` an enum.
- **Q5 (main).** Is span_pick :86's "engine/target/layer per call from 3.0" still meant? Recommendation:
  read it as T-FRAME's frame; target and layer stay art facts. Amend :86.
- **Q6 (Frank).** Should row 1 wait for the inline one-member finder, so its first priced comparison is
  like-for-like? Recommendation: yes.

## Charter-vs-committed checklist

| brief item | where |
|---|---|
| 1. Goals ranked, checkable; byte-identical first with an identity witness | note §1 Goal 1 (emit_sweep every arm vs named base, plus form hashes) |
| 2. per NEXT row's frame (form, handoff, site_kind); the call (hooks, phase set); the reply (method, resume, frame row); the asker fact's retirement with every reader and disposition | §2.1, §2.2, §2.3, §2.4's reader table |
| 3. MF_SITE_ABI (+ MF_CLASS_V): readers by grep, same-commit package | §3 (MF_CLASS_V: no move, with the reason and its readers) |
| 4. pcrec/kit split; pcrec edits as numbered fact asks | §4.1, §4.2; this report's asks |
| 5. units with witness, sabotage ids (next free), validation, separability | §5 (two units; rows A-J; S2982 expected) |
| 6. left to row 1; controlled candidates; does the reply carry anything for them | §6 (yes: `renderer`) |
| 7. open questions with recommendations | §7 |
| the three standing questions | §9 |
| deliverable: note, report, history-index line, design CLAUDE.md line, lanecheck DONE | committed on lane/memfn-u30d |
| journal nothing | none written |

## STATE AT HANDOFF

Delivered, tip on lane/memfn-u30d. OWED: none (design only: no make, no timing, no queued job). No
rulings file was named. The next steps are the kit manager's: rule §7, launch a design critic round on
`plan_frame.md`, then build 3.0a and 3.0b under R-35's stage-3 GO.
