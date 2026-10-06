# docs/design/startset/s3/ — the census re-run at START-SET stage 3

Lane `ssbuild3` (2026-10-06). `census_s3_summary.txt` is
`../s1/census_s1.py`'s summary (the stage-1 instrument, unchanged: the BUILT
`start_set` fact, per-block options, V and F as §2 states them, `E*` read off
the emitted tables) re-run when `tests/startset/dfahat.rxt`, `reseed.rxt` and
`hybrid.rxt` (ssedge's DFA-hat drafts, §6.4.4) and the hand-written `dfahat_paths.rxt` joined the corpus. It was run
with the PRE-STAGE-3 compiler (main `57db5152`), so `F` is derived from the
deny-equivalent artifact and never from the DFA hat's own selection. It
regenerated `tests/startset/manifests/`: `s3_dfa` +39 rows (23 `dfahat.rxt`, 1 `dfahat_paths.rxt`,
9 `reseed.rxt`, 6 `hybrid.rxt`), `s2_vm_forced` +54/-1, `s2_vm_auto`
unchanged. Every added row is a fixture block; the one removed row is
`tests/ucp/ctxnode.rxt:400`, whose (text, options) twin in `dfahat.rxt` now
sorts first in the census's dedup and takes its id. Reproduce:
`PCREC=<pre-stage-3 build> TREE=. BENCH=<pcrec-bench> OUT=<dir>
MANIFESTS=<dir> python3 docs/design/startset/s1/census_s1.py`. No check reads
this file; the manifests are what `tests/startset/dfahat_checks.py` and
`vmhat_checks.py` check.

`census_ssfix3_summary.txt` (lane ssfix3, 2026-10-06, the ss3 D6 panel fixes):
the same instrument after two changes — F reads `T = S` (the panel's BLOCKER
sound-F1 struck `S ∩ E*`), and every compile carries `-fno-start-set`
(checks-m5), so the census runs on the CURRENT build. It reproduced
`s3_dfa` and `s2_vm_auto` byte for byte and added 12 `s2_vm_forced` rows (the
`tests/startset/dfahat_f1.rxt` blocks). Its `F-checked: |E*| < 256` row reads
12 — the BLOCKER witnesses, where `E*` is not all 256 bytes, which is the
population D148 addendum 1's "`E*` is all 256 on every seeded machine" never
contained.
