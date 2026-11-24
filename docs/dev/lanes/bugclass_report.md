# bugclass report (sonnet, 2026-11-24)

## Summary
Bugs are handled at the class level (D203). Seven edits, docs and skills only; no code, no make beyond
`make -s test-plan-lint` (2 pass) and `scripts/check_claudemd_size.sh --all` (440 files within limits).

## Edits
1. CLAUDE.md: one situation-index row, "propose a fix for a bug" (root CLAUDE.md 18.3 KB -> under the 20 KB limit).
2. docs/dev/lanes/BRIEF_TEMPLATE.md (TRIAGE LANE paragraph) and .claude/skills/pcrec-manager/monitoring.md (§2 item 3, the red-triage step; the file has no separate triage section): class, rule or mechanism, sibling count with grep, class-level fix shape.
3. .claude/skills/pcrec-manager/SKILL.md: one always-on bullet after "A REASON given to the owner".
4. .claude/skills/pcrec-critic/SKILL.md: lens "general form (bug fix)", subjects C D, sonnet, runs even at one critic.
5. docs/dev/known_issues.md: field renamed "Fix shape (class level)" in every entry that has it (K155's line left alone), format note added at the top, open entries re-checked (below).
6. docs/dev/decisions.md: D203. decisions are a dormant pair (doc_format.md profile table), so no index line.
7. Doctrine grep (BOILERPLATE.md, learnings.md, the manager skill and its sub-files, root CLAUDE.md): the close-before-start, ninety-percent and one-pass doctrines live in memory files and plan/review records only, not in those files, so there was nothing to annotate. D203 itself records the override.

## Fix-shape recheck
Open entries with the field (K155 skipped, k155fix owns it):
- K158 (two shapes): old "a fix lane finds the pass" (instance) -> superseded; second shape rewritten to class: per-item rescan of the emitted body, `git grep -n 'strstr(' -- src cli lib` = 13 sites, two loop over a growing body (emit_vm.c:1841, vm_stmt.c:1095).
- K157: old "a fix lane decides" -> class: fixed capacity picked without the pattern; ONE pick site (`git grep -n 'VM_DEFAULT_RESUME_FRAMES\|VM_DEFAULT_TRAIL_FRAMES' -- src lib` = 5 lines); fix at the pick, limits.md §8a.
- K154: already class level (K150/K151 family, refuse before the work).
- K151: already class level (general depth/size mechanism, refusal ceiling before the table).
- K150: already class level (same mechanism; build prefix once or bound).
- K148: already class level (PCREC_SPINE_EACH, general spine mechanism).
- K107: already class level ((a) single effort budget dissolves the class).
- K105: already class level (adaptive-dense arm / [PRIOR-COST-UNIFY]).
- K104: already class level (rev-end-width or admission term).
- K103: already class level (entry fast path, rev-end-width).
- K111: old "flip the lib row's entry_match" (instance) -> class: two resolvers, two probes; `path_is_file(` 6 sites, `dir_has_exact` 3.
- K101: already class level (bound each stream by the other's pending hit; one gate, whole class of folded runs).
- K89: old "K84's: widen the check to the view table" -> class: `strcmp` on a row name, 9 hits in src/gen src/opt, two on view rows (emit_dfa.c:13606, 13610); widen the check to every table.
- K71: old "both halves from the same walk" -> class: one sentence from two sources, single-record form (`forces_registry` returns `why_pos`, 34 uses). FINDING: the accessors the entry names (`first_dfa_excluding`, `first_vmonly_pos`) no longer exist in src/; the witness needs a re-run, the entry may be stale.
- K32: old "A count CLAMP" (named the pattern, not the site) -> class: bounded-repeat replication, one loop at nfa.c:783 (`git grep -n rmax -- src/ir/nfa.c` = 7 lines).
FIXED/closed entries only got the field rename.

## STATE AT HANDOFF
Branch lane/bugclass, committed. Rulings file last entry applied: none (empty). Validation complete: test-plan-lint 2/2, claudemd size all within limits. OWED: none.
