# memfn/data/sets/ — the kit's measurement-set files before [MEASURE-SET]

Every `.tsv` here is WRITTEN by `generate.py` (`python3
memfn/data/sets/generate.py`; `--check` compares byte for byte and exits 1
on a difference). Never edit a set by hand. Each file carries its
`values_digest` (FNV-1a-64, `measure_sets.md` §1.6).

- `kit-interim-grid1.tsv` — the labelled kit-private INTERIM set: grid1's
  values relative to u = beta_walk(DFA_SCAN, r1e0c0), the derived `saving`
  rows computed in `generate.py` from the measured absolute betas. A TEST
  INPUT (Q-REVAL-10): it is what the predicted-mover manifest
  (`docs/design/memfn/r17b_prime/fdb2/predicted_movers_B4.tsv`, which
  supersedes B1's `fdb1/` one after B2's floor-token correction) was read
  under.
- `synthetic-all-walk.tsv`, `synthetic-all-v1.tsv`, `synthetic-all-wide.tsv`
  — the extreme sets (every saving 0 / 0.5 / 0.5 with W64 open).
- `synthetic-every-key.tsv` — every key a finder row or its pay rule can
  read, for every token the shadow can spell: the R-MS1 / R-MS4 tests' set.

A regeneration that changes a value moves no artifact byte at B1 (no row is
routed); from B4 it moves the selections the manifest predicts, a pcrec abi
event.
