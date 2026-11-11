# tests/families — [FEAT-FAMILIES] pre-move differentials

Checks owed before the bare default moves to a named family (D37 addendum,
2026-11-06: "one generated libpcre2 differential each for quoting and
named-groups"). Opt-in: not part of `make test` (queue them as box jobs).

## Files

- `module_diff.sh` — the shared body: a module's patterns against libpcre2
  over every subject of a small alphabet at every startpos, match span AND
  group spans compared; plus accept/refuse agreement for a refusal list.
  Reuses `tests/backrefs/bref_oracle.py` and `bref_batch.c` (one oracle in the
  tree). Populations are asserted exact; SKIPS loudly without libpcre2.
- `run_quoting_diff.sh` — `\Q..\E` (43 patterns, 14 refusal agreements).
- `run_named_diff.sh` — the three named-group spellings, with the references
  and lookbehinds they interact with (39 patterns, 20 refusal agreements).

Widened fuzz for the set: `tests/fuzz/fuzz.py --set extended`.
