# u30d4 — span_pick unit 3.0 design, rev 2.2 (review r13 applied as ruled)

STATE: delivered. Lane u30d4 (opus), 2026-11-07, branch lane/memfn-u30d (from tip b2fb1bfb3). Design text
only: no code, no make, no box job. OWED: none. No rulings file was named; the binding rulings are review r13's
"## Rulings (kit manager, 2026-11-07)" section.

## Summary

`docs/design/memfn/plan_frame.md` goes from rev 2.1 to REV 2.2. It applies re-check review
`docs/dev/reviews/2026-11-07-r13-memfn-planframe2.md` (r13) as the kit manager ruled it. Every accepted id is
applied: FIX-NOW R1-R11, R15-R19, R21, R25-R27, and DOC R12-R14, R22-R24, R28. R20 is NOTED; the note keeps it as
an optional control in 3.0b. A table, "R2.2. What revision 2.2 changed" (id -> section -> one line), sits at the top.
Changed text is marked `[rev2.2 Rn]`; every id has at least one mark (a per-id count is in the checklist below).
The two-unit split is unchanged.

The shape changes:
- **R1, narrow.** The agreement's FRAME part is compared against the stored record through a per-frame field map
  (§4.1). The decision group is re-derived through `decide`, with the purity harness and ASK-3 as its named
  independent controls. There is no stored decision copy.
- **R2, `stop_test`.** A new reply member beside `plan_test[]`. Its TABLE condition is "hook stated AND the covering
  span offers this set", and the define side is matched by offset. G2's marker is the hook's own spelling,
  `g2w_t<id>_<ref>[`.
- **R3, ST-many.** It is a named refusal raised after the gate, never a decline.
- **R8, unit content.** Every output only the reply reads moves from 3.0a to 3.0b: `fused`, the test kinds, the reply
  ids, the `fn_rows` pick column, the arm walk and the allocator. 3.0a now builds only what the define renders.

The counts are corrected: 3.0b has 18 sabotage rows (S2994-S3011) and the note has 30. RUNG-LIST's trigger now
carries the kit manager's restatement, verbatim. VECTOR moves to §2.5.5's NOTE and to RUNG-LIST.

Fixing these forced two choices the review did not make. Both are written as §7 questions with a recommendation,
and the text follows the recommendation:
- **Q14:** what `stop_test` reports where the search tests the stop by its bytes (B-pair, B-memchr) or probes
  another position (B-hors). It also asks whether to add sabotage row AF (`stop_test` always OWN). The
  recommendation is to keep the offer fact, as ruled, and to add AF.
- **Q15:** three either/or forms where r13 named no preference. The recommendations are: FDROUTE prints `frame=`
  (R10); `reach_equal.py` with `-fmemfn-simd` carries the SIMD-layer agreement (R19); `r33_sim/probe.c` is left
  to break (R23).

The standing-question PLAN rows r13 proposed ("Noted" section: one intersection rule over the three pieces; a
per-piece coverage fact) are NOT among the ruled ids, so they were not applied. They stay main's or the kit
manager's to file.

Commits on lane/memfn-u30d: c32fc9ef7, 37e11d978, 35ad1d46a (WIP note revisions), then the final commit with this
report, `docs/design/memfn/CLAUDE.md`'s rev line and the history-index line.

## Fixes by id

