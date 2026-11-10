# docfmt1 — lane report

Lane docfmt1 (opus), 2026-11-10. DESIGN ONLY; no real file converted. Branch
lane/docfmt, on top of rev 0 (9fc840548).

## Delivered

- `docs/design/doc_index_format.md` rev 1 (34.9 KB, under the 40 KB bound),
  applying the owner's six answers (Frank, 2026-11-10):
  1. statements written by OPUS lanes and checked 100% by a fresh OPUS
     critic; owner read-through dropped (§2.7, §5);
  2. one details file per index kept, with the reason in one line (§2);
  3. `scripts/entry` is a LEVELED accessor: level 0 index line, 1 + working
     fields (plan next/trigger/status/refs; decisions addenda titles; known
     Witness/Fix first lines), 2 full entry; item grep `-g` (search level
     `-in`, output level `-l`, whole items); `--work` view (plan
     not-started + blocked at level 1, by section, `-k` keyword); levels
     and work views are columns of the one profile table
     (`scripts/doc_profiles.py`) the linter also reads (§2.3, §2.4);
  4. file caps are SOFT: doc_lint WARNs, exit 0; `scripts/gestalt` gets
     one line per over-cap index via `entry --over-cap`, format
     `docs: decisions.md 51.3 KB over soft cap 48 KB (+3.3 KB, 107%)`,
     silent otherwise, `docs: unavailable` on failure (§2.4);
  5. §8 is a kit-facing proposal, sendable as is (facts, not methods);
     unit K sends it after the critic round;
  6. known issues is unit 3.
- Migration rewritten: T1 (FIRST) = profile table + accessor + gestalt line
  + doc_format.md, plan profile in a temporary `single` form so `--work`
  serves today's plan.md before any split; T2 = doc_lint fold; unit 1
  decisions with the census finding as explicit acceptance (`scripts/entry
  D47` prints D47.a1-a4 and no D48 text; C6 finds 0 misplaced addenda, 17
  before); opus statement batches; 2 plan; 3 known issues; 4 upstream; K.
- §7 rewritten as "Owner's answers (2026-11-10)" plus one new question.
- `docs/design/CLAUDE.md` listing says rev 1.

## Validation

Design only: no make run. Doc size `wc -c` 34,871 B. Pre-commit staged
checks: 52 passed, 0 failed; check_claudemd_size within limits. No
`<file>.md:<line>` cites in the doc (grep).

## STATE AT HANDOFF

- STATE: done (rev 1 committed on lane/docfmt).
- New open question for the owner (one): should the per-LINE limits
  (statement 200 chars, plan title 90, `now` 160) also be soft, or only the
  file sizes? Leaning: line limits stay HARD (they keep a statement a
  statement, fixable at write time, and plan_lint already refuses
  over-long titles and status lines today); only the file sizes are soft.
- Choices made as the manager's/lane's call (answer-free): one details file
  per index; plan `single` form as implement-then-replace in T1, deleted at
  unit 2; gestalt prints `docs: unavailable` on accessor failure; tooling
  units stay sonnet, only statements are opus.
- No rulings file named in the brief; none applied.
- Next: the critic round on rev 1 (pcrec-critic, design); then unit K
  (send §8 to the kit) and, on a build go, T1.
