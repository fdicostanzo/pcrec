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

**substb2 (2026-10-22): re-driven through the R4 interface** (`pcrec_subst_check`
/ `rx_subst_ctx_init`, a map, the element's pieces, the support unit's
`rx_subst_replace_all` / `rx_subst_flatten` / `pcrec_subst_map_names`) after
lane subst replaced R3's bind, byte-cursor element, glue and `--unset=`. Only
HOW the corpus is driven changed: the eleven `corpus/d_*.tsv` families are
byte-identical and keep the libpcre2 / writer answers. Each change is marked
`substb2` in its file. What moved, per directory:

- `lib/` — every case runs through the spec's recipes: limit `all` with gaps
  through `rx_subst_replace_all` (cross-checked against §6¶4's batch recipe
  through `rx_subst_flatten`, §10¶10); a numeric limit through §6¶2's per-match
  recipe, counting the loop (§6¶3); `nogap` through the element without
  `RX_SUBST_GAPS`; a pattern wider than `RX_SUBST_BATCH_PAIRS` (d_big's 300-group
  rows) takes the per-match recipe for `all` too (§10¶7). The `unset` column
  is the run-time `RX_SUBST_STRICT` flag (one subst artifact per template
  now). Named templates get a map from `pcrec_subst_map_names` (no
  `RX_SUBST_MAP_ABSENT`); a refusal at the setup prints `BIND` as before.
- `api/` — the eight drivers keep their names (`run_d27.sh` reads them) and
  run the R4 interface: `t_bind` the record shape, the check, the by-name
  helper and hand-filled maps; `t_shape` `rx_group_run` and the run/slot layout
  of the helper; `t_element` the pieces; `t_glue` replace-all and the recipes;
  `t_vars`, `t_iter`, `t_utf`, `t_threads` adapted. `build.sh` emits the
  support unit and compiles no artifact with `--unset=`.
- `cli/` — `--unset=` cases are refused-option cases; the R3 stamps and
  `PCREC_SUBST_PAIRS` cases are retired; the CLI composes the §6 recipes and
  the support unit (`--emit-support`) instead of bind and glue.

Per-case contract notes of the differential driver, R3 to R4: `short`, `zero`,
`canary` are now replace-all's NOSPACE with `*len` the total (§10¶8), exact
capacity malloc'd so ASan sees overruns; `nonzero` (error leaves `*outlen` and
`*nsubst` zero) became `touched` (a negative return other than NOSPACE leaves
`*len` untouched, §10¶9); `neg1` stays (§8¶1); `fresh` stays (limit 0 leaves
the iterator FRESH); new `limit0`, `bigcap`, `batch`.

Retired (the promise no longer exists): the glue's `limit` argument and
`*nsubst` out-count (the count of a NOSPACE call is not reported any more, so
`short`/`zero` no longer check it); the binding's tag (`bind.ok`'s tag,
`bind.refuse.after.ok`, `bind.mismatch.after.ok`); `bind.nseg0/1/2/extra` and
`seg_user` (no segments); `bind.rxabi` (the check reads only `ncaps`,
`ngroups`, `encoding`); `glue.after.refused.bind`, `glue.zeroed.binding`,
`glue.rx.abi.changed`, `glue.sub.abi.changed` (no binding to forge);
`glue.saturate.null.out`, `glue.nosat.max-1`, `glue.saturate.out`,
`el.saturate*`, `el.nosat.at.max-1`, `el.sat.at.max`, `put.*` and `el.writes.fits`
(the byte cursor and `rx_subst_put`; `var.huge.len.saturates` stays, as
replace-all's NOSPACE with `*len` `SIZE_MAX`, and the pieces' own overflow is
`el.need.overflow.*`); `el.k0.otherbinding`, `el.ncap`, `el.unbound`,
`el.other.artifact` (§4¶15: undetected or undefined); `shape.unset.empty/error`
and the `--unset=error` stamp cases (`stamp.unset.empty`, `stamp.unset.error`;
unset is a flag of the call); `shape.scoped` (the helper reads the caller
scope only); the `pairs.*` cases (`PCREC_SUBST_PAIRS` is retired; three
`foreachpairs.*` cases replaced them, and substland2 made those three
`batchpairs.*` when D175 dropped `RX_FOREACH_PAIRS`); `glue.limit*` through `pcrec_subst`
(the recipe carries them). `codes.values` drops `PCREC_SUBST_RENDER` (-13 is
reserved). Re-derived from §3¶2, not from the old text: `needs` order (named
first, group 0 included) is the reference list's first-appearance order
without group 0, so the `bad_ref` indices of `names.*` follow it. Spec
witnesses promoted from INFO to CHECK: a ended iterator to replace-all is
`PCREC_ERR_ITER`; an `out == NULL` with `cap > 0` is `MISMATCH`.

Re-tagged by ruling R14 (`docs/dev/lanes/subst_rulings.md`):
`include.case.prefixes` expected `sq.h` and `sQ.h` in one TU to compile;
§1¶3 makes the subst header `#error` on prefixes that differ only in case, a
clean refusal, so the case now expects that `#error` (kept, not deleted).

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
- `api/` — `build.sh` and the `t_*.c` drivers (bind = check and by-name
  helper, element = pieces, glue = replace-all and recipes, vars, shape,
  iterator, threads under ASan and TSan, utf); `t.h` holds the §6 recipes.
- `cli/` — `cli.sh` (modes, prefixes, refusals, stamps, header composition,
  the spec's examples verbatim) and `inc_body.c`.
- `substd27_report.md` — the writer's report (findings F1-F12).
