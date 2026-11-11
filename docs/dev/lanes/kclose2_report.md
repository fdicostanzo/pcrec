# kclose2 report (lane/memfn-kclose, follow-up to kclose)

## Summary

Merged main (dc1988069) into the branch; PIN-MSG-DEPTH is NOT the kit's (the rows plant pcrec text), so nothing changed there; XARCH-NEEDSOK is built in memfn/tests/check_targets.sh and S726 is re-declared DETECTED; the R-13 owed a sweep is prepared as gate job 580, not queued. Gate jobs 570-579 re-pointed to BASE dc1988069, dry-runs pass, not queued.

## Main merge

`git merge main` alone: clean, 1 file (tests/doc_lint/run_doc_lint.sh, the K37 brace fix). Merge commit 457eb5612. NEW BASE = main dc198806932da1bb9b30a9425ce91b7daacb843e (short dc1988069). `nice make -j2` and `make strict` green after the merge.

## PIN-MSG-DEPTH

Finding: S1760 and S1761 plant PCREC text, not kit text. Both name `SAB_FILE="src/parse/rxt_source.c"` (the `.rxt` include/lib pin reader), witness suite `code`, and probe through `$PCREC` with fixtures from tests/code/frag/. Per the charge I did NOT change them. The 256-byte `pcrec_error.msg` cut and the fixture-path length are the test-side half of the row in pcrec's lane; main takes the row back (plan.md [PIN-MSG-DEPTH]; its own `next:` names the fix: copy the fixtures to a short `$REACH_TMP`-relative path or match a message that puts the phrase before the path).

## XARCH-NEEDSOK

Built in memfn/tests/check_targets.sh (one new block before the `ok:` line, plus the level row now carries `vw`). For each kit level (levels.def) the check renders the level's helpers with G2's SIMD generator (memfn/tests/g2/g2_simd_gen.c, 24 sites, seed 1, at the widest level's test_march x86-64-v3, against build/libpcrec.a), keeps the helpers of that level's stamp and of every lower-width level of its family (a w32 helper falls through to w16) plus the shared bodies and loaders, drops G2's selector and wrapper and its host region, and compiles with the check's own floor `-march=x86-64 -mno-sse` plus `-m<each need>` and nothing else, with `-fkeep-inline-functions` so the unused static inlines are really compiled (without it gcc never inlines them and the weak need passes silently, measured). A refusal is a MISMATCH naming the level and the flags; a floor of 2 levels compiled (K35); a missing libpcrec.a SKIPS the cell, counted in the `ok:` line (`needs suffice at 2 levels (0 skipped)`).
- Hand plant (memfn/src/levels.def, w32 needs `avx2` -> `avx`, exactly S726's plant): `bash memfn/tests/check_targets.sh` rc=1: "level LV_X86_W32: its rendered helpers do not compile at -march=x86-64 -mno-sse -mavx ... error: inlining failed in call to always_inline _mm256_movemask_epi8: target specific option mismatch", and "compiled 1 levels (floor 2)". Revert: rc=0. The suite that hosts it, `bash tests/memfn/run_targets.sh`, reads `checks failed: 1` under the plant and `checks passed: 42, failed: 0` after the revert (the memfntargets arm the matrix scores).
- S726 (tests/mech/sabotages/S726_w32_under_weak_guard.sh) re-declared: `SAB_EXPECT=DETECTED`, `SAB_SUITES='memfntargets'` (g2simd dropped: it could not see it), header and description rewritten, SAB_BEFORE/SAB_AFTER unchanged (anchor tables unaffected: same file, same line). The matrix run of S726 is OWED to mech job 579 (box lock); the hand plant above is the evidence. Added to the mech shard 3 list. plan.md [XARCH-NEEDSOK] is main's to close (not edited here).
- No pcrec-side files needed.

## R-13 owed a job

Job 580-kit-kclose2-r13a (scratch jobs/): `python3 -I scripts/emit_sweep.py --ref dc1988069 --tree-rev HEAD --variant all --bases byte --trace --trace-order fallback=ordered --jobs 16 --out ... --emit-pins .../pins.py` on worktrees/kclose, then a comparison of the pins file's TRACE_VARIANT_RECORDS_FLOOR (min of base and tip per variant and arm, the records of the working side) with the floor in scripts/emit_sweep.py:2903. It prints `r13a cell VARIANT ARM: measured N floor M ok|ABOVE|BELOW` for the 10 cells and `r13a: DONE rc=0|1` (rc 1 on any BELOW or missing cell or a sweep that is not clean). Chained after mech3. Dry-run rc=0, not queued; est 3600 s, cap 7200.
How the floor will be pinned: the measured counts for the 10 cells (plain, lowsize, lowdfa, lowthr, lowboth x c-default, c-vm) are pasted verbatim, no margin (the trace is deterministic, emit_sweep.py's own comment), into TRACE_VARIANT_RECORDS_FLOOR by a reviewed change that names the sweep's BASE and tip, and a count ABOVE its floor is the re-pin; a count BELOW is a finding, never a quiet re-pin. The comment block above the table gets the date, the tip sha and `--ref` for the record.

## Checks

- `nice make -j2`, `make strict`: green (strict re-run after the new check: "the kit's target table check passes").
- `bash memfn/tests/check_targets.sh`: ok, needs suffice at 2 levels; red under the hand plant, green after the revert (above).
- `test-memfn-finder` 3419 passed / 0 failed; `test-memfn-rows` 95 / 0; `test-memfn-link` 11 / 0; `test-memfn-targets` 42 / 0 (also red under the plant).
- Anchors (`python3 -I scripts/m6read_check_sab_anchors.py`): 1226 sabotages, all anchors resolve.
- `make test-memfn-g2` and `make test-codegen`: g2 rc=0 (70,358,664 checks passed, 0 failed; log scratch/memfn/kclose2/g2.log); `make test-codegen` rc=0 (the K37 doc-lint red is gone with the merge; 0 test-section Error lines; log scratch/memfn/kclose2/codegen.log). All niced -j2.

## Gate jobs

Dir /var/tmp/pcrec-pcrec/scratch/memfn/kclose2/jobs/, keys kit-kclose2-{strict,ident1-3,reach,test,plants,mech1-3} numbers 570-579, plus 580-kit-kclose2-r13a. TREE worktrees/kclose (branch lane/memfn-kclose), BASE dc1988069, fresh BASE binary /var/tmp/pcrec-pcrec/scratch/memfn/kclose2/base/build/pcrec (`git archive dc1988069`, niced make -j2). Mech: shard 3 now 27 rows (S3015 and S726 added); the other shards unchanged. All eleven `--dry-run` rc=0. NOT queued. The jobs are scratch files, not committed.

## Charter-vs-committed checklist

- Merge main, BASE recorded: committed (457eb5612).
- PIN-MSG-DEPTH: finding reported, rows untouched (pcrec text): in this report.
- XARCH-NEEDSOK check + S726 re-declared, hand plant red / revert green: committed.
- R-13 owed a: job prepared and dry-run, floor pin procedure named; the sweep itself is owed to the queue.
- Gate jobs re-pointed, dry-run, not queued: scratch.

## STATE AT HANDOFF

Branch lane/memfn-kclose, tree clean after the commit of this report.

OWED: none (everything but the unqueued gates 570-580, which the kit manager queues)
