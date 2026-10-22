# docs/design/kit_proof/measure/ — `../../kit_proof.md` section 7, row "measure"

[KIT-VERIFY]'s D77 trigger and the GO/NO-GO for B1: a short, directional, same-box timing of the
harness-routed `cover` artifacts (`build/pcrec-harness --harness=kit-proof`) against the default
ones (`build/pcrec`). Measurement only: nothing under `src/`, `cli/`, `lib/`, and nothing here is
built or run by `make`. Lane covertime, 2026-10-21; report `docs/dev/lanes/covertime_report.md`
(the table format and the reading rule are in it).

- `cells.tsv` — the 8 cells (id TAB pattern). The four the brief names (`lit-l8`, `year4`,
  `file-ext-order`, `hex8-bounded`; patterns taken from `docs/dev/kvcensus/patterns.tsv.gz`) and four
  more from `tests/kitproof/cases.tsv`'s `verdict ... cover` rows, chosen for shape: a plain
  literal (`foobar`), a boundary-bounded literal (`\bcat\b`), a line-anchored literal
  (`(?m)done$`) and a lookahead class pair (`\w(?=\d)\w`).
- `gen_subjects.py` — deterministic subjects (python `random.Random`, seeded from cell and class)
  and, from python `re` alone, the EXPECTED answers. Three classes per cell: `real` (the cell's
  natural text, the match planted sparsely, near-misses present), `none` (the same filler, no
  match, asserted) and `dense` (matches back to back). Per class a ~1 MiB raw subject
  (`throughput`) and two sets of 1024 short records (`search_short`, `match`).
- `cdrv.c` — the timing driver, one binary per (cell, arm). Regimes: `throughput` = the
  match_api.md section 3.1.3 find-all loop over the raw subject; `search_short` = one `rx_search`
  per short record; `match` = one anchored `rx_match` at 0 per record.
- `measure.sh` — `build` (cached by a key of every input), `gate` (the answer gate: every arm equals
  python `re` on every subject, no clock; exit 3 on any disagreement), `time`, `calib`, `run`,
  `smoke`. Arms: DEF (build/pcrec), COV (harness, kit-proof), AA (build/pcrec again, a separate
  compile and link: the noise floor). Timing is interleaved (arm order rotated per item), pinned
  with `taskset` to cpu 7 (sibling cpu 15 idle), `L` launches, per launch each arm calibrates reps
  to `T` ns and takes `N` samples, the median per launch is the datum.
- `read.py` — `results.tsv` -> the Markdown table, the per-regime summary, the FINDINGS list and
  the A/A floor. Its header states the reading rule.
- `650-covertime-slot` — the boxqueue job (`--dry-run`: build + gate, no clock; `--ready`: the
  quiet gate; work: `exec measure.sh run`). Queued with `scripts/boxqueue add --name
  650-covertime-slot FILE` from the MAIN tree.

Output tree (gitignored): `<worktree>/build/covertime/` — `subj/`, `arts/<cell>/<arm>/`,
`cover_stamps.tsv`, `gate.tsv`, `results.tsv`, `table.md`.
