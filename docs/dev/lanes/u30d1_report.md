# u30d1 — span_pick unit 3.0 design, rev 1 ("the plan takes the frame", as a triple)

STATE: delivered. Lane u30d1 (opus), 2026-11-07, branch lane/memfn-u30d (from tip a061437e5). Design only:
no code, no make, no timing, no queued job. OWED: none. No rulings file was named.

## Summary

This lane revised `docs/design/memfn/plan_frame.md` from rev 0 to REV 1, applying Frank's two 2026-11-07
rulings to the kit. The rulings are recorded in the kit journal's "11-07 ~23:00: RULED by Frank" entry and
in `responses.md`'s "proposed decision entry" notice, both on lane/memfn-k1107. The note's new §R1 maps each
ruling and brief item to the section that answers it.

- **The plan is a triple.** A site's find-then-verify plan is (search, candidate stream, check). Each piece
  is a fact table: T-FIND, the new support table plus Table S, and T-VERIFY. The C renderer composes them
  inline (§2.5).
- **The reply.** Rev 0's `resume` becomes `stream` (`mf_wstream`: NONE, ONESHOT, MASK, SHIFT), and `method`
  stays the search. The check is the reply's existing T-VERIFY group (`nplan` .. `run_len`), so no member is
  added for it. Rev 0's `renderer` (a C id) is replaced by `fused`, which names a renderer only where that
  renderer renders the whole triple as one piece (§2.3).
- **Table B splits, with zero movers.** It splits into a search renderer table keyed (frame row, pick),
  which is rev 0's table kept as it was, a stream renderer table keyed (frame row, stream), and check
  renderer rows. B-fn becomes a fused row. The one spelling that moves between functions is D-hors's
  probe-miss resume, and its bytes are identical (§2.6.4). Rev 0's witnesses cover the split.
- **vrun and vany** are compositions in later units, byte-identical either way (§2.7).
- **Row 1** waits for the inline one-member finder (ruled). It runs one-piece comparisons (§6).
- **Units.** Still 3.0a (kit-only, now size M) and 3.0b (the seam plus five pcrec asks, one MF_SITE_ABI
  event). Sabotage rows A-N; the next free kit id is S2982, confirmed by grep.

## The triple (search, stream, check)

| piece | fact table | reply member | today's values |
|---|---|---|---|
| search | T-FIND (`fd_rows[]`, `memfn/src/finder.c:257`), over Table A's stop | `method` | D-hors, D1, D1c, D1w, PAIR, R7w |
| candidate stream | the support table and Table S (new, 3.0a; note §2.5.2-§2.5.3) | `stream` | SHIFT iff D-hors, else ONESHOT; MASK declared, with no producer in 3.0 |
| check | T-VERIFY (Table C, `memfn/src/window.c:1051`) | the existing T-VERIFY group | unchanged, frame-independent |

Which streams each search supports (note §2.5.2): memchr (D1, D1c), the walk and PAIR support ONESHOT only.
D-hors supports SHIFT only. A vector or word-at-a-time search supports ONESHOT or MASK, but none is a
T-FIND row in 3.0. PAIR's frontiers are the search's own state, not a stream: its restart is still c + 1.

## What changed from rev 0

