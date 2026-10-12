# docs/design/compound/twin/ — the split twin ([COMPOUND] design lane mscomp, as [COMPOSITE], 2026-10-12)

Hand-composed composites built from UNCHANGED `build/pcrec` compiles plus a
hand-written controller: the evidence behind `../../compound.md` §B. Light
measurement only (counted loads, an every-startpos differential); no clock.
Scratch output goes under the worktree's `build/` (never committed).

- `twin.py` — compiles, per case, the plain artifact (today, prefix `rxp`), the
  floor part `\G(?:P)` (`rxf`) and Q (`rxq`, P with `\G`/`\A`/`^` textually
  killed to `(?!)`: a stand-in for the AST derivation, correctness only, so Q
  usually routes VM here), writes the controller from `ctrl.c.in`, links
  `diff.c` and runs it over generated subjects. `--literal` builds D163's
  literal controller (Q from `from`, not past the floor).
- `diff.c` — every startpos (0..n+1) composite vs plain (rc + every caps
  slot), plain vs libpcre2-8 10.46 (whole-match span), and the match_api.md
  §3.1.3 find-all loop composite vs plain.
- `ctrl.c.in` — the split controller as the build would emit it.
- `cost.py` — counted subject loads of a whole find-all (the survey's
  `../../../dev/optloop/matchsplit/qdrv.c` instrument), today vs the composite
  with Q pruned by hand (the build's kill + prune), one translation unit.
  `sqli_p.txt` / `sqli_np.txt`: concat-sqli and its free part (from the
  survey's `ms_rows.tsv.gz`, column `txtNP_hex`).
- `results/` — `split_differential.tsv` (94 cases, 1,416,556 cells, 0
  differences), `split_differential_literal.tsv` (the literal controller: 3
  cases wrong), `split_loads.tsv`, `sizes.tsv`, `one_tu_probe.txt`,
  `cases.tsv` (the case list: mssurvey's floor-mixed rows + hand cases).

Reproduce from the worktree root (TMPDIR inside the worktree):
`python3 docs/design/compound/twin/twin.py build/pcrec docs/design/compound/twin/results/cases.tsv build/sc/tw`
and `python3 docs/design/compound/twin/cost.py build/pcrec build/sc/cost`.
