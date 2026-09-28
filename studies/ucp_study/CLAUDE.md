# studies/ucp_study/ — [UCP]'s thinking-and-testing study

Lane `ucpthink`, 2026-09-28, on `main` at `13b7c202`. Backs
`docs/dev/ucp_study.md`. Study only: never built or run by pcrec's make.
Oracle probes write nothing on the remote box (ssh-stdin payloads).

## Files

- `classify.c` — per code point (1.1M, surrogates skipped), which of the
  patterns in `classes.txt` match one character, under PCRE2_UTF and
  PCRE2_UTF|PCRE2_UCP; prints count + interval list. Local only (links
  Homebrew libpcre2). Output: `classify_10.48.tsv`.
- `classify_remote.py` — the same question as ONE `pcre2_substitute` per
  (pattern, mode) over an all-code-points subject; output format equals
  classify.c's (the two agree byte for byte on 10.48). Remote run:
  `ssh duxevents@100.69.121.107 "python3 -c \"$(…)\" /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0" < classes.txt`
  (see the memo; any quoting that feeds the script on stdin works).
  Output: `classify_10.46.tsv`.
- `classes.txt` — the 39 class spellings both classifiers read.
- `analyze.py FILE` — the set relations §B.1 cites; `analyze.out` holds both
  versions' results.
- `bequiv.py [LIB] [MAXLEN]` — `\b`/`\B` vs their lookaround spellings,
  exhaustive over a 14-character alphabet to length MAXLEN, three modes.
  `bequiv_10.46.txt` (ssh stdin: `python3 - LIB 5 < bequiv.py`),
  `bequiv_10.48.txt`.
- `pcrec_bdrive.c` + `run_bdrive.sh PCREC OUTDIR MAXLEN` — the same alphabet
  driven through pcrec-generated matchers (six artifacts per encoding); each
  stream's sha1 equals bequiv's iff every answer agrees. `bdrive_main.txt`.
- `probe_misc.py [LIB]` — point probes: caseless × UCP, UCP without UTF,
  the verbs, `(?a…)`, `(?r)`. `probe_misc_10.46.txt`, `probe_misc_10.48.txt`.
- `latin1.py [LIB]` — UCP without UTF over the 256 bytes. `latin1_10.4{6,8}.txt`.
- `census.py PCREC TREE BENCH OUT [FLAGS…]` — corpus + bench population
  census: lexical UCP features, engine stamps, and for `\b` patterns the
  `-e utf8` route and the lookaround rewrite's route. ~3 min, 3 workers;
  take the boxlock. `census_13b7c202.tsv` (default),
  `census_nocap_13b7c202.tsv` (`--no-captures`).
- `census_analyze.py CENSUS` — §A/§C/§D tables: `census_analysis.txt`,
  `census_nocap_analysis.txt`, `census_nocap_C.txt`.
- `sizes.sh PCREC OUTDIR` — §E object sizes per engine under `-e utf8`.
  `sizes_13b7c202.tsv`. Takes ~2.5 min (`\p{Xwd}+` compiles in ~66 s).
- `rewrite_sizes.sh PCREC OUTDIR` — §C.3's four bench patterns, original vs
  rewrite. `rewrite_sizes_13b7c202.tsv`.