| rev 0 | rev 1 | note |
|---|---|---|
| reply `resume` (`mf_wresume` NONE/NEXT/SHIFT) | `stream` (`mf_wstream` NONE/ONESHOT/MASK/SHIFT) | §2.3 |
| reply `renderer` (Table B row or `form_id`) | `fused` (`form_id` on E-func/E-stmt, the function's id under B-fn, else empty) | §2.3, Q7 |
| one renderer table keyed (frame row, pick) | the same table, now the SEARCH renderer table; renderable set extended with "a supported stream the frame renders" | §2.4 |
| Table B fused search and stream | split into search, stream and check renderer tables, plus fused rows | §2.6 |
| no stream table | the support table and Table S, plus a support pin from the ruling's text | §2.5, §5 |
| Q6 (row 1 waits?) | answered yes and dropped; §6 restated with the controlled comparisons | §6, §7 |
| sabotage A-J | A, H and J restated; K-N added to 3.0a | §5 |
| 3.0a S-M | 3.0a M | §5 |
| no §10 (rev 0 cited it) | §10 lists the span_pick drift | §10 |

## Table B split

Today Table B is three parallel arrays over `B_FN .. B_HORS` (`memfn/src/window.c:1794`): `wf_brows`
(`window.c:1795`), `wf_b_find` (`window.c:2576`) and `wf_b_render` (`window.c:2696`). Its `head` column is the
search (with the bound), its `next` column the stream, and its `define` column the stream's file-scope text
(D-hors's shift table). E-find's loop (`wf_find_expr`, `window.c:2718`) already writes HEAD, TEST, NEXT in
that order. The split turns those columns into the search renderer table (frame row, pick), the stream
renderer table (frame row, stream) and the check renderer rows (`wf_test_to` `window.c:2244`, `wf_test`
`window.c:2274`). B-fn is a fused row matched first (`b_fn_holds`, `window.c:1773`).

Byte identity. Every text is the same spellings in the same order (note §2.6.4's table). The one spelling
that moves between functions is D-hors's probe-miss resume. `d_hors_head` writes
`)) { %s += %s[%s]; continue; } ` (`window.c:2653`), and `d_hors_next` writes `%s += %s[%s]` with the same
three names (`window.c:2673`). The probe miss written as `)) { `, then S-shift's text, then `; continue; } `
is therefore the same bytes. The witnesses are rev 0's: emit_sweep on every arm against the named base,
form hashes unchanged (`arm_fixtures --hash`; check C's stale count 0), G2 green with its EFIND_FLOORS census
(`memfn/tests/run_g2_win.sh:82`), REACH equality, and `decider_census.py`.

## vrun and vany as compositions

- **vrun** (`memfn/src/vrun.c`): (vector block search at KA/KB, `vrun_render` `vrun.c:337`; MASK,
  `vrun_verify`'s `while (m) ... m &= m - 1` `vrun.c:310`; the run compare trimmed by what the mask proved,
  or padded). Today it is fused under fn-pair (`vrun_over`, `vrun.c:406`) as `fn_rows` PREFIX rungs
  (`memfn/src/ofsskip.c:418`). It is re-expressed in its OWN later zero-mover unit, after the target
  seam's U2+U3 and after the first MASK stream renderer exists. It is not in 3.0, because the reply is the
  OFF variant's and the target seam remodels vrun's admission first (D153). Q9.
- **vany** (`memfn/src/vany.c`): a bare vector any-of search whose lowest lane is the answer
  (`vany.c:167`, `vany.c:174`), so it is consumed ONESHOT. It is not routed (`vany.c:16`). It enters as a
  search piece (a T-FIND row, a search renderer row and its card) only in the unit that routes it,
  triggered by a measured win in row 1's search comparison. It is not in 3.0 (D77).

## Cites checked at the build tree

Worktree u30d at tip a061437e5. `git diff 5c3b65fb3 a061437e5` touches only this lane's docs. `git diff
5c3b65fb3 main` (a678d0a4e) under `memfn/`, `src/`, `tests/` touches only `tests/fuzz/fuzz.py`. So every rev
0 cite (u30d_report.md's table) stands, re-checked by grep for the asker readers, the MF_SITE_ABI readers
and the spec search. The new cites:

| cite | at this tree |
|---|---|
| Table C `wf_crows` | `memfn/src/window.c:1051` (the table opens at :1057), `c_plan` `window.c:1096` |
| `b_fn_holds` | `window.c:1773` |
| `B_FN .. B_HORS` | `window.c:1794` |
| `wf_brows` | `window.c:1795` |
| `wf_find_prepare` libc/include facts | `window.c:1877` |
| `wf_test_to` | `window.c:2244`; its call in `wf_find_expr` `window.c:2741` |
| `wf_test` | `window.c:2274` |
| `resume_next` | `window.c:2308` |
| `wf_floor_expr` | `window.c:2314` |
| `wf_b_memchr`, `wf_b_walk`, `wf_b_pair` | `window.c:2532`, `window.c:2549`, `window.c:2562` |
| `wf_b_find` | `window.c:2576` |
| `wf_find_fn` | `window.c:2621` |
| `d_hors_head`, its inline shift | `window.c:2642`, `window.c:2653` |
| `find_head` | `window.c:2662` |
| `d_hors_next`, its text | `window.c:2671`, `window.c:2673` |
| `d_hors_define` | `window.c:2677` |
| `wf_b_render` | `window.c:2696` (`} wf_b_render[] = {` at :2701) |
| `wf_find_expr` | `window.c:2718` |
| `wf_find_define`, the define order | `window.c:2753`, `window.c:2763` |
| T-FIND rows | `memfn/src/finder.c:257` (D-hors) to `finder.c:305` (R7w) |
| `fd_form` | `memfn/src/kit.h:538` |
| `ofs_pair_text` | `memfn/src/ofsskip.c:283` |
| `fn_rows` | `ofsskip.c:418` |
| `vrun_verify`, its MASK loop | `memfn/src/vrun.c:310`, `vrun.c:317` |
| `vrun_render` | `vrun.c:337` |
| `vrun_over` | `vrun.c:406` |
| vany not routed | `memfn/src/vany.c:16` |
| vany lowest lane | `vany.c:167`, `vany.c:174` |
| formhash `pair` instance | `memfn/src/formhash.c:296` |
| G2 E-find floors | `memfn/tests/run_g2_win.sh:82` |
| G2 D-hors control | `memfn/tests/g2/g2_win_gen.c:694` |
| `mf_wreply` | `memfn/include/memfn.h:1467` |
| `form_id` width 48, `row` width 8 | `memfn.h:1190`, `memfn.h:1213` |
| D186 title | `docs/dev/decisions.md:10031` |
| the rulings | lane/memfn-k1107 `memfn/docs/journal.md:3636`, `memfn/docs/responses.md:3262` |
| sabotage ids | highest S2981 (lane/memfn-k0 `tests/mech/sabotages/`; `memfn/docs/journal.md:3613`); `git grep` for S2982-S2999 over every local branch finds only this lane's own text |

## pcrec-side asks for main

The triple changes no fact pcrec states (facts only, D157). ASK-1, ASK-2, ASK-4 and ASK-5 are unchanged
from rev 0 (note §4.2).

1. **ASK-1.** The DFA prefilter's phase-1 ask states the offset-skip block's frame (FUNC/FIND/RETURN, MISS,
   POSITION, body ONESHOT, kind UNSTATED, decl_point 0, on_miss_leaves 0, `pred.fn_ref` 1), its define
   hooks, and call DEFINE.
2. **ASK-2.** The run window's ask states call NONE, `def` NULL.
3. **ASK-3 (field list changed).** In a `PCREC_CAND_TRACE` build, `ofs_site_define` re-asks, and every reply
   field must equal `UnanchStart.wr`: the decision group (the check's included) and `framed`, `frame_row`,
   `method`, `stream`, `fused`. pcrec compares them as opaque values. A difference fails the compile as
   "asked-plan-differs".
4. **ASK-4.** Name the trace suite and prove reach with a pcrec-side sabotage row (the ask stating
   STMT/ASSIGN goes red).
5. **ASK-5.** Restate the comments `src/gen/emit_dfa.c:7598` and `emit_dfa.c:4630`.

Not an ask of code: the kit asked main to file Frank's ruling as a decision entry. The recommendation is
an addendum to D186 (Q10).

## Open questions

Each has a recommendation in the note's §7. Q1, Q2, Q3 and Q5 are unchanged from rev 0, and Q6 is answered.

- **Q4 (kit manager), restated.** Row-id strings for `frame_row`, `method` and `fused`; `stream` an enum.
- **Q7 (kit manager), new.** Drop rev 0's `renderer` for `fused`? Recommendation: yes. On a composed frame
  the facts decide the renderer rows, so a renderer id would carry a C spelling across the seam.
- **Q8 (kit manager), new.** Declare MASK in `mf_wstream` now, though nothing produces it? Recommendation:
  yes, so there is one seam event instead of two. It is asserted unproduced (G2's MASK count 0).
- **Q9 (kit manager), new.** When is vrun re-expressed? Recommendation: in its own zero-mover unit, after
  the target seam's U2+U3 and after the first MASK stream renderer exists. Not in 3.0.
- **Q10 (main), new.** Should the ruling be a new D-entry or an addendum? Recommendation: an addendum to
  D186. Search, stream and check are units; a composition is a choice.

## Charter-vs-committed checklist

| brief item | where |
|---|---|
| read rev 0 and u30d_report.md; R1 section at the top in span_cards.md's style | note §R1 (table: ruling or item, change, where) |
| 1. reply as the triple; `resume` -> stream (ONESHOT/MASK/SHIFT in the kit's idiom); `method` the search; the check's field named; streams each search supports | §2.3 (`mf_wstream`; the check = the T-VERIFY group), §2.5.2 (support table: memchr ONESHOT only, vector/word ONESHOT or MASK, D-hors SHIFT) |
| 2. Table B -> search renderer + stream renderer, keyed so rev 0's table is preserved; byte-identical with rev 0's witnesses | §2.6 (search table = rev 0's (frame row, pick) table; stream table (frame row, stream); fused rows; §2.6.4 zero-mover argument and witnesses) |
| 3. vrun as (vector search, MASK, run-compare check): in 3.0 or later; vany as a search piece | §2.7 (later unit, Q9; vany only when routed, not 3.0, D77) |
| 4. facts apart from C spellings | §2.8 (fact tables vs renderer tables), §2.3 (`renderer` replaced by `fused`), Goal 5 |
| 5. row 1 waits (ruled); §6 restated; controlled comparisons varying one piece; not designed | §6 (search, stream, check and stop comparisons; no row 1 design) |
| 6. cites re-checked; pcrec asks updated (facts, D157); units, sabotage (next free S2982, grepped), §7 questions (Q6 dropped, new with recommendations) | header and §5 (S2982 confirmed), §4.2 (only ASK-3's list), §5 (K-N; A, H, J restated), §7 (Q6 answered; Q7-Q10) |
| deliver: note, this report, history index line, design CLAUDE.md line | committed on lane/memfn-u30d |
| journal nothing | none written |

## STATE AT HANDOFF

Delivered on lane/memfn-u30d. No rulings file was named. OWED: none (design only: no make, no timing,
no queued job). The next steps are the kit manager's: rule §7 (Q4, Q7-Q9; Q10 goes to main), launch a design
critic round on `plan_frame.md` rev 1, then build 3.0a and 3.0b under R-35's stage-3 GO.
