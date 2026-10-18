# docs/dev/kvcensus/ — instruments for `../kvcensus.md`

Lane `kvcensus`, 2026-10-18: the [KIT-VERIFY] proof census D161 addendum 16
gates the build on. MEASUREMENT ONLY: nothing under `src/` changes, nothing
here is built by `make` or read by any check. Compile-side and libpcre2-side
only; no clock is read, gcc is never run on an artifact.

- `kvprobe.c` — the SITE PROBE. Linked into a copy of the CLI with GNU ld's
  `--wrap=pcrec_memfn_define --wrap=pcrec_memfn_emit` (the two doors in
  `src/gen/memfn_sites.c`), it writes one `SITE` line per site pcrec hands the
  kit (op, form, handoff, consumer kind, span-0 terms with offsets/need/sets,
  `preds`, presence spans, `head_max`) and asks the kit's pure define-time
  query `mf_ask` for the same site, so the line also carries what the kit
  proves today (`proven0`, `proven_prev`, `exists`). Output to `$KV_OUT`
  (appended); unset, silent. Build line in its header (`build/kv/pcrec-kv`).
- `kvdfa.py` — reads a machine off the EMITTED C tables (premultiplied or
  indexed, seeds, views, class-indexed accepts; compiled with `-fno-scan-edge`
  so no state is deleted) and answers: `lang()` the per-position sets, span
  and EXACT prefix of the language from the origin (a walk over subsets of
  entry rows, so a seeded machine reads every context), with a counterexample
  pair where exactness ends; `uniform()` delta_uniform per position and
  consumable_len for a plain DFA consumer; `whole()` whole-cover.
- `kvvm.py` — the VM's leading literal prefix off `--emit-ir`'s program
  section (strict: stops at a capture write; relaxed: a capture open at the
  attempt start does not stop it).
- `kvctx.py` — the CONTEXT shapes of the pattern text (leading `\b`/`\B`/
  fixed lookbehind, trailing `\b`/`\B`/fixed lookahead), the stripped body,
  and per-item expressibility as per-position sets with the absent-byte bit.
- `kvpcre.py` — libpcre2-8 through ctypes: the INDEPENDENT control
  (prefix-of-a-match by hard partial matching, with truncated-UTF-8
  completion; anchored match length).
- `census.py` — the driver. Population IMPORTED from
  `../optloop/artrev/gen/census.py` (bench + corpus, deduplicated); each row
  in its native configuration and again under `-e utf8`; single process,
  `nice -n 19`, `--deadline` epoch stop. Writes `OUT/patterns.tsv.gz` and
  `OUT/sites.tsv.gz` (JSON lines).
- `summarize.py` — folds a run into the memo's tables (markdown on stdout,
  `OUT/summary.json`).
- `selftest.py` / `selftest.txt` — every instrument on known witnesses and in
  the FAILING direction against plants (an edited machine, a superset claimed
  exact, a straddling `\b`, a wrong rewrite); the committed transcript.
- `tables.md`, `summary.json` — the committed output of the 2026-10-18 run
  (`summarize.py` on it); the raw `*.tsv.gz` are committed beside them.
