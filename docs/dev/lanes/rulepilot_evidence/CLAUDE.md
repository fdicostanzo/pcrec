# docs/dev/lanes/rulepilot_evidence/ — lane rulepilot's instruments (measurement only)

The rule-list pilot of `docs/design/pricing_rulepilot.md`; report `../rulepilot_report.md`. Nothing here is
product code or built by `make`. Run with `python3 -I`. Compile sweeps over 50 compiles go through
`scripts/boxlock run`; timing only through the queued jobs in `jobs/`.

- `census_dry.py` — the bake-off's dry census walk, copied VERBATIM from lane/bakeoff2 (b8a321ae3); imported, never edited.
- `inventory.py OUT` — step 1: the walk on this tree's compiler, the pick vocabulary, every pick on every site, the facts.
- `inventory/` — its COMMITTED output (census.jsonl is the input of every later step; `pcrec.sha256`/`commit.txt` pin the compiler; `slots.txt` the per-slot table).
- `slots.py` — the inventory per slot. `pieces.py` — step 2, the 24 rule pieces over `--emit-facts`.
- `search.py DATASET` — step 5, the pre-registered exhaustive 0-3 rule search, split, score and pass rule.
- `drill.py [SEED]`, `drill.out` — the search on four synthetic truths (planted, beyond, noise, null).
- `gen_subj.py`, `slot_build.py` — the slot: grid1 ext-arm-set shape, streamed subjects from each question's own file.
- `read_slot.py OUT DATASET` — the timing job's raw launches -> the search's dataset.
- `inventory/exclusions.tsv` — declared pre-timing exclusions (N20), read by slot_build/mkjobs/read_slot.
- `mkjobs.py JOBDIR`, `jobs/`, `shards.tsv` — the boxqueue jobs (790 build, 791-797 timing shards).
