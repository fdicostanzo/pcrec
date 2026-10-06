# docs/design/startset/s3/ — the census re-run at START-SET stage 3

Lane `ssbuild3` (2026-10-06). `census_s3_summary.txt` is
`../s1/census_s1.py`'s summary (the stage-1 instrument, unchanged: the BUILT
`start_set` fact, per-block options, V and F as §2 states them, `E*` read off
the emitted tables) re-run when `tests/startset/dfahat.rxt`, `reseed.rxt` and
`hybrid.rxt` (ssedge's DFA-hat drafts, §6.4.4) joined the corpus. It was run
with the PRE-STAGE-3 compiler (main `57db5152`), so `F` is derived from the
deny-equivalent artifact and never from the DFA hat's own selection. It
regenerated `tests/startset/manifests/`: `s3_dfa` +38 rows (23 `dfahat.rxt`,
9 `reseed.rxt`, 6 `hybrid.rxt`), `s2_vm_forced` +53/-1, `s2_vm_auto`
unchanged. Every added row is a fixture block; the one removed row is
`tests/ucp/ctxnode.rxt:400`, whose (text, options) twin in `dfahat.rxt` now
sorts first in the census's dedup and takes its id. Reproduce:
`PCREC=<pre-stage-3 build> TREE=. BENCH=<pcrec-bench> OUT=<dir>
MANIFESTS=<dir> python3 docs/design/startset/s1/census_s1.py`. No check reads
this file; the manifests are what `tests/startset/dfahat_checks.py` and
`vmhat_checks.py` check.
