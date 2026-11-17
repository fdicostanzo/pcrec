# file40 report — filing of review r40 (predspec24)

## STATE AT HANDOFF
- Rulings file `file40_rulings.md`: empty (no R-n applied).
- Review number r40 was free (the last was r34 in `docs/dev/reviews`; the kit's r35-r39 are not in this tree); used as briefed.
- Id check: every id in dispositions.md (A1-A9, B1-B9, C1-C6, SIMULATE-8) is in the draft and every draft id is ruled; no mismatch. The draft's "ten owner questions" became nine (pass-own-labels not asked, per A1).
- Checks: `grep -rnE 'plan\.md:[0-9]'` over the review and its directory finds nothing; no `.md:N` line cite anywhere; `make -s test-plan-lint` PASS (45 plants, 0 failures); `check_claudemd_size.sh --all` 384 files within limits.
OWED: none
- Not done: no code, no disposition changed.

## WHAT WAS FILED
- `docs/dev/reviews/2026-11-17-r40-predspec24.md`: the draft with each PROPOSED line replaced by the ruled disposition and note (coordinator's proposal kept in brackets; "proposed X, ruled Y" where they differ: A1 no owner question, A4 no restriction of `hits` to WHOLE, A5 left-side-first withdrawn); a rulings summary, verdict NOT STABLE, the nine owner questions by slug, "What happens next" (fix lane predspec241 = rev 24.1, questions to the owner, short confirming re-check).
- Sibling directory `docs/dev/reviews/2026-11-17-r40-predspec24/` (42 files): critic findings, probe scripts, verify.md and its scripts, COMMON.md, process.md, dispositions.md, and a CLAUDE.md (r34's directory has none; r13's shape followed).
- Indexed in `docs/dev/reviews/CLAUDE.md` and in the history file's lane list (`docs/dev/history/claude_md/docs__dev__lanes.md`, file40 line).

## PROCESS CHANGES APPLIED
Four of four accepted (none changes who rules dispositions; none withheld):
1. Simulate lens row (SKILL.md): anchored / `\b` / lookahead operand drill for "whole on the stretch" operators (A3).
2. Simulate lens row: check each mode's "(labels compared)" key (A5).
3. Mode closure lens row: CAPTURE-STATE drill (A1/A2).
4. COMMON template paragraph (section 5): name the ORDER/SWAP switch and ask whether it can fail (C1).
Also in `docs/dev/guide/critics.md` "Lessons from review rounds" (three entries, dated, accepted 2026-11-17 manager) and a dated note appended to `docs/dev/meta/coordinator_framework.md`.
