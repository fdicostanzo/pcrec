# r23_semantics — the R23 semantics critic's toolkit (archived evidence)

Scripts and prototypes produced by the R23 panel's semantics critic
(2026-08-15, docs/dev/reviews/2026-08-15-r23-k18-memo.md; raw findings in
the r23 appendix file there). Archived because the note-revision lane and
the eventual rewrite lane need them: `proto_a2_fix.py` is the S16 two-line
stack-entry restore, `proto_a2_shadow*.py`/`proto_a2_dup.py` carry both
stack disciplines with counters, `proto_ref.py` is the no-memo reference,
`proto_half*.py` are §1.4's two halves, and `sweep_nst.py`/`sweep_dup.py`/
`sweep_shadow.py`/`ocheck.py`/`emitcmp.py`/`oracles2.py` are the harnesses
behind S3/S8/S10/S11/S14/S15/S16.

Prototypes build with the parent directory's `prototypes/mkproto.sh` into a
scratch tree (never this repo). Pattern corpora are NOT archived — they are
regenerable from the seeded generators here (`gen_r23.py`, `gen_r23b.py`,
`gen_rand.py` seed 20260815) plus the fixed lists quoted inline in the
findings. `oracles2.py` needs libpcre2 via the repo's dlopen shim, same as
`oracle_cmp.py` one level up.

Known critic-harness caveats, disclosed in the findings and already fixed
in these copies: `ocheck.py` maps a generated matcher's `nomatch` exit to
`None` (an earlier revision counted it as a mismatch); `oracles2.py` maps
PCRE2 negative returns other than NOMATCH (e.g. -47 MATCHLIMIT) to an
excluded-cell bucket, not "nomatch".

Maintenance: static evidence, like `outputs/` — do not evolve in place; a
new panel archives its own directory.
