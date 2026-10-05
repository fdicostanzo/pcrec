# docs/dev/optloop/s4/k82hbuild/ — K82 (B)'s HANDOFF build instruments (lane `k82hbuild`, 2026-10-05)

The checks behind `docs/dev/lanes/k82hbuild_report.md`, built from
`docs/design/litscan_k82h.md` revision 2 and Frank's rulings. Reference
material: never built or run by `make` (the in-suite detectors are
`tests/litscan/handoff.rxt`, `tests/codegen/run_prechecks.sh` §5.12 and
`run_encoding_checks.sh`'s DD12a(i) region (v)). Every script reads `BASE`
(the abi-60 compiler), `NEW` (the handoff), `SCR`/`TMPDIR` from the
environment and writes only there.

- `k82h_movers.py` — §4.1: the MOVER MANIFEST and the DENY ARM over
  `../c3_movers.py`'s populations (imported) plus the corpus's
  `--no-captures` and `--engine=vm -fprefilter` arms (r1 C-C9). BASE vs NEW
  with BASE's abi digit and NEW's one `RX_REQ_HANDOFF` line (and the
  size-cap reasons that count that line) normalized: the program moved iff a
  prediction recomputed from `--emit-facts` says so, the stamp equals
  `req_run_maxoff`, the run CHOICE never moves, and `-fno-req-handoff` is
  identical to BASE. Writes `$SCR/k82h_movers.json`, the input of the next
  two. It checks the plumbing, never the fact (its K is the walk's).
- `k82h_answers.py` — §4.2 item 1 / §4.3: BASE vs NEW through
  `tests/possessify/possdiff_driver.c` at every start position, per route,
  over b1's sweep, `k82h_gen.py`'s widest members, shifted/doubled/decoyed
  subjects and (utf8) ill-formed ones. NO allowance: every change is a
  defect (Q10). `CFLAGS` gives the ASan/UBSan arm, `SHARD=i/n` splits it,
  `ONLY_K_POS=1` with a K-1-planted NEW is §4.2a (c)'s coverage report.
- `k82h_oracle.py` — §4.2a (b): INVARIANT F against libpcre2 anchored
  attempts (PCRE2_ANCHORED at every start; utf8 with MATCH_INVALID_UTF), the
  window read off the stamp and nothing else of pcrec's; python `re`
  cross-checks the byte patterns. `KDELTA=-1` is its failing-direction
  control.
- `k82h_gen.py` — random members of a pattern's language biased to its
  WIDEST spellings (python's own parser, not pcrec's walk): the subjects a
  K one byte short can actually fail on.
- `k82h_movers.log`, `k82h_answers.log`, `k82h_answers_san.log`,
  `k82h_oracle.log`, `k82h_kminus1.log` — the landing transcripts
  (summaries of the runs the report cites).
