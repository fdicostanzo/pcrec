# docs/design/startset/s2/ — the census re-run at START-SET stage 2

Lane `ssbuild2` (2026-10-05, abi 62). `census_s2_summary.txt` is
`../s1/census_s1.py`'s summary (the stage-1 instrument, unchanged: the BUILT
`start_set` fact, per-block options, V and F as §2 states them) re-run when
`tests/startset/vmhat.rxt`, `giveup.rxt`, `vmhat_walk.rxt` and
`tests/vars/startset.rxt` joined the corpus. It regenerated
`tests/startset/manifests/` (+12 auto / +13 forced rows, every one a fixture
block; no existing row moved; the DFA manifest unchanged). Reproduce:
`PCREC=build/pcrec TREE=. BENCH=<pcrec-bench> OUT=<dir> MANIFESTS=<dir>
python3 docs/design/startset/s1/census_s1.py`. No check reads this file; the
manifests are what `tests/startset/vmhat_checks.py` checks.
