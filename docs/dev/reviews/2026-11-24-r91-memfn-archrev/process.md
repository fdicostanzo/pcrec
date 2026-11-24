# r91 memfn-archrev process

- freeze: S=30abd8706 (note), T=a0f13ad83, branch tip at freeze c86feec23 (journal-only after 4564d2752), main e11c5f4ef; rulings freeze = main e11c5f4ef (decisions/plan last touched c0f8bd689)
- setup 12:10-12:35; R/tree export of T with archrev*/archreview_report.md removed, journal cut before 2026-11-24 01:07, responses cut before R-48 ack
- launched 5 critics ~12:17 in one message (aggregation opus, sitemap sonnet, register sonnet, firstunit opus, ruling opus), background, unnamed
- all 5 returned in the launch turn; every final reply undeliverable (expected); every file complete with CRITIC COMPLETE; lanewatch DONE rc=0 at 12:27
- durations: register 3.3 min, sitemap 5.6, ruling 7.6, aggregation 9.7, firstunit 10.1
- findings raised: AGG 13, SITE 9 (2 suspected), REG 9 (1 suspected), FU 12 (1 suspected), RUL 14 (2 suspected) = 57 ids -> 21 consolidated
- no verifier agent: every CONFIRMED is a grep/quote claim; coordinator re-ran inline: AGG-1 (kit_pos_class_of kit.h:451, 0 in note), AGG-2 (window.c:2529, 0 in note), AGG-3 (fields.def:111/228, 10 FLD_denies), AGG-5/FU-2 (7 extra window.c->presence lines), AGG-6 (4104 4134 4400), AGG-7 (gate.c:911-913), AGG-8 (architecture.md:157,160), AGG-9/FU-7 (memfn.h:750-754), FU-3 (run_purity_reach.sh:27), FU-4 (k1_ref.c oracle), FU-8 (options.def header; registry.md:154), FU-9 (memfn_sites.c:906, emit_dfa.c:11692), FU-10 (12288), REG-1 (flag_demote_map.md:115), REG-2 (memfn_stamps.c:331-341: not drift), RUL-1 (0 in span_pick.md), RUL-6 (window_site.md:517-523; D162 add 3 l.9579), RUL-7 (integration.md:2599), RUL-8 (plan_frame.md:728-731), RUL-9 (D77 window 0 hits), RUL-10 (plan.md [row by tag]), SITE-4 (parpool 2 importers), SITE-7 (vrun.c:548). All HOLD.
- overlaps: ARV-9 ranges 3 lenses (SITE-3, AGG-5, FU-1); ARV-9 cycle 2 (AGG-5, FU-2); ARV-12 G2 writers 3 (AGG-9, FU-7, RUL-6); ARV-2 CLAUDE.md 3 (FU-10, SITE-5, AGG-13); ARV-5 count 2 (AGG-1, SITE-1); ARV-10 FLAG-DEMOTE 2 (REG-1, RUL-7)
- blinding: the R/tree export dropped docs/dev/lanes/archrev_* AND archreview_report.md (a different lane; over-reach, harmless); journal cut before 2026-11-24 01:07, responses before the R-48 ack. No leaks noticed.
- setup friction: the no_cd_worktree hook blocked two setup commands; zsh does not word-split "$G" (use a function)
- freeze drift: none (main e11c5f4ef at freeze and hand-back; decisions/plan/guide unchanged)
- time to draft: setup 12:10-12:17, critics 12:17-12:27, verify + draft 12:27-12:40

## Process observations
- Arch mode on a SECTION review with 15 suggestions: the size/gate question was asked of both aggregation (a) and first-unit identity, which produced the 3-lens overlaps on ARV-9/12/2. A whole-tree read-only export (R/tree) with the denied files stripped worked well: no critic touched the live repo or needed exclude pathspecs.
- The anchor map (generic, substring rule, enclosing function) fed FU-3/FU-5/FU-11/FU-12 directly; r50's anchors.py hard-coded ranges and could not be reused.
- Ruling lens was again the most record-productive (7 uncited rulings/filings found).

## Proposed changes
1. SKILL §4 ARCHITECTURE MODE, add: "On a SECTION review (a note with N suggestions rather than one feature), give each suggestion's SIZE and GATE to first-unit identity ONLY; aggregation asks about classification and second mechanisms, not size (r91: ARV-9's ranges found by 3 lenses, ARV-12's G2 writers by 3)."
2. SKILL §5 arch mode: "Build `R/tree/` as a `git archive <T>` export with the denylist's files deleted (and denied ledger entries truncated), and point every lens at it: no exclude pathspecs, no live-repo reads (r91: 0 leaks, 5 critics in 3-10 min)."
3. Commit `review/anchor_map.py` as a reusable tool (e.g. scripts/ or tools/review/): the generic SAB anchor -> enclosing-function map; the first-unit lens's "run the anchor map over EVERY function moved" then needs no per-round script.
4. pcrec-architect self-check: "every count command built from a NAME LIST is a floor; say so beside the count, or grep by shape" (r91: C-9, C-16, C-19b, C-34 each read as a census).

## Framework notes
- Five critics, 57 ids, 21 consolidated findings, about 30 minutes wall time end to end with no verifier agent. Verifying inline was the right call when every claim is a grep or a quote (r14's rule held).
