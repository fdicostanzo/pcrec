# skilled report (lane skilled, sonnet, 2026-11-23)

## Summary
Applied the skill, guide and plan edits PROPOSED in `docs/dev/pred/to_main.md` P-17, P-18, P-20, P-21, P-24, P-25, P-26 (24 items). Docs only; one item was applied in a reconciled form, none declined. Checks run: `make -s strict` clean; `make -s test-plan-lint` PASS; `scripts/check_claudemd_size.sh --all` within limits. Targets: `.claude/skills/pcrec-critic/SKILL.md`, `.claude/skills/pcrec-predicate-manager/SKILL.md`, `docs/dev/guide/critics.md`, `docs/dev/plan.md` ([COND-FAMILY] status line). Merged duplicates: P-17(2) with P-24(1); P-20(2), P-21 P5 and P-21 P1/P2 into one "Evidence models" bullet; P-18(1), P-20(1) and P-21 P3 into one section-3 paragraph plus one COMMON sentence.

## Applied
| Entry | Item | Target | Result |
|---|---|---|---|
| P-17 | (1) rule induced from examples is tested on every printed example | predicate-manager sec 2 | applied |
| P-17 | (2) run-output record line is pasted | predicate-manager sec 2 | applied, merged with P-24(1) |
| P-17 | (3) grep the library's ruled bodies before asking | predicate-manager sec 2 | applied |
| P-17 | (4) printed programs are legal language (`/.../` inside `${...}`) | predicate-manager sec 4, revision brief | applied |
| P-17 | [COND-FAMILY] status addition | plan.md | superseded by P-26's line, which is the latest |
| P-18 | (1) coordinator re-runs evidence, red evidence at freeze is a finding | critic sec 3 | applied, merged with P-20(1) |
| P-18 | (2) ruling lens greps earlier rulings on the same pieces | critic, ruling check row | applied |
| P-18 | (3) re-run evidence doc checks after a direct fold | predicate-manager sec 4 | applied |
| P-20 | (1) verdict is the last line, exit code is not evidence | critic sec 3 and sec 5 COMMON | applied (COMMON sentence added) |
| P-20 | (2) models exit non-zero on failure; fold lane re-greens or names every red | predicate-manager sec 4 | applied, merged with P-21 P5 |
| P-20 | (3) name-resolution lens drill | critic lens table, new "name grid" row | applied |
| P-20 | (4) "same" sentence run on a parting case | predicate-manager sec 2 | applied |
| P-21 | P1 NAME-GRID check in the newest model | predicate-manager sec 4 | applied |
| P-21 | P2 successor declaration carries the red's FAIL text | predicate-manager sec 4 | applied |
| P-21 | P3 shared no-checkout clone at the freeze | critic sec 3 | applied |
| P-21 | P4 root concept to one lens | critic, name grid row | applied |
| P-21 | P5 non-zero iff last line reports failure | predicate-manager sec 4 | applied (merged with P-20(2)) |
| P-24 | (1) paste run output | predicate-manager sec 2 | applied (merged with P-17(2)) |
| P-24 | (2) re-derive conclusions whose premise a ruling changed | predicate-manager sec 2 | applied |
| P-24 | (3) start pending dispositions and lane before the first question | predicate-manager sec 1 step 7 | applied, limited to pending dispositions of an earlier round |
| P-24 | (4) core.md no longer fits one read | predicate-manager sec 1 step 3 | applied ("in parts") |
| P-25 | three r84 lessons | guide critics.md | applied (new r84 block) |
| P-26 | four r86 lessons | guide critics.md | applied (new r86 block) |
| P-26 | fold brief quotes the asked statement | predicate-manager sec 4 | applied |
| P-26 | lanes poll their own runs, "never wait for a notification" | predicate-manager sec 4 | applied in reconciled form (see below) |
| P-26 | lone underscore vanishes in the owner's chat UI | predicate-manager sec 2 | applied |
| P-26 | [COND-FAMILY] status line | plan.md | applied; 278 chars of status text, PL10 passes; replaces the 2026-11-19 status (its stale counts "core 122, library 54, parked 39" and r60 note dropped) |

## Declined or conflicting
None declined. One reconciled: P-26 "lanes poll their own long runs; a brief says 'never wait for a notification'". BOILERPLATE.md DO-THEN-FINISH says a run longer than about 4 minutes is the lane's last act (report it OWED and END), and only shorter runs may be polled. Applied text: "a lane polls its own short run (log tail) and otherwise follows BOILERPLATE's DO-THEN-FINISH". The manager may restore the original wording if predicate lanes are meant to poll long single-process runs.
Not in scope and untouched: pcrec-manager skill and its sub-files (no entry proposed an edit there); `docs/dev/pred/to_main.md` P-19, P-22, P-23 carry no proposed edits.

## STATE AT HANDOFF
Branch lane/skilled, committed, docs only. No rulings file entries (it was empty). Validation complete: strict, test-plan-lint, CLAUDE.md size check. Nothing owed. For main: the plan.md hunk touches only the [COND-FAMILY] status line; `next:` on that row still reads "one revision folding the rulings made after rev 24.4", which is stale and was not in the proposed edits.
