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
Facts only (R2); the manager writes the landing text. Found by `git log --oneline main..HEAD` and docs/dev/reviews/.
- Reviews on this line: r32 (2026-11-16-r32-covs2code): its FIX-NOW items are in (lane covs2fix, green cloud runs per its header); F1 CODE-CAP is the open size-cap finding, now settled by R1 (spec corrected, plan row [COVER-SIZE-LADDER] status written). Kit rounds on the forms: r35-r41 (memfn-forms .. forms6), r44 (forms7), r45 (forms8): their FIX-NOW items were built by lanes formsfix* and formsland6 (commits in the log; r41 verdict "LAND AFTER LISTED FIXES"; r45 FORMS8-1/FORMS8-2 built in formsfixm). I did NOT verify each FIX-NOW against the tree one by one; formsland6's report says its --rev12 smoke timed out and its cloud runs were not dispatched, and the cloud suite below is the first full run on the merged tip. Plan-deferred (not FIX-NOW): r32 F2 kit near-miss skip, F4 dead-conjunct removal.
- Ride-along register (docs/dev/guide/architecture.md part 3): no row names [COVER-CAP]; rows whose text touches this line are 10 (signed start offsets, kit window spans) and 24 (offset-bound family). Whether the landing updates either is the manager's reading; I found no cover-cap-named row to update.
- [COVER-CAP] plan row status line to write: currently "status (2026-11-18): stage 1 landed (abi 108); stage 2 + the kit's forms MERGED on lane/covs2land (c774d15c0, abi 109); cloud: mechrows, asan green, test RED on a kit test bound, fix lane/memfn-g2pcap in its cloud run; ..." Facts for the rewrite: g2pcap merged (33fec79b3, cloud test green on d5c41db37 per its merge message); relabel64 comment-only merged (0df533a85); main merged (8c4cbc89e); spec sentence corrected (661fef79a); the full cloud suite on the tip is named below.
- D177 full-suite ledger line due: yes, one line for the cloud suite run named below (verdict not yet read).

## Spec sentence (part 2)
R1 applied. Probes re-run on tip 337e1ced8 (all matched R1): `build/pcrec -p rx --window-search-width=4095 -o X.c --pattern '[0-9a-f]{4095}'` rc 0, 23,830 B, DFA_SCAN "cover". Scratch build `make BUILD_DIR=$PCREC_TMPDIR/scratch/covland/b20k CFLAGS='-O2 -g -DPCREC_MAX_EMIT_BYTES=20000' .../pcrec`: same command rc 1 "pattern too large: 28577 bytes of emitted C source (limit 20000 ...)"; without the width flag rc 0, ENGINE_SEL "size-cap-retry".
- limits.md [3.12P4]: "The emitted-size cap (8.1) is not a second cliff at the shipped value: no legal width reaches PCREC_MAX_EMIT_BYTES (1,000,000) ... a builder who lowers the cap by -D below a cover's size gets a FAILED compile ... no rung of the size-cap ladder (8.4) drops the cover ... A route that is not a cover and exceeds a lowered cap still retries through the ladder, stamped size-cap-retry."
- tuning.md 2.56P2: last sentence replaced by the same facts, pointing at limits.md 3.12P4.
- plan.md [COVER-SIZE-LADDER]: status line only (2026-11-19, sentence corrected, trigger stated).

## Validation (part 2)
make rc 0; make strict, make test-codegen, tests/registry/limits_check.sh, make -s test-plan-lint: all rc 0 (log scratch/covland/val2.log).

## Cloud suite
`scripts/cloudrun --suite --owner main --ref 52afb3a81a779029b814bfee6dbe4f6daa4559a3` (the tip before this report commit; the tested tree differs from the final branch tip only in docs/dev/lanes/covland_report.md). DONE line: `cloudrun: SUITE rc=0 6 kind(s) (test axes ubsan asan mech recidentity) for 52afb3a81`. Proved by `git ls-remote origin 'refs/heads/cloud/main/*/suite-52afb3a'`: six branches cloud/main/{test,axes,ubsan,asan,mech,recidentity}/suite-52afb3a, all at 52afb3a81a779029b814bfee6dbe4f6daa4559a3 (the covland* glob matches none: branches are named suite-<sha7>). Verdicts arrive as CLOUD-DONE via queuewatch; not read.

## STATE AT HANDOFF
Branch lane/covland, rulings applied: R1, R2 (last: R2). R1 and R2 applied (last entry R2).
OWED: none (the cloud suite is dispatched, its verdict arrives via queuewatch as CLOUD-DONE for cloud/main/*/suite-52afb3a; named in the Cloud suite section).
