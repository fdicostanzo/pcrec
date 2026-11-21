# k147tri report

## Summary
Fixed the two cloud reds of run 44839634768 (branch cloud/main/test/k147f2-test @ ee54fdcd5). Tests and docs only; no emitted-byte change. Rulings file: no R-n present.

## Shard 6 manifests
test-startset's [vm-movers] named the true keys: tests/possessify/possessify.rxt:4859 and :4931 (the previous lane had :4860 and :4933). Fixed the two rows in manifest_s2_vm_auto.tsv and manifest_s2_vm_forced.tsv (same options/hex, line numbers only). Local `make test-startset`: both [vm-movers] lines PASS, 592 auto rows and 4510 forced rows, 0 off-diagonal.

## Shard 9 litpost
`litpost` removed from DEPTH_FAMILIES (tests/thread/run_compile_stack.sh) and listed in known_issues.md K152 as its trailing-element witness: 440,560 B on this box (gcc 15.2.0), died exit 139 on CI (run 44839634768). Replacement row `optaltpost`, `(?:a|b…c)?d`: high-water 312,560 B at 250 (29% under 442,368), refused by name at 251. `lazypost` (`*?`) measured 344,560 (22% under) and was not kept. Local `make test-stackdepth`: 65 passed, 0 failed.

## Spec
docs/spec/limits.md §3.10¶5 gains the one sentence: budget and figures are measured with this box's compiler (gcc 15.2.0, Ubuntu 15.2.0-16ubuntu1) at default flags; another compiler can need more (CI overflow of the 440,560-byte literal nest, K152). test-spec-history and test-doc-lint pass.

## Validation dispatched
Cloud run k147tri-test dispatched as last act; sha and ls-remote proof in STATE AT HANDOFF.

## STATE AT HANDOFF
Branch lane/k147tri, committed. Rulings: none applied. Owed: none.
Cloud dispatched: k147tri-test @ b2067a93c (ls-remote proven).
OWED: none
