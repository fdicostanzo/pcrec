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
  consumable_len for a plain DFA consumer; `whole()` whole-cover. Revised by
  lane x0fix (2026-10-21, kit_proof rev 2.2) for X0's two reading defects: the
  entry row is the EMITTED constant (`Machine.entry`; `starts()`, `whole()` and
  `forward_path()` assumed row 0, and the seeded `starts()` added row 0 for a
  DEAD absent entry), and `lang()` adds the byte a row consumes through its eol
  view at a subject-final `\n` (`Machine.vnl`, `acc_end`, reported as
  `view_d`), so the hull is the TRUE byte set. `starts()` now raises when no
  entry constant is emitted. The committed census tables below were produced
  with the old reading; `../../design/kit_proof/x0/exposure.py` counts the
  machines either change reaches.
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
  exact, a straddling `\b`, a wrong rewrite); the committed transcript (rerun
  2026-10-21 by lane x0fix with six added lines: `\Zx`'s emitted entry and the
  view-gated byte, each with its plant).
- `patterns.tsv.gz`, `sites.tsv.gz`, `census.log` — the 2026-10-18 run (JSON
  lines; one record per row x configuration, one per search site), pcrec at
  main `2523cfe4b`, pcrec-bench `34174712`, libpcre2-8 10.46.
- `tables.md`, `summary.json` — `summarize.py` on that run: every table the
  memo cites.
