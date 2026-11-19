#!/usr/bin/env bash
# S3356 (review r53 F2, lane l1fix 2026-11-19; docs/design/span_arms.md §14.3 D-9, RM-6) -- THE CONCATENATION'S NEVER CELL flips ANY -> EVERY in src/core/kindrow.def: a concatenation reads never only when EVERY item is never, so the split derivation's `^abc` (its `^` killed to the empty class) no longer reads never. The floor-only form is lost (Q is never where P's floor arm is the whole pattern) and the admission's A5 reads the un-pruned arm: `^abc|xyz$` and `^\s+|\s+$` stop shipping as split compounds.
# This is the row ON THE COLUMN RM-6 moved the never decision into; S899 binds the per-arm drop (`it[i].never && !it[i].keeps`), which kept its line.
# Detector: test-compound. HAND-MEASURED by lane l1fix 2026-11-19 (plant on a scratch export of lane/l1build at be76ad164, `make test-compound`): FAIL — E0 4 fixtures (split-f/np/q, gfloor) lose their entry rows, B2 5 never disagreements (`^a$`, `\Gab`, `a{0,4}\A`, `^ab`, `\Gab` utf8), B4 decline controls and the decline list (3 controls admit where A5 is recorded, 13 cases). split.rxt (harness) passes under it (review r53 V-2: the answers stay right, the compound is just not shipped), so the harness is not an arm.
SAB_ID='S3356-kindrow-cat-never-every'
SAB_FILE='src/core/kindrow.def'
SAB_SUITES='compound'
SAB_DESC='the concatenation'\''s NEVER cell reads EVERY: a spine with one never item no longer reads never, so the split derivation keeps the killed floor arm and the split compound stops shipping'
SAB_DOC_FIGURE='HAND-MEASURED by lane l1fix 2026-11-19: test-compound FAIL (E0 4 fixtures, B2 5 cases, B4 3 controls + 13 decline-list cases); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3356.'
SAB_REACH='"$PCREC" -p rx -o - --pattern "^abc|xyz\$" | grep -o "RX_COMPOUND \"[a-z]*\"" | head -1'
SAB_REACH_EXPECT='RX_COMPOUND "split"'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='KIND_ROW(A_CAT,     OWN,  TRANSPARENT, NONE,   0, ANY)'
SAB_AFTER='KIND_ROW(A_CAT,     OWN,  TRANSPARENT, NONE,   0, EVERY)   /* SABOTAGE S3356 */'
