# window_split.md rev 2 §3: each new file's title line and provenance line (assemble.py R5).
# The prefix_k transcription (memfn/PROVENANCE.md row 54) is Table A's A-model rows (stop) and
# Table C's C-model rows (verify); every other new file is kit original.
prov  window_stop.c    original pcrec-memory-functions text, except the A-model rows, which transcribe pcrec 7050f8652's src/opt/prefix_k.c selection (verify_cost, model_cost, the scan loop), relicensed 0BSD by its author (D145 addendum 1) (memfn/PROVENANCE.md).
prov  window_verify.c  original pcrec-memory-functions text, except the C-model rows, which transcribe pcrec 7050f8652's src/opt/prefix_k.c selection (the greedy verify pick, its exchange sort, the materiality test), relicensed 0BSD by its author (D145 addendum 1) (memfn/PROVENANCE.md).
title kit_pos.c        THE POSITION QUESTIONS (ARV-5, ARV-16): a 256-bit position set's membership, count, first member, shape, members and fullness, its spelling class, the mass of a position multiset (kit_mass, from presence.c) and the run member pick (kit_run_member).
title kit_pick.c       THE TIE TABLE (window_site.md §2.1) and the functions that search it: the pick's one before-relation and the two TIE predicates (O3).
title window_cands.c   THE DECISION's candidate list (span_pick.md §The shape step 2): cands, rd_set, rd_core, wf_extent, run_role, pinned_yes.
title window_check.c   THE STATEMENT'S RULES (wf_check).
title window_stop.c    TABLE A, the stop per alternative (window_site.md §2.1), and its searchers (wf_a_choose, wf_a_path, wf_a_is_model).
title window_margin.c  TABLE M, the MARGIN, the choice over alternatives (window_site.md §2.1), and its searcher wf_m_choose.
title window_verify.c  TABLE C, the verify plan (window_site.md §2.3), and its searcher c_plan.
title window_decide.c  THE DECISION (phase 1): decide, the one walker over Tables A, M and C through their searchers; rows_hold; reply_of.
title window_plan.c    THE PLAN the text tests (phase 2): offer_at, plan_of and the wf_plan_* accessors (kit.h).
title window_legacy.c  TABLE E's legacy rows: the plan as today's row's site (legacy_ok, run_bytes, run_rank, translate).
title window_frame.c   TABLE E, T-FRAME, the frame (window_site.md §2.6; span_pick 1e), and its searchers: wf_plan_site, wf_prepare, wf_frame_name, wf_tables_check.
title window_ren.c     THE TRIPLE's renderer tables (plan_frame.md §2.5): skeleton, search, stream, check, fused, the support table and Table S, with their searchers (ren_find and the kit.h entries).
title window_span.c    THE SPAN FORM TABLE (wfS; block_span.md §3) and its searchers (wf_stretches, wf_span_render, wf_span_define, wf_span_check).
title window_efind.c   E-FIND's PLAN (wf_find_prepare): C-run's compares and D-hors's window.
title window_ask.c     THE FRAMED ASK (plan_frame.md §2.2-§2.3): mf_wdecide (memfn.h) and its MF_TRACE agreement wf_agree.
title window_parts.c   THE PARTS (window_site.md §1.2's pre-check row): wf_has_parts, wf_parts_check, wf_parts_prepare.
title window_text.c    THE TEXT KIT every renderer calls: wf_rc's writers and the H form.
title window_test.c    THE CANDIDATE TEST text (wf_test_to), shared by E-find and the floor.
title window_floor.c   THE FLOOR ROW (E-generic): its text, its contract and its arm wf_floor_arm.
title window_find.c    E-FIND's TEXT (D172 S3): the B rows' functions, its contract and its arm wf_find_arm.
title window_vform.c   THE V FORM: wf_span_v, its define and the level admission block (where NEON V's text lands, §9).
title kit_kb.c         THE TEXT BUFFER (kb over the caller's mf_arena) and the sink writers (kit_fail, kit_flush, kit_sink_ok, kit_out): the kit's leaf (ARV-7, B-s3; moved from compose.c).
