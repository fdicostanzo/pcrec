# kitdrift report

## Summary
Checked the kit architecture review's (r91) tracker drift against main's tree and made three skill edits. Docs and skills only; nothing under memfn/ touched. `make -s test-plan-lint` 0 violations; `scripts/check_claudemd_size.sh --all` within limits.

## Drift
- [KIT-ARCH-STEP]: now STATE:started, status lists all three stages (stage 1 the in-flight effort, done; stage 2 the overall review, on the Mac under R-49, review r91 ruled 2026-11-24, revision r92; stage 3 per-feature arch reviews). Moved from Candidates to Active, with a `next:`.
- [SP1E-RENDERER-TABLE]: DONE, moved verbatim to plan_completed.md with a `completed:` line. SF_ASKER_PAIR and `fd_stop.renders_pair` were deleted by b5d1f8dd4 (memfn 3.0a commit 2); `git grep SF_ASKER_PAIR main -- memfn/src` finds nothing, only history text. `fd_renderers` moved into window.c's renderer tables (`ren_skel`, `ren_search`, `ren_stream`, `ren_check`, `ren_fused`, read through `ren_find`); the finder asks `wf_renders`. Caveat recorded in the moved row: it is five tables behind one accessor, not literally one (frame, pick, layer) table.
- [KN-CARRIERLESS]: the kit's "half done" does NOT hold on main as a code change (finder.c still has KN_A/I/M/N and "PEAIMN"). Read as "half the letters are carried": KN_P and KN_E have carriers in `fd_rows`; A, I, M, N have none. Row status/next rewritten to the remaining A/I/M/N removal, leaving "PE".
- Register row 10 (architecture.md, the ride-along register): current in substance; its trigger state matches ([LOOK-LOCATE] not-started; d92d672be exists and is the L3 landing). Fixed two moved cites: `struct CandRow` emit_dfa.c:5752 -> :5831; `MF_MAX_BACK` memfn.h:296 -> memfn/include/memfn.h:308 (value still 8). Ruling untouched. Note: the register is the section "The ride-along register" of architecture.md, not a "part 3" (the file has five tiers).

## Skill edits
(a) pcrec-critic SKILL.md section 4 arch paragraph: on a section review, size and gate go to the first-unit identity lens only.
(b) same paragraph: arch-mode review tree is a `git archive <T>` export with denylisted files removed; every lens points at it.
(c) pcrec-architect SKILL.md section 6 self-check: counts from a name list are a floor (or count by shape), tied to D203's sibling-count grep.
Proposal 3 (commit the round's anchor_map.py as a reusable tool) is the kit's to deliver with its branch; not done here.

## STATE AT HANDOFF
Complete. Nothing owed. Rulings file kitdrift_rulings.md was empty at last read.
