# covland report (STOPPED at the spec step: premise contradicted)

## Summary
Merges done and green (make, make strict, test-plan-lint). The spec-sentence probe CONTRADICTS limits.md [3.12¶4]: at a lowered cap the width-4095 cover compile FAILS (rc 1), it does not run the engine through the ladder. Per the brief's STOP rule no spec edit, no code fix, and NO cloud suite was dispatched.

## Merge
- lane/memfn-relabel64 (0df533a85): fast-forward, no conflicts (memfn/src/window.c comment block + relabel64_report.md).
- main (e121371b2): six doc-only conflicts, resolved keeping both sides' intent; merge commit 8c4cbc89e.
  - .claude/skills/pcrec-critic/SKILL.md: both plant sentences combined (git-archive copy from main, plus build with `build/pcrec build/pcrec-harness`).
  - docs/dev/guide/critics.md, docs/dev/history/claude_md/docs__dev__lanes.md, docs/dev/reviews/NOTES.md: both sides concatenated.
  - docs/dev/plan.md: took main's file and re-inserted the lane's added rows ([COVER-NEARMISS-SKIP] .. [COVER-ANSWERS-SYNC] before [COVER-SIZE-LADDER]; [SETTABLE-LIMITS] before [SPEC-ORG]); a naive both-sides merge broke plan lint (duplicate rows).
  - docs/dev/reviews/CLAUDE.md: took main's (12,125 B); the lane's 14 added index entries moved to docs/dev/reviews/NOTES.md (size limit 12,288).
- After the merge: `make -j16` rc 0, `make strict` rc 0, `make -s test-plan-lint` rc 0.

## Spec sentence
Probes on the merged tip (build/pcrec):
- `build/pcrec -p rx --window-search-width=4095 -o X.c --pattern '[0-9a-f]{4095}'`: rc 0, 23,830 B, RX_ENGINE "dfa", RX_ENGINE_SEL "selected", RX_DFA_SCAN "cover".
- same, default width: rc 0, 19,830 B, RX_ENGINE_SEL "selected", RX_DFA_SCAN "unanchored".
- Lowered cap, scratch build: `make BUILD_DIR=$PCREC_TMPDIR/scratch/covland/b20k CFLAGS='-O2 -g -DPCREC_MAX_EMIT_BYTES=20000' <dir>/pcrec`:
  - `--window-search-width=4095`: **rc 1**, no output, "pcrec: pattern too large: 28577 bytes of emitted C source (limit 20000 ...)". No ladder rung drops the cover. This contradicts [3.12¶4] ("runs the engine through the size-cap ladder ... the compile does not fail"); it is exactly the [COVER-SIZE-LADDER] finding, still present.
  - default width: rc 0, 14,773 B, RX_ENGINE_SEL "size-cap-retry" (drop-anchored rung), so the ladder works for the non-cover artifact.
- At the real default cap (1,000,000 B) the 4095 probe is 23,830 B, so on this pattern the cliff is not reachable without a lowered cap; a pattern reaching it at the default cap was not searched for.
Not edited: limits.md [3.12¶4], tuning.md §2.56 ¶2 (decision for the manager: correct the sentence to "fails with pattern too large" per the 2026-11-16 ruling, or add the rung; the ruling said corrected sentence, no rung, but the brief says stop on a contradiction).

## Validation
make, make strict, test-plan-lint: green (above). make test-codegen NOT run, cloud suite NOT dispatched (stopped). OWED: the full cloud suite on the tip after the spec sentence is settled.

## Ready to land
Not ready. Open: the spec sentence (above). Reviews/register/plan-row/ledger lists not compiled because of the stop; [COVER-SIZE-LADDER] plan row stays not-started and applies.

## STATE AT HANDOFF
Branch lane/covland tip = merge 8c4cbc89e plus the report commit. Rulings file empty: no R-n applied (none). Scratch: /var/tmp/pcrec-pcrec/scratch/covland/ (b20k build, probe outputs).
