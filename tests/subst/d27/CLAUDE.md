# tests/subst/d27 — the D27 blinded corpus for the subst artifact

Written by lane substd27 (opus, 2026-10-22) under D27: the author saw only
`docs/spec/subst_api.md` (with `match_api.md` §3.8), `lib/pcrec.h` and the
built binary, never `src/` or `tests/`. Its findings report is
`substd27_report.md` here. Adopted by lane substfix (2026-10-22), which
changed only what the adoption needed, each change marked `substfix` in the
file: paths, the timeout binary and the compiler from the environment; the
template's `-e` passed to the subst compile (the contract's §2¶5, which the
fixes added); a utf8 template refused at compile accepted where libpcre2
returns a UTF-8 error (§9 row 13); the fixed findings' rows retagged `diff`
(F1, F2, F3, F4, F7); the two DOC-finding API cases (F6, F8) pointed at the
corrected text. The cases themselves are the writer's.

Run and scored by `../run_d27.sh` (`make test-subst-d27`), which owns the
verdict (the runner below only prints counts).

## Files

- `run_all.sh` — runs every family, the API drivers and the CLI suite into
  `$OUT_ROOT`; one summary line per suite.
- `corpus/` — `d_*.tsv`, eleven differential families (columns in
  `lib/run_diff.py`), COMMITTED; `gen_corpus.py` and `gen_fuzz.py 600 2627`
  regenerate them (by hand; the section never does).
- `lib/` — `run_diff.py` (the differential runner: every rx and subst
  artifact compiled once, one ASan+UBSan driver process per case),
  `ref_pcre2.py` (libpcre2 via ctypes), `diff_driver.c`, `esc.py`.
- `api/` — `build.sh` and the `t_*.c` drivers (bind, element, glue, vars,
  shape, iterator, threads under ASan and TSan, utf).
- `cli/` — `cli.sh` (modes, prefixes, refusals, stamps, header composition,
  the spec's examples verbatim) and `inc_body.c`.
- `substd27_report.md` — the writer's report (findings F1-F12).
