# docs/design/startset/edge/ — START-SET's edge cells and the mutation run

Lane `ssedge` (2026-10-05, from main `e6ceeefa`, abi 61), answering D148
addendum 1's direction: the set argument is not a proof, so the EDGES carry
the evidence, and the planned tests must be shown to SEE each wrong variant
at answer level. The note is `../../startset.md` §6.4. Nothing here is built
or run by pcrec's `make`, and no check reads `out/`. Local libpcre2 is 10.48
(Homebrew); the 10.46 reference answered every question too (`out/`).

## The cells (DRAFTS: they move into `tests/` at build stage 1/2, §6.4.4)

- `cells.py` — THE AUTHORED HALF: each block's pattern, options, subjects,
  edge key and why. No answer is typed here.
- `gen_rxt.py` — `questions` lists every (block, subject, startpos at a
  character boundary) for the oracle; `write ORACLE [REF]` writes the
  drafts from the oracle's answers, refusing any cell where REF disagrees.
- `witnesses.rxt`, `lookbehind.rxt`, `wordb.rxt`, `reseed.rxt`,
  `multiline.rxt`, `utf8.rxt`, `bounds.rxt`, `hybrid.rxt`, `vmhat.rxt`,
  `giveup.rxt` — the drafts, house format (`docs/spec/rxt_format.md`),
  GENERATED, `oracle pcre2/10.46`. `hybrid.rxt`'s head builds the
  `-fprefilter-collapse` blocks as targets (the harness's own
  answer-identity control); `giveup.rxt` states the hat's answer with the
  Q-R3 allowance in its comment. Each block carries `tag edge=<key>`.
- `utfcheck_cells.tsv` — the `-futf-check` cells, which no `.rxt` directive
  can compile (`tests/utfcheck/CLAUDE.md`).
- `oracle.c` — the libpcre2 answerer (no pcrec code), built locally and,
  over ssh, on ubuntubudu.
- `rxtcells.py` — reads the drafts BACK (a minimal reader of exactly the
  subset they use; anything else is a hard error), so the mutation run
  tests the cells as written, not `cells.py`.

## The mutation run

- `fsp.c` — `../fs_probe.c` with the compile's options read (`-i`,
  `--ucp`, `-e utf8`; review r4 sound-F4). Build:
  `gcc-16 -O1 -std=gnu11 -Ilib -Isrc -o fsp docs/design/startset/edge/fsp.c build/libpcrec.a`.
- `hat.py` — compiles a block, reads `S` (fsp) and the emitted machine (E,
  per-seed escape sets, E\*, Tdfa; `../rev2/estar.py`'s reading, extended),
  decides the hat, and builds the twins: the DFA-hat table + re-seed
  (conditional / unconditional / none), the `first-memchr-bounded` form with
  its two landing paths, the VM entry + retry seek and its mutants.
- `mut.py` — per block: base (today's emitter = the deny arm), the correct
  twin (D0/V0) and every applicable mutant (the list is in its header); all
  cases run; DETECTED = a case's answer differs from the cell. A SWEEP arm
  (block alphabet, length <= 6, every startpos, twin vs base) says whether
  an undetected mutant is observable at all on that machine.
- `summarize.py` — folds `mut.py`'s rows into the mutation table.
- `classify.py` — a probe: one pattern's route, sets and hat verdict.
- `search_uncond.py` — random small-pattern families: DFA-hat movers on which
  the UNCONDITIONAL re-seed differs (plain family), and count-collapsed
  hybrid movers whose no-re-seed twin loses (`FAMILY=collapsed`).
- `census_reseed.py` — the conditional / none / unconditional re-seed on the
  56 census DFA-hat movers (rev2's per-row alphabets).
- `run.sh` — `W=<scratch> docs/design/startset/edge/run.sh
  [ref]` from the repo root reproduces everything (`ref` re-asks 10.46).

## out/ (verbatim transcripts)

`questions.tsv`, `oracle_local.tsv` (10.48), `oracle_ref_10.46.tsv` +
`.host` (ubuntubudu, 2070/2070 identical), `mut.blocks.tsv` /
`mut.variants.tsv` / `mut_run.txt` / `mut_summary.txt` (the table in §6.4.2),
`search_uncond_{plain,collapsed}.{tsv,log}`, `census_reseed.{tsv,txt}`.
The two searches and the census run were run as separate commands before
`run.sh` was written; `run.sh` chains the same commands.
