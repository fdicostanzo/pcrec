# tests/ci — the CI shard table and its control ([CI-SHARD])

Lane `cishard`, 2026-10-13. CI's serial `make test` outgrew the hosted 4-vCPU
runner's 90-minute step timeout (`docs/dev/lanes/citime_report.md`: growth,
not a hang), so `.github/workflows/ci.yml` runs `make test-shard CISHARD=K/N` as
a matrix of N jobs. `make test` itself is unchanged and stays the local
merge/close standard.

- **shards.tsv** — THE TABLE, data not code: `section`, `shard` (1..N),
  `weight_s`, `weight_source`, one row per `TEST_SECTIONS` member, in
  `TEST_SECTIONS` order. `# shards=N` and `# ci_scale=` header lines are read
  by the scripts. The first-pass weights are LOCAL-box seconds (ttune ledger
  medians at make -j<=4, with labeled estimates for the sections the ledger
  predates and for the G2 SIMD family) and are to be REPLACED by the runner's
  measured times.
- **check_shards.sh** — the control (`make test-ci-shards`): every
  `TEST_SECTIONS` member (passed on argv by the Makefile — the list is spelled
  once, there) in exactly one shard, no unknown names, shard numbers in range
  and non-empty, weights numeric with a source, `ci.yml`'s `shard:` matrix
  line equal to 1/N..N/N; prints the per-shard projection. `--selftest` plants
  one defect per check into copies of the table and the workflow and requires
  each red naming its cause. `--list K/N` prints a shard's sections (what
  `make test-shard` runs; also the dry-run: `bash tests/ci/check_shards.sh
  --list 1/3`).
- **shard_rebalance.py** — after a CI run: `python3 tests/ci/shard_rebalance.py
  --measured sections-1.tsv sections-2.tsv sections-3.tsv [--write]` replaces
  weights with measured runner seconds and re-balances (greedy LPT). Prints the
  proposal unless `--write`.

Per-section timestamps in CI come from `scripts/sectiontimes` over
`make --debug=j` (the mechanism `scripts/perfrun` already used), uploaded as
`pcrec-ci-sections-*` on success and failure. Design record and the weights'
basis: `docs/dev/lanes/cishard_report.md`; CI shape: `docs/testing.md` "CI".
