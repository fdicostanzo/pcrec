# substtri report -- triage of 703-subst-test (lane/subst), 2026-10-22

Source: .boxqueue/failed/*703-subst-test (job.log.make). Four red sections.
No src/ change; no real defect found (class d: none).

## test-memfn-arch -- class (a)
C4 read the prefix `sve` (subst + var + error) in the blinded tests/subst/d27/api
files as the SVE ISA name (class 1, 3 hits). Three allowlist rows added in
tests/memfn/c4_allowlist.tsv; the blinded files are untouched.

## test-spec-history -- class (b), the ONLY failure
`[cites] measures: tests/compound/CLAUDE.md:125 §5¶8` dangling: this branch's
measures.md lacks §5¶8 that main's tests/compound/CLAUDE.md cites. Resolves at
the merge. 172 checks passed, 1 failed (that one).

## test-subst-d27 -- class (a)
The ratchet reported FIXED? (a known-divergence row that now agrees with
libpcre2): bsk-062 (known:9), utf-073 and utf-089 (known:11). The runner's own
libpcre2 comparison is the evidence (mode diff/nogap PASS). Retagged in
corpus/gen_corpus.py and the committed TSVs (bsk-062 -> nogap, utf-073/089 ->
diff). The other KNOWN rows are unchanged. FAILs, FINDINGs: 0 throughout; api
and cli arms all green.

## test-codegen -- classes (a), five sub-reds
- [SABANCHOR]: S1306 (emit_dfa.c `.next_n` added by I2), S1347/S1351/S1358
  (emit_subst.c lines moved by substfix's guards), S1360 (subst_template.c
  name scan became st_name_len) -- anchors re-derived; checker says all 941 resolve.
  The sabotage detection itself is OWED to the mech job (703-subst-mech) and
  must be read for S1347/S1351/S1358/S1360/S1306 (AFTER text changed shape).
- [K37]: 19 unbounded compiler calls in tests/subst/run_subst_tests.sh and
  run_d27.sh -> `"$TIMEOUT_BIN" 60` / `3000` (sourced timeout_bin.sh).
- [facts-decisions]: `RX_FOREACH` (I4's macro in the shared block) is a caller
  macro, not a decision: added FOREACH to MACHINERY in run_facts_checks.sh
  (inherited from lane/i2build; main may take the same one-line fix).
- K80-c: the pre-54 "legacy" header rewrite leaves `info->abi == PCREC_RX_ABI_H`
  in rx_foreach_begin with an empty macro (not C); the awk now rewrites value uses
  to 0 (inherited from I4, not from subst).

## Confirmation / owed
Alone: test-memfn-arch green; others see STATE below. Full `make test` queued
as 709-substtri-test (expect only test-spec-history red).
