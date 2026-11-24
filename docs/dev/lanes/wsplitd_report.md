# Lane wsplitd — report

Lane wsplitd (opus), 2026-11-24, on lane/wsplitd (cut from lane/memfn-wsplit @ 4d25fda9a; T =
a0f13ad83, no `memfn/src`/`memfn/include`/`tests`/`memfn/tests` difference). Design only: nothing
under src/, cli/, lib/, memfn/ or tests/ was edited; no make was run.

## Summary

`docs/design/memfn/window_split.md` designs ARV-9 + ARV-16 + ARV-5 as one answer-identical unit
landing before NEON V: window.c (4,672 lines) and `kit_mass` become 21 files of 54-737 lines
(`kit_pos.c`, `kit_pick.c`, and 19 `window_*.c`), with one private header `window.h`. The census
instruments are committed in `docs/design/memfn/window_split/` with the cut as `cut.spec`, so every
number in the note re-runs from its stated command. Premise test TRUE (4672 lines; arch §8 H1 table
present).

## Design

- File list, ranges, public names, reasons: note §3. Public (outside-family) names: kit_pos 8
  (6 new), kit_pick 7, frame 9, plan 7 (`wf_plan_bren` moves to frame), parts 3, ask 2
  (`mf_wdecide`, `wf_agree`), check 1, floor 1, find 1, the rest 0.
- Private header: CENSUS at the pure move (`census.py $W $D/cut.spec --calls`): 79 statics,
  34 types/macros/enumerators, 19 kit.h names crossing (no cost). After accessors A1-A5 (predicted,
  re-counted at the tip): 78 statics, 28 types (5 of them bare struct tags). The rule changes WHAT
  crosses (no table but `use_nothing`), not much how many names.
- Arch C-39's 25 statics (2-file cut) is a comment-inclusive ceiling; this census reads 16 there.
  The 10 names C-39's script counts there and this census does not (b_hors_prepare chosen count
  find_groups run_part_terms walked wf_find_prepare wf_loop_len wf_plan_site wf_stretches) cross
  the cut only in comments or forward declarations (checked by hand); types match (17).
- No file cycle inside the family + presence.c (kitgraph.py, other files dropped). The finder/presence
  SCC survives (fd_pres_run; finder -> wf_renders, A8): F5.
- Order: C0 (FUW-12 stale plants) outside; U1 checks re-cut on the unsplit tree; U2 kit_pos (U2b
  the other files' copies, O6); U3 kit_pick; U4 window.h; U5 accessors in place; then one file per
  commit, emitter end first, ending with `git mv window.c window_decide.c`.
- Binders: 59 window.c mech anchors / 58 files, 55 census rows, 41 window.c G2 plants (2 stale),
  2 rows_check plants, purity population and purity_plant, PROVENANCE rows 53/54, KITHDRS: all
  bucketed by file in note §7.
- NEON V: V text in `window_vform.c`; ARV-11's level C-spelling table as a `.def` beside
  `targets_c.def`, static in `levels.c` with its lookup the only public name (§9).

## Owner rule applied

Every declared table with every function body that names it (note §4 table): TIE (kit_pick, A1),
Tables A (stop, A2), M (margin, A3), C (verify), E + renderer tables + S + support (frame, A4 for the
framed ask), wfS (span, A5), and the small tables (wsearch, nop_decl_rows, wr_members,
wf_param_decl, use lists). No table is searched from 4+ natural homes: the stop rule did not fire.
Two multi-home tables got a cut choice (renderer tables -> frame; wfS -> span). presence.c declares
no file-scope table. One residue: `use_nothing`, data shared by the A and S contracts.

## Open choices

O1 frame's 737 lines vs a `window_ren.c` split (86/41 names and an efind<->ren cycle unless ~4 more
accessors); O2 planner grain (stop/margin/verify/decide separate, 4 names, vs one ~840-line file);
O3 `kit_tie_rule` enum export vs two question-shaped predicates; O4 no file keeps the name window.c
(proposed) vs one part keeps it; O5 MARGIN's own file; O6 ARV-5's other-file copies inside or after
the unit; O7 find->frame 14 names vs merging find into frame (1,089 lines).
Findings: F1 memfn/src/CLAUDE.md has 11 B headroom; F2 decider_census.py's append-plants would
silently create window.c; F3 stale plants S1423/S3092; F4 six `wf_plan` fields with two writers;
F5 the finder/presence cycle; F6 784 docs line cites; F7 no location macros in memfn/src.

## STATE AT HANDOFF

- Commits on lane/wsplitd: cbc8abe02 (the note, its instruments, docs/design/memfn/CLAUDE.md), then
  this report's commit.
- Rulings file `docs/dev/lanes/wsplitd_rulings.md`: empty at every re-read (before each commit and
  this report): no entry applied.
- OWED: none. No runs owed; no ids proposed.
