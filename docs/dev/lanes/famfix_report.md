# famfix — land lane/famdef3 ([FEAT-FAMILIES]) onto main and fix its cloud reds

## STATE AT HANDOFF

STATE: delivered; cloud verification OWED (queued by `scripts/cloudrun --owner main --kind test --name famfix`).

Branch lane/famfix = lane/cloudtri (main + census fix) + `git merge --no-ff lane/famdef3` (7767af920).
The merge conflicted only in tests/codegen/run_recursion_identity.sh (FILEPIN/ABASEPIN).

- Recursion identity: famdef2/3 is abi 98 -> 99 (module `match-start-reset`; +18 bytes per artifact), so the emitted bytes DO move.
  Both pins are self-pinned to the merge 7767af920 (the branch's src-carrying commit; the later commits touch tests only); the manager re-pins to the landing merge. History text kept.
  `test-recursion-identity` itself NOT run locally (merge battery / cloud): OWED.
- (1) lookaround: `,match-start-reset` added to FEATS in tests/lookaround/run_lookaround_diff.sh (cloudtri's patch). `make test-lookaround` rc=0.
- (2) tests/codegen/manifests/m5_stage1_stamps.tsv re-recorded by `run_cpset_structure.sh` itself (file removed, section run): exactly 12 EMITTED_BYTES rows, +18 each = the abi 98 -> 99 stamp/feature-list growth (famdef's intended change). `make test-cpset-structure` rc=0.
- (3) startset: census_s1.py run on this branch (`-fno-start-set`; bench population left as committed). manifest_s2_vm_auto unchanged, manifest_s3_dfa unchanged, manifest_s2_vm_forced -71/+71 corpus rows (assertions d27 blocks using `\K` change option spelling to `assertions,match-start-reset`; shifted line ids). Header comment line added. `make test-startset` rc=0 (3/22/35 checks, 0 failed).
- Also green locally: `make strict`, `test-rxtsource`, `test-plan-lint`.
- Not touched: the ucpu3fix rows (cand-oracle, SABANCHOR) in cloudtri's report; not in this brief.

Local runs: nice make -j4, single sections; logs in /var/tmp/pcrec-pcrec/scratch/famfix/.