| id | ruled | where it landed |
|---|---|---|
| R1 | FIX-NOW, shape NARROW | Goal 2; §4.1 "The agreement's two halves" + the per-frame field map; §5 3.0b content, row E2; §9 Q2; R2 F29 note; §2.3 "Who decides" pointer |
| R2 | FIX-NOW, shape `stop_test` | §0 row 3; Goal 2; §2.3 (`plan_test`'s TABLE rule and offset match, new `stop_test` row, check members, observable meanings); §2.6.3 residue; §3 memfn.h entry; §4.1 field map; §5 3.0b G2 class and population, row AB; §6; §7 Q14; §9 Q2; R2 F12 note |
| R3 | FIX-NOW | §0 row 4; §2.4 "ST-many refuses AFTER the gate"; §2.5.3 ST-many row; §2.5.4 rule 2; §5 (R) |
| R4 | FIX-NOW | §2.4 "One accessor per table" (shapes narrowed; the 9 strays named; MEMBER_COUNT 59, HITS rule); Goal 4; §5 (D) |
| R5 | FIX-NOW | §2.6.4 witnesses (the new tables print no REACH; `reach_print`'s four contracts); §5 3.0a witnesses |
| R6 | FIX-NOW | §3 package (population patterns, the tables in `window.c`, the plant path, the harness descriptions); Goal 3 |
| R7 | FIX-NOW | §2.5.2 "The support pin" (`rows_check.py` §S, columns, `arm_fixtures --streams`, verbatim RULING cells, landing-time basis witnesses); §5 3.0a content and witnesses, row (M); §9 Q2 |
| R8 | FIX-NOW | §0 row 7; §2.2 allocation; §2.3 "Who reads"; §2.4 `fn_rows` BODY; §4.1 (3.0a = what the define renders; 3.0b gains the reply-only outputs); §5 3.0a/3.0b content, separability, concurrency, size |
| R9 | FIX-NOW | §5 3.0a "Sabotage re-aims" (S1423, S1427, S1428, S1543; S686 moves to 3.0b); §5 3.0b content; §9 Q2 |
| R10 | FIX-NOW | §2.4 reader table (`renderer_rows.tsv` 6th column `fused`, FDROUTE `frame=`); `trace_format.md` row; §8; §7 Q15 (1) |
| R11 | FIX-NOW | §5 (B) (the `rows_check.py` §R invariant over named witness lines), (C), (R); §9 Q2 |
| R12 | DOC | §5 Separability (commit 1 / commit 2 and their sabotage rows) |
| R13 | DOC | §2.6.2 (two S-restart rows, one text); §5 (L), (N) |
| R14 | DOC | §2.4 reader table (six new rows: `memfn/src/CLAUDE.md` :26, `tests/memfn/CLAUDE.md` :37, the comments, the `_Static_assert`s, `units_inventory.md`, `window_site.md` :272/:340/:342); §8 |
| R15 | FIX-NOW | §2.6.0 "Render order is not text order" |
| R16 | FIX-NOW | §2.2 (the site `opts` mechanism); §5 (I) (plant on `opts`, plus the `--memfn=no-fd-d1` fixture) |
| R17 | FIX-NOW (a), DOC (b) | (a) §5 (F) asserts ASK-3's message; (b) Goal 2 and §9 Q2, the chain |
| R18 | FIX-NOW | §2.2 "Contract lines" 1-4; §2.3 "The observable meaning of each value" (moved from §5's G2 classes) |
| R19 | FIX-NOW (doc) | Goal 2; §5 3.0b witnesses (G2 OFF only; `reach_equal.py` the corpus carrier, both layers) and heavy runs; §9 Q2; §7 Q15 (2) |
| R21 | FIX-NOW | §2.2 round-trip projection (the `miss`/`n` relation); §5 (AD) population |
| R22 | DOC | §5 header (30 rows; 3.0b 18, S2994-S3011); Size; §R2.1 correction note |
| R23 | DOC | §3 package (`r33_sim/probe.c` :94, left to break); §7 Q15 (3) |
| R24 | DOC | §2.3 `stream`; §2.6.3 (fused-rows table with a `stream` column, the offset-skip arm's RESTART home); Goal 5; §5 3.0b, (X); §9 Q3 ("fact column") |
| R25 | FIX-NOW (D77 trim) | §2.3 `search` (no VECTOR); §2.5.2 (VECTOR row removed); §2.5.5 NOTE; §7 RUNG-LIST content; Goal 5; §9 Q2 |
| R26 | FIX-NOW | §5 3.0b G2 impossible cells (E-func and E-stmt allow RESTART or NONE; NONE iff `fused` ARM) |
| R27 | FIX-NOW | §2.3 (the `offsetof(mf_wreply, framed)` comparator); §3 package |
| R28 | DOC | §7 RUNG-LIST trigger (verbatim: "row 1 compares a SIMD-on cell, or the first MASK stream RENDERER ROW lands"); §6; R2 F13 note |
| R20 | NOTED | §5 3.0b content: the reached-ask control, marked optional |

Not applied: none of the ruled ids. Not in the ruled set and so not applied: r13's two proposed PLAN rows from its
standing questions.

## R1 and R2 as ruled

**R1 (NARROW).** The define-side reply of the kit's MF_TRACE agreement is assembled, zeroed first, from two sources:
- **The FRAME part comes from the STORED record.** It is read through a per-frame field map in §4.1, which covers
  E-find, E-generic, E-func and E-stmt for `framed`, `frame_row`, `method`, `search`, `stream`, `fused`, `plan_test`
  and `stop_test`. The map reads `site_rec` (`kit.h` :239-270) and `wf_plan` (`window.c` :1242-1274). On E-func and
  E-stmt, `wplan` is NULL (`window.c` :1947-1950), so the map reads the stored site's `form` and `r->arm` there.
- **The decision group is RE-DERIVED.** `decide` runs on the stored site with the define's hooks and call, and
  `reply_of`'s decision half projects the result.

The decision half shares the plan function's source, so the note calls it a tripwire. Its named independent controls
are the purity harness and ASK-3. A decision fault common to both calls moves the define's text, which emit_sweep
sees. No decision copy goes into `site_rec`. Row E2 now names which half its plant lands in (the frame-part half).

The map needs three NEW members:
- a `wf_plan` stream renderer row (3.0a, since the define renders from it);
- the `site_rec` BODY row (3.0b, F29's);
- the `fn_rows` pick column (3.0b).

**R2 (`stop_test`).** `stop_test` is a `uint8_t` `mf_wtest`. Its value is TABLE iff the hook is stated AND the span
covering the stop's offset offers the stop's set; otherwise OWN. It is answered on E-find's composed rows when
`stop_ix >= 0`, and is NONE on the floor and on fused, E-stmt and ARM frames.

`plan_test`'s TABLE condition is corrected to the same "hook stated AND offered" rule. The define side is matched by
OFFSET, because the define's `off[]` holds the plan plus the stop, sorted (`window.c` :1300-1306), so its indices
differ from `plan[]`'s.

G2's marker is `g2w_t<id>_<ref>[` (`g2_win_gen.c` :569-574; G2 already searches it at :1065), matched to each offset
through G2's own offer. Row AB's population includes a stop below a TABLE position and a stated hook with no offer.
The memfn.h history entry and §2.6.3's residue name the new member.

One choice follows from the ruling and is left open as §7 Q14: what the offer fact means on stops that the search
tests by their bytes. Q14 also asks whether to add row AF.

## Cites checked at the build tree

Build tree: main **a678d0a4e**. That was main's HEAD at this lane's start (`git -C /home/pcrec/projects/pcrec log
-1 main`), and it is unchanged since r13 froze it. Every cite rev 2.2 adds or touches was re-read with `git show
a678d0a4e:<file> | sed -n`. All of them hold:
- `window.c`: :999-1002, :1082, :1224, :1242-1274, :1281-1290, :1296-1315, :1842, :1850-1851, :1917, :1947-1950,
  :2166, :2169, :2205, :2230, :2320-2321, :2324, :2536, :2553, :2566, :2642-2656, :2708-2711, :2723, :2729,
  :2838-2846, :2854 (`wf_floor_arm`), :2884 (`wf_find_arm`); the comment lines :39, :1264, :1533, :2484, :2692,
  :2815.
- `kit.h`: :239-270, :557-568.
- `compose.c`: :170-171, :277-283, :295-327, :333-339, :1100-1104, :1151, :1180-1186.
- `gate.c`: :648-656, :882-908 (four passes), :893.
- `finder.c`: :499-511, :514-516, :659-668.
- `memfn_sites.c`: :449.
- `emit_dfa.c`: :7610-7613.
- `vrun.c`: :327 (`m &= m - 1`).
- `g2_win_gen.c`: :569-574, :639, :1065.
- `run_g2_win.sh`: :66, :122, :134, :138, :159.
- `run_purity_reach.sh`: :27-37, :41-74.
- `reach_equal.py`: :237-240.
- `rows_check.py`: :103, :157-158, :756, :765.
- `decider_census.py`: :38-41, :65, :74, :75.
- `tests/memfn/CLAUDE.md`: :37, :43.
- `run_finder.sh`: :121-131.
- `run_wreply.sh`: :65.
- `docs/dev/lanes/r33_sim/probe.c`: :94 (and its jobs `240-kit-r33-sweep.sh`, `241-kit-r33-rp.sh`).
- `span_pick.md`: :378.
- `units_inventory.md`: :56, :111.
- `window_site.md`: :272, :340, :342.
- `memfn/src/CLAUDE.md`: :26.
- `tests/mech/sabotages/S686_fn_rows_body_order_swapped.sh` (it exists).

Two corrections against the review's text:
- The C-stop drop is `c_stop`'s `plan_drop` at `window.c` :999-1002; the row's declaration starts at :1082. The
  critics' ":1080-1081" is the C-pin row's description text.
- `wf_floor_expr`'s `wf_test` is at :2320 and `wf_open` at :2321. :2324 is `resume_next`, so the note keeps it as
  the floor's resume.

## Charter-vs-committed checklist

- [x] Read BOILERPLATE.md, memfn/CLAUDE.md, memfn/src/CLAUDE.md and docs/design/CLAUDE.md first.
- [x] Wrote only in the worktree (`docs/design/memfn/plan_frame.md`, `docs/design/memfn/CLAUDE.md`, this report,
  the history index) and the scratch dir `/var/tmp/pcrec-pcrec/scratch/memfn/u30d4/` (a read copy of `window.c`
  at a678d0a4e). No `/tmp`, no code, no make, no box job.
- [x] Every accepted id applied as r13 proposes it: R1-R11, R15-R19, R21, R25-R27 (FIX-NOW) and R12-R14,
  R22-R24, R28 (DOC). Marks per id in the note: R1 7, R2 13, R3 6, R4 3, R5 2, R6 2, R7 3, R8 11, R9 3, R10 4,
  R11 2, R12 1, R13 4, R14 8, R15 1, R16 2, R17 3, R18 3, R19 6, R21 2, R22 3, R23 2, R24 6, R25 7, R26 1,
  R27 2, R28 4.
- [x] R1 NARROW (the frame part against the stored record with §4.1's field map; the decision group through
  `decide`; the purity harness and ASK-3 named; no stored decision copy).
- [x] R2: a separate `stop_test`; TABLE = hook stated AND offered; the define side matched by OFFSET; the G2 marker
  is the hook's own spelling; AB's population includes the stop-below-TABLE case and the stated-no-offer case.
- [x] R28's restated trigger, verbatim.
- [x] "R2.2. What revision 2.2 changed" at the top (id -> section -> one line); changed text marked `[rev2.2 Rn]`.
- [x] Every touched cite re-checked at main HEAD a678d0a4e.
- [x] Two-unit split unchanged.
- [x] The choices r13 left open are written as §7 Q14 and Q15, each with a recommendation; none was made silently.
- [x] `docs/design/memfn/CLAUDE.md`'s plan_frame line moved to rev 2.2 (the file stays under its 12 KB limit).
- [x] The report's line is in the history index (`docs/dev/history/claude_md/docs__dev__lanes.md`).
- [x] `scripts/lanecheck --deliver docs/dev/lanes/u30d4_deliver.txt u30d4` run from the worktree, ending on DONE.
